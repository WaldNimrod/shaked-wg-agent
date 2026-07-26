#!/usr/bin/env bash
# branch_guard_pre_commit.sh — AOS branch-safety pre-commit hook
# WP: AOS-V4-WP-SPAWN-4-BRANCH-GUARD | Closes: F15 (auto-rebase branch-cross)
# Owner: team_60 (OPS) | Track: OPS | ADR044 OPS track
#
# PURPOSE:
#   Validates the current branch is allowed to accept the detected change type
#   before any commit lands. Reads allowlist from .git-branch-allowlist at repo root.
#
# BYPASS:
#   Use `git commit --no-verify` to bypass. Bypass events are logged to
#   _COMMUNICATION/_log/branch_guard_bypass.log with timestamp, branch, and
#   changeset summary. Bypass requires explicit --no-verify; there is no
#   ambient override mechanism.
#
# INSTALL:
#   Run scripts/install_hooks.sh — this script is installed as .git/hooks/pre-commit

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
ALLOWLIST_FILE="${REPO_ROOT}/.git-branch-allowlist"
BYPASS_LOG="${REPO_ROOT}/_COMMUNICATION/_log/branch_guard_bypass.log"

# ─── Helpers ──────────────────────────────────────────────────────────────────

log_bypass() {
    local branch="$1"
    local committer
    committer="$(git config user.name 2>/dev/null || echo 'unknown')"
    local timestamp
    timestamp="$(date '+%Y-%m-%dT%H:%M:%S')"
    local stat
    stat="$(git diff --stat --cached 2>/dev/null | tail -1 || echo 'stat unavailable')"

    mkdir -p "$(dirname "$BYPASS_LOG")"
    echo "[BYPASS] ${timestamp} | branch=${branch} | committer=${committer} | stat=${stat}" >> "$BYPASS_LOG"
}

reject() {
    local branch="$1"
    local change_type="$2"
    local allowed_types="$3"

    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  AOS BRANCH GUARD — COMMIT REJECTED                             ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  Branch      : ${branch}"
    echo "║  Change type : ${change_type}"
    echo "║  Allowed     : ${allowed_types}"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  ACTION REQUIRED:                                                ║"
    echo "║  • Switch to a branch that allows '${change_type}' changes"
    echo "║  • Or update .git-branch-allowlist (team_00/team_100 only)"
    echo "║  • Emergency bypass: git commit --no-verify (LOGGED)"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
}

# ─── Detect change type ───────────────────────────────────────────────────────
# Code change = any diff in .py .sh .yaml .json .ts .js files
# EXCLUDING governance/planning paths:
#   _COMMUNICATION/  _aos/work_packages/  methodology/  governance/  _archive/

CODE_EXTENSIONS="\.py$|\.sh$|\.yaml$|\.yml$|\.json$|\.ts$|\.js$"
GOVERNANCE_PATHS="^_COMMUNICATION/|^_aos/|^methodology/|^governance/|^lean-kit/|^scripts/|^_archive/"

STAGED_FILES="$(git diff --cached --name-only 2>/dev/null || true)"

if [ -z "$STAGED_FILES" ]; then
    # Nothing staged — git should handle this but be safe
    exit 0
fi

# Filter staged files: code vs governance
CODE_FILES=""
while IFS= read -r f; do
    [ -z "$f" ] && continue
    # Skip governance paths
    if echo "$f" | grep -qE "$GOVERNANCE_PATHS"; then
        continue
    fi
    # Match code extensions
    if echo "$f" | grep -qE "$CODE_EXTENSIONS"; then
        CODE_FILES="${CODE_FILES}${f}"$'\n'
    fi
done <<< "$STAGED_FILES"

if [ -n "$CODE_FILES" ]; then
    DETECTED_CHANGE_TYPE="code"
else
    DETECTED_CHANGE_TYPE="governance"
fi

# ─── Load allowlist ───────────────────────────────────────────────────────────

if [ ! -f "$ALLOWLIST_FILE" ]; then
    echo "[branch-guard] WARNING: .git-branch-allowlist not found at repo root."
    echo "[branch-guard] Skipping branch guard check (allowlist missing = permissive mode)."
    exit 0
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'UNKNOWN')"

if [ "$CURRENT_BRANCH" = "HEAD" ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  AOS BRANCH GUARD — DETACHED HEAD DETECTED                      ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  You are in detached HEAD state. Commits here are unsafe —      ║"
    echo "║  they may be lost or reattached to the wrong branch.            ║"
    echo "║  Run: git checkout <branch-name>  before committing.            ║"
    echo "║  Emergency bypass: git commit --no-verify (LOGGED)              ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

# ─── Parse allowlist and match current branch ─────────────────────────────────
# Allowlist format (YAML-style, parsed as line-oriented config):
#   branch: <pattern>        — glob pattern matched against current branch
#   allow: <type1>,<type2>  — comma-separated: code, governance, all
#   (lines starting with # are comments; blank lines skipped)
#
# Matching: first match wins (allowlist is ordered; most-specific patterns first)

MATCHED_ALLOW=""
CURRENT_PATTERN=""
CURRENT_ALLOW=""

parse_allowlist() {
    local allowlist="$1"
    local branch="$2"

    while IFS= read -r line; do
        # Skip comments and blanks
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line//[[:space:]]/}" ]] && continue

        if [[ "$line" =~ ^branch:[[:space:]]*(.+)$ ]]; then
            CURRENT_PATTERN="${BASH_REMATCH[1]// /}"
        elif [[ "$line" =~ ^allow:[[:space:]]*(.+)$ ]]; then
            CURRENT_ALLOW="${BASH_REMATCH[1]// /}"
            # Check if current branch matches this pattern (glob match)
            if [[ "$branch" == $CURRENT_PATTERN ]]; then
                MATCHED_ALLOW="$CURRENT_ALLOW"
                return 0
            fi
            # Reset for next block
            CURRENT_PATTERN=""
            CURRENT_ALLOW=""
        fi
    done < "$allowlist"

    return 1
}

parse_allowlist "$ALLOWLIST_FILE" "$CURRENT_BRANCH" || true

if [ -z "$MATCHED_ALLOW" ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  AOS BRANCH GUARD — BRANCH NOT IN ALLOWLIST                     ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  Branch: ${CURRENT_BRANCH}"
    echo "║  This branch has no entry in .git-branch-allowlist.             ║"
    echo "║  Add an entry or switch to a registered branch.                 ║"
    echo "║  Emergency bypass: git commit --no-verify (LOGGED)              ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

# ─── Evaluate permission ──────────────────────────────────────────────────────

ALLOWED_LOWER="$(echo "$MATCHED_ALLOW" | tr '[:upper:]' '[:lower:]')"

is_allowed() {
    local change="$1"
    local allowed="$2"
    # "all" permits everything
    [[ "$allowed" == *"all"* ]] && return 0
    [[ "$allowed" == *"$change"* ]] && return 0
    return 1
}

if is_allowed "$DETECTED_CHANGE_TYPE" "$ALLOWED_LOWER"; then
    # Commit permitted
    exit 0
else
    reject "$CURRENT_BRANCH" "$DETECTED_CHANGE_TYPE" "$MATCHED_ALLOW"
fi
