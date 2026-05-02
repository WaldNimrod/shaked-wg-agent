#!/usr/bin/env bash
# msg_preflight.sh — API-first preflight + branch-safe MSG delivery helper
# ADR043 v1.1.0 §4 (Branch Independence) + §5 (API-First Pre-flight) + §6 (Multi-Domain Routing)
#
# Canonical SSoT: lean-kit/modules/team-messaging/scripts/msg_preflight.sh
# Snapshot:       _aos/lean-kit/modules/team-messaging/scripts/msg_preflight.sh
#
# USAGE
#   source msg_preflight.sh --verbose
#       Probes {AOS_API_BASE}/api/system/health (2s timeout).
#       Exports:  API_ONLINE=0|1, API_BASE, API_ERROR (if offline)
#                 AOS_PROJECT_ID (auto-detected from CWD git remote unless preset).
#       Exit code: 0 always (source-friendly); callers read API_ONLINE.
#
#   msg_deliver_file <msg_path>
#       After writing a MSG file to _COMMUNICATION/, call this to ensure
#       it lands on origin/main regardless of current branch (ADR043 §4).
#       Exit code: 0 on success, non-zero on push failure.
#
#   msg_detect_project_id
#       Echo the spoke id resolved from CWD git remote (or AOS_PROJECT_ID env).
#       Used by msg_curl to inject X-Project-Id automatically (§6).
#
#   msg_curl <method> <api_path> [json_body]
#       curl wrapper that always injects X-Actor-Team-Id and X-Project-Id.
#       Requires AOS_ACTOR_TEAM_ID env var. Echoes response body.
#
# DEPENDENCIES: curl, git

set -u

AOS_API_BASE="${AOS_API_BASE:-http://127.0.0.1:8090}"
API_BASE="$AOS_API_BASE"
_MSG_PREFLIGHT_VERBOSE=0
for arg in "$@"; do
  [ "$arg" = "--verbose" ] && _MSG_PREFLIGHT_VERBOSE=1
done

# --- API probe -------------------------------------------------------------
_probe_api() {
  local http_code
  http_code=$(curl -s -o /dev/null -w '%{http_code}' \
              --max-time 2 --connect-timeout 2 \
              "${AOS_API_BASE}/api/system/health" 2>/dev/null || echo "000")
  if [ "$http_code" = "200" ]; then
    export API_ONLINE=1
    unset API_ERROR
    [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ] && echo "✓ API online: $AOS_API_BASE"
    return 0
  fi
  export API_ONLINE=0
  export API_ERROR="probe failed (HTTP $http_code) at ${AOS_API_BASE}/api/system/health"
  if [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ]; then
    echo "⚠ API offline — $API_ERROR"
    echo "  Hint: start hub API with: bash scripts/start_aos_api_local.sh"
    echo "  Fallback: file-based MSG + branch-safe push to origin/main (ADR043 §4)"
  fi
  return 0
}

# --- Branch-safe file delivery (ADR043 §4) ---------------------------------
msg_deliver_file() {
  local msg_path="${1:-}"
  if [ -z "$msg_path" ] || [ ! -f "$msg_path" ]; then
    echo "ERROR: msg_deliver_file requires an existing MSG file path" >&2
    return 2
  fi

  local current_branch
  current_branch=$(git branch --show-current 2>/dev/null || echo "")
  if [ -z "$current_branch" ]; then
    echo "ERROR: not inside a git worktree or detached HEAD — cannot deliver" >&2
    return 3
  fi

  # Same-branch-as-main happy path
  if [ "$current_branch" = "main" ]; then
    git add "$msg_path" >/dev/null 2>&1 || return 4
    git commit -m "msg: deliver $(basename "$msg_path")" >/dev/null 2>&1 || return 5
    git push origin main >/dev/null 2>&1 || return 6
    echo "✓ MSG delivered via origin/main (branch=main): $msg_path"
    return 0
  fi

  # Isolated-branch case: commit here, push only the commit to main, then
  # keep local branch clean by moving the branch tip forward but leaving the
  # MSG file present on the working branch for audit continuity.
  local commit_msg="msg(fallback): deliver $(basename "$msg_path") from ${current_branch}"
  git add "$msg_path" >/dev/null 2>&1 || return 4
  git commit -m "$commit_msg" >/dev/null 2>&1 || return 5

  # Push the commit to origin/main as a fast-forward OR a force-with-lease
  # refusal-safe update. Protocol §4: failure to push = failure to deliver.
  if ! git push origin "HEAD:main" 2>/dev/null; then
    echo "ERROR: push to origin/main rejected. Pull + retry required." >&2
    echo "  Remedy: git fetch origin; rebase local commit onto origin/main;" >&2
    echo "           then re-run msg_deliver_file." >&2
    return 6
  fi
  echo "✓ MSG delivered via origin/main (fallback from branch=${current_branch}): $msg_path"
  return 0
}

# --- Multi-domain routing helpers (ADR043 v1.1.0 §6) -----------------------
# Auto-detect current spoke from git remote URL (or honor AOS_PROJECT_ID env).
msg_detect_project_id() {
  if [ -n "${AOS_PROJECT_ID:-}" ]; then echo "$AOS_PROJECT_ID"; return 0; fi
  local remote_url
  remote_url=$(git config --get remote.origin.url 2>/dev/null || echo "")
  case "$remote_url" in
    *agents-os*)        echo "agents-os" ;;
    *TikTrack*|*tiktrack*) echo "tiktrack" ;;
    *EyalAmit*|*eyalamit*) echo "eyalamit" ;;
    *HobbitHome*|*hobbithome*) echo "hobbithome" ;;
    *Microgreens*|*microgreens*) echo "microgreens" ;;
    *AOS-Sandbox-Lean*) echo "aos-sandbox-lean" ;;
    *AOS-Sandbox-Full*) echo "aos-sandbox-full" ;;
    *agros-insite*)     echo "agros-insite" ;;
    *)                  echo "agents-os" ;;   # safe default
  esac
}

# curl wrapper that auto-injects X-Actor-Team-Id + X-Project-Id headers.
# Usage:  msg_curl <method> <api_path> [json_body]
# Example: msg_curl GET "/api/messaging/inbox?to_team=team_99"
#          msg_curl POST "/api/messaging/send" "$payload"
# Auth:    Set AOS_ACTOR_API_KEY env var (shared secret configured in AOS_V3_ACTOR_KEYS
#          on the server) to authenticate. Required when server has AOS_V3_ACTOR_KEYS
#          set (production). Not required in local dev (AOS_V3_TRUST_CLIENT_ACTOR=1).
msg_curl() {
  local method="${1:?usage: msg_curl <method> <api_path> [json_body]}"
  local api_path="${2:?usage: msg_curl <method> <api_path> [json_body]}"
  local data="${3:-}"
  local team="${AOS_ACTOR_TEAM_ID:-}"
  if [ -z "$team" ]; then
    echo "ERROR: AOS_ACTOR_TEAM_ID env var must be set before calling msg_curl" >&2
    return 2
  fi
  local proj
  proj=$(msg_detect_project_id)
  local args=(-s -X "$method" -H "X-Actor-Team-Id: $team" -H "X-Project-Id: $proj")
  # Inject API key when configured (AOS_V3_ACTOR_KEYS production auth model — SEC-001)
  local api_key="${AOS_ACTOR_API_KEY:-}"
  if [ -n "$api_key" ]; then
    args+=(-H "X-Actor-Api-Key: $api_key")
  fi
  if [ -n "$data" ]; then
    args+=(-H "Content-Type: application/json" -d "$data")
  fi
  curl "${args[@]}" "${AOS_API_BASE}${api_path}"
}

# ── Bypass audit log helper (AOS-V4-WP-MSG-HARDENING §bypass) ─────────────
# msg_log_bypass <bypassed_file> [branch]
#   Appends a JSONL entry with op=hook_bypassed to messages.log.
#   Called by the pre-commit hook bypass path (git commit --no-verify).
#   Falls back to local file append if W4 MSG-LOG endpoint is not available.
msg_log_bypass() {
  local bypassed_file="${1:-unknown}"
  local branch="${2:-$(git branch --show-current 2>/dev/null || echo 'unknown')}"
  local ts
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%SZ')"
  local repo_root
  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  local log_dir="${repo_root}/_COMMUNICATION/_log"
  local log_file="${log_dir}/messages.log"
  local entry
  entry="{\"ts\":\"${ts}\",\"op\":\"hook_bypassed\",\"file\":\"${bypassed_file}\",\"branch\":\"${branch}\"}"

  mkdir -p "$log_dir"
  # Atomic POSIX append (single write, same safety as _append_log_entry in team_messaging.py)
  printf '%s\n' "$entry" >> "$log_file" 2>/dev/null || true
}

# Export helpers so subshells can use them too (best-effort; bash-only).
export -f msg_detect_project_id 2>/dev/null || true
export -f msg_curl 2>/dev/null || true
export -f msg_log_bypass 2>/dev/null || true

# Branch state check (AOS-V4-WP-SPAWN-4-BRANCH-GUARD AC-10) — non-blocking warning
bash scripts/check_branch_state.sh || true

# Auto-probe when sourced (so callers just `source ... && echo $API_ONLINE`)
_probe_api

# Auto-detect domain on source so callers can `echo $AOS_PROJECT_ID` immediately.
export AOS_PROJECT_ID="${AOS_PROJECT_ID:-$(msg_detect_project_id)}"
# Use if/fi so `source` exits 0 when verbose=0 (a bare `[ ... ] && echo` is non-zero and breaks callers).
if [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ]; then
  echo "✓ Project context: $AOS_PROJECT_ID"
fi
