# S005-P004 LOD400 Validation Result (L-GATE_S)
**Validator:** Team 190 (shaked_val / OpenAI)  
**Date:** 2026-04-12  
**Gate:** L-GATE_S (Spec + Authorization)  
**Overall Verdict:** FAIL

## Per-WP Verdicts

| WP | Verdict | Findings |
|----|---------|----------|
| S005-P004-WP001 | FAIL | BLOCKING: AC contradictions (`grep` zero-hits vs required backward-compat fallbacks); MAJOR: references non-existent `TuttiScraper`; MAJOR: parent LOD200 version mismatch. |
| S005-P004-WP002 | FAIL | BLOCKING: requires `shaked_wg_agent.scrapers.tutti.TuttiScraper` FQN but scraper module/class not present; MAJOR: connector_class contract forces `BaseScraper` subclass (potentially incompatible with intended “connector” separation). |
| S005-P004-WP003 | FAIL | BLOCKING: §2.6 directs adding locale strings “to `Locale` dataclass” but AC-01 fixes `Locale` at 10 fields; BLOCKING: “or” branch leaves design decision unresolved at LOD400; MAJOR: currency symbol vs ISO currency code not specified for IL. |

## Cross-WP Consistency

| Check | Verdict | Notes |
|-------|---------|-------|
| Field rename cascade | PASS WITH FINDINGS | WP001 defines `listing.get("price") or listing.get("price_chf")` fallback (§2.4), but its own AC-22 conflicts (see WP001 findings). WP003 does not re-spec budget/price handling, so merge safety depends on WP001. |
| Currency vs currency_symbol alignment | PASS WITH FINDINGS | WP001 defines `CityDefinition.currency` as ISO 4217 code (§1/§3.1), while WP003 defines `Locale.currency_symbol` (§2.1/§3.1). Complementary, but IL mapping (ISO code vs display symbol) is not made explicit. |
| Country field in ScrapedListing | PASS | WP001 adds `ScrapedListing.currency` (§2.2) and WP003 adds `ScrapedListing.country` (§2.3). Both are additive and set from `city` at scrape time. |
| Budget field rename consistency | PASS | WP001 renames `budget_min_chf/budget_max_chf` → `budget_min/budget_max` (§2.3) and updates scorer budget access (§2.4). WP003 does not contradict this. |
| SourceDefinition connector_class | PASS WITH FINDINGS | Only WP002 introduces `connector_class` (§2.1–§2.2). No direct conflict with WP001/WP003, but connector validation rule may constrain future connector design. |
| Accept-Language vs scraper instantiation | PASS | WP003 keeps `BaseScraper.__init__(source_id, search_url, city)` signature and only sets headers (§2.4); WP002 instantiates via resolved class with the same signature (§2.3). |
| LOD300 → LOD400 traceability | FAIL | WP001 and WP002 carry forward requirements that are not executable against current repo state (TuttiScraper) and/or contain internally contradictory ACs; WP003 has internal contradictions around `Locale` field count vs email localization. |

## Detailed Findings

### S005-P004-WP001 — Data Field Generalization (Currency + Transit Labels)

- **BLOCKING (Checklist #4 / executability):** AC-22/AC-23 in §2.10 require `grep` zero hits for legacy identifiers, but §2.3(3) and §2.4(3) explicitly require backward-compatible fallbacks that reference `"budget_min_chf"`, `"budget_max_chf"`, and `"price_chf"` in code. These criteria cannot be simultaneously satisfied as written.
  - Affected: §2.3(3) + AC-07, §2.4(3) + AC-10, §2.10 AC-22/AC-23.
- **MAJOR (Checklist #3/#5 / codebase alignment):** §2.2(4) + AC-05 require updating `TuttiScraper`, but there is no `shaked_wg_agent/scrapers/tutti.py` module or `TuttiScraper` class in the current codebase. The WP must either (a) explicitly add Tutti scraper implementation into scope, or (b) explicitly remove/disable the `tutti` source entry and remove Tutti-related ACs.
- **MAJOR (Traceability metadata):** Header lists `parent_lod200: ... v1.1.0`, but the current `LOD200_S005-P004-WP001.md` frontmatter is `version: v1.0.0`. Align the referenced parent version(s) to avoid governance ambiguity.
- **MINOR (Checklist #11):** §4 includes multiple code blocks. If the project’s LOD400 policy treats any code block beyond short signatures as leakage, these should be reduced to “BEFORE/AFTER field name lists” instead of function bodies.

### S005-P004-WP002 — Dynamic Scraper Registry

- **BLOCKING (Checklist #3/#4 / executability):** §2.5 + AC-16 require `_resolve_class()` to successfully resolve `shaked_wg_agent.scrapers.tutti.TuttiScraper`, but there is no `shaked_wg_agent/scrapers/tutti.py` module in the current repo. This blocks implementability and testability (AC-16/AC-17) unless the WP explicitly includes adding the missing scraper module/class or removing the source entry from `data/sources.json`.
- **MAJOR (Contract clarity):** §2.3(2) requires `issubclass(cls, BaseScraper)` for both `scraper_class` and `connector_class` resolution. If `connector_class` is meant for non-scraper “connector/normalizer” objects, LOD400 must explicitly define whether connectors must subclass `BaseScraper` (and why), or define a separate `BaseConnector` contract and validation rule.
- **MAJOR (Checklist #11 boundary):** §2.3 specifies an exact resolution algorithm (split FQN, importlib, getattr). If LOD400 is intended to be “what/contract” not “implementation recipe”, reduce this to required behavior + error cases, leaving micro-steps to LOD500.
- **MAJOR (Traceability metadata):** Header lists `parent_lod200: ... v1.1.0`, but the current `LOD200_S005-P004-WP002.md` frontmatter is `version: v1.0.0`.

### S005-P004-WP003 — Keyword and Label Locale Generalization

- **BLOCKING (Checklist #3/#4 / internal contradiction):** §2.1 AC-01 fixes `Locale` as a frozen dataclass with **10 fields**, but §2.6(2) instructs “Add locale-specific string constants to the `Locale` dataclass or resolve from locale at notification time.” Adding fields to `Locale` violates AC-01; leaving them out leaves the behavior underspecified. Choose one explicit approach:
  - Option A: Keep `Locale` at 10 fields; define email strings as separate module-level constants per locale (not dataclass fields), and specify exact lookup behavior in email notifier.
  - Option B: Add explicit email-string fields to `Locale`; then update §2.1/§3.1 and AC-01 to the new field count and list.
- **BLOCKING (Checklist #3 / executability):** The “or” branch in §2.6(2) is a builder design decision at LOD400. LOD400 must specify one exact schema/contract for where localized email strings live and how they are accessed.
- **MAJOR (Cross-WP alignment):** WP001 introduces `CityDefinition.currency` as ISO 4217 code, while WP003 defines `Locale.currency_symbol` for display. The specs should explicitly define the IL ISO currency code expected (and the relationship to the display symbol) to avoid inconsistent UI/API output across consumers.
- **MAJOR (Traceability metadata):** Header lists `parent_lod200: ... v1.1.0`, but the current `LOD200_S005-P004-WP003.md` frontmatter is `version: v1.0.0`.

## Recommendation

**HALT** — revise the LOD400 specs before any builder starts S005-P004 implementation.

Minimum remediation required before re-submitting for L-GATE_S:
1. **WP001:** Resolve AC contradictions by scoping `grep` checks to field definitions/assignments only (or drop “zero hits” checks) while preserving backward compatibility requirements.
2. **WP001+WP002:** Decide and document the `tutti` source path: either add `shaked_wg_agent/scrapers/tutti.py` + `TuttiScraper` explicitly in-scope, or remove/disable the source and delete related ACs and FQNs.
3. **WP003:** Remove the §2.6 “or” branch and make email localization storage explicit, consistent with `Locale` field-count AC-01.
4. **All WPs:** Align `parent_lod200` version references with actual LOD200 doc versions (or bump LOD200 versions to match).

Routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004 LOD400 | 2026-04-12
