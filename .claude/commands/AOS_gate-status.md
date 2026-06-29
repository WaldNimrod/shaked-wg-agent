---
summary: "Check the current gate status and communication timeline for a work package."
category: gate
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8092`); (3) `http://127.0.0.1:8092` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team). **Front door (shell execution):** when running these calls from a shell, the canonical boilerplate front door is `scripts/aos_api_server_call.sh <team_id> <METHOD> <path> [curl_args]` (W5 W-S1) — it applies this same three-tier base resolution + actor headers in one place, so callers no longer hand-roll the curl/auth block.

Check the current gate status and communication timeline for a work package.

API endpoint: `GET {HUB_API_BASE}/api/wps/{wp_id}/status?include_timeline=true`  
(`HUB_API_BASE` defaults to `http://127.0.0.1:8092`; override via `AOS_API_BASE` env)

## Phase 0 — Parse arguments

Accept: `$ARGUMENTS` → WP ID (e.g. `AOS-V323-WP-COMMANDS-UNIFICATION`)

If empty, ask: "Enter WP ID (or partial match):"

## Phase 1 — Call API

```
GET {HUB_API_BASE}/api/wps/{wp_id}/status?include_timeline=true
```

**If API unreachable:** STOP. Instruct user: `bash scripts/start_aos_api_local.sh`  
**If 404:** suggest partial-match alternatives from `_aos/roadmap.yaml`.

## Phase 2 — Display timeline

Format response as:

```
=== GATE STATUS — {wp_id} ===================================
Label:  {label}
Status: {status}  Track: {track}  LOD: {lod_status}

── Gate Progress ────────────────────────────────────────────
{for each gate_history entry: gate | result | date | notes}

── Communication Timeline ───────────────────────────────────
{for each artifact: modified | type | path}

── Pending Action ───────────────────────────────────────────
{derive from gate_history + artifacts: awaiting verdict / blocked / ready to close / complete}

── Suggested Next Step ──────────────────────────────────────
{/AOS_gate-mandate {wp_id} {NEXT_GATE} | /AOS_qa | /AOS_validate}
=============================================================
```

## Error Handling

- API 4xx → parse detail, present to user
- API 5xx → display status; instruct user to check server logs
