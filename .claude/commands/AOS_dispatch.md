---
summary: "Dispatch inter-team task: send MSG + autonomous cross-engine exec (default) or v4 paste fallback."
category: infrastructure
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8090`); (3) `http://127.0.0.1:8090` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team).

# /AOS_dispatch

Arguments: `{to_team} {task_description} [--wp {WP_ID}] [--scenario canary|gate|qa|info] [--mandate {path}] [--workspace {path}] [--dry-run] [--paste|--no-exec]`

Minimal: `/AOS_dispatch team_90 "validate D1-D4"`

**Default:** `--exec` is ON — drives the validator engine headless via `POST /api/validation/cross-engine/exec` (canon: `methodology/AOS_CROSS_ENGINE_AUTONOMOUS_VALIDATION_v1.0.0.md`). Use `--paste` / `--no-exec` only for engines with no headless CLI (v4 fallback).

---

## Phase 0 — Parse arguments

Extract from invocation string:
- `to_team` — first positional arg. Must match `team_\d{2,3}`. If missing or invalid: print usage + exit.
- `task` — remaining non-flag text (free description). If empty: print usage + exit.
- `--wp {WP_ID}` — optional. If absent: scan `_aos/roadmap.yaml` for IN_PROGRESS WPs and take the first.
  If roadmap has none: use `"dispatch"` as subject prefix.
- `--scenario {value}` — optional. Values: `canary | gate | qa | info`. Default: `info`.
- `--mandate {path}` — optional. Mandate file for cross-engine validation (auto-resolved under `_COMMUNICATION/{to_team}/` if omitted).
- `--workspace {path}` — optional. Target repo/worktree (defaults to current project root).
- `--dry-run` — optional. Pass through to cross-engine exec API (print command, do not invoke).
- `--paste` / `--no-exec` — optional. Force v4 human-paste activation block instead of autonomous exec.
- **Exec mode:** ON by default unless `--paste` or `--no-exec` is set.

Resolve `current_team` from `_aos/governance/` (look for the file matching current session engine)
or from the activation context. Default: `team_100`.

Resolve `mandate_path` when `--exec` and no `--mandate`: newest `_COMMUNICATION/{to_team}/MANDATE_*{wp_id}*.md`.

---

## Phase 1 — Send message via API

```
POST {AOS_API_BASE}/api/messaging/send
X-Actor-Team-Id: {current_team}
Content-Type: application/json

{
  "from_team": "{current_team}",
  "to_team": "{to_team}",
  "subject": "[{scenario}] {task}",
  "body": "ראה mandate ב-_COMMUNICATION/{to_team}/ — בקשה לביצוע: {task}",
  "type": "informal",
  "related_wp": "{wp_id}",
  "expects_response": true
}
```

When `--scenario gate`, use `type: "task"` with ADR043 continuation fields:

```json
"type": "task",
"next_step": "Execute cross-engine validation per mandate",
"handoff_to": "{to_team}",
"handoff_context_pointer": "{mandate_path}"
```

AOS_API_BASE defaults to `http://127.0.0.1:8090`.

On HTTP 2xx: extract `msg_id` and `activation_hint` from response JSON.
On any error: print `[DISPATCH ERROR] {status_code}: {detail}` — stop. Do not display partial output.

---

## Phase 2 — Autonomous exec OR v4 paste fallback

### 2a — Autonomous (default: `--exec` and no `--paste`)

```
POST {AOS_API_BASE}/api/validation/cross-engine/exec
X-Actor-Team-Id: {current_team}
Content-Type: application/json

{
  "validator_team": "{to_team}",
  "wp_id": "{wp_id}",
  "mandate_path": "{mandate_path}",
  "workspace": "{workspace}",
  "dry_run": {true|false}
}
```

On HTTP 200: display inline (ADR032):

```
── cross-engine validation result — {to_team} | {msg_id} ──
  engine     : {resolved_engine}  model: {model}
  workspace  : {workspace}
  mandate    : {mandate_path}
  log        : {log_path}
  command    : {command joined}
  verdict    : {verdict_flag} → {verdict_file}
```

On HTTP 503 (`no_headless_cli`): fall through to Phase 2b with label *fallback — target engine has no headless CLI*.

On HTTP 422 (IR#1 / missing mandate): print error and stop.

### 2b — v4 paste fallback (`--paste` / `--no-exec` / CLI unavailable)

Title and instructions are OUTSIDE the fenced block. Block contains clean prompt text ONLY.

── פרומפט אקטיבציה (fallback — only when the target engine has no headless CLI) — סשן {to_team} | {msg_id} ──
📋 העתק את הבלוק → פתח Claude Desktop חדש → הדבק כהודעה ראשונה

```
{activation_hint — verbatim, no additions}
```

---

## Phase 3 — Display send confirmation + watch command

```
✉  Sent: {msg_id} → {to_team} | "[{scenario}] {task}"
📡 Monitor: /AOS_mail --watch {msg_id}
```

On `--exec` with verdict: append `Verdict: {verdict_flag}` line.

Exit. No blocking wait.

## Error Handling

| Condition | Action |
|-----------|--------|
| Invalid or missing `to_team` / empty task | Print usage; do not call API |
| HTTP non-2xx from `/api/messaging/send` | `[DISPATCH ERROR] {code}: {detail}` — stop (no partial output) |
| HTTP 422 from cross-engine exec | Print IR#1 / mandate error — stop |
| HTTP 503 (`no_headless_cli`) | Fall back to Phase 2b paste block |
| Response JSON missing `msg_id` / `activation_hint` (paste path) | Re-fetch or surface parse error; do not fabricate |
| API unreachable | Same as HTTP error; user may start `AOS` API on `127.0.0.1:8090` |
