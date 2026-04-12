---
lod_target: LOD500
lod_status: LOCKED
track: A
authoring_team: team_110
consuming_team: team_190
date: 2026-04-12
version: v1.0.0
supersedes: null
fidelity: FULL_MATCH
verifying_team: team_190
spec_ref: _aos/work_packages/S002-P001-WP001/LOD400_S002-P001-WP001.md
---

# City-agnostic Config Schema + Scraper Interface — LOD500 As-Built

**work_package_id:** S002-P001-WP001
**spec_ref:** LOD400_S002-P001-WP001.md v1.1.0
**gate:** L-GATE_B
**fidelity:** FULL_MATCH

## 1. What was built

Three-entity configuration model (`AgentMeta`, `SearchProfile`, `CityDefinition`, `SourceDefinition` / `ResolvedSource`), `load_config(profile_id)`, CLI `--profile` and deprecated `--city`, scrapers take `CityDefinition`, listings use `transit_match_lines`, scorer uses `SearchProfile` and `transit_lines`, runner persists `city_id`/`profile_id` on listings and runs.

## 2. Fidelity record

| AC | LOD400 requirement | As-built result | Fidelity |
|----|--------------------|-----------------|----------|
| AC-01–AC-11 | Dataclasses, validation, `ProjectConfig.active_sources` | Implemented in `config.py`; `AgentConfig`/`Source` removed | ✅ MATCH |
| AC-12–AC-20 | Loaders and file I/O | `_load_*` + `load_config` with logging warnings | ✅ MATCH |
| AC-21–AC-28 | Resolution and priority | Intersection + priority by `city.available_sources` order | ✅ MATCH |
| AC-29–AC-33 | CLI argparse | `__main__.py` | ✅ MATCH |
| AC-34–AC-39 | Scrapers + runner | `BaseScraper`, `runner._build_scraper`, `run_scan` signature | ✅ MATCH |
| AC-40–AC-45 | Scorer | `scorer.py` uses `SearchProfile`, `transit_match_lines` | ✅ MATCH |

## 3. Deviations from spec (if any)

None.

## 4. Test evidence

- Unit + integration tests: 81 total (see `pytest` run); all PASS.
- `ruff check` — clean.
- `validate_aos.sh` — 12/12 PASS.

## 5. Files changed

| File | Change type | Notes |
|------|-------------|-------|
| `shaked_wg_agent/config.py` | MODIFY | Three-entity model |
| `shaked_wg_agent/runner.py` | MODIFY | Profile/city IDs, flatfox bbox verify |
| `shaked_wg_agent/scorer.py` | MODIFY | `SearchProfile`, transit naming |
| `shaked_wg_agent/__main__.py` | MODIFY | argparse |
| `shaked_wg_agent/scrapers/*.py` | MODIFY | `CityDefinition`, `transit_match_lines` |
| `data/agent.json`, `data/cities/basel.json`, `data/profiles/default.json`, `data/sources.json` | ADD/MODIFY | S002 layout |
| `tests/test_config.py`, `tests/test_integration.py` | ADD | WP001 coverage |

## 6. Verifying team sign-off

> I confirm this as-built record is accurate. Fidelity classification FULL_MATCH is correct.
> All acceptance criteria verified independently. No deviations found.
> **Signature:** Team 190 (shaked_val / OpenAI) | 2026-04-12
