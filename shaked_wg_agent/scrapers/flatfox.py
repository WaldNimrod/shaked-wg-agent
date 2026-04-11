"""Scraper for flatfox.ch — uses public REST API (no JS rendering needed).

Flow:
  1. GET /api/v1/pin/ (bbox=Basel) → list of all PKs in the area
  2. Batch GET /api/v1/public-listing/?pk=...&pk=... (50/batch) → full details
  3. Filter locally: Basel zip (4001–4059), RENT only, WG rooms or small apartments
  4. Direct URL: constructed from API `url` field
"""
from __future__ import annotations

import re
import time
from typing import Any

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

_BASE_URL = "https://flatfox.ch"
_PIN_URL = f"{_BASE_URL}/api/v1/pin/"
_LISTING_URL = f"{_BASE_URL}/api/v1/public-listing/"

# Basel metro bounding box — filter by zip below to exclude suburbs
_BBOX = {
    "west": "7.5147", "east": "7.6559",
    "south": "47.5176", "north": "47.5956",
    "max_count": "500",
}

# Basel proper zip codes (4001–4059)
_BASEL_ZIPS = {str(z) for z in range(4001, 4060)}

# Only these object categories are relevant for Shaked
_ALLOWED_CATEGORIES = {"SHARED", "APARTMENT"}
# For apartments (not WG rooms): price and room caps
_MAX_PRICE_APARTMENT = 1200
_MAX_ROOMS_APARTMENT = 2.0

_BATCH_SIZE = 50

_TRAM_PATTERN = re.compile(r"\bTram\s*(\d+)\b", re.IGNORECASE)
_PHONE_PATTERN = re.compile(r"(?:\+41|0)[0-9\s\-/.]{8,14}[0-9]")
_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_VEGAN_KEYWORDS = ["vegan", "pflanzlich", "vegetarisch", "tierfreie"]

_ZIP_DISTRICT: dict[str, str] = {
    "4001": "Innenstadt", "4002": "Innenstadt",
    "4051": "Altstadt",   "4052": "Gundeli",
    "4053": "Bachletten", "4054": "Iselin",
    "4055": "St. Alban",  "4056": "Matthäus",
    "4057": "Kleinbasel", "4058": "Kleinhüningen",
    "4059": "Allschwil-Grenze",
}


class FlatfoxScraper(BaseScraper):
    """Flatfox scraper using the public JSON API."""

    def fetch_listings(self) -> list[ScrapedListing]:
        try:
            pks = self._get_all_pks()
        except Exception:
            return []

        if not pks:
            return []

        results: list[ScrapedListing] = []
        for i in range(0, len(pks), _BATCH_SIZE):
            batch = pks[i : i + _BATCH_SIZE]
            try:
                raw = self._fetch_batch(batch)
                for lst in raw:
                    parsed = self._parse(lst)
                    if parsed:
                        results.append(parsed)
            except Exception:
                continue
            time.sleep(1.0)

        return results

    # ── private helpers ──────────────────────────────────────────────────────

    def _get_all_pks(self) -> list[int]:
        resp = self._session.get(_PIN_URL, params=_BBOX, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("results", [])
        return [item["pk"] for item in items if "pk" in item]

    def _fetch_batch(self, pks: list[int]) -> list[dict]:
        qs = "&".join(f"pk={pk}" for pk in pks)
        url = f"{_LISTING_URL}?{qs}&limit=0"
        resp = self._session.get(url, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("results", [])

    def _parse(self, lst: dict) -> ScrapedListing | None:
        try:
            # ── zip filter: Basel only ────────────────────────────────────
            zipcode = str(lst.get("zipcode", ""))
            if zipcode not in _BASEL_ZIPS:
                return None

            if lst.get("offer_type") != "RENT":
                return None

            category = lst.get("object_category", "")
            price = lst.get("price_display")

            # Skip irrelevant categories (parking, industry, hobby rooms, etc.)
            if category not in _ALLOWED_CATEGORIES:
                return None

            # For non-WG apartments: apply price + room size caps
            if category == "APARTMENT":
                rooms = lst.get("number_of_rooms") or 0
                if price and int(price) > _MAX_PRICE_APARTMENT:
                    return None
                if rooms and float(rooms) > _MAX_ROOMS_APARTMENT:
                    return None

            # ── build direct URL ───────────────────────────────────────────
            pk = str(lst["pk"])
            api_url = lst.get("url", "")  # e.g. /en/flat/slug/pk/
            if api_url:
                # Convert to German version for Shaked
                direct_url = _BASE_URL + api_url.replace("/en/flat/", "/de/flat/")
            else:
                slug = lst.get("slug", "")
                direct_url = (
                    f"{_BASE_URL}/de/flat/{slug}/{pk}/"
                    if slug
                    else f"{_BASE_URL}/de/flat/{pk}/"
                )

            # ── extract fields ─────────────────────────────────────────────
            title = (
                lst.get("short_title")
                or lst.get("pitch_title")
                or lst.get("description_title")
                or lst.get("public_title")
                or f"Flatfox #{pk}"
            )
            description = lst.get("description") or ""
            street = lst.get("street") or ""
            city = lst.get("city") or "Basel"
            rooms = lst.get("number_of_rooms")
            floor_space = lst.get("surface_living") or lst.get("space_display")
            object_type = lst.get("object_type", "")
            is_furnished = lst.get("is_furnished", False)
            is_temporary = lst.get("is_temporary", False)
            available_from = lst.get("moving_date") or lst.get("move_in_date")
            agency = (lst.get("agency") or {}).get("name", "")

            district = _ZIP_DISTRICT.get(zipcode, city)
            location_text = f"{street}, {zipcode} {city}" if street else f"{zipcode} {city}"

            full_text = f"{title} {description} {street}"
            tram_lines = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})
            vegan = self._detect_vegan(full_text)

            # Extract contact info from description text
            phones = _PHONE_PATTERN.findall(description)
            emails = _EMAIL_PATTERN.findall(description)
            contact_extracted = ", ".join(phones[:2] + emails[:2]) if (phones or emails) else ""

            summary_parts = [
                f"{object_type}" if object_type else "",
                f"{rooms} Zimmer" if rooms else "",
                f"{floor_space} m²" if floor_space else "",
                "möbliert" if is_furnished else "",
                "Zwischenmiete" if is_temporary else "",
            ]
            summary_prefix = " · ".join(p for p in summary_parts if p)
            summary = f"{summary_prefix}. {description[:200]}" if summary_prefix else description[:240]

            # Determine tier: SHARED = 🔐 (has direct link, contact via platform)
            url_status = "direct"

            return ScrapedListing(
                source=self.source_id,
                source_listing_id=pk,
                source_search_url=self.search_url,
                title=title[:100],
                price_chf=int(price) if price else None,
                available_from=str(available_from) if available_from else None,
                location_text=location_text,
                district=district,
                tram_match_lines=tram_lines,
                roommate_signal=agency or "",
                vegan_signal=vegan,
                summary=summary[:300],
                direct_url=direct_url,
                url_status=url_status,
                recovery_query=f"site:flatfox.ch {title[:40]} Basel",
            )
        except Exception:
            return None

    @staticmethod
    def _detect_vegan(text: str) -> str:
        lower = text.lower()
        for kw in _VEGAN_KEYWORDS:
            if kw in lower:
                return kw
        return "kein Signal"
