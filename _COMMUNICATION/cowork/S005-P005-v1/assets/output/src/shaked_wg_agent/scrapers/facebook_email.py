"""Facebook email notification scraper — parses FB group emails via IMAP or .eml files.

Reads Facebook group notification emails from an IMAP mailbox or local .eml files,
extracts post snippets from notification HTML, feeds them through the WP002 LLM parser,
deduplicates across sources, and outputs ScrapedListing entries.

All IMAP credentials come from env vars only — inline secrets are forbidden.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import urllib.parse
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing
from shaked_wg_agent.parsers.llm_listing_parser import check_llm_config, parse_rental_post

logger = logging.getLogger(__name__)

_PHONE_PATTERN = re.compile(r"0\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}")


class EmailFacebookScraper(BaseScraper):
    """Facebook email notification scraper — parses FB group emails via IMAP or .eml files."""

    _FB_SENDER = "notification@facebookmail.com"
    _MIN_SNIPPET_LENGTH = 50
    _PROCESSED_IDS_FILE = Path("data/facebook/processed_email_ids.json")

    def __init__(self, source_id: str, search_url: str, city: Any) -> None:
        super().__init__(source_id, search_url, city)
        self._is_imap = search_url.startswith("imap://")
        self._processed_ids = self._load_processed_ids()

    def fetch_listings(self) -> list[ScrapedListing]:
        """Main pipeline: fetch emails -> extract snippets -> LLM parse -> dedup -> return.

        Never raises. Returns [] on any run-level failure.
        """
        # Step 1: Check LLM config (required for parsing)
        if not check_llm_config():
            logger.warning("No LLM API key; facebook-email scraper disabled")
            return []

        # Step 2: Get email messages
        if self._is_imap:
            messages = self._fetch_imap()
        else:
            messages = self._read_eml_files()

        if not messages:
            return []

        # Step 3: Extract post snippets from emails
        snippets: list[dict] = []
        for msg in messages:
            msg_id = msg.get("message_id", "")

            # Dedup layer 1: message-ID
            if msg_id in self._processed_ids:
                continue

            extracted = self._parse_email_html(
                msg.get("html_body", ""), msg.get("subject", "")
            )
            for snippet in extracted:
                snippet["message_id"] = msg_id
                snippet["email_date"] = msg.get("date", "")
                snippets.append(snippet)

            # Mark as processed
            self._processed_ids.add(msg_id)

        # Step 4: Dedup layers 2-3
        snippets = self._dedup_snippets(snippets)

        # Step 5: LLM parse each snippet
        listings: list[ScrapedListing] = []
        for snippet in snippets:
            if len(snippet.get("text", "")) < self._MIN_SNIPPET_LENGTH:
                logger.debug(
                    "Snippet too short (%d chars), skipping",
                    len(snippet.get("text", "")),
                )
                continue

            parsed = parse_rental_post(
                snippet["text"], snippet.get("group_name", ""),
                post_id=snippet.get("message_id", ""),
            )
            if parsed is None:
                continue
            if not parsed.get("is_rental_offer", False):
                continue

            listing = self._to_scraped_listing(snippet, parsed)
            listings.append(listing)

        # Step 6: Save processed IDs
        self._save_processed_ids()

        return listings

    # -- IMAP Connection & Fetching -------------------------------------------

    def _get_imap_config(self) -> tuple[str, str, str, str] | None:
        """Return (host, user, password, folder) or None if not configured."""
        host = os.environ.get("SHAKED_EMAIL_HOST", "")
        user = os.environ.get("SHAKED_EMAIL_USER", "")
        password = os.environ.get("SHAKED_EMAIL_PASS", "")

        if not all([host, user, password]):
            logger.warning(
                "IMAP not configured: SHAKED_EMAIL_HOST/USER/PASS required"
            )
            return None

        # Extract folder from search_url: imap://env/INBOX -> "INBOX"
        folder = (
            self.search_url.split("/")[-1] if "/" in self.search_url else "INBOX"
        )
        return (host, user, password, folder)

    def _fetch_imap(self) -> list[dict]:
        """Connect to IMAP, fetch unread Facebook notification emails."""
        config = self._get_imap_config()
        if config is None:
            return []

        host, user, password, folder = config
        messages = []

        try:
            import imaplib
            import email as email_lib

            conn = imaplib.IMAP4_SSL(host, timeout=30)
            try:
                conn.login(user, password)
                conn.select(folder)

                # Search for unread emails from Facebook
                _, msg_nums = conn.search(
                    None, '(UNSEEN FROM "facebookmail.com")'
                )
                if not msg_nums[0]:
                    return []

                for num in msg_nums[0].split():
                    _, msg_data = conn.fetch(num, "(RFC822)")
                    raw_email = msg_data[0][1]
                    msg = email_lib.message_from_bytes(raw_email)

                    parsed = {
                        "message_id": msg.get("Message-ID", ""),
                        "subject": msg.get("Subject", ""),
                        "date": msg.get("Date", ""),
                        "html_body": self._extract_html_body(msg),
                    }
                    messages.append(parsed)

                    # Mark as read
                    conn.store(num, "+FLAGS", "\\Seen")

                conn.close()
            finally:
                conn.logout()

        except imaplib.IMAP4.error as e:
            logger.error("IMAP error: %s", e)
        except Exception as e:
            logger.error("IMAP connection failed: %s", e)

        return messages

    def _extract_html_body(self, msg: Any) -> str:
        """Extract HTML body from email message (multipart or simple)."""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    charset = part.get_content_charset() or "utf-8"
                    return part.get_payload(decode=True).decode(
                        charset, errors="replace"
                    )
        elif msg.get_content_type() == "text/html":
            charset = msg.get_content_charset() or "utf-8"
            return msg.get_payload(decode=True).decode(charset, errors="replace")
        return ""

    # -- File Mode (.eml reading) ---------------------------------------------

    def _read_eml_files(self) -> list[dict]:
        """Read .eml files from a directory."""
        import email as email_lib

        dir_path = Path(self.search_url)
        if not dir_path.exists() or not dir_path.is_dir():
            logger.info("Email directory not found: %s", dir_path)
            return []

        messages = []
        for filepath in sorted(dir_path.glob("*.eml")):
            try:
                with open(filepath, "rb") as f:
                    msg = email_lib.message_from_bytes(f.read())
                parsed = {
                    "message_id": msg.get("Message-ID", "") or filepath.stem,
                    "subject": msg.get("Subject", ""),
                    "date": msg.get("Date", ""),
                    "html_body": self._extract_html_body(msg),
                }
                messages.append(parsed)
            except Exception as e:
                logger.warning("Failed to parse %s: %s", filepath, e)

        return messages

    # -- Facebook Email HTML Parsing ------------------------------------------

    def _parse_email_html(self, html: str, subject: str) -> list[dict]:
        """Extract post snippets from Facebook notification email HTML.

        Returns list of dicts with keys: text, group_name, group_url, post_url
        """
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        snippets = []

        group_name = self._extract_group_name(subject)

        # Strategy 1: Look for post content blocks
        for block in self._find_post_blocks(soup):
            text = block.get("text", "").strip()
            if text:
                snippets.append(
                    {
                        "text": text,
                        "group_name": group_name,
                        "group_url": block.get("group_url", ""),
                        "post_url": block.get("post_url", ""),
                    }
                )

        return snippets

    def _find_post_blocks(self, soup: Any) -> list[dict]:
        """Find post content blocks in Facebook email HTML."""
        blocks = []

        # Primary: links to facebook.com/groups/.../posts/...
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if "/groups/" in href and "/posts/" in href:
                parent_td = link.find_parent("td")
                if parent_td:
                    text = parent_td.get_text(separator="\n", strip=True)
                    # Remove "See post" / "View post" link text
                    text = re.sub(
                        r"\b(See|View)\s+(post|more)\b",
                        "",
                        text,
                        flags=re.IGNORECASE,
                    ).strip()
                    if text:
                        blocks.append(
                            {
                                "text": text,
                                "post_url": self._clean_fb_url(href),
                                "group_url": "",
                            }
                        )

        # Fallback: if no post links found, try generic content blocks
        if not blocks:
            for td in soup.find_all("td"):
                text = td.get_text(strip=True)
                if len(text) > 80 and any(
                    kw in text
                    for kw in (
                        "\u05d7\u05d3\u05e8",
                        "\u05d3\u05d9\u05e8\u05d4",
                        "\u05dc\u05d4\u05e9\u05db\u05e8\u05d4",
                        "\u05e9\u05db\u05d9\u05e8\u05d5\u05ea",
                        "room",
                        "apartment",
                    )
                ):
                    blocks.append(
                        {
                            "text": text,
                            "post_url": "",
                            "group_url": "",
                        }
                    )

        return blocks

    def _extract_group_name(self, subject: str) -> str:
        """Extract group name from email subject."""
        patterns = [
            r"(?:New post|new posts|Popular posts?) in (.+)",
            r"\u05e4\u05d5\u05e1\u05d8 \u05d7\u05d3\u05e9 \u05d1\u05e7\u05d1\u05d5\u05e6\u05d4 (.+)",
            r"\u05e4\u05d5\u05e1\u05d8\u05d9\u05dd \u05d7\u05d3\u05e9\u05d9\u05dd \u05d1\u05e7\u05d1\u05d5\u05e6\u05d4 (.+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, subject, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return subject

    def _clean_fb_url(self, url: str) -> str:
        """Remove Facebook tracking params from URL."""
        if "l.facebook.com/l.php" in url:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            if "u" in params:
                return params["u"][0]
        return url.split("?")[0]  # Strip query params

    # -- Deduplication Pipeline -----------------------------------------------

    def _load_processed_ids(self) -> set[str]:
        """Load previously processed email message IDs."""
        if self._PROCESSED_IDS_FILE.exists():
            try:
                with open(self._PROCESSED_IDS_FILE) as f:
                    return set(json.load(f))
            except (json.JSONDecodeError, TypeError):
                return set()
        return set()

    def _save_processed_ids(self) -> None:
        """Persist processed email IDs to disk."""
        self._PROCESSED_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self._PROCESSED_IDS_FILE, "w") as f:
            json.dump(sorted(self._processed_ids), f, indent=2)

    def _dedup_snippets(self, snippets: list[dict]) -> list[dict]:
        """Dedup within batch: URL exact match (P2) and text hash (P3)."""
        seen_urls: set[str] = set()
        seen_hashes: set[str] = set()
        unique = []

        for s in snippets:
            # P2: URL exact match
            url = s.get("post_url", "")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)

            # P3: Text hash
            text_hash = hashlib.sha256(
                s.get("text", "").strip().encode()
            ).hexdigest()
            if text_hash in seen_hashes:
                continue
            seen_hashes.add(text_hash)

            unique.append(s)

        return unique

    # -- Output Mapping -------------------------------------------------------

    def _to_scraped_listing(
        self, snippet: dict, parsed: dict
    ) -> ScrapedListing:
        """Map LLM output + snippet metadata to ScrapedListing."""
        summary = self._strip_pii(parsed)

        return ScrapedListing(
            source=self.source_id,
            source_listing_id=hashlib.sha256(
                snippet.get("post_url", snippet.get("text", "")).encode()
            ).hexdigest()[:16],
            source_search_url="email:" + snippet.get("message_id", ""),
            title=self._build_title(parsed),
            price=parsed.get("price_ils"),
            currency="ILS",
            country="IL",
            available_from=parsed.get("available_from"),
            location_text=self._build_location(parsed),
            district=parsed.get("neighborhood") or parsed.get("city", ""),
            summary=summary,
            direct_url=snippet.get("post_url", ""),
            url_status="direct" if snippet.get("post_url") else "none",
            posted_date=self._parse_email_date(snippet.get("email_date")),
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
        summary = " \u00b7 ".join(parts)
        return _PHONE_PATTERN.sub("[phone removed]", summary)

    def _build_title(self, parsed: dict) -> str:
        """Build title from parsed data."""
        ptype = parsed.get("property_type", "listing")
        rooms = parsed.get("rooms", "")
        city = parsed.get("city", "")
        if rooms:
            return (
                f"{ptype} {rooms} \u05d7\u05d3\u05e8\u05d9\u05dd \u05d1{city}"
                if city
                else f"{ptype} {rooms} \u05d7\u05d3\u05e8\u05d9\u05dd"
            )
        return f"{ptype} \u05d1{city}" if city else ptype

    def _build_location(self, parsed: dict) -> str:
        """Build location_text from parsed data."""
        parts = [parsed.get("street", ""), parsed.get("city", "")]
        return ", ".join(p for p in parts if p)

    def _parse_email_date(self, raw: str | None) -> str | None:
        """Parse email Date header to date string."""
        if not raw:
            return None
        try:
            import email.utils
            parsed = email.utils.parsedate_to_datetime(raw)
            return parsed.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    def _detect_vegan_signal(self, parsed: dict) -> str:
        """Check key_features for vegan/vegetarian signals."""
        features = parsed.get("key_features", [])
        for f in features:
            if any(
                kw in f.lower()
                for kw in ("vegan", "\u05d8\u05d1\u05e2\u05d5\u05e0\u05d9", "\u05e6\u05de\u05d7\u05d5\u05e0\u05d9")
            ):
                return f
        return ""
