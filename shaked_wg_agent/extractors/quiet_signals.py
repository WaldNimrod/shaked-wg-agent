"""Quiet/calm household signal extractor.

Detects listings that indicate a quiet or calm living environment.
"""
from __future__ import annotations

import re

_QUIET_PATTERN = re.compile(
    r"ruhig|quiet|calm|leise|schallisolier|sound[\s\-]?insul"
    r"|peaceful|ruhige\s+wg|ruhige\s+mitbewohner",
    re.IGNORECASE,
)


def detect(text: str) -> bool:
    """Return True if text indicates a quiet/calm household."""
    if not text:
        return False
    return bool(_QUIET_PATTERN.search(text))


def classify(text: str) -> dict:
    """Return classification dict for quiet signals.

    Returns:
        {
            "is_quiet_friendly": bool,
            "matched_keywords": list[str],
        }
    """
    if not text:
        return {"is_quiet_friendly": False, "matched_keywords": []}

    matches = list(_QUIET_PATTERN.finditer(text))
    if not matches:
        return {"is_quiet_friendly": False, "matched_keywords": []}

    keywords = list({m.group(0).lower() for m in matches})
    return {"is_quiet_friendly": True, "matched_keywords": keywords}
