# LOD400 — SWG-PLAT-M2 — Full-description extraction
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110) + team_110 orchestrator (spec completed after builder truncation)
**WP:** SWG-PLAT-M2
**Type:** LOD400_SPEC

---

## Exact Changes

### 1. `shaked_wg_agent/scrapers/base.py`

**Field addition to `ScrapedListing` dataclass** (after `summary: str = ""`):
```python
full_description: str = ""
```

**Serialization in `to_dict()`** (after `"summary": self.summary`):
```python
"full_description": self.full_description,
```

### 2. `shaked_wg_agent/scrapers/flatfox.py`

**In `_parse_listing()`, before `return ScrapedListing(...)`:**
```python
# full_description: use the raw API description field (untruncated).
# Falls back to summary when description is empty.
full_description = description if description else summary
```

**In `ScrapedListing(...)` constructor** (after `summary=summary[:300]`):
```python
full_description=full_description,
```

**Where `description` comes from:** The flatfox API JSON response includes a `description` field (the full listing body text). The existing scraper already extracts this as a local variable before building `summary`. `full_description` captures it untruncated.

### 3. `shaked_wg_agent/scrapers/wgzimmer_pw.py`

**In `ScrapedListing(...)` constructor** (after `summary=summary`):
```python
full_description=full_text,
```

**Where `full_text` comes from:** M3's rewrite of `wgzimmer_pw.py` constructs `full_text` by concatenating all DOM text from the listing entry (`<li class="search-mate-entry">`). This is the full listing body available from the POST response HTML.

### 4. `data/listings.json` migration

Applied at time of WP build. For each listing object in the JSON array:
```python
if "full_description" not in listing:
    listing["full_description"] = listing.get("summary", "")
```
Write the updated array back to the file (preserving all other fields).

### 5. `tests/fixtures/scrapers/` — fixture file list

| File | Content |
|---|---|
| `flatfox_listing_01.html` – `flatfox_listing_05.html` | Minimal but structurally realistic flatfox listing HTML with description paragraphs ≥500 chars |
| `wgzimmer_listing_01.html` – `wgzimmer_listing_05.html` | Minimal wgzimmer listing HTML with full body text |
| `wgzimmer_search_page.html` | wgzimmer search form page (created by M3 for selector validation) |

### 6. `tests/test_scrapers/test_full_description.py` — new tests

**Test cases:**
1. `test_scraper_listing_has_full_description_field` — assert `ScrapedListing()` accepts `full_description` kwarg
2. `test_full_description_defaults_to_empty` — assert default is `""`
3. `test_full_description_in_to_dict` — assert `to_dict()` includes `"full_description"` key
4. `test_flatfox_fixture_extraction` — parse `flatfox_listing_01.html`, assert extracted body ≥ 50 chars
5. `test_wgzimmer_fixture_extraction` — parse `wgzimmer_listing_01.html`, assert extracted body ≥ 50 chars
6. `test_migration_adds_field_from_summary` — dict without `full_description` → migration adds it from `summary`
7. `test_migration_preserves_existing_value` — dict WITH `full_description` → migration leaves it unchanged

---

## Acceptance Criteria Mapping

| AC | Implementation | Verification |
|---|---|---|
| AC1: `full_description` exposed on ScrapedListing | `base.py` field addition | `test_scraper_listing_has_full_description_field` |
| AC2: flatfox `full_description` ≥ 50 chars and longer than `summary` when listing has body text | `flatfox.py` untruncated extraction | `test_flatfox_fixture_extraction` (≥50 chars + parametrized longer-than-summary on fixtures with `len(full_desc)>240`) |
| AC3: migration — all legacy listings have key | listings.json migration | inspect `data/listings.json` after build |
| AC4: ≥10 fixture HTML files | 11 files in `tests/fixtures/scrapers/` | `ls tests/fixtures/scrapers/ \| wc -l` |
| AC5: ruff + pytest clean | fixed in touched files | `ruff check .` + `pytest tests/` |

---

## Build Status (actual)

- `base.py`: `full_description: str = ""` added to dataclass and `to_dict()` ✓
- `flatfox.py`: `full_description=full_description` in ScrapedListing constructor ✓
- `wgzimmer_pw.py`: `full_description=full_text` added (applied at M2+M3 merge by orchestrator) ✓
- `data/listings.json`: migration applied — all listings have `full_description` key ✓
- `tests/fixtures/scrapers/`: 11 HTML files ✓
- `tests/test_scrapers/test_full_description.py`: 7+ test cases ✓
- pytest: 144 passed ✓
- ruff: pre-existing errors only (not introduced by this WP) ✓
