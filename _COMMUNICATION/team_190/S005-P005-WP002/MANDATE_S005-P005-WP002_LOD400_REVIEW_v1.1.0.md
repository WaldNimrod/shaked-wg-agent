---
id: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.1.0
from: Team 110 (Architecture Agent)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-15
type: LOD400_REVIEW_MANDATE
wp: S005-P005-WP002
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
correction_cycle: 1
supersedes: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.0.0
engine_constraint: "validator engine (openai) != builder engine (cursor-composer)"
---

# LOD400 Review Mandate (Round 2) — S005-P005-WP002: Facebook Manual Listing Parser

## 1. Header

| Field | Value |
|-------|-------|
| Gate | LOD400 Spec Review — Round 2 (re-validation after BLOCK) |
| Work Package | S005-P005-WP002 |
| Label | Facebook manual listing parser — LLM-based Hebrew extraction |
| Track | A |
| Profile | L0 |
| Priority | HIGH |
| Correction Cycle | 1 (re-review after v1.0.0 BLOCK) |

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_S Round 1 | BLOCK | 2026-04-15 | team_190 | F-001..F-005 |
| L-GATE_S Round 2 | PASS | 2026-04-15 | team_190 | All findings closed |
| LOD400 Review v1.0.0 | BLOCK | 2026-04-15 | team_190 | F-LOD400-001..004 |

## 3. Findings Addressed in v1.1.0

| Finding | Severity | Resolution |
|---------|----------|------------|
| F-LOD400-001 | BLOCKING | Added NEW §2.3 Deduplication Implementation — within-batch text-hash dedup + cross-source dedup against existing `listings.json` with algorithm, persistence touchpoints, AC-33..AC-38 |
| F-LOD400-002 | BLOCKING | Rewrote `parse_rental_post()` error handling with explicit 1:1 LOD200 failure mode mapping table (7 modes), mode comments in code, verification cross-reference table |
| F-LOD400-003 | MAJOR | Added `_validate_post()` method with field-by-field schema mapping table (8 fields → validator → default → invalid behavior → AC), matching LOD200 normative schema exactly |
| F-LOD400-004 | MINOR | Fixed metadata placeholders — `approved_by` and `approved_at` updated to reflect draft/review status |

## 4. Scope — What This Re-Review Validates

1. **F-LOD400-001 closure** — dedup subsection is complete with algorithm, code, and AC coverage
2. **F-LOD400-002 closure** — LLM failure matrix 1:1 fidelity with LOD200 7-mode table
3. **F-LOD400-003 closure** — field-by-field schema contract fully specified
4. **F-LOD400-004 closure** — metadata normalized
5. **Test coverage** — new tests UT-23..UT-41, IT-05..IT-06, XE-07..XE-09 cover all new ACs
6. **No regression** — existing sections unchanged; no scope creep

## 5. Validation Criteria (unchanged from v1.0.0)

| VC | Criterion |
|----|-----------|
| VC-01 | LOD400 structural completeness |
| VC-02 | AC measurability |
| VC-03 | LLM failure matrix fidelity |
| VC-04 | Input schema normative contract fidelity |
| VC-05 | Affected components completeness |
| VC-06 | Privacy implementation |
| VC-07 | BaseScraper interface compliance |
| VC-08 | Test fixture specification |
| VC-09 | No Iron Rule violations |
| VC-10 | No scope creep vs LOD200 |

## 6. Files to Review

| File | Purpose |
|------|---------|
| `_aos/work_packages/S005-P005-WP002/LOD400_S005-P005-WP002.md` | **Primary artifact (v1.1.0)** |
| `_aos/work_packages/S005-P005-WP002/LOD200_S005-P005-WP002.md` | Parent LOD200 spec (v1.1.0) |
| `shaked_wg_agent/scrapers/base.py` | BaseScraper interface + ScrapedListing |
| `data/sources.json` | Source registry |
| `data/cities/pardes-hanna-region.json` | City config |
| `data/profiles/pardes-hanna.json` | Profile config |

## 7. Output

**Verdict file:** `_COMMUNICATION/team_190/VERDICT_S005-P005-WP002_LOD400_REVIEW_v1.1.0.md`

**Verdict options:**
- `PASS` — LOD400 approved, proceed to builder
- `PASS_WITH_FINDINGS` — approved with findings for builder to address
- `BLOCK` — material deficiencies; must be revised
