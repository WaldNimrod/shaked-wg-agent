# Handoff — Team 110 (Builder)
## From: shaked_arch (Claude Code) + Team 00 (Nimrod)
## To: shaked_build (Cursor Composer — new session)
## Date: 2026-04-12
## Subject: S001 closed. S002 entry brief. Full project state transfer.

---

## 1. PROJECT IDENTITY

| Field | Value |
|-------|-------|
| Project | shaked-wg-agent |
| Name | Shaked WG Basel Search Agent |
| Repo | WaldNimrod/shaked-wg-agent |
| Local path | `/Users/nimrod/Documents/shaked-wg-agent` |
| Profile | **L0** (current) → L2 at S002-P002-WP001 entry |
| Owner | Nimrod (Team 00) |
| Deployed | `https://www.nimrod.bio/agents/shaked-wg/` (FTPS, 3× daily cron) |

**What this project is:** A personal apartment-search automation agent for Shaked moving to Basel, Switzerland (June 2026). The agent scans 3 rental platforms (wgzimmer.ch, wg-gesucht.de, flatfox.ch), scores listings against Shaked's preferences (vegan, tram lines 2/3/8/16, CHF 200–1000/mo), and publishes a ranked HTML report.

**Future direction:** SaaS product — multi-city, multi-tenant, billing-enabled apartment-finding service (S002–S004).

---

## 2. CURRENT STATE — WHAT IS DONE

### S001: COMPLETE (2026-04-11)

Both S001 WPs closed at L-GATE_V PASS:

| WP | Label | Status |
|----|-------|--------|
| S001-P001-WP001 | Application core (Python agent, scrapers, CLI, HTML publish) | **COMPLETE** |
| S001-P002-WP001 | AOS canonization + SaaS roadmap register | **COMPLETE** |

**Application state (v0.2.2):**
- 59 live Basel listings in `data/listings.json`
- 57 verified_active (flatfox REST PIN API validation)
- 3 scrapers: flatfox (live), wg-gesucht (live), wgzimmer (Playwright, reCAPTCHA fallback)
- Dual-table UI: verified listings (Bootstrap 5.3.3) + unverified section (amber border)
- Live "Validate" button: client-side JS → flatfox `/api/v1/pin/` endpoint
- Proof page: `proof.html` with scraper output screenshots
- 53 tests passing, ruff clean
- validate_aos.sh: **12/12 PASS**

**Governance state:**
- lean-kit v3.1.3+3e4164e (physical copy in `_aos/lean-kit/`)
- `_aos/project_identity.yaml` present and correct
- Hub registered: `agents-os/_aos/projects.yaml`, `active_milestone: S002`
- roadmap.yaml: S001 COMPLETE, S002+ PLANNED/DEFERRED

---

## 3. TEAM MODEL (your role)

| ID | Name | Engine | Role |
|----|------|--------|------|
| `shaked_sd` | Nimrod | human | System Designer — Team 00. All gate approvals. |
| `shaked_arch` | Claude Code | claude-code | Architecture agent. Specs + gate reviews. |
| **`shaked_build`** | **Cursor Composer** | **cursor-composer** | **You. Builder. Implements specs.** |
| `shaked_val` | OpenAI | openai | Validator. L-GATE_V only. Cross-engine (Iron Rule #1). |

**Your constraints:**
- You do NOT author specs — `shaked_arch` (Claude Code) authors LOD400 before you begin
- You do NOT run L-GATE_V — `shaked_val` (OpenAI) runs it; it is immutable
- You write to: `shaked_wg_agent/`, `data/`, `tests/`, `scripts/`, `deploy/`, `_aos/work_packages/[WP]/LOD500_asbuilt.md`
- You do NOT write to: `agents-os/`, `_aos/roadmap.yaml` (arch/sd owns that), other projects

---

## 4. ACTIVE MILESTONE: S002 — Platform Foundation

**Profile: L2 (requires profile transition before complex WPs begin)**  
**Target: 2026-09-30**

### S002 Work Packages

| WP | Label | Track | Profile | Status | Builder entry condition |
|----|-------|-------|---------|--------|------------------------|
| S002-P001-WP001 | City-agnostic config schema + scraper interface | A | L2 | PLANNED | Awaiting LOD400 from shaked_arch |
| S002-P001-WP002 | Add Zurich + Bern search profiles | A | L2 | PLANNED | Depends on WP001 above |
| **S002-P002-WP001** | **REST API layer — /search, /listings, /runs** | **B** | **L2.5** | **PLANNED** | L2 profile transition + LOD300 required first |
| S002-P002-WP002 | API key auth (single-user) | A | L2 | PLANNED | Depends on API WP |
| S002-P003-WP001 | Email/Telegram notification digest | A | L2 | PLANNED | Awaiting LOD400 |

**Team 00 decisions locked (2026-04-12):**
- S002-P002-WP001: **L2.5 / Track B confirmed** — requires LOD300 + EXT-CP1 before L-GATE_S
- Billing (S003-P002): **DEFERRED** — pending dedicated spec session (provider research needed)

### S002 Entry Prerequisites (your checklist before starting any S002 WP)

- [ ] `shaked_arch` has issued LOD400 via `_COMMUNICATION/team_110/[WP]/LOD400_mandate.md`
- [ ] L2 profile transition complete for complex WPs (metadata.yaml has `aos_engine_version`)
- [ ] `validate_aos.sh .` still passes (run before beginning and after completing each WP)

---

## 5. CODEBASE MAP

```
shaked_wg_agent/
├── __init__.py          version = "0.2.2"
├── __main__.py          CLI: run | status | list
├── config.py            AgentConfig, Source, ProjectConfig dataclasses — loads data/config.json + data/sources.json
├── persistence.py       CRUD: data/listings.json (upsert, stale), data/runs.json
├── scorer.py            5-dimension scoring: vegan(35) + tram(25) + roommate(15) + freshness(15) + url(10)
├── runner.py            run_scan() orchestrator
└── scrapers/
    ├── base.py          BaseScraper ABC + ScrapedListing dataclass
    ├── flatfox.py       flatfox.ch — REST JSON API (public, CORS-enabled)
    ├── wg_gesucht.py    wg-gesucht.de — BeautifulSoup HTML scraper
    └── wgzimmer.py      wgzimmer.ch — Playwright headless (reCAPTCHA fallback to empty)

publisher/
├── html_report.py       Bootstrap 5.3.3 dual-table HTML generator + FTPS publish
└── proof_report.py      Playwright screenshot proof page

data/
├── config.json          Search profile (city, budget, tram lines, vegan flag)
├── sources.json         Platform source definitions
├── listings.json        Listing database (59 records)
└── runs.json            Run history log

scripts/
├── generate_proof.py    Proof page generator (runs Playwright for screenshots)
└── publish.py           Standalone FTPS publish

tests/
├── test_scorer.py       32 tests
├── test_persistence.py  12 tests
├── test_config.py        5 tests
├── test_scrapers.py      4 tests (stub-level)
└── ...                  total 53 tests
```

---

## 6. DEVELOPMENT COMMANDS

```bash
# Run agent
python -m shaked_wg_agent run

# Status + list
python -m shaked_wg_agent status
python -m shaked_wg_agent list

# Tests
pytest tests/ -v                        # all 53 tests
pytest tests/ -v --tb=short             # compact failures

# Linting
ruff check shaked_wg_agent/ tests/      # must be clean before any WP closes

# AOS validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Expected: 12 PASS / 0 SKIP / 0 FAIL

# Proof page
python scripts/generate_proof.py        # generates + publishes proof.html

# Publish manually
python scripts/publish.py
```

---

## 7. GATE MODEL

```
L-GATE_E → L-GATE_S → L-GATE_B → L-GATE_V → COMPLETE
```

| Gate | Authority | Your role |
|------|-----------|-----------|
| L-GATE_E | Team 00 approves entry | You receive mandate after E passes |
| L-GATE_S | shaked_arch reviews spec | You WAIT for LOD400 mandate |
| **L-GATE_B** | **You own this gate** | Implement spec → write LOD500 as-built → run tests + ruff + validate_aos |
| L-GATE_V | shaked_val (OpenAI) only | You hand off; do NOT self-validate |

**L-GATE_B checklist (your deliverable):**
1. All spec items from LOD400 implemented
2. `pytest tests/ -v` — all tests pass (new tests for new functionality)
3. `ruff check .` — clean
4. `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — 12/12
5. LOD500 as-built written to `_aos/work_packages/[WP-ID]/LOD500_asbuilt.md`
6. Post result to `_COMMUNICATION/team_110/[WP-ID]/L-GATE_B_result.md`

---

## 8. IRON RULES (binding on you)

1. **Builder engine ≠ Validator engine.** You are cursor-composer. `shaked_val` (OpenAI) runs L-GATE_V. Never self-validate.
2. **`_aos/lean-kit/` is a physical copy.** Never convert to symlink.
3. **All `spec_ref` paths are repo-internal.** No absolute paths in governance artifacts.
4. **Single writer on `roadmap.yaml`.** You do NOT write to roadmap.yaml — `shaked_arch` or `shaked_sd` owns it.
5. **L-GATE_V is always `shaked_val`.** Immutable. Constitutional.

---

## 9. KEY FILES TO READ ON SESSION START

In order:

```
1. _aos/roadmap.yaml                   ← active WP + gate position
2. _aos/context/PROJECT_CONTEXT.md     ← project background
3. _COMMUNICATION/team_110/[latest]/   ← your active mandate (LOD400)
4. _aos/work_packages/[WP-ID]/LOD400_spec.md  ← what to build
```

---

## 10. KNOWN ISSUES / WATCH LIST

| Item | Detail |
|------|--------|
| wgzimmer reCAPTCHA | Playwright blocked by reCAPTCHA v3 — scraper returns empty gracefully. Not a bug; architecture supports it. Fix in S002 scope (proxy/bypass strategy) if needed. |
| Flatfox PIN validation | Public API, no auth needed. Bounding box coords in `data/config.json`. If flatfox changes API, `publisher/html_report.py` live-validate JS breaks. |
| verified_active field | Written by `persistence.py` via flatfox PIN API check on each run. First-run listings may be unverified until next scan. |
| pyproject.toml | `version = "0.2.2"` — keep aligned with `shaked_wg_agent/__init__.py`. |
| FTPS credentials | In `.env` (not committed). Keys: `FTP_HOST`, `FTP_USER`, `FTP_PASS`, `FTP_REMOTE_DIR`. |
| S002 L2 transition | Before S002-P002-WP001 (REST API) enters L-GATE_S, `aos_engine_version` must be set in `_aos/metadata.yaml`. This is an infra task — coordinate with Team 00. |

---

## 11. COMMUNICATION PATHS

| What | Where |
|------|-------|
| Your mandates (LOD400) | `_COMMUNICATION/team_110/[WP-ID]/LOD400_mandate.md` |
| Your deliverables (LOD500, gate results) | `_COMMUNICATION/team_110/[WP-ID]/L-GATE_B_result.md` |
| Architecture reviews | `_COMMUNICATION/team_100/[WP-ID]/ARCH_REVIEW_*.md` |
| Validator results | `_COMMUNICATION/team_190/[WP-ID]/L-GATE_V_result.md` |
| Team 00 decisions | `_COMMUNICATION/team_00/DECISIONS_*.md` |

---

## 12. S002 FIRST STEPS (what to expect next)

1. `shaked_arch` will author LOD400 for `S002-P001-WP001` (city-agnostic config schema)
2. Team 00 approves L-GATE_E
3. LOD400 mandate arrives in `_COMMUNICATION/team_110/S002-P001-WP001/`
4. You begin implementation — refactor `data/config.json` schema + `BaseScraper` interface
5. L-GATE_B → LOD500 → shaked_val → COMPLETE

---

*Handoff prepared by shaked_arch (Claude Code) + Team 00 | 2026-04-12*  
*shaked-wg-agent | S001 COMPLETE | Active milestone: S002*
