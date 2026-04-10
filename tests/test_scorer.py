"""Unit tests for the relevance scoring engine."""
from __future__ import annotations

import pytest

from shaked_wg_agent.config import AgentConfig, LanguagePolicy
from shaked_wg_agent.scorer import (
    _budget_ok,
    _freshness_score,
    _roommate_score,
    _tram_score,
    _url_score,
    _vegan_score,
    score_listing,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base_config() -> AgentConfig:
    return AgentConfig(
        profile_name="Test",
        target_city="Basel",
        move_in_from="2026-06-01",
        budget_min_chf=200,
        budget_max_chf=1000,
        preferred_roommate_age="young",
        diet="vegan",
        tram_lines=["2", "3", "8", "16"],
        language_policy=LanguagePolicy(),
        retention_days=30,
        project_window_days=60,
        project_start="2026-04-09",
        project_end="2026-06-08",
        manual_triggers_only=True,
    )


@pytest.fixture()
def perfect_listing() -> dict:
    return {
        "price_chf": 700,
        "vegan_signal": "vegane Küche, kein Fleisch",
        "tram_match_lines": ["2", "3"],
        "roommate_signal": "Studenten WG 22 Jahre",
        "posted_date": "2026-04-09",
        "url_status": "direct",
    }


# ---------------------------------------------------------------------------
# Vegan score
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("signal,expected_min", [
    ("vegane WG", 35),
    ("pflanzlich orientiert", 22),
    ("kein Fleisch", 12),
    ("kein Signal", 0),
    ("unbekannt", 0),
    ("", 0),
])
def test_vegan_score(signal: str, expected_min: int) -> None:
    assert _vegan_score(signal) >= expected_min


def test_vegan_score_strong_max() -> None:
    assert _vegan_score("vegane Küche") == 35


def test_vegan_score_none() -> None:
    assert _vegan_score("kein Signal") == 0


# ---------------------------------------------------------------------------
# Tram score
# ---------------------------------------------------------------------------

def test_tram_score_no_match() -> None:
    assert _tram_score(["1", "6"], ["2", "3", "8", "16"]) == 0


def test_tram_score_one_match() -> None:
    assert _tram_score(["2"], ["2", "3", "8"]) == 12


def test_tram_score_two_matches() -> None:
    assert _tram_score(["2", "3"], ["2", "3", "8"]) == 20


def test_tram_score_three_or_more() -> None:
    assert _tram_score(["2", "3", "8", "16"], ["2", "3", "8", "16"]) == 25


def test_tram_score_empty_inputs() -> None:
    assert _tram_score([], ["2"]) == 0
    assert _tram_score(["2"], []) == 0


# ---------------------------------------------------------------------------
# Budget gate
# ---------------------------------------------------------------------------

def test_budget_ok_within_range(base_config: AgentConfig) -> None:
    assert _budget_ok(700, base_config) is True


def test_budget_ok_at_min(base_config: AgentConfig) -> None:
    assert _budget_ok(200, base_config) is True


def test_budget_ok_at_max(base_config: AgentConfig) -> None:
    assert _budget_ok(1000, base_config) is True


def test_budget_fail_over(base_config: AgentConfig) -> None:
    assert _budget_ok(1100, base_config) is False


def test_budget_fail_under(base_config: AgentConfig) -> None:
    assert _budget_ok(100, base_config) is False


def test_budget_none_passes(base_config: AgentConfig) -> None:
    assert _budget_ok(None, base_config) is True


# ---------------------------------------------------------------------------
# Roommate score
# ---------------------------------------------------------------------------

def test_roommate_young_match() -> None:
    assert _roommate_score("Studenten WG, 22 Jahre", "young") == 15


def test_roommate_young_no_signal() -> None:
    assert _roommate_score("", "young") == 0


def test_roommate_no_preference() -> None:
    # When no age preference, score is neutral (non-zero)
    assert _roommate_score("ältere WG, 40+", "any") > 0


# ---------------------------------------------------------------------------
# Freshness score
# ---------------------------------------------------------------------------

def test_freshness_today() -> None:
    from datetime import date
    today = date.today().isoformat()
    assert _freshness_score(today, None) >= 13  # very fresh


def test_freshness_old_date() -> None:
    assert _freshness_score("2020-01-01", None) == 0


def test_freshness_unknown() -> None:
    assert _freshness_score(None, None) == 7  # neutral


# ---------------------------------------------------------------------------
# URL score
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status,expected", [
    ("direct", 10),
    ("search_only", 4),
    ("broken_needs_recovery", 2),
])
def test_url_score(status: str, expected: int) -> None:
    assert _url_score(status) == expected


# ---------------------------------------------------------------------------
# Full listing score
# ---------------------------------------------------------------------------

def test_score_listing_perfect(perfect_listing: dict, base_config: AgentConfig) -> None:
    score = score_listing(perfect_listing, base_config)
    assert score >= 80, f"Expected high score, got {score}"


def test_score_listing_over_budget(perfect_listing: dict, base_config: AgentConfig) -> None:
    perfect_listing["price_chf"] = 2000
    assert score_listing(perfect_listing, base_config) == 0


def test_score_listing_no_vegan(perfect_listing: dict, base_config: AgentConfig) -> None:
    perfect_listing["vegan_signal"] = "kein Signal"
    score = score_listing(perfect_listing, base_config)
    # Score should drop but not be catastrophic
    assert score < 70


def test_score_listing_capped_at_100(perfect_listing: dict, base_config: AgentConfig) -> None:
    # Even in best case, score should not exceed 100
    assert score_listing(perfect_listing, base_config) <= 100
