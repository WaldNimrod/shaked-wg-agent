# S005-P004 LOD400 Revalidation Result (L-GATE_S) — v1.1.0
**Validator:** Team 190 (shaked_val / OpenAI)  
**Date:** 2026-04-12  
**Gate:** L-GATE_S (Spec + Authorization)  
**Previous verdict:** FAIL (v1.0.0)  
**Current verdict:** PASS WITH FINDINGS

## Remediation Verification

| # | Finding (v1.0.0) | Resolved? | Notes |
|---|-------------------|-----------|-------|
| R1 | WP001 AC contradiction | YES | WP001 §2.10 AC-22 now scopes to legacy **definitions/assignments**; backward-compat `.get("price_chf")` reads are explicitly allowed. |
| R2 | Tutti source | YES | WP001 §2.2 excludes tutti; WP002 §2.5 requires removing `tutti` entry from `data/sources.json`. |
| R3 | WP003 Locale field count | YES | WP003 §2.1 AC-01 fixes `Locale` at 10 fields; WP003 §2.6 AC-29 reaffirms email strings are not Locale fields. |
| R4 | WP003 "or" branch | YES | WP003 §2.6 specifies one exact approach: `EMAIL_STRINGS` + `get_email_strings()` accessor. |
| R5 | IL ISO currency code | YES | WP001 §2.1(4) defines ISO 4217 `"ILS"`; WP003 §2.1 cross-WP note maps ISO vs display symbol (`"₪"`). |
| R6 | connector_class contract | YES | WP002 §2.3(2) explicitly requires connectors subclass `BaseScraper` (no `BaseConnector`). |

## Per-WP Verdicts

| WP | Verdict | Findings |
|----|---------|----------|
| S005-P004-WP001 | PASS | MINOR: AC-23 scope ambiguity vs WP003 locale currency symbols (see Detailed Findings). |
| S005-P004-WP002 | PASS | MINOR: Parent LOD300 mockup still references Tutti FQN; align LOD300 example to v1.1.0 behavior. |
| S005-P004-WP003 | PASS | No new issues found; remediation is consistent and testable. |

## Cross-WP Consistency

| Check | Verdict | Notes |
|-------|---------|-------|
| Field rename cascade | PASS | WP001 defines `price` + backward-compat reads for `price_chf`; WP003 changes vegan scoring only and does not conflict. |
| Currency vs currency_symbol alignment | PASS WITH FINDINGS | WP001 uses ISO codes (`CityDefinition.currency="ILS"`); WP003 uses display symbol (`Locale.currency_symbol="₪"`). WP001 AC-23 wording may accidentally outlaw locale symbols (see Detailed Findings). |
| Country field in ScrapedListing | PASS | WP001 adds `ScrapedListing.currency`; WP003 adds `ScrapedListing.country`; both set from `city` at scrape time. |
| Budget field rename consistency | PASS | WP001 renames to `budget_min/budget_max` and updates scorer access; WP003 does not contradict. |
| SourceDefinition connector_class | PASS | Only WP002 adds `connector_class` to `SourceDefinition`/`ResolvedSource`; no conflicts with WP001/WP003. |
| Accept-Language vs scraper instantiation | PASS | WP003 changes `BaseScraper.__init__` header behavior; WP002 instantiates resolved classes with unchanged constructor signature (`source_id, search_url, city`). |
| LOD300 → LOD400 traceability | PASS WITH FINDINGS | All LOD300 business rules are covered; one stale LOD300 WP002 example still shows Tutti mapping and should be updated for consistency. |

## Detailed Findings (if any)

- **MINOR (WP001 §2.10 AC-23; WP003 §2.1):** WP001 AC-23 states “No hardcoded `"CHF"` display string exists in application code”, but WP003 §2.1 requires `Locale.currency_symbol = "CHF"` for CH. Clarify AC-23 scope to exclude the locale registry module (treat it as canonical display data), or rephrase to prohibit hardcoded currency strings only in *consumer rendering code* (CLI/report/notifiers), not in locale/config tables.
- **MINOR (Traceability / parent doc drift):** `LOD300_S005-P004-WP002.md` §5.3 still includes an example mapping for `"TuttiScraper" → "shaked_wg_agent.scrapers.tutti.TuttiScraper"`, while `LOD400_S005-P004-WP002.md` §2.5 requires removing the `tutti` entry entirely. Update the LOD300 example to match the v1.1.0 remediation to prevent future confusion.

## Recommendation

**PASS L-GATE_S → authorize builder to proceed**, with the two MINOR documentation clarifications above ideally applied before implementation starts (or captured as a builder clarification note in the WP execution log).

Routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004 LOD400 revalidation v1.1.0 | 2026-04-12
