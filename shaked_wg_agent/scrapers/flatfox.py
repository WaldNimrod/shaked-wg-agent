"""Scraper for flatfox.ch — Swiss platform for Basel WG listings."""
from __future__ import annotations

import re
from typing import Any

import requests

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

_BASE_URL = "https://flatfox.ch"
_TRAM_PATTERN = re.compile(r"\bTram\s*(\d+)\b", re.IGNORECASE)
_PRICE_PATTERN = re.compile(r"(\d{3,4})\s*(?:CHF|Fr\.?|/Mt\.?)", re.IGNORECASE)
_VEGAN_KEYWORDS = ["vegan", "pflanzlich", "vegetarisch", "tierfreie"]


class FlatfoxScraper(BaseScraper):
    """Scraper for flatfox.ch Basel search results."""

    def fetch_listings(self) -> list[ScrapedListing]:
        """Fetch listings from flatfox.ch search page."""
        try:
            resp = self._get(self.search_url)
        except requests.RequestException:
            return []

        soup = self._soup(resp.text)
        results: list[ScrapedListing] = []

        # Flatfox uses card-based layout
        for item in soup.select(
            "div.listing-item, div[class*='flat-card'], article[class*='listing']"
        ):
            listing = self._parse_item(item)
            if listing:
                results.append(listing)

        return results

    def _parse_item(self, item: Any) -> ScrapedListing | None:
        """Parse a single listing card into a ScrapedListing."""
        try:
            link_tag = item.select_one("a[href*='/flat/'], a[href]")
            if not link_tag:
                return None
            href = link_tag.get("href", "")
            title_tag = item.select_one("h2, h3, [class*='title']")
            title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
            if not title:
                return None

            direct_url = f"{_BASE_URL}{href}" if href.startswith("/") else href
            flat_id_m = re.search(r"/flat/(\d+)", href)
            sid = flat_id_m.group(1) if flat_id_m else href.strip("/").split("/")[-1]

            full_text = item.get_text(" ", strip=True)
            price = self._extract_price(full_text)
            tram_lines = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})
            vegan = self._detect_vegan(full_text)

            loc_tag = item.select_one("[class*='location'], [class*='address'], [class*='city']")
            location_text = loc_tag.get_text(strip=True) if loc_tag else ""

            avail_tag = item.select_one("[class*='available'], [class*='move']")
            available_from = avail_tag.get_text(strip=True) if avail_tag else None

            return ScrapedListing(
                source=self.source_id,
                source_listing_id=sid,
                source_search_url=self.search_url,
                title=title,
                price_chf=price,
                available_from=available_from,
                location_text=location_text,
                district=location_text.split(",")[0].strip(),
                tram_match_lines=tram_lines,
                vegan_signal=vegan,
                summary=full_text[:200],
                direct_url=direct_url,
                url_status="direct" if "/flat/" in href else "search_only",
                recovery_query=f"site:flatfox.ch WG Zimmer Basel {title[:40]}",
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
