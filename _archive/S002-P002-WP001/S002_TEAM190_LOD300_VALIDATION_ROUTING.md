# Team 190 Validation Routing — S002 LOD300 Batch
# From: Team 00 (Nimrod)
# To: Team 190 (shaked_val / OpenAI)
# Date: 2026-04-12
# Gate: LOD300 Validation (pre-LOD400)

---

## Activation Prompt for Team 190

You are **Team 190** (shaked_val), the constitutional cross-engine validator for the **shaked-wg-agent** project. Your engine is OpenAI (cross-engine from Team 110's cursor-composer builder).

**Task:** Validate 5 LOD300 system design documents for S002 (Platform Foundation) work packages.

---

## Input Files (read all before validating)

| # | WP ID | LOD300 Path |
|---|-------|-------------|
| 1 | S002-P001-WP001 | `_aos/work_packages/S002-P001-WP001/LOD300_S002-P001-WP001.md` |
| 2 | S002-P001-WP002 | `_aos/work_packages/S002-P001-WP002/LOD300_S002-P001-WP002.md` |
| 3 | S002-P002-WP001 | `_aos/work_packages/S002-P002-WP001/LOD300_S002-P002-WP001.md` |
| 4 | S002-P002-WP002 | `_aos/work_packages/S002-P002-WP002/LOD300_S002-P002-WP002.md` |
| 5 | S002-P003-WP001 | `_aos/work_packages/S002-P003-WP001/LOD300_S002-P003-WP001.md` |

**Also read for context:**
- `_aos/roadmap.yaml` — current project state and WP metadata
- `_aos/context/PROJECT_CONTEXT.md` — project background
- `shaked_wg_agent/config.py` — current config implementation
- `shaked_wg_agent/scrapers/base.py` — current scraper interface
- `shaked_wg_agent/runner.py` — current runner orchestration
- `shaked_wg_agent/persistence.py` — current persistence layer

---

## Validation Checklist (apply to each LOD300)

### Per-Document Checks

| # | Check | Requirement |
|---|-------|-------------|
| 1 | State machine present | Mermaid stateDiagram-v2 or equivalent text diagram with all states and transitions |
| 2 | Business rules | Numbered, unambiguous, no single interpretation possible |
| 3 | Data model | Entities defined with fields, types, and constraints |
| 4 | API surface | Method, path, request schema, response schema, error codes (where applicable) |
| 5 | Sequence diagrams | At least primary happy path + one error flow |
| 6 | Integration contracts | Producer/consumer table with explicit contracts |
| 7 | Acceptance criteria | System behavior level, testable, measurable |
| 8 | Open questions resolved | No unresolved questions; all decisions documented with rationale |
| 9 | No implementation leakage | LOD300 describes behavior, not code (no function names, class hierarchy, SQL schemas) |
| 10 | Frontmatter correct | lod_target, lod_status, track, work_package_id all present and valid |

### Cross-WP Consistency Checks

| # | Check | What to verify |
|---|-------|---------------|
| 11 | Three-entity model consistency | CityDefinition, SearchProfile, and SourceDefinition definitions in WP001 match references in WP002 (city definitions + source registry), WP003 (API profile_id param), WP005 (per-profile notification config) |
| 12 | Error envelope consistency | ErrorResponse format in WP003 (API) matches WP004 (auth 401 response) |
| 13 | Run record consistency | Run record fields in WP003 match the notification_sent extension in WP005 |
| 14 | Dependency chain valid | WP002 depends on WP001, WP004 depends on WP003, WP005 depends on WP001 — no circular dependencies |
| 15 | Track A override | WPs 001, 002, 004, 005 are Track A with LOD300 override — frontmatter should note Team 00 mandate |

---

## Output Format

Write your validation result to:
```
_COMMUNICATION/team_190/S002_LOD300_VALIDATION_RESULT.md
```

**Structure:**

```markdown
# S002 LOD300 Validation Result
**Validator:** Team 190 (shaked_val / OpenAI)
**Date:** [date]
**Overall Verdict:** [PASS / FAIL / PASS WITH FINDINGS]

## Per-WP Verdicts

| WP | Verdict | Findings |
|----|---------|----------|
| S002-P001-WP001 | PASS/FAIL | [summary] |
| S002-P001-WP002 | PASS/FAIL | [summary] |
| S002-P002-WP001 | PASS/FAIL | [summary] |
| S002-P002-WP002 | PASS/FAIL | [summary] |
| S002-P003-WP001 | PASS/FAIL | [summary] |

## Cross-WP Consistency

| Check | Verdict | Notes |
|-------|---------|-------|
| Three-entity model consistency | PASS/FAIL | ... |
| Error envelope consistency | PASS/FAIL | ... |
| Run record consistency | PASS/FAIL | ... |
| Dependency chain | PASS/FAIL | ... |
| Track override noted | PASS/FAIL | ... |

## Detailed Findings

[Per-WP detailed findings with severity: BLOCKING / MAJOR / MINOR / INFO]

## Recommendation

[PROCEED to LOD400 / REVISE specific WPs / HALT]
```

---

## Iron Rules (binding on this validation)

1. **Cross-engine immutable.** You are OpenAI. The builder is cursor-composer. Do NOT self-build.
2. **Read before judging.** Read all 5 LOD300 docs + source code before issuing any verdict.
3. **No forbidden patterns.** Do NOT quote `forbidden_patterns` literals from `project_identity.yaml` in your output. Reference them indirectly (e.g., "hub path variants" instead of the actual strings).
4. **Validate behavior, not code.** LOD300 is a system design document. Flag implementation leakage but do not penalize absence of code details.
5. **Be specific.** Findings must cite the exact WP, section number, and what is missing/wrong.

---

*Routing prepared by Team 00 (Nimrod) via Team 110 | shaked-wg-agent | 2026-04-12*
