"""Scraper for unimarkt.ch — uses tRPC JSON API (Next.js / Supabase backend).

Flow:
  1. GET /api/trpc/post.getPublicList?input={...} → tRPC JSON payload
  2. Parse response: result.data.json.posts → list of post dicts
  3. Paginate using page/limit params if hasMore is True
  4. Map each post dict → ScrapedListing

robots.txt check (2026-05-05):
  Site was unreachable from scraper host (connection timeout); robots.txt could not
  be fetched. Implementing in fixture-compatible mode. Live access skipped.
  Result: UNKNOWN (fixture-only mode active)

API discovery (team_00 research, 2026-05-05):
  URL: https://www.unimarkt.ch/api/trpc/post.getPublicList
  Method: GET (tRPC query)
  WG-Zimmer category UUID: e70b7bef-981e-4410-9780-7d14db95c2f4
  Housing parent UUID:      bff9562f-1f3a-475e-afe1-0e56ba0f72ac
  tRPC envelope: result.data.json
  10 Basel WG listings confirmed live (by team_00 research agent)
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any
from urllib.parse import urlencode

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.unimarkt.ch"
_TRPC_ENDPOINT = f"{_BASE_URL}/api/trpc/post.getPublicList"

# WG-Zimmer category UUID (Supabase-backed enum value)
_WG_CATEGORY_ID = "e70b7bef-981e-4410-9780-7d14db95c2f4"

_POLITE_DELAY = 5.0  # seconds between paginated requests (per task spec)
_PAGE_LIMIT = 50

_ZIP_DISTRICT: dict[str, str] = {
    "4001": "Innenstadt",
    "4002": "Innenstadt",
    "4051": "Altstadt",
    "4052": "Gundeli",
    "4053": "Bachletten",
    "4054": "Iselin",
    "4055": "St. Alban",
    "4056": "Matthäus",
    "4057": "Kleinbasel",
    "4058": "Kleinhüningen",
    "4059": "Allschwil-Grenze",
}

_VEGAN_KEYWORDS = ["vegan", "pflanzlich", "vegetarisch", "tierfreie"]

_TRAM_PATTERN = re.compile(r"\bTram\s*(\d+)\b", re.IGNORECASE)

# Fallback tram lines per Basel zip when description has no explicit mentions
_ZIP_TRAM: dict[str, list[str]] = {
    "4001": ["3", "8", "10", "11"],
    "4002": ["3", "8", "10"],
    "4051": ["3", "8", "11"],
    "4052": ["14", "16"],
    "4053": ["3", "6"],
    "4054": ["14", "16"],
    "4055": ["3", "10"],
    "4056": ["14", "16"],
    "4057": ["2", "3"],
    "4058": ["2", "14"],
}


class UnimarktScraper(BaseScraper):
    """Unimarkt.ch scraper using the tRPC JSON API.

    Polite delay: 5 seconds between paginated requests.
    transit_match_lines: extracted from description text where available,
    otherwise inferred from zip code.
    """

    #: City name passed to the API filter (unimarkt uses German city names)
    city_name_api: str = "Basel"

    def fetch_listings(self) -> list[ScrapedListing]:
        """Fetch all Basel WG listings from unimarkt.ch, paginating if needed."""
        results: list[ScrapedListing] = []
        page = 1

        while True:
            url = self._build_url(page=page)
            logger.debug("UnimarktScraper: fetching page %d — %s", page, url)
            try:
                resp = self._get(url)
                raw_json = resp.json()
            except Exception as exc:
                logger.warning(
                    "UnimarktScraper: failed to fetch page %d: %s", page, exc
                )
                break

            posts, has_more = self._extract_posts(raw_json)
            for post in posts:
                listing = self._parse_post(post)
                if listing is not None:
                    results.append(listing)

            if not has_more:
                break

            page += 1
            time.sleep(_POLITE_DELAY)

        logger.info("UnimarktScraper: fetched %d listings total.", len(results))
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_url(self, page: int = 1) -> str:
        """Build the tRPC GET URL with JSON-encoded input parameter."""
        input_payload: dict[str, Any] = {
            "json": {
                "categoryId": _WG_CATEGORY_ID,
                "city": self.city_name_api,
                "limit": _PAGE_LIMIT,
                "page": page,
            }
        }
        params = urlencode({"input": json.dumps(input_payload)})
        return f"{_TRPC_ENDPOINT}?{params}"

    @staticmethod
    def _extract_posts(raw: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
        """Extract the posts list and hasMore flag from a tRPC response envelope.

        tRPC response structure:
          { "result": { "data": { "json": { "posts": [...], "hasMore": bool } } } }
        """
        try:
            payload = raw["result"]["data"]["json"]
            posts = payload.get("posts") or []
            has_more = bool(payload.get("hasMore", False))
            return posts, has_more
        except (KeyError, TypeError):
            logger.warning(
                "UnimarktScraper: unexpected tRPC response structure: %s",
                str(raw)[:200],
            )
            return [], False

    def _parse_post(self, post: dict[str, Any]) -> ScrapedListing | None:
        """Convert a single unimarkt post dict to a ScrapedListing."""
        return self._parse_raw(post, source_search_url=self.search_url)

    @staticmethod
    def _parse_raw(
        post: dict[str, Any], *, source_search_url: str
    ) -> ScrapedListing | None:
        """Convert a raw unimarkt post dict to a ScrapedListing (static for testing)."""
        try:
            post_id = post.get("id") or ""
            if not post_id:
                return None

            title: str = (post.get("title") or "").strip() or f"Unimarkt #{post_id}"
            description: str = (post.get("description") or "").strip()

            slug: str = post.get("slug") or ""
            if slug:
                direct_url = f"{_BASE_URL}/immobilien/wg/{slug}-{post_id}"
            else:
                direct_url = f"{_BASE_URL}/immobilien/wg/{post_id}"

            zipcode: str = str(post.get("zip_code") or "")
            city_name: str = post.get("city") or "Basel"
            street: str = (post.get("street") or "").strip()

            location_text = (
                f"{street}, {zipcode} {city_name}"
                if street
                else f"{zipcode} {city_name}"
            )
            district = _ZIP_DISTRICT.get(zipcode, post.get("district") or city_name)

            price_raw = post.get("price")
            price: int | None = int(price_raw) if price_raw is not None else None

            available_from_raw = post.get("available_from")
            available_from: str | None = (
                str(available_from_raw) if available_from_raw else None
            )

            posted_date_raw = post.get("created_at")
            posted_date: str | None = (
                str(posted_date_raw) if posted_date_raw else None
            )

            # Transit: extract from description, fall back to zip lookup
            full_text = f"{title} {description}"
            tram_ids = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})
            if not tram_ids:
                tram_ids = _ZIP_TRAM.get(zipcode, [])

            # Vegan signal
            lower_text = full_text.lower()
            vegan_signal = "kein Signal"
            for kw in _VEGAN_KEYWORDS:
                if kw in lower_text:
                    vegan_signal = kw
                    break

            full_description = description
            summary = description[:300]

            return ScrapedListing(
                source="unimarkt",
                source_listing_id=str(post_id),
                source_search_url=source_search_url,
                title=title[:100],
                price=price,
                currency="CHF",
                country="CH",
                available_from=available_from,
                location_text=location_text,
                district=district,
                transit_match_lines=tram_ids,
                vegan_signal=vegan_signal,
                summary=summary,
                full_description=full_description,
                direct_url=direct_url,
                url_status="direct",
                recovery_query=f"site:unimarkt.ch {title[:40]} {city_name}",
                posted_date=posted_date,
            )
        except Exception:
            logger.exception(
                "UnimarktScraper: failed to parse post id=%s", post.get("id")
            )
            return None

    @staticmethod
    def _parse_listings_from_fixture(raw_json: dict[str, Any]) -> list[ScrapedListing]:
        """Parse listings from a fixture/API JSON dict (used in tests).

        Accepts the full tRPC response envelope or just the posts list.
        """
        # Accept full tRPC envelope
        if "result" in raw_json:
            posts, _ = UnimarktScraper._extract_posts(raw_json)
        # Accept bare posts list wrapper
        elif "posts" in raw_json:
            posts = raw_json["posts"]
        else:
            posts = []

        source_url = (
            f"{_TRPC_ENDPOINT}?input="
            + json.dumps({"json": {"categoryId": _WG_CATEGORY_ID, "city": "Basel"}})
        )
        results: list[ScrapedListing] = []
        for post in posts:
            listing = UnimarktScraper._parse_raw(post, source_search_url=source_url)
            if listing is not None:
                results.append(listing)
        return results
