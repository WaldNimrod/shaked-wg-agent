#!/usr/bin/env bash
# session_preflight.sh — AOS session startup pre-flight (C→A state machine)
# WP: AOS-V4.5-WP-SESSION-W2-WORKTREE-ISOLATION
#
# Prerequisites: git, python3, bash; env AOS_SESSION_ENV (default local-mac);
#   optional AOS_SESSION_FORCE=1 or --force
# Ports: none
#
# Invoked at session start (manual or future hook). Does NOT auto-install during W2 build.
#
# USAGE:
#   bash scripts/hooks/session_preflight.sh [--wp WP_ID] [--force] [--non-interactive]

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE_LOG="${REPO_ROOT}/_COMMUNICATION/_log/session_force.log"

WP_ID=""
FORCE=0
NON_INTERACTIVE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --wp) WP_ID="${2:-}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --non-interactive) NON_INTERACTIVE=1; shift ;;
    -h|--help)
      echo "Usage: session_preflight.sh [--wp WP_ID] [--force] [--non-interactive]"
      exit 0
      ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ "${AOS_SESSION_FORCE:-0}" = "1" ]; then
  FORCE=1
fi

# shellcheck source=/dev/null
source "${REPO_ROOT}/scripts/start_worktree.sh"

# W3: register + heartbeat (on-activity, F2)
if [ -x "${REPO_ROOT}/scripts/aos_session_ctl.sh" ]; then
  bash "${REPO_ROOT}/scripts/aos_session_ctl.sh" register "${WP_ID:-}" 2>/dev/null || true
  bash "${REPO_ROOT}/scripts/aos_session_ctl.sh" heartbeat 2>/dev/null || true
fi

aos_log_force() {
  local reason="$1"
  mkdir -p "$(dirname "$FORCE_LOG")"
  local ts branch
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%SZ')"
  branch="$(git branch --show-current 2>/dev/null || echo 'unknown')"
  printf '%s wp=%s branch=%s env=%s pid=%s reason=%s\n' \
    "$ts" "${WP_ID:-none}" "$branch" "${AOS_SESSION_ENV:-local-mac}" "$$" "$reason" >> "$FORCE_LOG"
}

# --force / AOS_SESSION_FORCE escape is logged BEFORE any further work (AC3/AC9).
if [ "$FORCE" -eq 1 ]; then
  aos_log_force "preflight invoked with --force or AOS_SESSION_FORCE=1"
fi

json="$(detect_concurrency register "${WP_ID:-}")"
state="$(echo "$json" | python3 -c "import json,sys; print(json.load(sys.stdin)['state'])")"
recommended="$(echo "$json" | python3 -c "import json,sys; print(json.load(sys.stdin)['recommended_worktree'])")"
has_uncertain="$(echo "$json" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('yes' if any('uncertain' in e for e in d.get('evidence',[])) else 'no')
")"

echo "AOS session pre-flight — env=${AOS_SESSION_ENV:-local-mac} state=${state}"
echo "$json" | python3 -m json.tool 2>/dev/null || echo "$json"

case "$state" in
  EXEMPT)
    echo "EXEMPT: no pre-flight action (special-team environment)."
    exit 0
    ;;
  CLEAR)
    if [ "$has_uncertain" = "yes" ] && [ "$FORCE" -eq 0 ]; then
      echo ""
      echo "OFFER (non-blocking): detection uncertain — consider isolated worktree:"
      echo "  ${recommended}"
      echo "  bash scripts/start_worktree.sh --json"
      echo "  /AOS_session --worktree ${WP_ID:-<wp>}"
      echo "Or proceed with --force / AOS_SESSION_FORCE=1 (logged)."
    fi
    aos_write_lock "sess-$$" "$REPO_ROOT" 2>/dev/null || true
    echo "CLEAR: session lock written; proceed."
    exit 0
    ;;
  CONCURRENT)
    if [ "$FORCE" -eq 1 ]; then
      aos_log_force "force proceed on shared tree; state=CONCURRENT"
      aos_write_lock "sess-$$-force" "$REPO_ROOT" 2>/dev/null || true
      echo "FORCE: proceeding on shared tree (logged to session_force.log)."
      exit 0
    fi
    if [ "$NON_INTERACTIVE" -eq 1 ]; then
      if aos_worktree_add "${WP_ID:-}" "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"; then
        aos_write_lock "sess-$$" "$(recommended_worktree_for_wp "${WP_ID:-}")" 2>/dev/null || true
        echo "AUTO-WORKTREE: created/verified ${recommended}; open a new session there."
        exit 0
      fi
      echo "HARD-REFUSE: auto-worktree failed in non-interactive mode." >&2
      echo "Remediation: fix dirty state, run: git worktree add ${recommended} <branch>" >&2
      echo "Or: AOS_SESSION_FORCE=1 / --force (logged)." >&2
      exit 1
    fi
    echo ""
    echo "CONCURRENT: another live session may share this tree."
    echo "  Recommended: ${recommended}"
    read -r -p "Create/use worktree now? [y/N/force] " ans || ans="n"
    case "$ans" in
      y|Y|yes|Yes)
        if aos_worktree_add "${WP_ID:-}" "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"; then
          echo "Worktree ready at ${recommended}. Start the new session from that path."
          exit 0
        fi
        echo "HARD-REFUSE: worktree add failed (unsafe to share tree)." >&2
        exit 1
        ;;
      force|FORCE|f)
        aos_log_force "interactive force after CONCURRENT"
        aos_write_lock "sess-$$-force" "$REPO_ROOT" 2>/dev/null || true
        exit 0
        ;;
      *)
        echo "HARD-REFUSE: shared tree is CONCURRENT — isolate before proceeding." >&2
        echo "  bash scripts/worktree_isolate.sh <branch> [wp_id]" >&2
        echo "  Or: --force / AOS_SESSION_FORCE=1 (logged override)." >&2
        exit 1
        ;;
    esac
    ;;
  *)
    echo "WARN: unknown detect state; offering worktree (anti-wedge)."
    exit 0
    ;;
esac
