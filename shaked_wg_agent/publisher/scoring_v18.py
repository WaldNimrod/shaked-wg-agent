"""Thin wrapper exposing the v1.8/v1.9 scorer for the curated HTML publisher.

The canonical scoring logic lives in shaked_wg_agent.scorer.  This module
re-exports the public API so html_curated.py has a stable, versioned import
target without duplicating any logic.
"""
from __future__ import annotations

from typing import Any

# Re-export the full public surface from the canonical scorer.
from shaked_wg_agent.config import CityDefinition, SearchProfile  # noqa: F401
from shaked_wg_agent.scorer import (  # noqa: F401
    score_all,
    score_listing,
)


def score_top_n(
    listings: list[dict[str, Any]],
    profile: SearchProfile,
    city: CityDefinition | None = None,
    top: int = 10,
) -> list[dict[str, Any]]:
    """Score *listings* in-place, sort descending, return the top-N active ones.

    Listings whose status is 'rejected' or 'replied_negative' are excluded
    from the ranked output (they are handled by the underlying scorer already).
    """
    ranked = score_all(listings, profile, city)
    # score_all already excludes closed statuses from the ranked head.
    # We only want listings with a positive score.
    active = [lst for lst in ranked if lst.get("relevance_score", 0) > 0]
    return active[:top]
