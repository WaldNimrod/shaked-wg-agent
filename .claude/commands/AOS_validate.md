---
summary: "Execute a canonical constitutional or technical validation against a gate mandate."
category: gate
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8092`); (3) `http://127.0.0.1:8092` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team). **Front door (shell execution):** when running these calls from a shell, the canonical boilerplate front door is `scripts/aos_api_server_call.sh <team_id> <METHOD> <path> [curl_args]` (W5 W-S1) — it applies this same three-tier base resolution + actor headers in one place, so callers no longer hand-roll the curl/auth block.

Execute a canonical constitutional or technical validation against a gate mandate.

> **Layer:** Constitutional — "Is the process and delivery sound?"  
> **NOT:** Functional acceptance / AC testing (use `/AOS_qa` for that)  
> **Info-barrier:** At L-GATE_VALIDATE with `existing_qa_verdict`, QA rationale/findings are redacted — only verdict flag passes through.

API endpoint: `POST {HUB_API_BASE}/api/verdicts/validate`  
(`HUB_API_BASE` defaults to `http://127.0.0.1:8092`; override via `AOS_API_BASE` env)

**Invocation:** `/AOS_validate <mandate-path> [--qa-verdict <qa-verdict-path>]`

## Phase 0 — Parse mandate

Accept `$ARGUMENTS` → mandate path + optional `--qa-verdict` path.  
If missing, ask for mandate path. Parse YAML frontmatter: `gate`, `wp`, `to`, `from`, `resubmission_round`.

## Phase 1 — Load context via API (info-barrier applied)

If `--qa-verdict` path provided → read QA verdict file into `existing_qa_verdict` dict.

```
POST {HUB_API_BASE}/api/verdicts/validate
{"wp_id": "{wp}", "gate": "{gate}", "team_id": "{to}",
 "existing_qa_verdict": {qa_verdict_or_null}}
```

**If API unreachable:** STOP. Instruct user: `bash scripts/start_aos_api_local.sh`

At L-GATE_VALIDATE: `info_barrier_applied=true` means only QA verdict flag is visible in context — not findings/rationale. This is constitutional separation of concerns.

## Phase 2 — Execute validation

Check: Iron Rule compliance, spec fidelity, team authority, methodology adherence, boundary violations, governance drift.  
For resubmissions: verify each prior finding is addressed.  
Compile findings by severity: BLOCKER | MAJOR | MINOR | NOTE.

## Phase 3 — Determine verdict

- 0 BLOCKERs → PASS or PASS_WITH_FINDINGS
- Any BLOCKER → BLOCK (with resubmission path)

## Phase 4 — Write verdict artifact

Write to `_COMMUNICATION/team_{to}/VERDICT_{WP_ID}_{GATE}_v{N}.md` (ADR032 always-inline block).

## Phase 5 — Verdict notification (API-first — ADR043 §4 + §5)

```
source lean-kit/modules/team-messaging/scripts/msg_preflight.sh --verbose
# API_ONLINE=1 → POST (body below, X-Actor-Team-Id: {to})
# 4xx → EXIT (do NOT fallback — §5)   |   5xx/offline → fallback + msg_deliver_file
```

POST body (preferred wrapper: `msg_curl POST "/api/messaging/send" "$payload"` — auto-injects `X-Project-Id` per ADR043 §6):
```
POST {HUB_API_BASE}/api/messaging/send
Headers: X-Actor-Team-Id: {to}, X-Project-Id: $(msg_detect_project_id)
{
  "from_team": "{to}", "to_team": "{from}", "type": "task_response",
  "subject": "Verdict ready: {gate} for {WP_ID} — {verdict}",
  "body": "## Validation Verdict: {verdict}\n\nPath: _COMMUNICATION/team_{to}/VERDICT_{WP_ID}_{GATE}_v{N}.md\n\n**Summary:** {one_line_findings_summary}",
  "in_response_to": "{mandate_msg_id_if_known}", "expects_response": false
}
```

`mandate_msg_id_if_known`: check `_COMMUNICATION/team_{to}/` for `MSG-HUB-*.md` with matching `related_wp` + `type: task`; omit if not found.

**Fallback:** write to `_COMMUNICATION/team_{from}/MSG-HUB-{YYYYMMDD}-{NNN}.md` then `msg_deliver_file <path>` (branch-safe push to origin/main per ADR043 §4). Push failure = verdict not delivered.

## Phase 6 — Auto-capture verdict to orchestrator inbox (W4 — Finding 1, degrade-safe)

After the verdict artifact is written (Phase 4), the closing step deposits a `verdict` notice into the
orchestrator's DB inbox so the orchestrating session auto-reads it on its next turn — **no human relay**
(LOD300 §4.1). One thin call to the shared helper; degrade-safe (never blocks this session):

```bash
bash scripts/aos_session_ctl.sh capture verdict \
  "$(bash scripts/aos_session_ctl.sh resolve-orchestrator "{wp}")" team \
  "{gate} {verdict} — {wp}" \
  "_COMMUNICATION/team_{to}/VERDICT_{WP_ID}_{GATE}_v{N}.md" \
  "{gate}" "{wp}" || true   # never block closure on capture (degrade-safe; matches aos_session_close)
```

Recipient resolution = `$AOS_ORCHESTRATOR_TEAM` → WP owning-team from register → `team_100` (Finding 4).
On API-unreachable / non-2xx / PK conflict → the helper appends `event=capture … degrade=1` to
`_COMMUNICATION/_log/messages.log` and continues (AC5/AC9). In ADDITION to the Phase-5 file MSG
(dual-write compat window, AC10) — the v2 DB inbox is the canonical cross-engine relay.

## Error Handling

- API 4xx → EXIT with error (do NOT silently fallback — ADR043 §5)
- API 5xx / offline → file fallback + branch-safe push
- gate not recognized → warn, continue without info-barrier
- W4 capture (Phase 6) never blocks: degrade to `messages.log` on any failure.
