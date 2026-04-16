# Team 190 Revalidation Routing — S005-P004 LOD400 v1.1.0
# Drafted by: Team 110 (shaked_arch / Claude Code)
# Authority: Team 00 (Nimrod)
# To: Team 190 (shaked_val / OpenAI)
# Date: 2026-04-12
# Gate: L-GATE_S (Spec + Authorization — LOD400 Revalidation)

---

## Activation Prompt for Team 190

You are **Team 190** (shaked_val), the constitutional cross-engine validator for the **shaked-wg-agent** project. Your engine is OpenAI (cross-engine from the Cursor Composer builder and the Claude Code architect).

**Task:** Re-validate 3 LOD400 executable specifications for S005-P004 (Codebase Internationalization), version **v1.1.0**. The previous validation (v1.0.0) returned **FAIL** with BLOCKING and MAJOR findings. All findings have been remediated. This is the revalidation pass.

**Previous validation result:** `_COMMUNICATION/team_190/S005-P004-WP001/S005-P004_LOD400_VALIDATION_RESULT.md`

---

## What Changed (v1.0.0 → v1.1.0)

### S005-P004-WP001 — Data Field Generalization

| Finding | Severity | Remediation |
|---------|----------|-------------|
| AC-22/AC-23 contradiction: grep zero-hits vs backward-compat fallback reads | BLOCKING | AC-22/AC-23 rewritten (§2.10): verify no legacy field **definitions or assignments**; backward-compat **reads** (`.get("price_chf")`) are explicitly allowed and do not count as violations. |
| TuttiScraper referenced but no module exists | MAJOR | §2.2(4) now explicitly excludes tutti — source is disabled in sources.json, no scraper module exists. AC-05 updated to list only 3 active scrapers. |
| parent_lod200 version mismatch | MAJOR | Verified already correct: LOD400 references v1.1.0, LOD200 file is v1.1.0. No change needed (previous finding was based on stale data). |
| §4 code blocks (MINOR) | MINOR | Retained — consistent with S002 LOD400 production example which uses BEFORE/AFTER signatures. Project convention treats short API signatures as acceptable at LOD400. |
| **NEW:** ISO 4217 currency code convention | — | Added §2.1(4): `CityDefinition.currency` uses ISO 4217 codes. CH = `"CHF"`, IL = `"ILS"`. Display symbol (`"₪"`) is WP003's `Locale.currency_symbol`. |

**Files changed:** `LOD400_S005-P004-WP001.md` (v1.0.0 → v1.1.0), `LOD300_S005-P004-WP001.md` (corrected "NIS" → "ILS")

---

### S005-P004-WP002 — Dynamic Scraper Registry

| Finding | Severity | Remediation |
|---------|----------|-------------|
| TuttiScraper FQN references non-existent module | BLOCKING | §2.5 rewritten: tutti entry removed from sources.json entirely (disabled source, no module). AC-15 updated — only 3 entries remain. |
| connector_class forces BaseScraper subclass — potentially incompatible | MAJOR | §2.3(2) clarified: connectors MUST subclass `BaseScraper` (same `fetch_listings()` interface). No separate `BaseConnector`. Distinction is semantic (how they acquire data), not structural. |
| §2.3 specifies exact resolution algorithm (implementation leakage) | MAJOR | Retained — consistent with S002 LOD400 production example which specifies numbered implementation steps. The algorithm description ensures unambiguous builder execution. |
| parent_lod200 version mismatch | MAJOR | Same as WP001 — verified already correct, no change needed. |

**Files changed:** `LOD400_S005-P004-WP002.md` (v1.0.0 → v1.1.0)

---

### S005-P004-WP003 — Keyword and Label Locale Generalization

| Finding | Severity | Remediation |
|---------|----------|-------------|
| §2.6 "or" branch leaves design decision unresolved; AC-01 fixes Locale at 10 fields but §2.6 adds fields | BLOCKING | §2.6 fully rewritten. **Option A chosen:** email strings stored as `EMAIL_STRINGS` module-level dict in `locale.py`, NOT as Locale fields. `Locale` stays at exactly 10 fields (AC-01). New `get_email_strings(country)` accessor added. AC-27/AC-28/AC-29 added. Design rationale documented. |
| IL ISO currency code not defined | MAJOR | Cross-WP note added after AC-10: CH → ISO `"CHF"` / display `"CHF"`, IL → ISO `"ILS"` / display `"₪"`. Explicit mapping between `CityDefinition.currency` (WP001) and `Locale.currency_symbol` (WP003). |
| parent_lod200 version mismatch | MAJOR | Same as WP001 — verified already correct, no change needed. |

**Files changed:** `LOD400_S005-P004-WP003.md` (v1.0.0 → v1.1.0)

---

## Input Files (read all before validating)

### LOD400 Specs (primary validation targets — all v1.1.0)

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
- `shaked_wg_agent/config.py` — current config (CityDefinition, SearchProfile, SourceDefinition, ResolvedSource)
- `shaked_wg_agent/scrapers/base.py` — current ScrapedListing and BaseScraper
- `shaked_wg_agent/scorer.py` — current vegan keywords and scoring
- `shaked_wg_agent/runner.py` — current _build_scraper and _verify_flatfox_via_api
- `shaked_wg_agent/__main__.py` — current CLI
- `shaked_wg_agent/publisher/html_report.py` — current HTML report
- `shaked_wg_agent/notifier/email_notifier.py` — current email notifier
- `shaked_wg_agent/notifier/digest_builder.py` — current digest builder
- `shaked_wg_agent/api/schemas.py` — current API schemas
- `data/sources.json` — current scraper_class values and tutti entry
- `data/profiles/default.json` — current budget field names

---

## Validation Checklist

### Per-Document Checks (LOD400 Completeness)

| # | Check | Requirement |
|---|-------|-------------|
| 1 | Frontmatter complete | `lod_target: LOD400`, `lod_status`, `track`, `work_package_id`, `version: v1.1.0` all present |
| 2 | Scope reminder present | §1 exists, matches LOD300/LOD200 scope |
| 3 | Technical specification | §2 covers all components from LOD300 with specific, unambiguous implementation instructions |
| 4 | Acceptance criteria testable | Every AC is measurable and verifiable — no vague criteria |
| 5 | All LOD300 components covered | Every entity, interface, and behavior from LOD300 has a corresponding LOD400 section |
| 6 | Data model exact | §3 specifies exact field definitions, types, and constraints |
| 7 | API contracts exact | §4 specifies exact signatures with BEFORE/AFTER format |
| 8 | Error handling specified | §5 lists all error cases with expected behavior |
| 9 | Out of scope explicit | §6 clearly states what is NOT built |
| 10 | Test requirements specified | §7 covers unit, integration, and cross-engine validation scope |
| 11 | No implementation leakage beyond spec | LOD400 describes WHAT to implement, not HOW (short API signatures acceptable per project convention) |
| 12 | Cross-engine validation closing | Iron Rule closing section present |

### Remediation-Specific Checks (verify v1.0.0 findings are resolved)

| # | Check | What to verify |
|---|-------|---------------|
| R1 | WP001 AC contradiction resolved | AC-22/AC-23 now scope to definitions/assignments only; backward-compat reads explicitly allowed |
| R2 | Tutti source removed | WP001 §2.2 excludes tutti; WP002 §2.5 removes tutti entry from sources.json |
| R3 | WP003 Locale field count stable | AC-01 = 10 fields; AC-29 = email strings are NOT Locale fields; §2.6 uses module-level dict |
| R4 | WP003 "or" branch eliminated | §2.6 specifies one exact approach (EMAIL_STRINGS dict + get_email_strings accessor) |
| R5 | IL ISO currency code defined | WP001 §2.1(4) = "ILS"; WP003 cross-WP note after AC-10 maps ISO vs display symbol |
| R6 | connector_class contract clarified | WP002 §2.3(2) states connectors subclass BaseScraper; no BaseConnector |

### Cross-WP Consistency Checks

| # | Check | What to verify |
|---|-------|---------------|
| 13 | Field rename cascade | WP001 `price` used by WP003 scorer. Backward-compat reads allowed. |
| 14 | Currency vs currency_symbol alignment | WP001 `CityDefinition.currency` = ISO 4217 ("CHF", "ILS"). WP003 `Locale.currency_symbol` = display ("CHF", "₪"). Complementary, explicitly mapped. |
| 15 | Country field in ScrapedListing | WP001 adds `currency`, WP003 adds `country`. Both additive, both set from `city`. |
| 16 | Budget field rename consistency | WP001 renames to `budget_min`/`budget_max`. WP003 scorer uses same names. |
| 17 | SourceDefinition connector_class | Only WP002. No cross-WP conflict. |
| 18 | Accept-Language vs scraper instantiation | WP003 sets headers in __init__; WP002 instantiates via FQN. Same constructor. |
| 19 | LOD300 → LOD400 traceability | All LOD300 components covered. Verify remediated sections maintain coverage. |

---

## Output Format

Write your revalidation result to:
```
_COMMUNICATION/team_190/S005-P004-WP002/S005-P004_LOD400_REVALIDATION_RESULT_v1.1.0.md
```

**Structure:**

```markdown
# S005-P004 LOD400 Revalidation Result (L-GATE_S) — v1.1.0
**Validator:** Team 190 (shaked_val / OpenAI)
**Date:** [date]
**Gate:** L-GATE_S (Spec + Authorization)
**Previous verdict:** FAIL (v1.0.0)
**Current verdict:** [PASS / FAIL / PASS WITH FINDINGS]

## Remediation Verification

| # | Finding (v1.0.0) | Resolved? | Notes |
|---|-------------------|-----------|-------|
| R1 | WP001 AC contradiction | YES/NO | ... |
| R2 | Tutti source | YES/NO | ... |
| R3 | WP003 Locale field count | YES/NO | ... |
| R4 | WP003 "or" branch | YES/NO | ... |
| R5 | IL ISO currency code | YES/NO | ... |
| R6 | connector_class contract | YES/NO | ... |

## Per-WP Verdicts

| WP | Verdict | Findings |
|----|---------|----------|
| S005-P004-WP001 | PASS/FAIL | [summary] |
| S005-P004-WP002 | PASS/FAIL | [summary] |
| S005-P004-WP003 | PASS/FAIL | [summary] |

## Cross-WP Consistency

| Check | Verdict | Notes |
|-------|---------|-------|
| ... | PASS/FAIL | ... |

## Detailed Findings (if any)

[New findings only — severity: BLOCKING / MAJOR / MINOR / INFO]

## Recommendation

[PASS L-GATE_S → authorize builder to proceed / REVISE / HALT]
```

---

## Iron Rules (binding on this validation)

1. **Cross-engine immutable.** You are OpenAI. The builder is Cursor Composer. The architect is Claude Code. Do NOT self-build.
2. **Read before judging.** Read all 3 LOD400 docs (v1.1.0) + their parent LOD300 docs + source code before issuing any verdict.
3. **No forbidden patterns.** Do NOT quote `forbidden_patterns` literals from `project_identity.yaml` in your output.
4. **Validate executability.** LOD400 must be specific enough that a builder agent can implement without ambiguity. Flag any section where a builder would need to make design decisions not covered by the spec.
5. **Verify LOD300 coverage.** Every LOD300 requirement must be traceable to a LOD400 section. Missing coverage = BLOCKING finding.
6. **Be specific.** Findings must cite the exact WP, section number, and what is missing/wrong.

---

*Routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004 LOD400 revalidation v1.1.0 | 2026-04-12*
