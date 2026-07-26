#!/usr/bin/env bash
# hub_write_guard.sh — refuse hub-tree git writes when a live human session owns main (C2)
# WP: AOS-V5-WP-CONCURRENCY-DECONFLICTION
#
# Called by aos_sync_all before git commit on $AOS_ROOT. Returns 0 = proceed, 1 = skip/refuse.

set -euo pipefail

HUB_ROOT="${1:?hub root required}"
CLIENT="${HUB_ROOT}/scripts/session_register_client.py"
ACTOR_TEAM="${AOS_ACTOR_TEAM_ID:-${AOS_SESSION_TEAM_ID:-}}"

# Automation actor may write when registered on the automation worktree only.
if [ "${AOS_SYNC_AUTOMATION:-0}" = "1" ]; then
  exit 0
fi

if [ ! -f "$CLIENT" ]; then
  exit 0
fi

owners_json="$(python3 "$CLIENT" owners --worktree-path "$HUB_ROOT" --exclude-session-id "aos-sync-$$" 2>/dev/null \
  || echo '{"owners":[]}')"
count="$(printf '%s' "$owners_json" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(len(d.get('owners') or []))
" 2>/dev/null || echo 0)"

if [ "${count:-0}" -gt 0 ]; then
  echo "HUB WRITE GUARD: skipping hub git commit — ${count} live session(s) on ${HUB_ROOT}" >&2
  printf '%s' "$owners_json" | python3 -c "
import json,sys
for o in json.load(sys.stdin).get('owners') or []:
    print(f\"  session={o.get('session_id')} team={o.get('team_id')} wp={o.get('wp_id') or '—'}\", file=sys.stderr)
" 2>/dev/null || true
  echo "  Remediation: worktree-isolate human sessions; re-run sync; or AOS_SYNC_AUTOMATION=1 from automation worktree." >&2
  exit 1
fi

exit 0
