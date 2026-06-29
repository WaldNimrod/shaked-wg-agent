#!/usr/bin/env bash
# aos_session_ctl.sh — W3 session register CLI (register/heartbeat/close/list/render)
# WP: AOS-V4.5-WP-SESSION-W3-DB-REGISTER
#
# Prerequisites: python3, curl optional; env AOS_API_BASE, AOS_SESSION_ENV, AOS_V3_TRUST_CLIENT_ACTOR=1 (local)
# Ports: hub API (default 8090)

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT="${SCRIPT_DIR}/session_register_client.py"

aos_session_id() {
  if [ -n "${AOS_SESSION_ID:-}" ]; then
    echo "$AOS_SESSION_ID"
    return
  fi
  local sid_file
  sid_file="$(git rev-parse --git-path aos-session-id 2>/dev/null || echo ".git/aos-session-id")"
  if [ -f "$sid_file" ]; then
    cat "$sid_file"
    return
  fi
  echo "sess-$$"
}

aos_persist_session_id() {
  local sid="$1"
  local sid_file
  sid_file="$(git rev-parse --git-path aos-session-id 2>/dev/null || echo ".git/aos-session-id")"
  mkdir -p "$(dirname "$sid_file")"
  printf '%s\n' "$sid" >"$sid_file"
}

aos_messages_log() {
  echo "${REPO_ROOT}/_COMMUNICATION/_log/messages.log"
}

# COMM-07 (v5 ENV): resolve the session's ACTING TEAM identity at SEND time — no env export needed.
# Precedence: AOS_SESSION_TEAM_ID (explicit override) → committed worktree marker `_aos/session_identity`
# → AOS_ACTOR_TEAM_ID (global default) → team_90. Reading the marker at send time (not via a child
# `register` export, which can't reach the parent shell) means a domain worktree is correctly attributed
# in BOTH parent-shell and child-process invocation. This is the fix for the team_100 identity collapse.
aos_session_team() {
  if [ -n "${AOS_SESSION_TEAM_ID:-}" ]; then printf '%s' "$AOS_SESSION_TEAM_ID"; return; fi
  local marker="${REPO_ROOT}/_aos/session_identity"
  if [ -f "$marker" ]; then
    local tid
    tid="$(head -n1 "$marker" 2>/dev/null | tr -d '[:space:]')"
    if [ -n "$tid" ]; then printf '%s' "$tid"; return; fi
  fi
  printf '%s' "${AOS_ACTOR_TEAM_ID:-team_90}"
}

# Recipient resolution (Finding 4): $AOS_ORCHESTRATOR_TEAM → WP owning-team from register → team_100.
aos_resolve_orchestrator() {
  local wp="${1:-}" owner
  if [ -n "${AOS_ORCHESTRATOR_TEAM:-}" ]; then
    echo "$AOS_ORCHESTRATOR_TEAM"
    return
  fi
  if [ -n "$wp" ]; then
    owner="$(python3 "$CLIENT" list 2>/dev/null \
      | python3 -c "import json,sys,os
wp=os.environ.get('AOS_WP_HINT','')
try: data=json.load(sys.stdin)
except Exception: data={}
for s in (data.get('sessions') or []):
    if s.get('wp_id')==wp and s.get('team_id'):
        print(s['team_id']); break
" AOS_WP_HINT="$wp" 2>/dev/null || true)"
    if [ -n "$owner" ]; then echo "$owner"; return; fi
  fi
  # ORCH-08 (v5 ENV): the bare team_100 fallback silently swallows a spoke transition into the hub inbox.
  # Make it LOUD (stderr, non-blocking) and set a flag the caller can fold into the captured subject, so a
  # missing $AOS_ORCHESTRATOR_TEAM / unregistered next owner is surfaced rather than mis-attributed.
  echo "⚠ orchestrator unresolved for WP='${wp:-?}'; defaulting recipient → team_100. Set \$AOS_ORCHESTRATOR_TEAM or register the next owner to avoid it." >&2
  export AOS_ORCH_FALLBACK=1
  echo "team_100"
}

# Shared auto-capture helper (Finding 1). The three closings call this ONE line.
# Degrade-safe (F1/AC5): on non-2xx / unreachable / PK conflict → append to messages.log and CONTINUE.
# NEVER blocks the completing session (returns 0 always).
# Usage: aos_capture <kind> <recipient> <recipient_kind> <subject> <body_ref> [gate] [wp_id]
aos_capture() {
  local kind="$1" recipient="$2" rkind="${3:-team}" subject="$4" body_ref="${5:-}" gate="${6:-}" wp="${7:-}"
  local sid sender log ts out rc
  sid="$(aos_session_id)"
  sender="$(aos_session_team)"
  log="$(aos_messages_log)"
  mkdir -p "$(dirname "$log")"
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%SZ')"
  rc=0
  # set -e safe: capture the REAL client exit via `|| rc=$?` (NOT `|| true`, which would mask it),
  # so the degrade block below runs instead of the script aborting (F-VAL-01 / AC5 / F1 degrade contract).
  out="$(python3 "$CLIENT" capture \
    --sender "$sender" \
    --recipient "$recipient" \
    --recipient-kind "$rkind" \
    --kind "$kind" \
    --subject "$subject" \
    ${body_ref:+--body-ref "$body_ref"} \
    --session-id "$sid" \
    ${wp:+--wp-id "$wp"} \
    ${gate:+--gate "$gate"} 2>/dev/null)" || rc=$?
  if [ "$rc" -ne 0 ]; then
    # DEGRADE: sole record is messages.log; completing session NOT blocked.
    printf '%s event=capture from=%s to=%s(%s) kind=%s%s%s ref=%s degrade=1\n' \
      "$ts" "$sender" "$recipient" "$rkind" "$kind" \
      "${gate:+ gate=$gate}" "${wp:+ wp=$wp}" "${body_ref:-—}" >>"$log"
    echo "⚠ capture degraded → ${log} (session not blocked)" >&2
    return 0
  fi
  echo "$out"
  return 0
}

# Inbox auto-read for self (team + session + environment). Used at register-startup (Finding 5).
aos_inbox_check() {
  local team env sid count
  team="$(aos_session_team)"
  env="${AOS_SESSION_ENV:-local-mac}"
  sid="$(aos_session_id)"
  for pair in "team:$team" "session:$sid" "environment:$env"; do
    local rk="${pair%%:*}" rv="${pair#*:}"
    [ -z "$rv" ] && continue
    count="$(python3 "$CLIENT" inbox --recipient-kind "$rk" --recipient "$rv" --status pending --limit 20 2>/dev/null \
      | python3 -c "import json,sys
try: print(json.load(sys.stdin).get('count',0))
except Exception: print(0)" 2>/dev/null || echo 0)"
    if [ "${count:-0}" -gt 0 ] 2>/dev/null; then
      echo "📬 inbox: ${count} pending for ${rk}=${rv} — run /AOS_mail check"
    fi
  done
}

aos_session_register() {
  local sid branch wt wp
  # Git-hygiene (AOS-V4.5-WP-GIT-HYGIENE): surface a bared working checkout at
  # session start. Best-effort, NEVER blocks register (the guard exits 0 even
  # when it warns; it only prints a loud remediation line to stderr).
  if [ -x "${SCRIPT_DIR}/aos_bare_guard.sh" ]; then
    bash "${SCRIPT_DIR}/aos_bare_guard.sh" "$REPO_ROOT" || true
  fi
  # CTX-06 (v5 ENV): allow-list identity guard — warns (non-blocking) when the resolved acting team is
  # not a team that operates in this repo (catches team_100-in-spoke / team_90-fallback at session START,
  # before a mis-attributed handoff reaches the hub). Correctly stays SILENT for a legit hub team_100
  # (it IS in the hub allow-list) — supersedes the earlier marker-only COMM-07 warn which false-fired there.
  if [ -x "${SCRIPT_DIR}/aos_identity_guard.sh" ]; then
    bash "${SCRIPT_DIR}/aos_identity_guard.sh" "$REPO_ROOT" || true
  fi
  sid="$(aos_session_id)"
  aos_persist_session_id "$sid"
  branch="$(git branch --show-current 2>/dev/null || true)"
  wt="$REPO_ROOT"
  wp="${1:-}"
  python3 "$CLIENT" register \
    --session-id "$sid" \
    --branch "$branch" \
    --worktree-path "$wt" \
    ${wp:+--wp-id "$wp"}
  # Finding 5: register-startup ALSO runs an inbox check so auto-read fires without operator memory.
  aos_inbox_check || true
  # Model B (ADR054): hydrate the git-ignored Tier-A governance cache at session start so an
  # operator never works against a missing/stale cache. Best-effort, NEVER blocks register.
  if [ -x "${SCRIPT_DIR}/aos_governance_bootstrap.sh" ]; then
    bash "${SCRIPT_DIR}/aos_governance_bootstrap.sh" --repo "$REPO_ROOT" >/dev/null 2>&1 \
      || echo "[aos] governance cache bootstrap skipped (run scripts/aos_governance_bootstrap.sh manually)" >&2
  fi
  echo "ℹ clobber guard: alias git='bash ${SCRIPT_DIR}/aos_git.sh' (recommended for ADR052 W2 enforcement)" >&2
}

aos_session_owner() {
  local path="${1:-$REPO_ROOT}"
  python3 "$CLIENT" owners --worktree-path "$path" --exclude-session-id "$(aos_session_id)" 2>/dev/null \
    | python3 -m json.tool 2>/dev/null \
    || python3 "$CLIENT" owners --worktree-path "$path" --exclude-session-id "$(aos_session_id)" 2>/dev/null \
    || echo '{"owners":[]}'
}

aos_session_heartbeat() {
  python3 "$CLIENT" heartbeat --session-id "$(aos_session_id)"
  # CTX-08 (v5 ENV): ride a cheap COUNT-ONLY inbox check on the heartbeat beat so a long-running session
  # surfaces a '📬 N pending' hint mid-session without operator memory. NOT a flip — read stays a
  # /AOS_mail check action (loop-guard preserved). Interim ride-along; full push = the M7 dispatcher.
  aos_inbox_check || true
}

aos_session_close() {
  # Finding 1 / LOD300 §4.2: capture completion to the orchestrator inbox BEFORE the API close call.
  local wp orch ref me
  wp="${1:-${AOS_WP_ID:-}}"
  orch="$(aos_resolve_orchestrator "$wp")"
  me="$(aos_session_team)"
  ref="${AOS_COMPLETION_REF:-}"
  # COMM-04 (v5 ENV): a completion to one's OWN team is a self-route (400 INVALID_ROUTE) and pure
  # self-noise — the WP row already carries closure state. Skip the self-notice (clean, no degrade
  # spam); only mail the orchestrator when it is a DIFFERENT team than the closing session.
  if [ "$orch" = "$me" ]; then
    echo "ℹ completion self-notice skipped (orchestrator == ${me}); WP state tracked in DB row" >&2
  else
    local subj="Session completion${wp:+ — $wp}"
    # ORCH-08: stamp the audit record itself when the recipient was the team_100 fall-through.
    [ "${AOS_ORCH_FALLBACK:-0}" = "1" ] && subj="$subj (FALLBACK — next owner unregistered, recipient=team_100)"
    aos_capture completion "$orch" team "$subj" "$ref" "" "$wp" >/dev/null 2>&1 || true
  fi
  python3 "$CLIENT" close --session-id "$(aos_session_id)" 2>/dev/null || true
}

aos_session_list_json() {
  python3 "$CLIENT" list --live
}

aos_session_render_list() {
  local now sid
  now="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%SZ')"
  sid="$(aos_session_id)"
  export AOS_SESSION_ID="$sid"
  echo "AOS active sessions — register (TTL ${AOS_SESSION_TTL_SEC:-7200}s)            now: ${now}"
  echo "┌──────────────┬──────────┬───────────────┬─────────────────────┬──────────┬───────────┐"
  echo "│ session      │ team     │ environment   │ worktree / branch   │ status   │ last_hb   │"
  echo "├──────────────┼──────────┼───────────────┼─────────────────────┼──────────┼───────────┤"
  python3 -c "
import json, sys, os
from datetime import datetime, timezone
data = json.load(sys.stdin)
sessions = data.get('sessions') or []
self_id = os.environ.get('AOS_SESSION_ID') or ''
for s in sessions:
    sid = s.get('session_id', '?')[:12]
    mark = ' *' if s.get('session_id') == self_id else '  '
    team = (s.get('team_id') or '?')[:8]
    env = (s.get('environment') or '?')[:13]
    wt = s.get('worktree_path') or '—'
    br = s.get('branch') or ''
    path = wt if wt == '—' else f\"{wt} / {br}\"[:19]
    st = (s.get('status') or '?')[:8]
    hb = s.get('last_heartbeat') or ''
    ago = '—'
    if hb:
        try:
            dt = datetime.fromisoformat(hb.replace('Z', '+00:00'))
            sec = int((datetime.now(timezone.utc) - dt).total_seconds())
            if sec < 60: ago = f'{sec}s ago'
            elif sec < 3600: ago = f'{sec//60}m ago'
            else: ago = f'{sec//3600}h ago'
        except Exception:
            ago = hb[:8]
    print(f'│ {sid}{mark} │ {team:<8} │ {env:<13} │ {path:<19} │ {st:<8} │ {ago:<9} │')
" <<< "$(aos_session_list_json 2>/dev/null || echo '{"sessions":[]}')"
  echo "└──────────────┴──────────┴───────────────┴─────────────────────┴──────────┴───────────┘"
  echo "  * = this session"
}

# ── W5 (additive) ────────────────────────────────────────────────────────────
# W-S2 advance keyed by wp_id. Resolves the run via the EXISTING
# GET /api/work-packages/{wp_id} (linked_run_id), then calls the EXISTING
# POST /api/runs/{run_id}/advance UNCHANGED — cross-engine guard stays server-side.
# Friction: 3 ops by hand (lookup run_id → recall verdict → advance) → 1 verb.
# Usage: aos_session_ctl.sh advance <wp_id> <verdict> [summary]
aos_gate_advance() {
  local wp="${1:?Usage: aos_session_ctl.sh advance <wp_id> <verdict> [summary]}"
  local verdict="${2:?verdict required (e.g. PASS)}" summary="${3:-}"
  local resolved run_id
  resolved="$(python3 "$CLIENT" wp-run --wp-id "$wp")" || {
    echo "✗ could not resolve run for ${wp} (is the WP ACTIVE with a linked run?)" >&2
    return 1
  }
  run_id="$(printf '%s' "$resolved" | python3 -c "import json,sys; print(json.load(sys.stdin).get('run_id',''))" 2>/dev/null)"
  if [ -z "$run_id" ]; then echo "✗ no run_id for ${wp}" >&2; return 1; fi
  python3 "$CLIENT" advance --run-id "$run_id" --verdict "$verdict" ${summary:+--summary "$summary"}
}

# W-S3 session-start single verb: register → heartbeat → detect-concurrency → inbox-check.
# Every sub-call already exists (W3/W4) and stays independently callable (AC7).
# Friction: 4 ops spread across /AOS_session phases → 1 verb.
# Usage: aos_session_ctl.sh start [wp_id]
aos_session_start() {
  local wp="${1:-}" sid
  aos_session_register "$wp"          # also persists sid + runs aos_inbox_check (W3)
  aos_session_heartbeat || true
  sid="$(aos_session_id)"
  python3 "$CLIENT" detect --repo-root "$REPO_ROOT" --session-id "$sid" ${wp:+--wp-hint "$wp"} 2>/dev/null || true
  aos_inbox_check || true
}

case "${1:-}" in
  register) aos_session_register "${2:-}" ;;
  # W5 additive verbs (W-S2 / W-S3):
  advance) shift; aos_gate_advance "$@" ;;
  start) aos_session_start "${2:-}" ;;
  heartbeat) aos_session_heartbeat ;;
  close) aos_session_close "${2:-}" ;;
  list) aos_session_render_list ;;
  list-json) aos_session_list_json ;;
  session-id) aos_session_id ;;
  # W4: shared auto-capture (Finding 1) + inbox helpers.
  # capture <kind> <recipient> <recipient_kind> <subject> <body_ref> [gate] [wp_id]
  capture) shift; aos_capture "$@" ;;
  inbox-check) aos_inbox_check ;;
  resolve-orchestrator) aos_resolve_orchestrator "${2:-}" ;;
  # CTX-06 (v5 ENV): surface the resolved session team + run the allow-list identity guard (/AOS_session --status).
  identity) echo "session_team=$(aos_session_team)  repo=$(basename "$REPO_ROOT")"; bash "${SCRIPT_DIR}/aos_identity_guard.sh" "$REPO_ROOT" || true ;;
  owner|owners) aos_session_owner "${2:-}" ;;
  *) echo "Usage: aos_session_ctl.sh {start|register|heartbeat|close|list|list-json|session-id|advance|capture|inbox-check|resolve-orchestrator|identity|owner} [args]" >&2; exit 2 ;;
esac
