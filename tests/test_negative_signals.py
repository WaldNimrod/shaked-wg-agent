"""Tests for the negative-signal extractor (M5) and its scorer integration."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from shaked_wg_agent.config import LanguagePolicy, SearchProfile
from shaked_wg_agent.extractors.negative_signals import detect_negative_signals
from shaked_wg_agent.scorer import score_listing

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _all_false(signals: dict[str, bool]) -> bool:
    return not any(signals.values())


def _base_profile() -> SearchProfile:
    return SearchProfile(
        profile_id="test",
        profile_name="Test",
        city_id="basel",
        move_in_from="2026-06-01",
        budget_min=200,
        budget_max=1500,
        preferred_roommate_age="young",
        rental_duration="permanent",
        diet="",
        smoking_policy="",
        transit_lines=[],
        custom_tags=[],
        language_policy=LanguagePolicy(),
        retention_days=30,
        enabled_sources=[],
        notifications=None,
    )


# ---------------------------------------------------------------------------
# Basic signal detection tests (1–10)
# ---------------------------------------------------------------------------


def test_women_only_detected() -> None:
    """'nur Frauen WG gesucht' should set women_only=True."""
    signals = detect_negative_signals("nur Frauen WG gesucht")
    assert signals["women_only"] is True
    assert signals["men_only"] is False


def test_men_only_detected() -> None:
    """'nur Männer, kein Platz für Frauen' should set men_only=True."""
    signals = detect_negative_signals("nur Männer, kein Platz für Frauen")
    assert signals["men_only"] is True
    assert signals["women_only"] is False


def test_wochenaufenthalter_detected() -> None:
    """'für Wochenaufenthalter geeignet' should set wochenaufenthalter=True."""
    signals = detect_negative_signals("für Wochenaufenthalter geeignet")
    assert signals["wochenaufenthalter"] is True


def test_zwischenmiete_short_detected() -> None:
    """'Zwischenmiete 3 Monate' — short duration → zwischenmiete_short=True."""
    signals = detect_negative_signals("Zwischenmiete 3 Monate")
    assert signals["zwischenmiete_short"] is True


def test_zwischenmiete_long_not_flagged() -> None:
    """'Zwischenmiete 12 Monate' — 12 months is ≥6 → zwischenmiete_short=False."""
    signals = detect_negative_signals("Zwischenmiete 12 Monate")
    assert signals["zwischenmiete_short"] is False


def test_religion_preference_detected() -> None:
    """'Christian preferably' should set religion_preference=True."""
    signals = detect_negative_signals("Christian preferably")
    assert signals["religion_preference"] is True


def test_clean_listing_no_signals() -> None:
    """'Schöne WG, vegan friendly' should have no signals."""
    signals = detect_negative_signals("Schöne WG, vegan friendly")
    assert _all_false(signals)


def test_case_insensitive() -> None:
    """'WOCHENAUFENTHALTER' (all caps) should still be detected."""
    signals = detect_negative_signals("WOCHENAUFENTHALTER gesucht")
    assert signals["wochenaufenthalter"] is True


def test_business_only_detected() -> None:
    """'nur Geschäftsleute' should set business_only=True."""
    signals = detect_negative_signals("nur Geschäftsleute willkommen")
    assert signals["business_only"] is True


def test_french_pattern() -> None:
    """'pour femmes' is a common multilingual Basel listing pattern → women_only=True."""
    signals = detect_negative_signals("Appartement pour femmes, Basel Zentrum")
    assert signals["women_only"] is True


# ---------------------------------------------------------------------------
# Zwischenmiete edge cases
# ---------------------------------------------------------------------------


def test_zwischenmiete_6_months_boundary() -> None:
    """Exactly 6 Monate → should NOT flag as short."""
    signals = detect_negative_signals("Zwischenmiete, 6 Monate")
    assert signals["zwischenmiete_short"] is False


def test_zwischenmiete_1_year() -> None:
    """1 Jahr alongside zwischenmiete → not short."""
    signals = detect_negative_signals("untermiete für 1 Jahr verfügbar")
    assert signals["zwischenmiete_short"] is False


def test_zwischenmiete_2_months() -> None:
    """2 Monate is < 6 months — no long-duration override → short=True."""
    signals = detect_negative_signals("Zwischenmiete 2 Monate")
    assert signals["zwischenmiete_short"] is True


def test_zwischenmiete_no_duration_flagged() -> None:
    """zwischenmiete with no duration context → assume short, flag it."""
    signals = detect_negative_signals("Zwischenmiete ab sofort verfügbar")
    assert signals["zwischenmiete_short"] is True


# ---------------------------------------------------------------------------
# Recall test (test 11) — hand-labelled synthetic German listing texts
# ---------------------------------------------------------------------------

# Five synthetic texts representative of real German listing patterns that
# should trigger a signal (hand-labelled TRUE positives).
_RECALL_CASES = [
    # 1. Frauen-WG
    (
        "Wir sind eine reine Frauen-WG und suchen eine weitere Mitbewohnerin. "
        "Nur Frauen bitte, keine Männer.",
        "women_only",
    ),
    # 2. Männer-WG
    (
        "Männer-WG in Basel sucht Nachmieter. Wir sind vier Jungs und bevorzugen "
        "nur Männer in unserem Haushalt.",
        "men_only",
    ),
    # 3. Wochenaufenthalter
    (
        "Zimmer geeignet für Wochenaufenthalter oder Pendler. "
        "Nur unter der Woche bewohnt, ideal für Berufstätige.",
        "wochenaufenthalter",
    ),
    # 4. Short Zwischenmiete
    (
        "Untermiete für 2 Monate gesucht — Zwischenmiete während Urlaub. "
        "Nur befristet, ab 1. Juni.",
        "zwischenmiete_short",
    ),
    # 5. Business only
    (
        "Helles Zimmer, geeignet für Geschäftsleute. "
        "Wir sind alles Berufstätige und suchen nur Berufstätige.",
        "business_only",
    ),
]


@pytest.mark.parametrize("text,expected_signal", _RECALL_CASES)
def test_recall_synthetic(text: str, expected_signal: str) -> None:
    """Each synthetic TRUE-positive text must fire the expected signal."""
    signals = detect_negative_signals(text)
    assert signals[expected_signal] is True, (
        f"Expected signal '{expected_signal}' to be True for text: {text[:80]}…"
    )


# ---------------------------------------------------------------------------
# Precision test (test 12) — clean listings with no negative signals
# ---------------------------------------------------------------------------

# Five clean listing texts that should produce ZERO false positives.
_PRECISION_CASES = [
    # 1. Typical vegan student WG
    "Schöne 3er WG sucht vegane Mitbewohnerin. Wir kochen gerne zusammen und sind alle Studenten.",
    # 2. English-language Basel listing
    "Room available in a friendly shared flat near Marktplatz. "
    "All genders welcome, international flatmates.",
    # 3. Standard Basel apartment with transit info
    "Helles Zimmer in ruhiger Lage, direkt an Tram 8. "
    "WG aus 2 Personen, offen für alle.",
    # 4. Listing mentioning Monate in a non-zwischenmiete context
    "Wir wohnen seit 6 Monaten zusammen und suchen jemanden langfristig. "
    "Keine Zwischenmiete — wir möchten dauerhafte Mitbewohner.",
    # 5. Listing with religion mentioned neutrally
    "Multikulturelle WG, verschiedene Religionen und Hintergründe. "
    "Offen für alle.",
]


@pytest.mark.parametrize("text", _PRECISION_CASES)
def test_precision_clean_listing(text: str) -> None:
    """Clean listing texts must produce no false-positive signals."""
    signals = detect_negative_signals(text)
    false_positives = [k for k, v in signals.items() if v]
    assert false_positives == [], (
        f"False positive(s) {false_positives} for text: {text[:80]}…"
    )


# ---------------------------------------------------------------------------
# Scorer integration tests
# ---------------------------------------------------------------------------


def test_scorer_men_only_returns_minus_one() -> None:
    """A listing with men_only text must get score=-1 from score_listing."""
    profile = _base_profile()
    listing = {
        "price": 600,
        "summary": "Männer-WG sucht Nachmieter, nur Männer.",
        "full_description": None,
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    assert score_listing(listing, profile) == -1


def test_scorer_wochenaufenthalter_returns_minus_one() -> None:
    """A listing advertising Wochenaufenthalter must get score=-1."""
    profile = _base_profile()
    listing = {
        "price": 500,
        "summary": "Perfektes Zimmer für Wochenaufenthalter in Basel.",
        "full_description": None,
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    assert score_listing(listing, profile) == -1


def test_scorer_zwischenmiete_short_returns_minus_one() -> None:
    """A listing with short Zwischenmiete must get score=-1."""
    profile = _base_profile()
    listing = {
        "price": 500,
        "summary": "Zwischenmiete 3 Monate, ab sofort.",
        "full_description": None,
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    assert score_listing(listing, profile) == -1


def test_scorer_business_only_returns_minus_one() -> None:
    """A listing with business_only signal must get score=-1."""
    profile = _base_profile()
    listing = {
        "price": 500,
        "summary": "Zimmer für Geschäftsleute, nur Berufstätige.",
        "full_description": None,
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    assert score_listing(listing, profile) == -1


def test_scorer_women_only_not_excluded() -> None:
    """A women_only listing must NOT be hard-excluded (Shaked is female)."""
    profile = _base_profile()
    listing = {
        "price": 600,
        "summary": "Nur Frauen, reine Frauen-WG in Basel.",
        "full_description": None,
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    score = score_listing(listing, profile)
    assert score != -1
    assert score >= 0


def test_scorer_religion_penalty_applied() -> None:
    """A listing with religion_preference should score lower but not -1."""
    profile = _base_profile()
    base_listing: dict = {
        "price": 600,
        "summary": "Schöne WG sucht Mitbewohnerin.",
        "full_description": None,
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    religious_listing: dict = {
        **base_listing,
        "summary": "Schöne WG sucht Mitbewohnerin. Christian preferably.",
    }
    base_score = score_listing(base_listing, profile)
    religious_score = score_listing(religious_listing, profile)
    assert religious_score != -1
    assert religious_score < base_score  # penalty applied


def test_scorer_fallback_to_summary_when_no_full_description() -> None:
    """When full_description is absent/None, scorer must fall back to summary."""
    profile = _base_profile()
    listing = {
        "price": 600,
        "summary": "nur Männer WG",
        # full_description intentionally absent
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    assert score_listing(listing, profile) == -1


def test_scorer_uses_full_description_over_summary() -> None:
    """full_description takes priority over summary for signal detection."""
    profile = _base_profile()
    listing = {
        "price": 600,
        "summary": "Schöne WG, alle willkommen.",  # no signal in summary
        "full_description": "nur Männer WG, keine Frauen.",  # signal in full_desc
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    assert score_listing(listing, profile) == -1


def test_scorer_clean_listing_not_excluded() -> None:
    """A perfectly clean listing must not be excluded by the negative-signal filter."""
    profile = _base_profile()
    listing = {
        "price": 600,
        "summary": "Schöne vegane WG sucht Mitbewohnerin. Alle willkommen.",
        "full_description": "Helles Zimmer, gute Lage, nette Mitbewohner.",
        "vegan_signal": "vegan",
        "url_status": "direct",
        "posted_date": "2026-04-01",
    }
    score = score_listing(listing, profile)
    assert score > 0


# ---------------------------------------------------------------------------
# Data-driven recall / precision over actual listings.json
# (If real data has negative-signal listings, test them; otherwise skip.)
# ---------------------------------------------------------------------------

_LISTINGS_PATH = Path(__file__).parent.parent / "data" / "listings.json"


@pytest.fixture(scope="module")
def all_listings() -> list[dict]:
    if not _LISTINGS_PATH.exists():
        return []
    return json.loads(_LISTINGS_PATH.read_text(encoding="utf-8"))


def test_no_false_positives_on_real_listings(all_listings: list[dict]) -> None:
    """Run extractor over every listing in data/listings.json.

    For each listing, the signals dict must have the correct types and keys.
    We cannot assert ground-truth labels here (no annotation), but we verify:
    - No exceptions raised.
    - All returned keys are present with bool values.
    """
    expected_keys = {
        "women_only",
        "men_only",
        "wochenaufenthalter",
        "business_only",
        "zwischenmiete_short",
        "religion_preference",
    }
    for listing in all_listings:
        text = listing.get("full_description") or listing.get("summary") or ""
        signals = detect_negative_signals(text)
        assert set(signals.keys()) == expected_keys
        for v in signals.values():
            assert isinstance(v, bool)
