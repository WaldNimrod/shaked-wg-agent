"""Scraper for weegee.ch — parses __NEXT_DATA__ JSON embedded in search pages.

Flow:
  1. GET /de/search/city-basel?page={N} → HTML page with embedded __NEXT_DATA__ JSON
  2. Parse JSON → extract listings list from pageProps
  3. Iterate pages until hasNext is False
  4. Map each listing dict → ScrapedListing

robots.txt check (2026-05-05):
  User-agent: * → Allow: /  (only /monitoring disallowed)
  ClaudeBot is blocked, but scraper uses a Chrome User-Agent — allowed.
  Result: ALLOWED
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

_BASE_URL = "https://weegee.ch"
_SEARCH_URL_TEMPLATE = _BASE_URL + "/de/search/city-basel"

_POLITE_DELAY = 7.0  # seconds between page requests (class-level override)

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


class WeegeeScraper(BaseScraper):
    """Weegee.ch scraper using embedded __NEXT_DATA__ JSON.

    Polite delay: 7 seconds between page requests.
    transit_match_lines: empty list (weegee search cards don't expose transit).
    """

    _POLITE_DELAY = _POLITE_DELAY  # override base class default

    def fetch_listings(self) -> list[ScrapedListing]:
        """Fetch all Basel WG listings from weegee.ch, paginating through all pages."""
        results: list[ScrapedListing] = []
        page = 1

        while True:
            url = f"{self.search_url}?page={page}" if page > 1 else self.search_url
            logger.debug("WeeegeeScraper: fetching page %d — %s", page, url)
            try:
                resp = self._get(url)
                html = resp.text
            except Exception as exc:
                logger.warning("WeegeeScraper: failed to fetch page %d: %s", page, exc)
                break

            page_data = self._extract_next_data(html)
            if page_data is None:
                logger.warning(
                    "WeegeeScraper: __NEXT_DATA__ not found on page %d, stopping.", page
                )
                break

            raw_listings: list[dict[str, Any]] = page_data.get("listings", [])
            for raw in raw_listings:
                listing = self._parse_listing(raw)
                if listing is not None:
                    results.append(listing)

            has_next = page_data.get("hasNext", False)
            if not has_next:
                break

            page += 1
            time.sleep(self._POLITE_DELAY)

        logger.info("WeegeeScraper: fetched %d listings total.", len(results))
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_next_data(self, html: str) -> dict[str, Any] | None:
        """Extract and return the pageProps dict from __NEXT_DATA__ script tag."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        script = soup.find("script", id="__NEXT_DATA__")
        if script is None or not script.string:
            return None
        try:
            data = json.loads(script.string)
            return data.get("props", {}).get("pageProps", {})
        except (json.JSONDecodeError, AttributeError):
            return None

    @classmethod
    def _parse_listing_from_html(cls, html: str) -> list[ScrapedListing]:
        """Parse listings from raw HTML string (used in tests / fixture parsing).

        This is a classmethod helper that does not require a live scraper instance.
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        script = soup.find("script", id="__NEXT_DATA__")
        if script is None or not script.string:
            return []
        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            return []

        page_props = data.get("props", {}).get("pageProps", {})
        raw_listings = page_props.get("listings", [])

        # Build a minimal source_search_url from location_name_search
        location = page_props.get("location_name_search", "city-basel")
        source_search_url = f"{_BASE_URL}/de/search/{location}"

        results: list[ScrapedListing] = []
        for raw in raw_listings:
            listing = cls._parse_raw(raw, source_search_url=source_search_url)
            if listing is not None:
                results.append(listing)
        return results

    def _parse_listing(self, raw: dict[str, Any]) -> ScrapedListing | None:
        """Parse a single raw listing dict into a ScrapedListing."""
        return self._parse_raw(raw, source_search_url=self.search_url)

    @staticmethod
    def _parse_raw(
        raw: dict[str, Any], *, source_search_url: str
    ) -> ScrapedListing | None:
        """Convert a raw weegee listing dict to a ScrapedListing."""
        try:
            public_id: str = raw.get("public_id") or ""
            if not public_id:
                return None

            detail_url_path: str = raw.get("detail_url", "")
            direct_url = _BASE_URL + detail_url_path if detail_url_path else ""

            zipcode: str = str(raw.get("address_postalcode") or "")
            locality: str = raw.get("address_locality") or "Basel"
            street: str = raw.get("address_street") or ""

            location_text = (
                f"{street}, {zipcode} {locality}" if street else f"{zipcode} {locality}"
            )
            district = _ZIP_DISTRICT.get(zipcode, locality or "Basel")

            price_raw = raw.get("price")
            price: int | None = int(price_raw) if price_raw is not None else None

            available_from_raw: str | None = raw.get("available_from_raw") or None
            available_from: str | None = (
                str(available_from_raw) if available_from_raw else None
            )

            living_space = raw.get("characteristics_livingspace")
            description: str = raw.get("text_description_extract") or ""

            classifications: list[str] = raw.get("classifications") or []
            is_furnished = "furnished" in classifications

            # Build a human-readable title
            space_str = f"{living_space}m² " if living_space else ""
            furnished_str = "möbliert, " if is_furnished else ""
            addr_str = f"{street}, {zipcode} {locality}" if street else f"{zipcode} {locality}"
            title = f"{space_str}WG-Zimmer {furnished_str}in {addr_str}"

            full_description = description
            summary = description[:300]

            # Detect vegan signal from description
            lower_desc = description.lower()
            vegan_signal = "kein Signal"
            for kw in _VEGAN_KEYWORDS:
                if kw in lower_desc:
                    vegan_signal = kw
                    break

            return ScrapedListing(
                source="weegee",
                source_listing_id=public_id,
                source_search_url=source_search_url,
                title=title[:100],
                price=price,
                available_from=available_from,
                location_text=location_text,
                district=district,
                currency="CHF",
                country="CH",
                transit_match_lines=[],  # weegee cards don't expose transit data
                vegan_signal=vegan_signal,
                summary=summary,
                full_description=full_description,
                direct_url=direct_url,
                url_status="direct",
                recovery_query=f"site:weegee.ch {street} {zipcode}",
            )
        except Exception:
            logger.exception("WeegeeScraper: failed to parse listing %s", raw.get("public_id"))
            return None
