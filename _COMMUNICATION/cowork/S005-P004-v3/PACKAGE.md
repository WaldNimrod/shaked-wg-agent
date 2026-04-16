# S005-P004 — Codebase Internationalization

## Identity


| Field              | Value                                                         |
| ------------------ | ------------------------------------------------------------- |
| **Package ID**     | S005-P004                                                     |
| **Sprint**         | S005 — Israel Market Expansion                                |
| **Date**           | 2026-04-13                                                    |
| **Version**        | v3 — Cowork-adapted                                           |
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
You are the builder (Team 20) for the shaked-wg-agent project.
You are implementing S005-P004: Codebase Internationalization — 3 work packages, 70 acceptance criteria.

═══ ENVIRONMENT ═══

You work in the Cowork environment with FULL capabilities:
  • Shell (Bash): Ubuntu 22 with Python 3.10, grep, diff, pytest — USE THEM for verification
  • File Tools: Read, Write, Edit — for direct file access and modification
  • Python: Can execute scripts, run tests, import modules
  • TodoList: Track progress per-WP and per-AC

SOURCE FILES are in a mounted folder. The root path is:
  SOURCE_ROOT = mnt/S005-P004/assets

Directory structure:
  SOURCE_ROOT/src/shaked_wg_agent/           — Python source code (25 files)
  SOURCE_ROOT/src/shaked_wg_agent/scrapers/  — Scraper modules
  SOURCE_ROOT/src/shaked_wg_agent/notifier/  — Notification modules
  SOURCE_ROOT/src/shaked_wg_agent/api/       — API modules
  SOURCE_ROOT/src/shaked_wg_agent/publisher/ — HTML report
  SOURCE_ROOT/specs/                         — LOD400 specs + Mandates (6 files)
  SOURCE_ROOT/data/                          — sources.json, profiles/, cities/
  SOURCE_ROOT/tests/                         — Test files (7 files)

OUTPUT: Write all modified files to SOURCE_ROOT/output/ preserving directory structure.
  Example: Modified config.py → SOURCE_ROOT/output/src/shaked_wg_agent/config.py
  New files (locale.py) → SOURCE_ROOT/output/src/shaked_wg_agent/locale.py

═══ PROJECT ═══

shaked-wg-agent is a Python CLI application that scrapes Swiss WG (shared apartment) listings from multiple platforms (wgzimmer, flatfox, wg-gesucht), scores them by relevance for a specific user profile, and delivers results via CLI, HTML report, REST API, and notifications (email, Telegram, Discord, ntfy). Today the codebase is hardcoded for Switzerland. This package removes all Switzerland-specific hardcoding so the system can support Israel (and any future country) by adding only data.

═══ ARCHITECTURE — DATA FLOW ═══

  profiles/default.json → config.py (SearchProfile) → scorer.py → CLI / notifications
  sources.json → config.py (SourceDefinition → ResolvedSource) → runner.py → scrapers
  cities/basel.json → config.py (CityDefinition) → scrapers, runner, CLI

═══ EXECUTION RULES ═══

1. Linear execution: WP001 → WP002 → WP003. No skipping, no reordering.
2. Per-WP workflow:
   a. Read MANDATE file for scope + DO NOT list
   b. Read LOD400 spec for exact changes per file
   c. Read each target source file using Read tool
   d. Apply changes using Edit tool (targeted diffs preferred over full rewrites)
   e. Write modified file to OUTPUT directory
   f. Run grep verification commands in shell
   g. Mark WP complete, proceed to next
3. Verification gates: all grep checks must show zero hits before advancing.
4. Spec is law: LOD400 is authoritative. Mandate defines your scope.
5. Backward compatibility: keep .get("price_chf") fallback reads per LOD400 spec.
6. Tests: update assertions referencing renamed fields. Do not change test logic or add new tests.
7. No scope creep: if you find issues outside your current WP, note them — do not fix them.

═══ FILE ROLES (by WP) ═══

WP001 — Data Field Generalization (24 ACs):
  MODIFY: config.py, scrapers/base.py, scrapers/flatfox.py, scrapers/wg_gesucht.py,
          scrapers/wgzimmer_pw.py, scorer.py, __main__.py, publisher/html_report.py,
          notifier/email_notifier.py, ntfy_notifier.py, telegram_notifier.py,
          discord_notifier.py, notifier/digest_builder.py, api/schemas.py,
          data/profiles/default.json
  Key changes: price_chf→price, budget_min_chf→budget_min, +currency field, "Transit lines"

WP002 — Dynamic Scraper Registry (17 ACs):
  MODIFY: config.py, runner.py, scrapers/flatfox.py, data/sources.json
  Key changes: FQN class resolution via importlib, remove hardcoded mapping, extract flatfox verification, remove tutti

WP003 — Keyword/Label Locale (29 ACs):
  CREATE: locale.py
  MODIFY: scorer.py, scrapers/base.py, __main__.py, notifier/email_notifier.py
  Key changes: Locale dataclass (10 fields), locale-driven vegan scoring, +country field, localized status labels + email text
```

---

## Activation Prompt

> Paste this as the first message in the Cowork chat.

```
Execute S005-P004: Codebase Internationalization.
3 work packages, 70 acceptance criteria, strict linear order.

SOURCE_ROOT = "mnt/S005-P004/assets"

Create a TodoList with WP001, WP002, WP003 as top-level tasks, then begin.

══════════════════════════════════════════════
PHASE 1: WP001 — Data Field Generalization (24 ACs)
══════════════════════════════════════════════

Step 1 — Read scope:
  • Read SOURCE_ROOT/specs/MANDATE_S005-P004-WP001_TEAM20.md
  • Read SOURCE_ROOT/specs/LOD400_S005-P004-WP001.md

Step 2 — Implement (10 components, §2.1–§2.10):
  For each file listed in the mandate:
  a) Read the source file from SOURCE_ROOT/src/ or SOURCE_ROOT/data/
  b) Apply changes per LOD400 spec using Edit tool
  c) Write modified file to SOURCE_ROOT/output/ (preserving path structure)

Step 3 — Update test assertions:
  Read SOURCE_ROOT/tests/test_config.py, test_scorer.py, test_api.py, test_persistence.py, test_notifier.py
  Update any assertion referencing price_chf, budget_min_chf, budget_max_chf to use new field names
  Write updated test files to SOURCE_ROOT/output/tests/

Step 4 — Verification gate (run ALL in shell):
  grep -rn "price_chf" SOURCE_ROOT/output/src/ --include="*.py" | grep -v "\.get\("
  → Expected: zero hits (backward-compat .get() reads are allowed)

  grep -rn '"CHF"' SOURCE_ROOT/output/src/shaked_wg_agent/publisher/html_report.py
  → Expected: zero hits

  grep -n "Tram lines" SOURCE_ROOT/output/src/shaked_wg_agent/__main__.py
  → Expected: zero hits

  grep -n "budget_min_chf\|budget_max_chf" SOURCE_ROOT/output/data/profiles/default.json
  → Expected: zero hits

If any verification fails → fix and re-verify before proceeding.

══════════════════════════════════════════════
PHASE 2: WP002 — Dynamic Scraper Registry (17 ACs)
══════════════════════════════════════════════

Step 1 — Read scope:
  • Read SOURCE_ROOT/specs/MANDATE_S005-P004-WP002_TEAM20.md
  • Read SOURCE_ROOT/specs/LOD400_S005-P004-WP002.md

Step 2 — Implement (5 components, §2.1–§2.5):
  IMPORTANT: Start from WP001 output files (SOURCE_ROOT/output/), not original source.
  For config.py and flatfox.py, read from output/ since WP001 already modified them.
  For runner.py and sources.json, read from SOURCE_ROOT/src/ and SOURCE_ROOT/data/ (unmodified by WP001).

Step 3 — Verification gate:
  grep -n "mapping\s*=" SOURCE_ROOT/output/src/shaked_wg_agent/runner.py
  → Expected: zero hits

  grep -n "_verify_flatfox_via_api" SOURCE_ROOT/output/src/shaked_wg_agent/runner.py
  → Expected: zero hits

  python3 -c "import json; d=json.load(open('SOURCE_ROOT/output/data/sources.json')); print(len(d)); assert len(d)==3; assert all('.' in s['scraper_class'] for s in d); print('PASS')"
  → Expected: 3 entries, all FQN, no tutti

══════════════════════════════════════════════
PHASE 3: WP003 — Keyword/Label Locale (29 ACs)
══════════════════════════════════════════════

Step 1 — Read scope:
  • Read SOURCE_ROOT/specs/MANDATE_S005-P004-WP003_TEAM20.md
  • Read SOURCE_ROOT/specs/LOD400_S005-P004-WP003.md

Step 2 — Implement (6 components, §2.1–§2.6):
  CREATE locale.py (new file) → Write to SOURCE_ROOT/output/src/shaked_wg_agent/locale.py
  For scorer.py, base.py, __main__.py, email_notifier.py → read from output/ (already modified by WP001)

Step 3 — Verification gate:
  grep -n "_VEGAN_STRONG\|_VEGAN_PARTIAL\|_VEGAN_WEAK" SOURCE_ROOT/output/src/shaked_wg_agent/scorer.py
  → Expected: zero hits

  grep -n "de-CH" SOURCE_ROOT/output/src/shaked_wg_agent/scrapers/base.py
  → Expected: zero hits

  grep -n '"neue Angebote\|Preis nicht angegeben\|Generiert von"' SOURCE_ROOT/output/src/shaked_wg_agent/notifier/email_notifier.py
  → Expected: zero hits

  python3 -c "
  import sys; sys.path.insert(0, 'SOURCE_ROOT/output/src')
  from shaked_wg_agent.locale import Locale, get_locale
  import dataclasses
  fields = dataclasses.fields(Locale)
  assert len(fields) == 10, f'Expected 10 fields, got {len(fields)}'
  assert get_locale('CH').direction == 'ltr'
  assert get_locale('IL').direction == 'rtl'
  print('Locale validation PASS')
  "

══════════════════════════════════════════════
FINAL VERIFICATION
══════════════════════════════════════════════

Run comprehensive check:
  grep -rn "price_chf" SOURCE_ROOT/output/src/ --include="*.py" | grep -v "\.get\("
  grep -rn '"CHF"' SOURCE_ROOT/output/src/shaked_wg_agent/publisher/html_report.py
  grep -n "mapping\s*=" SOURCE_ROOT/output/src/shaked_wg_agent/runner.py
  grep -n "_VEGAN_STRONG" SOURCE_ROOT/output/src/shaked_wg_agent/scorer.py
  → ALL must return zero hits

Summarize: list all files written to output/, total ACs addressed per WP, and any issues encountered.

IRON RULES:
1. Linear execution: WP001 → WP002 → WP003
2. Gate discipline: all verifications must pass before next phase
3. Spec is law: LOD400 is authoritative, Mandate scopes your work
4. Use Edit tool for changes, Write for new files, shell for verification
5. Never paste complete file contents into chat — write files to output/
```

---

## Project Setup Checklist

Before launching the Cowork session:

- [ ] Create a Cowork project named `S005-P004-Internationalization`
- [ ] Mount the S005-P004-v3 folder as the workspace (ASCII-safe name, no special chars)
- [ ] Paste the Instructions block (above) into project Instructions
- [ ] Create a new chat session
- [ ] Paste the Activation Prompt (above) as the first message
- [ ] Output directory will be created by the agent at `SOURCE_ROOT/output/`

---

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


| File                  | Role                                        | WP  |
| --------------------- | ------------------------------------------- | --- |
| `__init__.py`         | read-only                                   | —   |
| `test_config.py`      | update assertions for renamed fields        | WP001 |
| `test_scorer.py`      | update assertions for renamed fields        | WP001 |
| `test_api.py`         | update assertions for renamed fields        | WP001 |
| `test_persistence.py` | read-only (no renamed field refs)           | —   |
| `test_integration.py` | update assertions for renamed fields        | WP001 |
| `test_notifier.py`    | update assertions for renamed fields        | WP001 |


### New file created by WP003


| File                        | Role       | WP    |
| --------------------------- | ---------- | ----- |
| `shaked_wg_agent/locale.py` | **create** | WP003 |


**Total: 41 files in assets + 1 new file created during execution**

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

## v1→v3 Changes

| Aspect | v1/v2 (Chat-Oriented) | v3 (Cowork-Adapted) |
|--------|----------------------|---------------------|
| Environment model | "Cannot run shell/Python" | "Full shell, Python, file tools — USE THEM" |
| File references | Relative names ("config.py") | Anchored to SOURCE_ROOT mount path |
| Output method | "Output complete file contents" | Write files to output/ directory using Edit/Write |
| Verification | Textual assertion descriptions | Actual shell commands with expected results |
| WP chaining | Files referenced independently | WP002/WP003 explicitly read from WP001 output |
| Test files | "read-only (must not break)" | "update assertions for renamed fields only" |
| Progress tracking | Implicit | Explicit TodoList per WP |
| Instructions size | ~65 lines (2800 tokens) | ~55 lines (~1800 tokens) |
| Activation Prompt size | ~175 lines (too long) | ~85 lines (within limits) |

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

*Package prepared by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004-v3 | 2026-04-13*
