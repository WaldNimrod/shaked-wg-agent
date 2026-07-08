---
id: VERDICT_SWG-PLAT-M1_L-GATE_INTERNAL_R1_v1.0.0
type: INTERNAL_VALIDATOR_VERDICT
wp_id: SWG-PLAT-M1
validator: haiku_sub_agent
round: R1_INTERNAL
date: 2026-04-30
gates: [L-GATE_SPEC_R1_INTERNAL, L-GATE_BUILD_R1_INTERNAL, L-GATE_VALIDATE_R1_INTERNAL]
---

# DETERMINISTIC VC CHECKLIST RESULTS — SWG-PLAT-M1

## GATE 1: L-GATE_SPEC_R1_INTERNAL

[PASS] Check 1: `_aos/work_packages/SWG-PLAT-M1/LOD200_spec.md` exists and has 106 lines (>20 ✓)

[PASS] Check 2: `_aos/work_packages/SWG-PLAT-M1/LOD400_spec.md` exists and has 196 lines (>20 ✓)

[PASS] Check 3: LOD200 mentions all 6 new fields: age, occupation_status, studies_field, studies_institution, studies_start, move_in_optimal (grep count: 28 field mentions across table and text)

[PASS] Check 4: LOD200 documents the 3 weight constants: AGE_MATCH_BONUS, STUDENT_BONUS, MOVE_IN_OPTIMAL_BONUS (all three present in section 4.1)

[PASS] Check 5: LOD200 documents both hard-exclude conditions (age < min, age > max) in section 4.3 "Hard excludes"

---

## GATE 2: L-GATE_BUILD_R1_INTERNAL

[PASS] Check 6: `grep "age.*int.*None\|age: int"` — Field present at config.py:116: `age: int | None = None`

[PASS] Check 7: `grep "occupation_status"` — Field present at config.py:117

[PASS] Check 8: `grep "move_in_optimal"` — Field present at config.py:121

[PASS] Check 9: `grep "AGE_MATCH_BONUS\|STUDENT_BONUS\|MOVE_IN_OPTIMAL_BONUS"` — All constants present in config.py:18–20

[PASS] Check 10: `grep "roommate_age_min\|roommate_age_max\|is_student_oriented"` — Listing fields present in base.py:51–53 and to_dict() at lines 79–81

[PASS] Check 11: `grep "_profile_bonuses\|_age_hard_exclude\|AGE_MATCH_BONUS"` — Scorer logic present: _profile_bonuses() at line 157, _age_hard_exclude() at line 183, integration at line 226–227, line 237

[PASS] Check 12: default.json profile load: `python3 -c "import json; p=json.load(open('data/profiles/default.json')); print(p['age'], p['occupation_status'])"` → Output: `18 student` ✓

[PASS] Check 13: dror.json profile load: `python3 -c "import json; p=json.load(open('data/profiles/dror.json')); print(p.get('age'))"` → Output: `None` ✓

[PASS] Check 14: `pytest tests/test_config.py -k "age or studies or move_in" -v` — 7 passed (test_profile_age_field, test_profile_age_null, test_profile_studies_fields, test_profile_move_in_optimal all PASSED)

[PASS] Check 15: `pytest tests/test_scorer.py -k "age or student or move_in or hard_exclude" -v` — 8 passed (test_age_match_bonus, test_age_no_match_no_bonus, test_age_null_skips_check, test_move_in_optimal_bonus, test_move_in_optimal_no_match, test_student_bonus, test_hard_exclude_age_below_min, test_hard_exclude_age_above_max all PASSED)

[PASS] Check 16: `pytest tests/ -q` — Full suite: 156 passed (0 failed)

---

## GATE 3: L-GATE_VALIDATE_R1_INTERNAL

[PASS] Check 17: `grep -n "TODO.*M5\|gender"` — Gender hard-exclude deferred to M5 present at scorer.py:186 `TODO M5: gender_restriction hard-exclude`

[PASS] Check 18: Age scoring graceful when `profile.age is None` — score_listing() with dror profile (age=None) and listing with roommate_age_min/max=20/30 returns score=0 (valid, no exception, no -1 hard exclude)

[PASS] Check 19: `ruff check` — All checks passed on config.py and scorer.py (no errors reported)

[PASS] Check 20: `validate_aos.sh .` — RESULT: 30 PASS / 9 SKIP / 0 FAIL

---

## OVERALL: PASS

All 20 checks PASS. WP SWG-PLAT-M1 meets all specification and build requirements for L-GATE_INTERNAL_R1.

### Summary of Validation

| Dimension | Status |
|-----------|--------|
| Spec completeness (LOD200/400) | ✓ PASS |
| Config field implementation | ✓ PASS |
| Listing field integration | ✓ PASS |
| Scorer logic (bonuses + excludes) | ✓ PASS |
| Profile JSON data | ✓ PASS |
| Test coverage | ✓ PASS (15/15 tests pass) |
| Full test suite | ✓ PASS (156/156) |
| Linting / AOS validation | ✓ PASS |
| Graceful null handling | ✓ PASS |
| Gender deferral (M5) | ✓ DOCUMENTED |

---

**Validated by:** haiku_sub_agent  
**Date:** 2026-04-30  
**Round:** R1_INTERNAL
