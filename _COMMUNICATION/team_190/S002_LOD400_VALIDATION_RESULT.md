# S002 LOD400 Validation Result (L-GATE_S)
**Validator:** Team 190 (shaked_val / OpenAI)  
**Date:** 2026-04-12  
**Gate:** L-GATE_S (Spec + Authorization)  
**Overall Verdict:** FAIL

## Per-WP Verdicts

| WP | Verdict | Findings |
|----|---------|----------|
| S002-P001-WP001 | FAIL | BLOCKING cross-WP schema mismatch for `SearchProfile.notifications` + `NotificationConfig/ChannelConfig` (see §3.7–§3.8 vs S002-P003-WP001 §3.1–§3.2). “No code snippets” rule violated beyond allowed short signature snippets (see §4.1–§4.6). |
| S002-P001-WP002 | FAIL | BLOCKING depends on unresolved notifications schema; `default.json` includes `digest_*` fields that don’t exist in WP001’s NotificationConfig (see §2.3). Requires decisions about source registry `scraper_class` naming vs runtime dispatch. |
| S002-P002-WP001 | FAIL | BLOCKING Listing field-name drift (`transit_match_lines` vs current `tram_match_lines`) and “all fields from listings.json” claim is not executable without specifying rename vs mapping (see §2.3 + LOD300 “ListingResponse”). Multiple new behaviors (profile/city aliasing) not aligned with S002-P001-WP001 city→profile resolution rule. |
| S002-P002-WP002 | FAIL | BLOCKING LOD400 contradicts its parent LOD300 middleware contract and leaves “builder chooses” Option A/B (see §2.1) → not executable under LOD400 rules. |
| S002-P003-WP001 | FAIL | BLOCKING notifications data model conflicts with S002-P001-WP001 NotificationConfig/ChannelConfig (see §3.1–§3.2). Large implementation-level prescriptions exceed LOD400 (“HOW” leakage) under checklist #11. |

## Cross-WP Consistency

| Check | Verdict | Notes |
|-------|---------|-------|
| Three-entity model consistency | FAIL | `SearchProfile.notifications` + channel structure differs across WPs; also stricter/different ID patterns appear in WP002 schemas vs WP001 regex rules. |
| NotificationConfig channels model | FAIL | WP001 defines `NotificationConfig(enabled, channels)` + `ChannelConfig(type,destination,enabled)` (S002-P001-WP001 §3.7–§3.8). WP003 defines `digest_max_listings/min_score_threshold/channels` + type-specific channel fields (S002-P003-WP001 §3.1–§3.2). WP002 default profile uses WP003-style fields (S002-P001-WP002 §2.3). |
| API profile_id parameter | PASS WITH FINDINGS | `profile_id` preferred + `city_id` deprecated alias appears consistently, but alias resolution logic differs from S002-P001-WP001 (“scan profiles directory”) vs API mapping fallback (needs one canonical rule). |
| Error envelope consistency | PASS WITH FINDINGS | Shape aligns (`{"error": {"code","message","detail"}}`). Auth WP correctly requires byte-identical 401 bodies, but LOD400 must remove “builder chooses” implementation ambiguity for producing exact body. |
| Run record consistency | PASS WITH FINDINGS | WP001 adds `profile_id/city_id` to run records; WP003 adds `notification_sent`. API models use `extra="ignore"` which can tolerate extensions, but fields must be named and persisted consistently (`runs.json`). |
| LOD300→LOD400 traceability | FAIL | Most WPs contain LOD400-level “builder choice” / conflicting contracts (notably auth), and several requirements conflict with the running schema/code (API listings field set). |
| Dependency chain | PASS | Declared dependencies are acyclic (WP002→WP001, auth→API, notify→WP001). Note: `_aos/roadmap.yaml` still lists these WPs at `L-GATE_E` (process mismatch to resolve). |

## Detailed Findings

### S002-P001-WP001 (City-agnostic config) — Detailed Findings
- **BLOCKING:** `NotificationConfig/ChannelConfig` schema in §3.7–§3.8 is incompatible with S002-P003-WP001 §3.1–§3.2 (digest fields + type-specific channel fields). This prevents a builder from implementing a single config schema without making design decisions.
- **MAJOR (per checklist #11, “Mixed” interpretation):** §4.1–§4.6 include multiple code-fenced “BEFORE/AFTER” blocks and CLI implementation-level detail. Short signature snippets are acceptable; larger blocks should be moved to LOD500 or rewritten as declarative contracts (tables + prose).

### S002-P001-WP002 (Data creation for cities/sources/profiles) — Detailed Findings
- **BLOCKING:** `data/profiles/default.json` includes `notifications.digest_max_listings` and `notifications.min_score_threshold` (§2.3) which do not exist in WP001’s `NotificationConfig` (§3.7). Cannot be validated/executed until the canonical notifications schema is fixed.
- **MAJOR:** `scraper_class` values (e.g., `"WgzimmerScraper"`) must be reconciled with actual runtime dispatch (current code dispatches by `source_id`, not class-name strings). LOD400 must specify whether `scraper_class` is informational or authoritative.

### S002-P002-WP001 (REST API) — Detailed Findings
- **BLOCKING:** Listing schema mismatch: LOD400 uses `transit_match_lines` in `ListingResponse` (§2.3), but current persisted schema uses `tram_match_lines` (see `data/listings.json` and `shaked_wg_agent/scrapers/base.py`). LOD400 must specify: rename persisted field vs map at API boundary (and update LOD300/LOD400 accordingly).
- **MAJOR:** City/profile aliasing behavior must match S002-P001-WP001’s defined deprecation strategy (CLI `--city` resolution). Current LOD400 introduces a different mapping fallback approach; this is a design decision that must be locked in spec.

### S002-P002-WP002 (API key auth) — Detailed Findings
- **BLOCKING:** Parent LOD300 defines a middleware-stack contract (`auth_middleware(request, call_next)`), but LOD400 §2.1 prescribes dependency-injection and explicitly allows two options (“builder chooses”). This violates LOD400 executability and LOD300 consistency.
- **BLOCKING:** “Builder chooses” (Option A/B) is not allowed at LOD400. The spec must commit to one mechanism and define exact exempt-path behavior.

### S002-P003-WP001 (Notifications) — Detailed Findings
- **BLOCKING:** Notifications schema (§3.1–§3.2) conflicts with WP001’s `NotificationConfig/ChannelConfig` (§3.7–§3.8). Needs one canonical schema across S002.
- **MAJOR (checklist #11):** Large implementation prescriptions (HTML structure, retry sleep calls, specific libraries per channel) exceed the “WHAT not HOW” constraint for LOD400 unless explicitly allowed by Team 00’s spec policy.

## Recommendation

**HALT.** Do **not** authorize builder to proceed on S002 until the BLOCKING items are resolved, primarily:
1) Canonicalize `SearchProfile.notifications` + channel schema across WPs (Team 00 decision required).  
2) Lock API listing field naming and alignment with persisted schema (`tram_match_lines` vs `transit_match_lines`).  
3) Align Auth WP LOD400 with its LOD300 contract and remove all “builder chooses” branches.  
4) Apply checklist #11 discipline (“Mixed”): keep only minimal signature snippets in LOD400; move implementation-heavy code blocks to LOD500.

Routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S002 LOD400 | 2026-04-12

