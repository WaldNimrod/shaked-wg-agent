# LOD200 — SWG-PLAT-M5 — Negative-signal autofilter
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110)
**WP:** SWG-PLAT-M5
**Type:** LOD200_SPEC

---

## 1. Problem Statement

The live search session manually filters listings with signals like "nur Männer",
"Wochenaufenthalter", "Zwischenmiete" each round. This is not scalable and relies on
human review of listing body text. With `full_description` now available (added by M2),
automated filtering is feasible.

Shaked's profile: female, age 18, student, seeking **permanent** accommodation.

---

## 2. Scope

**In scope:**
- Hard-exclude signals: gender restriction conflicting with profile, Wochenaufenthalter,
  business-only, short Zwischenmiete (<6 months).
- Advisory signals: religion preference (score penalty only, not hard exclude).
- Integration with `scorer.py` `score_listing()`.
- Unit tests with ≥90% recall and ≥95% precision on hand-labelled set.

**Out of scope:**
- Gender inference from profile data (no `profile.gender` field — future concern).
- Machine-learning-based classification.
- Scraper changes.

---

## 3. Architecture

```
score_listing()  ← scorer.py
    │
    ├─ [existing] budget gate → 0
    ├─ [existing] settlement gate → 0
    ├─ [existing] age hard-exclude → -1
    │
    ├─ [M5 NEW] detect_negative_signals(full_description or summary)
    │       │
    │       └─ returns dict[signal_name → bool]
    │
    ├─ [M5] men_only=True → return -1
    ├─ [M5] wochenaufenthalter=True or business_only=True → return -1
    ├─ [M5] zwischenmiete_short=True → return -1
    │
    └─ [M5] religion_preference=True → total -= 10 (advisory penalty)
```

### Module layout

```
shaked_wg_agent/
  extractors/
    __init__.py          (empty)
    negative_signals.py  (new — M5)
  scorer.py              (modified — M5 integration)
tests/
  test_negative_signals.py  (new — M5)
```

---

## 4. Signal taxonomy

| Signal               | Type         | Action              |
|----------------------|--------------|---------------------|
| `men_only`           | Hard exclude | score = -1          |
| `women_only`         | Keep (Shaked is female) | no action  |
| `wochenaufenthalter` | Hard exclude | score = -1          |
| `business_only`      | Hard exclude | score = -1          |
| `zwischenmiete_short`| Hard exclude | score = -1          |
| `religion_preference`| Advisory     | score -= 10         |

---

## 5. Graceful degradation

- If `full_description` is `None` or empty, fall back to `summary`.
- If both are empty, `detect_negative_signals("")` returns all-False (no false positives).
- No `profile.gender` field is required — `men_only` is always excluded based on Shaked being female.

---

## 6. Acceptance criteria

1. Recall ≥90% on hand-labelled synthetic set (5 positive cases per signal category).
2. Precision ≥95% (5 clean listings produce zero false positives).
3. scorer returns -1 for all hard-exclude signals.
4. `python3 -m pytest tests/ -q` — all tests pass.
5. `ruff check` — clean on touched files.
