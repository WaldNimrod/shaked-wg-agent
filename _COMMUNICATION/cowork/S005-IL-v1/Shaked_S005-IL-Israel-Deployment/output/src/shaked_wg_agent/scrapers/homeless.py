"""Scraper for homeless.co.il — Israeli rental classifieds.

Uses Playwright to bypass Cloudflare managed challenge.
Follow wgzimmer_pw.py pattern for browser lifecycle.

Board URL: https://www.homeless.co.il/rent/
Area filter: /rent/inumber1=AREA_ID
Listing rows: <tr id="ad_NNNNNN" type="ad">
"""
from __future__ import annotations

import re
from typing import Any

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

_BASE_URL = "https://www.homeless.co.il"
_AD_ROW_PATTERN = re.compile(r"^ad_(\d+)$")


class HomelessScraper(BaseScraper):
    """Scraper for homeless.co.il Israeli rental classifieds.

    Uses Playwright to bypass Cloudflare managed challenge.
    Follow wgzimmer_pw.py pattern for browser lifecycle.
    """

    MAX_PAGES = 5  # Safety limit on pagination
    _WAIT_SECONDS = 8  # Wait for Cloudflare challenge to resolve

    def fetch_listings(self) -> list[ScrapedListing]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return []

        results: list[ScrapedListing] = []
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                try:
                    ctx = browser.new_context(
                        locale="he-IL",
                        user_agent=(
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/122.0.0.0 Safari/537.36"
                        ),
                    )
                    page = ctx.new_page()
                    # Remove webdriver detection (Cloudflare stealth)
                    page.add_init_script(
                        "Object.defineProperty(navigator, 'webdriver', "
                        "{get: () => undefined})"
                    )

                    for page_num in range(1, self.MAX_PAGES + 1):
                        url = self._page_url(page_num)
                        page.goto(url, wait_until="domcontentloaded")
                        page.wait_for_timeout(self._WAIT_SECONDS * 1000)
                        html = page.content()
                        soup = self._soup(html)
                        rows = self._parse_listing_rows(soup)
                        if not rows:
                            break
                        results.extend(rows)
                        if not self._has_next_page(soup, page_num):
                            break
                finally:
                    browser.close()
        except Exception:
            pass  # Return whatever we collected
        return results

    def _page_url(self, page_num: int) -> str:
        """Build URL for a given page number."""
        if page_num == 1:
            return self.search_url
        base = self.search_url.rstrip("/")
        return f"{base}/{page_num}"

    def _parse_listing_rows(self, soup: Any) -> list[ScrapedListing]:
        """Parse all listing rows from the board page HTML."""
        listings: list[ScrapedListing] = []
        for row in soup.find_all("tr", id=_AD_ROW_PATTERN):
            try:
                parsed = self._parse_row(row)
                if parsed is not None:
                    listings.append(parsed)
            except Exception:
                continue  # Skip unparseable rows
        return listings

    def _parse_row(self, row: Any) -> ScrapedListing | None:
        """Parse a single <tr id="ad_NNNNNN"> row into a ScrapedListing."""
        row_id = row.get("id", "")
        m = _AD_ROW_PATTERN.match(row_id)
        if not m:
            return None
        ad_id = m.group(1)

        cells = row.find_all("td")
        if len(cells) < 11:
            return None

        # Skip first 2 cells (checkbox, image)
        # Cells 3-11: property_type, city, neighborhood, street, rooms, floor,
        #             price, entry_date, update_date
        property_type = cells[2].get_text(strip=True)
        city = cells[3].get_text(strip=True)
        neighborhood = cells[4].get_text(strip=True)
        street = cells[5].get_text(strip=True)
        rooms = cells[6].get_text(strip=True)
        floor = cells[7].get_text(strip=True)
        price_text = cells[8].get_text(strip=True)
        entry_date_text = cells[9].get_text(strip=True)
        update_date_text = cells[10].get_text(strip=True)

        # Parse fields
        price = self._parse_price(price_text)
        available_from = self._parse_date(entry_date_text)
        posted_date = self._parse_date(update_date_text)

        # Build direct URL
        direct_url = f"{_BASE_URL}/rent/viewad,{ad_id}.aspx"

        # Build location_text: "{street}, {city}" (omit street if empty)
        if street:
            location_text = f"{street}, {city}"
        else:
            location_text = city

        # Build district: neighborhood (or city if neighborhood empty)
        district = neighborhood if neighborhood else city

        # Build title: "{property_type} {rooms} חדרים ב{city}" (Hebrew)
        title = f"{property_type} {rooms} חדרים ב{city}"

        # Build summary: "{property_type} · {rooms} חדרים · קומה {floor}"
        summary = f"{property_type} · {rooms} חדרים · קומה {floor}"

        return ScrapedListing(
            source=self.source_id,
            source_listing_id=ad_id,
            source_search_url=self.search_url,
            title=title,
            price=price,
            currency=self.city.currency,
            country=self.city.country,
            available_from=available_from,
            location_text=location_text,
            district=district,
            transit_match_lines=[],
            roommate_signal="",
            vegan_signal="",
            summary=summary,
            direct_url=direct_url,
            url_status="direct",
            recovery_query=f"site:homeless.co.il {title[:40]}",
            posted_date=posted_date,
        )

    def _has_next_page(self, soup: Any, current_page: int) -> bool:
        """Check if paging div contains a link to the next page."""
        paging = soup.find("div", id="paging")
        if not paging:
            return False
        next_page = current_page + 1
        for link in paging.find_all("a", href=True):
            href = link.get("href", "")
            if href.rstrip("/").endswith(f"/{next_page}"):
                return True
        return False

    @staticmethod
    def _parse_price(text: str) -> int | None:
        """Parse price from 'N,NNN ₪' format to int, or None."""
        text = text.strip()
        if not text:
            return None
        # Remove ₪ symbol and commas
        cleaned = text.replace("₪", "").replace(",", "").strip()
        try:
            return int(cleaned)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_date(text: str) -> str | None:
        """Parse date: 'מיידי' → None, DD/MM/YYYY → 'YYYY-MM-DD'."""
        text = text.strip()
        if not text or "מיידי" in text:
            return None
        # Try DD/MM/YYYY format
        m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
        if m:
            day, month, year = m.group(1), m.group(2), m.group(3)
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return None
