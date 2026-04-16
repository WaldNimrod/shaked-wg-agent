"""Unit tests for input validation logic (UT-29 through UT-35)."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "output" / "src"))
sys.path.insert(0, str(_ROOT / "src"))

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
        "street": "הגפן",
        "available_from": "2026-07-01",
        "property_type": "apartment",
        "floor": 2,
        "area_sqm": 80,
        "key_features": [],
        "contact_method": "whatsapp",
    }


# UT-29: Valid posted_at -> parsed as date in ScrapedListing.posted_date
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_valid_posted_at(mock_parse, mock_config, tmp_path, city_mock):
    posts = [{"post_id": "v1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל",
              "posted_at": "2026-04-10T14:30:00+03:00"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert len(results) == 1
    assert results[0].posted_date == "2026-04-10"


# UT-30: Invalid posted_at -> coerced to None, WARNING logged
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_invalid_posted_at(mock_parse, mock_config, tmp_path, city_mock, caplog):
    posts = [{"post_id": "v2", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל",
              "posted_at": "not-a-date"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    with caplog.at_level(logging.WARNING):
        results = scraper.fetch_listings()
    assert len(results) == 1
    assert results[0].posted_date is None


# UT-31: has_images with string "true" -> coerced to True
def test_has_images_string_coercion(city_mock):
    scraper = ManualFacebookScraper("facebook-manual", "test.json", city_mock)
    post = {"post_id": "hi1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל",
            "has_images": "true"}
    seen = set()
    error = scraper._validate_post(post, seen)
    assert error is None
    assert post["has_images"] is True  # bool("true") is True


# UT-32: has_images missing -> defaults to False
def test_has_images_missing_default(city_mock):
    scraper = ManualFacebookScraper("facebook-manual", "test.json", city_mock)
    post = {"post_id": "hi2", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"}
    seen = set()
    error = scraper._validate_post(post, seen)
    assert error is None
    assert post["has_images"] is False


# UT-33: raw_url present -> stored in ScrapedListing.direct_url
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_raw_url_stored(mock_parse, mock_config, tmp_path, city_mock):
    posts = [{"post_id": "u1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל",
              "raw_url": "https://facebook.com/post/123"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert results[0].direct_url == "https://facebook.com/post/123"
    assert results[0].url_status == "direct"


# UT-34: raw_url missing -> direct_url defaults to ""
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_raw_url_missing_default(mock_parse, mock_config, tmp_path, city_mock):
    posts = [{"post_id": "u2", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert results[0].direct_url == ""
    assert results[0].url_status == "none"


# UT-35: group_url present -> stored as-is (no URL validation)
def test_group_url_stored_asis(city_mock):
    scraper = ManualFacebookScraper("facebook-manual", "test.json", city_mock)
    post = {"post_id": "g1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל",
            "group_url": "not-a-valid-url"}
    seen = set()
    error = scraper._validate_post(post, seen)
    assert error is None  # No URL validation on group_url
    assert post["group_url"] == "not-a-valid-url"
