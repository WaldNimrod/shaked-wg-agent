"""Tests for shaked_wg_agent.scrapers.unimarkt.UnimarktScraper.

All tests are fixture-based — no live network access required.
Live API is unreachable from the CI/local host (connection timeout at 2026-05-05).
"""
from __future__ import annotations

import json
import pathlib
from unittest.mock import MagicMock, patch

from shaked_wg_agent.config import BoundingBox, CityDefinition
from shaked_wg_agent.scrapers.base import ScrapedListing
from shaked_wg_agent.scrapers.unimarkt import (
    _WG_CATEGORY_ID,
    UnimarktScraper,
)

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

_FIXTURE_DIR = pathlib.Path(__file__).parent.parent / "fixtures" / "scrapers"
_FIXTURE_PATH = _FIXTURE_DIR / "unimarkt_basel_response.json"

_SEARCH_URL = "https://www.unimarkt.ch/api/trpc/post.getPublicList"


def _load_fixture() -> dict:
    return json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))


def _load_fixture_listings() -> list[ScrapedListing]:
    return UnimarktScraper._parse_listings_from_fixture(_load_fixture())


def _make_city() -> CityDefinition:
    return CityDefinition(
        city_id="basel",
        city_name="Basel",
        country="CH",
        currency="CHF",
        bounding_box=BoundingBox(west=7.5, east=7.7, south=47.5, north=47.6),
        available_sources=["unimarkt"],
        zip_filter=["4001", "4051", "4052", "4053", "4054", "4055", "4056", "4057", "4058"],
    )


def _make_scraper() -> UnimarktScraper:
    return UnimarktScraper(
        source_id="unimarkt",
        search_url=_SEARCH_URL,
        city=_make_city(),
    )


# ---------------------------------------------------------------------------
# 1. Fixture file sanity
# ---------------------------------------------------------------------------


def test_fixture_file_exists() -> None:
    """The fixture JSON file must exist and be valid JSON."""
    assert _FIXTURE_PATH.exists(), f"Fixture not found: {_FIXTURE_PATH}"
    data = _load_fixture()
    assert "result" in data


def test_fixture_has_posts() -> None:
    """Fixture must contain ≥5 posts."""
    data = _load_fixture()
    posts = data["result"]["data"]["json"]["posts"]
    assert len(posts) >= 5, f"Expected ≥5 posts, got {len(posts)}"


# ---------------------------------------------------------------------------
# 2. Fixture parse: count
# ---------------------------------------------------------------------------


def test_parse_fixture_returns_listings() -> None:
    """Parsing the fixture must return ≥5 ScrapedListing objects."""
    listings = _load_fixture_listings()
    assert len(listings) >= 5, f"Expected ≥5 listings, got {len(listings)}"
    for lst in listings:
        assert isinstance(lst, ScrapedListing)


# ---------------------------------------------------------------------------
# 3. Required fields on every listing
# ---------------------------------------------------------------------------


def test_listing_required_fields() -> None:
    """Every listing must have the required non-empty fields per acceptance criteria."""
    listings = _load_fixture_listings()
    assert listings, "No listings parsed — check fixture."

    for lst in listings:
        d = lst.to_dict()

        # listing_id: source-{id}
        assert d["listing_id"], f"Missing listing_id: {d}"
        assert d["listing_id"].startswith("unimarkt-"), (
            f"listing_id must start with 'unimarkt-': {d['listing_id']}"
        )

        # source_listing_id: non-empty
        assert lst.source_listing_id, f"Missing source_listing_id: {d}"

        # title: non-empty string
        assert lst.title, f"Missing title: {d}"

        # price: int or None
        assert lst.price is None or isinstance(lst.price, int), (
            f"price must be int or None, got {type(lst.price)}: {d}"
        )

        # location_text: non-empty
        assert lst.location_text, f"Missing location_text: {d}"

        # direct_url: non-empty, starts with https://
        assert lst.direct_url, f"Missing direct_url: {d}"
        assert lst.direct_url.startswith("https://"), (
            f"direct_url must start with https://: {lst.direct_url}"
        )

        # full_description: str
        assert isinstance(lst.full_description, str), f"full_description must be str: {d}"


# ---------------------------------------------------------------------------
# 4. Source / currency / country metadata
# ---------------------------------------------------------------------------


def test_listing_source_metadata() -> None:
    """All listings must have correct source, currency, and country."""
    listings = _load_fixture_listings()
    for lst in listings:
        assert lst.source == "unimarkt", f"Wrong source: {lst.source}"
        assert lst.currency == "CHF", f"Wrong currency: {lst.currency}"
        assert lst.country == "CH", f"Wrong country: {lst.country}"


# ---------------------------------------------------------------------------
# 5. direct_url construction
# ---------------------------------------------------------------------------


def test_listing_direct_url_format() -> None:
    """direct_url must point to unimarkt.ch immobilien/wg/ path."""
    listings = _load_fixture_listings()
    for lst in listings:
        assert "unimarkt.ch" in lst.direct_url, (
            f"direct_url not on unimarkt.ch: {lst.direct_url}"
        )
        assert "/immobilien/wg/" in lst.direct_url, (
            f"direct_url missing /immobilien/wg/ path: {lst.direct_url}"
        )


# ---------------------------------------------------------------------------
# 6. District mapping from zip code
# ---------------------------------------------------------------------------


def test_listing_district_mapping() -> None:
    """Known zip codes in the fixture must map to the correct district."""
    listings = _load_fixture_listings()
    expected = {
        "4051": "Altstadt",
        "4052": "Gundeli",
        "4053": "Bachletten",
        "4054": "Iselin",
        "4055": "St. Alban",
        "4056": "Matthäus",
        "4057": "Kleinbasel",
        "4058": "Kleinhüningen",
    }
    by_zip: dict[str, str] = {}
    for lst in listings:
        import re
        m = re.search(r"\b(40\d{2})\b", lst.location_text)
        if m:
            by_zip[m.group(1)] = lst.district

    for zipcode, expected_district in expected.items():
        if zipcode in by_zip:
            assert by_zip[zipcode] == expected_district, (
                f"ZIP {zipcode}: expected {expected_district!r}, got {by_zip[zipcode]!r}"
            )


# ---------------------------------------------------------------------------
# 7. Vegan signal detection
# ---------------------------------------------------------------------------


def test_vegan_signal_detected() -> None:
    """Fixture contains listings with 'vegan' or 'tierfreie' keywords."""
    listings = _load_fixture_listings()
    vegan_listings = [lst for lst in listings if lst.vegan_signal != "kein Signal"]
    assert vegan_listings, (
        "Expected ≥1 listing with vegan signal (fixture has 'vegan' and 'tierfreie')"
    )


def test_vegan_signal_absent() -> None:
    """Listings without vegan keywords should return 'kein Signal'."""
    listings = _load_fixture_listings()
    non_vegan = [lst for lst in listings if lst.vegan_signal == "kein Signal"]
    assert non_vegan, "Expected ≥1 listing without vegan signal in fixture."


# ---------------------------------------------------------------------------
# 8. Transit lines from description text
# ---------------------------------------------------------------------------


def test_transit_lines_extracted_from_description() -> None:
    """Listings mentioning 'Tram N' must have transit_match_lines populated."""
    listings = _load_fixture_listings()
    tram_listings = [
        lst for lst in listings
        if any("Tram" in kw or "tram" in kw for kw in
               [lst.full_description, lst.title])
    ]
    assert tram_listings, "Expected ≥1 listing with Tram mention in fixture."
    for lst in tram_listings:
        assert lst.transit_match_lines, (
            f"Expected transit_match_lines for listing with Tram mention: {lst.title}"
        )


# ---------------------------------------------------------------------------
# 9. _extract_posts handles malformed response
# ---------------------------------------------------------------------------


def test_extract_posts_malformed_response() -> None:
    """_extract_posts must return ([], False) on unexpected response structure."""
    posts, has_more = UnimarktScraper._extract_posts({})
    assert posts == []
    assert has_more is False


def test_extract_posts_valid_response() -> None:
    """_extract_posts correctly unpacks tRPC envelope."""
    data = _load_fixture()
    posts, has_more = UnimarktScraper._extract_posts(data)
    assert len(posts) >= 5
    assert isinstance(has_more, bool)


# ---------------------------------------------------------------------------
# 10. _parse_raw returns None for missing id
# ---------------------------------------------------------------------------


def test_parse_raw_missing_id_returns_none() -> None:
    """_parse_raw must return None when the post has no id."""
    bad_post = {"title": "No ID post", "description": "test", "price": 500}
    result = UnimarktScraper._parse_raw(bad_post, source_search_url=_SEARCH_URL)
    assert result is None


# ---------------------------------------------------------------------------
# 11. Price None is handled correctly
# ---------------------------------------------------------------------------


def test_parse_listing_with_null_price() -> None:
    """Listings with null price should produce price=None (not raise)."""
    listings = _load_fixture_listings()
    null_price = [lst for lst in listings if lst.price is None]
    assert null_price, "Expected ≥1 listing with null price in fixture."
    for lst in null_price:
        assert lst.price is None


# ---------------------------------------------------------------------------
# 12. fetch_listings via mocked _get — single page, no pagination
# ---------------------------------------------------------------------------


def test_fetch_listings_single_page() -> None:
    """fetch_listings returns listings from a single mocked page response."""
    scraper = _make_scraper()
    fixture_data = _load_fixture()

    mock_resp = MagicMock()
    mock_resp.json.return_value = fixture_data

    with patch.object(scraper, "_get", return_value=mock_resp):
        listings = scraper.fetch_listings()

    assert len(listings) >= 5
    assert all(isinstance(lst, ScrapedListing) for lst in listings)


# ---------------------------------------------------------------------------
# 13. fetch_listings returns [] on network failure
# ---------------------------------------------------------------------------


def test_fetch_listings_empty_on_network_error() -> None:
    """fetch_listings must return [] when _get raises on first request."""
    scraper = _make_scraper()

    with patch.object(scraper, "_get", side_effect=RuntimeError("network error")):
        listings = scraper.fetch_listings()

    assert listings == []


# ---------------------------------------------------------------------------
# 14. _build_url encodes categoryId and city
# ---------------------------------------------------------------------------


def test_build_url_contains_category_id() -> None:
    """_build_url must include the WG category UUID in the encoded input param."""
    scraper = _make_scraper()
    url = scraper._build_url(page=1)
    assert _WG_CATEGORY_ID in url, f"WG category ID not in URL: {url}"
    assert "Basel" in url, f"City 'Basel' not in URL: {url}"


# ---------------------------------------------------------------------------
# 15. Pagination: fetch_listings makes multiple calls when hasMore=True
# ---------------------------------------------------------------------------


def test_fetch_listings_paginates() -> None:
    """fetch_listings must make a second _get call when hasMore is True."""
    scraper = _make_scraper()

    page1_data = {
        "result": {
            "data": {
                "json": {
                    "posts": [
                        {
                            "id": "p1",
                            "title": "Zimmer 1",
                            "description": "desc",
                            "price": 600,
                            "city": "Basel",
                            "zip_code": "4051",
                            "slug": "zimmer-1",
                        }
                    ],
                    "hasMore": True,
                    "page": 1,
                }
            }
        }
    }
    page2_data = {
        "result": {
            "data": {
                "json": {
                    "posts": [
                        {
                            "id": "p2",
                            "title": "Zimmer 2",
                            "description": "desc2",
                            "price": 700,
                            "city": "Basel",
                            "zip_code": "4052",
                            "slug": "zimmer-2",
                        }
                    ],
                    "hasMore": False,
                    "page": 2,
                }
            }
        }
    }

    responses = [page1_data, page2_data]
    call_count = 0

    def _mock_get(url: str, retries: int = 2) -> MagicMock:
        nonlocal call_count
        mock = MagicMock()
        mock.json.return_value = responses[call_count]
        call_count += 1
        return mock

    with patch.object(scraper, "_get", side_effect=_mock_get):
        listings = scraper.fetch_listings()

    assert call_count == 2, f"Expected 2 pages fetched, got {call_count}"
    assert len(listings) == 2
    ids = {lst.source_listing_id for lst in listings}
    assert ids == {"p1", "p2"}


# ---------------------------------------------------------------------------
# 16. summary truncated to ≤300 chars
# ---------------------------------------------------------------------------


def test_listing_summary_max_length() -> None:
    listings = _load_fixture_listings()
    for lst in listings:
        assert len(lst.summary) <= 300, (
            f"summary too long ({len(lst.summary)} chars): {lst.summary[:50]}..."
        )


# ---------------------------------------------------------------------------
# 17. All fixture posts parse without error
# ---------------------------------------------------------------------------


def test_all_fixture_posts_parse() -> None:
    """All posts in the fixture should parse to non-None ScrapedListing."""
    data = _load_fixture()
    posts, _ = UnimarktScraper._extract_posts(data)
    for post in posts:
        listing = UnimarktScraper._parse_raw(post, source_search_url=_SEARCH_URL)
        assert listing is not None, f"Failed to parse post id={post.get('id')}"
