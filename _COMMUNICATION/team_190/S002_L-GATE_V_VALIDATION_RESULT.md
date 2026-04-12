# S002 L-GATE_V Validation Result (Validate + Lock)
**Validator:** Team 190 (shaked_val / OpenAI)  
**Date:** 2026-04-12  
**Gate:** L-GATE_V (Validate + Lock)  
**Overall Verdict:** PASS

## Revalidation (post-fix)

**Revalidation run at:** 2026-04-12 10:05 IDT  

Independent checks re-run:
- `python3 -m pytest tests/ -q` → **81 passed**
- `ruff check shaked_wg_agent/ tests/` → **clean**
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → **12/12 PASS**

## Prior blockers — resolved

1. **WP002 AC-30:** `data/sources.json.bak` now exists (restored S001 flat-format backup).  
2. **Documentation drift:** `docs/DEVELOPER_GUIDE.md` corrected to match implementation:
   - Removed non-existent CLI flags (`--triggered-by`, `--sources`)
   - Replaced `ConfigValidationError` with `ValueError` / `FileNotFoundError`
   - Corrected stale-listing behavior (dropped directly; no intermediate `"stale"` status)

## Evidence (independent)

- `python3 -m pytest tests/ -v --tb=short` → **81 passed**  
- `ruff check shaked_wg_agent/ tests/` → **All checks passed**  
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → **12/12 PASS**

## Per-WP Verdicts

| WP | LOD400 | LOD500 | Verdict | Findings (summary) |
|----|--------|--------|---------|--------------------|
| S002-P001-WP001 | v1.1.0 | `LOD500_asbuilt.md` | PASS | Implementation matches ACs; tests cover config/runner/scorer/api integration points. |
| S002-P001-WP002 | v1.1.0 | `LOD500_asbuilt.md` | PASS | City files + registry + default profile + agent meta + migrations match LOD400 (including `.bak` artifacts). |
| S002-P002-WP001 | v1.1.1 | `LOD500_asbuilt.md` | PASS | Endpoints + schemas + request-id + CORS + error envelopes behave as specified; validated via tests and spot-checks. |
| S002-P002-WP002 | v1.1.2 | `LOD500_asbuilt.md` | PASS | Auth dependency uses `hmac.compare_digest`, exact 401 body, exempt `/health` + `/docs` + `/openapi.json`, 500 when `API_KEY` unset. |
| S002-P003-WP001 | v1.1.0 | `LOD500_asbuilt.md` | PASS | Notifier package present; digest builder filters/sorts/truncates; orchestrator never raises; runner writes `notification_sent`. |
| Documentation | — | — | PASS | Developer guide matches implementation for CLI, validation errors, persistence semantics, API/auth/notifier behavior. |

## Per-WP Validation Notes (against LOD400 ACs)

### WP001 — Config Schema + Scraper Interface (S002-P001-WP001)
✅ **MATCH** across LOD400 v1.1.0 ACs, supported by:
- `shaked_wg_agent/config.py` — dataclasses, loaders, `load_config(profile_id)` resolution + logging + validations.
- `shaked_wg_agent/__main__.py` — argparse CLI with `--profile` and deprecated `--city` directory-scan resolution.
- `shaked_wg_agent/scrapers/base.py` — `BaseScraper.__init__(..., city: CityDefinition)` and `ScrapedListing.transit_match_lines`.
- `shaked_wg_agent/scorer.py` — `SearchProfile` + `transit_lines`, legacy `tram_match_lines` accepted for scoring.
- `shaked_wg_agent/runner.py` — `run_scan(profile_id, cfg, triggered_by)`, persists `city_id`/`profile_id`, and writes `notification_sent`.
- Tests: `tests/test_config.py`, `tests/test_scorer.py`, `tests/test_integration.py`.

### WP002 — City Definitions + Registry + Default Profile (S002-P001-WP002)
✅ **MATCH** for exact file contents:
- `data/cities/basel.json`, `data/cities/zurich.json`, `data/cities/bern.json` — match spec JSON exactly.
- `data/sources.json` — matches spec JSON exactly.
- `data/profiles/default.json` — matches spec JSON exactly.
- `data/agent.json` — matches spec JSON exactly.
- `data/config.json.bak` — present (migration performed for `config.json`).

❌ **MISSING (BLOCKER):**
- `data/sources.json.bak` — **absent** while LOD400 §2.5 AC-30 requires it when old `data/sources.json` existed.

### WP003 — REST API Layer (S002-P002-WP001)
✅ **MATCH** across LOD400 v1.1.1 ACs, supported by:
- `shaked_wg_agent/api/app.py` — `create_app()`, CORS (`API_CORS_ORIGINS`), request-id middleware, 500 handler, HTTPException passthrough for `{error:...}`.
- `shaked_wg_agent/api/routes.py` — `/search`, `/listings`, `/listings/{id}`, `/runs`, `/runs/{id}`, `/health`.
- `shaked_wg_agent/api/schemas.py` — Pydantic models with `extra="ignore"` for listing/run schemas.
- `shaked_wg_agent/api/deps.py` — `resolve_profile_id` via directory scan.
- Tests: `tests/test_api.py` (includes `X-Request-ID` assertion).

### WP004 — API Key Auth (S002-P002-WP002)
✅ **MATCH** across LOD400 v1.1.2 ACs, supported by:
- `shaked_wg_agent/api/auth.py` — `verify_api_key`, `hmac.compare_digest`, literal unauthorized body reused for missing/invalid.
- `shaked_wg_agent/api/app.py` — auth dependency applied only to protected router; exempt endpoints are public.
- Spot-checks: `/docs` and `/openapi.json` return 200 without `X-API-Key`.
- Tests: `tests/test_api.py` (`401` body match, `500` when `API_KEY` missing).

### WP005 — Notification Digest (S002-P003-WP001)
✅ **MATCH** for core ACs, supported by:
- `shaked_wg_agent/notifier/` package present and importable.
- `digest_builder.build_digest_payload()` filters by `min_score_threshold`, sorts, truncates by `digest_max_listings`.
- `orchestrator.notify_digest()` never raises; retries once for transient failures via `last_error_transient`.
- `runner.run_scan()` sets `run_record["notification_sent"]` when `new_results > 0` and notifications configured.
- Tests: `tests/test_notifier.py`.

## Cross-WP Consistency Checks

| Check | Verdict | Notes |
|---|---|---|
| Data model coherence | PASS | Three-entity model used; legacy flat config not read (`data/config.json` is `.bak`). |
| `profile_id` end-to-end | PASS | CLI/API/config/runner persist `profile_id` consistently; API resolves city→profile via profile-directory scan. |
| `transit_match_lines` end-to-end | PASS WITH FINDINGS | New writes use `transit_match_lines`; scorer/digest builder accept legacy `tram_match_lines` for backward compatibility. Existing `data/listings.json` may still contain legacy key until next scan rewrites entries. |
| Auth integration | PASS | Protected API routes require `X-API-Key`; `/health`, `/docs`, `/openapi.json` are exempt. |
| NotificationConfig schema | PASS | Canonical schema from WP001 consumed by WP005; default profile matches. |
| Error envelope | PASS | API and auth errors share `{"error": {"code","message","detail"}}`. |
| Test coverage | PASS WITH FINDINGS | 81 tests cover core flows; notifier channel-specific behavior is lightly tested (builder claims FULL_MATCH; minimum smoke coverage is present). |

## Documentation Validation — `docs/DEVELOPER_GUIDE.md`

**Verdict:** PASS

## Fidelity Reconciliation (Team 190 vs builder LOD500)

| WP | Builder LOD500 fidelity | Team 190 finding |
|----|--------------------------|------------------|
| WP001 | FULL_MATCH | ✅ Agree |
| WP002 | FULL_MATCH | ✅ Agree |
| WP003 | FULL_MATCH | ✅ Agree |
| WP004 | FULL_MATCH | ✅ Agree |
| WP005 | FULL_MATCH | ✅ Agree |
| Docs | N/A | ✅ PASS |

## Recommendation

**PASS L-GATE_V → authorize Validate + Lock.**

Next actions (by Team 110 / Team 00 process owners, not Team 190):
1. Lock LOD500 chain for S002 WPs (update each `LOD500_asbuilt.md` frontmatter `lod_status: LOCKED` per your governance procedure).
2. Update `_aos/roadmap.yaml` for S002 WPs to reflect gate progression and the L-GATE_V PASS record (single-writer rule applies).
