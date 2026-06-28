---
summary: "Generate a canonical gate mandate for any team/WP/gate combo (per CANON v1.6.0)."
category: gate
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8090`); (3) `http://127.0.0.1:8090` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team). **Front door (shell execution):** when running these calls from a shell, the canonical boilerplate front door is `scripts/aos_api_server_call.sh <team_id> <METHOD> <path> [curl_args]` (W5 W-S1) — it applies this same three-tier base resolution + actor headers in one place, so callers no longer hand-roll the curl/auth block.

Generate a canonical gate mandate for any team/WP/gate combination.

API endpoint: `POST {HUB_API_BASE}/api/mandates/generate`  
(`HUB_API_BASE` defaults to `http://127.0.0.1:8090`; override via `AOS_API_BASE` env)

Full mandate CANON: `lean-kit/modules/validation-quality/docs/AOS_GATE_MANDATE_CANON_v1.0.0.md`  
Governance: `governance/directives/ADR036_AOS_GATE_MANDATE_CANON_HUB_AND_SPOKES_v1.0.0.md`

## Phase 0 — Detect signal

Identify session signal (three-signal model):
- **Signal A:** New gate — no prior result for this gate
- **Signal B:** Gate PASS → mandating next gate
- **Signal C:** BLOCK/FAIL → resubmission mandate

Parse `$ARGUMENTS` for `wp_id` + `gate`. If missing, resolve interactively from roadmap.

## Phase 1 — Call API

```
POST {HUB_API_BASE}/api/mandates/generate
{"wp_id": "{wp_id}", "gate": "{gate}", "signal": "{A|B|C}",
 "gate_result": "{prior_result}", "wp_status": "{status}"}
```

**If API unreachable:** STOP. Instruct user: `bash scripts/start_aos_api_local.sh`

## Phase 2 — Write the server-rendered mandate body (ORCH-09 — verbatim, no hand-authoring)

`POST /api/mandates/generate` returns a `body` field = the **full 8-section canon mandate body**, rendered
server-side by `mandates.render_mandate_body` (pure → byte-identical for identical inputs, track-correct §8
routing per ADR044). Do **NOT** re-author the sections from the template.
1. Take the response `body` field (the complete 8-section mandate).
2. Write it **VERBATIM** to `target_path` (combined with the `frontmatter`).
3. Do not edit, summarize, or re-order sections — the gate chain, scope, cross-engine rule and next-step
   are canon-locked by the API. (`template_path` is informational only; the API output is authoritative.)

## Phase 3 — Mail delivery (API-first — ADR043 §4 + §5)

Preflight + send (helper: `lean-kit/modules/team-messaging/scripts/msg_preflight.sh`):

```
source lean-kit/modules/team-messaging/scripts/msg_preflight.sh --verbose
# API_ONLINE=1 → POST /api/messaging/send (body below, X-Actor-Team-Id header)
# API 4xx → EXIT (bad schema / missing header) — do NOT fallback per §5
# API offline / 5xx → fallback: write MSG file + msg_deliver_file (branch-safe push to origin/main)
```

POST body (API path; preferred wrapper: `msg_curl POST "/api/messaging/send" "$payload"` from `msg_preflight.sh` — auto-injects `X-Project-Id` per ADR043 §6):
```
POST {HUB_API_BASE}/api/messaging/send
Headers: X-Actor-Team-Id: {current_team_id}, X-Project-Id: $(msg_detect_project_id)
{
  "from_team": "{current_team_id}", "to_team": "{to_team}", "type": "task",
  "subject": "{gate} for {wp_id} — Round #{round_number}",
  "body": "## Mandate: {gate} for {wp_id}\n\nMandate path: {target_path}\n\nSignal: {signal_description}\n\n{scope_summary}",
  "activation_hint": "{routing_block — Phase 4 content}",
  "expects_response": true, "related_wp": "{wp_id}", "mandate_ref": "{target_path}"
}
```
Record returned `msg_id`.

**Fallback path:** write to `_COMMUNICATION/team_{to_team}/MSG-HUB-{YYYYMMDD}-{NNN}.md` using `_aos/lean-kit/modules/team-messaging/MSG-HUB.template.md`, then `msg_deliver_file <path>` (ADR043 §4). Failure to push = delivery failure — do NOT continue to Phase 4 with unpushed MSG.

## Phase 4 — Mail-pointer routing prompt (ADR032 §3.5)

Display activation block inline. Content depends on `round_number`:

**Round #1 (Signal A or first Signal B — fresh context):**

```
── Copy this block ──────────────────────────────────────────────
You are Team {to_team} — {role_title}.
Repo: {repo_path} | Engine: {engine}
Read your governance contract: _aos/governance/team_{to_team}.md

ACTION: Run /AOS_mail — your mandate for {gate} / {wp_id} is in your inbox.
Verdict path: _COMMUNICATION/team_{to_team}/VERDICT_{wp_id}_{gate}_v1.0.0.md
─────────────────────────────────────────────────────────────────
```

**Round #2+ (Signal C or second Signal B+ — continuation):**

```
── Copy this block ──────────────────────────────────────────────
Run /AOS_mail — new task in inbox: {gate} for {wp_id} (Round #{round_number}).
─────────────────────────────────────────────────────────────────
```

After the block output:
```
Mandate : {target_path}
Inbox MSG: {msg_id}
```

## Error Handling

- API 4xx → parse detail; fall back to reading MANDATE_TEMPLATE.md directly
- API 5xx → display status; instruct user to check server logs
- Messaging API error → continue with fallback MSG file write; never abort mandate flow
