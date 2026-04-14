# Mandate — S005-P004-WP001 | Team 20 (Builder) | L2.5 Phase 4C

**Issued by:** Team 110 (shaked_arch / Claude Code)
**Authority:** Team 00 (Nimrod)
**Date:** 2026-04-12
**Execution order:** 1 of 3 (FIRST)

---

## Context

- **Work Package:** S005-P004-WP001 — Data Field Generalization
- **LOD400 spec:** `specs/LOD400_S005-P004-WP001.md` (v1.1.0)
- **Your scope:** Rename CHF-specific fields to currency-neutral names across the entire codebase. Add `currency` field to CityDefinition, ScrapedListing, and API schema. Remove all hardcoded "CHF" display strings from consumer rendering code.

## Inputs (read before implementing)

| # | File | Purpose |
|---|------|---------|
| 1 | `specs/LOD400_S005-P004-WP001.md` | **Primary spec — follow exactly** |
| 2 | `shaked_wg_agent/config.py` | CityDefinition (§2.1), SearchProfile (§2.3) |
| 3 | `shaked_wg_agent/scrapers/base.py` | ScrapedListing (§2.2) |
| 4 | `shaked_wg_agent/scorer.py` | _budget_ok, score_listing (§2.4) |
| 5 | `shaked_wg_agent/__main__.py` | CLI display (§2.5) |
| 6 | `shaked_wg_agent/publisher/html_report.py` | HTML report (§2.6) |
| 7 | `shaked_wg_agent/notifier/email_notifier.py` | Email notifier (§2.7) |
| 8 | `shaked_wg_agent/notifier/ntfy_notifier.py` | Ntfy notifier (§2.7) |
| 9 | `shaked_wg_agent/notifier/telegram_notifier.py` | Telegram notifier (§2.7) |
| 10 | `shaked_wg_agent/notifier/discord_notifier.py` | Discord notifier (§2.7) |
| 11 | `shaked_wg_agent/notifier/digest_builder.py` | Digest builder (§2.7) |
| 12 | `shaked_wg_agent/api/schemas.py` | API schema (§2.8) |
| 13 | `shaked_wg_agent/scrapers/flatfox.py` | Scraper — set currency (§2.2) |
| 14 | `shaked_wg_agent/scrapers/wg_gesucht.py` | Scraper — set currency (§2.2) |
| 15 | `shaked_wg_agent/scrapers/wgzimmer_pw.py` | Scraper — set currency (§2.2) |
| 16 | `data/profiles/default.json` | Profile JSON (§2.9) |

## Deliverables

All files listed in the **Inputs** table above (modified in-place). No new files created.

## Acceptance Criteria (your scope — all 24)

| AC | Description | Verification |
|----|-------------|--------------|
| AC-01 | `CityDefinition` has `currency: str` defaulting to `"CHF"` | Unit test |
| AC-02 | `_load_city("basel")` returns `currency="CHF"` without JSON change | Unit test |
| AC-03 | `ScrapedListing` has `price: int | None` and `currency: str = "CHF"`. No `price_chf` field. | Unit test |
| AC-04 | `ScrapedListing.to_dict()` emits `"price"` and `"currency"` keys, not `"price_chf"` | Unit test |
| AC-05 | All 3 active scrapers construct `ScrapedListing` with `currency=city.currency` | Code review |
| AC-06 | `SearchProfile` has `budget_min: int` and `budget_max: int`. No `_chf` suffixed fields. | Unit test |
| AC-07 | `_load_profile("default")` with old key `"budget_min_chf"` returns correct `budget_min` | Unit test |
| AC-08 | `_load_profile("default")` with new key `"budget_min"` returns correct `budget_min` | Unit test |
| AC-09 | `_budget_ok(price=780, profile)` with `budget_min=400, budget_max=950` returns `True` | Unit test |
| AC-10 | `score_listing()` reads `listing["price_chf"]` (backward-compat fallback) correctly | Unit test |
| AC-11 | `score_listing()` reads `listing["price"]` (new format) correctly | Unit test |
| AC-12 | CLI displays `"{currency} {budget_min}-{budget_max}"` with dynamic currency | Integration |
| AC-13 | CLI displays `"Transit lines"` (not `"Tram lines"`) | grep check |
| AC-14 | CLI price column uses `listing["currency"]`, not hardcoded | Code review |
| AC-15 | `grep -i '"CHF"' shaked_wg_agent/publisher/html_report.py` = zero hits | grep check |
| AC-16 | HTML report listing table uses `listing["currency"]` before price | Code review |
| AC-17 | HTML report modal uses `listing["currency"]` before price | Code review |
| AC-18 | `digest_builder.py` outputs `"price"` + `"currency"` keys, not `"price_chf"` | Unit test |
| AC-19 | All 4 notifiers use `listing.get("currency", "CHF")` | grep check |
| AC-20 | `ListingResponse` has `price: int | None` + `currency: str = "CHF"`. No `price_chf`. | Unit test |
| AC-21 | `data/profiles/default.json` has `"budget_min"` and `"budget_max"` keys | File check |
| AC-22 | No field definition/assignment uses `price_chf`, `budget_min_chf`, `budget_max_chf`. Backward-compat `.get()` reads allowed. | grep check |
| AC-23 | No hardcoded `"CHF"` in consumer rendering code. Dataclass defaults and locale constants allowed. | grep check |
| AC-24 | `pytest tests/ -v` exits 0 | Test run |

## DO NOT

- Create new files (all changes are modifications to existing files)
- Implement currency conversion logic
- Create mixed-currency table/report rendering
- Implement RTL rendering (WP004 scope)
- Create new Israeli city JSON files
- Build a listings.json bulk migration script
- Modify locale keywords (WP003 scope)
- Add `connector_class` to SourceDefinition (WP002 scope)
- Touch `shaked_wg_agent/runner.py` `_build_scraper` mapping (WP002 scope)
- Remove the `tutti` entry from `data/sources.json` (WP002 scope)
- Make design decisions not covered by the LOD400 spec
- Modify files outside your listed deliverables

---

*Mandate issued by Team 110 (shaked_arch / Claude Code) on authority of Team 00 | shaked-wg-agent | S005-P004-WP001 | 2026-04-12*
