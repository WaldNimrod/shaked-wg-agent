# MANDATE — S005-IL-WP003: Israeli Profile + Sources Integration

**Assigned to:** Team 20 (Builder)
**Authority:** Team 00

## YOUR TASK

1. Add the Homeless.co.il source entry to `data/sources.json` (append to existing array, keep all Swiss sources).
2. Create `data/profiles/pardes-hanna.json` — an Israeli search profile pointing to the Pardes Hanna region city.
3. Verify the full pipeline works end-to-end.

## INPUT FILES

- **Read:** `specs/LOD400_S005-IL-WP003.md` — full spec with exact JSON content
- **Reference:** `data/profiles/default.json` — existing Swiss profile (pattern to follow)
- **Reference:** `data/sources.json` — current sources (append to this)

## OUTPUT FILES

- **Modify:** `output/data/sources.json` — add homeless entry, keep existing 3 Swiss sources
- **Create:** `output/data/profiles/pardes-hanna.json`

## DO NOT

- Remove or modify existing Swiss source entries
- Remove or modify the default.json profile
- Modify any Python source code
- Change budget values without justification (ILS range is intentional)

## DEPENDENCIES

- WP001 must be complete (city definition exists)
- WP002 must be complete (scraper module exists for FQN resolution)
