# S002 LOD400 Re-Validation Result (L-GATE_S, v1.1.0)
**Validator:** Team 190 (shaked_val / OpenAI)  
**Date:** 2026-04-12  
**Gate:** L-GATE_S (Spec + Authorization)  
**Overall Verdict:** FAIL

## Re-Validation Scope

Validated v1.1.0 of all five S002 LOD400 specs against:
- their parent LOD300 specs,
- the Team 190 checklist (12 per-doc + 7 cross-WP checks),
- current code baseline (`config.py`, `scrapers/base.py`, `runner.py`, `persistence.py`),
- and S001 LOD400 reference style.

## Per-WP Verdicts

| WP | Verdict | Findings |
|----|---------|----------|
| S002-P001-WP001 | PASS WITH FINDINGS | Canonical notifications schema and `transit_match_lines` rename are fixed. Remaining finding: signature code blocks in §4 are acceptable as contract declarations but still borderline under checklist #11. |
| S002-P001-WP002 | PASS WITH FINDINGS | Notifications shape now matches WP001; `scraper_class` runtime ambiguity resolved as informational metadata only (§2.2 note). Remaining finding: schema constraints for IDs are stricter than WP001 regex in §3.1. |
| S002-P002-WP001 | FAIL | **BLOCKING:** profile resolution is specified but not actually applied in `POST /search` flow (§2.4.2 uses `load_config()`/`run_scan(cfg=cfg)` without the resolved profile), leaving profile-aware behavior non-executable as written. |
| S002-P002-WP002 | FAIL | **BLOCKING:** still not fully traceable to parent LOD300 contract; LOD300 specifies middleware-stack interface `auth_middleware(request, call_next)` while LOD400 redefines router dependency interface `auth_middleware(request)` without updating parent contract. |
| S002-P003-WP001 | PASS WITH FINDINGS | Canonical reference to WP001 notifications schema is fixed (§3.1–§3.2). Remaining finding: substantial implementation-level prescription persists in multiple sections (especially §2.2–§2.7), still heavy for LOD400 checklist #11. |

## Cross-WP Consistency

| Check | Verdict | Notes |
|-------|---------|-------|
| Three-entity model consistency | PASS WITH FINDINGS | Core entity split is now coherent; remaining ID-regex mismatch persists between WP001 and WP002 schema patterns. |
| NotificationConfig channels model | PASS | Canonicalized across WP001/WP002/WP005 with `digest_max_listings`, `min_score_threshold`, `channels`. |
| API profile_id parameter | FAIL | Alias strategy is now aligned (directory scan), but WP003 endpoint flow still does not consistently apply resolved `profile_id` to scan execution/filtering behavior in spec pseudocode. |
| Error envelope consistency | PASS WITH FINDINGS | Envelope shapes align; auth doc now commits to one path, but exact 401 byte-identical requirement remains implementation-sensitive and should be explicitly bound to one response mechanism. |
| Run record consistency | PASS | `profile_id`/`city_id` and `notification_sent` extensions are now coherently represented across WP001/WP003/WP005. |
| LOD300→LOD400 traceability | FAIL | Auth WP still diverges from parent interface contract; API WP profile-driven behavior is incompletely traceable in route flow. |
| Dependency chain | PASS | Declared dependencies remain acyclic and logically ordered. |

## Detailed Findings

### S002-P002-WP001 (REST API) — Detailed Findings
- **BLOCKING:** In §2.4.2 (`POST /search`), `profile_id = resolve_profile_id(...)` is computed but not used to load config or run scan. The flow then calls `load_config()` and `run_scan(cfg=cfg)` without binding the resolved profile. This conflicts with the same document’s profile-aware contract and ACs around profile/city alias behavior.
- **MAJOR:** In `GET /listings` (§2.4.3), `profile_id` is resolved but filtering logic only applies `city_id`, `min_score`, `status`, and `source`; profile-based filtering behavior is not explicit/executable when only `profile_id` is provided.

### S002-P002-WP002 (API key auth) — Detailed Findings
- **BLOCKING:** Parent LOD300 defines middleware interface `auth_middleware(request, call_next)` in interface contracts and interaction diagrams, but LOD400 switches to router dependency (`Depends(auth_middleware)`, signature `auth_middleware(request)`) without harmonizing parent contract language. At L-GATE_S, this remains a contract drift between LOD levels.
- **MAJOR:** The document mixes middleware terminology with dependency-injection semantics; this is implementable, but normative wording should be singular and explicit to prevent builder interpretation drift.

### S002-P003-WP001 (Notifications) — Detailed Findings
- **MAJOR (checklist #11):** Although schema consistency is fixed, §2.2–§2.7 still prescribes detailed class/method bodies and transport-level call sequences at near-implementation granularity. This is improved but still heavy for strict LOD400 “WHAT over HOW”.

### S002-P001-WP002 (Data files) — Detailed Findings
- **MINOR:** JSON schema pattern in §3.1 (`city_id` as `^[a-z]+$`) is stricter than WP001 canonical ID regex (`^[a-z][a-z0-9-]{0,29}$`). Not blocking for current IDs, but cross-WP normalization is recommended.

## Resolved Since v1.0.0

Confirmed fixed from prior FAIL package:
1) NotificationConfig/ChannelConfig cross-WP mismatch — **resolved**.  
2) `tram_match_lines` vs `transit_match_lines` naming drift — **resolved at spec level**.  
3) Auth “builder chooses” Option A/B ambiguity — **resolved** (single path declared).  
4) `scraper_class` runtime ambiguity — **resolved** (informational metadata).  
5) City/profile alias strategy divergence — **substantially improved** (directory-scan approach aligned).

## Recommendation

**HALT (targeted).** Do **not** authorize full S002 builder start yet.  
Authorize only after these two BLOCKING corrections are merged:
1) **WP003:** Make `POST /search` and related API flows explicitly apply resolved `profile_id` end-to-end (load + run + filtering semantics).  
2) **WP004:** Reconcile LOD300 and LOD400 auth contract wording/interface (either update LOD300 contract to dependency model or align LOD400 to declared middleware contract).

After those two fixes, this package is likely to pass with only non-blocking editorial findings.

Routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S002 LOD400 re-validation | 2026-04-12