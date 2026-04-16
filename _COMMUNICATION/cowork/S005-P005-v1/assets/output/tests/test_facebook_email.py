"""Unit tests for EmailFacebookScraper (UT-01 through UT-20)."""
from __future__ import annotations

import email as email_lib
import json
import logging
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "output" / "src"))
sys.path.insert(0, str(_ROOT / "src"))

from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing
from shaked_wg_agent.scrapers.facebook_email import EmailFacebookScraper

FIXTURES_DIR = _ROOT / "tests" / "fixtures"


@pytest.fixture
def city_mock():
    city = MagicMock()
    city.currency = "ILS"
    city.country = "IL"
    city.city_name = "Pardes Hanna"
    city.city_id = "pardes-hanna-region"
    return city


@pytest.fixture
def scraper(city_mock, tmp_path):
    """Create scraper pointing to fixtures directory (file mode)."""
    s = EmailFacebookScraper("facebook-email", str(FIXTURES_DIR), city_mock)
    # Override processed IDs file to temp
    s._PROCESSED_IDS_FILE = tmp_path / "processed_ids.json"
    s._processed_ids = set()
    return s


def _load_fixture_html(filename: str) -> str:
    """Load HTML body from .eml fixture."""
    filepath = FIXTURES_DIR / filename
    with open(filepath, "rb") as f:
        msg = email_lib.message_from_bytes(f.read())
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                charset = part.get_content_charset() or "utf-8"
                return part.get_payload(decode=True).decode(charset, errors="replace")
    elif msg.get_content_type() == "text/html":
        charset = msg.get_content_charset() or "utf-8"
        return msg.get_payload(decode=True).decode(charset, errors="replace")
    return ""


# UT-01: EmailFacebookScraper is a subclass of BaseScraper
def test_is_basescraper_subclass():
    assert issubclass(EmailFacebookScraper, BaseScraper)


# UT-02: No LLM config -> fetch_listings() returns []
@patch("shaked_wg_agent.scrapers.facebook_email.check_llm_config", return_value=False)
def test_no_llm_config_returns_empty(mock_config, scraper, caplog):
    with caplog.at_level(logging.WARNING):
        results = scraper.fetch_listings()
    assert results == []
    assert "disabled" in caplog.text.lower() or "llm" in caplog.text.lower()


# UT-03: No IMAP env vars -> _fetch_imap() returns []
def test_no_imap_env_returns_empty(city_mock):
    scraper = EmailFacebookScraper("facebook-email", "imap://env/INBOX", city_mock)
    with patch.dict(os.environ, {}, clear=True):
        result = scraper._fetch_imap()
    assert result == []


# UT-04: _get_imap_config() returns None when env vars missing
def test_imap_config_none_when_missing(city_mock):
    scraper = EmailFacebookScraper("facebook-email", "imap://env/INBOX", city_mock)
    with patch.dict(os.environ, {"SHAKED_EMAIL_HOST": "imap.example.com"}, clear=True):
        result = scraper._get_imap_config()
    assert result is None


# UT-05: _get_imap_config() returns tuple when all env vars set
def test_imap_config_returns_tuple(city_mock):
    scraper = EmailFacebookScraper("facebook-email", "imap://env/INBOX", city_mock)
    with patch.dict(os.environ, {
        "SHAKED_EMAIL_HOST": "imap.example.com",
        "SHAKED_EMAIL_USER": "user@example.com",
        "SHAKED_EMAIL_PASS": "secret",
    }):
        result = scraper._get_imap_config()
    assert result is not None
    assert len(result) == 4
    assert result[0] == "imap.example.com"
    assert result[3] == "INBOX"


# UT-06: Single-post fixture -> _parse_email_html() returns 1 snippet
def test_parse_single_post_email(scraper):
    html = _load_fixture_html("fb_email_single.eml")
    snippets = scraper._parse_email_html(html, "New post in דירות להשכרה פרדס חנה")
    assert len(snippets) >= 1
    assert snippets[0]["text"]
    assert "post_url" in snippets[0]


# UT-07: Digest fixture -> _parse_email_html() returns >=2 snippets
def test_parse_digest_email(scraper):
    html = _load_fixture_html("fb_email_digest.eml")
    snippets = scraper._parse_email_html(html, "3 new posts in דירות להשכרה פרדס חנה")
    assert len(snippets) >= 2


# UT-08: _extract_group_name extracts group name from subject
def test_extract_group_name(scraper):
    assert scraper._extract_group_name("New post in דירות") == "דירות"
    assert scraper._extract_group_name("3 new posts in דירות בפרדס חנה") == "דירות בפרדס חנה"
    assert scraper._extract_group_name("Popular post in נדל\"ן כרכור") == "נדל\"ן כרכור"


# UT-09: _clean_fb_url() strips tracking redirects
def test_clean_fb_url(scraper):
    # Tracking redirect
    url = "https://l.facebook.com/l.php?u=https://www.facebook.com/groups/test/posts/123&h=AT123"
    assert scraper._clean_fb_url(url) == "https://www.facebook.com/groups/test/posts/123"
    # Direct URL with query params
    url2 = "https://www.facebook.com/groups/test/posts/456?ref=notif"
    assert scraper._clean_fb_url(url2) == "https://www.facebook.com/groups/test/posts/456"


# UT-10: Snippet < 50 chars -> skipped
@patch("shaked_wg_agent.scrapers.facebook_email.check_llm_config", return_value=True)
def test_short_snippet_skipped(mock_config, scraper):
    scraper._read_eml_files = MagicMock(return_value=[
        {"message_id": "m1", "subject": "test", "date": "", "html_body": ""}
    ])
    scraper._parse_email_html = MagicMock(return_value=[
        {"text": "short", "group_name": "", "post_url": ""}
    ])
    results = scraper.fetch_listings()
    assert results == []


# UT-11: Dedup: same post_url -> only first kept
def test_dedup_same_url(scraper):
    snippets = [
        {"text": "post A " * 20, "post_url": "https://fb.com/post/1"},
        {"text": "post B " * 20, "post_url": "https://fb.com/post/1"},
    ]
    result = scraper._dedup_snippets(snippets)
    assert len(result) == 1


# UT-12: Dedup: same text hash -> only first kept
def test_dedup_same_text_hash(scraper):
    same_text = "identical content about a rental apartment in the city center " * 3
    snippets = [
        {"text": same_text, "post_url": "https://fb.com/post/1"},
        {"text": same_text, "post_url": "https://fb.com/post/2"},
    ]
    result = scraper._dedup_snippets(snippets)
    assert len(result) == 1


# UT-13: Dedup: same message-ID on second run -> skipped
@patch("shaked_wg_agent.scrapers.facebook_email.check_llm_config", return_value=True)
def test_message_id_dedup_across_runs(mock_config, scraper, tmp_path):
    scraper._processed_ids = {"<already-processed@facebookmail.com>"}
    scraper._read_eml_files = MagicMock(return_value=[
        {"message_id": "<already-processed@facebookmail.com>", "subject": "test",
         "date": "", "html_body": "<html><body>some content</body></html>"}
    ])
    results = scraper.fetch_listings()
    assert results == []


# UT-14: PII stripping: no phone numbers in output
def test_pii_phone_stripped(scraper):
    import re
    parsed = {
        "property_type": "apartment",
        "rooms": 3,
        "city": "פרדס חנה 052-1234567",
        "key_features": [],
    }
    summary = scraper._strip_pii(parsed)
    phone_re = re.compile(r"0\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}")
    assert not phone_re.search(summary)


# UT-15: File mode: reads .eml files from directory
def test_file_mode_reads_emls(scraper):
    messages = scraper._read_eml_files()
    assert len(messages) == 3  # 3 fixture files
    for msg in messages:
        assert "message_id" in msg
        assert "html_body" in msg


# UT-16: File mode: directory missing -> returns []
def test_file_mode_missing_dir(city_mock):
    scraper = EmailFacebookScraper("facebook-email", "/nonexistent/dir", city_mock)
    messages = scraper._read_eml_files()
    assert messages == []


# UT-17: File mode: corrupt .eml -> skipped, others processed
def test_file_mode_corrupt_eml(city_mock, tmp_path):
    # Create a corrupt file and a valid file
    corrupt = tmp_path / "corrupt.eml"
    corrupt.write_bytes(b"\x00\x01\x02 invalid binary data")

    valid = tmp_path / "valid.eml"
    valid.write_text(
        "From: notification@facebookmail.com\n"
        "Subject: Test\n"
        "Message-ID: <valid@test.com>\n"
        "Content-Type: text/html; charset=utf-8\n\n"
        "<html><body>valid content</body></html>"
    )

    scraper = EmailFacebookScraper("facebook-email", str(tmp_path), city_mock)
    messages = scraper._read_eml_files()
    # At least the valid file should parse
    assert len(messages) >= 1


# UT-18: Output currency is ILS, country is IL
@patch("shaked_wg_agent.scrapers.facebook_email.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_email.parse_rental_post")
def test_currency_and_country(mock_parse, mock_config, scraper):
    mock_parse.return_value = {
        "is_rental_offer": True,
        "price_ils": 3500,
        "rooms": 3,
        "city": "פרדס חנה",
        "neighborhood": "",
        "street": "",
        "property_type": "apartment",
        "key_features": [],
    }
    snippet = {
        "text": "rental post " * 20,
        "group_name": "test",
        "post_url": "https://fb.com/post/1",
        "message_id": "m1",
        "email_date": "Tue, 10 Apr 2026 14:30:00 +0300",
    }
    listing = scraper._to_scraped_listing(snippet, mock_parse.return_value)
    assert listing.currency == "ILS"
    assert listing.country == "IL"


# UT-19: processed_email_ids.json is written after run
@patch("shaked_wg_agent.scrapers.facebook_email.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_email.parse_rental_post", return_value=None)
def test_processed_ids_written(mock_parse, mock_config, scraper, tmp_path):
    scraper._PROCESSED_IDS_FILE = tmp_path / "processed_ids.json"
    scraper._read_eml_files = MagicMock(return_value=[
        {"message_id": "<new@test.com>", "subject": "test", "date": "",
         "html_body": "<html><body>some content</body></html>"}
    ])
    scraper._parse_email_html = MagicMock(return_value=[
        {"text": "long enough text for a rental listing in pardes hanna " * 3,
         "group_name": "test", "post_url": ""}
    ])
    scraper.fetch_listings()
    assert scraper._PROCESSED_IDS_FILE.exists()
    data = json.loads(scraper._PROCESSED_IDS_FILE.read_text())
    assert "<new@test.com>" in data


# UT-20: processed_email_ids.json is loaded on next run
def test_processed_ids_loaded(city_mock, tmp_path):
    ids_file = tmp_path / "processed_ids.json"
    ids_file.write_text(json.dumps(["<old@test.com>"]))

    scraper = EmailFacebookScraper("facebook-email", str(tmp_path), city_mock)
    scraper._PROCESSED_IDS_FILE = ids_file
    scraper._processed_ids = scraper._load_processed_ids()
    assert "<old@test.com>" in scraper._processed_ids


# UT-33: Each fixture is parseable by email.message_from_bytes
def test_fixtures_parseable():
    for fname in ["fb_email_single.eml", "fb_email_digest.eml", "fb_email_popular.eml"]:
        filepath = FIXTURES_DIR / fname
        assert filepath.exists(), f"{fname} missing"
        with open(filepath, "rb") as f:
            msg = email_lib.message_from_bytes(f.read())
        assert msg.get("From") is not None, f"{fname}: no From header"
        assert msg.get("Message-ID") is not None, f"{fname}: no Message-ID"
