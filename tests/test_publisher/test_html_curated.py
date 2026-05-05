"""Tests for shaked_wg_agent.publisher.html_curated — WP W1.4 acceptance gate."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_listing(
    idx: int,
    score: int = 50,
    is_vegetarian_friendly: bool = False,
    price: int = 900,
) -> dict:
    return {
        "listing_id": f"test-listing-{idx}",
        "title": f"Test Listing {idx}",
        "district": f"Gundeldingen",
        "location_text": "Basel, CH",
        "price_chf": price,
        "price": price,
        "available_from": "2026-06-01",
        "direct_url": f"https://example.com/listing/{idx}",
        "source_search_url": f"https://example.com/search?q={idx}",
        "url_status": "direct",
        "vegan_signal": "vegan friendly" if is_vegetarian_friendly else "",
        "roommate_signal": "young students",
        "summary": f"Nice WG in Basel, listing number {idx}",
        "transit_match_lines": ["3", "8"],
        "tram_match_lines": ["3", "8"],
        "relevance_score": score,
        "status": "neu",
        "first_seen_at": "2026-04-28T10:00:00+00:00",
        "posted_date": "2026-04-28",
        "full_description": "vegan friendly cook together" if is_vegetarian_friendly else "nice flat",
        "is_vegetarian_friendly": is_vegetarian_friendly,
        "is_quiet_friendly": False,
        "is_student_oriented": True,
        "source": "wg-gesucht",
        "country": "CH",
        "currency": "CHF",
    }


def _make_profile():
    """Return a minimal SearchProfile-like object for testing."""
    from shaked_wg_agent.config import SearchProfile, LanguagePolicy

    return SearchProfile(
        profile_id="default",
        profile_name="Test Profile",
        city_id="basel",
        move_in_from="2026-06-01",
        budget_min=500,
        budget_max=1000,
        preferred_roommate_age="young",
        rental_duration="permanent",
        diet="vegan",
        transit_lines=["3", "8", "2"],
        language_policy=LanguagePolicy(),
    )


# ---------------------------------------------------------------------------
# 1. test_rebuild_produces_html_file
# ---------------------------------------------------------------------------

def test_rebuild_produces_html_file(tmp_path: Path) -> None:
    """rebuild_html() must produce a file at the --out path."""
    out = tmp_path / "test_output.html"

    from shaked_wg_agent.publisher.html_curated import rebuild_html

    result = rebuild_html(profile_id=None, top=10, out=str(out))

    assert result.exists(), f"Output file not created at {result}"
    assert result.stat().st_size > 0, "Output file is empty"


# ---------------------------------------------------------------------------
# 2. test_rebuild_html_structure
# ---------------------------------------------------------------------------

def test_rebuild_html_structure(tmp_path: Path) -> None:
    """Output must contain required structural elements."""
    out = tmp_path / "structure_test.html"

    from shaked_wg_agent.publisher.html_curated import rebuild_html

    rebuild_html(profile_id=None, top=10, out=str(out))
    content = out.read_text(encoding="utf-8")

    assert "<html" in content, "Missing <html> tag"
    assert "<head" in content, "Missing <head> tag"
    assert "<body" in content, "Missing <body> tag"
    # Score table section
    assert "score-matrix-tbody" in content, "Missing score matrix table body"
    # At least one listing card
    assert "data-listing-card" in content, "Missing listing card(s)"
    # Check for the Hebrew header text
    assert "דירות לשקד" in content, "Missing Hebrew header content"


# ---------------------------------------------------------------------------
# 3. test_rebuild_runtime_under_30s
# ---------------------------------------------------------------------------

def test_rebuild_runtime_under_30s(tmp_path: Path) -> None:
    """rebuild_html() must complete in ≤ 30 seconds."""
    from shaked_wg_agent.persistence import load_listings

    listings = load_listings()
    if not listings:
        pytest.skip("No listings in data/listings.json — skipping timing test")

    out = tmp_path / "timing_test.html"
    t0 = time.monotonic()

    from shaked_wg_agent.publisher.html_curated import rebuild_html

    rebuild_html(profile_id=None, top=10, out=str(out))
    elapsed = time.monotonic() - t0

    assert elapsed <= 30.0, f"rebuild_html() took {elapsed:.1f}s > 30s limit"


# ---------------------------------------------------------------------------
# 4. test_rebuild_top_n_parameter
# ---------------------------------------------------------------------------

def test_rebuild_top_n_parameter(tmp_path: Path) -> None:
    """With top=5, the output must contain exactly 5 listing cards."""
    from shaked_wg_agent.publisher.html_curated import build_html

    profile = _make_profile()
    # Create 10 listings; only top 5 should appear
    listings = [_make_listing(i, score=100 - i * 5) for i in range(10)]

    html = build_html(listings, profile, city=None, top=5)

    # Count <article tags — each listing card is one <article element
    card_count = html.count("<article ")
    assert card_count == 5, f"Expected 5 cards with top=5, got {card_count}"


# ---------------------------------------------------------------------------
# 5. test_rebuild_cooking_culture_badge
# ---------------------------------------------------------------------------

def test_rebuild_cooking_culture_badge(tmp_path: Path) -> None:
    """Listing with is_vegetarian_friendly=True must render a cooking-culture badge."""
    from shaked_wg_agent.publisher.html_curated import build_html

    profile = _make_profile()
    listings = [
        _make_listing(1, score=80, is_vegetarian_friendly=True),
        _make_listing(2, score=70, is_vegetarian_friendly=False),
    ]

    html = build_html(listings, profile, city=None, top=2)

    assert "Cooking-Culture" in html, (
        "Expected 🌱 Cooking-Culture badge for is_vegetarian_friendly=True listing"
    )
