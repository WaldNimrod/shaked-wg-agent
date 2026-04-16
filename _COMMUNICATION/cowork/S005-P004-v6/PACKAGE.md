# S005-P004 — Codebase Internationalization

## Identity


| Field              | Value                                                         |
| ------------------ | ------------------------------------------------------------- |
| **Package ID**     | S005-P004                                                     |
| **Sprint**         | S005 — Israel Market Expansion                                |
| **Date**           | 2026-04-13                                                    |
| **Version**        | v6 — Full validator pass, mount-path aligned, cross-refs fixed |
| **Work Packages**  | WP001 (Data Fields), WP002 (Scraper Registry), WP003 (Locale) |
| **Total ACs**      | 70 (24 + 17 + 29)                                             |
| **Authoring Team** | Team 110 (shaked_arch / Claude Code)                          |
| **Authority**      | Team 00 (Nimrod)                                              |
| **Validation**     | Team 190 — PASS WITH FINDINGS (v1.1.0), minors resolved       |
| **Pre-Submit**     | AOS Package Validator v1.1 — 99.1% PASS, 0 CRITICAL (11 checks) |


## Purpose

**shaked-wg-agent** is a Python CLI application that scrapes Swiss WG (shared apartment) listings from multiple platforms (wgzimmer, flatfox, wg-gesucht), scores them by relevance for a specific user profile, and delivers results via CLI, HTML report, REST API, and notifications (email, Telegram, Discord, ntfy).

Today the codebase is hardcoded for Switzerland: prices are `price_chf`, budgets are `budget_min_chf`, scraper selection is a hardcoded dict, vegan keywords are German-only, Accept-Language is `de-CH`, and notification text is German.

This package removes all Switzerland-specific hardcoding so the system can support Israel (and any future country) by adding only data — no code changes. Three work packages, executed in strict order.

---

## Cowork Setup

### Copy-Paste Files

The package includes two standalone text files with the exact content to paste into Cowork:

| File | Paste Into | Content |
|------|-----------|---------|
| **`S005-P004_INSTRUCTIONS.txt`** | Cowork project "Instructions" field | Agent identity, environment capabilities, project architecture, execution rules, file roles |
| **`S005-P004_ACTIVATION_PROMPT.txt`** | First chat message | Phase-by-phase execution plan, verification gates, iron rules |

### Setup Checklist

1. Create a Cowork project named `S005-P004-Internationalization`
2. Mount this folder (`S005-P004-v6`) as the workspace
3. Open `S005-P004_INSTRUCTIONS.txt` → copy entire content → paste into project Instructions
4. Create a new chat session
5. Open `S005-P004_ACTIVATION_PROMPT.txt` → copy entire content → paste as first message
6. Output directory will be created automatically by the activation prompt (`mkdir -p`)

---

## File Manifest

### Root — Copy-Paste Files (2 files)

| File | Content |
|------|---------|
| `S005-P004_INSTRUCTIONS.txt` | Exact text for Cowork project Instructions field |
| `S005-P004_ACTIVATION_PROMPT.txt` | Exact text for first Cowork chat message |

### assets/specs/ — Specifications and Mandates (6 files)


| File                                | Role                                     | WP    |
| ----------------------------------- | ---------------------------------------- | ----- |
| `LOD400_S005-P004-WP001.md`         | Primary spec — Data Field Generalization | WP001 |
| `LOD400_S005-P004-WP002.md`         | Primary spec — Dynamic Scraper Registry  | WP002 |
| `LOD400_S005-P004-WP003.md`         | Primary spec — Keyword/Label Locale      | WP003 |
| `MANDATE_S005-P004-WP001_TEAM20.md` | Builder mandate — scope, ACs, DO NOT     | WP001 |
| `MANDATE_S005-P004-WP002_TEAM20.md` | Builder mandate — scope, ACs, DO NOT     | WP002 |
| `MANDATE_S005-P004-WP003_TEAM20.md` | Builder mandate — scope, ACs, DO NOT     | WP003 |


### assets/src/ — Source Code (25 files)


| File                                            | Role       | WP           |
| ----------------------------------------------- | ---------- | ------------ |
| `shaked_wg_agent/__init__.py`                   | read-only  | —            |
| `shaked_wg_agent/__main__.py`                   | **modify** | WP001, WP003 |
| `shaked_wg_agent/config.py`                     | **modify** | WP001, WP002 |
| `shaked_wg_agent/runner.py`                     | **modify** | WP002        |
| `shaked_wg_agent/scorer.py`                     | **modify** | WP001, WP003 |
| `shaked_wg_agent/persistence.py`                | read-only  | —            |
| `shaked_wg_agent/scrapers/__init__.py`          | read-only  | —            |
| `shaked_wg_agent/scrapers/base.py`              | **modify** | WP001, WP003 |
| `shaked_wg_agent/scrapers/flatfox.py`           | **modify** | WP001, WP002 |
| `shaked_wg_agent/scrapers/wg_gesucht.py`        | **modify** | WP001        |
| `shaked_wg_agent/scrapers/wgzimmer_pw.py`       | **modify** | WP001        |
| `shaked_wg_agent/notifier/__init__.py`          | read-only  | —            |
| `shaked_wg_agent/notifier/base.py`              | read-only  | —            |
| `shaked_wg_agent/notifier/email_notifier.py`    | **modify** | WP001, WP003 |
| `shaked_wg_agent/notifier/ntfy_notifier.py`     | **modify** | WP001        |
| `shaked_wg_agent/notifier/telegram_notifier.py` | **modify** | WP001        |
| `shaked_wg_agent/notifier/discord_notifier.py`  | **modify** | WP001        |
| `shaked_wg_agent/notifier/digest_builder.py`    | **modify** | WP001        |
| `shaked_wg_agent/notifier/orchestrator.py`      | read-only  | —            |
| `shaked_wg_agent/api/__init__.py`               | read-only  | —            |
| `shaked_wg_agent/api/schemas.py`                | **modify** | WP001        |
| `shaked_wg_agent/api/app.py`                    | read-only  | —            |
| `shaked_wg_agent/api/routes.py`                 | read-only  | —            |
| `shaked_wg_agent/publisher/__init__.py`         | read-only  | —            |
| `shaked_wg_agent/publisher/html_report.py`      | **modify** | WP001        |


### assets/data/ — Data Files (3 files)


| File                    | Role       | WP    |
| ----------------------- | ---------- | ----- |
| `sources.json`          | **modify** | WP002 |
| `profiles/default.json` | **modify** | WP001 |
| `cities/basel.json`     | read-only  | —     |


### assets/tests/ — Test Files (7 files)


| File                  | Role                                        | WP    |
| --------------------- | ------------------------------------------- | ----- |
| `__init__.py`         | read-only                                   | —     |
| `test_config.py`      | update assertions for renamed fields        | WP001 |
| `test_scorer.py`      | update assertions for renamed fields        | WP001 |
| `test_api.py`         | update assertions for renamed fields        | WP001 |
| `test_persistence.py` | read-only (no renamed field refs)           | —     |
| `test_integration.py` | update assertions for renamed fields        | WP001 |
| `test_notifier.py`    | update assertions for renamed fields        | WP001 |


### New file created by WP003


| File                        | Role       | WP    |
| --------------------------- | ---------- | ----- |
| `shaked_wg_agent/locale.py` | **create** | WP003 |


**Total: 41 files in assets + 2 copy-paste files + 1 new file created during execution**

### validation/ — Pre-Submit Validation & Post-Submit Tool (4 files)


| File | Content |
|------|---------|
| `aos_package_validator.py` | AOS Package Validator v1.0 — generic Python tool for Cowork package validation |
| `aos_validator_config_template.json` | Config template documenting all validator fields |
| `validate_S005-P004-v6.json` | Filled config for this package (set `package_root` before running) |
| `validate_S005-P004-v6_report.json` | Pre-submit validation report — **99.1% PASS, 0 CRITICAL** |


---

## Pre-Submit Validation Report

This package was validated using the AOS Package Validator before submission.

**Result: 99.1% PASS — 0 CRITICAL, 0 HIGH, 0 MEDIUM, 0 LOW**


| Check Category | Passed | Total | Status |
|----------------|--------|-------|--------|
| FILE_EXISTS | 43 | 43 | PASS |
| PATH_RESOLUTION | 3 | 3 | PASS |
| SOURCE_ROOT_CONSISTENCY | 1 | 2 | PASS |
| CROSS_REFERENCE | 1 | 1 | PASS |
| WORK_PACKAGE_COMPLETENESS | 29 | 29 | PASS |
| OUTPUT_STRUCTURE | 2 | 2 | PASS |
| COWORK_CAPABILITIES | 8 | 8 | PASS |
| FIELD_RENAMES | 6 | 6 | PASS |
| VERIFICATION_GATES | 14 | 14 | PASS |
| WP_DEPENDENCY_CHAIN | 2 | 2 | PASS |
| MOUNT_PATH_ALIGNMENT | 2 | 2 | PASS |
| **TOTAL** | **111** | **112** | **PASS** |


Only 1 INFO-level finding remains (verification gate count — informational).

### Post-Submit Usage

The validator can also be run inside Cowork after execution to verify the agent's output:

```
cd validation/
python3 aos_package_validator.py validate_S005-P004-v6.json
```

The validator checks: file existence, path resolution in shell commands, SOURCE_ROOT consistency, cross-references, work package completeness, output directory structure, Cowork capability declarations, field rename compliance, verification gate correctness, WP dependency chain enforcement, and mount path alignment.

**Note:** Before running, set `package_root` in the config JSON to the actual mount path (e.g., `/sessions/.../mnt/S005-P004-v6`).

---

## Validation Criteria

### After Phase 1 (WP001 — Data Field Generalization)
- `grep -rn "price_chf" src/ --include="*.py" | grep -v "\.get\("` → zero hits
- `grep -rn '"CHF"' src/publisher/html_report.py` → zero hits
- `grep -n "Tram lines" src/__main__.py` → zero hits
- `grep -n "budget_min_chf" data/profiles/default.json` → zero hits
- CityDefinition has field `currency: str` with default `"CHF"`
- SearchProfile has `budget_min` and `budget_max` (no `_chf`)
- ScrapedListing has `price` + `currency` (no `price_chf`)

### After Phase 2 (WP002 — Dynamic Scraper Registry)
- `grep -n "mapping\s*=" src/runner.py` → zero hits
- `grep -n "_verify_flatfox_via_api" src/runner.py` → zero hits
- sources.json: 3 entries, all FQN, no tutti
- flatfox.py exports `verify_listings(listings, city)`

### After Phase 3 (WP003 — Locale Generalization)
- `grep -n "_VEGAN_STRONG" src/scorer.py` → zero hits
- `grep -n "de-CH" src/scrapers/base.py` → zero hits
- `grep -n '"neue Angebote"' src/notifier/email_notifier.py` → zero hits
- Locale dataclass has exactly 10 fields
- EMAIL_STRINGS is module-level dict, NOT Locale fields

### Final Comprehensive
- All Phase 1–3 grep checks pass simultaneously
- All test assertions compatible with new field names

---

## Expected Output

The agent writes modified files to `SOURCE_ROOT/output/` preserving directory structure:


| Phase | File                          | Changes                                                                               |
| ----- | ----------------------------- | ------------------------------------------------------------------------------------- |
| 1     | config.py                     | +CityDefinition.currency, renamed SearchProfile budget fields, backward-compat loader |
| 1     | scrapers/base.py              | Renamed price_chf→price, +currency field, updated to_dict                             |
| 1     | scrapers/flatfox.py           | ScrapedListing construction with price=, currency=                                    |
| 1     | scrapers/wg_gesucht.py        | ScrapedListing construction with price=, currency=                                    |
| 1     | scrapers/wgzimmer_pw.py       | ScrapedListing construction with price=, currency=                                    |
| 1     | scorer.py                     | Updated _budget_ok + score_listing field access                                       |
| 1     | __main__.py                   | Dynamic currency, "Transit lines" label                                               |
| 1     | publisher/html_report.py      | All hardcoded "CHF" → dynamic                                                         |
| 1     | notifier/email_notifier.py    | Dynamic currency in price display                                                     |
| 1     | notifier/ntfy_notifier.py     | Dynamic currency                                                                      |
| 1     | notifier/telegram_notifier.py | Dynamic currency                                                                      |
| 1     | notifier/discord_notifier.py  | Dynamic currency                                                                      |
| 1     | notifier/digest_builder.py    | "price"+"currency" keys                                                               |
| 1     | api/schemas.py                | Renamed ListingResponse.price_chf→price, +currency                                    |
| 1     | profiles/default.json         | Renamed budget keys                                                                   |
| 2     | config.py                     | +connector_class on SourceDefinition, ResolvedSource                                  |
| 2     | runner.py                     | _resolve_class + dynamic _build_scraper, removed _verify_flatfox_via_api              |
| 2     | scrapers/flatfox.py           | +verify_listings function                                                             |
| 2     | sources.json                  | FQN scraper_class values, tutti removed                                               |
| 3     | **locale.py** (NEW)           | Locale dataclass, LOCALE_CH, LOCALE_IL, get_locale, EMAIL_STRINGS                     |
| 3     | scorer.py                     | Locale-driven vegan scoring                                                           |
| 3     | scrapers/base.py              | +country field, locale-driven Accept-Language                                         |
| 3     | __main__.py                   | Localized status labels                                                               |
| 3     | notifier/email_notifier.py    | Localized text via get_email_strings                                                  |


---

## Summary


| Metric                  | Value                  |
| ----------------------- | ---------------------- |
| Files to modify         | 17                     |
| Files to create         | 1 (`locale.py`)        |
| Files read-only context | 23                     |
| Copy-paste files        | 2 (.txt)               |
| Total ACs               | 70                     |
| Validation gates        | 4 (3 per-WP + 1 final) |
| Execution model         | Serial, single session |


---

*Package prepared by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004-v6 | 2026-04-13*
