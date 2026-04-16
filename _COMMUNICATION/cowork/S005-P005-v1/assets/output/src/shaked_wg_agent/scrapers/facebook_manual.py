"""Facebook manual listing scraper — reads from local JSON, parses with LLM.

Acquisition is manual (user copies posts from Facebook groups into a JSON file);
the parsing is automated via LLM (Claude or OpenAI).

Input JSON schema per post:
  post_id (REQUIRED), group_name, group_url, text (REQUIRED, >=10 chars),
  author_name, posted_at, has_images, raw_url
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing
from shaked_wg_agent.parsers.llm_listing_parser import (
    check_llm_config,
    parse_rental_post,
)

logger = logging.getLogger(__name__)

_LLM_PROVIDER = os.environ.get("SHAKED_LLM_PROVIDER", "")
_PHONE_PATTERN = re.compile(r"0\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}")


class ManualFacebookScraper(BaseScraper):
    """Facebook manual listing scraper — reads from JSON file, parses with LLM."""

    def __init__(self, source_id: str, search_url: str, city: Any) -> None:
        super().__init__(source_id, search_url, city)
        self.input_path = Path(search_url)

    def fetch_listings(self) -> list[ScrapedListing]:
        """Main pipeline: read JSON -> validate -> LLM parse -> dedup -> return.

        Never raises. Returns [] on any run-level failure.
        """
        # Step 1: Check LLM config (distinct warnings per matrix modes 1 & 2)
        if not _LLM_PROVIDER:
            logger.warning(
                "No LLM provider configured (SHAKED_LLM_PROVIDER); "
                "facebook-manual scraper disabled"
            )
            return []
        if not check_llm_config():
            logger.warning(
                "No LLM API key for provider '%s'; facebook-manual scraper disabled",
                _LLM_PROVIDER,
            )
            return []

        # Step 2: Read input file
        posts = self._read_input_file()
        if not posts:
            return []

        # Step 3: Parse each post
        listings: list[ScrapedListing] = []
        seen_ids: set[str] = set()
        seen_text_hashes: set[str] = set()
        failed_count = 0

        for post in posts:
            # Validate post schema
            error = self._validate_post(post, seen_ids)
            if error is not None:
                logger.warning("Skipping post: %s", error)
                continue

            post_id = post.get("post_id", "")
            text = post.get("text", "")

            seen_ids.add(post_id)

            # Within-batch text-hash dedup
            text_hash = hashlib.sha256(text.strip().encode()).hexdigest()
            if text_hash in seen_text_hashes:
                logger.warning("Duplicate text hash for post %s, skipping", post_id)
                continue
            seen_text_hashes.add(text_hash)

            # LLM parse
            parsed = parse_rental_post(
                text, post.get("group_name", ""), post_id=post_id
            )
            if parsed is None:
                failed_count += 1
                continue
            if not parsed.get("is_rental_offer", False):
                continue

            listing = self._to_scraped_listing(post, parsed)
            listings.append(listing)

        if failed_count == len(posts) and len(posts) > 0:
            logger.error("All %d posts failed LLM parsing", len(posts))

        # Step 4: Cross-source dedup
        listings = self._deduplicate_against_existing(listings)
        return listings

    def _read_input_file(self) -> list[dict]:
        """Read and validate the input JSON file."""
        if not self.input_path.exists():
            logger.info("Input file not found: %s — returning empty", self.input_path)
            return []
        try:
            with open(self.input_path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                logger.error("Input file is not a JSON array: %s", self.input_path)
                return []
            return data
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in %s: %s", self.input_path, e)
            return []

    def _validate_post(self, post: dict, seen_ids: set[str]) -> str | None:
        """Validate a single post against normative schema. Returns error message or None."""
        post_id = post.get("post_id", "")
        text = post.get("text", "")

        # post_id: REQUIRED, non-empty, unique
        if not post_id:
            return "missing required field: post_id"
        if post_id in seen_ids:
            return f"duplicate post_id: {post_id}"

        # text: REQUIRED, non-empty, min 10 chars
        if not text or len(text.strip()) < 10:
            return f"text too short or missing (post_id={post_id})"

        # group_name: OPTIONAL, default ""
        if "group_name" not in post:
            post["group_name"] = ""

        # author_name: OPTIONAL, default "" — NEVER propagated to output

        # posted_at: OPTIONAL, ISO 8601 if present, default null
        posted_at = post.get("posted_at")
        if posted_at:
            try:
                datetime.fromisoformat(posted_at.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                logger.warning(
                    "Invalid posted_at for %s: %s — treating as null",
                    post_id,
                    posted_at,
                )
                post["posted_at"] = None

        # has_images: OPTIONAL, default false — coerced to boolean
        post["has_images"] = bool(post.get("has_images", False))

        # raw_url: OPTIONAL, stored as-is in direct_url — no URL validation
        return None  # validation passed

    def _to_scraped_listing(self, post: dict, parsed: dict) -> ScrapedListing:
        """Map LLM output + post metadata to ScrapedListing."""
        summary = self._strip_pii(parsed)

        return ScrapedListing(
            source=self.source_id,
            source_listing_id=post.get("post_id", ""),
            source_search_url=str(self.input_path),
            title=self._build_title(parsed),
            price=parsed.get("price_ils"),
            currency="ILS",
            country="IL",
            available_from=parsed.get("available_from"),
            location_text=self._build_location(parsed),
            district=parsed.get("neighborhood") or parsed.get("city", ""),
            summary=summary,
            direct_url=post.get("raw_url", ""),
            url_status="direct" if post.get("raw_url") else "none",
            posted_date=self._parse_posted_at(post.get("posted_at")),
            vegan_signal=self._detect_vegan_signal(parsed),
            roommate_signal="",
        )

    def _strip_pii(self, parsed: dict) -> str:
        """Build summary from parsed data, stripping phone numbers."""
        parts = []
        if parsed.get("property_type"):
            parts.append(parsed["property_type"])
        if parsed.get("rooms"):
            parts.append(f"{parsed['rooms']} rooms")
        if parsed.get("city"):
            parts.append(parsed["city"])
        if parsed.get("key_features"):
            parts.append(", ".join(parsed["key_features"][:5]))
        summary = " · ".join(parts)
        return _PHONE_PATTERN.sub("[phone removed]", summary)

    def _build_title(self, parsed: dict) -> str:
        """Build title from parsed data."""
        ptype = parsed.get("property_type", "listing")
        rooms = parsed.get("rooms", "")
        city = parsed.get("city", "")
        if rooms:
            return f"{ptype} {rooms} חדרים ב{city}" if city else f"{ptype} {rooms} חדרים"
        return f"{ptype} ב{city}" if city else ptype

    def _build_location(self, parsed: dict) -> str:
        """Build location_text from parsed data."""
        parts = [parsed.get("street", ""), parsed.get("city", "")]
        return ", ".join(p for p in parts if p)

    def _parse_posted_at(self, raw: str | None) -> str | None:
        """Parse posted_at to date string."""
        if not raw:
            return None
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            logger.warning("Invalid posted_at format: %s", raw)
            return None

    def _detect_vegan_signal(self, parsed: dict) -> str:
        """Check key_features for vegan/vegetarian signals."""
        features = parsed.get("key_features", [])
        for f in features:
            if any(kw in f.lower() for kw in ("vegan", "\u05d8\u05d1\u05e2\u05d5\u05e0\u05d9", "\u05e6\u05de\u05d7\u05d5\u05e0\u05d9")):
                return f
        return ""

    # -- Deduplication --------------------------------------------------------

    def _deduplicate_against_existing(
        self, listings: list[ScrapedListing]
    ) -> list[ScrapedListing]:
        """Dedup against existing listings.json using fuzzy match."""
        existing_path = Path("data/listings.json")
        if not existing_path.exists():
            return listings

        try:
            with open(existing_path) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return listings

        unique: list[ScrapedListing] = []
        for listing in listings:
            if self._is_duplicate(listing, existing):
                logger.debug(
                    "Cross-source duplicate: %s", listing.source_listing_id
                )
                continue
            unique.append(listing)
        return unique

    def _is_duplicate(
        self, listing: ScrapedListing, existing: list[dict]
    ) -> bool:
        """Check if listing matches an existing one.

        Two-tier match:
          1. Same source + same source_listing_id -> exact duplicate.
          2. Cross-source fuzzy: location_text + price(+-10%) -> probable duplicate.
        """
        for ex in existing:
            # Tier 1: Same source, same ID -> exact duplicate
            if (
                ex.get("source") == self.source_id
                and ex.get("source_listing_id") == listing.source_listing_id
            ):
                return True

            # Tier 2: Cross-source fuzzy — location + price(+-10%)
            ex_price = ex.get("price")
            if listing.price and ex_price:
                price_close = abs(listing.price - ex_price) <= listing.price * 0.10
            else:
                price_close = False

            loc_match = (
                listing.location_text
                and ex.get("location_text")
                and listing.location_text.lower()
                in ex.get("location_text", "").lower()
            )

            if price_close and loc_match:
                return True

        return False
