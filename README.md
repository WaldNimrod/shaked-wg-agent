# shaked-wg-agent

Personal WG (shared apartment) search agent for Basel, Switzerland.

**Owner:** Shaked | **Project window:** April 9 – June 8, 2026 | **Profile:** L0

---

## What it does

Scans WG listing platforms (wgzimmer.ch, wg-gesucht.de, flatfox.ch), scores listings
against Shaked's preferences (vegan-friendly, tram-accessible, young roommates, CHF 200–1000),
and maintains a local database of relevant listings.

Manual triggers only — no background polling.

---

## Quick Start

```bash
# Install
make install
source .venv/bin/activate

# Show project summary
make status

# List all listings (sorted by relevance)
make list

# Trigger a full scan
make run
```

---

## CLI

```bash
python -m shaked_wg_agent run      # scan all enabled platforms
python -m shaked_wg_agent status   # show summary
python -m shaked_wg_agent list     # show listings table
```

---

## Project Structure

```
shaked_wg_agent/         Application code
  config.py              Load data/config.json + data/sources.json
  persistence.py         CRUD for listings.json + runs.json
  scorer.py              Relevance scoring (vegan/tram/roommate/freshness/url)
  runner.py              Scan orchestrator
  __main__.py            CLI entry point
  scrapers/              Platform-specific scrapers
    base.py              Abstract BaseScraper + ScrapedListing
    wgzimmer.py          wgzimmer.ch
    wg_gesucht.py        wg-gesucht.de
    flatfox.py           flatfox.ch

data/                    JSON data store
  config.json            Search profile (budget, diet, tram lines, etc.)
  sources.json           Platform source definitions
  runs.json              Run history log
  listings.json          Apartment listing database

_aos/                    AOS governance (L0 profile)
tests/                   Unit tests (46 tests)
```

---

## Scoring

| Dimension | Max | Logic |
|-----------|-----|-------|
| Vegan signal | 35 | vegane/pflanzlich/kein Fleisch |
| Tram lines | 25 | intersection with preferred [2,3,8,16] |
| Roommate age | 15 | young/student signal |
| Freshness | 15 | linear decay over 14 days |
| URL quality | 10 | direct > search_only > broken |
| Budget gate | — | hard fail if outside CHF 200–1000 |

---

## Config

Edit `data/config.json` to adjust search parameters. Key fields:

```json
{
  "budget_min_chf": 200,
  "budget_max_chf": 1000,
  "diet": "vegan",
  "tram_lines": ["8", "3", "2", "16"],
  "move_in_from": "2026-06-01",
  "manual_triggers_only": true
}
```

> **Note:** `data/listings.json` and `data/runs.json` contain synthetic seed data
> from initial project setup. Run `make run` to replace with live data.

---

## Development

```bash
make test        # run pytest (46 tests)
make lint        # run ruff
make check       # lint + test
make validate-aos  # AOS structural validation
```

---

## AOS Governance

This project is managed under the AOS L0 (Lean/Manual) profile.
See `_aos/` for governance artifacts, `CLAUDE.md` for agent activation instructions.
