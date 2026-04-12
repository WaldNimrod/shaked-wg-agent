# Team 190 Validation Routing — S002 L-GATE_V (Implementation Validation)
# Drafted by: Team 110 (shaked_arch / Claude Code)
# Authority: Team 00 (Nimrod)
# To: Team 190 (shaked_val / OpenAI)
# Date: 2026-04-12
# Gate: L-GATE_V (Validate + Lock)

---

## Context

L-GATE_B is complete. The builder (Cursor Composer) has implemented all 5 S002 work packages against LOD400 specs. 81 tests pass, ruff clean, validate_aos.sh 12/12 PASS. Your job: **independently validate the implementation against each LOD400 AC**. Do NOT rely on the builder's LOD500 self-assessment — form your own verdict.

**Iron Rule:** Your engine (OpenAI) ≠ builder engine (Cursor Composer). You have NOT been involved in building.

---

## What to Validate

For each WP, compare the **implementation** (source code, data files, tests) against the **LOD400 spec** acceptance criteria. Then cross-check against the builder's **LOD500 as-built** fidelity table.

| # | WP ID | LOD400 Spec | LOD500 As-Built | Key Source Files |
|---|-------|-------------|-----------------|------------------|
| 1 | S002-P001-WP001 | `_aos/work_packages/S002-P001-WP001/LOD400_S002-P001-WP001.md` (v1.1.0) | `LOD500_asbuilt.md` | `shaked_wg_agent/config.py`, `__main__.py`, `runner.py`, `scorer.py`, `scrapers/*.py` |
| 2 | S002-P001-WP002 | `_aos/work_packages/S002-P001-WP002/LOD400_S002-P001-WP002.md` (v1.1.0) | `LOD500_asbuilt.md` | `data/cities/*.json`, `data/profiles/default.json`, `data/agent.json`, `data/sources.json` |
| 3 | S002-P002-WP001 | `_aos/work_packages/S002-P002-WP001/LOD400_S002-P002-WP001.md` (v1.1.1) | `LOD500_asbuilt.md` | `shaked_wg_agent/api/app.py`, `routes.py`, `schemas.py`, `deps.py` |
| 4 | S002-P002-WP002 | `_aos/work_packages/S002-P002-WP002/LOD400_S002-P002-WP002.md` (v1.1.2) | `LOD500_asbuilt.md` | `shaked_wg_agent/api/auth.py`, `app.py` |
| 5 | S002-P003-WP001 | `_aos/work_packages/S002-P003-WP001/LOD400_S002-P003-WP001.md` (v1.1.0) | `LOD500_asbuilt.md` | `shaked_wg_agent/notifier/*.py`, `runner.py` |

---

## Per-WP Validation Checklist

### WP001 — Config Schema + Scraper Interface (AC-01 to AC-45)

| # | Check | What to verify |
|---|-------|----------------|
| 1 | Dataclass fidelity | `AgentMeta`, `CityDefinition`, `SearchProfile`, `SourceDefinition`, `ResolvedSource`, `CitySourceParams`, `BoundingBox`, `NotificationConfig`, `ChannelConfig` all present in `config.py` with fields matching LOD400 §3 |
| 2 | `load_config(profile_id)` | Function exists, loads profile → city → sources, returns `ProjectConfig`. Handles `None` profile_id via `agent.json` default |
| 3 | Source resolution | `profile.enabled_sources ∩ city.available_sources → sources.json lookup` produces `ResolvedSource[]` |
| 4 | Validation | `budget_min < budget_max`, `enabled_sources ⊆ available_sources`, `digest_max_listings` range, `min_score_threshold` range |
| 5 | CLI | `--profile` flag, `--city` deprecated alias, `--triggered-by`, `--sources` filter |
| 6 | Scraper interface | `BaseScraper.__init__` takes `CityDefinition + ResolvedSource`, `run_scan` receives profile-aware config |
| 7 | Scorer | Uses `SearchProfile` fields; `transit_lines` / `transit_match_lines`; legacy `tram_match_lines` still scored |
| 8 | Runner | `run_scan(profile_id, ...)`, persists `city_id`/`profile_id` on listings and runs, `triggered_by` field |

### WP002 — City Definitions (AC-01 to AC-28)

| # | Check | What to verify |
|---|-------|----------------|
| 1 | City files | `data/cities/basel.json`, `zurich.json`, `bern.json` — all have `city_id`, `city_name`, `country`, `bounding_box`, `zip_filter`, `available_sources` |
| 2 | Source registry | `data/sources.json` has `city_params` per city for each source |
| 3 | Default profile | `data/profiles/default.json` with `profile_id: "default"`, `city_id: "basel"`, budget/diet/transit fields |
| 4 | Agent meta | `data/agent.json` with `default_profile_id: "default"` |
| 5 | Legacy migration | `data/config.json` renamed to `.bak` |
| 6 | `scraper_class` | Present in sources.json as informational metadata, NOT used for runtime dispatch |

### WP003 — REST API (AC-01 to AC-29)

| # | Check | What to verify |
|---|-------|----------------|
| 1 | Factory pattern | `create_app()` in `api/app.py` returns FastAPI instance |
| 2 | Endpoints | `POST /search`, `GET /listings`, `GET /listings/{id}`, `GET /runs`, `GET /runs/{id}`, `GET /health` — all exist and respond |
| 3 | Schemas | Pydantic models match LOD400 §2 request/response contracts. `ListingResponse`/`RunResponse` include `city_id`/`profile_id` |
| 4 | Profile resolution | `profile_id` preferred; `city_id` deprecated alias resolved via directory scan of `data/profiles/*.json` |
| 5 | `POST /search` | Passes resolved `profile_id` to `load_config(profile_id)` — the end-to-end fix from v1.1.1 |
| 6 | `GET /listings` | Profile-aware filtering when `profile_id` provided |
| 7 | CORS | Configurable via `API_CORS_ORIGINS` env var |
| 8 | Request ID | `X-Request-ID` header middleware |
| 9 | Error responses | `ErrorResponse` envelope: `{"error": {"code": "...", "message": "...", "detail": ...}}` |

### WP004 — API Key Auth (AC-01 to AC-17)

| # | Check | What to verify |
|---|-------|----------------|
| 1 | Dependency function | `verify_api_key(request)` in `api/auth.py`, usable with `Depends()` |
| 2 | Router separation | `auth_router` (protected) vs public router (/health, /docs, /openapi.json) |
| 3 | `hmac.compare_digest()` | Used for key comparison — NOT `==` |
| 4 | Error bodies | 401 body: `{"error": {"code": "UNAUTHORIZED", ...}}` — byte-identical for missing and invalid key |
| 5 | 500 on missing env | Missing `API_KEY` → 500 with `INTERNAL_ERROR` on protected endpoints |
| 6 | `/health` | Includes `auth_configured` boolean field |
| 7 | No key in logs | API key value never appears in any log output |
| 8 | Exempt paths | `/health`, `/docs`, `/openapi.json` — 200 without `X-API-Key` |

### WP005 — Notification Digest (core ACs)

| # | Check | What to verify |
|---|-------|----------------|
| 1 | Channel notifiers | `EmailNotifier`, `TelegramNotifier`, `DiscordNotifier`, `NtfyNotifier`, `WebhookNotifier` — all implement `BaseNotifier` |
| 2 | Digest builder | `build_digest_payload` produces structured payload from new listings + profile + city |
| 3 | Orchestrator | `notify_digest` iterates enabled channels, sends per channel, logs errors, never aborts run |
| 4 | Runner integration | `runner.py` calls `notify_digest` when `new_results > 0` and profile has `notifications`; sets `notification_sent` on run record |
| 5 | Config schema | Uses `NotificationConfig`/`ChannelConfig` from WP001 §3.7-§3.8 (canonical source) |
| 6 | `digest_max_listings` | Respected — caps listings in digest payload |
| 7 | `min_score_threshold` | Respected — filters listings below threshold |

---

## Cross-WP Consistency Checks

| # | Check | What to verify |
|---|-------|----------------|
| 1 | Data model coherence | All WPs use the same three-entity model (CityDefinition, SearchProfile, SourceDefinition) — no leftover flat-config patterns |
| 2 | `profile_id` end-to-end | CLI → config → runner → API → notifications all pass `profile_id` consistently |
| 3 | `transit_match_lines` | Field name consistent across config, scrapers, scorer, API schemas, listing output — no stale `tram_match_lines` in new code (legacy scoring accepted) |
| 4 | Auth integration | API endpoints properly gated: protected routes require `X-API-Key`, exempt routes do not |
| 5 | NotificationConfig schema | Single canonical definition in WP001 config.py; WP002 default profile uses it; WP005 notifier consumes it |
| 6 | Error envelope | `ErrorResponse` format consistent across API error responses (WP003) and auth errors (WP004) |
| 7 | Test coverage | 81 tests cover config, persistence, scorer, scrapers, API, notifier — no WP left untested |

---

## Validation Procedure

1. **Read each LOD400 spec independently** — do NOT start from the LOD500 as-built
2. **Review implementation against each AC** — read the source code, check data files, verify test coverage
3. **Form your own fidelity assessment** per AC: ✅ MATCH / ⚠️ DEVIATION / ❌ MISSING
4. **Cross-check against LOD500** — reconcile any discrepancies between your assessment and the builder's self-QA
5. **Run cross-WP consistency checks**
6. **Classify findings:** BLOCKER / MAJOR / MINOR

---

## Test Evidence (builder-reported)

```
pytest tests/ -v: 81 passed in 0.35s
ruff check: clean
validate_aos.sh: 12/12 PASS
```

You should **independently verify** these pass. Run:
```bash
python3 -m pytest tests/ -v --tb=short
ruff check shaked_wg_agent/ tests/
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

---

## Output

Write your validation result to:
```
_COMMUNICATION/team_190/S002_L-GATE_V_VALIDATION_RESULT.md
```

**Required sections:**
1. Per-WP verdict table (PASS / CONDITIONAL PASS / FAIL) with findings
2. Cross-WP consistency check results
3. Fidelity reconciliation (your assessment vs builder's LOD500)
4. Overall verdict: PASS / CONDITIONAL PASS / FAIL
5. If PASS: LOD500 sign-off text for §6 of each WP

**On PASS:** Each LOD500 `lod_status` changes from FINAL to LOCKED. Architecture agent (Team 110) updates `roadmap.yaml`.

---

## Pre-conditions

- L-GATE_B complete: all 5 WPs implemented, 5 LOD500 as-builts present
- AOS governance: 12 PASS / 0 FAIL
- Tests: 81 passed, ruff clean
- Builder engine: Cursor Composer ≠ Validator engine: OpenAI ✅

---

*L-GATE_V routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S002 L-GATE_V | 2026-04-12*
