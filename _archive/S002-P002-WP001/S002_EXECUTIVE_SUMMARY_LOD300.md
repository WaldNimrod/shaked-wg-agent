# S002 Platform Foundation — Executive Summary (LOD300) v2

**Prepared by:** Team 110 (Builder Agent)
**Date:** 2026-04-12
**For:** Team 00 (Nimrod) — approval review
**Status:** PENDING APPROVAL
**Revision:** v2.0 — corrected three-entity data model (City/Source/Profile separation)

---

## 1. Milestone Overview

S002 transforms the personal Basel apartment agent into a **city-agnostic platform** with API access and notification capabilities. Five work packages across three pillars:

| Pillar | WPs | Description |
|--------|-----|-------------|
| **P001: Abstraction** | WP001, WP002 | Three-entity model (CityDefinition, SourceDefinition, SearchProfile) + Zurich/Bern city definitions |
| **P002: API** | WP001, WP002 | REST API layer + API key auth |
| **P003: Alerts** | WP001 | Email/Telegram notification digest (per-profile) |

**Target:** 2026-09-30 | **Profile:** L2 (L2.5 for REST API WP)

---

## 2. Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                        Entry Points                                │
│  ┌──────────┐  ┌──────────────────┐  ┌────────────────────────┐   │
│  │   CLI    │  │   REST API       │  │   Cron (3x daily)      │   │
│  │ --profile│  │   FastAPI :8000  │  │   run_scan()           │   │
│  └────┬─────┘  └───────┬──────────┘  └──────────┬─────────────┘   │
│       │                │ X-API-Key auth          │                 │
│       └────────────────┼─────────────────────────┘                 │
│                        ▼                                           │
│              ┌──────────────────┐                                  │
│              │  load_config()   │                                  │
│              │  (profile_id)    │                                  │
│              └────────┬─────────┘                                  │
│                       │                                            │
│     ┌─────────────────┼──────────────────┐                         │
│     ▼                 ▼                  ▼                          │
│  data/profiles/    data/cities/       data/sources.json             │
│  ┌────────────┐  ┌──────┬──────┬────┐  (Global Registry)          │
│  │  default   │  │Basel │Zurich│Bern│  ┌────────────────┐          │
│  │(SearchProf)│  │(City)│(City)│(Ci)│  │ wgzimmer       │          │
│  │budget,diet │  │bbox  │bbox  │bbox│  │ flatfox        │          │
│  │tram,notif. │  │zips  │zips  │zips│  │ wg-gesucht     │          │
│  │city→basel  │  │avail │avail │avai│  │ tutti           │          │
│  └────────────┘  └──────┴──────┴────┘  │ +city_params   │          │
│                                         └────────────────┘          │
│                       ▼                                            │
│     resolve: profile.enabled_sources ∩ city.available_sources      │
│                       ▼                                            │
│              ┌──────────────────┐                                  │
│              │   run_scan()     │                                  │
│              │   (orchestrator) │                                  │
│              └────────┬─────────┘                                  │
│          ┌────────────┼────────────┐                               │
│          ▼            ▼            ▼                                │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐                         │
│    │ flatfox  │ │ wgzimmer │ │ wg-ges.  │  Scrapers               │
│    │ (REST)   │ │ (PW)     │ │ (BS4)    │  (CityDefinition)       │
│    └────┬─────┘ └────┬─────┘ └────┬─────┘                         │
│         └─────────────┼────────────┘                               │
│                       ▼                                            │
│    ┌──────────────────────────────────┐                            │
│    │  scorer.py → persistence.py      │                            │
│    │  Score(SearchProfile) → Save     │                            │
│    └────────────────┬─────────────────┘                            │
│                     ▼                                              │
│    ┌──────────────────────────────────┐                            │
│    │  notifier.py (per-profile)       │                            │
│    │  Email (SMTP) + Telegram (Bot)   │                            │
│    │  Config from profile.notifications│                            │
│    └──────────────────────────────────┘                            │
│                     ▼                                              │
│    ┌──────────────────────────────────┐                            │
│    │  publisher → FTPS → nimrod.bio   │                            │
│    └──────────────────────────────────┘                            │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. Work Package Summary

| # | WP ID | Label | Track | Key Deliverable | Dependencies |
|---|-------|-------|-------|-----------------|--------------|
| 1 | S002-P001-WP001 | Config schema | A | Three-entity model (CityDefinition + SearchProfile + SourceDefinition), --profile CLI flag | None |
| 2 | S002-P001-WP002 | City definitions | A | Basel/Zurich/Bern city files, global source registry, default profile | WP001 |
| 3 | S002-P002-WP001 | REST API | **B (L2.5)** | FastAPI /search, /listings, /runs with profile_id param | WP001 |
| 4 | S002-P002-WP002 | API key auth | A | X-API-Key middleware, constant-time validation | WP003 (API) |
| 5 | S002-P003-WP001 | Notifications | A | Email + Telegram digest, per-profile config (embedded) | WP001 |

---

## 4. Dependency Graph

```
S002-P001-WP001 (Config Schema — Three-Entity Model)
    │
    ├──────────────────────────────────┐
    ▼                                  ▼
S002-P001-WP002 (City Definitions)  S002-P002-WP001 (REST API)
                                       │
                                       ▼
                                  S002-P002-WP002 (API Auth)

S002-P001-WP001 (Config Schema)
    │
    └──→ S002-P003-WP001 (Notifications)
         (can parallelize with API track)
```

**Recommended build order:**
1. WP001 (config) — foundation (three-entity model)
2. WP002 (cities) + WP003 (API) — can start in parallel after WP001
3. WP004 (auth) — after API layer exists
4. WP005 (notifications) — after config refactor, parallel with API

---

## 5. Per-WP Summary

### 5.1 S002-P001-WP001: City-agnostic Config Schema

Refactors the monolithic `data/config.json` into a **three-entity model**: `CityDefinition` (geography: bbox, zips, available_sources), `SearchProfile` (user preferences: budget, diet, tram, notifications), and `SourceDefinition` (global platform registry with per-city params). This separation ensures S003 multi-user transition requires only adding `owner_user_id` to profiles — no structural changes.

**LOD300:** `_aos/work_packages/S002-P001-WP001/LOD300_S002-P001-WP001.md`
**Mockup:** `_aos/work_packages/S002-P001-WP001/mockup_html/`

### 5.2 S002-P001-WP002: Zurich + Bern City Definitions

Creates city definition files for Zurich (bbox, 25 PLZ, VBZ tram area) and Bern (bbox, 18 PLZ, Bernmobil area). Migrates Basel to the new structure. Populates the global source registry (`data/sources.json`) with per-city `city_params`. Creates single default search profile targeting Basel. City definitions are geography-only — no user preferences.

**LOD300:** `_aos/work_packages/S002-P001-WP002/LOD300_S002-P001-WP002.md`
**Mockup:** `_aos/work_packages/S002-P001-WP002/mockup_html/`

### 5.3 S002-P002-WP001: REST API Layer (L2.5 / Track B)

FastAPI wrapper exposing `POST /search`, `GET /listings`, `GET /runs` endpoints. Accepts `profile_id` (preferred) or `city_id` (deprecated alias). Uniform JSON response envelope with pagination. Synchronous scan (10-30s). Auto-generated OpenAPI docs at `/docs`. Shares JSON persistence with CLI.

**LOD300:** `_aos/work_packages/S002-P002-WP001/LOD300_S002-P002-WP001.md`
**Mockup:** `_aos/work_packages/S002-P002-WP001/mockup_html/`

### 5.4 S002-P002-WP002: API Key Auth

Static single API key via `X-API-Key` header. Constant-time comparison (`hmac.compare_digest`). `/health` and `/docs` exempt. Missing and invalid keys return identical 401 response (no information leakage). S003 transition path documented: JWT + RBAC replaces static key.

**LOD300:** `_aos/work_packages/S002-P002-WP002/LOD300_S002-P002-WP002.md`
**Mockup:** `_aos/work_packages/S002-P002-WP002/mockup_html/`

### 5.5 S002-P003-WP001: Email/Telegram Notifications

Auto-triggered after scan when `new_results > 0`. HTML email via SMTP + Markdown message via Telegram Bot API. **Per-profile configuration** embedded in `SearchProfile.notifications` (not a separate per-city file). One retry on transient failure, then log and continue. Delivery status persisted in run record.

**LOD300:** `_aos/work_packages/S002-P003-WP001/LOD300_S002-P003-WP001.md`
**Mockup:** `_aos/work_packages/S002-P003-WP001/mockup_html/`

---

## 6. Key Architectural Decisions

| # | Decision | Choice | Alternatives Rejected | Rationale |
|---|----------|--------|----------------------|-----------|
| 1 | Data model | Three-entity: CityDefinition + SearchProfile + SourceDefinition | Monolithic per-city dirs; single flat config | Clean separation: geography (shared) vs preferences (per-user) vs platforms (global). S003 adds user_id to profiles — no restructure needed |
| 2 | City-source relationship | Many-to-many via global source registry + city_params | Per-city sources.json files | Adding a new city = add city_params entries. Adding a new source = one registry entry. No file duplication |
| 3 | Notification config | Embedded in SearchProfile | Separate per-city notifications.json file | Notifications are user preferences, not city properties. In S003, each user manages their own notifications |
| 4 | REST framework | FastAPI | Flask, Django REST, aiohttp | Auto-OpenAPI, Pydantic validation, async-ready, lightweight |
| 5 | Response format | Uniform `{"data", "meta"}` envelope | Bare JSON arrays; HAL/JSON-API | Simple, consistent, includes pagination + request tracing |
| 6 | Auth mechanism | Static X-API-Key header | Bearer token; OAuth; session | Simplest correct for single-user; S003 upgrades to JWT/RBAC |
| 7 | Persistence | Keep JSON files | SQLite; PostgreSQL | < 10K records, no concurrent writes. DB migration in S003 |

---

## 7. S003 Transition Path

| S002 Entity | S003 Change |
|-------------|-------------|
| `data/profiles/{id}.json` (SearchProfile) | Gains `owner_user_id` → PostgreSQL `search_profiles` table |
| `data/cities/{id}.json` (CityDefinition) | No structural change → PostgreSQL `cities` table |
| `data/sources.json` (SourceDefinition[]) | No change → PostgreSQL `sources` + `city_source_params` tables |
| Static `API_KEY` env var | Per-user JWT tokens with RBAC |
| `data/agent.json` (AgentMeta) | `default_profile_id` becomes per-user preference |
| JSON persistence (listings, runs) | PostgreSQL with row-level tenant isolation |

**Key principle:** S002 data model is SaaS-aware but single-user. No structural changes needed in S003 — only storage layer and user ownership.

---

## 8. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | Flatfox API changes (bbox format, rate limiting) | Medium | High | Scraper uses public API; monitor for 4xx; fallback to empty result |
| 2 | wgzimmer reCAPTCHA blocks intensify | Medium | Medium | Scraper returns [] gracefully; per-city behavior may differ |
| 3 | JSON persistence performance at scale | Low (S002) | Low | < 10K listings; in-memory filtering. DB migration in S003 |
| 4 | SMTP/Telegram delivery reliability | Medium | Low | Retry once; log failure; never block scan |
| 5 | Concurrent CLI + API access to JSON files | Low | Medium | Single-user assumption. Not supported — documented in spec |

---

## 9. Mockup Links

Each WP has a clickable HTML mockup. Open the `index.html` file in each `mockup_html/` directory:

| WP | Mockup Path |
|----|-------------|
| S002-P001-WP001 | `_aos/work_packages/S002-P001-WP001/mockup_html/index.html` |
| S002-P001-WP002 | `_aos/work_packages/S002-P001-WP002/mockup_html/index.html` |
| S002-P002-WP001 | `_aos/work_packages/S002-P002-WP001/mockup_html/index.html` |
| S002-P002-WP002 | `_aos/work_packages/S002-P002-WP002/mockup_html/index.html` |
| S002-P003-WP001 | `_aos/work_packages/S002-P003-WP001/mockup_html/index.html` |

---

## 10. Approval Request

**Team 00 — please review the 5 LOD300 specifications (v2.0) and HTML mockups.**

| Option | Action |
|--------|--------|
| **APPROVED** | LOD300 phase complete. Proceed to LOD400 specification for each WP. |
| **REVISIONS** | Specify which WPs need revision and what changes are required. |
| **REJECTED** | Halt S002 planning. Specify reason. |

---

*Team 110 (Builder Agent) | shaked-wg-agent | S002 LOD300 v2.0 | 2026-04-12*
