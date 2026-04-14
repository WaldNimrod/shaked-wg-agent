"""Playwright scraper for wgzimmer.ch — intercepts the REST API response.

Strategy:
  1. Launch headless Playwright Chromium
  2. Register response listener on img.wgzimmer.ch/.rest/v1/* (JSON listings)
  3. Navigate to Basel search URL — reCAPTCHA v3 runs invisibly, no puzzle
  4. Collect intercepted JSON; if none after 15 s, fall back to DOM parsing
  5. Filter for Basel city (PLZ 4001–4059) and budget range
  6. Map to ScrapedListing objects

Direct URL: https://www.wgzimmer.ch/wgzimmer/mate/ch/baselstadt/{date}-{id}.html
"""
from __future__ import annotations

import re
import time
from typing import Any

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

_BASE_URL = "https://www.wgzimmer.ch"
_TRAM_PATTERN = re.compile(r"\bTram\s*(\d+)\b", re.IGNORECASE)
_PRICE_PATTERN = re.compile(r"(\d{3,4})\s*(?:CHF|Fr\.?)", re.IGNORECASE)
_VEGAN_KEYWORDS = ["vegan", "pflanzlich", "vegetarisch", "tierfreie", "kein fleisch"]
_MAX_WAIT_SECONDS = 15
_API_URL_FRAGMENT = "img.wgzimmer.ch"

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


class WgzimmerPlaywrightScraper(BaseScraper):
    """wgzimmer.ch scraper using Playwright to bypass reCAPTCHA v3."""

    def _allowed_zips(self) -> set[str]:
        zf = self.city.zip_filter
        return set(zf) if zf else _BASEL_ZIPS_FALLBACK

    def _wg_path_segment(self) -> str:
        return _WG_CITY_PATH.get(self.city.city_id, "baselstadt")

    def fetch_listings(self) -> list[ScrapedListing]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return []

        captured: list[dict] = []

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

                # Capture JSON responses from the wgzimmer REST API
                def _on_response(response: Any) -> None:
                    if _API_URL_FRAGMENT in response.url and response.status == 200:
                        try:
                            data = response.json()
                            if isinstance(data, list):
                                captured.extend(data)
                            elif isinstance(data, dict):
                                items = (
                                    data.get("wgObjects")
                                    or data.get("items")
                                    or data.get("results")
                                    or []
                                )
                                captured.extend(items)
                        except Exception:
                            pass

                page.on("response", _on_response)

                page.goto(self.search_url, wait_until="domcontentloaded", timeout=30_000)
                page.wait_for_timeout(3_000)

                # Detect reCAPTCHA block early — no point waiting if page is gated
                content = page.content()
                if "stopped by" in content.lower() and "recaptcha" in content.lower():
                    return []  # reCAPTCHA block — return empty, don't fall back

                # Wait for API call to arrive (max _MAX_WAIT_SECONDS)
                deadline = time.time() + _MAX_WAIT_SECONDS
                while not captured and time.time() < deadline:
                    page.wait_for_timeout(500)

                # If API interception yielded nothing, try DOM fallback
                if not captured:
                    return self._dom_fallback(page)

            finally:
                browser.close()

        results: list[ScrapedListing] = []
        for item in captured:
            parsed = self._parse_api_item(item)
            if parsed:
                results.append(parsed)
        return results

    # ── API-based parsing ────────────────────────────────────────────────────

    def _parse_api_item(self, item: dict) -> ScrapedListing | None:  # noqa: C901
        try:
            # ── ID + URL ──────────────────────────────────────────────────
            sid = str(
                item.get("id") or item.get("wgId") or item.get("objectId") or ""
            )
            if not sid:
                return None

            # date string for URL (e.g. "2024-03-15" → "2024-03-15-{id}")
            date_str = (
                item.get("availableFrom")
                or item.get("moveInDate")
                or item.get("date")
                or ""
            )
            date_part = str(date_str)[:10] if date_str else ""
            seg = self._wg_path_segment()
            if date_part:
                direct_url = f"{_BASE_URL}/wgzimmer/mate/ch/{seg}/{date_part}-{sid}.html"
            else:
                direct_url = f"{_BASE_URL}/wgzimmer/mate/ch/{seg}/{sid}.html"

            # ── Zip / location filter ─────────────────────────────────────
            zipcode = str(
                item.get("zip") or item.get("plz") or item.get("postalCode") or ""
            ).strip()
            allowed = self._allowed_zips()
            if zipcode and zipcode not in allowed:
                return None
            city = str(item.get("city") or item.get("ort") or "Basel")
            street = str(item.get("street") or item.get("strasse") or "")
            location_text = f"{street}, {zipcode} {city}" if street else f"{zipcode} {city}"
            district = _ZIP_DISTRICT.get(zipcode, city)

            # ── Price ─────────────────────────────────────────────────────
            price_raw = (
                item.get("price")
                or item.get("rent")
                or item.get("miete")
                or item.get("totalCost")
            )
            try:
                price_val = int(price_raw) if price_raw else None
            except (ValueError, TypeError):
                price_text = str(price_raw or "")
                m = _PRICE_PATTERN.search(price_text)
                price_val = int(m.group(1)) if m else None

            # ── Title / description ───────────────────────────────────────
            title = str(
                item.get("title")
                or item.get("heading")
                or item.get("name")
                or item.get("beschreibung", "")[:60]
                or f"WGZimmer #{sid}"
            )
            description = str(
                item.get("description")
                or item.get("text")
                or item.get("beschreibung")
                or ""
            )

            # ── Dates ─────────────────────────────────────────────────────
            available_from = (
                item.get("availableFrom")
                or item.get("moveInDate")
                or item.get("freeFrom")
                or item.get("freiBis")
                or date_str
                or None
            )
            if available_from:
                available_from = str(available_from)[:10]

            posted_date = str(item.get("insertDate") or item.get("postedDate") or "")[:10] or None

            # ── Tram ──────────────────────────────────────────────────────
            full_text = f"{title} {description} {street}"
            tram_lines = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})
            if not tram_lines:
                tram_lines = _ZIP_TRAM.get(zipcode, [])

            # ── Vegan signal ─────────────────────────────────────────────
            vegan = self._detect_vegan(full_text)

            # ── Roommate / flatmates ──────────────────────────────────────
            roommates = item.get("roommates") or item.get("mitbewohner") or item.get("flatmates") or []
            if isinstance(roommates, list) and roommates:
                roommate_signal = "; ".join(
                    str(r.get("name") or r.get("age") or r) for r in roommates[:3]
                )
            else:
                roommate_signal = str(roommates) if roommates else ""

            # ── Summary ──────────────────────────────────────────────────
            rooms = item.get("rooms") or item.get("zimmer") or ""
            floor_space = item.get("size") or item.get("flaeche") or ""
            summary_parts = [
                f"{rooms} Zimmer" if rooms else "",
                f"{floor_space} m²" if floor_space else "",
            ]
            summary_prefix = " · ".join(p for p in summary_parts if p)
            summary = f"{summary_prefix}. {description[:200]}" if summary_prefix else description[:240]

            return ScrapedListing(
                source=self.source_id,
                source_listing_id=sid,
                source_search_url=self.search_url,
                title=title[:100],
                price=price_val,
                currency=self.city.currency,
                country=self.city.country,
                available_from=available_from,
                location_text=location_text,
                district=district,
                transit_match_lines=tram_lines,
                roommate_signal=roommate_signal[:200],
                vegan_signal=vegan,
                summary=summary[:300],
                direct_url=direct_url,
                url_status="direct",
                recovery_query=f"site:wgzimmer.ch {self.city.city_name} {title[:40]}",
                posted_date=posted_date,
            )
        except Exception:
            return None

    # ── DOM fallback (if API interception failed) ────────────────────────────

    def _dom_fallback(self, page: Any) -> list[ScrapedListing]:
        """Parse visible listing elements from the rendered page."""
        results: list[ScrapedListing] = []
        try:
            from bs4 import BeautifulSoup
            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            for item in soup.select(
                "li.search-result-entry, li[class*='result'], "
                "div[class*='listing'], article[class*='listing']"
            ):
                link_tag = item.select_one("a[href]")
                if not link_tag:
                    continue
                href = link_tag.get("href", "")
                title = link_tag.get_text(strip=True)
                if not title or not href:
                    continue

                direct_url = f"{_BASE_URL}{href}" if href.startswith("/") else href
                sid_m = re.search(r"(\d{4,})", href)
                sid = sid_m.group(1) if sid_m else href.split("/")[-1].replace(".html", "")

                full_text = item.get_text(" ", strip=True)
                price_m = _PRICE_PATTERN.search(full_text)
                tram_lines = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})

                results.append(
                    ScrapedListing(
                        source=self.source_id,
                        source_listing_id=sid,
                        source_search_url=self.search_url,
                        title=title[:100],
                        price=int(price_m.group(1)) if price_m else None,
                        currency=self.city.currency,
                        country=self.city.country,
                        available_from=None,
                        location_text=self.city.city_name,
                        district=self.city.city_name,
                        transit_match_lines=tram_lines,
                        roommate_signal="",
                        vegan_signal=self._detect_vegan(full_text),
                        summary=full_text[:240],
                        direct_url=direct_url,
                        url_status="direct",
                        recovery_query=f"site:wgzimmer.ch {self.city.city_name} {title[:40]}",
                    )
                )
        except Exception:
            pass
        return results

    @staticmethod
    def _detect_vegan(text: str) -> str:
        lower = text.lower()
        for kw in _VEGAN_KEYWORDS:
            if kw in lower:
                return kw
        return "kein Signal"
