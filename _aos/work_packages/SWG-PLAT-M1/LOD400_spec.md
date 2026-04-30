# LOD400 — SWG-PLAT-M1 — Profile schema: age, studies, move_in_optimal
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110)
**WP:** SWG-PLAT-M1
**Type:** LOD400_SPEC

---

## 1. config.py — SearchProfile additions

### 1.1 New imports required

```python
from typing import Literal
```

(already imported via `Any` — add `Literal` to the `typing` import)

### 1.2 New dataclass fields on SearchProfile

```python
# M1: personal attributes for age/student/move-in scoring
age: int | None = None
occupation_status: Literal["student", "working", "mixed"] | None = None
studies_field: str | None = None
studies_institution: str | None = None
studies_start: str | None = None   # "YYYY-MM"
move_in_optimal: str | None = None  # "YYYY-MM-DD"
```

### 1.3 New weight constants (module level, near other constants)

```python
# M1 scoring weights
AGE_MATCH_BONUS: int = 30
STUDENT_BONUS: int = 20
MOVE_IN_OPTIMAL_BONUS: int = 30
```

### 1.4 _load_profile() additions

In the `SearchProfile(...)` constructor call, add:

```python
age=raw.get("age"),
occupation_status=raw.get("occupation_status"),
studies_field=raw.get("studies_field"),
studies_institution=raw.get("studies_institution"),
studies_start=raw.get("studies_start"),
move_in_optimal=raw.get("move_in_optimal"),
```

---

## 2. scrapers/base.py — ScrapedListing additions

Add to the `ScrapedListing` dataclass (after `posted_date`):

```python
# M1: age-range and student-orientation fields (set by scrapers that expose them)
roommate_age_min: int | None = None
roommate_age_max: int | None = None
is_student_oriented: bool = False
```

Add to `to_dict()` return dict:

```python
"roommate_age_min": self.roommate_age_min,
"roommate_age_max": self.roommate_age_max,
"is_student_oriented": self.is_student_oriented,
```

---

## 3. scorer.py — new helper and integration

### 3.1 Import weight constants

```python
from shaked_wg_agent.config import (
    AGE_MATCH_BONUS,
    CityDefinition,
    MOVE_IN_OPTIMAL_BONUS,
    SearchProfile,
    STUDENT_BONUS,
)
```

### 3.2 New helper function

```python
def _profile_bonuses(listing: dict[str, Any], profile: SearchProfile) -> int:
    """Return M1 additive bonuses: age match, student orientation, move-in optimal."""
    bonus = 0

    age_min = listing.get("roommate_age_min")
    age_max = listing.get("roommate_age_max")
    if (
        profile.age is not None
        and age_min is not None
        and age_max is not None
        and age_min <= profile.age <= age_max
    ):
        bonus += AGE_MATCH_BONUS

    if profile.occupation_status == "student" and listing.get("is_student_oriented"):
        bonus += STUDENT_BONUS

    if (
        profile.move_in_optimal is not None
        and listing.get("available_from") == profile.move_in_optimal
    ):
        bonus += MOVE_IN_OPTIMAL_BONUS

    return bonus


def _age_hard_exclude(listing: dict[str, Any], profile: SearchProfile) -> bool:
    """Return True if listing's age range excludes the profile's age (hard exclude)."""
    if profile.age is None:
        return False
    age_min = listing.get("roommate_age_min")
    if age_min is not None and profile.age < age_min:
        return True
    age_max = listing.get("roommate_age_max")
    if age_max is not None and profile.age > age_max:
        return True
    # TODO M5: gender_restriction hard-exclude
    return False
```

### 3.3 Integration in score_listing()

After the budget and settlement gates, before computing `total`:

```python
if _age_hard_exclude(listing, profile):
    return -1
```

Add `_profile_bonuses(listing, profile)` to the `total` sum.

---

## 4. Profile JSON changes

### 4.1 data/profiles/default.json — add Shaked's values

```json
"age": 18,
"occupation_status": "student",
"studies_field": "chemistry (planned)",
"studies_institution": "Universität Basel",
"studies_start": "2026-09",
"move_in_optimal": "2026-06-01"
```

### 4.2 data/profiles/dror.json — add null placeholders

```json
"age": null,
"occupation_status": null,
"studies_field": null,
"studies_institution": null,
"studies_start": null,
"move_in_optimal": null
```

---

## 5. Tests

### 5.1 tests/test_config.py — new test names and assertions

| Test name | Assertion |
|---|---|
| `test_profile_age_field` | Load real `default.json`; `profile.age == 18` |
| `test_profile_age_null` | Load real `dror.json`; `profile.age is None` |
| `test_profile_studies_fields` | Load real `default.json`; `occupation_status == "student"`, `studies_institution == "Universität Basel"` |
| `test_profile_move_in_optimal` | Load real `default.json`; `move_in_optimal == "2026-06-01"` |

These tests load real profile files — no tmp_path fixture needed.

### 5.2 tests/test_scorer.py — new test names and assertions

| Test name | Assertion |
|---|---|
| `test_age_match_bonus` | age=18, min=16, max=25 → score includes +30 vs same without age range |
| `test_age_no_match_no_bonus` | age=30, min=16, max=25 → score == -1 (hard exclude) |
| `test_age_null_skips_check` | age=None, min=16, max=25 → no exception, no exclude |
| `test_move_in_optimal_bonus` | available_from == move_in_optimal → +30 |
| `test_move_in_optimal_no_match` | available_from != move_in_optimal → no bonus |
| `test_student_bonus` | occupation_status="student" + is_student_oriented=True → +20 |
| `test_hard_exclude_age_below_min` | age=14, min=16 → score == -1 |
| `test_hard_exclude_age_above_max` | age=30, max=25 → score == -1 |
