"""Relevance scoring engine for WG listings.

Scoring breakdown (max 100 pts, capped):
  vegan_signal    — up to 35 pts (exact "vegan" > partial > pflanzlich > none)
  transit_lines   — up to 25 pts (intersection of listing transit_match_lines with profile)
  budget          — pass/fail gate (0 pts if outside budget, no penalty for within)
  roommate_age    — up to 15 pts (young signal present)
  freshness       — up to 15 pts (decays linearly over 14 days from first_seen_at)
  available_from  — up to 10 pts (within Shaked's move-in window)
  url_quality     — up to 10 pts (direct link > search_only > broken)
"""
from __future__ import annotations

import math
from datetime import UTC, date, datetime
from typing import Any

from shaked_wg_agent.config import (
    AGE_MATCH_BONUS,
    MOVE_IN_OPTIMAL_BONUS,
    STUDENT_BONUS,
    CityDefinition,
    SearchProfile,
)
from shaked_wg_agent.extractors.diet_signals import classify as _diet_classify
from shaked_wg_agent.extractors.negative_signals import detect_negative_signals
from shaked_wg_agent.extractors.quiet_signals import classify as _quiet_classify
from shaked_wg_agent.locale import get_locale


def _settlement_haystack(listing: dict[str, Any]) -> str:
    """Concatenate location fields used to match Hebrew settlement names."""
    parts = [
        str(listing.get("district") or ""),
        str(listing.get("location_text") or ""),
        str(listing.get("title") or ""),
        str(listing.get("summary") or ""),
    ]
    return " ".join(parts)


def _settlement_allowed(listing: dict[str, Any], allowlist: list[str]) -> bool:
    """True if haystack contains at least one allowlisted settlement substring."""
    if not allowlist:
        return True
    hay = _settlement_haystack(listing)
    for name in allowlist:
        n = name.strip()
        if n and n in hay:
            return True
    return False


def _vegan_score(signal: str, country: str = "CH") -> int:
    """Return 0–35 based on vegan_signal field content (locale-aware)."""
    if not signal:
        return 0
    locale = get_locale(country)
    lower = signal.lower()
    if lower in locale.vegan_no_signal:
        return 0
    if any(kw in lower for kw in locale.vegan_strong):
        return 35
    if any(kw in lower for kw in locale.vegan_partial):
        return 22
    if any(kw in lower for kw in locale.vegan_weak):
        return 12
    return 5  # signal exists but unrecognised — small positive


def _transit_score(match_lines: list[str], preferred_lines: list[str]) -> int:
    """Return 0–25 based on transit line intersection."""
    if not match_lines or not preferred_lines:
        return 0
    preferred_set = set(preferred_lines)
    matches = len(set(match_lines) & preferred_set)
    if matches == 0:
        return 0
    return min(25, 12 + (matches - 1) * 8)


def _listing_transit_lines(listing: dict[str, Any]) -> list[str]:
    raw = listing.get("transit_match_lines") or listing.get("tram_match_lines") or []
    return list(raw) if raw else []


def _roommate_score(signal: str, preferred_age: str) -> int:
    """Return 0–15 based on roommate age signal."""
    if preferred_age.lower() not in ("young", "jung"):
        return 8  # neutral when no preference
    if not signal:
        return 0
    lower = signal.lower()
    young_keywords = ("student", "jung", "young", "20", "21", "22", "23", "24", "25", "26", "27")
    if any(kw in lower for kw in young_keywords):
        return 15
    return 3


def _freshness_score(posted_date: str | None, first_seen_at: str | None) -> int:
    """Return 0–15 based on how recently the listing was posted/first seen.

    Uses posted_date when available (source date), else first_seen_at (when we
    first discovered it). Does NOT use last_seen_at — that updates every scan
    and would give every listing max freshness regardless of actual age.

    Decays linearly from 15 → 0 over 14 days.
    """
    date_str = posted_date or first_seen_at
    if not date_str:
        return 7  # unknown → neutral
    try:
        if "T" in date_str:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(date_str).replace(tzinfo=UTC)
    except ValueError:
        return 7
    now = datetime.now(UTC)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    age_days = max(0, (now - dt).days)
    score = math.ceil(15 * max(0, 1 - age_days / 14))
    return int(score)


def _available_score(available_from: str | None, move_in_from: str) -> int:
    """Return 0–10 based on whether the listing is available for Shaked's window.

    Scoring:
      available by 2026-08-31  → 10 pts  (works for June move-in)
      available by 2026-10-31  →  5 pts  (late but still possible)
      available_from = None    →  5 pts  (unknown → neutral)
      after 2026-10-31         →  0 pts  (too late)
    """
    if not available_from:
        return 5  # unknown → neutral
    try:
        avail = date.fromisoformat(str(available_from)[:10])
    except (ValueError, TypeError):
        return 5
    if avail <= date(2026, 8, 31):
        return 10
    if avail <= date(2026, 10, 31):
        return 5
    return 0


def _url_score(url_status: str) -> int:
    """Return 0–10 based on URL availability."""
    mapping = {
        "direct": 10,
        "search_only": 4,
        "broken_needs_recovery": 2,
        "": 0,
    }
    return mapping.get(url_status.lower() if url_status else "", 3)


def _profile_bonuses(listing: dict[str, Any], profile: SearchProfile) -> int:
    """Return M1 additive bonuses: age match, student orientation, move-in optimal."""
    bonus = 0

    age_min = listing.get("roommate_age_min")
    age_max = listing.get("roommate_age_max")
    if (
        profile.age is not None
        and age_min is not None
        and age_max is not None
        and age_min <= profile.age <= age_max
    ):
        bonus += AGE_MATCH_BONUS

    if profile.occupation_status == "student" and listing.get("is_student_oriented"):
        bonus += STUDENT_BONUS

    if (
        profile.move_in_optimal is not None
        and listing.get("available_from") == profile.move_in_optimal
    ):
        bonus += MOVE_IN_OPTIMAL_BONUS

    return bonus


def _age_hard_exclude(listing: dict[str, Any], profile: SearchProfile) -> bool:
    """Return True if listing's age range excludes the profile's age (hard exclude)."""
    if profile.age is None:
        return False
    age_min = listing.get("roommate_age_min")
    if age_min is not None and profile.age < age_min:
        return True
    age_max = listing.get("roommate_age_max")
    return age_max is not None and profile.age > age_max


def _budget_ok(price: int | None, profile: SearchProfile) -> bool:
    """Return False if price is outside budget (hard gate)."""
    if price is None:
        return True  # unknown price — don't disqualify
    return profile.budget_min <= price <= profile.budget_max


def score_listing(
    listing: dict[str, Any],
    profile: SearchProfile,
    city: CityDefinition | None = None,
) -> int:
    """Compute relevance score (0–100) for a single listing.

    Returns 0 if the listing fails the budget hard gate or settlement allowlist (when configured).
    """
    price = listing.get("price")
    if price is None:
        price = listing.get("price_chf")
    if not _budget_ok(price, profile):
        return 0

    if (
        city is not None
        and city.settlement_allowlist
        and not _settlement_allowed(listing, city.settlement_allowlist)
    ):
        return 0

    if _age_hard_exclude(listing, profile):
        return -1

    # M5: Negative-signal autofilter — run after age hard-exclude (early return saves time).
    _neg_text = listing.get("full_description") or listing.get("summary") or ""
    signals = detect_negative_signals(_neg_text)

    # W1.3: Run diet and quiet signal extractors when full_description is available.
    _full_desc = listing.get("full_description") or ""
    if _full_desc:
        _diet_result = _diet_classify(_full_desc)
        listing["is_vegetarian_friendly"] = _diet_result["is_vegetarian_friendly"]
        listing["diet_matched_keywords"] = _diet_result["matched_keywords"]

        _quiet_result = _quiet_classify(_full_desc)
        listing["is_quiet_friendly"] = _quiet_result["is_quiet_friendly"]

    # Gender: exclude only when restriction conflicts with profile (Shaked is female).
    # men_only → hard exclude. women_only → keep (Shaked is female).
    if signals["men_only"]:
        return -1

    # Tenant type: Shaked needs permanent accommodation.
    if signals["wochenaufenthalter"] or signals["business_only"]:
        return -1

    # Short Zwischenmiete: exclude.
    if signals["zwischenmiete_short"]:
        return -1

    lines = _listing_transit_lines(listing)

    # W1.3 extractor bonuses (applied to subscore, not score total cap)
    _diet_bonus = 2 if listing.get("is_vegetarian_friendly") else 0
    _quiet_bonus = 1 if listing.get("is_quiet_friendly") else 0

    # Subscore cap: vegan subscore max is 35, add diet_bonus capped at 35
    _vegan_subscore = min(
        35,
        _vegan_score(listing.get("vegan_signal", ""), listing.get("country", "CH"))
        + _diet_bonus,
    )
    # Roommate subscore max is 15, add quiet_bonus capped at 15
    _roommate_subscore = min(
        15,
        _roommate_score(listing.get("roommate_signal", ""), profile.preferred_roommate_age)
        + _quiet_bonus,
    )

    total = (
        _vegan_subscore
        + _transit_score(lines, profile.transit_lines)
        + _roommate_subscore
        + _freshness_score(listing.get("posted_date"), listing.get("first_seen_at"))
        + _available_score(listing.get("available_from"), profile.move_in_from)
        + _url_score(listing.get("url_status", ""))
        + _profile_bonuses(listing, profile)
    )

    # Advisory penalty (not a hard exclude).
    if signals["religion_preference"]:
        total -= 10

    return min(100, total)


# M4: statuses that are excluded from the active ranked list
_CLOSED_STATUSES: frozenset[str] = frozenset({"rejected", "replied_negative"})


def score_all(
    listings: list[dict[str, Any]],
    profile: SearchProfile,
    city: CityDefinition | None = None,
) -> list[dict[str, Any]]:
    """Re-score all listings in-place and return sorted (highest first).

    Listings with status 'rejected' or 'replied_negative' are excluded from
    the ranked portion and appended at the end (unranked) so they are preserved
    but never appear in the top-N selection.
    """
    active = [lst for lst in listings if lst.get("status") not in _CLOSED_STATUSES]
    closed = [lst for lst in listings if lst.get("status") in _CLOSED_STATUSES]
    for lst in active:
        lst["relevance_score"] = score_listing(lst, profile, city)
    ranked = sorted(active, key=lambda x: x.get("relevance_score", 0), reverse=True)
    return ranked + closed
