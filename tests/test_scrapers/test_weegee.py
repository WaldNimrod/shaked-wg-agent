"""Tests for shaked_wg_agent.scrapers.weegee.WeegeeScraper.

All tests are fixture-based — no live network access required.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from shaked_wg_agent.config import BoundingBox, CityDefinition
from shaked_wg_agent.scrapers.base import ScrapedListing
from shaked_wg_agent.scrapers.weegee import WeegeeScraper

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "scrapers"
_SEARCH_PAGE_HTML = (_FIXTURE_DIR / "weegee_basel_search.html").read_text(encoding="utf-8")

_SEARCH_URL = "https://weegee.ch/de/search/city-basel"


def _make_city() -> CityDefinition:
    return CityDefinition(
        city_id="basel",
        city_name="Basel",
        country="CH",
        currency="CHF",
        bounding_box=BoundingBox(west=7.5, east=7.7, south=47.5, north=47.6),
        available_sources=["wgzimmer", "flatfox", "weegee"],
        zip_filter=["4051", "4052", "4053", "4054", "4055", "4056", "4057", "4058"],
    )


def _make_scraper() -> WeegeeScraper:
    return WeegeeScraper(
        source_id="weegee",
        search_url=_SEARCH_URL,
        city=_make_city(),
    )


# ---------------------------------------------------------------------------
# Test: parse ≥10 listings from fixture
# ---------------------------------------------------------------------------


def test_parse_basel_search() -> None:
    """Parsing the fixture HTML must return ≥10 listings."""
    listings = WeegeeScraper._parse_listing_from_html(_SEARCH_PAGE_HTML)
    assert len(listings) >= 10, f"Expected ≥10 listings, got {len(listings)}"
    for lst in listings:
        assert isinstance(lst, ScrapedListing)


# ---------------------------------------------------------------------------
# Test: required fields on every listing
# ---------------------------------------------------------------------------


def test_listing_fields() -> None:
    """Every listing must have the required non-empty fields."""
    listings = WeegeeScraper._parse_listing_from_html(_SEARCH_PAGE_HTML)
    assert listings, "No listings parsed — check fixture."

    for lst in listings:
        d = lst.to_dict()

        # listing_id is derived from source + source_listing_id
        assert d["listing_id"], f"Missing listing_id: {d}"

        # source_listing_id: non-empty string
        assert lst.source_listing_id, f"Missing source_listing_id: {d}"

        # title: non-empty string
        assert lst.title, f"Missing title: {d}"

        # price: int or None (None is allowed for free rooms / price-on-request)
        assert lst.price is None or isinstance(lst.price, int), (
            f"price must be int or None, got {type(lst.price)}: {d}"
        )

        # available_from: str or None
        assert lst.available_from is None or isinstance(lst.available_from, str), (
            f"available_from must be str or None: {d}"
        )

        # location_text: non-empty
        assert lst.location_text, f"Missing location_text: {d}"

        # direct_url: non-empty and starts with https://
        assert lst.direct_url, f"Missing direct_url: {d}"
        assert lst.direct_url.startswith("https://"), (
            f"direct_url must start with https://: {lst.direct_url}"
        )

        # summary: str (may be empty for listings with no description)
        assert isinstance(lst.summary, str), f"summary must be str: {d}"

        # full_description: str
        assert isinstance(lst.full_description, str), f"full_description must be str: {d}"


# ---------------------------------------------------------------------------
# Test: source and country/currency
# ---------------------------------------------------------------------------


def test_listing_source_and_currency() -> None:
    listings = WeegeeScraper._parse_listing_from_html(_SEARCH_PAGE_HTML)
    for lst in listings:
        assert lst.source == "weegee"
        assert lst.currency == "CHF"
        assert lst.country == "CH"


# ---------------------------------------------------------------------------
# Test: direct_url construction
# ---------------------------------------------------------------------------


def test_listing_direct_url_format() -> None:
    listings = WeegeeScraper._parse_listing_from_html(_SEARCH_PAGE_HTML)
    for lst in listings:
        assert lst.direct_url.startswith("https://weegee.ch/de/wg/"), (
            f"Expected weegee.ch detail URL, got: {lst.direct_url}"
        )


# ---------------------------------------------------------------------------
# Test: district mapping
# ---------------------------------------------------------------------------


def test_listing_district_mapping() -> None:
    """Listings with known zip codes must map to the correct district."""
    listings = WeegeeScraper._parse_listing_from_html(_SEARCH_PAGE_HTML)
    by_zip: dict[str, str] = {}
    for lst in listings:
        # Extract zip from location_text (first 4-digit segment)
        import re
        m = re.search(r"\b(40\d{2})\b", lst.location_text)
        if m:
            by_zip[m.group(1)] = lst.district

    expected = {
        "4051": "Altstadt",
        "4052": "Gundeli",
        "4053": "Bachletten",
        "4054": "Iselin",
        "4055": "St. Alban",
        "4057": "Kleinbasel",
        "4058": "Kleinhüningen",
    }
    for zipcode, expected_district in expected.items():
        if zipcode in by_zip:
            assert by_zip[zipcode] == expected_district, (
                f"ZIP {zipcode}: expected district {expected_district!r}, "
                f"got {by_zip[zipcode]!r}"
            )


# ---------------------------------------------------------------------------
# Test: summary is truncated to ≤300 chars
# ---------------------------------------------------------------------------


def test_listing_summary_max_length() -> None:
    listings = WeegeeScraper._parse_listing_from_html(_SEARCH_PAGE_HTML)
    for lst in listings:
        assert len(lst.summary) <= 300, (
            f"summary too long ({len(lst.summary)} chars): {lst.summary[:50]}..."
        )


# ---------------------------------------------------------------------------
# Test: transit_match_lines is empty list (weegee doesn't expose transit)
# ---------------------------------------------------------------------------


def test_listing_transit_match_lines_empty() -> None:
    listings = WeegeeScraper._parse_listing_from_html(_SEARCH_PAGE_HTML)
    for lst in listings:
        assert lst.transit_match_lines == [], (
            f"Expected empty transit_match_lines, got: {lst.transit_match_lines}"
        )


# ---------------------------------------------------------------------------
# Test: vegan signal detection
# ---------------------------------------------------------------------------


def test_listing_vegan_signal_detected() -> None:
    """Fixture contains listings with 'vegan' and 'tierfreie' keywords."""
    listings = WeegeeScraper._parse_listing_from_html(_SEARCH_PAGE_HTML)
    vegan_listings = [lst for lst in listings if lst.vegan_signal != "kein Signal"]
    assert vegan_listings, (
        "Expected ≥1 listing with vegan signal (fixture has 'vegane' and 'tierfreie')"
    )


# ---------------------------------------------------------------------------
# Test: fetch_listings uses _get and paginates
# ---------------------------------------------------------------------------


def test_fetch_listings_single_page_no_next() -> None:
    """fetch_listings returns listings from a mocked single-page response."""
    scraper = _make_scraper()

    mock_resp = MagicMock()
    mock_resp.text = _SEARCH_PAGE_HTML

    # The fixture has hasNext=true in JSON but we override to confirm stop logic.
    # Use the actual fixture — it has hasNext: true so we just check it fetches page 1
    # and then returns what was found (we mock _get to raise on page 2 to stop).
    call_count = 0

    def _mock_get(url: str, retries: int = 2) -> MagicMock:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_resp
        raise RuntimeError("stop pagination in test")

    with patch.object(scraper, "_get", side_effect=_mock_get):
        listings = scraper.fetch_listings()

    # Should have parsed page 1 (12 listings in fixture)
    assert len(listings) >= 10
    assert call_count >= 1


def test_fetch_listings_returns_empty_on_network_failure() -> None:
    """fetch_listings returns [] when network fails on first page."""
    scraper = _make_scraper()

    with patch.object(scraper, "_get", side_effect=RuntimeError("network error")):
        listings = scraper.fetch_listings()

    assert listings == []


# ---------------------------------------------------------------------------
# Test: no crash on empty or malformed HTML
# ---------------------------------------------------------------------------


def test_parse_empty_html_returns_empty() -> None:
    listings = WeegeeScraper._parse_listing_from_html("")
    assert listings == []


def test_parse_html_without_next_data_returns_empty() -> None:
    html = "<html><body><h1>No listings here</h1></body></html>"
    listings = WeegeeScraper._parse_listing_from_html(html)
    assert listings == []


def test_parse_html_with_empty_listings_array() -> None:
    import json

    data = {
        "props": {
            "pageProps": {
                "listings": [],
                "hasNext": False,
                "location_name_search": "city-basel",
            }
        }
    }
    html = f"""
    <html><body>
    <script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script>
    </body></html>
    """
    listings = WeegeeScraper._parse_listing_from_html(html)
    assert listings == []
