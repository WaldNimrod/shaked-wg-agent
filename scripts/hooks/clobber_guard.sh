#!/usr/bin/env bash
# clobber_guard.sh — block destructive git ops that discard another live session's work (ADR052 W2 enforcement)
# WP: AOS-V5-WP-CONCURRENCY-DECONFLICTION (C1)
#
# Prerequisites: git, python3, bash; optional AOS_API_BASE for W3 register backend
# Ports: hub API (default 8092)
#
# USAGE (via aos_git.sh or direct):
#   bash scripts/hooks/clobber_guard.sh --op reset -- "$@"
#   bash scripts/hooks/clobber_guard.sh --op checkout -- <args>

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT="${REPO_ROOT}/scripts/session_register_client.py"
FORCE_LOG="${REPO_ROOT}/_COMMUNICATION/_log/clobber_guard_force.log"
OP="${1:-}"
shift || true

if [ "$OP" = "--op" ]; then
  OP="${1:-}"
  shift || true
fi

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

aos_log_force() {
  local reason="$1"
  mkdir -p "$(dirname "$FORCE_LOG")"
  local ts
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%SZ')"
  printf '%s op=%s repo=%s session=%s reason=%s\n' \
    "$ts" "$OP" "$REPO_ROOT" "$(aos_session_id)" "$reason" >>"$FORCE_LOG"
}

if [ "${AOS_CLOBBER_GUARD_FORCE:-0}" = "1" ]; then
  aos_log_force "clobber_guard bypassed via AOS_CLOBBER_GUARD_FORCE=1"
  exit 0
fi

# Solo / clean tree fast-path: no local changes → nothing to clobber.
if ! git -C "$REPO_ROOT" status --porcelain 2>/dev/null | grep -q .; then
  exit 0
fi

# Destructive-op filter: only guard ops that can discard work.
case "$OP" in
  reset|clean|worktree-remove) ;;
  checkout)
    # checkout away from dirty tree is destructive
    ;;
  *)
    exit 0
    ;;
esac

SID="$(aos_session_id)"
PEERS_JSON='{"owners":[]}'

if [ -f "$CLIENT" ]; then
  PEERS_JSON="$(python3 "$CLIENT" owners --worktree-path "$REPO_ROOT" --exclude-session-id "$SID" 2>/dev/null \
    || echo '{"owners":[]}')"
fi

# Lockfile interim fallback when API degrades.
if [ "$PEERS_JSON" = "[]" ] || [ "$PEERS_JSON" = '{"owners":[]}' ]; then
  if [ -f "${REPO_ROOT}/scripts/start_worktree.sh" ]; then
    # shellcheck source=/dev/null
    source "${REPO_ROOT}/scripts/start_worktree.sh" 2>/dev/null || true
    if declare -f detect_concurrency >/dev/null 2>&1; then
      det="$(detect_concurrency interim "" 2>/dev/null || echo '{}')"
      state="$(echo "$det" | python3 -c "import json,sys; print(json.load(sys.stdin).get('state','CLEAR'))" 2>/dev/null || echo CLEAR)"
      if [ "$state" = "CONCURRENT" ]; then
        echo "CLOBBER GUARD: interim detect reports CONCURRENT on shared tree." >&2
        echo "  Remediation: bash scripts/worktree_isolate.sh <branch> [wp_id]" >&2
        echo "  Or: AOS_CLOBBER_GUARD_FORCE=1 (logged) to override." >&2
        exit 1
      fi
    fi
  fi
  exit 0
fi

peer_count="$(printf '%s' "$PEERS_JSON" | python3 -c "
import json,sys
try:
    data=json.load(sys.stdin)
except Exception:
    data={}
owners=data.get('owners') if isinstance(data,dict) else data
print(len(owners or []))
" 2>/dev/null || echo 0)"

if [ "${peer_count:-0}" -gt 0 ]; then
  printf '%s' "$PEERS_JSON" | python3 -c "
import json,sys
data=json.load(sys.stdin)
owners=data.get('owners') or []
print('CLOBBER GUARD: refusing destructive git op — another live session owns this checkout:', file=sys.stderr)
for o in owners:
    print(f\"  owner session={o.get('session_id')} team={o.get('team_id')} wp={o.get('wp_id') or '—'}\", file=sys.stderr)
print('Remediation:', file=sys.stderr)
print('  bash scripts/worktree_isolate.sh <branch> [wp_id]', file=sys.stderr)
print('  bash scripts/aos_session_ctl.sh owner', file=sys.stderr)
print('  AOS_CLOBBER_GUARD_FORCE=1 to override (logged)', file=sys.stderr)
" || true
  exit 1
fi

exit 0
