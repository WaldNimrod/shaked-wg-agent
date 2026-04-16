# Team 190 Validation Routing — S005-P004 LOD200 Batch (WP001 + WP002 + WP003)
**Drafted by:** Team 110 (shaked_arch / Claude Code)
**Authority:** Team 00 (Nimrod)
**To:** Team 190 (shaked_val / OpenAI)
**Date:** 2026-04-12
**Gate:** L-GATE_S (Spec + Authorization — LOD200 Concept Validation)

---

## Activation Prompt for Team 190

You are **Team 190** (shaked_val), the constitutional cross-engine validator for the **shaked-wg-agent** project. Your engine is OpenAI (cross-engine from the Cursor Composer builder and the Claude Code architect).

**Task:** Validate 3 LOD200 concept specs for S005-P004 (Codebase Internationalization). These are the specifications that enable Israeli listings to flow through the existing pipeline — independent of the Yad2 POC (S005-P001-WP001, running separately with Team 20).

**Context:** S005 (Israel Market Expansion) is ACTIVE. Team 00 strategic decisions are documented in `_COMMUNICATION/team_00/DECISIONS_ISRAEL_STRATEGY_v1.0.0.md`. A codebase audit identified CH/CHF/Swiss-specific hardcoding across 14+ files that must be generalized before any Israeli listing can enter the pipeline. These 3 WPs decompose that work by risk and complexity.

---

## Input Files (read all before validating)

### LOD200 Specs (primary validation targets)

| # | WP ID | Label | Track | Priority | LOD200 Path |
|---|-------|-------|-------|----------|-------------|
| 1 | S005-P004-WP001 | Data field generalization (currency + transit) | A | HIGH | `_aos/work_packages/S005-P004-WP001/LOD200_S005-P004-WP001.md` |
| 2 | S005-P004-WP002 | Dynamic scraper registry | A | MEDIUM | `_aos/work_packages/S005-P004-WP002/LOD200_S005-P004-WP002.md` |
| 3 | S005-P004-WP003 | Keyword/label locale generalization | B | LOW | `_aos/work_packages/S005-P004-WP003/LOD200_S005-P004-WP003.md` |

### Context files (also read)

- `_aos/roadmap.yaml` — current project state, all WP metadata, dependency chains
- `_COMMUNICATION/team_00/DECISIONS_ISRAEL_STRATEGY_v1.0.0.md` — Team 00 strategic decisions driving this work
- `_aos/MILESTONE_MAP.md` — milestone status overview
- `shaked_wg_agent/scrapers/base.py` — current ScrapedListing dataclass (price_chf field, line 35)
- `shaked_wg_agent/config.py` — current SearchProfile (budget_min_chf/budget_max_chf, lines 93-94), CityDefinition
- `shaked_wg_agent/scorer.py` — current scoring logic, German vegan keywords (lines 21-23)
- `shaked_wg_agent/runner.py` — current _build_scraper() hardcoded mapping (lines 113-126)
- `shaked_wg_agent/publisher/html_report.py` — hardcoded CHF references, German UI labels
- `shaked_wg_agent/__main__.py` — "Tram lines" label, German status badges

---

## Validation Checklist (apply to each LOD200)

### Per-Document Checks (LOD200 Completeness)

| # | Check | Requirement |
|---|-------|-------------|
| 1 | Frontmatter complete | `lod_target: LOD200`, `lod_status`, `track`, `authoring_team`, `consuming_team`, `priority` all present |
| 2 | Problem statement clear | §1 articulates WHY this work is needed with specific references to current code |
| 3 | Scope well-bounded | §3.1 (in scope) is specific enough to estimate effort; §3.2 (out of scope) prevents creep |
| 4 | Affected components listed | §4 names specific files with nature of change |
| 5 | Dependencies accurate | §5 lists correct dependencies; no missing or phantom deps |
| 6 | Risks identified | §6 lists realistic risks with mitigations |
| 7 | Success criteria testable | §7 each criterion is verifiable (grep, test suite, manual check) |
| 8 | Track decision justified | §8 rationale matches Track A/B criteria from governance model |
| 9 | No premature LOD400 detail | LOD200 describes WHAT and WHY, not detailed HOW (no function signatures, no code snippets) |

### Cross-WP Consistency Checks

| # | Check | What to verify |
|---|-------|---------------|
| 10 | Dependency chain valid | WP003 depends on WP001; no circular deps; order is WP001 → WP002 (parallel) → WP003 |
| 11 | Scope non-overlapping | No duplicate scope between the 3 WPs (currency in WP001, registry in WP002, keywords in WP003) |
| 12 | Field rename consistency | WP001 renames `price_chf`→`price` + adds `currency`; WP002 references `connector_class` for registry; WP003 references locale config — verify no conflicts |
| 13 | Blocked WP alignment | Verify WP003 (Track B) correctly identifies LOD300 gate need; WP001/WP002 (Track A) correctly skip LOD300 |
| 14 | Strategic alignment | All 3 WPs trace back to Team 00 decisions (D1-D5) and S005 milestone objectives |
| 15 | Codebase accuracy | File paths and line numbers referenced in specs match actual current codebase |

---

## Codebase Verification (validator MUST check)

The specs reference specific line numbers and field names. Verify these are accurate:

| Claim in spec | File | Expected |
|--------------|------|----------|
| `price_chf` field at line 35 | `scrapers/base.py` | ScrapedListing.price_chf: int \| None |
| `budget_min_chf` at line 93 | `config.py` | SearchProfile.budget_min_chf |
| German vegan keywords at lines 21-23 | `scorer.py` | Hardcoded German keyword sets |
| Hardcoded scraper mapping lines 113-126 | `runner.py` | Dict mapping source names to classes |
| "Tram lines" label | `__main__.py` | Hardcoded transit label |

---

## Output Format

Write your validation result to:
```
_COMMUNICATION/team_190/S005-P004-WP001/S005-P004_LOD200_VALIDATION_RESULT.md
```

**Structure:**

```markdown
# S005-P004 LOD200 Validation Result (L-GATE_S)
**Validator:** Team 190 (shaked_val / OpenAI)
**Date:** [date]
**Gate:** L-GATE_S (Spec + Authorization)
**Overall Verdict:** [PASS / FAIL / PASS WITH FINDINGS]

## Per-WP Verdicts

| WP | Track | Verdict | Findings |
|----|-------|---------|----------|
| S005-P004-WP001 | A | PASS/FAIL | [summary] |
| S005-P004-WP002 | A | PASS/FAIL | [summary] |
| S005-P004-WP003 | B | PASS/FAIL | [summary] |

## Cross-WP Consistency

| Check | Verdict | Notes |
|-------|---------|-------|
| Dependency chain | PASS/FAIL | ... |
| Scope non-overlapping | PASS/FAIL | ... |
| Field rename consistency | PASS/FAIL | ... |
| Track decisions | PASS/FAIL | ... |
| Strategic alignment | PASS/FAIL | ... |
| Codebase accuracy | PASS/FAIL | ... |

## Detailed Findings

[Per-WP detailed findings with severity: BLOCKING / MAJOR / MINOR / INFO]

## Recommendation

[PASS L-GATE_S → authorize LOD400 spec creation (WP001+WP002 Track A)
 and LOD300 design (WP003 Track B) / REVISE specific WPs / HALT]
```

---

## Iron Rules (binding on this validation)

1. **Cross-engine immutable.** You are OpenAI. The builder is Cursor Composer. The architect is Claude Code. Do NOT self-build.
2. **Read before judging.** Read all 3 LOD200 docs + context files + source code before issuing any verdict.
3. **No forbidden patterns.** Do NOT quote `forbidden_patterns` literals from `project_identity.yaml` in your output.
4. **Validate concept clarity.** LOD200 must be clear enough that an architect can produce LOD400 (Track A) or LOD300 (Track B) without ambiguity. Flag any section where scope is unclear or success criteria are untestable.
5. **Verify codebase claims.** Every file path, line number, and field name referenced in the specs must match the actual codebase. Inaccurate references = MAJOR finding.
6. **Be specific.** Findings must cite the exact WP, section number, and what is missing/wrong.

---

*Routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004 LOD200 | 2026-04-12*
