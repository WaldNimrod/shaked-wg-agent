# VERDICT — SWG-PLAT-M1 — team_190 — v1.0.0
**Date:** 2026-04-30
**Author:** team_190
**WP:** SWG-PLAT-M1
**Gate:** L-GATE_VALIDATE R1 EXTERNAL
**Overall:** PASS_WITH_FINDINGS
**Engine:** GPT-5.2 (Cursor Agent)

## Findings
| ID | Severity | Location | Description | Blocking? |
|----|----------|----------|-------------|-----------|
| M1-F01 | MINOR | [shaked_wg_agent/scorer.py](shaked_wg_agent/scorer.py) `_age_hard_exclude` | Docstring still says `TODO M5: gender_restriction`; gender-based hard excludes for male-only listings are implemented in M5 via `detect_negative_signals` / `men_only`. Comment is misleading for maintainers. | No |

## Acceptance Criteria Coverage
| Criterion (LOD400 §1–5) | Status |
|-------------------------|--------|
| `SearchProfile`: `age`, `occupation_status`, `studies_*`, `move_in_optimal` with `Literal` typing | VERIFIED — [config.py](shaked_wg_agent/config.py) |
| Module weights `AGE_MATCH_BONUS`, `STUDENT_BONUS`, `MOVE_IN_OPTIMAL_BONUS` | VERIFIED — config.py |
| `_load_profile` passes new fields from JSON | VERIFIED — config.py |
| `ScrapedListing`: `roommate_age_min/max`, `is_student_oriented` + `to_dict()` | VERIFIED — [base.py](shaked_wg_agent/scrapers/base.py) |
| `_profile_bonuses`, `_age_hard_exclude`, integration in `score_listing` (exclude before total) | VERIFIED — [scorer.py](shaked_wg_agent/scorer.py) |
| `data/profiles/default.json` Shaked values; `dror.json` nulls | VERIFIED |
| Tests: `test_profile_*`, `test_age_*`, `test_move_in_*`, `test_student_*`, hard-exclude age tests | VERIFIED — [test_config.py](tests/test_config.py), [test_scorer.py](tests/test_scorer.py) |

## Verdict Rationale
All LOD400-deliverable acceptance paths are implemented and covered by tests; automated gates passed. PASS_WITH_FINDINGS solely for the stale M5 TODO comment in `_age_hard_exclude`, which does not affect runtime behavior.
