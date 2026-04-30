# LOD400 — SWG-PLAT-M5 — Negative-signal autofilter
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110)
**WP:** SWG-PLAT-M5
**Type:** LOD400_SPEC

---

## 1. Module: `shaked_wg_agent/extractors/negative_signals.py`

### Public API

```python
def detect_negative_signals(text: str) -> dict[str, bool]:
    """
    Detect negative signals in listing text (summary + full_description).
    Returns dict of signal name → bool (True = signal present).
    Keys: women_only, men_only, wochenaufenthalter, business_only,
          zwischenmiete_short, religion_preference.
    """
```

### Pattern catalogue

#### `women_only`
Search `text.lower()` for any of:
- `"nur frauen"`, `"frauen-wg"`, `"frauenwg"`, `"women only"`, `"female only"`,
  `"nur damen"`, `"damen-wg"`, `"solo donne"`, `"pour femmes"`

#### `men_only`
- `"nur männer"`, `"männer-wg"`, `"men only"`, `"male only"`, `"nur herren"`,
  `"herren-wg"`, `"solo uomini"`

#### `wochenaufenthalter`
- `"wochenaufenthalter"`, `"wochenaufenthalerin"`, `"pendler"`,
  `"nur wochenaufenthalter"`

#### `business_only`
- `"geschäftsleute"`, `"business only"`, `"berufstätige only"`,
  `"nur berufstätige"`

#### `zwischenmiete_short`
Step 1 — raw trigger: any of `"zwischenmiete"`, `"untermiete"`, `"temporary stay"`,
`"nur befristet"`, `"interim rent"`.

Step 2 — long-duration override: if the text also matches
```
\b(6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24)\s*monate?\b
|\b[1-9]\d*\s*jahre?\b
|\b(ein|zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|elf|zwölf)\s*jahre?\b
```
(case-insensitive), set `zwischenmiete_short = False`.
Otherwise `zwischenmiete_short = True` when raw trigger fires.

#### `religion_preference`
- `"christian preferably"`, `"christlich bevorzugt"`, `"religiös"`,
  `"catholisch bevorzugt"`

---

## 2. Integration in `shaked_wg_agent/scorer.py`

### Import

```python
from shaked_wg_agent.extractors.negative_signals import detect_negative_signals
```

### Insertion point in `score_listing()`

After the `_age_hard_exclude` early return, before `_listing_transit_lines`:

```python
if _age_hard_exclude(listing, profile):
    return -1

# M5: Negative-signal autofilter
_neg_text = listing.get("full_description") or listing.get("summary") or ""
signals = detect_negative_signals(_neg_text)

if signals["men_only"]:
    return -1
if signals["wochenaufenthalter"] or signals["business_only"]:
    return -1
if signals["zwischenmiete_short"]:
    return -1

# ... existing scoring ...
# Advisory penalty at the end, before min(100, total):
if signals["religion_preference"]:
    total -= 10
```

### Reasoning for signal placement
- Hard excludes placed before scoring computation (early return = no wasted computation).
- `men_only` checked first (most specific to profile).
- `women_only` explicitly NOT excluded (Shaked is female — keep those listings).
- Religion penalty applied after summing all positive scores.

---

## 3. Tests: `tests/test_negative_signals.py`

### Signal detection (unit)
| Test | Input | Expected |
|------|-------|----------|
| `test_women_only_detected` | `"nur Frauen WG gesucht"` | `women_only=True` |
| `test_men_only_detected` | `"nur Männer, kein Platz für Frauen"` | `men_only=True` |
| `test_wochenaufenthalter_detected` | `"für Wochenaufenthalter geeignet"` | `wochenaufenthalter=True` |
| `test_zwischenmiete_short_detected` | `"Zwischenmiete 3 Monate"` | `zwischenmiete_short=True` |
| `test_zwischenmiete_long_not_flagged` | `"Zwischenmiete 12 Monate"` | `zwischenmiete_short=False` |
| `test_religion_preference_detected` | `"Christian preferably"` | `religion_preference=True` |
| `test_clean_listing_no_signals` | `"Schöne WG, vegan friendly"` | all False |
| `test_case_insensitive` | `"WOCHENAUFENTHALTER"` | `wochenaufenthalter=True` |
| `test_business_only_detected` | `"nur Geschäftsleute"` | `business_only=True` |
| `test_french_pattern` | `"pour femmes seulement"` | `women_only=True` |

### Recall (5 synthetic TRUE positives)
Texts covering: Frauen-WG, Männer-WG, Wochenaufenthalter/Pendler,
short Untermiete, Geschäftsleute. Each must fire exactly the expected signal.

### Precision (5 clean listings)
Texts covering: vegan student WG, English-language listing, tram-adjacent listing,
"6 Monaten" in non-zwischenmiete context, multicultural/religion-neutral listing.
All must produce zero false positives.

### Scorer integration
| Test | Expected |
|------|----------|
| `test_scorer_men_only_returns_minus_one` | `score == -1` |
| `test_scorer_wochenaufenthalter_returns_minus_one` | `score == -1` |
| `test_scorer_zwischenmiete_short_returns_minus_one` | `score == -1` |
| `test_scorer_business_only_returns_minus_one` | `score == -1` |
| `test_scorer_women_only_not_excluded` | `score != -1 and score >= 0` |
| `test_scorer_religion_penalty_applied` | `religious_score < base_score` |
| `test_scorer_fallback_to_summary_when_no_full_description` | `score == -1` |
| `test_scorer_uses_full_description_over_summary` | `score == -1` |
| `test_scorer_clean_listing_not_excluded` | `score > 0` |

---

## 4. Ruff compliance

Files touched: `shaked_wg_agent/extractors/negative_signals.py`, `shaked_wg_agent/scorer.py`.
Both must pass `ruff check` with zero errors before delivery.
