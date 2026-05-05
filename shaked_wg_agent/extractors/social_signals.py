"""Social signal extractor — named roommates, age ranges, social vibe.

Detects:
  - Named roommates (e.g. "Ich bin Lisa, 26")
  - Age ranges mentioned in the listing (e.g. "wir sind 22 und 28 Jahre alt")
  - Social vibe: "community" (cooking together, shared activities) vs "neutral"
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Named roommate patterns
# ---------------------------------------------------------------------------

# German/English intro: "Ich bin Lisa", "Ich heiße Tom", "I am Sarah"
_NAMED_INTRO = re.compile(
    r"ich\s+bin\s+([A-ZÄÖÜa-zäöü][a-zäöü]+)"
    r"|ich\s+hei[ßs]e\s+([A-ZÄÖÜa-zäöü][a-zäöü]+)"
    r"|i\s+am\s+([A-Za-z][a-z]+)"
    r"|my\s+name\s+is\s+([A-Za-z][a-z]+)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Age range patterns
# ---------------------------------------------------------------------------

# "wir sind 22 und 28 Jahre alt"
# "zwischen 22 und 28"
# "ages 23-29"
# "we are 24 and 27 years old"
_AGE_RANGE_MULTI = re.compile(
    r"(?:zwischen|between)\s+(\d{2})\s+(?:und|and)\s+(\d{2})"
    r"|(\d{2})\s+(?:und|and)\s+(\d{2})\s+(?:jahre?|years?)",
    re.IGNORECASE,
)

# Single age mention: "Ich bin 26 Jahre alt"
_AGE_SINGLE = re.compile(
    r"(?:ich\s+bin|i\s+am)\s+(\d{2})\s*(?:jahre?|years?)?\s*(?:alt)?",
    re.IGNORECASE,
)

# Ages in parentheses after name: "Lisa (25)", "Tom (28)"
_AGE_IN_PARENS = re.compile(
    r"[A-ZÄÖÜa-zäöü][a-zäöü]+\s*\((\d{2})\)",
)

# ---------------------------------------------------------------------------
# Social vibe patterns
# ---------------------------------------------------------------------------

_COMMUNITY_PATTERN = re.compile(
    r"kochen\s+(zusammen|gemeinsam)"
    r"|gemeinsam\s+kochen"
    r"|cook\s+together"
    r"|gemeinsame\s+(abende|aktivit)"
    r"|wir\s+unternehmen\s+gemeinsam"
    r"|gemeinsame\s+unternehmungen"
    r"|WG-Abende?"
    r"|wg[\s\-]events?"
    r"|gemeinsames?\s+essen",
    re.IGNORECASE,
)


def _extract_age_range(text: str) -> tuple[int, int] | None:
    """Extract (min_age, max_age) from text, or None if not found."""
    # Try "zwischen X und Y" or "X und Y Jahre"
    for m in _AGE_RANGE_MULTI.finditer(text):
        groups = [g for g in m.groups() if g is not None]
        if len(groups) >= 2:
            ages = sorted(int(g) for g in groups[:2] if 16 <= int(g) <= 60)
            if len(ages) == 2:
                return (ages[0], ages[1])

    # Try single age in parens (multiple occurrences → infer range)
    parens_ages = [
        int(m.group(1))
        for m in _AGE_IN_PARENS.finditer(text)
        if 16 <= int(m.group(1)) <= 60
    ]
    if len(parens_ages) >= 2:
        return (min(parens_ages), max(parens_ages))
    if len(parens_ages) == 1:
        return (parens_ages[0], parens_ages[0])

    # Try single age from intro sentence
    m = _AGE_SINGLE.search(text)
    if m:
        age = int(m.group(1))
        if 16 <= age <= 60:
            return (age, age)

    return None


def detect(text: str) -> dict:
    """Return social signal dict for a listing description.

    Returns:
        {
            "has_named_roommates": bool,
            "age_range": tuple[int, int] | None,
            "social_vibe": "community" | "neutral",
        }
    """
    if not text:
        return {
            "has_named_roommates": False,
            "age_range": None,
            "social_vibe": "neutral",
        }

    has_named = bool(_NAMED_INTRO.search(text))
    age_range = _extract_age_range(text)
    vibe = "community" if _COMMUNITY_PATTERN.search(text) else "neutral"

    return {
        "has_named_roommates": has_named,
        "age_range": age_range,
        "social_vibe": vibe,
    }
