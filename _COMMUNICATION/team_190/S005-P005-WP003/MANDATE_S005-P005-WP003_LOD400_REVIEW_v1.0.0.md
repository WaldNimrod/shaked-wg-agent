---
id: MANDATE_S005-P005-WP003_LOD400_REVIEW_v1.0.0
from: Team 110 (Architecture Agent)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-15
type: LOD400_REVIEW_MANDATE
wp: S005-P005-WP003
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
engine_constraint: "validator engine (openai) != builder engine (cursor-composer)"
---

# LOD400 Review Mandate — S005-P005-WP003: Facebook Email Notification Parser

## 1. Header

| Field | Value |
|-------|-------|
| Gate | LOD400 Spec Review (pre-build validation) |
| Work Package | S005-P005-WP003 |
| Label | Facebook email notification parser — passive acquisition |
| Track | A |
| Profile | L0 |
| Priority | MEDIUM |
| Dependency | S005-P005-WP002 (reuses LLM parser) |

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_S Round 1 | PASS_WITH_FINDINGS | 2026-04-15 | team_190 | F01-F03 non-blocking |

## 3. Scope — What This Review Validates

1. **LOD400 spec completeness** — all sections present
2. **AC measurability** — every criterion testable
3. **IMAP credential contract** — env-var only policy enforced at code level (LOD200 F01 resolution)
4. **Dedup pipeline** — 4-layer ordered dedup from LOD200 F02 faithfully implemented
5. **Email HTML parsing** — 3 notification formats handled
6. **WP002 dependency** — LLM parser reuse correctly specified
7. **Spec is builder-executable without clarification**

## 4. Validation Criteria

| VC | Criterion | What to Check |
|----|-----------|---------------|
| VC-01 | LOD400 structural completeness | All 8 sections present |
| VC-02 | AC measurability | Every AC testable |
| VC-03 | IMAP credential security | Env-var only, no inline secrets, verified by grep |
| VC-04 | Dedup pipeline fidelity | 4-layer order (message-ID → URL → hash → fuzzy) in code |
| VC-05 | Email parsing coverage | Single, digest, popular notification types handled |
| VC-06 | WP002 dependency contract | `parse_rental_post()` and `check_llm_config()` reused correctly |
| VC-07 | BaseScraper compliance | Constructor + fetch_listings() signature match |
| VC-08 | Test fixtures | .eml fixtures for all 3 email types specified |
| VC-09 | No Iron Rule violations | Cross-engine, independence |
| VC-10 | LOD200 findings addressed | F01 (creds), F02 (dedup), F03 (SC phrasing) all resolved |

## 5. Files to Review

| File | Purpose |
|------|---------|
| `_aos/work_packages/S005-P005-WP003/LOD400_S005-P005-WP003.md` | **Primary artifact** |
| `_aos/work_packages/S005-P005-WP003/LOD200_S005-P005-WP003.md` | Parent LOD200 spec (v1.1.0) |
| `_aos/work_packages/S005-P005-WP002/LOD400_S005-P005-WP002.md` | WP002 LOD400 (dependency) |
| `shaked_wg_agent/scrapers/base.py` | BaseScraper interface |
| `data/sources.json` | Source registry |
| `data/cities/pardes-hanna-region.json` | City config |

## 6. Output

**Verdict file:** `_COMMUNICATION/team_190/VERDICT_S005-P005-WP003_LOD400_REVIEW_v1.0.0.md`

**Verdict options:**
- `PASS` — LOD400 approved, proceed to builder
- `PASS_WITH_FINDINGS` — approved with findings for builder to address
- `BLOCK` — material deficiencies; must be revised
