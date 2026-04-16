---
id: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.0.0
from: Team 110 (Architecture Agent)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-15
type: LOD400_REVIEW_MANDATE
wp: S005-P005-WP002
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
engine_constraint: "validator engine (openai) != builder engine (cursor-composer)"
---

# LOD400 Review Mandate — S005-P005-WP002: Facebook Manual Listing Parser

## 1. Header

| Field | Value |
|-------|-------|
| Gate | LOD400 Spec Review (pre-build validation) |
| Work Package | S005-P005-WP002 |
| Label | Facebook manual listing parser — LLM-based Hebrew extraction |
| Track | A |
| Profile | L0 |
| Priority | HIGH |

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_S Round 1 | BLOCK | 2026-04-15 | team_190 | F-001..F-005 |
| L-GATE_S Round 2 | PASS | 2026-04-15 | team_190 | All findings closed |

## 3. Scope — What This Review Validates

1. **LOD400 spec completeness** — all sections, including code-level implementation detail
2. **AC measurability** — every acceptance criterion has a testable verification method
3. **LLM integration design** — failure matrix from LOD200 faithfully translated to implementation spec
4. **Input schema contract** — normative schema from LOD200 reflected in code spec
5. **Affected components** — city allowlist, profile, sources.json all covered
6. **Privacy safeguards** — PII stripping specified at code level
7. **Spec is builder-executable without clarification**

## 4. Validation Criteria

| VC | Criterion | What to Check |
|----|-----------|---------------|
| VC-01 | LOD400 structural completeness | All 8 required sections present |
| VC-02 | AC measurability | Every AC has grep/test/assertion verification |
| VC-03 | LLM failure matrix fidelity | LOD200 failure behavior matrix (7 modes) covered in LOD400 error handling + code |
| VC-04 | Input schema normative contract | LOD200 schema table reflected in code validation logic |
| VC-05 | Affected components completeness | city JSON, profile JSON, sources.json, new files all specified |
| VC-06 | Privacy implementation | PII stripping code + tests specified |
| VC-07 | BaseScraper interface compliance | Constructor signature, fetch_listings() return type match |
| VC-08 | Test fixture specification | Hebrew test corpus requirements defined |
| VC-09 | No Iron Rule violations | Cross-engine, independence, governance |
| VC-10 | No scope creep vs LOD200 | No new features or components beyond approved scope |

## 5. Files to Review

| File | Purpose |
|------|---------|
| `_aos/work_packages/S005-P005-WP002/LOD400_S005-P005-WP002.md` | **Primary artifact** |
| `_aos/work_packages/S005-P005-WP002/LOD200_S005-P005-WP002.md` | Parent LOD200 spec (v1.1.0) |
| `shaked_wg_agent/scrapers/base.py` | BaseScraper interface + ScrapedListing |
| `shaked_wg_agent/scrapers/homeless.py` | Reference scraper pattern |
| `data/sources.json` | Source registry |
| `data/cities/pardes-hanna-region.json` | City config |
| `data/profiles/pardes-hanna.json` | Profile config |

## 6. Output

**Verdict file:** `_COMMUNICATION/team_190/VERDICT_S005-P005-WP002_LOD400_REVIEW_v1.0.0.md`

**Verdict options:**
- `PASS` — LOD400 approved, proceed to builder
- `PASS_WITH_FINDINGS` — approved with findings for builder to address
- `BLOCK` — material deficiencies; must be revised
