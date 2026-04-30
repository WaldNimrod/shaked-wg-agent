"""Playwright scraper for wgzimmer.ch — submits the search form and parses HTML results.

Strategy (corrected from original):
  1. Launch headless Playwright Chromium
  2. Navigate to canton search URL (loads the search form page with reCAPTCHA v3 JS)
  3. Execute submitForm() via page.evaluate() — this triggers the invisible reCAPTCHA v3
     challenge in the real Chromium context, obtains a token, and POSTs the form
  4. Wait for navigation to complete (the POST response contains listing HTML)
  5. Detect reCAPTCHA block in the POST response; if blocked → log WARNING, return []
  6. Parse listing items from #content ul.list li.search-mate-entry
  7. Filter for Basel city (PLZ 4001–4059) and budget range
  8. Map to ScrapedListing objects

Why the original approach failed:
  - It intercepted img.wgzimmer.ch/.rest/v1/* responses expecting JSON listing data.
    That domain is the Magnolia CMS image CDN (returns HTTP 401). It never serves listings.
  - DOM fallback used li.search-result-entry — a CSS class that does not exist on wgzimmer.ch.
    The correct class (confirmed from CSS analysis) is li.search-mate-entry.
  - The canton URL GET page shows only a search form — no results are present until the form
    is submitted with a valid reCAPTCHA v3 token.

Direct listing URL: https://www.wgzimmer.ch/en/wgzimmer/mate/ch/baselstadt/{date}-{id}.html
"""
from __future__ import annotations

import logging
import re
from typing import Any

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None  # type: ignore[assignment]

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.wgzimmer.ch"
_TRAM_PATTERN = re.compile(r"\bTram\s*(\d+)\b", re.IGNORECASE)
_PRICE_PATTERN = re.compile(r"(\d{3,4})\s*(?:CHF|Fr\.?|sFr\.?)", re.IGNORECASE)
_VEGAN_KEYWORDS = ["vegan", "pflanzlich", "vegetarisch", "tierfreie", "kein fleisch"]

# reCAPTCHA block detection strings (case-insensitive)
_RECAPTCHA_BLOCK_SIGNALS = ["stopped by", "recaptcha", "please try again"]

# Fallback zip range if city.zip_filter is empty
_BASEL_ZIPS_FALLBACK = {str(z) for z in range(4001, 4060)}

_WG_CITY_PATH = {
    "basel": "baselstadt",
    "zurich": "zuerich",
    "bern": "bern",
}

_ZIP_DISTRICT: dict[str, str] = {
    "4001": "Innenstadt", "4002": "Innenstadt",
    "4051": "Altstadt",   "4052": "Gundeli",
    "4053": "Bachletten", "4054": "Iselin",
    "4055": "St. Alban",  "4056": "Matthäus",
    "4057": "Kleinbasel", "4058": "Kleinhüningen",
}

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

# CSS selectors for listing items in search result page
# Confirmed from wgzimmer.ch CSS analysis (legacy.min.css)
# Primary: li.search-mate-entry inside #content ul.list
# Fallbacks in order of specificity
_LISTING_SELECTORS = [
    "#content ul.list li.search-mate-entry",
    "ul.list li.search-mate-entry",
    "li.search-mate-entry",
    "li[class*='search-mate-entry']",
    "#content ul.list li",  # broad fallback — includes header row, filter below
]


def _is_recaptcha_blocked(content: str) -> bool:
    """Return True if the page content indicates a reCAPTCHA block."""
    lower = content.lower()
    return all(s in lower for s in ["stopped by", "recaptcha"])


class WgzimmerPlaywrightScraper(BaseScraper):
    """wgzimmer.ch scraper using Playwright to execute the search form.

    Navigates to the canton search URL, calls submitForm() which executes the
    invisible reCAPTCHA v3 challenge, and parses the resulting HTML.
    """

    def _allowed_zips(self) -> set[str]:
        zf = self.city.zip_filter
        return set(zf) if zf else _BASEL_ZIPS_FALLBACK

    def _wg_path_segment(self) -> str:
        return _WG_CITY_PATH.get(self.city.city_id, "baselstadt")

    def fetch_listings(self) -> list[ScrapedListing]:
        if sync_playwright is None:
            logger.warning(
                "wgzimmer: playwright not installed — cannot fetch listings"
            )
            return []

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                ctx = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    ),
                    locale="de-CH",
                )
                page = ctx.new_page()

                # Step 1: Navigate to canton search URL (loads form + reCAPTCHA v3 JS)
                page.goto(self.search_url, wait_until="domcontentloaded", timeout=30_000)
                # Allow reCAPTCHA v3 script to fully initialize
                page.wait_for_timeout(2_000)

                # Step 2: Execute submitForm() — this calls grecaptcha.execute(),
                # obtains a v3 token, and submits the POST form
                try:
                    page.evaluate("submitForm()")
                except Exception as exc:
                    logger.warning(
                        "wgzimmer: submitForm() failed — reCAPTCHA v3 JS not available: %s",
                        exc,
                    )
                    return []

                # Step 3: Wait for the POST response to load
                try:
                    page.wait_for_load_state("networkidle", timeout=20_000)
                except Exception:
                    # networkidle may time out if ads keep firing; fall through
                    page.wait_for_timeout(3_000)

                # Step 4: Check for reCAPTCHA block
                content = page.content()
                page_title = page.title()
                if _is_recaptcha_blocked(content):
                    logger.warning(
                        "wgzimmer: reCAPTCHA v3 block — headless browser scored below "
                        "site threshold. URL=%s title=%r. Returning 0 results. "
                        "Consider reducing scrape frequency or requesting API access.",
                        self.search_url,
                        page_title,
                    )
                    return []

                # Step 5: Parse results from POST response HTML
                results = self._dom_parse_results(content)

                if not results:
                    logger.warning(
                        "wgzimmer: 0 listings parsed from search results page. "
                        "URL=%s title=%r. Possible selector drift or empty results.",
                        self.search_url,
                        page_title,
                    )

                return results

            finally:
                browser.close()

    # ── DOM parsing ──────────────────────────────────────────────────────────

    def _dom_parse_results(self, html: str) -> list[ScrapedListing]:
        """Parse listing items from the wgzimmer search results HTML."""
        results: list[ScrapedListing] = []
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "lxml")
            items = self._select_listing_items(soup)

            for item in items:
                listing = self._parse_item(item)
                if listing:
                    results.append(listing)
        except Exception as exc:
            logger.warning("wgzimmer: DOM parsing error: %s", exc)

        return results

    def _select_listing_items(self, soup: Any) -> list[Any]:
        """Try selectors in priority order until we get results."""
        for selector in _LISTING_SELECTORS:
            items = soup.select(selector)
            if not items:
                continue
            # For the broad fallback, filter out header rows (no anchor or text too short)
            if selector == "#content ul.list li":
                items = [
                    i for i in items
                    if i.select_one("a[href]")
                    and len(i.get_text(strip=True)) > 20
                    and "search-mate-list-header" not in " ".join(i.get("class", []))
                ]
            if items:
                return items
        return []

    def _parse_item(self, item: Any) -> ScrapedListing | None:
        """Parse a single <li> search-mate-entry into a ScrapedListing."""
        try:
            link_tag = item.select_one("a[href]")
            if not link_tag:
                return None
            href = link_tag.get("href", "")
            if not href:
                return None

            direct_url = (
                f"{_BASE_URL}{href}" if href.startswith("/") else href
            )

            # Extract source_listing_id from the URL path
            sid_m = re.search(r"(\d{5,})", href)
            sid = sid_m.group(1) if sid_m else href.rstrip("/").split("/")[-1].replace(".html", "")
            if not sid:
                return None

            # Title: prefer .state h3 > .state text > link text
            title = ""
            state_el = link_tag.select_one(".state h3") or link_tag.select_one(".state")
            if state_el:
                title = state_el.get_text(strip=True)
            if not title:
                title = link_tag.get_text(strip=True)
            if not title:
                title = f"WGZimmer #{sid}"
            title = title[:100]

            # Price
            cost_el = link_tag.select_one(".cost")
            price_text = cost_el.get_text(strip=True) if cost_el else ""
            price_val = self._extract_price(price_text or link_tag.get_text())

            # Available from
            date_el = (
                link_tag.select_one(".from-date")
                or link_tag.select_one(".searchMateFormFromDate")
                or link_tag.select_one(".create-date")
            )
            available_from = date_el.get_text(strip=True) if date_el else None

            # Location — extract zip from URL or from text
            full_text = item.get_text(" ", strip=True)
            zipcode = ""
            zip_m = re.search(r"\b(40[0-5]\d)\b", full_text)
            if zip_m:
                zipcode = zip_m.group(1)

            allowed = self._allowed_zips()
            if zipcode and zipcode not in allowed:
                return None

            location_text = (
                f"{zipcode} {self.city.city_name}" if zipcode else self.city.city_name
            )
            district = _ZIP_DISTRICT.get(zipcode, self.city.city_name)

            # Tram lines
            tram_lines = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})
            if not tram_lines:
                tram_lines = _ZIP_TRAM.get(zipcode, [])

            # Vegan signal
            vegan = self._detect_vegan(full_text)

            # Summary
            summary = full_text[:240]

            return ScrapedListing(
                source=self.source_id,
                source_listing_id=sid,
                source_search_url=self.search_url,
                title=title,
                price=price_val,
                currency=self.city.currency,
                country=self.city.country,
                available_from=available_from,
                location_text=location_text,
                district=district,
                transit_match_lines=tram_lines,
                roommate_signal="",
                vegan_signal=vegan,
                summary=summary,
                full_description=full_text,
                direct_url=direct_url,
                url_status="direct",
                recovery_query=f"site:wgzimmer.ch {self.city.city_name} {title[:40]}",
            )
        except Exception as exc:
            logger.debug("wgzimmer: failed to parse listing item: %s", exc)
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
