"""Scraper for ronorp.net Basel WG-Zimmer listings.

Flow:
  1. GET https://cockpit.ronorp.net/api/market/posts/housing?city_id=4&is_mobile=0
     (unauthenticated endpoint; returns housing posts for Basel)
  2. Filter by sub_category_id=144 (WG subcategory) and Basel zip codes
  3. Paginate using skip/take until no more results
  4. Map each post → ScrapedListing

robots.txt check (2026-05-05):
  User-agent: * → /basel/market/* is NOT disallowed
  The target path /basel/markt/immobilien-basel/wg-zimmer-basel is allowed.
  ClaudeBot also explicitly allowed.
  Result: ALLOWED

API Notes:
  - The listing page (ronorp.net/basel/market/immobilien-basel/wg-zimmer-basel) is a Next.js
    client-side rendered app. Listing data is fetched from cockpit.ronorp.net/api.
  - The unauthenticated endpoint /market/posts/housing returns housing posts for a city.
  - The WG subcategory (id=144, slug='shared-apartments') posts are filtered client-side.
  - The authenticated endpoint (/market/category/immobilien-basel?category_id=…) requires
    a Bearer token; not available without login.
  - This scraper uses the unauthenticated path and filters by sub_category_id=144.
  - During periods of low WG activity on Basel ronorp, the scraper may return 0 listings.

Polite delay: 7 seconds between page requests.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Any

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

logger = logging.getLogger(__name__)

_BASE_URL = "https://ronorp.net"
_API_BASE = "https://cockpit.ronorp.net/api"

# Basel city_id in the ronorp database
_BASEL_CITY_ID = 4

# WG subcategory id (shared-apartments) in ronorp taxonomy
_WG_SUBCATEGORY_ID = 144

# Basel zip codes range (4001–4059)
_BASEL_ZIPS: set[str] = {str(z) for z in range(4001, 4060)}

_POLITE_DELAY = 7.0  # seconds between page requests

_VEGAN_KEYWORDS = ["vegan", "pflanzlich", "pflanzenbasiert", "vegetarisch", "tierfreie"]

_TRAM_PATTERN = re.compile(r"\bTram\s*(\d+)\b", re.IGNORECASE)

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

# Posts to fetch per page
_PAGE_SIZE = 20


class RonorpScraper(BaseScraper):
    """Scraper for ronorp.net Basel WG listings using the cockpit.ronorp.net REST API.

    Polite delay: 7 seconds between page requests.
    Filters: sub_category_id=144 (WG), Basel zip codes (4001–4059).
    """

    _POLITE_DELAY = _POLITE_DELAY

    def fetch_listings(self) -> list[ScrapedListing]:
        """Fetch all Basel WG listings from ronorp.net cockpit API."""
        results: list[ScrapedListing] = []
        skip = 0

        while True:
            url = (
                f"{_API_BASE}/market/posts/housing"
                f"?city_id={_BASEL_CITY_ID}&is_mobile=0"
                f"&skip={skip}&take={_PAGE_SIZE}"
            )
            logger.debug("RonorpScraper: fetching skip=%d — %s", skip, url)

            try:
                resp = self._get(url)
                data = resp.json()
            except Exception as exc:
                logger.warning("RonorpScraper: failed to fetch skip=%d: %s", skip, exc)
                break

            housing = data.get("housing", []) if isinstance(data, dict) else []
            if not housing:
                logger.debug("RonorpScraper: no more posts at skip=%d, stopping.", skip)
                break

            for raw in housing:
                if not self._is_wg_post(raw):
                    continue
                listing = self._parse_listing(raw)
                if listing is not None:
                    results.append(listing)

            if len(housing) < _PAGE_SIZE:
                break

            skip += _PAGE_SIZE
            time.sleep(self._POLITE_DELAY)

        logger.info("RonorpScraper: fetched %d WG listings total.", len(results))
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_wg_post(raw: dict[str, Any]) -> bool:
        """Return True if the post is a WG listing in Basel."""
        if raw.get("sub_category_id") != _WG_SUBCATEGORY_ID:
            return False
        zip_code = str(raw.get("zip_code") or "")
        return zip_code in _BASEL_ZIPS

    @classmethod
    def _parse_listing_from_api_post(cls, raw: dict[str, Any]) -> ScrapedListing | None:
        """Parse a raw API post dict into a ScrapedListing (class method for tests)."""
        return cls._parse_raw(raw)

    def _parse_listing(self, raw: dict[str, Any]) -> ScrapedListing | None:
        """Parse a single raw API post dict into a ScrapedListing."""
        return self._parse_raw(raw)

    @staticmethod
    def _parse_raw(raw: dict[str, Any]) -> ScrapedListing | None:
        """Convert a raw ronorp API post to a ScrapedListing."""
        try:
            post_id = str(raw.get("id") or "")
            if not post_id:
                return None

            seo_slug = raw.get("seo_slug") or raw.get("slug") or post_id
            direct_url = f"{_BASE_URL}/basel/market/immobilien-basel/{seo_slug}"

            zip_code = str(raw.get("zip_code") or "")
            location_info = raw.get("location") or {}
            address = location_info.get("address") or "Basel"

            location_text = (
                f"{address}, {zip_code} Basel" if zip_code else address
            )
            district = _ZIP_DISTRICT.get(zip_code, "Basel")

            title = raw.get("title") or f"Ronorp WG #{post_id}"

            # Strip HTML tags from description
            description_html = raw.get("description") or ""
            description = re.sub(r"<[^>]+>", "", description_html).strip()

            # Price from pricing_details or direct price field
            pricing_details = raw.get("pricing_details") or {}
            price_str = pricing_details.get("price") or raw.get("price") or ""
            try:
                price: int | None = int(float(price_str)) if price_str else None
            except (ValueError, TypeError):
                price = None

            # Available from housing_detail
            housing_detail = raw.get("housing_detail") or {}
            available_from = housing_detail.get("ready_to_move") or None

            # Posted date
            posted_date = raw.get("created_at") or None

            # Transit detection
            full_text = f"{title} {description} {address}"
            line_ids = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})

            # Vegan signal
            lower_desc = description.lower()
            vegan_signal = "kein Signal"
            for kw in _VEGAN_KEYWORDS:
                if kw in lower_desc:
                    vegan_signal = kw
                    break

            # Author info for roommate_signal
            author_info = raw.get("author_info") or {}
            roommate_signal = author_info.get("full_name") or author_info.get("username") or ""

            # Rooms from housing_detail
            rooms = housing_detail.get("num_of_rooms") or ""
            floor_size = housing_detail.get("floor_size") or ""
            size_str = f"{floor_size} m²" if floor_size else ""
            rooms_str = f"{rooms} Zimmer" if rooms else ""
            summary_parts = [p for p in [rooms_str, size_str, description[:200]] if p]
            summary = ". ".join(summary_parts)[:300]

            full_description = description

            return ScrapedListing(
                source="ronorp",
                source_listing_id=post_id,
                source_search_url=(
                    f"{_BASE_URL}/basel/market/immobilien-basel/wg-zimmer-basel"
                ),
                title=title[:100],
                price=price,
                currency="CHF",
                country="CH",
                available_from=available_from,
                location_text=location_text,
                district=district,
                transit_match_lines=line_ids,
                roommate_signal=roommate_signal,
                vegan_signal=vegan_signal,
                summary=summary,
                full_description=full_description,
                direct_url=direct_url,
                url_status="direct",
                recovery_query=f"site:ronorp.net {title[:40]} Basel WG",
                posted_date=posted_date,
            )
        except Exception:
            logger.exception(
                "RonorpScraper: failed to parse post id=%s", raw.get("id")
            )
            return None
