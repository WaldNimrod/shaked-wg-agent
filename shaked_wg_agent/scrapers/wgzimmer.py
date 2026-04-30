"""DEPRECATED — wgzimmer.ch legacy HTTP scraper.

This module is superseded by `wgzimmer_pw.WgzimmerPlaywrightScraper`.

Reasons for deprecation:
1. wgzimmer.ch now requires reCAPTCHA v3 for all search results. Plain HTTP GET/POST
   requests without a valid browser-issued token are blocked.
2. This class contains a runtime bug: `ScrapedListing(price_chf=...)` — the field is
   named `price`, not `price_chf`. The class would raise TypeError on any parsed item.
3. The DOM selectors (`li.search-result-entry`) do not match the current site HTML.
   The correct selector is `li.search-mate-entry`.

Do NOT invoke this class. Use `WgzimmerPlaywrightScraper` from `wgzimmer_pw` instead.
If Playwright cannot obtain a valid reCAPTCHA token, consider: reducing scrape frequency,
requesting API access from wgzimmer.ch, or switching to an alternative source
(e.g. Homegate.ch).
"""
from __future__ import annotations

import re
from typing import Any

import requests

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

_BASE_URL = "https://www.wgzimmer.ch"
_TRAM_PATTERN = re.compile(r"\bTram\s*(\d+)\b", re.IGNORECASE)
_PRICE_PATTERN = re.compile(r"(\d{3,4})\s*(?:CHF|Fr\.?)", re.IGNORECASE)
_VEGAN_KEYWORDS = ["vegan", "pflanzlich", "vegetarisch", "tierfreie", "kein fleisch"]


class WgzimmerScraper(BaseScraper):
    """Scraper for wgzimmer.ch Basel search results."""

    def fetch_listings(self) -> list[ScrapedListing]:
        """Fetch listings from wgzimmer.ch search page."""
        try:
            resp = self._get(self.search_url)
        except requests.RequestException:
            return []

        soup = self._soup(resp.text)
        results: list[ScrapedListing] = []

        # wgzimmer.ch lists results in <li class="..."> containers
        for item in soup.select("li.search-result-entry, li[class*='result']"):
            listing = self._parse_item(item)
            if listing:
                results.append(listing)

        return results

    def _parse_item(self, item: Any) -> ScrapedListing | None:
        """Parse a single search result <li> into a ScrapedListing."""
        try:
            # Title / link
            link_tag = item.select_one("a[href]")
            if not link_tag:
                return None
            href = link_tag.get("href", "")
            title = link_tag.get_text(strip=True)
            if not title:
                return None

            direct_url = f"{_BASE_URL}{href}" if href.startswith("/") else href
            source_listing_id = re.search(r"(\d{5,})", href)
            sid = source_listing_id.group(1) if source_listing_id else href.split("/")[-1]

            # Price
            price_tag = item.select_one("[class*='price'], [class*='cost'], [class*='miete']")
            price_text = price_tag.get_text(strip=True) if price_tag else ""
            price = self._extract_price(price_text or item.get_text())

            # Location
            loc_tag = item.select_one("[class*='location'], [class*='ort'], [class*='district']")
            location_text = loc_tag.get_text(strip=True) if loc_tag else ""

            # Tram lines
            full_text = item.get_text(" ", strip=True)
            tram_lines = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})

            # Vegan signal
            vegan = self._detect_vegan(full_text)

            # Roommate signal
            roommate_tag = item.select_one("[class*='roommate'], [class*='mitbewohner']")
            roommate_signal = roommate_tag.get_text(strip=True) if roommate_tag else ""

            # Available from
            avail_tag = item.select_one("[class*='available'], [class*='bezug'], [class*='frei']")
            available_from = avail_tag.get_text(strip=True) if avail_tag else None

            return ScrapedListing(
                source=self.source_id,
                source_listing_id=sid,
                source_search_url=self.search_url,
                title=title,
                price_chf=price,
                available_from=available_from,
                location_text=location_text,
                district=self._extract_district(location_text),
                transit_match_lines=tram_lines,
                roommate_signal=roommate_signal,
                vegan_signal=vegan,
                summary=full_text[:200],
                direct_url=direct_url,
                url_status="direct",
                recovery_query=f"site:wgzimmer.ch WG Zimmer Basel {title[:40]}",
            )
        except Exception:
            return None

    @staticmethod
    def _extract_price(text: str) -> int | None:
        m = _PRICE_PATTERN.search(text)
        return int(m.group(1)) if m else None

    @staticmethod
    def _detect_vegan(text: str) -> str:
        lower = text.lower()
        for kw in _VEGAN_KEYWORDS:
            if kw in lower:
                return kw
        return "kein Signal"

    @staticmethod
    def _extract_district(location_text: str) -> str:
        """Best-effort district extraction from location string."""
        known = [
            "Gundeli", "Gundeldingens", "Kleinbasel", "Innenstadt",
            "St. Johann", "Matthäus", "Iselin", "Breite", "Bachletten",
            "Altstadt", "Vorstädte", "Clara", "Wettstein",
        ]
        for district in known:
            if district.lower() in location_text.lower():
                return district
        return location_text.split(",")[0].strip() if location_text else ""
