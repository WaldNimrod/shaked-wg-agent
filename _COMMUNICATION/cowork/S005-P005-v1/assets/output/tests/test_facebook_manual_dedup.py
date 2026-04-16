"""Unit tests for deduplication logic (UT-23 through UT-28)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "output" / "src"))
sys.path.insert(0, str(_ROOT / "src"))

from shaked_wg_agent.scrapers.base import ScrapedListing
from shaked_wg_agent.scrapers.facebook_manual import ManualFacebookScraper


@pytest.fixture
def city_mock():
    city = MagicMock()
    city.currency = "ILS"
    city.country = "IL"
    city.city_name = "Pardes Hanna"
    city.city_id = "pardes-hanna-region"
    return city


def _mock_parse_rental(text, group_name="", post_id=""):
    return {
        "is_rental_offer": True,
        "price_ils": 3500,
        "rooms": 3,
        "city": "פרדס חנה",
        "neighborhood": "מרכז",
        "street": "",
        "available_from": "2026-07-01",
        "property_type": "apartment",
        "floor": 2,
        "area_sqm": 80,
        "key_features": [],
        "contact_method": "whatsapp",
    }


# UT-23: Within-batch: identical text (different post_id) -> second skipped via text-hash
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_text_hash_dedup(mock_parse, mock_config, tmp_path, city_mock):
    same_text = "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל חדש"
    posts = [
        {"post_id": "a1", "text": same_text},
        {"post_id": "a2", "text": same_text},  # same text, different ID
    ]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert len(results) == 1
    assert results[0].source_listing_id == "a1"


# UT-24: Cross-source: existing listing with matching location+price(+-10%) -> skipped
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_cross_source_dedup_price_location(mock_parse, mock_config, tmp_path, city_mock):
    posts = [{"post_id": "x1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))

    # Create listings.json with overlapping entry
    listings_path = tmp_path / "data" / "listings.json"
    listings_path.parent.mkdir(parents=True)
    existing = [{"source": "homeless", "source_listing_id": "999",
                 "location_text": "פרדס חנה", "price": 3400}]  # within 10% of 3500
    listings_path.write_text(json.dumps(existing, ensure_ascii=False))

    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    with patch.object(Path, "exists", side_effect=lambda self=None: True):
        with patch("builtins.open", side_effect=lambda p, *a, **k: (
            open(str(listings_path)) if "listings.json" in str(p) else open(str(fp), *a, **k)
        )):
            # Simplified: directly test _is_duplicate
            listing = ScrapedListing(
                source="facebook-manual", source_listing_id="x1",
                source_search_url="test", title="test", price=3500,
                currency="ILS", country="IL", available_from=None,
                location_text="פרדס חנה", district="מרכז",
            )
            assert scraper._is_duplicate(listing, existing) is True


# UT-25: Price difference >10% -> listing NOT skipped
def test_cross_source_dedup_price_outside_range(city_mock):
    scraper = ManualFacebookScraper("facebook-manual", "test.json", city_mock)
    existing = [{"source": "homeless", "source_listing_id": "999",
                 "location_text": "פרדס חנה", "price": 5000}]  # 5000 vs 3500 = >10%
    listing = ScrapedListing(
        source="facebook-manual", source_listing_id="x1",
        source_search_url="test", title="test", price=3500,
        currency="ILS", country="IL", available_from=None,
        location_text="פרדס חנה", district="מרכז",
    )
    assert scraper._is_duplicate(listing, existing) is False


# UT-26: Same source + same source_listing_id -> skipped
def test_same_source_same_id_dedup(city_mock):
    scraper = ManualFacebookScraper("facebook-manual", "test.json", city_mock)
    existing = [{"source": "facebook-manual", "source_listing_id": "x1",
                 "location_text": "somewhere", "price": 9999}]
    listing = ScrapedListing(
        source="facebook-manual", source_listing_id="x1",
        source_search_url="test", title="test", price=3500,
        currency="ILS", country="IL", available_from=None,
        location_text="פרדס חנה", district="מרכז",
    )
    assert scraper._is_duplicate(listing, existing) is True


# UT-27: No listings.json -> dedup step silently passes
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_no_listings_json_all_returned(mock_parse, mock_config, tmp_path, city_mock):
    posts = [
        {"post_id": "n1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"},
        {"post_id": "n2", "text": "דירת 4 חדרים להשכרה בכרכור 4200 שקל חדש"},
    ]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    # No data/listings.json exists -> dedup passes through
    results = scraper.fetch_listings()
    assert len(results) == 2


# UT-28: Cross-source match from different source -> listing skipped
def test_cross_source_different_source_dedup(city_mock):
    scraper = ManualFacebookScraper("facebook-manual", "test.json", city_mock)
    existing = [{"source": "homeless", "source_listing_id": "h123",
                 "location_text": "פרדס חנה", "price": 3450}]  # within 10% of 3500
    listing = ScrapedListing(
        source="facebook-manual", source_listing_id="fb1",
        source_search_url="test", title="test", price=3500,
        currency="ILS", country="IL", available_from=None,
        location_text="פרדס חנה", district="מרכז",
    )
    assert scraper._is_duplicate(listing, existing) is True
