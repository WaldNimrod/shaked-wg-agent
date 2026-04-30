# LOD200 — SWG-PLAT-M1 — Profile schema: age, studies, move_in_optimal
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110)
**WP:** SWG-PLAT-M1
**Type:** LOD200_SPEC

---

## 1. Context

`SearchProfile` currently lacks personal attributes (age, student status, move-in preference).
This prevents the scorer from:
- Awarding an age-match bonus when a listing's roommate age range fits the searcher
- Awarding a student-friendly bonus when a listing targets students
- Awarding an exact move-in date bonus
- Hard-excluding listings that conflict with the searcher's age

Shaked is 18, a chemistry student starting at Universität Basel in September 2026, and
wants to move in on 2026-06-01.

---

## 2. New fields

| Field | Type | Default | Validation |
|---|---|---|---|
| `age` | `int \| None` | `None` | 16–99 when set |
| `occupation_status` | `Literal["student","working","mixed"] \| None` | `None` | one of the three literals |
| `studies_field` | `str \| None` | `None` | free text |
| `studies_institution` | `str \| None` | `None` | free text |
| `studies_start` | `str \| None` | `None` | "YYYY-MM" format |
| `move_in_optimal` | `str \| None` | `None` | "YYYY-MM-DD" format |

All fields are optional with `None` default to ensure backward compatibility with all existing profiles.

---

## 3. Listing fields required by scorer

New optional fields on `ScrapedListing` (in `scrapers/base.py`):

| Field | Type | Default | Meaning |
|---|---|---|---|
| `roommate_age_min` | `int \| None` | `None` | Minimum acceptable roommate age |
| `roommate_age_max` | `int \| None` | `None` | Maximum acceptable roommate age |
| `is_student_oriented` | `bool` | `False` | Listing targets students |

---

## 4. Scorer logic

### 4.1 Weight constants (in config.py)

```
AGE_MATCH_BONUS      = 30
STUDENT_BONUS        = 20
MOVE_IN_OPTIMAL_BONUS = 30
```

### 4.2 Bonuses (additive to existing score)

| Condition | Bonus |
|---|---|
| `profile.age` set AND `listing.roommate_age_min <= profile.age <= listing.roommate_age_max` | +30 |
| `profile.occupation_status == "student"` AND `listing.is_student_oriented` is truthy | +20 |
| `profile.move_in_optimal` set AND `listing.available_from == profile.move_in_optimal` | +30 |

### 4.3 Hard excludes (return score = -1, omitted from digest)

| Condition | Action |
|---|---|
| `listing.roommate_age_min` set AND `profile.age` set AND `profile.age < listing.roommate_age_min` | EXCLUDE |
| `listing.roommate_age_max` set AND `profile.age` set AND `profile.age > listing.roommate_age_max` | EXCLUDE |

Note: Gender restriction hard-exclude deferred to M5.

### 4.4 Graceful skip

When `profile.age is None`, ALL age-related logic (bonus and exclude) is skipped without error.

---

## 5. Migration plan

- All new `SearchProfile` fields have `None` defaults — no changes required in existing profile JSON files
- `dror.json` and any other non-Shaked profiles: explicitly set all new fields to `null` for clarity
- `default.json`: populate with Shaked's actual values
- No DB migration required — listings.json fields are read via `.get()` with safe defaults

---

## 6. Test strategy

### test_config.py additions
- `test_profile_age_field` — default.json → `profile.age == 18`
- `test_profile_age_null` — dror.json → `profile.age is None`
- `test_profile_studies_fields` — default.json → occupation/institution
- `test_profile_move_in_optimal` — default.json → `move_in_optimal == "2026-06-01"`

### test_scorer.py additions
- `test_age_match_bonus` — in-range age → +30
- `test_age_no_match_no_bonus` / `test_hard_exclude_age_below_min` / `test_hard_exclude_age_above_max`
- `test_age_null_skips_check` — None age → no error, no bonus, no exclude
- `test_move_in_optimal_bonus` — exact match → +30
- `test_move_in_optimal_no_match` — mismatch → no bonus
- `test_student_bonus` — student + is_student_oriented → +20
