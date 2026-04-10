# PROJECT CONTEXT — shaked-wg-agent

## What is this project?

A personal WG (shared apartment) search automation agent for Shaked moving to Basel, Switzerland.
The agent scans 3 active rental platforms, scores listings against Shaked's preferences,
and maintains a local JSON-backed database of listings with relevance tracking.

**Key constraints:**
- Manual triggers only (no automatic polling)
- Project window: April 9 – June 8, 2026 (60 days)
- Move-in target: June 1, 2026

## Profile

| Field | Value |
|-------|-------|
| Target city | Basel, Switzerland |
| Budget | CHF 200–1000/month |
| Diet | Vegan |
| Preferred roommates | Young (students, 20s) |
| Priority tram lines | 2, 3, 8, 16 |
| Language | German (de) primary |

## Architecture

```
shaked_wg_agent/
├── config.py        — load data/config.json + data/sources.json
├── persistence.py   — CRUD for data/listings.json + data/runs.json
├── scorer.py        — vegan(35) + tram(25) + roommate(15) + freshness(15) + url(10)
├── runner.py        — orchestrate full scan cycle
├── __main__.py      — CLI: run | status | list
└── scrapers/
    ├── base.py      — abstract BaseScraper
    ├── wgzimmer.py  — wgzimmer.ch scraper
    ├── wg_gesucht.py — wg-gesucht.de scraper
    └── flatfox.py   — flatfox.ch scraper
```

## Current State

- **Active milestone:** SHAKED-M001
- **Active WP:** SHAKED-P001-WP001 at L-GATE_B
- **Profile:** L0
- **Tests:** 46 passing
- **CLI:** `python -m shaked_wg_agent [run|status|list]`

## Key Paths

| Path | Content |
|------|---------|
| `data/config.json` | Search profile configuration |
| `data/sources.json` | Platform source definitions |
| `data/runs.json` | Run history log |
| `data/listings.json` | Apartment listing database |
| `shaked_wg_agent/` | Application source code |
| `tests/` | Unit tests (pytest) |
| `_aos/` | AOS governance artifacts |
| `_COMMUNICATION/` | Inter-team communication artifacts |
