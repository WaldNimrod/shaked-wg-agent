"""Relevance scoring engine for WG listings.

Scoring breakdown (max 100 pts, capped):
  vegan_signal    — up to 35 pts (exact "vegan" > partial > pflanzlich > none)
  tram_lines      — up to 25 pts (intersection of listing tram_match_lines with config)
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

from shaked_wg_agent.config import AgentConfig

# Vegan signal keywords (ordered by strength)
_VEGAN_STRONG = {"vegan", "vegane", "veganer", "veganes", "tierfreie küche", "tierfreie wg"}
_VEGAN_PARTIAL = {"pflanzlich", "pflanzliche", "vegan-freundlich", "vegetarisch"}
_VEGAN_WEAK = {"kein fleisch", "kein fisch", "plant-based"}


def _vegan_score(signal: str) -> int:
    """Return 0–35 based on vegan_signal field content."""
    if not signal or signal.lower() in ("kein signal", "unbekannt", ""):
        return 0
    lower = signal.lower()
    if any(kw in lower for kw in _VEGAN_STRONG):
        return 35
    if any(kw in lower for kw in _VEGAN_PARTIAL):
        return 22
    if any(kw in lower for kw in _VEGAN_WEAK):
        return 12
    return 5  # signal exists but unrecognised — small positive


def _tram_score(match_lines: list[str], preferred_lines: list[str]) -> int:
    """Return 0–25 based on tram line intersection."""
    if not match_lines or not preferred_lines:
        return 0
    preferred_set = set(preferred_lines)
    matches = len(set(match_lines) & preferred_set)
    if matches == 0:
        return 0
    # Linear: 1 match → 12, 2 → 20, 3+ → 25
    return min(25, 12 + (matches - 1) * 8)


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


def _budget_ok(price_chf: int | None, cfg: AgentConfig) -> bool:
    """Return False if price is outside budget (hard gate)."""
    if price_chf is None:
        return True  # unknown price — don't disqualify
    return cfg.budget_min_chf <= price_chf <= cfg.budget_max_chf


def score_listing(listing: dict[str, Any], cfg: AgentConfig) -> int:
    """Compute relevance score (0–100) for a single listing.

    Returns 0 if the listing fails the budget hard gate.
    """
    price = listing.get("price_chf")
    if not _budget_ok(price, cfg):
        return 0

    total = (
        _vegan_score(listing.get("vegan_signal", ""))
        + _tram_score(listing.get("tram_match_lines", []), cfg.tram_lines)
        + _roommate_score(listing.get("roommate_signal", ""), cfg.preferred_roommate_age)
        + _freshness_score(listing.get("posted_date"), listing.get("first_seen_at"))
        + _available_score(listing.get("available_from"), cfg.move_in_from)
        + _url_score(listing.get("url_status", ""))
    )

    return min(100, total)


def score_all(listings: list[dict[str, Any]], cfg: AgentConfig) -> list[dict[str, Any]]:
    """Re-score all listings in-place and return sorted (highest first)."""
    for lst in listings:
        lst["relevance_score"] = score_listing(lst, cfg)
    return sorted(listings, key=lambda x: x.get("relevance_score", 0), reverse=True)
