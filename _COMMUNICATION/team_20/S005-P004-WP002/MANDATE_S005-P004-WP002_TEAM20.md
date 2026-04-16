# Mandate — S005-P004-WP002 | Team 20 (Builder) | L2.5 Phase 4C

**Issued by:** Team 110 (shaked_arch / Claude Code)
**Authority:** Team 00 (Nimrod)
**Date:** 2026-04-12
**Execution order:** 2 of 3 (AFTER WP001)

---

## Context

- **Work Package:** S005-P004-WP002 — Dynamic Scraper Registry
- **LOD400 spec:** `_aos/work_packages/S005-P004-WP002/LOD400_S005-P004-WP002.md` (v1.1.0)
- **Your scope:** Replace hardcoded scraper mapping in `runner.py` with FQN-based dynamic class resolution from `sources.json`. Add `connector_class` field to SourceDefinition/ResolvedSource. Extract flatfox verification from runner to flatfox module. Remove tutti entry from sources.json.
- **Prerequisite:** WP001 must be complete and validated. Field renames (`price`, `currency`, `budget_min`, `budget_max`) are already in place.

## Inputs (read before implementing)

| # | File | Purpose |
|---|------|---------|
| 1 | `_aos/work_packages/S005-P004-WP002/LOD400_S005-P004-WP002.md` | **Primary spec — follow exactly** |
| 2 | `shaked_wg_agent/config.py` | SourceDefinition (§2.1), ResolvedSource (§2.2) |
| 3 | `shaked_wg_agent/runner.py` | _build_scraper (§2.3), _verify_flatfox_via_api (§2.4) |
| 4 | `shaked_wg_agent/scrapers/base.py` | BaseScraper — for issubclass validation |
| 5 | `shaked_wg_agent/scrapers/flatfox.py` | Target for verify_listings extraction (§2.4) |
| 6 | `data/sources.json` | FQN update + tutti removal (§2.5) |

## Deliverables

| # | File | Change |
|---|------|--------|
| 1 | `shaked_wg_agent/config.py` | Add `connector_class` to SourceDefinition + ResolvedSource |
| 2 | `shaked_wg_agent/runner.py` | Replace `_build_scraper` + remove `_verify_flatfox_via_api` |
| 3 | `shaked_wg_agent/scrapers/flatfox.py` | Add `verify_listings()` function |
| 4 | `data/sources.json` | Update to FQN class names + remove tutti entry |

## Acceptance Criteria (your scope — all 17)

| AC | Description | Verification |
|----|-------------|--------------|
| AC-01 | `SourceDefinition` has `connector_class: str | None` defaulting to `None` | Unit test |
| AC-02 | `_load_sources()` with JSON `"connector_class": "some.Module.Class"` parses correctly | Unit test |
| AC-03 | `_load_sources()` without `"connector_class"` key returns `connector_class is None` | Unit test |
| AC-04 | `ResolvedSource` has `connector_class: str | None` defaulting to `None` | Unit test |
| AC-05 | `ResolvedSource` passes through `connector_class` from `SourceDefinition` | Unit test |
| AC-06 | `_resolve_class("shaked_wg_agent.scrapers.flatfox.FlatfoxScraper")` returns FlatfoxScraper | Unit test |
| AC-07 | `_resolve_class("nonexistent.module.SomeClass")` raises `ImportError` | Unit test |
| AC-08 | `_resolve_class` with non-BaseScraper subclass raises `TypeError` | Unit test |
| AC-09 | `_build_scraper()` with `connector_class` set uses `connector_class` over `scraper_class` | Unit test |
| AC-10 | `_build_scraper()` with `connector_class=None` uses `scraper_class` | Unit test |
| AC-11 | `grep -n "mapping\s*=" shaked_wg_agent/runner.py` = zero hits | grep check |
| AC-12 | `grep -n "_verify_flatfox_via_api" shaked_wg_agent/runner.py` = zero hits | grep check |
| AC-13 | `shaked_wg_agent/scrapers/flatfox.py` exports `verify_listings(listings, city)` | Import test |
| AC-14 | Flatfox verification behavior identical after extraction | Integration test |
| AC-15 | All `sources.json` entries have FQN `scraper_class` (contain `"."`). Tutti entry removed. | File check |
| AC-16 | Each FQN in `sources.json` resolves via `_resolve_class()` without error | Integration test |
| AC-17 | `pytest tests/ -v` exits 0 | Test run |

## DO NOT

- Implement Yad2 connector or any new scraper
- Build a generic post-scrape hook framework (YAGNI — only flatfox has verification)
- Add FQN schema-level validation to sources.json (runtime resolution is sufficient)
- Cache resolved classes (scan frequency is 3x/day — overhead negligible)
- Modify ScrapedListing fields (WP001 scope, already done)
- Modify scorer or locale logic (WP003 scope)
- Add new scraper modules
- Modify any notifier or HTML report files
- Make design decisions not covered by the LOD400 spec
- Modify files outside your listed deliverables

---

*Mandate issued by Team 110 (shaked_arch / Claude Code) on authority of Team 00 | shaked-wg-agent | S005-P004-WP002 | 2026-04-12*
