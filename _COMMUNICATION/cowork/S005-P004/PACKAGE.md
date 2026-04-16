# S005-P004 — Codebase Internationalization

## Identity


| Field              | Value                                                         |
| ------------------ | ------------------------------------------------------------- |
| **Package ID**     | S005-P004                                                     |
| **Sprint**         | S005 — Israel Market Expansion                                |
| **Date**           | 2026-04-13                                                    |
| **Work Packages**  | WP001 (Data Fields), WP002 (Scraper Registry), WP003 (Locale) |
| **Total ACs**      | 70 (24 + 17 + 29)                                             |
| **Authoring Team** | Team 110 (shaked_arch / Claude Code)                          |
| **Authority**      | Team 00 (Nimrod)                                              |
| **Validation**     | Team 190 — PASS WITH FINDINGS (v1.1.0), minors resolved       |


## Purpose

**shaked-wg-agent** is a Python CLI application that scrapes Swiss WG (shared apartment) listings from multiple platforms (wgzimmer, flatfox, wg-gesucht), scores them by relevance for a specific user profile, and delivers results via CLI, HTML report, REST API, and notifications (email, Telegram, Discord, ntfy).

Today the codebase is hardcoded for Switzerland: prices are `price_chf`, budgets are `budget_min_chf`, scraper selection is a hardcoded dict, vegan keywords are German-only, Accept-Language is `de-CH`, and notification text is German.

This package removes all Switzerland-specific hardcoding so the system can support Israel (and any future country) by adding only data — no code changes. Three work packages, executed in strict order.

---

## Instructions

> Paste this into the Cowork project "Instructions" field.

```
You are the builder (Team 20) for the shaked-wg-agent project. You are implementing S005-P004: Codebase Internationalization — 3 work packages, 70 acceptance criteria.

ENVIRONMENT: You work in an isolated environment. You can only read uploaded files and produce edited versions. You cannot run shell commands, execute Python, or access the repository. Output = complete file contents for every file you modify.

PROJECT: shaked-wg-agent is a Python CLI application that scrapes Swiss WG (shared apartment) listings from multiple platforms (wgzimmer, flatfox, wg-gesucht), scores them by relevance for a specific user profile, and delivers results via CLI, HTML report, REST API, and notifications (email, Telegram, Discord, ntfy). Today the codebase is hardcoded for Switzerland. This package removes all Switzerland-specific hardcoding so the system can support Israel (and any future country) by adding only data.

ARCHITECTURE — DATA FLOW:
  profiles/default.json → config.py (SearchProfile) → scorer.py → CLI / notifications
  sources.json → config.py (SourceDefinition → ResolvedSource) → runner.py → scrapers
  cities/basel.json → config.py (CityDefinition) → scrapers, runner, CLI

FILE CONTEXT — every uploaded file and its role:

- config.py (375 lines): Core configuration and data loading. Key elements: CityDefinition dataclass at line 40 (city_id, city_name, bounding_box, available_sources, country="CH" — NO currency field yet), SearchProfile dataclass at line 88 (budget_min_chf: int, budget_max_chf: int — legacy names), SourceDefinition dataclass at line 114 (source_id, label, base_url, scraper_class — no connector_class yet), ResolvedSource dataclass at line 125, _load_city() function, _load_profile() function with JSON loading, _load_sources() function. Role: modify in WP001 (field renames + currency) and WP002 (connector_class).

- scrapers/base.py (121 lines): Base scraping abstractions. Key elements: _DEFAULT_HEADERS dict at line 14 (hardcoded "Accept-Language": "de-CH,de;q=0.9,en;q=0.8"), ScrapedListing dataclass at line 28 (price_chf: int | None — legacy name, no currency or country fields), to_dict() method at line 48 (emits "price_chf" key), BaseScraper abstract class at line 76 (__init__(source_id, search_url, city)). Role: modify in WP001 (rename price_chf→price, +currency), WP003 (+country, locale-driven Accept-Language).

- scrapers/flatfox.py: FlatfoxScraper implementation. Constructs ScrapedListing with price_chf=... Role: modify in WP001 (price=, currency=), WP002 (+verify_listings function extracted from runner).

- scrapers/wg_gesucht.py: WgGesuchtScraper implementation. Constructs ScrapedListing with price_chf=... Role: modify in WP001 (price=, currency=).

- scrapers/wgzimmer_pw.py: WgzimmerPlaywrightScraper using Playwright. Constructs ScrapedListing with price_chf=... Role: modify in WP001 (price=, currency=).

- runner.py (250 lines): Orchestration engine. Key elements: _verify_flatfox_via_api function at line 28 (flatfox pin API verification), _build_scraper function at line 113 (HARDCODED mapping = {"wgzimmer": WgzimmerPlaywrightScraper, "wg-gesucht": WgGesuchtScraper, "flatfox": FlatfoxScraper}). Role: modify in WP002 (dynamic class resolution, remove verification function).

- scorer.py (162 lines): Listing relevance scoring. Key elements: _VEGAN_STRONG/_PARTIAL/_WEAK constants at lines 21-23 (all German keywords), _vegan_score(signal) function at line 26 (returns 0-35, German-only), _budget_ok function (uses profile.budget_min_chf), score_listing function (reads listing["price_chf"]). Role: modify in WP001 (field renames), WP003 (locale-driven vegan keywords).

- __main__.py (195 lines): CLI entry point. Key elements: line 81 f"CHF {budget_min_chf}–{budget_max_chf}", line 84 "Tram lines", line 134 table column "Tram", line 150 f"CHF {price_chf}", status labels "neu","interessant",etc at lines 138-144. Role: modify in WP001 (dynamic currency, "Transit lines"), WP003 (localized status labels).

- publisher/html_report.py (710 lines): HTML report generator. Hardcoded "CHF" at lines 184, 266, 621-623. Role: modify in WP001 (dynamic currency).

- notifier/email_notifier.py (98 lines): Email notifications. Key elements: line 35 "neue Angebote", line 41 "Preis nicht angegeben", line 52 "Generiert von", line 71 subject "neue Angebote", hardcoded "CHF" in price display. Role: modify in WP001 (dynamic currency), WP003 (localized text via get_email_strings).

- notifier/ntfy_notifier.py, telegram_notifier.py, discord_notifier.py: Notification channels with hardcoded "CHF". Role: modify in WP001 (dynamic currency).

- notifier/digest_builder.py: Builds notification digests. Line 31 emits "price_chf" key. Role: modify in WP001 ("price"+"currency" keys).

- api/schemas.py (128 lines): Pydantic API models. ListingResponse.price_chf at line 74. Role: modify in WP001 (rename + currency).

- sources.json (92 lines): 4 source entries with short scraper_class names ("FlatfoxScraper" etc.), tutti entry present (disabled). Role: modify in WP002 (FQN names, remove tutti).

- profiles/default.json (26 lines): User search profile. budget_min_chf: 200, budget_max_chf: 1000. Role: modify in WP001 (rename keys).

- cities/basel.json: Basel city definition with country="CH". Read-only context.

- LOD400_S005-P004-WP001.md: Full executable spec for WP001 — Data Field Generalization (24 ACs). Read-only guidance.
- LOD400_S005-P004-WP002.md: Full executable spec for WP002 — Dynamic Scraper Registry (17 ACs). Read-only guidance.
- LOD400_S005-P004-WP003.md: Full executable spec for WP003 — Keyword/Label Locale (29 ACs). Read-only guidance.
- MANDATE_S005-P004-WP001_TEAM20.md: Builder mandate — scope, ACs, DO NOT list. Read-only guidance.
- MANDATE_S005-P004-WP002_TEAM20.md: Builder mandate — scope, ACs, DO NOT list. Read-only guidance.
- MANDATE_S005-P004-WP003_TEAM20.md: Builder mandate — scope, ACs, DO NOT list. Read-only guidance.

- Test files (test_config.py, test_scorer.py, test_api.py, test_persistence.py, test_integration.py, test_notifier.py): Read-only. Must not break — review assertions that reference old field names and update them.

DEPENDENCIES BETWEEN WORK PACKAGES:
WP001 renames price_chf→price, budget_min_chf→budget_min across the codebase. WP002 consumes the renamed fields and changes scraper instantiation to FQN-based. WP003 consumes both the renamed fields and the new scraper registry to add locale-driven keywords, Accept-Language, status labels, and email text. Therefore: strict linear execution WP001 → WP002 → WP003 is mandatory.

BEHAVIORAL RULES:
- Output format: provide COMPLETE content of every modified file per phase
- Scope: only modify files listed as "modify" in the file context above for the current WP
- Backward compatibility: keep .get("price_chf") fallback reads where specified in the LOD400 spec
- Tests: review test files and update assertions that reference renamed fields
- No scope creep: if you find issues outside your current WP scope, note them — do not fix them
```

---

## Activation Prompt

> Paste this as the first message in the Cowork chat.

```
Execute S005-P004: 3 work packages in strict linear order.

FILE INDEX (uploaded to this project):
  Specs:    LOD400_S005-P004-WP001.md, LOD400_S005-P004-WP002.md, LOD400_S005-P004-WP003.md
  Mandates: MANDATE_S005-P004-WP001_TEAM20.md, MANDATE_S005-P004-WP002_TEAM20.md, MANDATE_S005-P004-WP003_TEAM20.md
  Source:   All .py files from shaked_wg_agent/ (see Instructions for file context)
  Data:     sources.json, profiles/default.json, cities/basel.json
  Tests:    test_config.py, test_scorer.py, test_api.py, test_persistence.py, test_integration.py, test_notifier.py

--- PHASE 1: WP001 — Data Field Generalization (24 ACs) ---

1. Read MANDATE_S005-P004-WP001_TEAM20.md for scope + DO NOT list
2. Read LOD400_S005-P004-WP001.md §2.1–§2.10 for exact changes per file
3. Implement all 10 components. Key changes: price_chf→price, budget_min_chf→budget_min, +currency field, "Transit lines"
4. Review test files — update assertions referencing old field names

VERIFY before proceeding:
  ✓ No field named price_chf, budget_min_chf, or budget_max_chf in any .py file (backward-compat .get() reads allowed)
  ✓ No hardcoded "CHF" in html_report.py
  ✓ No "Tram lines" in __main__.py
  ✓ profiles/default.json uses "budget_min"/"budget_max" keys

--- PHASE 2: WP002 — Dynamic Scraper Registry (17 ACs) ---

1. Read MANDATE_S005-P004-WP002_TEAM20.md for scope + DO NOT list
2. Read LOD400_S005-P004-WP002.md §2.1–§2.5 for exact changes per file
3. Implement all 5 components. Key changes: FQN class resolution via importlib, remove hardcoded mapping, extract flatfox verification, remove tutti

VERIFY before proceeding:
  ✓ runner.py has no "mapping" dict and no _verify_flatfox_via_api function
  ✓ flatfox.py exports verify_listings(listings, city)
  ✓ sources.json: 3 entries (no tutti), all FQN scraper_class containing "."

--- PHASE 3: WP003 — Keyword/Label Locale Generalization (29 ACs) ---

1. Read MANDATE_S005-P004-WP003_TEAM20.md for scope + DO NOT list
2. Read LOD400_S005-P004-WP003.md §2.1–§2.6 for exact changes per file
3. Implement all 6 components. Key changes: new locale.py (frozen Locale, 10 fields), locale-driven vegan scoring, +country field, locale Accept-Language, localized status labels + email text

VERIFY before proceeding:
  ✓ Locale dataclass has exactly 10 fields; EMAIL_STRINGS is module-level dict, NOT Locale fields
  ✓ scorer.py has no _VEGAN_STRONG/_PARTIAL/_WEAK constants
  ✓ base.py _DEFAULT_HEADERS has no "de-CH"
  ✓ email_notifier.py has no hardcoded German strings

--- FINAL VERIFICATION ---

  ✓ ScrapedListing has: price, currency, country — no price_chf
  ✓ sources.json: 3 FQN entries, no tutti
  ✓ Locale: exactly 10 fields
  ✓ All test assertions compatible with new field names

IRON RULES:
1. Linear execution: WP001 → WP002 → WP003. No skipping, no reordering.
2. Gate discipline: all verifications must pass before starting next phase.
3. Spec is law: LOD400 is authoritative. Mandate scopes your work.
4. Output: COMPLETE content of every modified file per phase. Summary at end.
```

## File Manifest

### specs/ — Specifications and Mandates (6 files)


| File                                | Role                                     | WP    |
| ----------------------------------- | ---------------------------------------- | ----- |
| `LOD400_S005-P004-WP001.md`         | Primary spec — Data Field Generalization | WP001 |
| `LOD400_S005-P004-WP002.md`         | Primary spec — Dynamic Scraper Registry  | WP002 |
| `LOD400_S005-P004-WP003.md`         | Primary spec — Keyword/Label Locale      | WP003 |
| `MANDATE_S005-P004-WP001_TEAM20.md` | Builder mandate — scope, ACs, DO NOT     | WP001 |
| `MANDATE_S005-P004-WP002_TEAM20.md` | Builder mandate — scope, ACs, DO NOT     | WP002 |
| `MANDATE_S005-P004-WP003_TEAM20.md` | Builder mandate — scope, ACs, DO NOT     | WP003 |


### src/ — Source Code (25 files)


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


### data/ — Data Files (3 files)


| File                    | Role       | WP    |
| ----------------------- | ---------- | ----- |
| `sources.json`          | **modify** | WP002 |
| `profiles/default.json` | **modify** | WP001 |
| `cities/basel.json`     | read-only  | —     |


### tests/ — Test Files (7 files)


| File                  | Role                       | WP  |
| --------------------- | -------------------------- | --- |
| `__init__.py`         | read-only                  | —   |
| `test_config.py`      | read-only (must not break) | —   |
| `test_scorer.py`      | read-only (must not break) | —   |
| `test_api.py`         | read-only (must not break) | —   |
| `test_persistence.py` | read-only (must not break) | —   |
| `test_integration.py` | read-only (must not break) | —   |
| `test_notifier.py`    | read-only (must not break) | —   |


### New file created by WP003


| File                        | Role       | WP    |
| --------------------------- | ---------- | ----- |
| `shaked_wg_agent/locale.py` | **create** | WP003 |


**Total: 41 files in assets + 1 new file created during execution**

---

## Validation Criteria

### After Phase 1 (WP001 — Data Field Generalization)

- CityDefinition has field `currency: str` with default `"CHF"`
- ScrapedListing has field `price: int | None` and `currency: str = "CHF"` — no `price_chf` field
- ScrapedListing.to_dict() returns keys `"price"` and `"currency"`, not `"price_chf"`
- SearchProfile has fields `budget_min: int` and `budget_max: int` — no `_chf` suffixed fields
- _load_profile has backward-compat fallback: reads `"budget_min_chf"` from JSON as `budget_min`
- No hardcoded `"CHF"` string in html_report.py
- No `"Tram lines"` string in **main**.py
- profiles/default.json has keys `"budget_min"` and `"budget_max"`
- All test assertions updated for renamed fields

### After Phase 2 (WP002 — Dynamic Scraper Registry)

- SourceDefinition and ResolvedSource both have `connector_class: str | None = None`
- runner.py has no hardcoded mapping dict or variable `mapping`
- runner.py has no function `_verify_flatfox_via_api`
- flatfox.py has a `verify_listings(listings, city)` function
- sources.json has exactly 3 entries (tutti removed), all with FQN `scraper_class` containing `.`

### After Phase 3 (WP003 — Locale Generalization)

- locale.py exists with frozen Locale dataclass having exactly 10 fields
- scorer.py has no `_VEGAN_STRONG`, `_VEGAN_PARTIAL`, or `_VEGAN_WEAK` constants
- `_vegan_score` has signature `(signal, country="CH")`
- base.py `_DEFAULT_HEADERS` has no `"de-CH"` string
- ScrapedListing has `country: str = "CH"` field
- email_notifier.py has no hardcoded `"neue Angebote"`, `"Preis nicht angegeben"`, `"Generiert von"`
- `EMAIL_STRINGS` is a module-level dict in locale.py, NOT Locale dataclass fields

### Final Comprehensive

- No `price_chf`, `budget_min_chf`, `budget_max_chf` as field definitions in any .py file
- ScrapedListing has: `price`, `currency`, `country` — no `price_chf`
- sources.json: 3 entries, all FQN, no tutti
- Locale has exactly 10 fields
- All test assertions compatible with new field names

---

## Expected Output

The agent produces the complete content of these files:


| Phase | File                          | Changes                                                                               |
| ----- | ----------------------------- | ------------------------------------------------------------------------------------- |
| 1     | config.py                     | +CityDefinition.currency, renamed SearchProfile budget fields, backward-compat loader |
| 1     | scrapers/base.py              | Renamed price_chf→price, +currency field, updated to_dict                             |
| 1     | scrapers/flatfox.py           | ScrapedListing construction with price=, currency=                                    |
| 1     | scrapers/wg_gesucht.py        | ScrapedListing construction with price=, currency=                                    |
| 1     | scrapers/wgzimmer_pw.py       | ScrapedListing construction with price=, currency=                                    |
| 1     | scorer.py                     | Updated _budget_ok + score_listing field access                                       |
| 1     | **main**.py                   | Dynamic currency, "Transit lines" label                                               |
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
| 3     | **main**.py                   | Localized status labels                                                               |
| 3     | notifier/email_notifier.py    | Localized text via get_email_strings                                                  |


---

## Summary


| Metric                  | Value                  |
| ----------------------- | ---------------------- |
| Files to modify         | 17                     |
| Files to create         | 1 (`locale.py`)        |
| Files read-only context | 23                     |
| Total ACs               | 70                     |
| Validation gates        | 4 (3 per-WP + 1 final) |
| Execution model         | Serial, single session |


---

*Package prepared by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004 | 2026-04-13*