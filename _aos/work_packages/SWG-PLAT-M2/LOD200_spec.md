# LOD200 — SWG-PLAT-M2 — Full-description extraction
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110) + team_110 orchestrator (spec completed after builder truncation)
**WP:** SWG-PLAT-M2
**Type:** LOD200_SPEC

---

## Problem

`ScrapedListing.summary` was truncated at ~200–300 chars. All downstream extractors that need age/student/vegan/restriction signals (WPs M1 and M5) operate on `summary` and therefore fail at recall. The full listing body text — containing keywords like "nur Frauen", "Wochenaufenthalter", "Student bevorzugt" — was discarded at scrape time.

## Architecture

### Component changes

| Component | Change | Rationale |
|---|---|---|
| `shaked_wg_agent/scrapers/base.py` | Add `full_description: str = ""` field to `ScrapedListing` dataclass and `to_dict()` serialization | SSoT for the new field; all scrapers and downstream consumers reference this one class |
| `shaked_wg_agent/scrapers/flatfox.py` | Set `full_description = description if description else summary` before constructing `ScrapedListing` | Flatfox API returns a `description` field with the full body text |
| `shaked_wg_agent/scrapers/wgzimmer_pw.py` | Set `full_description = full_text` in `ScrapedListing` constructor | M3 rewrites wgzimmer_pw.py; full_text is the parsed listing body available in M3's new flow |
| `data/listings.json` | Migration: add `full_description` key to every existing listing (value = `summary` for legacy rows) | Prevents `KeyError` in downstream readers; enables M5 to work on all existing listings |
| `tests/fixtures/scrapers/` | 10 minimal HTML fixture files (5 flatfox, 5 wgzimmer listing pages) | Fixture-based tests require realistic HTML structure; no live network in CI |
| `tests/test_scrapers/test_full_description.py` | New fixture-driven tests | Validates extraction correctness without live scraping |

### Data flow

```
Flatfox API JSON response
  └─> FlatfoxScraper._parse_listing()
        ├─> summary  = description[:300]   (existing, truncated)
        └─> full_description = description  (NEW — untruncated API field)

wgzimmer.ch POST response HTML (M3 new flow)
  └─> WgzimmerPlaywrightScraper._parse_listing_entry()
        ├─> summary  = full_text[:240]     (existing)
        └─> full_description = full_text   (NEW — full DOM-extracted text)

Legacy listings.json rows (migration)
  └─> full_description = summary           (fallback — no data loss)
```

### Migration strategy

The migration is applied in-place to `data/listings.json`. Every listing object that lacks a `full_description` key gets `full_description = summary`. This is a one-time transform; new listings populate `full_description` at scrape time via the updated scrapers.

### Test strategy

Fixture-based: HTML files in `tests/fixtures/scrapers/` simulate realistic scraper inputs without network access. Tests parse the fixture HTML using the same extraction logic as production scrapers and assert:
- `full_description` length ≥ `summary` length (for listings where body > 300 chars)
- Fallback: `full_description == summary` when no body text available
- Migration: legacy dict without `full_description` gets the field added correctly

---

## Dependencies

- **Blocked by:** nothing (this WP is the Wave-1 unblocker)
- **Blocks:** SWG-PLAT-M1 (needs full_description for accurate age/student signal extraction), SWG-PLAT-M5 (needs full_description for negative-signal recall)
- **Parallel with:** SWG-PLAT-M3 (independent code areas for most of the work; wgzimmer_pw.py changes coordinated at merge time)
