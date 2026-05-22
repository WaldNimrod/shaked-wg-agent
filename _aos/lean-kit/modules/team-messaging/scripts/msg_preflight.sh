#!/usr/bin/env bash
# msg_preflight.sh — API-first preflight + branch-safe MSG delivery helper
# ADR043 v1.5.0 §3 (Inbox design) + §4 (Branch Independence) + §5 (API-First Pre-flight)
# + §6 (Multi-Domain Routing) + §6.1 (Cross-Domain File-Fallback) + §11 (Env Reference)
# + §16 (Endpoint Auth Matrix) + Rule 5 (auth-class fallback)
#
# Canonical SSoT: lean-kit/modules/team-messaging/scripts/msg_preflight.sh
# Snapshot:       _aos/lean-kit/modules/team-messaging/scripts/msg_preflight.sh
#
# USAGE
#   source msg_preflight.sh --verbose
#       Probes {AOS_API_BASE}/api/system/health (2s timeout).
#       Exports:  API_ONLINE=0|1, API_BASE, API_ERROR (if offline)
#                 AOS_PROJECT_ID (auto-detected from CWD git remote unless preset).
#                 MSG_CURL_AUTH_FALLBACK=0, MSG_CURL_AUTH_CODE=""
#       Exit code: 0 always (source-friendly); callers read API_ONLINE.
#
#   msg_deliver_file <msg_path>
#       After writing a MSG file to _COMMUNICATION/, call this to ensure
#       it lands on origin/main regardless of current branch (ADR043 §4).
#       Exit code: 0 on success, non-zero on push failure.
#
#   msg_deliver_file_cross_domain <local_msg> <target_domain_root>
#       Copy MSG to a different domain repo and push both origin/main heads.
#       ADR043 v1.5.0 §6.1 / R-MSG-07.
#       Exit codes: 0=success, 2=arg/file error, 4=target not git repo,
#       5=target dirty, 6=copy failed, 7=spoke push failed, 8=target push failed.
#
#   msg_detect_project_id
#       Echo the spoke id resolved from CWD git remote (or AOS_PROJECT_ID env).
#       3-tier: env override → TSV cache → /api/projects → static fallback.
#       Used by msg_curl to inject X-Project-Id automatically (§6).
#
#   msg_curl <method> <api_path> [json_body]
#       curl wrapper that always injects X-Actor-Team-Id and X-Project-Id.
#       Requires AOS_ACTOR_TEAM_ID env var. Echoes response body.
#       Exit codes: 0=success, 1=programmer error (schema/unknown-project/4xx),
#                   3=auth-class error (401/403/ACTOR_KEY_NOT_CONFIGURED → file-fallback),
#                   4=transient/network error (5xx/000 → file-fallback)
#
#   msg_next_id [from_team] [to_team] [date_stamp]
#       Returns next available MSG-HUB-YYYYMMDD-NNN for to_team's inbox in current repo.
#       Note: snapshot-based (not atomic). Touch the returned file before second call
#       if you need strict sequential ids. ADR043 v1.5.0 / R-MSG-09.
#
# DEPENDENCIES: curl, git

set -u

# AOS_API_BASE resolution — three tiers (ADR043 §11 / §15):
#   Tier 1: explicit AOS_API_BASE (caller or shell profile — highest priority)
#   Tier 2: AOS_V3_PUBLIC_API_BASE (from core/.env — canonical server URL for Python + shell)
#   Tier 3: localhost fallback (correct on waldhomeserver; hits stub on Mac → HTTP 410)
AOS_API_BASE="${AOS_API_BASE:-${AOS_V3_PUBLIC_API_BASE:-http://127.0.0.1:8090}}"
API_BASE="$AOS_API_BASE"
_MSG_PREFLIGHT_VERBOSE=0
for _arg in "$@"; do
  [ "$_arg" = "--verbose" ] && _MSG_PREFLIGHT_VERBOSE=1
done

# ADR043 v1.5.0 §5 Rule 5 export sentinel (cleared per source)
MSG_CURL_AUTH_FALLBACK=0
MSG_CURL_AUTH_CODE=""

# --- API probe -------------------------------------------------------------
_probe_api() {
  # R-MSG-05 Tier-0 self-healing (ADR043 v1.5.0):
  # If Tier-3 default in effect AND not on waldhomeserver AND Tailscale up AND canonical URL
  # responds → promote. Zero cost on waldhomeserver (marker exits early).
  if [ "${AOS_API_BASE}" = "http://127.0.0.1:8090" ] && \
     ! [ -e /etc/aos-server-host ]; then
    if command -v tailscale >/dev/null 2>&1 && \
       tailscale status >/dev/null 2>&1; then
      if curl -fsS --max-time 1 \
           "http://100.125.98.56:8090/api/system/health" >/dev/null 2>&1; then
        AOS_API_BASE="http://100.125.98.56:8090"
        API_BASE="$AOS_API_BASE"
        if [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ]; then
          printf 'ℹ promoted AOS_API_BASE → %s (Tailscale + canonical health probe)\n' \
                 "${AOS_API_BASE}" >&2
        fi
      fi
    fi
  fi

  local http_code
  http_code=$(curl -s -o /dev/null -w '%{http_code}' \
              --max-time 2 --connect-timeout 2 \
              "${AOS_API_BASE}/api/system/health" 2>/dev/null || printf '000')
  if [ "$http_code" = "200" ]; then
    export API_ONLINE=1
    unset API_ERROR
    if [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ]; then
      printf '✓ API online: %s\n' "$AOS_API_BASE"
    fi
    return 0
  fi
  if [ "$http_code" = "410" ]; then
    # Mac legacy stub (aos_legacy_stub.py, v4.0.0 GA) is running.
    # HTTP 410 is a redirect signal — NOT a connection failure. ADR043 §5 Rule 4.
    export API_ONLINE=0
    export API_ERROR="Mac legacy stub active (HTTP 410) at ${AOS_API_BASE} — canonical API: http://100.125.98.56:8090"
    if [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ]; then
      printf '⚠ Legacy stub detected at %s (HTTP 410)\n' "${AOS_API_BASE}"
      printf '  Canonical API → http://100.125.98.56:8090 (waldhomeserver, Tailscale)\n'
      printf '  Fix: export AOS_API_BASE=http://100.125.98.56:8090\n'
      printf '       or set AOS_V3_PUBLIC_API_BASE=http://100.125.98.56:8090 in core/.env\n'
      printf '  Fallback: file-based MSG + branch-safe push to origin/main (ADR043 §4)\n'
    fi
    return 0
  fi
  export API_ONLINE=0
  export API_ERROR="probe failed (HTTP $http_code) at ${AOS_API_BASE}/api/system/health"
  if [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ]; then
    printf '⚠ API offline — %s\n' "$API_ERROR"
    printf '  Hint: canonical API at http://100.125.98.56:8090 (waldhomeserver, Tailscale)\n'
    printf '        export AOS_API_BASE=http://100.125.98.56:8090\n'
    printf '        or set AOS_V3_PUBLIC_API_BASE=http://100.125.98.56:8090 in core/.env\n'
    printf '  Fallback: file-based MSG + branch-safe push to origin/main (ADR043 §4)\n'
  fi
  return 0
}

# --- Branch-safe file delivery (ADR043 §4) ---------------------------------
msg_deliver_file() {
  local msg_path="${1:-}"
  if [ -z "$msg_path" ] || [ ! -f "$msg_path" ]; then
    printf 'ERROR: msg_deliver_file requires an existing MSG file path\n' >&2
    return 2
  fi

  local current_branch
  current_branch=$(git branch --show-current 2>/dev/null || printf '')
  if [ -z "$current_branch" ]; then
    printf 'ERROR: not inside a git worktree or detached HEAD — cannot deliver\n' >&2
    return 3
  fi

  # Same-branch-as-main happy path
  if [ "$current_branch" = "main" ]; then
    git add "$msg_path" >/dev/null 2>&1 || return 4
    git commit -m "msg: deliver $(basename "$msg_path")" >/dev/null 2>&1 || return 5
    git push origin main >/dev/null 2>&1 || return 6
    printf '✓ MSG delivered via origin/main (branch=main): %s\n' "$msg_path"
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
    printf 'ERROR: push to origin/main rejected. Pull + retry required.\n' >&2
    printf '  Remedy: git fetch origin; rebase local commit onto origin/main;\n' >&2
    printf '           then re-run msg_deliver_file.\n' >&2
    return 6
  fi
  printf '✓ MSG delivered via origin/main (fallback from branch=%s): %s\n' \
         "$current_branch" "$msg_path"
  return 0
}

# --- Cross-domain file-fallback delivery (ADR043 v1.5.0 §6.1 / R-MSG-07) ----
# msg_deliver_file_cross_domain <local_msg> <target_domain_root>
# Exit codes: 0=success, 2=arg/file error, 4=target not git repo,
# 5=target dirty, 6=copy failed, 7=spoke push failed, 8=target push failed.
#
# BUILD_CHECKLIST F-MSG-001: source repo dirty-tree guard added (symmetric with
# target-repo guard). Source repo must also be clean before delivery.
msg_deliver_file_cross_domain() {
  local local_msg="${1:-}"
  local target_root="${2:-}"

  if [ -z "$local_msg" ] || [ -z "$target_root" ]; then
    printf 'ERROR: msg_deliver_file_cross_domain requires <local_msg> <target_domain_root>\n' >&2
    return 2
  fi
  if [ ! -f "$local_msg" ]; then
    printf 'ERROR: local_msg %s does not exist\n' "$local_msg" >&2
    return 2
  fi

  # Source repo dirty-tree guard (F-MSG-001 — symmetric with target guard).
  local _src_dirty
  _src_dirty=$(git status --porcelain 2>/dev/null) || _src_dirty="ERROR"
  if [ -n "$_src_dirty" ]; then
    printf 'ERROR: source repo has uncommitted changes.\n' >&2
    printf '       Commit or stash source changes before cross-domain delivery.\n' >&2
    printf '%s\n' "$_src_dirty" >&2
    return 5
  fi

  if ! git -C "$target_root" rev-parse --show-toplevel >/dev/null 2>&1; then
    printf 'ERROR: target root %s is not a git repo — cannot deliver cross-domain\n' \
           "$target_root" >&2
    return 4
  fi

  local _dirty
  _dirty=$(git -C "$target_root" status --porcelain 2>/dev/null) || _dirty="ERROR"
  if [ -n "$_dirty" ]; then
    printf 'ERROR: target repo at %s has uncommitted changes.\n' "$target_root" >&2
    printf '       Commit or stash target changes before cross-domain delivery.\n' >&2
    printf '%s\n' "$_dirty" >&2
    return 5
  fi

  local _rel_path
  _rel_path=$(printf '%s' "$local_msg" | sed 's|.*/_COMMUNICATION/|_COMMUNICATION/|')
  case "$_rel_path" in
    _COMMUNICATION/*) : ;;
    *)
      printf 'ERROR: local_msg %s does not contain /_COMMUNICATION/ segment\n' "$local_msg" >&2
      return 2
      ;;
  esac

  local target_msg="${target_root}/${_rel_path}"
  local target_dir
  target_dir=$(dirname "$target_msg")
  mkdir -p "$target_dir" 2>/dev/null || {
    printf 'ERROR: cannot create target directory %s\n' "$target_dir" >&2
    return 6
  }
  cp "$local_msg" "$target_msg" 2>/dev/null || {
    printf 'ERROR: copy to %s failed\n' "$target_msg" >&2
    return 6
  }
  printf '→ Cross-domain copy written: %s\n' "$target_msg"

  msg_deliver_file "$local_msg" || {
    printf 'ERROR: push of spoke audit copy to origin/main failed (exit %d)\n' "$?" >&2
    return 7
  }

  (
    cd "$target_root" || exit 4
    msg_deliver_file "$_rel_path"
  ) || {
    printf 'ERROR: push to target origin/main failed (exit %d)\n' "$?" >&2
    return 8
  }

  printf '✓ Cross-domain MSG delivered: both origin/main heads updated.\n'
  printf '  Spoke copy:  %s\n' "$local_msg"
  printf '  Target copy: %s\n' "$target_msg"
  return 0
}

# --- Multi-domain routing helpers (ADR043 v1.5.0 §6) -----------------------
# Auto-detect current spoke from git remote URL (or honor AOS_PROJECT_ID env).
# 3-tier: Tier 0 = env override, Tier 1 = TSV cache, Tier 2 = /api/projects, Tier 3 = static.
msg_detect_project_id() {
  # Tier 0: explicit env override.
  if [ -n "${AOS_PROJECT_ID:-}" ]; then
    printf '%s\n' "$AOS_PROJECT_ID"
    return 0
  fi

  local remote_url
  remote_url=$(git config --get remote.origin.url 2>/dev/null) || remote_url=""

  # Tier 1: cached TSV from previous Tier-2 fetch.
  local _cache_dir="${HOME}/.cache/aos"
  local _cache="${_cache_dir}/project_remote_map.tsv"
  if [ -n "$remote_url" ] && [ -r "$_cache" ]; then
    local _hit
    _hit=$(awk -F'\t' -v u="$remote_url" \
           'length($2)>0 && (index(u,$2)>0 || index($2,u)>0) {print $1; exit}' \
           "$_cache" 2>/dev/null) || _hit=""
    if [ -n "$_hit" ]; then
      printf '%s\n' "$_hit"
      return 0
    fi
  fi

  # Tier 2: live /api/projects fetch — only when API known online.
  if [ "${API_ONLINE:-0}" = "1" ] && [ -n "${AOS_API_BASE:-}" ]; then
    local _proj_tmp
    _proj_tmp=$(mktemp 2>/dev/null) || _proj_tmp="/tmp/aos_projects_$$"
    if curl -fsS --max-time 2 \
         -H "X-Actor-Team-Id: ${AOS_ACTOR_TEAM_ID:-team_unknown}" \
         "${AOS_API_BASE}/api/projects" \
         -o "$_proj_tmp" 2>/dev/null; then
      mkdir -p "$_cache_dir" 2>/dev/null || true
      if command -v python3 >/dev/null 2>&1; then
        python3 - "$_proj_tmp" "$_cache" <<'PYEOF' 2>/dev/null
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    lines = []
    for p in (d.get('projects') or []):
        pid = (p.get('id') or '').strip()
        gr  = (p.get('git_remote') or p.get('repo') or '').strip()
        if pid and gr:
            lines.append(pid + '\t' + gr)
    with open(sys.argv[2], 'w') as out:
        out.write('\n'.join(lines) + '\n')
except Exception:
    pass
PYEOF
      fi
      rm -f "$_proj_tmp" 2>/dev/null || true
      if [ -r "$_cache" ] && [ -n "$remote_url" ]; then
        local _hit2
        _hit2=$(awk -F'\t' -v u="$remote_url" \
                'length($2)>0 && (index(u,$2)>0 || index($2,u)>0) {print $1; exit}' \
                "$_cache" 2>/dev/null) || _hit2=""
        if [ -n "$_hit2" ]; then
          printf '%s\n' "$_hit2"
          return 0
        fi
      fi
    else
      rm -f "$_proj_tmp" 2>/dev/null || true
    fi
  fi

  # Tier 3: static fallback (includes all registered spokes as of 2026-05-11).
  case "$remote_url" in
    *agents-os*)                           printf 'agents-os\n' ;;
    *SmallFarmsAgents*|*smallfarmsagents*) printf 'smallfarmsagents\n' ;;
    *nimrod-bio*|*NimrodBio*)              printf 'nimrod-bio\n' ;;
    *TikTrack*|*tiktrack*)                 printf 'tiktrack\n' ;;
    *EyalAmit*|*eyalamit*)                 printf 'eyalamit\n' ;;
    *HobbitHome*|*hobbithome*)             printf 'hobbithome\n' ;;
    *Microgreens*|*microgreens*)           printf 'microgreens\n' ;;
    *AOS-Sandbox-Lean*)                    printf 'aos-sandbox-lean\n' ;;
    *AOS-Sandbox-Full*)                    printf 'aos-sandbox-full\n' ;;
    *agros-insite*)                        printf 'agros-insite\n' ;;
    *)
      printf 'agents-os\n'
      if [ "${_MSG_PREFLIGHT_VERBOSE:-0}" -eq 1 ]; then
        printf '⚠ msg_detect_project_id: unknown remote %s — defaulting to agents-os (likely wrong)\n' \
               "$remote_url" >&2
        printf '  Fix: set AOS_PROJECT_ID env var, or register spoke via /AOS_project-init.\n' >&2
      fi
      ;;
  esac
}

# --- Internal helper — emit auth-class warning + append JSONL audit log -----
# _emit_auth_fallback_warning <code> <team_id> <api_path>
# Mandatory visible warning on stderr (NOT gated by verbose flag).
# ADR043 v1.5.0 §5 Rule 5 / R-MSG-02.
_emit_auth_fallback_warning() {
  local code="${1:-ACTOR_KEY_NOT_CONFIGURED}"
  local team_id="${2:-unknown}"
  local api_path="${3:-unknown}"
  local branch
  branch=$(git branch --show-current 2>/dev/null) || branch="unknown"
  # Mandatory visible warning on stderr — NOT gated by verbose flag.
  printf '⚠ API auth unavailable (%s) — falling back to file delivery.\n' "$code" >&2
  printf '  Cause: server has no provisioned key for %s.\n' "$team_id" >&2
  printf '  Admin: provision via POST /api/admin/actors/%s/issue-key (team_00 only).\n' "$team_id" >&2
  printf '  MSG WILL be delivered to origin/main via file-fallback; no DB record created.\n' >&2
  # Mandatory JSONL audit entry.
  local ts
  ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null) || ts=$(date '+%Y-%m-%dT%H:%M:%SZ')
  local repo_root
  repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || repo_root="$(pwd)"
  local log_dir="${repo_root}/_COMMUNICATION/_log"
  local log_file="${log_dir}/messages.log"
  mkdir -p "$log_dir" 2>/dev/null || true
  local entry
  entry="{\"ts\":\"${ts}\",\"op\":\"auth_fallback\",\"code\":\"${code}\",\"team_id\":\"${team_id}\",\"api_path\":\"${api_path}\",\"branch\":\"${branch}\",\"channel\":\"file_fallback\"}"
  printf '%s\n' "$entry" >> "$log_file" 2>/dev/null || true
}

# --- curl wrapper (ADR043 v1.5.0 R-MSG-02) ----------------------------------
# Usage:  msg_curl <method> <api_path> [json_body]
# Example: msg_curl GET "/api/messaging/inbox?to_team=team_99"
#          msg_curl POST "/api/messaging/send" "$payload"
# Auth:    Set AOS_ACTOR_API_KEY env var (shared secret configured in AOS_V3_ACTOR_KEYS
#          on the server) to authenticate. Required when server has AOS_V3_ACTOR_KEYS
#          set (production). Not required in local dev (AOS_V3_TRUST_CLIENT_ACTOR=1).
# Exit codes (R-MSG-02 / F-A-001):
#   0 — success; response body on stdout
#   1 — programmer error (4xx schema/unknown-project/missing-header); caller MUST EXIT
#   3 — auth-class error (401/403/ACTOR_KEY_NOT_CONFIGURED); MSG_CURL_AUTH_FALLBACK=1; use file-fallback
#   4 — transient/network error (5xx/000/connection-reset); use file-fallback
msg_curl() {
  local method="${1:?usage: msg_curl <method> <api_path> [json_body]}"
  local api_path="${2:?usage: msg_curl <method> <api_path> [json_body]}"
  local data="${3:-}"
  local team="${AOS_ACTOR_TEAM_ID:-}"
  if [ -z "$team" ]; then
    printf 'ERROR: AOS_ACTOR_TEAM_ID env var must be set before calling msg_curl\n' >&2
    return 2
  fi
  # R-MSG-02 API_ONLINE guard (AC-8 / AOS-V4.2-WP-POST-MIGRATION-HARDENING):
  # Refuse when API is offline. Callers handle return code 4 (transient) per
  # ADR043 §5 Rule 5 and fall back to msg_deliver_file (R-MSG-02 contract).
  if [ "${API_ONLINE:-0}" -ne 1 ]; then
    echo "ERROR: API offline (${API_ERROR:-no details}) — msg_curl refused. Use msg_deliver_file for file-based MSG delivery per R-MSG-02 Rule 5." >&2
    return 4
  fi
  local proj
  proj=$(msg_detect_project_id)
  local args
  args=(-s -X "$method" -H "X-Actor-Team-Id: $team" -H "X-Project-Id: $proj")
  # Inject API key when configured (AOS_V3_ACTOR_KEYS production auth model — SEC-001)
  local api_key="${AOS_ACTOR_API_KEY:-}"
  if [ -n "$api_key" ]; then
    args=("${args[@]}" -H "X-Actor-Api-Key: $api_key")
  fi
  if [ -n "$data" ]; then
    args=("${args[@]}" -H "Content-Type: application/json" -d "$data")
  fi

  local _body_tmp
  _body_tmp=$(mktemp 2>/dev/null) || _body_tmp="/tmp/aos_msg_curl_$$_${RANDOM:-0}"
  local _http_status
  _http_status=$(curl "${args[@]}" -o "$_body_tmp" -w '%{http_code}' \
                 "${AOS_API_BASE}${api_path}" 2>/dev/null) || _http_status="000"
  local _body
  _body=$(cat "$_body_tmp" 2>/dev/null) || _body=""
  rm -f "$_body_tmp" 2>/dev/null || true

  case "$_http_status" in
    2*)
      printf '%s' "$_body"
      return 0
      ;;
    401|403)
      local _auth_code
      _auth_code=$(printf '%s' "$_body" | grep -o '"code":"[^"]*"' | head -1 | \
                   sed 's/"code":"//;s/".*//') || _auth_code="HTTP_${_http_status}"
      _auth_code="${_auth_code:-HTTP_${_http_status}}"
      _emit_auth_fallback_warning "$_auth_code" "$team" "$api_path"
      export MSG_CURL_AUTH_FALLBACK=1
      export MSG_CURL_AUTH_CODE="$_auth_code"
      return 3
      ;;
    5*|"000"|"")
      # Transient/network error — proceed to file-fallback (F-A-001 exit 4)
      printf 'WARN: msg_curl transient error HTTP %s from %s%s — proceeding to file-fallback\n' \
             "$_http_status" "$AOS_API_BASE" "$api_path" >&2
      printf '%s' "$_body" >&2
      return 4
      ;;
    *)
      if printf '%s' "$_body" | grep -q 'ACTOR_KEY_NOT_CONFIGURED'; then
        _emit_auth_fallback_warning "ACTOR_KEY_NOT_CONFIGURED" "$team" "$api_path"
        export MSG_CURL_AUTH_FALLBACK=1
        export MSG_CURL_AUTH_CODE="ACTOR_KEY_NOT_CONFIGURED"
        return 3
      fi
      printf 'ERROR: msg_curl got HTTP %s from %s%s\n' \
             "$_http_status" "$AOS_API_BASE" "$api_path" >&2
      printf '%s' "$_body" >&2
      return 1
      ;;
  esac
}

# ── Bypass audit log helper (AOS-V4-WP-MSG-HARDENING §bypass) ─────────────
# msg_log_bypass <bypassed_file> [branch]
#   Appends a JSONL entry with op=hook_bypassed to messages.log.
#   Called by the pre-commit hook bypass path (git commit --no-verify).
#   Falls back to local file append if W4 MSG-LOG endpoint is not available.
msg_log_bypass() {
  local bypassed_file="${1:-unknown}"
  local branch="${2:-$(git branch --show-current 2>/dev/null || printf 'unknown')}"
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

# --- MSG sequence id allocator (ADR043 v1.5.0 / R-MSG-09) ------------------
# msg_next_id [from_team] [to_team] [date_stamp]
# Returns next available MSG-HUB-YYYYMMDD-NNN for to_team's inbox in current repo.
#
# NOTE (BUILD_CHECKLIST F-MSG-002): This helper is snapshot-based, not atomic.
# Two consecutive calls without writing the first returned MSG file will return
# the SAME id. The expected usage is: call msg_next_id, write the MSG file at
# the returned path immediately, then call msg_next_id again if a second id is
# needed. In test scenarios requiring sequential ids, touch the first returned
# file before the second call:
#   id1=$(msg_next_id team_100 team_10)
#   touch "$inbox_dir/${id1}.md"
#   id2=$(msg_next_id team_100 team_10)   # → NNN+1 ✓
msg_next_id() {
  local from_team="${1:-${AOS_ACTOR_TEAM_ID:-}}"
  local to_team="${2:-${from_team}}"
  local date_stamp="${3:-$(date -u '+%Y%m%d' 2>/dev/null)}"

  if [ -z "$to_team" ]; then
    printf 'ERROR: msg_next_id: to_team argument required (or set AOS_ACTOR_TEAM_ID)\n' >&2
    return 2
  fi

  local repo_root
  repo_root=$(git rev-parse --show-toplevel 2>/dev/null) || repo_root="$(pwd)"
  local inbox_dir="${repo_root}/_COMMUNICATION/${to_team}"

  local last_nnn=0
  if [ -d "$inbox_dir" ]; then
    local _found
    _found=$(ls "${inbox_dir}/MSG-HUB-${date_stamp}-"[0-9][0-9][0-9].md 2>/dev/null \
             | sed -n "s|.*MSG-HUB-${date_stamp}-0*\([1-9][0-9]*\)\.md|\1|p; \
                       s|.*MSG-HUB-${date_stamp}-000\.md|0|p" \
             | sort -n | tail -1) || _found=""
    last_nnn="${_found:-0}"
  fi

  local next_nnn
  next_nnn=$(( last_nnn + 1 ))
  printf 'MSG-HUB-%s-%03d\n' "$date_stamp" "$next_nnn"
}

# Export helpers so subshells can use them too (best-effort; bash-only).
export -f msg_detect_project_id 2>/dev/null || true
export -f msg_curl 2>/dev/null || true
export -f msg_log_bypass 2>/dev/null || true
export -f msg_deliver_file_cross_domain 2>/dev/null || true
export -f msg_next_id 2>/dev/null || true
export -f _emit_auth_fallback_warning 2>/dev/null || true

# Branch state check (AOS-V4-WP-SPAWN-4-BRANCH-GUARD AC-10) — non-blocking warning
bash scripts/check_branch_state.sh || true

# Auto-probe when sourced (so callers just `source ... && echo $API_ONLINE`)
_probe_api

# Auto-detect domain on source so callers can `echo $AOS_PROJECT_ID` immediately.
export AOS_PROJECT_ID="${AOS_PROJECT_ID:-$(msg_detect_project_id)}"
# Use if/fi so `source` exits 0 when verbose=0 (a bare `[ ... ] && echo` is non-zero and breaks callers).
if [ "$_MSG_PREFLIGHT_VERBOSE" -eq 1 ]; then
  printf '✓ Project context: %s\n' "$AOS_PROJECT_ID"
fi
