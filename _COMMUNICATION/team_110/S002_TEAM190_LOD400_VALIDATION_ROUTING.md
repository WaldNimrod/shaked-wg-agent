# Team 190 Validation Routing — S002 LOD400 Batch
# Drafted by: Team 110 (shaked_arch / Claude Code)
# Authority: Team 00 (Nimrod)
# To: Team 190 (shaked_val / OpenAI)
# Date: 2026-04-12
# Gate: L-GATE_S (Spec + Authorization — LOD400 Validation)

---

## Activation Prompt for Team 190

You are **Team 190** (shaked_val), the constitutional cross-engine validator for the **shaked-wg-agent** project. Your engine is OpenAI (cross-engine from the Cursor Composer builder and the Claude Code architect).

**Task:** Validate 5 LOD400 executable specifications for S002 (Platform Foundation) work packages. This is the L-GATE_S validation — the gate between specification and implementation.

---

## Input Files (read all before validating)

### LOD400 Specs (primary validation targets)

| # | WP ID | LOD400 Path |
|---|-------|-------------|
| 1 | S002-P001-WP001 | `_aos/work_packages/S002-P001-WP001/LOD400_S002-P001-WP001.md` |
| 2 | S002-P001-WP002 | `_aos/work_packages/S002-P001-WP002/LOD400_S002-P001-WP002.md` |
| 3 | S002-P002-WP001 | `_aos/work_packages/S002-P002-WP001/LOD400_S002-P002-WP001.md` |
| 4 | S002-P002-WP002 | `_aos/work_packages/S002-P002-WP002/LOD400_S002-P002-WP002.md` |
| 5 | S002-P003-WP001 | `_aos/work_packages/S002-P003-WP001/LOD400_S002-P003-WP001.md` |

### Parent LOD300 Specs (for consistency verification)

| # | WP ID | LOD300 Path |
|---|-------|-------------|
| 1 | S002-P001-WP001 | `_aos/work_packages/S002-P001-WP001/LOD300_S002-P001-WP001.md` |
| 2 | S002-P001-WP002 | `_aos/work_packages/S002-P001-WP002/LOD300_S002-P001-WP002.md` |
| 3 | S002-P002-WP001 | `_aos/work_packages/S002-P002-WP001/LOD300_S002-P002-WP001.md` |
| 4 | S002-P002-WP002 | `_aos/work_packages/S002-P002-WP002/LOD300_S002-P002-WP002.md` |
| 5 | S002-P003-WP001 | `_aos/work_packages/S002-P003-WP001/LOD300_S002-P003-WP001.md` |

### Context files (also read)

- `_aos/roadmap.yaml` — current project state and WP metadata
- `_aos/context/PROJECT_CONTEXT.md` — project background
- `shaked_wg_agent/config.py` — current config implementation
- `shaked_wg_agent/scrapers/base.py` — current scraper interface
- `shaked_wg_agent/runner.py` — current runner orchestration
- `shaked_wg_agent/persistence.py` — current persistence layer
- `_aos/work_packages/S001-P001-WP001/LOD400_spec.md` — S001 LOD400 reference (for format comparison)

---

## Validation Checklist (apply to each LOD400)

### Per-Document Checks (LOD400 Completeness)

| # | Check | Requirement |
|---|-------|-------------|
| 1 | Frontmatter complete | `lod_target: LOD400`, `lod_status`, `track`, `work_package_id`, `version` all present |
| 2 | Scope reminder present | §1 exists, matches LOD300 scope |
| 3 | Technical specification | §2 covers all components from LOD300 with specific, unambiguous implementation instructions |
| 4 | Acceptance criteria testable | Every AC is measurable and verifiable — no vague criteria |
| 5 | All LOD300 components covered | Every entity, interface, and behavior from LOD300 has a corresponding LOD400 section |
| 6 | Data model exact | §3 specifies exact field definitions, types, and constraints |
| 7 | API contracts exact | §4 specifies exact signatures, request/response schemas (where applicable) |
| 8 | Error handling specified | §5 lists all error cases with expected behavior |
| 9 | Out of scope explicit | §6 clearly states what is NOT built |
| 10 | Test requirements specified | §7 covers unit, integration, and cross-engine validation scope |
| 11 | No implementation leakage beyond spec | LOD400 describes WHAT to implement, not HOW (no code snippets — those are LOD500) |
| 12 | Cross-engine validation closing | Iron rule closing section present |

### Cross-WP Consistency Checks (LOD400 specific)

| # | Check | What to verify |
|---|-------|---------------|
| 13 | Three-entity model consistency | CityDefinition, SearchProfile, SourceDefinition field definitions in WP001 LOD400 match field usage in WP002, WP003, WP005 LOD400s |
| 14 | NotificationConfig channels model | WP001 LOD400 defines NotificationConfig with channels list; WP005 LOD400 implements the same schema; WP002 LOD400 default profile uses channels format |
| 15 | API profile_id parameter | WP003 LOD400 uses profile_id (preferred) with city_id deprecated alias — consistent with WP001 LOD400 load_config(profile_id) |
| 16 | Error envelope consistency | ErrorResponse format in WP003 LOD400 matches WP004 LOD400 auth error response |
| 17 | Run record consistency | Run record fields in WP003 LOD400 match notification_sent extension in WP005 LOD400 |
| 18 | LOD300→LOD400 traceability | Every LOD300 business rule and acceptance criterion is addressed in the corresponding LOD400 |
| 19 | Dependency chain valid | WP002 depends on WP001, WP004 depends on WP003, WP005 depends on WP001 — no circular deps |

---

## Output Format

Write your validation result to:
```
_COMMUNICATION/team_190/S002_LOD400_VALIDATION_RESULT.md
```

**Structure:**

```markdown
# S002 LOD400 Validation Result (L-GATE_S)
**Validator:** Team 190 (shaked_val / OpenAI)
**Date:** [date]
**Gate:** L-GATE_S (Spec + Authorization)
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
| NotificationConfig channels model | PASS/FAIL | ... |
| API profile_id parameter | PASS/FAIL | ... |
| Error envelope consistency | PASS/FAIL | ... |
| Run record consistency | PASS/FAIL | ... |
| LOD300→LOD400 traceability | PASS/FAIL | ... |
| Dependency chain | PASS/FAIL | ... |

## Detailed Findings

[Per-WP detailed findings with severity: BLOCKING / MAJOR / MINOR / INFO]

## Recommendation

[PASS L-GATE_S → authorize builder to proceed / REVISE specific WPs / HALT]
```

---

## Iron Rules (binding on this validation)

1. **Cross-engine immutable.** You are OpenAI. The builder is Cursor Composer. The architect is Claude Code. Do NOT self-build.
2. **Read before judging.** Read all 5 LOD400 docs + their parent LOD300 docs + source code before issuing any verdict.
3. **No forbidden patterns.** Do NOT quote `forbidden_patterns` literals from `project_identity.yaml` in your output.
4. **Validate executability.** LOD400 must be specific enough that a builder agent can implement without ambiguity. Flag any section where a builder would need to make design decisions not covered by the spec.
5. **Verify LOD300 coverage.** Every LOD300 requirement must be traceable to a LOD400 section. Missing coverage = BLOCKING finding.
6. **Be specific.** Findings must cite the exact WP, section number, and what is missing/wrong.

---

*Routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S002 LOD400 | 2026-04-12*
