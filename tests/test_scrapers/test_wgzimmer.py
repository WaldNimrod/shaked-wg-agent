"""Tests for shaked_wg_agent.scrapers.wgzimmer_pw.WgzimmerPlaywrightScraper.

All tests are mocked — no live network access is required.
"""
from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shaked_wg_agent.config import CityDefinition
from shaked_wg_agent.scrapers.base import ScrapedListing
from shaked_wg_agent.scrapers.wgzimmer_pw import (
    WgzimmerPlaywrightScraper,
    _is_recaptcha_blocked,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "scrapers"
_SEARCH_PAGE_HTML = (_FIXTURE_DIR / "wgzimmer_search_page.html").read_text(encoding="utf-8")

_RECAPTCHA_BLOCK_HTML = """
<html><body><div id="content">
  <h1>The processing of the request was stopped by Google reCaptcha, please try again.</h1>
  <form id="searchMateForm" action="/en/wgzimmer/search/mate.html" method="post"></form>
</div></body></html>
"""

_EMPTY_RESULTS_HTML = """
<html><body><div id="content">
  <div class="text"><h1>Available rooms in Basel City</h1></div>
  <ul class="list">
    <li id="list-header" class="search-mate-list-header">
      <a href="#"><div class="state">State</div><div class="cost">Cost</div></a>
    </li>
  </ul>
</div></body></html>
"""


def _make_city() -> CityDefinition:
    from shaked_wg_agent.config import BoundingBox

    return CityDefinition(
        city_id="basel",
        city_name="Basel",
        country="CH",
        currency="CHF",
        bounding_box=BoundingBox(west=7.5, east=7.7, south=47.5, north=47.6),
        available_sources=["wgzimmer", "flatfox"],
        zip_filter=["4051", "4052", "4053", "4054", "4055", "4056", "4057", "4058"],
    )


def _make_scraper() -> WgzimmerPlaywrightScraper:
    return WgzimmerPlaywrightScraper(
        source_id="wgzimmer",
        search_url="https://www.wgzimmer.ch/en/wgzimmer/search/mate/ch/baselstadt.html",
        city=_make_city(),
    )


# ---------------------------------------------------------------------------
# Unit tests — _is_recaptcha_blocked helper
# ---------------------------------------------------------------------------


def test_recaptcha_blocked_detected() -> None:
    assert _is_recaptcha_blocked(_RECAPTCHA_BLOCK_HTML) is True


def test_recaptcha_blocked_not_false_positive() -> None:
    assert _is_recaptcha_blocked(_SEARCH_PAGE_HTML) is False
    assert _is_recaptcha_blocked(_EMPTY_RESULTS_HTML) is False


# ---------------------------------------------------------------------------
# Unit tests — _dom_parse_results (no Playwright required)
# ---------------------------------------------------------------------------


def test_parse_listing_page_returns_listings() -> None:
    """Given the fixture HTML, _dom_parse_results returns ≥1 listing."""
    scraper = _make_scraper()
    results = scraper._dom_parse_results(_SEARCH_PAGE_HTML)

    assert len(results) >= 1, f"Expected ≥1 listing, got {len(results)}"
    for r in results:
        assert isinstance(r, ScrapedListing)
        assert r.source == "wgzimmer"
        assert r.direct_url.startswith("https://www.wgzimmer.ch")
        assert r.source_listing_id  # non-empty


def test_parse_listing_page_extracts_title() -> None:
    scraper = _make_scraper()
    results = scraper._dom_parse_results(_SEARCH_PAGE_HTML)
    titles = [r.title for r in results]
    assert any("Gundeli" in t for t in titles), f"Expected Gundeli in titles: {titles}"


def test_parse_listing_page_extracts_price() -> None:
    scraper = _make_scraper()
    results = scraper._dom_parse_results(_SEARCH_PAGE_HTML)
    prices = [r.price for r in results if r.price is not None]
    assert prices, "Expected at least one listing with a price"
    # Fixture has 800, 750, 900, 1200 CHF
    assert any(p in (800, 750, 900, 1200) for p in prices), f"Unexpected prices: {prices}"


def test_parse_listing_page_extracts_url() -> None:
    scraper = _make_scraper()
    results = scraper._dom_parse_results(_SEARCH_PAGE_HTML)
    assert any("123456" in r.source_listing_id for r in results)
    assert any(r.direct_url.endswith("123456.html") for r in results)


def test_parse_listing_page_detects_vegan() -> None:
    scraper = _make_scraper()
    results = scraper._dom_parse_results(_SEARCH_PAGE_HTML)
    # The fixture has "Veganes WG-Zimmer" which should trigger vegan detection
    vegan_results = [r for r in results if r.vegan_signal != "kein Signal"]
    assert vegan_results, "Expected at least one listing with vegan signal"


def test_parse_listing_page_detects_tram() -> None:
    scraper = _make_scraper()
    results = scraper._dom_parse_results(_SEARCH_PAGE_HTML)
    # Fixture has "Tram 14 und 16" in one title
    tram_results = [r for r in results if r.transit_match_lines]
    assert tram_results, "Expected at least one listing with tram lines detected"


# ---------------------------------------------------------------------------
# Test — zero results with warning logging
# ---------------------------------------------------------------------------


def test_zero_results_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Given an empty results page, _dom_parse_results returns [] — no crash."""
    scraper = _make_scraper()
    with caplog.at_level(logging.WARNING, logger="shaked_wg_agent.scrapers.wgzimmer_pw"):
        results = scraper._dom_parse_results(_EMPTY_RESULTS_HTML)
    assert results == []


def test_fetch_listings_logs_warning_on_zero_results() -> None:
    """fetch_listings logs a WARNING when 0 results are parsed from a valid (non-blocked) page."""
    scraper = _make_scraper()

    mock_page = MagicMock()
    mock_page.content.return_value = _EMPTY_RESULTS_HTML
    mock_page.title.return_value = "wgzimmer.ch - Basel City"
    mock_page.evaluate.return_value = None
    mock_page.wait_for_load_state.return_value = None
    mock_page.wait_for_timeout.return_value = None
    mock_page.goto.return_value = None

    mock_ctx = MagicMock()
    mock_ctx.new_page.return_value = mock_page

    mock_browser = MagicMock()
    mock_browser.new_context.return_value = mock_ctx

    mock_pw_instance = MagicMock()
    mock_pw_instance.chromium.launch.return_value = mock_browser

    mock_sync_pw_cm = MagicMock()
    mock_sync_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
    mock_sync_pw_cm.__exit__ = MagicMock(return_value=False)

    with patch(
        "shaked_wg_agent.scrapers.wgzimmer_pw.sync_playwright",
        return_value=mock_sync_pw_cm,
    ):
        results = scraper.fetch_listings()

    assert results == []


# ---------------------------------------------------------------------------
# Test — reCAPTCHA block handling in fetch_listings
# ---------------------------------------------------------------------------


def test_fetch_listings_returns_empty_on_recaptcha_block(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """When the POST response contains a reCAPTCHA block, fetch_listings returns []."""
    scraper = _make_scraper()

    mock_page = MagicMock()
    mock_page.content.return_value = _RECAPTCHA_BLOCK_HTML
    mock_page.title.return_value = "wgzimmer.ch - Looking for a free room"
    mock_page.evaluate.return_value = None
    mock_page.wait_for_load_state.return_value = None
    mock_page.wait_for_timeout.return_value = None
    mock_page.goto.return_value = None

    mock_ctx = MagicMock()
    mock_ctx.new_page.return_value = mock_page

    mock_browser = MagicMock()
    mock_browser.new_context.return_value = mock_ctx

    mock_pw_instance = MagicMock()
    mock_pw_instance.chromium.launch.return_value = mock_browser

    mock_sync_pw_cm = MagicMock()
    mock_sync_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
    mock_sync_pw_cm.__exit__ = MagicMock(return_value=False)

    with caplog.at_level(logging.WARNING, logger="shaked_wg_agent.scrapers.wgzimmer_pw"), patch(
        "shaked_wg_agent.scrapers.wgzimmer_pw.sync_playwright",
        return_value=mock_sync_pw_cm,
    ):
        results = scraper.fetch_listings()

    assert results == []
    assert any(
        "recaptcha" in record.message.lower() or "reCAPTCHA" in record.message
        for record in caplog.records
    ), f"Expected reCAPTCHA warning in logs, got: {[r.message for r in caplog.records]}"


# ---------------------------------------------------------------------------
# Test — submitForm() is called
# ---------------------------------------------------------------------------


def test_fetch_listings_calls_submit_form() -> None:
    """fetch_listings must call page.evaluate('submitForm()') to trigger reCAPTCHA v3."""
    scraper = _make_scraper()

    mock_page = MagicMock()
    # Return non-blocked content so the flow continues past the reCAPTCHA check
    mock_page.content.return_value = _SEARCH_PAGE_HTML
    mock_page.title.return_value = "wgzimmer.ch - Basel City"
    mock_page.evaluate.return_value = None
    mock_page.wait_for_load_state.return_value = None
    mock_page.wait_for_timeout.return_value = None
    mock_page.goto.return_value = None

    mock_ctx = MagicMock()
    mock_ctx.new_page.return_value = mock_page

    mock_browser = MagicMock()
    mock_browser.new_context.return_value = mock_ctx

    mock_pw_instance = MagicMock()
    mock_pw_instance.chromium.launch.return_value = mock_browser

    mock_sync_pw_cm = MagicMock()
    mock_sync_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
    mock_sync_pw_cm.__exit__ = MagicMock(return_value=False)

    with patch(
        "shaked_wg_agent.scrapers.wgzimmer_pw.sync_playwright",
        return_value=mock_sync_pw_cm,
    ):
        scraper.fetch_listings()

    mock_page.evaluate.assert_called_once_with("submitForm()")


# ---------------------------------------------------------------------------
# Test — fallback selector chain
# ---------------------------------------------------------------------------


def test_dom_fallback_selectors_on_non_standard_html() -> None:
    """If primary selector fails, fallback selectors catch li[class*='search-mate-entry']."""
    # Slight variant: no id='content', ul has no class
    html = """
    <html><body>
      <ul>
        <li class="search-mate-entry">
          <a href="/en/wgzimmer/mate/ch/baselstadt/2026-04-01-999001.html">
            <div class="state"><h3>Fallback Test Listing</h3></div>
            <div class="cost">650 CHF</div>
          </a>
        </li>
      </ul>
    </body></html>
    """
    scraper = _make_scraper()
    results = scraper._dom_parse_results(html)
    assert len(results) >= 1
    assert any("999001" in r.source_listing_id for r in results)
