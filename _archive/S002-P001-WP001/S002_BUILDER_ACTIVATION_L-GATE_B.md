# S002 Builder Activation — L-GATE_B Entry
# Drafted by: Team 110 (shaked_arch / Claude Code)
# Authority: Team 00 (Nimrod)
# To: shaked_build (Cursor Composer)
# Date: 2026-04-12
# Gate: L-GATE_B (Build + QA)

---

## Your Identity

- **ID:** shaked_build
- **Role:** Builder agent
- **Engine:** Cursor Composer
- **Project:** Shaked WG Basel (shaked-wg-agent)
- **Scope:** Implement against LOD400 specs. This project only.

## Gate Status

L-GATE_S **PASSED** (2026-04-12). All 5 LOD400 specs validated by Team 190 (OpenAI) — PASS WITH FINDINGS (v1.1.2, 3 MINOR non-gating editorial items, zero BLOCKING). You are authorized to build.

---

## LOD400 Specs — Build Order

Build in this order. Each WP depends on the one above it.

| # | WP ID | Label | LOD400 Spec | Version | Depends On |
|---|-------|-------|-------------|---------|------------|
| 1 | S002-P001-WP001 | Config schema + scraper interface | `_aos/work_packages/S002-P001-WP001/LOD400_S002-P001-WP001.md` | v1.1.0 | — (foundation) |
| 2 | S002-P001-WP002 | Zurich + Bern city definitions | `_aos/work_packages/S002-P001-WP002/LOD400_S002-P001-WP002.md` | v1.1.0 | WP001 |
| 3 | S002-P002-WP001 | REST API layer | `_aos/work_packages/S002-P002-WP001/LOD400_S002-P002-WP001.md` | v1.1.1 | WP001 |
| 4 | S002-P002-WP002 | API key auth | `_aos/work_packages/S002-P002-WP002/LOD400_S002-P002-WP002.md` | v1.1.2 | WP003 (API layer) |
| 5 | S002-P003-WP001 | Notification digest | `_aos/work_packages/S002-P003-WP001/LOD400_S002-P003-WP001.md` | v1.1.0 | WP001 + WP003 |

**Critical:** Read each LOD400 spec top-to-bottom before implementing. Every acceptance criterion must be attempted — none skipped.

---

## Three-Entity Data Model (Key Context)

S002 replaces the flat `data/config.json` with three separated entities:

| Entity | File(s) | Purpose |
|--------|---------|---------|
| **CityDefinition** | `data/cities/{city_id}.json` | Geography only — bbox, zips, available_sources |
| **SearchProfile** | `data/profiles/{profile_id}.json` | User preferences — budget, diet, transit, city_id ref |
| **SourceDefinition** | `data/sources.json` | Global platform registry with per-city `city_params` |

- `load_config(profile_id)` resolves profile → city → sources
- Source resolution: `profile.enabled_sources ∩ city.available_sources → lookup in sources.json`
- S002 has one implicit profile (`default`). Multi-user deferred to S003.

---

## Per-WP Build Notes

### WP001 (Config Schema) — Foundation, build first
- Replaces `config.py` dataclasses: `AgentConfig` → `AgentMeta`, `Source` → `SourceDefinition + CityDefinition + SearchProfile`
- New `load_config(profile_id)` replaces old `load_config(city_id)` 
- Field rename: `tram_match_lines` → `transit_match_lines` in listing output
- NotificationConfig canonical schema: `digest_max_listings`, `min_score_threshold`, `channels: list[ChannelConfig]`
- See §2, §3 (dataclass specs), §4 (migration BEFORE/AFTER)

### WP002 (City Definitions) — Data files
- Create `data/cities/basel.json`, `data/cities/zurich.json`, `data/cities/bern.json`
- Create `data/profiles/default.json` (targets Basel)
- Update `data/sources.json` with `city_params` per city
- Create `data/agent.json` with `default_profile_id: "default"`
- `scraper_class` in sources.json is metadata only — NOT used for runtime dispatch

### WP003 (REST API) — FastAPI application
- `POST /search`, `GET /listings`, `GET /listings/{id}`, `GET /runs`, `GET /runs/{id}`, `GET /health`
- `profile_id` is the preferred parameter; `city_id` is a deprecated alias that resolves via directory scan
- Profile resolution: scan `data/profiles/*.json` for matching `city_id` field
- The spec defines WHAT (API contracts, request/response schemas), not HOW (framework internals)

### WP004 (Auth) — Router dependency
- `verify_api_key(request)` as FastAPI `Depends()` dependency — NOT ASGI middleware
- File: `shaked_wg_agent/api/auth.py`
- `hmac.compare_digest()` for constant-time comparison
- Router-level: `auth_router` (data endpoints) vs public router (health/docs)
- 401 responses byte-identical for missing and invalid key

### WP005 (Notifications) — Multi-channel digest
- Channels: email, telegram, discord, ntfy, webhook
- NotificationConfig/ChannelConfig schema defined canonically in WP001 §3.7-§3.8
- Orchestrator: iterate channels, send per enabled channel, log errors, never abort run

---

## L-GATE_B Deliverables (per WP)

For each WP, you must produce:

1. **Implementation** — all source code in `shaked_wg_agent/`, `data/`, `scripts/`
2. **Tests** — new unit + integration tests in `tests/`
3. **LOD500 as-built** — `_aos/work_packages/{WP-ID}/LOD500_asbuilt.md` using template at `_aos/lean-kit/modules/document-lifecycle/templates/LOD500_ASBUILT_TEMPLATE.md`
4. **Self-QA** — every AC marked ✅ MATCH / ⚠️ DEVIATION / ❌ MISSING in LOD500 §2

**Before declaring L-GATE_B PASS on each WP:**
- `pytest tests/ -v` — all pass
- `ruff check shaked_wg_agent/ tests/` — clean
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — 12/12 PASS

---

## What You Do NOT Do

- **Do NOT declare L-GATE_V** — that is Team 190 (OpenAI), cross-engine, immutable
- **Do NOT modify `_aos/roadmap.yaml`** — architecture agent owns it
- **Do NOT write to `_COMMUNICATION/team_00/`** — sacred folder, Team 00 only
- **Do NOT deviate from LOD400 without documented approval** — if spec is ambiguous, raise to architecture agent via `_COMMUNICATION/team_110/`
- **Do NOT write to `_aos/lean-kit/`** — physical copy, read-only for builders

---

## Iron Rules (binding)

1. Builder engine ≠ Validator engine (you=Cursor, validator=OpenAI)
2. `_aos/lean-kit/` is physical copy — never symlink
3. All `spec_ref` paths are repo-internal
4. L-GATE_V is always Team 190 — immutable, constitutional
5. Artifacts to `_COMMUNICATION/team_110/` only (never `team_00/`)

---

## Session Start Checklist

1. Read `_aos/roadmap.yaml` — confirm active milestone is S002
2. Read this activation file — confirm your identity and constraints
3. Read LOD400 spec for your current WP (start with WP001)
4. Implement against the spec — do not deviate without approval

---

*Builder activation drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S002 L-GATE_B | 2026-04-12*
