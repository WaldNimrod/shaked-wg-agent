"""Diet signal extractor — detect vegetarian/vegan-friendly WG households.

Design notes — avoiding false positives:
  The regex matches keyword forms. Context scoring then decides confidence:

  HIGH confidence (context words within 50 chars of keyword):
    "wir", "unser", "wg", "küche", "haushalt", "kochen", "wohnung", "leben"
    → These indicate the WG household has a diet, not just a nearby restaurant.

  LOW confidence (keyword present but no WG-subject context):
    → Still classified as True (detect=True) but flagged as low confidence.
    → Examples: "veganes Restaurant", "Ich suche vegane WG" (applicant, not host).

  False positive avoidance strategy:
    Phrase patterns that indicate the applicant (not the WG) is vegan, or that
    mention external vegan businesses, are NOT subject-matched — they lack the
    WG-subject context words. The context window of 50 chars catches "wir sind vegan"
    and "vegane WG" but misses "veganes Restaurant um die Ecke".
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Keyword pattern (case-insensitive, German + English)
# ---------------------------------------------------------------------------
_DIET_PATTERN = re.compile(
    r"vegan|vegetar|pflanzenbasiert|fleischlos|plant[\s\-]?based"
    r"|veggi|bio[\s\-]?k[üu]che|tierfreie[\s\-]?k[üu]che|tierfreundlich",
    re.IGNORECASE,
)

# Subject-context words that indicate the WG household (not a restaurant/applicant)
_SUBJECT_CONTEXT = re.compile(
    r"wir\b|unser|wg\b|wg-|k[üu]che|haushalt|kochen|wohnung|leben|mitbewohner|"
    r"wg\s*sucht|wir\s+sind|wir\s+kochen|unsere\s+wg",
    re.IGNORECASE,
)

# Phrases that strongly suggest the match is about a restaurant or applicant,
# NOT the WG household diet — used to downgrade confidence.
_FALSE_POSITIVE_HINTS = re.compile(
    r"restaurant\b|bistro\b|café\b|cafe\b|laden\b|imbiss\b"
    r"|ich\s+bin\s+(selbst\s+)?vegan|ich\s+bin\s+(selbst\s+)?vegetar"
    r"|als\s+veganerin\b|als\s+veganer\b",
    re.IGNORECASE,
)

_CONTEXT_WINDOW = 50  # chars on each side of a keyword match


def _has_subject_context(text: str, match_start: int, match_end: int) -> bool:
    """Return True if WG-subject context words appear within ±50 chars of the keyword."""
    window_start = max(0, match_start - _CONTEXT_WINDOW)
    window_end = min(len(text), match_end + _CONTEXT_WINDOW)
    window = text[window_start:window_end]
    return bool(_SUBJECT_CONTEXT.search(window))


def _matched_keywords(text: str) -> list[str]:
    """Return list of distinct matched keyword strings (lowercase)."""
    return list({m.group(0).lower() for m in _DIET_PATTERN.finditer(text)})


def detect(text: str) -> bool:
    """Return True if text indicates a vegetarian/vegan-friendly WG household.

    Checks for diet keywords. Returns True even for low-confidence matches
    (the caller can use classify() for full confidence detail).
    """
    if not text:
        return False
    return bool(_DIET_PATTERN.search(text))


def classify(text: str) -> dict:
    """Return classification dict for diet signals.

    Returns:
        {
            "is_vegetarian_friendly": bool,
            "matched_keywords": list[str],
            "confidence": "high" | "low" | "none",
        }
    """
    if not text:
        return {
            "is_vegetarian_friendly": False,
            "matched_keywords": [],
            "confidence": "none",
        }

    matches = list(_DIET_PATTERN.finditer(text))
    if not matches:
        return {
            "is_vegetarian_friendly": False,
            "matched_keywords": [],
            "confidence": "none",
        }

    keywords = list({m.group(0).lower() for m in matches})

    # Check for false-positive hints — if dominant signals point elsewhere, downgrade
    has_fp_hint = bool(_FALSE_POSITIVE_HINTS.search(text))

    # Check for subject context around any of the matches
    any_high = any(
        _has_subject_context(text, m.start(), m.end()) for m in matches
    )

    if any_high and not has_fp_hint:
        confidence = "high"
    elif has_fp_hint and not any_high:
        # Strong false-positive indicator without subject context → still detect but low
        confidence = "low"
    else:
        confidence = "low"

    return {
        "is_vegetarian_friendly": True,
        "matched_keywords": keywords,
        "confidence": confidence,
    }
