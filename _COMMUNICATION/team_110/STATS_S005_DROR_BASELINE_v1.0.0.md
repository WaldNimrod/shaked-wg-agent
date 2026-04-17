# S005 Dror Launch — Baseline Statistics and KPI Frame

## Date
2026-04-17

## Data snapshot source
- `data/runs.json`
- `data/listings.json`
- `data/sources.json`
- `data/cities/pardes-hanna-region.json`
- `data/profiles/pardes-hanna.json`
- `_COMMUNICATION/team_00/DECISIONS_ISRAEL_STRATEGY_v1.0.0.md`

---

## Baseline metrics (before Dror first run)

- `runs_total`: 16
- `runs_pardes_hanna`: 0
- `runs_with_homeless_source`: 0
- `listings_total`: 59
- `listings_homeless`: 0
- `listings_homeless_verified`: 0
- `active_sources_configured_for_IL_profile`: `["homeless"]`
- `configured_source_ids`: `["wgzimmer", "flatfox", "wg-gesucht", "homeless"]`
- `dominant_live_source_in_db`: `flatfox` (59/59)

Interpretation:
- ישראל הוגדרה קונפיגורטיבית אך טרם הוזרם דאטה תפעולי ממקור ישראלי.
- הפער העיקרי הוא “source configured” מול “source producing listings”.

---

## Market-context statistics from strategy research

From Team 00 decision artifact:
- 11 Israeli rental platforms mapped
- 7+ competitors analyzed
- Homeless identified as easiest initial technical entry
- Yad2 identified as dominant but anti-bot heavy

---

## Dror link target

Planned production URL for Dror:
- `https://www.nimrod.bio/wp-content/uploads/shaked-wg/dror/index.html`

---

## Post-run KPI template (fill after first Dror production run)

- `run_id`:
- `run_timestamp`:
- `sources_scanned`:
- `results_scanned`:
- `new_results`:
- `updated_results`:
- `errors_count`:
- `report_url`:
- `listings_from_target_settlements`:
- `listings_matching_rooms_6_7`:
- `listings_with_clinic_or_separate_unit_signal`:
- `listings_with_yard_250_plus_signal`:
- `qualification_ratio` (`qualified / scanned`):

