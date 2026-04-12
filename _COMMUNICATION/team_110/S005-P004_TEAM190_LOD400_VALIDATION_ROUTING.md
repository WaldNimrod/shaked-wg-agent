# Team 190 Validation Routing — S005-P004 LOD400 Batch
# Drafted by: Team 110 (shaked_arch / Claude Code)
# Authority: Team 00 (Nimrod)
# To: Team 190 (shaked_val / OpenAI)
# Date: 2026-04-12
# Gate: L-GATE_S (Spec + Authorization — LOD400 Validation)

---

## Activation Prompt for Team 190

You are **Team 190** (shaked_val), the constitutional cross-engine validator for the **shaked-wg-agent** project. Your engine is OpenAI (cross-engine from the Cursor Composer builder and the Claude Code architect).

**Task:** Validate 3 LOD400 executable specifications for S005-P004 (Codebase Internationalization) work packages. This is the L-GATE_S validation — the gate between specification and implementation.

---

## Input Files (read all before validating)

### LOD400 Specs (primary validation targets)

| # | WP ID | LOD400 Path |
|---|-------|-------------|
| 1 | S005-P004-WP001 | `_aos/work_packages/S005-P004-WP001/LOD400_S005-P004-WP001.md` |
| 2 | S005-P004-WP002 | `_aos/work_packages/S005-P004-WP002/LOD400_S005-P004-WP002.md` |
| 3 | S005-P004-WP003 | `_aos/work_packages/S005-P004-WP003/LOD400_S005-P004-WP003.md` |

### Parent LOD300 Specs (for consistency verification)

| # | WP ID | LOD300 Path |
|---|-------|-------------|
| 1 | S005-P004-WP001 | `_aos/work_packages/S005-P004-WP001/LOD300_S005-P004-WP001.md` |
| 2 | S005-P004-WP002 | `_aos/work_packages/S005-P004-WP002/LOD300_S005-P004-WP002.md` |
| 3 | S005-P004-WP003 | `_aos/work_packages/S005-P004-WP003/LOD300_S005-P004-WP003.md` |

### Context files (also read)

- `_aos/roadmap.yaml` — current project state and WP metadata
- `_aos/context/PROJECT_CONTEXT.md` — project background
- `shaked_wg_agent/config.py` — current config implementation (CityDefinition, SearchProfile, SourceDefinition, ResolvedSource)
- `shaked_wg_agent/scrapers/base.py` — current ScrapedListing dataclass and BaseScraper interface
- `shaked_wg_agent/scorer.py` — current vegan keywords and scoring logic
- `shaked_wg_agent/runner.py` — current _build_scraper mapping and _verify_flatfox_via_api
- `shaked_wg_agent/__main__.py` — current CLI status display and status badges
- `shaked_wg_agent/publisher/html_report.py` — current HTML report with hardcoded "CHF"
- `shaked_wg_agent/notifier/email_notifier.py` — current email notifier with German text
- `shaked_wg_agent/notifier/digest_builder.py` — current digest builder with price_chf
- `shaked_wg_agent/api/schemas.py` — current API schemas
- `data/sources.json` — current scraper_class values (short names)
- `data/profiles/default.json` — current budget_min_chf / budget_max_chf fields

---

## Validation Checklist (apply to each LOD400)

### Per-Document Checks (LOD400 Completeness)

| # | Check | Requirement |
|---|-------|-------------|
| 1 | Frontmatter complete | `lod_target: LOD400`, `lod_status`, `track`, `work_package_id`, `version` all present |
| 2 | Scope reminder present | §1 exists, matches LOD300/LOD200 scope |
| 3 | Technical specification | §2 covers all components from LOD300 with specific, unambiguous implementation instructions |
| 4 | Acceptance criteria testable | Every AC is measurable and verifiable — no vague criteria |
| 5 | All LOD300 components covered | Every entity, interface, and behavior from LOD300 has a corresponding LOD400 section |
| 6 | Data model exact | §3 specifies exact field definitions, types, and constraints |
| 7 | API contracts exact | §4 specifies exact signatures with BEFORE/AFTER format |
| 8 | Error handling specified | §5 lists all error cases with expected behavior |
| 9 | Out of scope explicit | §6 clearly states what is NOT built |
| 10 | Test requirements specified | §7 covers unit, integration, and cross-engine validation scope |
| 11 | No implementation leakage beyond spec | LOD400 describes WHAT to implement, not HOW (no full code blocks — those are LOD500) |
| 12 | Cross-engine validation closing | Iron Rule closing section present |

### Cross-WP Consistency Checks (S005-P004 specific)

| # | Check | What to verify |
|---|-------|---------------|
| 13 | Field rename cascade | WP001 renames `price_chf` → `price`. WP003 scorer reads `listing.get("price")` (not `price_chf`). Verify consistent field name usage. |
| 14 | Currency vs currency_symbol alignment | WP001 adds `CityDefinition.currency` (ISO 4217 code, e.g. "CHF"). WP003 adds `Locale.currency_symbol` (display symbol, e.g. "₪"). Verify these are complementary, not conflicting. |
| 15 | Country field in ScrapedListing | WP003 adds `ScrapedListing.country`. WP001 adds `ScrapedListing.currency`. Verify both are additive fields, both set from `city` at scrape time, no conflict. |
| 16 | Budget field rename consistency | WP001 renames `budget_min_chf` → `budget_min`. WP003 scorer must use `profile.budget_min` (not old name). Verify cross-WP field name consistency. |
| 17 | SourceDefinition connector_class | Only WP002 adds `connector_class` to SourceDefinition/ResolvedSource. Verify WP001 and WP003 do not conflict with this addition. |
| 18 | Accept-Language vs scraper instantiation | WP003 parameterizes Accept-Language in BaseScraper.__init__. WP002 changes how scrapers are instantiated (FQN resolution). Verify both go through same constructor signature without conflict. |
| 19 | LOD300 → LOD400 traceability | Every LOD300 business rule, acceptance criterion, and component must be traceable to a LOD400 section. Missing coverage = BLOCKING finding. |

---

## Output Format

Write your validation result to:
```
_COMMUNICATION/team_190/S005-P004_LOD400_VALIDATION_RESULT.md
```

**Structure:**

```markdown
# S005-P004 LOD400 Validation Result (L-GATE_S)
**Validator:** Team 190 (shaked_val / OpenAI)
**Date:** [date]
**Gate:** L-GATE_S (Spec + Authorization)
**Overall Verdict:** [PASS / FAIL / PASS WITH FINDINGS]

## Per-WP Verdicts

| WP | Verdict | Findings |
|----|---------|----------|
| S005-P004-WP001 | PASS/FAIL | [summary] |
| S005-P004-WP002 | PASS/FAIL | [summary] |
| S005-P004-WP003 | PASS/FAIL | [summary] |

## Cross-WP Consistency

| Check | Verdict | Notes |
|-------|---------|-------|
| Field rename cascade | PASS/FAIL | ... |
| Currency vs currency_symbol alignment | PASS/FAIL | ... |
| Country field in ScrapedListing | PASS/FAIL | ... |
| Budget field rename consistency | PASS/FAIL | ... |
| SourceDefinition connector_class | PASS/FAIL | ... |
| Accept-Language vs scraper instantiation | PASS/FAIL | ... |
| LOD300 → LOD400 traceability | PASS/FAIL | ... |

## Detailed Findings

[Per-WP detailed findings with severity: BLOCKING / MAJOR / MINOR / INFO]

## Recommendation

[PASS L-GATE_S → authorize builder to proceed / REVISE specific WPs / HALT]
```

---

## Iron Rules (binding on this validation)

1. **Cross-engine immutable.** You are OpenAI. The builder is Cursor Composer. The architect is Claude Code. Do NOT self-build.
2. **Read before judging.** Read all 3 LOD400 docs + their parent LOD300 docs + source code before issuing any verdict.
3. **No forbidden patterns.** Do NOT quote `forbidden_patterns` literals from `project_identity.yaml` in your output.
4. **Validate executability.** LOD400 must be specific enough that a builder agent can implement without ambiguity. Flag any section where a builder would need to make design decisions not covered by the spec.
5. **Verify LOD300 coverage.** Every LOD300 requirement must be traceable to a LOD400 section. Missing coverage = BLOCKING finding.
6. **Be specific.** Findings must cite the exact WP, section number, and what is missing/wrong.

---

*Routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004 LOD400 | 2026-04-12*
