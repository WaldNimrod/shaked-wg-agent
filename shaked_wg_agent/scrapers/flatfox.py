"""Scraper for flatfox.ch — uses public REST API (no JS rendering needed).

Flow:
  1. GET /api/v1/pin/ (bbox) → list of all PKs in the area
  2. Batch GET /api/v1/public-listing/?pk=...&pk=... (50/batch) → full details
  3. Filter locally: city zip list, RENT only, WG rooms or small apartments
  4. Direct URL: constructed from API `url` field
"""
from __future__ import annotations

import re
import time
from datetime import UTC, datetime

import requests as _requests

from shaked_wg_agent.config import CityDefinition
from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing

_BASE_URL = "https://flatfox.ch"
PIN_URL = f"{_BASE_URL}/api/v1/pin/"
_LISTING_URL = f"{_BASE_URL}/api/v1/public-listing/"

# Fallback when city has no zip_filter (should not happen for configured cities)
_BASEL_ZIPS_FALLBACK = {str(z) for z in range(4001, 4060)}

# Only these object categories are relevant for Shaked
_ALLOWED_CATEGORIES = {"SHARED", "APARTMENT"}
# For apartments (not WG rooms): price and room caps
_MAX_PRICE_APARTMENT = 1200
_MAX_ROOMS_APARTMENT = 2.0

_BATCH_SIZE = 50

_TRAM_PATTERN = re.compile(r"\bTram\s*(\d+)\b", re.IGNORECASE)
_VEGAN_KEYWORDS = ["vegan", "pflanzlich", "vegetarisch", "tierfreie"]

_ZIP_DISTRICT: dict[str, str] = {
    "4001": "Innenstadt", "4002": "Innenstadt",
    "4051": "Altstadt", "4052": "Gundeli",
    "4053": "Bachletten", "4054": "Iselin",
    "4055": "St. Alban", "4056": "Matthäus",
    "4057": "Kleinbasel", "4058": "Kleinhüningen",
    "4059": "Allschwil-Grenze",
}

# Tram lines per Basel zip when description has no tram mentions.
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


def flatfox_pin_query_params(city: CityDefinition) -> dict[str, str]:
    """Query params for GET /api/v1/pin/ from city bounding box."""
    bb = city.bounding_box
    return {
        "west": str(bb.west),
        "east": str(bb.east),
        "south": str(bb.south),
        "north": str(bb.north),
        "max_count": "500",
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

    def _allowed_zips(self) -> set[str]:
        zf = self.city.zip_filter
        return set(zf) if zf else _BASEL_ZIPS_FALLBACK

    def _get_all_pks(self) -> list[int]:
        params = flatfox_pin_query_params(self.city)
        resp = self._session.get(PIN_URL, params=params, timeout=20)
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
            zipcode = str(lst.get("zipcode", ""))
            allowed = self._allowed_zips()
            if zipcode not in allowed:
                return None

            if lst.get("offer_type") != "RENT":
                return None

            category = lst.get("object_category", "")
            price = lst.get("price_display")

            if category not in _ALLOWED_CATEGORIES:
                return None

            if category == "APARTMENT":
                rooms = lst.get("number_of_rooms") or 0
                if price and int(price) > _MAX_PRICE_APARTMENT:
                    return None
                if rooms and float(rooms) > _MAX_ROOMS_APARTMENT:
                    return None

            pk = str(lst["pk"])
            api_url = lst.get("url", "")
            if api_url:
                direct_url = _BASE_URL + api_url.replace("/en/flat/", "/de/wohnung/")
            else:
                slug = lst.get("slug", "")
                direct_url = (
                    f"{_BASE_URL}/de/wohnung/{slug}/{pk}/"
                    if slug
                    else f"{_BASE_URL}/en/flat/{pk}/"
                )

            title = (
                lst.get("short_title")
                or lst.get("pitch_title")
                or lst.get("description_title")
                or lst.get("public_title")
                or f"Flatfox #{pk}"
            )
            description = lst.get("description") or ""
            street = lst.get("street") or ""
            place = lst.get("city") or self.city.city_name
            rooms = lst.get("number_of_rooms")
            floor_space = lst.get("surface_living") or lst.get("space_display")
            object_type = lst.get("object_type", "")
            is_furnished = lst.get("is_furnished", False)
            is_temporary = lst.get("is_temporary", False)
            available_from = lst.get("moving_date") or lst.get("move_in_date")
            agency = (lst.get("agency") or {}).get("name", "")

            district = _ZIP_DISTRICT.get(zipcode, place)
            location_text = f"{street}, {zipcode} {place}" if street else f"{zipcode} {place}"

            full_text = f"{title} {description} {street}"
            line_ids = list({m.group(1) for m in _TRAM_PATTERN.finditer(full_text)})
            if not line_ids:
                line_ids = _ZIP_TRAM.get(zipcode, [])
            vegan = self._detect_vegan(full_text)

            summary_parts = [
                f"{object_type}" if object_type else "",
                f"{rooms} Zimmer" if rooms else "",
                f"{floor_space} m²" if floor_space else "",
                "möbliert" if is_furnished else "",
                "Zwischenmiete" if is_temporary else "",
            ]
            summary_prefix = " · ".join(p for p in summary_parts if p)
            summary = f"{summary_prefix}. {description[:200]}" if summary_prefix else description[:240]

            url_status = "direct"

            # full_description: use the raw API description field (untruncated).
            # Falls back to summary when description is empty.
            full_description = description if description else summary

            return ScrapedListing(
                source=self.source_id,
                source_listing_id=pk,
                source_search_url=self.search_url,
                title=title[:100],
                price=int(price) if price else None,
                currency=self.city.currency,
                country=self.city.country,
                available_from=str(available_from) if available_from else None,
                location_text=location_text,
                district=district,
                transit_match_lines=line_ids,
                roommate_signal=agency or "",
                vegan_signal=vegan,
                summary=summary[:300],
                full_description=full_description,
                direct_url=direct_url,
                url_status=url_status,
                recovery_query=f"site:flatfox.ch {title[:40]} {self.city.city_name}",
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


def verify_listings(listings: list[dict], city: CityDefinition) -> None:
    """Verify flatfox listings using the pin API (not blocked by Cloudflare).

    Fetches the current set of active PKs from the bbox search and marks
    each stored flatfox listing as verified_active=True/False accordingly.
    """
    flatfox = [
        row
        for row in listings
        if row.get("source") == "flatfox" and row.get("source_listing_id")
    ]
    if not flatfox:
        return

    try:
        params = flatfox_pin_query_params(city)
        resp = _requests.get(PIN_URL, params=params, timeout=20)
        resp.raise_for_status()
        active_pks = {str(item["pk"]) for item in resp.json() if "pk" in item}
    except Exception:
        return  # API unreachable — leave existing state unchanged

    now = datetime.now(UTC).isoformat(timespec="seconds")
    for lst in flatfox:
        pk = str(lst["source_listing_id"])
        if pk in active_pks:
            lst["verified_active"] = True
            lst["last_verified_at"] = now
            if lst.get("url_status") == "broken_needs_recovery":
                lst["url_status"] = "direct"
        else:
            lst["verified_active"] = False
            lst["url_status"] = "broken_needs_recovery"
