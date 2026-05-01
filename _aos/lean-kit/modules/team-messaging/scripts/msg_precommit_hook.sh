#!/usr/bin/env bash
# msg_precommit_hook.sh — AOS MSG frontmatter pre-commit validator
# WP: AOS-V4-WP-MSG-HARDENING | Implements: C12 | Closes: F8, F9, F11
# ADR043 v1.2.0 + v1.3.0 (continuation fields for formal types)
#
# PURPOSE:
#   Validates every staged _COMMUNICATION/team_*/MSG-*.md file for:
#     1. Filename pattern: MSG-HUB-YYYYMMDD-NNN.md
#     2. Required frontmatter fields: from_team, to_team, type, subject, date, id
#     3. schema_version (required when AOS_MSG_STRICT=1; warn-only by default)
#     4. Continuation fields for formal types: next_step, handoff_to,
#        handoff_context_pointer (task, task_response, routing,
#        session_activation, gate_response) per ADR043 v1.3.0
#
# INSTALL: Run scripts/install_hooks.sh (auto-appended to pre-commit)
#
# BYPASS: git commit --no-verify bypasses this hook.
#   Bypass is detected by the post-commit hook and logged to
#   _COMMUNICATION/_log/messages.log with op: hook_bypassed.
#
# PERFORMANCE: Single awk invocation for ALL staged MSG files.
#   Target: <200ms on 50 staged MSGs.
#
# STRICT MODE: AOS_MSG_STRICT=1  →  schema_version missing = REJECT
#              AOS_MSG_STRICT=0  →  schema_version missing = WARN only (default)
#
# COMPATIBILITY: bash 3.2+ (macOS default), POSIX awk with FILENAME (BSD/GNU)

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
AOS_MSG_STRICT="${AOS_MSG_STRICT:-0}"

# ─── Output helpers ───────────────────────────────────────────────────────────

_fail() {
    printf '\n' >&2
    printf '╔══════════════════════════════════════════════════════════════════╗\n' >&2
    printf '║  AOS MSG HOOK — COMMIT REJECTED                                  ║\n' >&2
    printf '╠══════════════════════════════════════════════════════════════════╣\n' >&2
    printf '%s\n' "$1" | while IFS= read -r line; do
        printf "║  %-64s║\n" "$line" >&2
    done
    printf '╠══════════════════════════════════════════════════════════════════╣\n' >&2
    printf '║  Fix the issue above and re-stage the file, then retry.          ║\n' >&2
    printf '║  Emergency bypass: git commit --no-verify  (LOGGED to MSG-LOG)  ║\n' >&2
    printf '╚══════════════════════════════════════════════════════════════════╝\n' >&2
    printf '\n' >&2
    exit 1
}

_has_value() {
    # Pure bash — no subshell, no external process (critical for performance)
    local v="$1"
    v="${v// /}"       # strip spaces
    v="${v//$'\t'/}"   # strip tabs
    v="${v//\'/}"      # strip single quotes
    v="${v//\"/}"      # strip double quotes
    [ -n "$v" ]
}

# ─── Collect staged MSG files ────────────────────────────────────────────────

STAGED_MSGS=""
while IFS= read -r f; do
    [ -z "$f" ] && continue
    if printf '%s' "$f" | grep -qE '^_COMMUNICATION/team_[0-9]+/MSG-.+\.md$'; then
        STAGED_MSGS="${STAGED_MSGS}${f}"$'\n'
    fi
done < <(git diff --cached --name-only 2>/dev/null || true)

[ -z "$STAGED_MSGS" ] && exit 0

# ─── Phase 1: filename validation + build file list for awk ───────────────────

ERRORS=""
WARNINGS=""
AWK_FILE_ARGS=""        # space-separated absolute paths for awk
# Map: relative path -> absolute path (for error reporting with relative path)
# We pass paths as awk args; awk uses FILENAME (absolute). We'll strip REPO_ROOT prefix in output.

while IFS= read -r staged_file; do
    [ -z "$staged_file" ] && continue
    basename_file="${staged_file##*/}"

    if ! printf '%s' "$basename_file" | grep -qE '^MSG-HUB-[0-9]{8}-[0-9]{3}\.md$'; then
        ERRORS="${ERRORS}File: ${staged_file}
  FAIL: filename does not match required pattern MSG-HUB-YYYYMMDD-NNN.md
  Got: ${basename_file}
  Fix: rename to MSG-HUB-YYYYMMDD-NNN.md  (e.g. MSG-HUB-20260430-001.md)
  Reference: ADR043 v1.2.0 §3 (filename pattern)
"
        continue
    fi

    local_path="${REPO_ROOT}/${staged_file}"
    if [ -f "$local_path" ]; then
        AWK_FILE_ARGS="${AWK_FILE_ARGS} ${local_path}"
    else
        # File removed from working tree but staged — skip (git show fallback not needed
        # for the awk path; emit clear error)
        ERRORS="${ERRORS}File: ${staged_file}
  FAIL: staged file not found in working tree: ${local_path}
  Fix: ensure the file exists before committing
"
    fi
done <<< "$STAGED_MSGS"

# ─── Phase 2: single awk pass over ALL valid files ────────────────────────────

FIELD_LINES=""
if [ -n "$AWK_FILE_ARGS" ]; then
    # Write awk script to temp file to avoid quoting issues with eval/inline scripts.
    # Script extracts frontmatter fields from multiple files in one pass.
    # Output: "<absolute_path>|<key>=<value>" per field found.
    _awk_script="$(mktemp /tmp/aos_msg_awk_XXXXXX.awk)"
    cat > "$_awk_script" << 'AWK_SCRIPT_EOF'
BEGIN {
  in_fm = 0
  fields = " from_team to_team type subject date id schema_version next_step handoff_to handoff_context_pointer "
}
FNR == 1 { in_fm = 0; cur_file = FILENAME }
/^---[[:space:]]*$/ {
  if (in_fm == 0) { in_fm = 1; next }
  else { in_fm = 0; next }
}
in_fm {
  colon = index($0, ":")
  if (colon < 2) next
  key = substr($0, 1, colon - 1)
  if (index(fields, " " key " ") == 0) next
  val = substr($0, colon + 1)
  while (length(val) > 0 && (substr(val,1,1) == " " || substr(val,1,1) == "\t"))
    val = substr(val, 2)
  print cur_file "|" key "=" val
}
AWK_SCRIPT_EOF

    # Single awk invocation over ALL valid files
    FIELD_LINES="$(eval awk -f "$_awk_script" $AWK_FILE_ARGS 2>/dev/null || true)"
    rm -f "$_awk_script"
fi

# ─── Phase 3: validate per-file using extracted fields ────────────────────────
# Group FIELD_LINES by file, then validate each group.
# Since awk processes files in order, lines for a file are contiguous.

_cur_abs=""  # current absolute path being processed
_fm_from_team="" _fm_to_team="" _fm_type="" _fm_subject="" _fm_date="" _fm_id=""
_fm_schema_version="" _fm_next_step="" _fm_handoff_to="" _fm_handoff_context_pointer=""

_validate_file() {
    local abs_path="$1"
    # Convert absolute path back to relative for error messages
    local rel_path="${abs_path#${REPO_ROOT}/}"

    # Required fields
    for _fp in \
        "from_team:$_fm_from_team" \
        "to_team:$_fm_to_team" \
        "type:$_fm_type" \
        "subject:$_fm_subject" \
        "date:$_fm_date" \
        "id:$_fm_id"; do
        _fn="${_fp%%:*}"
        _fv="${_fp#*:}"
        if ! _has_value "$_fv"; then
            ERRORS="${ERRORS}File: ${rel_path}
  FAIL: required frontmatter field '${_fn}' is missing or empty
  Fix: add '${_fn}: <value>' to the YAML frontmatter block
  Reference: ADR043 v1.2.0 §3 (required: from_team, to_team, type, subject, date, id)
"
        fi
    done

    # schema_version
    if ! _has_value "$_fm_schema_version"; then
        if [ "$AOS_MSG_STRICT" = "1" ]; then
            ERRORS="${ERRORS}File: ${rel_path}
  FAIL: 'schema_version' missing (AOS_MSG_STRICT=1 enforces it)
  Fix: add 'schema_version: aos_v1_team_messaging' to frontmatter
  Reference: ADR043 v1.2.0 §3.1 strict mode
"
        else
            WARNINGS="${WARNINGS}File: ${rel_path}
  WARN: 'schema_version' missing — add: schema_version: aos_v1_team_messaging
  (Set AOS_MSG_STRICT=1 to treat missing schema_version as a hard failure)
"
        fi
    elif [ "$_fm_schema_version" != "aos_v1_team_messaging" ]; then
        ERRORS="${ERRORS}File: ${rel_path}
  FAIL: 'schema_version' has invalid value: '${_fm_schema_version}'
  Expected: aos_v1_team_messaging
  Reference: ADR043 v1.2.0 §3.1
"
    fi

    # Continuation fields for formal types (ADR043 v1.3.0 §13)
    # Strip quotes/whitespace from type — pure bash, no subshell
    _stype="$_fm_type"
    _stype="${_stype// /}"
    _stype="${_stype//$'\t'/}"
    _stype="${_stype//\'/}"
    _stype="${_stype//\"/}"
    if [ -n "$_stype" ]; then
        case "$_stype" in
            task|task_response|routing|session_activation|gate_response)
                for _cf in \
                    "next_step:$_fm_next_step" \
                    "handoff_to:$_fm_handoff_to" \
                    "handoff_context_pointer:$_fm_handoff_context_pointer"; do
                    _cn="${_cf%%:*}"
                    _cv="${_cf#*:}"
                    if ! _has_value "$_cv"; then
                        ERRORS="${ERRORS}File: ${rel_path}
  FAIL: formal type '${_stype}' requires continuation field '${_cn}'
  Fix: add '${_cn}: <value>' to frontmatter
  Reference: ADR043 v1.3.0 §13 (required for:
    task, task_response, routing, session_activation, gate_response)
"
                    fi
                done ;;
        esac
    fi
}

_reset_fm() {
    _fm_from_team="" _fm_to_team="" _fm_type="" _fm_subject="" _fm_date="" _fm_id=""
    _fm_schema_version="" _fm_next_step="" _fm_handoff_to="" _fm_handoff_context_pointer=""
}

if [ -n "$FIELD_LINES" ]; then
    while IFS='|' read -r _abs _field_line; do
        [ -z "$_abs" ] && continue
        if [ "$_abs" != "$_cur_abs" ]; then
            # Validate previous file before switching (skip if first iteration)
            if [ -n "$_cur_abs" ]; then
                _validate_file "$_cur_abs"
            fi
            _cur_abs="$_abs"
            _reset_fm
        fi
        _k="${_field_line%%=*}"
        _v="${_field_line#*=}"
        case "$_k" in
            from_team)               _fm_from_team="$_v" ;;
            to_team)                 _fm_to_team="$_v" ;;
            type)                    _fm_type="$_v" ;;
            subject)                 _fm_subject="$_v" ;;
            date)                    _fm_date="$_v" ;;
            id)                      _fm_id="$_v" ;;
            schema_version)          _fm_schema_version="$_v" ;;
            next_step)               _fm_next_step="$_v" ;;
            handoff_to)              _fm_handoff_to="$_v" ;;
            handoff_context_pointer) _fm_handoff_context_pointer="$_v" ;;
        esac
    done <<< "$FIELD_LINES"
    # Validate last file
    [ -n "$_cur_abs" ] && _validate_file "$_cur_abs"
else
    # No field lines extracted — every file in AWK_FILE_ARGS has empty frontmatter
    # (or AWK_FILE_ARGS was empty). Only report error if we had valid files to process.
    if [ -n "$AWK_FILE_ARGS" ]; then
        while IFS= read -r sf; do
            [ -z "$sf" ] && continue
            # Treat as "all required fields missing" via normal validation
            _cur_abs="${REPO_ROOT}/${sf}"
            _reset_fm
            _validate_file "$_cur_abs"
        done <<< "$STAGED_MSGS"
    fi
fi

# ── Emit warnings ─────────────────────────────────────────────────────────────
if [ -n "$WARNINGS" ]; then
    printf '\n[msg-hook] WARNINGS (non-blocking):\n' >&2
    printf '%s\n' "$WARNINGS" >&2
fi

# ── Reject on errors ──────────────────────────────────────────────────────────
if [ -n "$ERRORS" ]; then
    _fail "$ERRORS"
fi

# Signal post-commit bypass detector that this hook ran.
# Touch a sentinel file in /tmp — the post-commit hook checks for its presence
# to determine whether the pre-commit hook ran (bypass detection mechanism).
touch "/tmp/aos_msg_hook_ran_$$" 2>/dev/null || true

exit 0
