"""Unit tests for ManualFacebookScraper (UT-01 through UT-16)."""
from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure output/src is on path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "output" / "src"))
sys.path.insert(0, str(_ROOT / "src"))

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing
from shaked_wg_agent.scrapers.facebook_manual import ManualFacebookScraper


@pytest.fixture
def city_mock():
    """Mock CityDefinition for IL market."""
    city = MagicMock()
    city.currency = "ILS"
    city.country = "IL"
    city.city_name = "Pardes Hanna"
    city.city_id = "pardes-hanna-region"
    return city


@pytest.fixture
def valid_posts_file(tmp_path):
    """Create a temp JSON file with 4 posts (3 rental + 1 non-rental)."""
    posts = [
        {
            "post_id": "p1",
            "text": "דירת 3 חדרים להשכרה בפרדס חנה, 3500 שקלים, כניסה מיולי",
            "group_name": "test-group",
            "posted_at": "2026-04-10T14:00:00+03:00",
            "raw_url": "https://facebook.com/post/1",
        },
        {
            "post_id": "p2",
            "text": "להשכרה סטודיו 35 מטר בפרדס חנה, 2200 שקל, פנוי מיידית",
            "group_name": "test-group",
            "posted_at": "2026-04-09T10:00:00+03:00",
        },
        {
            "post_id": "p3",
            "text": "וילה 5 חדרים להשכרה בכרכור, 7500 שקל, כולל בריכה וגינה",
            "group_name": "test-group",
        },
        {
            "post_id": "p4",
            "text": "מחפשת דירה להשכרה באזור פרדס חנה, תקציב עד 3000 שקל",
            "group_name": "test-group",
        },
    ]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False), encoding="utf-8")
    return fp


def _mock_parse_rental(text, group_name="", post_id=""):
    """Mock LLM parser that classifies based on keywords."""
    if "מחפש" in text or "מישהו יודע" in text or "למכירה" in text:
        return {"is_rental_offer": False}
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
        "key_features": ["parking", "elevator"],
        "contact_method": "whatsapp",
    }


# UT-01: ManualFacebookScraper is a subclass of BaseScraper
def test_is_basescraper_subclass():
    assert issubclass(ManualFacebookScraper, BaseScraper)


# UT-02: Input file with valid posts -> returns list[ScrapedListing]
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_valid_posts_returns_listings(mock_parse, mock_config, valid_posts_file, city_mock):
    scraper = ManualFacebookScraper("facebook-manual", str(valid_posts_file), city_mock)
    results = scraper.fetch_listings()
    assert isinstance(results, list)
    assert all(isinstance(r, ScrapedListing) for r in results)
    assert len(results) == 3  # 3 rentals, 1 non-rental filtered


# UT-03: Required-only fields parse without error
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_required_only_fields(mock_parse, mock_config, tmp_path, city_mock):
    posts = [{"post_id": "min1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert len(results) == 1


# UT-05: Missing optional fields -> defaults applied
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_missing_optional_fields(mock_parse, mock_config, tmp_path, city_mock):
    posts = [{"post_id": "opt1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert len(results) == 1
    assert results[0].direct_url == ""  # raw_url missing -> ""


# UT-06: Post missing post_id -> skipped, warning logged
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_missing_post_id_skipped(mock_parse, mock_config, tmp_path, city_mock, caplog):
    posts = [
        {"text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל חסר מזהה"},
        {"post_id": "ok1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"},
    ]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    with caplog.at_level(logging.WARNING):
        results = scraper.fetch_listings()
    assert len(results) == 1
    assert "missing required field" in caplog.text.lower() or "post_id" in caplog.text


# UT-07: Post with text < 10 chars -> skipped with warning
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_short_text_skipped(mock_parse, mock_config, tmp_path, city_mock, caplog):
    posts = [
        {"post_id": "short1", "text": "קצר"},
        {"post_id": "ok1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"},
    ]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    with caplog.at_level(logging.WARNING):
        results = scraper.fetch_listings()
    assert len(results) == 1
    assert "too short" in caplog.text.lower() or "text" in caplog.text.lower()


# UT-08: Duplicate post_id -> second occurrence skipped
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_duplicate_post_id_skipped(mock_parse, mock_config, tmp_path, city_mock):
    posts = [
        {"post_id": "dup1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"},
        {"post_id": "dup1", "text": "דירת 4 חדרים להשכרה בכרכור 4200 שקל חדש"},
    ]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert len(results) == 1


# UT-09: Input file missing -> returns []
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
def test_missing_file_returns_empty(mock_config, city_mock):
    scraper = ManualFacebookScraper("facebook-manual", "/nonexistent/path.json", city_mock)
    results = scraper.fetch_listings()
    assert results == []


# UT-10: Input file invalid JSON -> returns [], error logged
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
def test_invalid_json_returns_empty(mock_config, tmp_path, city_mock, caplog):
    fp = tmp_path / "bad.json"
    fp.write_text("{not valid json!!!}")
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    with caplog.at_level(logging.ERROR):
        results = scraper.fetch_listings()
    assert results == []


# UT-11: Empty input file ([]) -> returns []
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
def test_empty_array_returns_empty(mock_config, tmp_path, city_mock):
    fp = tmp_path / "empty.json"
    fp.write_text("[]")
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert results == []


# UT-12: No LLM config -> returns [], warning logged
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "")
def test_no_llm_config_returns_empty(city_mock, caplog):
    scraper = ManualFacebookScraper("facebook-manual", "irrelevant.json", city_mock)
    with caplog.at_level(logging.WARNING):
        results = scraper.fetch_listings()
    assert results == []
    assert "scraper disabled" in caplog.text.lower() or "provider" in caplog.text.lower()


# UT-13: All LLM calls fail -> returns [], error logged
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", return_value=None)
def test_all_llm_fail_returns_empty(mock_parse, mock_config, tmp_path, city_mock, caplog):
    posts = [
        {"post_id": "f1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"},
        {"post_id": "f2", "text": "דירת 4 חדרים להשכרה בכרכור 4200 שקל חדש"},
    ]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    with caplog.at_level(logging.ERROR):
        results = scraper.fetch_listings()
    assert results == []
    assert "failed" in caplog.text.lower()


# UT-14: PII stripping: phone numbers removed from summary
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
def test_pii_phone_stripped(mock_config, tmp_path, city_mock):
    def mock_parse(text, group_name="", post_id=""):
        return {
            "is_rental_offer": True,
            "price_ils": 3500,
            "rooms": 3,
            "city": "פרדס חנה 052-1234567",
            "neighborhood": "",
            "street": "",
            "property_type": "apartment",
            "key_features": [],
            "contact_method": "phone",
        }

    posts = [{"post_id": "pii1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל 052-1234567"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))

    with patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=mock_parse):
        scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
        results = scraper.fetch_listings()
    assert len(results) == 1
    import re
    phone_re = re.compile(r"0\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}")
    assert not phone_re.search(results[0].summary)


# UT-15: author_name never appears in output
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_author_name_not_in_output(mock_parse, mock_config, tmp_path, city_mock):
    posts = [{"post_id": "au1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל", "author_name": "יוסי כהן"}]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))
    scraper = ManualFacebookScraper("facebook-manual", str(fp), city_mock)
    results = scraper.fetch_listings()
    assert len(results) == 1
    listing = results[0]
    all_fields = str(listing.to_dict())
    assert "יוסי כהן" not in all_fields


# UT-16: Output currency is ILS and country is IL
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", side_effect=_mock_parse_rental)
def test_currency_and_country(mock_parse, mock_config, valid_posts_file, city_mock):
    scraper = ManualFacebookScraper("facebook-manual", str(valid_posts_file), city_mock)
    results = scraper.fetch_listings()
    for r in results:
        assert r.currency == "ILS"
        assert r.country == "IL"
