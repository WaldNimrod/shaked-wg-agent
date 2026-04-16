"""Unit tests for LLM parser failure modes (UT-36 through UT-41)."""
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

from shaked_wg_agent.parsers.llm_listing_parser import parse_rental_post
from shaked_wg_agent.scrapers.facebook_manual import ManualFacebookScraper


# UT-36: API timeout -> returns None, WARNING logged with post_id
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.parsers.llm_listing_parser._ANTHROPIC_KEY", "sk-test")
def test_api_timeout(caplog):
    with patch(
        "shaked_wg_agent.parsers.llm_listing_parser._call_claude",
        side_effect=Exception("Connection timed out"),
    ):
        with caplog.at_level(logging.WARNING):
            result = parse_rental_post("some text", "group", post_id="timeout-1")
    assert result is None
    assert "timeout" in caplog.text.lower()


# UT-37: Rate limit (429) -> retry 1x, if still 429 -> return None
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.parsers.llm_listing_parser._ANTHROPIC_KEY", "sk-test")
@patch("shaked_wg_agent.parsers.llm_listing_parser.time.sleep")  # don't actually sleep
def test_rate_limit_retry_fail(mock_sleep, caplog):
    with patch(
        "shaked_wg_agent.parsers.llm_listing_parser._call_claude",
        side_effect=Exception("rate_limit_error: 429 Too Many Requests"),
    ):
        with caplog.at_level(logging.WARNING):
            result = parse_rental_post("some text", "group", post_id="rl-1")
    assert result is None
    mock_sleep.assert_called_once_with(2)
    assert "rate" in caplog.text.lower()


# UT-38: Rate limit recovery: 429 first call, success second
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.parsers.llm_listing_parser._ANTHROPIC_KEY", "sk-test")
@patch("shaked_wg_agent.parsers.llm_listing_parser.time.sleep")
def test_rate_limit_retry_success(mock_sleep):
    call_count = 0

    def mock_call(text, group_name):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("rate_limit_error: 429")
        return {"is_rental_offer": True, "price_ils": 3500}

    with patch(
        "shaked_wg_agent.parsers.llm_listing_parser._call_claude",
        side_effect=mock_call,
    ):
        result = parse_rental_post("some text", "group", post_id="rl-2")
    assert result is not None
    assert result["is_rental_offer"] is True
    mock_sleep.assert_called_once_with(2)


# UT-39: Malformed response -> return None, WARNING with first 200 chars
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.parsers.llm_listing_parser._ANTHROPIC_KEY", "sk-test")
def test_malformed_response(caplog):
    def mock_call(text, group_name):
        # Simulate LLM returning non-JSON directly through _parse_response
        from shaked_wg_agent.parsers.llm_listing_parser import _parse_response
        return _parse_response("This is not JSON at all, just random text output")

    with patch(
        "shaked_wg_agent.parsers.llm_listing_parser._call_claude",
        side_effect=mock_call,
    ):
        with caplog.at_level(logging.WARNING):
            result = parse_rental_post("some text", "group", post_id="mal-1")
    assert result is None


# UT-40: API error (500) -> return None, ERROR logged with post_id
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.parsers.llm_listing_parser._ANTHROPIC_KEY", "sk-test")
def test_api_error_500(caplog):
    with patch(
        "shaked_wg_agent.parsers.llm_listing_parser._call_claude",
        side_effect=Exception("Internal server error 500"),
    ):
        with caplog.at_level(logging.ERROR):
            result = parse_rental_post("some text", "group", post_id="err-1")
    assert result is None
    assert "err-1" in caplog.text


# UT-41: All posts fail -> fetch_listings() returns [], ERROR logged
@patch("shaked_wg_agent.scrapers.facebook_manual._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.scrapers.facebook_manual.check_llm_config", return_value=True)
@patch("shaked_wg_agent.scrapers.facebook_manual.parse_rental_post", return_value=None)
def test_all_posts_fail(mock_parse, mock_config, tmp_path, caplog):
    city = MagicMock()
    city.currency = "ILS"
    city.country = "IL"
    city.city_name = "Pardes Hanna"
    city.city_id = "pardes-hanna-region"

    posts = [
        {"post_id": "f1", "text": "דירת 3 חדרים להשכרה בפרדס חנה 3500 שקל"},
        {"post_id": "f2", "text": "דירת 4 חדרים להשכרה בכרכור 4200 שקל חדש"},
        {"post_id": "f3", "text": "וילה 5 חדרים להשכרה בכרכור 7500 שקל גדולה"},
    ]
    fp = tmp_path / "posts.json"
    fp.write_text(json.dumps(posts, ensure_ascii=False))

    scraper = ManualFacebookScraper("facebook-manual", str(fp), city)
    with caplog.at_level(logging.ERROR):
        results = scraper.fetch_listings()
    assert results == []
    assert "all" in caplog.text.lower() and "failed" in caplog.text.lower()
