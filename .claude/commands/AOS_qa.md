---
summary: "Execute a canonical QA functional acceptance process against a gate mandate."
category: gate
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8092`); (3) `http://127.0.0.1:8092` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team).

Execute a canonical QA functional acceptance process against a gate mandate.

> **Layer:** Functional acceptance — "Does the code do what the spec says?"  
> **NOT:** Constitutional validation (use `/AOS_validate` for that)

API endpoint: `POST {HUB_API_BASE}/api/verdicts/qa`  
(`HUB_API_BASE` defaults to `http://127.0.0.1:8092`; override via `AOS_API_BASE` env)

**Invocation:** `/AOS_qa <mandate-path>`

## Phase 0 — Parse mandate

Accept `$ARGUMENTS` → mandate path (e.g. `_COMMUNICATION/team_50/MANDATE_{WP_ID}_{GATE}_v1.0.0.md`).  
If missing, ask for it. Parse YAML frontmatter: `gate`, `wp`, `to` (team_id), `from`.  
If frontmatter incomplete → WARN and ask user to confirm interpretation.

## Phase 1 — Load context via API

```
POST {HUB_API_BASE}/api/verdicts/qa
{"wp_id": "{wp}", "gate": "{gate}", "team_id": "{to}"}
```

**If API unreachable:** STOP. Instruct user: `bash scripts/start_aos_api_local.sh`

Use returned `context.team_role`, `context.wp_spec_excerpt` to orient QA scope.

## Phase 2 — Execute QA process

Check each AC in the mandate: verify delivered behavior matches spec.  
Run applicable tests (`validate_aos.sh`, pytest, browser verification per mandate scope).  
Compile findings by severity: BLOCKER | MAJOR | MINOR | NOTE.

## Phase 3 — Determine verdict

- 0 BLOCKERs + 0 MAJORs → PASS (or PASS_WITH_FINDINGS if MINOR/NOTEs exist)
- Any BLOCKER or MAJOR → BLOCK

## Phase 4 — Write verdict artifact

Write to `_COMMUNICATION/team_{to}/VERDICT_{WP_ID}_{GATE}_v{N}.md` (ADR032 always-inline block).

## Phase 5 — Verdict notification (API-first — ADR043 §4 + §5)

```
source lean-kit/modules/team-messaging/scripts/msg_preflight.sh --verbose
# API_ONLINE=1 → POST /api/messaging/send (body below, X-Actor-Team-Id: {to})
# API 4xx → EXIT (bad schema / auth) — do NOT fallback silently per §5
# API offline / 5xx → fallback: write MSG + msg_deliver_file (branch-safe push)
```

POST body (preferred wrapper: `msg_curl POST "/api/messaging/send" "$payload"` — auto-injects `X-Project-Id` per ADR043 §6):
```
POST {HUB_API_BASE}/api/messaging/send
Headers: X-Actor-Team-Id: {to}, X-Project-Id: $(msg_detect_project_id)
{
  "from_team": "{to}", "to_team": "{from}", "type": "task_response",
  "subject": "Verdict ready: {gate} for {WP_ID} — {verdict}",
  "body": "## QA Verdict: {verdict}\n\nPath: _COMMUNICATION/team_{to}/VERDICT_{WP_ID}_{GATE}_v{N}.md\n\n**Summary:** {one_line_findings_summary}",
  "in_response_to": "{mandate_msg_id_if_known}", "expects_response": false
}
```

`mandate_msg_id_if_known`: check `_COMMUNICATION/team_{to}/` for `MSG-HUB-*.md` with matching `related_wp` + `type: task`; omit if absent.

**Fallback:** write `_COMMUNICATION/team_{from}/MSG-HUB-{YYYYMMDD}-{NNN}.md` then `msg_deliver_file <path>` (ADR043 §4). Push failure = verdict not delivered — surface error.

## Phase 6 — Auto-capture verdict to orchestrator inbox (W4 — Finding 1, degrade-safe)

After the verdict artifact is written (Phase 4), the closing step deposits a `verdict` notice into the
orchestrator's DB inbox so the orchestrating session auto-reads it on its next turn — **no human relay**
(LOD300 §4.1). One thin call to the shared helper; degrade-safe (never blocks this session):

```bash
bash scripts/aos_session_ctl.sh capture verdict \
  "$(bash scripts/aos_session_ctl.sh resolve-orchestrator "{wp}")" team \
  "{gate} {verdict} — {wp}" \
  "_COMMUNICATION/team_{to}/VERDICT_{WP_ID}_{GATE}_v{N}.md" \
  "{gate}" "{wp}" || true   # never block closure on capture (degrade-safe; parity with AOS_validate)
```

Recipient resolution = `$AOS_ORCHESTRATOR_TEAM` → WP owning-team from register → `team_100` (Finding 4).
On API-unreachable / non-2xx / PK conflict → the helper appends `event=capture … degrade=1` to
`_COMMUNICATION/_log/messages.log` and continues (AC5/AC9). In ADDITION to the Phase-5 file MSG
(dual-write compat window, AC10) — the v2 DB inbox is the canonical cross-engine relay.

## Error Handling

- API 4xx → EXIT with error (do NOT silently fallback — ADR043 §5)
- API 5xx / offline → file fallback + branch-safe push
- AC not verifiable (missing test, no access) → flag as SKIP with justification
- W4 capture (Phase 6) never blocks: degrade to `messages.log` on any failure.
