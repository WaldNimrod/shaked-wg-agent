# S005-P005 — Data Source Expansion: reCAPTCHA Bypass + Facebook Parsers

## Identity


| Field              | Value                                                                |
| ------------------ | -------------------------------------------------------------------- |
| **Package ID**     | S005-P005                                                            |
| **Sprint**         | S005 — Data Source Expansion                                         |
| **Date**           | 2026-04-15                                                           |
| **Version**        | v1                                                                   |
| **Work Packages**  | WP001 (reCAPTCHA Bypass), WP002 (Facebook Manual Parser), WP003 (Facebook Email Parser) |
| **Total ACs**      | 87 (15 + 38 + 34)                                                   |
| **Authoring Team** | Team 110 (shaked_arch / Claude Code)                                 |
| **Authority**      | Team 00 (Nimrod)                                                     |
| **Track**          | A (pattern-following: LOD200 -> LOD400 direct)                       |
| **Depends On**     | S005-IL (Israeli city/profile/homeless already deployed)             |
| **Pre-Submit**     | AOS Package Validator — _pending_                                    |


## Purpose

**shaked-wg-agent** aggregates rental listings from multiple platforms. This package adds three capabilities:

1. **WP001 — wgzimmer.ch reliability** (15 ACs): Replace Playwright with Patchright (drop-in fork removing automation markers) and switch to a persistent browser profile. Restores ~20-40 Swiss WG listings/scan by improving reCAPTCHA v3 score from 0.1-0.3 (blocked) to 0.7-0.9 (passed).

2. **WP002 — Facebook manual parser** (38 ACs): Create a ManualFacebookScraper that reads copy-pasted Facebook group posts from a local JSON file, sends each post to an LLM (Claude/GPT) for structured Hebrew extraction, filters, strips PII, deduplicates, and outputs ScrapedListing entries. Introduces the `parsers/` module.

3. **WP003 — Facebook email parser** (34 ACs): Create an EmailFacebookScraper that reads Facebook group notification emails via IMAP, reuses WP002's LLM parser, and provides passive listing coverage (~30-60% of group posts) with zero legal risk.

After this package, `shaked-wg-agent` will have 3 new data sources: improved wgzimmer.ch, manual Facebook group parsing, and passive Facebook email notifications.

---

## Cowork Setup

### Copy-Paste Files

| File | Paste Into | Content |
|------|-----------|---------|
| **`S005-P005_INSTRUCTIONS.txt`** | Cowork project "Instructions" field | Agent identity, environment, architecture, file roles |
| **`S005-P005_ACTIVATION_PROMPT.txt`** | First chat message | Phase-by-phase execution, verification gates, iron rules |

### Setup Checklist

1. Create a Cowork project named `S005-P005-DataSourceExpansion`
2. Mount this folder (`S005-P005-v1`) as the workspace
3. Open `S005-P005_INSTRUCTIONS.txt` -> copy entire content -> paste into project Instructions
4. Create a new chat session
5. Open `S005-P005_ACTIVATION_PROMPT.txt` -> copy entire content -> paste as first message
6. Output directory will be created automatically by the activation prompt (`mkdir -p`)

---

## File Manifest

### Root — Copy-Paste Files (2 files)

| File | Content |
|------|---------|
| `S005-P005_INSTRUCTIONS.txt` | Exact text for Cowork project Instructions field |
| `S005-P005_ACTIVATION_PROMPT.txt` | Exact text for first Cowork chat message |

### assets/specs/ — Specifications and Mandates (6 files)


| File                                    | Role                                      | WP    |
| --------------------------------------- | ----------------------------------------- | ----- |
| `LOD400_S005-P005-WP001.md`            | Primary spec — reCAPTCHA Bypass           | WP001 |
| `LOD400_S005-P005-WP002.md`            | Primary spec — Facebook Manual Parser     | WP002 |
| `LOD400_S005-P005-WP003.md`            | Primary spec — Facebook Email Parser      | WP003 |
| `MANDATE_S005-P005-WP001_TEAM20.md`    | Builder mandate — scope, ACs, DO NOT      | WP001 |
| `MANDATE_S005-P005-WP002_TEAM20.md`    | Builder mandate — scope, ACs, DO NOT      | WP002 |
| `MANDATE_S005-P005-WP003_TEAM20.md`    | Builder mandate — scope, ACs, DO NOT      | WP003 |


### assets/src/ — Source Code (7 files, read-only reference)


| File                                       | Role      | Used By      |
| ------------------------------------------ | --------- | ------------ |
| `shaked_wg_agent/__init__.py`              | read-only | —            |
| `shaked_wg_agent/config.py`                | read-only | WP002, WP003 |
| `shaked_wg_agent/scrapers/__init__.py`     | read-only | —            |
| `shaked_wg_agent/scrapers/base.py`         | read-only | ALL WPs      |
| `shaked_wg_agent/scrapers/wgzimmer_pw.py`  | **modify** | WP001        |
| `shaked_wg_agent/scrapers/flatfox.py`      | read-only | WP002 ref    |
| `shaked_wg_agent/scrapers/homeless.py`     | read-only | WP002 ref    |


### assets/data/ — Data Files (3 files)


| File                              | Role                  | Used By      |
| --------------------------------- | --------------------- | ------------ |
| `sources.json`                    | read-only -> **modify** | WP002, WP003 |
| `cities/pardes-hanna-region.json` | read-only -> **modify** | WP002, WP003 |
| `profiles/pardes-hanna.json`      | read-only -> **modify** | WP002, WP003 |


### New files created during execution


| File                                              | Role       | WP    |
| ------------------------------------------------- | ---------- | ----- |
| `shaked_wg_agent/scrapers/wgzimmer_pw.py`        | **modify** | WP001 |
| `shaked_wg_agent/parsers/__init__.py`             | **create** | WP002 |
| `shaked_wg_agent/parsers/llm_listing_parser.py`  | **create** | WP002 |
| `shaked_wg_agent/scrapers/facebook_manual.py`     | **create** | WP002 |
| `data/facebook/pardes-hanna-posts.json`           | **create** | WP002 |
| `data/sources.json`                               | **modify** | WP002 |
| `data/cities/pardes-hanna-region.json`            | **modify** | WP002 |
| `data/profiles/pardes-hanna.json`                 | **modify** | WP002 |
| `tests/fixtures/hebrew_posts.json`                | **create** | WP002 |
| `tests/test_facebook_manual.py`                   | **create** | WP002 |
| `tests/test_llm_parser.py`                        | **create** | WP002 |
| `tests/test_facebook_manual_dedup.py`             | **create** | WP002 |
| `tests/test_facebook_manual_validation.py`        | **create** | WP002 |
| `tests/test_llm_parser_modes.py`                  | **create** | WP002 |
| `shaked_wg_agent/scrapers/facebook_email.py`      | **create** | WP003 |
| `data/facebook/processed_email_ids.json`          | **create** | WP003 |
| `data/sources.json`                               | **modify** | WP003 |
| `data/cities/pardes-hanna-region.json`            | **modify** | WP003 |
| `data/profiles/pardes-hanna.json`                 | **modify** | WP003 |
| `tests/fixtures/fb_email_single.eml`              | **create** | WP003 |
| `tests/fixtures/fb_email_digest.eml`              | **create** | WP003 |
| `tests/fixtures/fb_email_popular.eml`             | **create** | WP003 |
| `tests/test_facebook_email.py`                    | **create** | WP003 |


---

## Validation Criteria

### After Phase 1 (WP001 — reCAPTCHA Bypass)
- `wgzimmer_pw.py` imports from `patchright.sync_api` (not `playwright.sync_api`)
- `launch_persistent_context` used (not `browser.new_context`)
- `SHAKED_BROWSER_PROFILE_DIR` env var is read
- Parsing methods (`_parse_api_item`, `_dom_fallback`, etc.) are unchanged
- `fetch_listings()` wrapped in `try/except Exception`

### After Phase 2 (WP002 — Facebook Manual Parser)
- `parsers/llm_listing_parser.py` exports `parse_rental_post` and `check_llm_config`
- `ManualFacebookScraper` subclasses `BaseScraper`
- `facebook-manual` registered in sources.json, city JSON, profile JSON
- Test fixture has >=13 Hebrew posts with `post_id` and `text`

### After Phase 3 (WP003 — Facebook Email Parser)
- `EmailFacebookScraper` subclasses `BaseScraper`
- `facebook-email` registered in sources.json (alongside `facebook-manual` from WP002)
- 3 `.eml` fixture files exist
- WP002 entries preserved in all data files

### Final Comprehensive
- All Phase 1-3 verification gates pass simultaneously
- Data files contain both `facebook-manual` and `facebook-email` entries

---

## Expected Output

The agent writes new/modified files to `SOURCE_ROOT/output/` preserving directory structure:


| Phase | File                                                    | Description                              |
| ----- | ------------------------------------------------------- | ---------------------------------------- |
| 1     | `src/shaked_wg_agent/scrapers/wgzimmer_pw.py`          | Patchright + persistent context          |
| 2     | `src/shaked_wg_agent/parsers/__init__.py`               | Parser package init                      |
| 2     | `src/shaked_wg_agent/parsers/llm_listing_parser.py`     | LLM extraction module                    |
| 2     | `src/shaked_wg_agent/scrapers/facebook_manual.py`       | Manual FB group parser                   |
| 2     | `data/sources.json`                                     | +facebook-manual entry                   |
| 2     | `data/cities/pardes-hanna-region.json`                  | +facebook-manual in available_sources    |
| 2     | `data/profiles/pardes-hanna.json`                       | +facebook-manual in enabled_sources      |
| 2     | `data/facebook/pardes-hanna-posts.json`                 | Empty input template                     |
| 2     | `tests/fixtures/hebrew_posts.json`                      | >=13 Hebrew post fixtures                |
| 2     | `tests/test_*.py` (5 files)                             | Unit tests for parser + scraper          |
| 3     | `src/shaked_wg_agent/scrapers/facebook_email.py`        | Email notification parser                |
| 3     | `data/sources.json`                                     | +facebook-email entry                    |
| 3     | `data/cities/pardes-hanna-region.json`                  | +facebook-email in available_sources     |
| 3     | `data/profiles/pardes-hanna.json`                       | +facebook-email in enabled_sources       |
| 3     | `data/facebook/processed_email_ids.json`                | Empty state file                         |
| 3     | `tests/fixtures/*.eml` (3 files)                        | Email notification fixtures              |
| 3     | `tests/test_facebook_email.py`                          | Unit tests for email parser              |


---

## Summary


| Metric                  | Value                                                  |
| ----------------------- | ------------------------------------------------------ |
| Files to create         | ~17 (3 scrapers/parsers, 2 data templates, 4 fixtures, 6 test files, 2 package inits) |
| Files to modify         | 4 (wgzimmer_pw.py, sources.json, city JSON, profile JSON) |
| Files read-only context | 12                                                     |
| Copy-paste files        | 2 (.txt)                                               |
| Total ACs               | 87 (15 + 38 + 34)                                     |
| Validation gates        | 4 (3 per-WP + 1 final)                                |
| Execution model         | Serial, single session                                 |
| pip installs needed     | patchright, anthropic, openai, imapclient              |
| WP dependency           | WP003 depends on WP002 (parser module + data files)    |


---

*Package prepared by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P005-v1 | 2026-04-15*
