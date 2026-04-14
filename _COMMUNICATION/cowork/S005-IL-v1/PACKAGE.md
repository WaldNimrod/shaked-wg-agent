# S005-IL — Israel Deployment: First City, Scraper, Profile

## Identity


| Field              | Value                                                                |
| ------------------ | -------------------------------------------------------------------- |
| **Package ID**     | S005-IL                                                              |
| **Sprint**         | S005 — Israel Market Expansion                                       |
| **Date**           | 2026-04-14                                                           |
| **Version**        | v1                                                                   |
| **Work Packages**  | WP001 (City Definition), WP002 (Homeless Scraper), WP003 (Profile + Sources) |
| **Total ACs**      | 42 (12 + 15 + 15)                                                   |
| **Authoring Team** | Team 110 (shaked_arch / Claude Code)                                 |
| **Authority**      | Team 00 (Nimrod)                                                     |
| **Track**          | A (pattern-following: LOD200 → LOD400 direct)                        |
| **Depends On**     | S005-P004 (internationalization — already integrated)                |
| **Pre-Submit**     | AOS Package Validator v1.2 — 98.1% PASS, 0 CRITICAL (11 checks)     |


## Purpose

**shaked-wg-agent** was recently internationalized (S005-P004) — all fields are currency-agnostic, locale-aware, and support `country="IL"`. This package creates the first Israeli deployment: a Pardes Hanna region city definition, a Homeless.co.il rental scraper, and an Israeli search profile with source registration.

After this package, running `shaked-wg-agent --profile pardes-hanna` will scrape Israeli rental listings from homeless.co.il, score them, and produce results — a fully operational Israeli system.

**Strategic context:**
- Decision D3: Pardes Hanna region as first Israeli target area
- Decision D4: Yad2 direct scraping declined — Homeless.co.il is the entry point
- Decision D2: All rental types (not just WG/shared apartments)

---

## Cowork Setup

### Copy-Paste Files

| File | Paste Into | Content |
|------|-----------|---------|
| **`S005-IL_INSTRUCTIONS.txt`** | Cowork project "Instructions" field | Agent identity, environment, project architecture, file roles |
| **`S005-IL_ACTIVATION_PROMPT.txt`** | First chat message | Phase-by-phase execution, verification gates, iron rules |

### Setup Checklist

1. Create a Cowork project named `S005-IL-Israel-Deployment`
2. Mount this folder (`S005-IL-v1`) as the workspace
3. Open `S005-IL_INSTRUCTIONS.txt` → copy entire content → paste into project Instructions
4. Create a new chat session
5. Open `S005-IL_ACTIVATION_PROMPT.txt` → copy entire content → paste as first message
6. Output directory will be created automatically by the activation prompt (`mkdir -p`)

---

## File Manifest

### Root — Copy-Paste Files (2 files)

| File | Content |
|------|---------|
| `S005-IL_INSTRUCTIONS.txt` | Exact text for Cowork project Instructions field |
| `S005-IL_ACTIVATION_PROMPT.txt` | Exact text for first Cowork chat message |

### assets/specs/ — Specifications and Mandates (6 files)


| File                                | Role                                     | WP    |
| ----------------------------------- | ---------------------------------------- | ----- |
| `LOD400_S005-IL-WP001.md`          | Primary spec — City Definition           | WP001 |
| `LOD400_S005-IL-WP002.md`          | Primary spec — Homeless.co.il Scraper    | WP002 |
| `LOD400_S005-IL-WP003.md`          | Primary spec — Profile + Sources         | WP003 |
| `MANDATE_S005-IL-WP001_TEAM20.md`  | Builder mandate — scope, ACs, DO NOT     | WP001 |
| `MANDATE_S005-IL-WP002_TEAM20.md`  | Builder mandate — scope, ACs, DO NOT     | WP002 |
| `MANDATE_S005-IL-WP003_TEAM20.md`  | Builder mandate — scope, ACs, DO NOT     | WP003 |


### assets/src/ — Source Code (9 files, all read-only reference)


| File                                       | Role      | Used By   |
| ------------------------------------------ | --------- | --------- |
| `shaked_wg_agent/__init__.py`              | read-only | —         |
| `shaked_wg_agent/__main__.py`              | read-only | —         |
| `shaked_wg_agent/config.py`                | read-only | WP001 ref |
| `shaked_wg_agent/locale.py`                | read-only | WP002 ref |
| `shaked_wg_agent/runner.py`                | read-only | WP003 ref |
| `shaked_wg_agent/scorer.py`                | read-only | WP003 ref |
| `shaked_wg_agent/scrapers/__init__.py`     | read-only | —         |
| `shaked_wg_agent/scrapers/base.py`         | read-only | WP002 ref |
| `shaked_wg_agent/scrapers/flatfox.py`      | read-only | WP002 ref |
| `shaked_wg_agent/scrapers/wgzimmer_pw.py`  | read-only | WP002 ref (Playwright pattern) |


### assets/data/ — Data Files (3 files)


| File                    | Role      | Used By   |
| ----------------------- | --------- | --------- |
| `cities/basel.json`     | read-only | WP001 ref |
| `profiles/default.json` | read-only | WP003 ref |
| `sources.json`          | read-only → **modify** | WP003 |


### assets/tests/ — Test Files (1 file)


| File              | Role      | Used By   |
| ----------------- | --------- | --------- |
| `test_config.py`  | read-only | WP001 ref |


### New files created during execution


| File                                        | Role       | WP    |
| ------------------------------------------- | ---------- | ----- |
| `data/cities/pardes-hanna-region.json`      | **create** | WP001 |
| `shaked_wg_agent/scrapers/homeless.py`      | **create** | WP002 |
| `data/sources.json`                         | **modify** | WP003 |
| `data/profiles/pardes-hanna.json`           | **create** | WP003 |


**Total: 21 files in assets + 2 copy-paste files + 4 output files created during execution**

---

## Validation Criteria

### After Phase 1 (WP001 — City Definition)
- `pardes-hanna-region.json` is valid JSON
- `city_id == "pardes-hanna-region"`, `country == "IL"`, `currency == "ILS"`
- Bounding box: west=34.87, east=35.00, south=32.42, north=32.60
- `zip_filter == []`, `available_sources` includes `"homeless"`

### After Phase 2 (WP002 — Homeless Scraper)
- `homeless.py` exists, `HomelessScraper` subclasses `BaseScraper`
- `fetch_listings()` method exists and returns `list[ScrapedListing]`
- Scraper uses `self._get()` and `self._soup()` (inherited helpers)
- No Playwright dependency
- Can be imported without error

### After Phase 3 (WP003 — Profile + Sources)
- `sources.json` has 4 entries (3 Swiss + 1 homeless)
- `homeless` entry has FQN `scraper_class` and `pardes-hanna-region` in `city_params`
- `pardes-hanna.json` profile has `city_id="pardes-hanna-region"`, ILS budget, `enabled_sources=["homeless"]`
- `language_policy.primary_listing_language == "he"`

### Final Comprehensive
- All Phase 1–3 verification gates pass simultaneously
- City + scraper + sources + profile form a complete pipeline

---

## Expected Output

The agent writes new/modified files to `SOURCE_ROOT/output/` preserving directory structure:


| Phase | File                                         | Description                                    |
| ----- | -------------------------------------------- | ---------------------------------------------- |
| 1     | `data/cities/pardes-hanna-region.json`       | Israeli city definition, IL/ILS, bounding box  |
| 2     | `src/shaked_wg_agent/scrapers/homeless.py`   | Homeless.co.il HTML scraper, BaseScraper subclass |
| 3     | `data/sources.json`                          | 4 entries (3 Swiss + homeless), FQN classes     |
| 3     | `data/profiles/pardes-hanna.json`            | Israeli search profile, ILS budget, Hebrew     |


---

## Summary


| Metric                  | Value                          |
| ----------------------- | ------------------------------ |
| Files to create         | 3 (city, scraper, profile)     |
| Files to modify         | 1 (sources.json)               |
| Files read-only context | 18                             |
| Copy-paste files        | 2 (.txt)                       |
| Total ACs               | 42                             |
| Validation gates        | 4 (3 per-WP + 1 final)        |
| Execution model         | Serial, single session         |
| Live HTTP required      | Yes (WP002 fetches homeless.co.il) |


---

*Package prepared by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-IL-v1 | 2026-04-14*
