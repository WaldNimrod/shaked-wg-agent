# LOD400 Executable Spec — S001-P001-WP001

**WP ID:** S001-P001-WP001  
**Label:** Application core — Python agent skeleton, scraper stubs, CLI  
**Gate:** L-GATE_S → L-GATE_B  
**Author:** shaked_arch (claude-code)  
**Date:** 2026-04-10  
**Status:** APPROVED — builder may proceed

---

## Scope

Implement the full Python package `shaked_wg_agent` with:
1. Configuration loader (data/config.json + data/sources.json)
2. JSON persistence layer (listings.json + runs.json)
3. Relevance scoring engine
4. Run orchestrator
5. Platform scrapers (wgzimmer.ch, wg-gesucht.de, flatfox.ch)
6. CLI entry point (run | status | list)
7. Unit tests (46 minimum)

---

## Package Structure

```
shaked_wg_agent/
├── __init__.py
├── __main__.py      ← CLI entry point
├── config.py        ← AgentConfig, Source, ProjectConfig dataclasses
├── persistence.py   ← upsert_listing, mark_stale, append_run, last_run
├── scorer.py        ← score_listing (vegan/tram/roommate/freshness/url)
├── runner.py        ← run_scan() → run_record dict
└── scrapers/
    ├── __init__.py
    ├── base.py      ← BaseScraper ABC + ScrapedListing dataclass
    ├── wgzimmer.py
    ├── wg_gesucht.py
    └── flatfox.py
```

---

## Scoring Formula

| Dimension | Max pts | Logic |
|-----------|---------|-------|
| vegan_signal | 35 | "vegan/vegane" → 35, "pflanzlich" → 22, "kein fleisch" → 12, none → 0 |
| tram_lines | 25 | 1 match → 12, 2 → 20, 3+ → 25 |
| roommate_age | 15 | "young" pref + student signal → 15 |
| freshness | 15 | 0 days old → 15, 14+ days → 0, linear decay |
| url_quality | 10 | direct → 10, search_only → 4, broken → 2 |
| **Total** | **100** | budget outside range → hard 0 |

---

## CLI Specification

```
python -m shaked_wg_agent run     # triggers run_scan(), updates listings.json + runs.json
python -m shaked_wg_agent status  # summary table (profile, listings count, top pick, deadline)
python -m shaked_wg_agent list    # rich table sorted by relevance_score desc
```

---

## Exit Criteria (L-GATE_B)

- [ ] `pytest tests/ -v` → 46+ tests, 0 failures
- [ ] `ruff check shaked_wg_agent/ tests/` → 0 errors
- [ ] `python -m shaked_wg_agent status` → renders without exception
- [ ] `python -m shaked_wg_agent list` → renders listing table with existing data
