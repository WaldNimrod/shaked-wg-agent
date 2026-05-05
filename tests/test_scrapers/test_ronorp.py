"""Tests for the ronorp.net Basel WG scraper.

The scraper uses the cockpit.ronorp.net REST API (JSON, no HTML parsing).
Tests use the fixture file ronorp_basel_search.html which embeds a
<script id="ronorp-fixture"> tag containing a representative API JSON payload.
"""
from __future__ import annotations

import json
import pathlib

from shaked_wg_agent.scrapers.ronorp import _BASEL_ZIPS, _WG_SUBCATEGORY_ID, RonorpScraper

_FIXTURE = (
    pathlib.Path(__file__).parent.parent
    / "fixtures"
    / "scrapers"
    / "ronorp_basel_search.html"
)


def _load_fixture_posts() -> list[dict]:
    """Parse the fixture HTML and return the housing posts list."""
    from bs4 import BeautifulSoup

    html = _FIXTURE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    script = soup.find("script", id="ronorp-fixture")
    assert script is not None, "Fixture script tag not found"
    data = json.loads(script.string)
    return data.get("housing", [])


def _wg_posts() -> list[dict]:
    """Return only WG posts (sub_category_id=144) in Basel zip range."""
    posts = _load_fixture_posts()
    return [
        p
        for p in posts
        if p.get("sub_category_id") == _WG_SUBCATEGORY_ID
        and str(p.get("zip_code", "")) in _BASEL_ZIPS
    ]


class TestFixtureLoad:
    """Basic fixture sanity checks."""

    def test_fixture_file_exists(self):
        assert _FIXTURE.exists(), f"Fixture not found: {_FIXTURE}"

    def test_fixture_has_posts(self):
        posts = _load_fixture_posts()
        assert len(posts) >= 10, f"Expected ≥10 posts, got {len(posts)}"

    def test_fixture_has_wg_posts(self):
        wg = _wg_posts()
        assert len(wg) >= 10, f"Expected ≥10 WG posts, got {len(wg)}"

    def test_fixture_has_non_wg_post(self):
        """Fixture must contain at least one non-WG post to verify filtering works."""
        posts = _load_fixture_posts()
        non_wg = [p for p in posts if p.get("sub_category_id") != _WG_SUBCATEGORY_ID]
        assert len(non_wg) >= 1, "Fixture should have at least one non-WG post"


class TestRonorpScraperParsing:
    """Unit tests for RonorpScraper._parse_listing_from_api_post()."""

    def test_parse_basic_listing(self):
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing is not None
        assert listing.source == "ronorp"

    def test_parse_listing_id(self):
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing.source_listing_id == str(posts[0]["id"])

    def test_parse_title(self):
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing.title
        assert len(listing.title) <= 100

    def test_parse_price(self):
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing.price is not None
        assert listing.price > 0

    def test_parse_location(self):
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert "Basel" in listing.location_text or listing.district

    def test_parse_direct_url(self):
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing.direct_url.startswith("https://ronorp.net/")
        assert listing.url_status == "direct"

    def test_parse_full_description_strips_html(self):
        """full_description should be plain text (HTML tags stripped)."""
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert "<p>" not in listing.full_description
        assert "</p>" not in listing.full_description
        assert len(listing.full_description) > 10

    def test_parse_available_from(self):
        """Listings with ready_to_move should populate available_from."""
        posts = [p for p in _wg_posts() if p.get("housing_detail", {}).get("ready_to_move")]
        assert posts, "No posts with ready_to_move in fixture"
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing.available_from is not None

    def test_parse_available_from_none(self):
        """Listings without ready_to_move should have available_from=None."""
        posts = [
            p for p in _wg_posts()
            if not p.get("housing_detail", {}).get("ready_to_move")
        ]
        assert posts, "No posts without ready_to_move in fixture"
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing.available_from is None

    def test_parse_currency(self):
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing.currency == "CHF"
        assert listing.country == "CH"

    def test_parse_vegan_signal_detected(self):
        """Posts with vegan/pflanzlich keywords in description should have vegan_signal set."""
        vegan_posts = [
            p for p in _wg_posts()
            if any(
                kw in (p.get("description") or "").lower()
                for kw in ["vegan", "pflanzlich", "pflanzenbas", "tierfreie"]
            )
        ]
        assert vegan_posts, "Fixture must contain at least one vegan post"
        for p in vegan_posts:
            listing = RonorpScraper._parse_listing_from_api_post(p)
            assert listing.vegan_signal != "kein Signal", (
                f"Expected vegan signal for post id={p['id']!r}: {p.get('description')!r}"
            )

    def test_parse_vegan_signal_absent(self):
        """Posts without vegan keywords should return 'kein Signal'."""
        non_vegan = [
            p for p in _wg_posts()
            if not any(
                kw in (p.get("description") or "").lower()
                for kw in ["vegan", "pflanzlich", "pflanzenbas", "tierfreie"]
            )
        ]
        assert non_vegan, "Fixture must contain at least one non-vegan post"
        listing = RonorpScraper._parse_listing_from_api_post(non_vegan[0])
        assert listing.vegan_signal == "kein Signal"

    def test_parse_transit_lines_detected(self):
        """Posts mentioning 'Tram N' should populate transit_match_lines."""
        tram_posts = [
            p for p in _wg_posts()
            if "Tram" in (p.get("description") or "")
            or "Tram" in (p.get("title") or "")
        ]
        assert tram_posts, "Fixture must contain posts with Tram mentions"
        listing = RonorpScraper._parse_listing_from_api_post(tram_posts[0])
        assert len(listing.transit_match_lines) >= 1

    def test_parse_district_from_zip(self):
        """Zip code 4056 should map to 'Matthäus'."""
        zip_4056 = [p for p in _wg_posts() if str(p.get("zip_code")) == "4056"]
        assert zip_4056, "Fixture must have a 4056 post"
        listing = RonorpScraper._parse_listing_from_api_post(zip_4056[0])
        assert listing.district == "Matthäus"

    def test_parse_source_search_url(self):
        posts = _wg_posts()
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert "ronorp.net" in listing.source_search_url
        assert "wg-zimmer-basel" in listing.source_search_url

    def test_parse_posted_date(self):
        """Listings should carry the created_at as posted_date."""
        posts = [p for p in _wg_posts() if p.get("created_at")]
        assert posts
        listing = RonorpScraper._parse_listing_from_api_post(posts[0])
        assert listing.posted_date is not None


class TestRonorpFilterLogic:
    """Tests for the WG post filter logic."""

    def test_is_wg_post_true(self):
        wg_post = {
            "sub_category_id": 144,
            "zip_code": 4056,
        }
        assert RonorpScraper._is_wg_post(wg_post) is True

    def test_is_wg_post_wrong_subcategory(self):
        not_wg = {
            "sub_category_id": 141,  # Möbl. Appartements
            "zip_code": 4056,
        }
        assert RonorpScraper._is_wg_post(not_wg) is False

    def test_is_wg_post_outside_basel(self):
        outside_basel = {
            "sub_category_id": 144,
            "zip_code": 8001,  # Zurich
        }
        assert RonorpScraper._is_wg_post(outside_basel) is False

    def test_fixture_filters_non_wg(self):
        """The non-WG post in the fixture should be excluded by _is_wg_post."""
        posts = _load_fixture_posts()
        non_wg = [p for p in posts if p.get("sub_category_id") != _WG_SUBCATEGORY_ID]
        for p in non_wg:
            assert not RonorpScraper._is_wg_post(p), (
                f"Post id={p.get('id')} with sub_cat={p.get('sub_category_id')} "
                "should be filtered out"
            )

    def test_all_wg_posts_parse_without_error(self):
        """All WG posts in the fixture should parse to non-None ScrapedListing."""
        for post in _wg_posts():
            listing = RonorpScraper._parse_listing_from_api_post(post)
            assert listing is not None, f"Failed to parse post id={post.get('id')}"

    def test_parse_returns_none_for_empty_id(self):
        """Parsing a post without an id should return None."""
        bad_post = {"sub_category_id": 144, "zip_code": 4056, "title": "No ID"}
        result = RonorpScraper._parse_listing_from_api_post(bad_post)
        assert result is None

    def test_count_parseable_wg_listings(self):
        """All ≥10 WG fixtures should parse successfully."""
        parsed = [
            RonorpScraper._parse_listing_from_api_post(p)
            for p in _wg_posts()
        ]
        valid = [item for item in parsed if item is not None]
        assert len(valid) >= 10, f"Expected ≥10 valid listings, got {len(valid)}"
