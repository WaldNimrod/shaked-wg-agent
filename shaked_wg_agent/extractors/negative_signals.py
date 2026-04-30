"""Negative-signal detector for WG listing text.

Detects hard-exclude signals (gender restrictions, temporary-only tenants,
short Zwischenmiete) and advisory signals (religion preference) from listing
body text (full_description or summary).
"""
from __future__ import annotations

import re

# --- Pattern lists -----------------------------------------------------------

_WOMEN_ONLY_PATTERNS = [
    "nur frauen",
    "frauen-wg",
    "frauenwg",
    "women only",
    "female only",
    "nur damen",
    "damen-wg",
    "solo donne",
    "pour femmes",
]

_MEN_ONLY_PATTERNS = [
    "nur männer",
    "männer-wg",
    "men only",
    "male only",
    "nur herren",
    "herren-wg",
    "solo uomini",
]

_WOCHENAUFENTHALTER_PATTERNS = [
    "wochenaufenthalter",
    "wochenaufenthalerin",
    "pendler",
    "nur wochenaufenthalter",
]

_BUSINESS_ONLY_PATTERNS = [
    "geschäftsleute",
    "business only",
    "berufstätige only",
    "nur berufstätige",
]

_ZWISCHENMIETE_PATTERNS = [
    "zwischenmiete",
    "untermiete",
    "temporary stay",
    "nur befristet",
    "interim rent",
]

_RELIGION_PATTERNS = [
    "christian preferably",
    "christlich bevorzugt",
    "religiös",
    "catholisch bevorzugt",
]

# Duration indicators that mean ≥6 months — if present alongside zwischenmiete,
# do NOT flag zwischenmiete_short.
_LONG_DURATION_RE = re.compile(
    # Numeric months ≥6: "6 Monate", "6 Monaten", "12 Monate", etc.
    r"(?<!\d)(6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24)\s*monat(?:e|en)?"
    # Numeric years: "1 Jahr", "1 Jahre", "2 Jahren", etc.
    r"|(?<!\d)[1-9]\d*\s*jahr(?:e|en)?"
    # Written-out years in German: "ein Jahr", "zwei Jahre", etc.
    r"|(?:^|(?<=\s))(ein|zwei|drei|vier|f[uü]nf|sechs|sieben|acht|neun|zehn|elf|zw[oö]lf)\s*jahr(?:e|en)?",
    re.IGNORECASE,
)


def _any_pattern(text: str, patterns: list[str]) -> bool:
    """Return True if any pattern is found as a substring in text."""
    return any(p in text for p in patterns)


def detect_negative_signals(text: str) -> dict[str, bool]:
    """Detect negative signals in listing text (summary + full_description).

    Args:
        text: Concatenated listing text to search (summary and/or full_description).

    Returns:
        Dict mapping signal name → bool (True = signal present).
        Keys: women_only, men_only, wochenaufenthalter, business_only,
              zwischenmiete_short, religion_preference.
    """
    lower = text.lower() if text else ""

    women_only = _any_pattern(lower, _WOMEN_ONLY_PATTERNS)
    men_only = _any_pattern(lower, _MEN_ONLY_PATTERNS)
    wochenaufenthalter = _any_pattern(lower, _WOCHENAUFENTHALTER_PATTERNS)
    business_only = _any_pattern(lower, _BUSINESS_ONLY_PATTERNS)
    religion_preference = _any_pattern(lower, _RELIGION_PATTERNS)

    # Zwischenmiete: flag only if the text does NOT also indicate a long duration (≥6 months).
    zwischenmiete_raw = _any_pattern(lower, _ZWISCHENMIETE_PATTERNS)
    if zwischenmiete_raw and _LONG_DURATION_RE.search(lower):
        zwischenmiete_short = False
    else:
        zwischenmiete_short = zwischenmiete_raw

    return {
        "women_only": women_only,
        "men_only": men_only,
        "wochenaufenthalter": wochenaufenthalter,
        "business_only": business_only,
        "zwischenmiete_short": zwischenmiete_short,
        "religion_preference": religion_preference,
    }
