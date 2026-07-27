#!/usr/bin/env bash
# Usage: git_health_check.sh [project_root]
# Checks:
#   1. Is this a git repo?
#   2. Current branch name
#   3. Uncommitted changes (warn)
#   4. Stale worktrees (warn) — `git worktree list` should show only main
#   5. Remote sync status (ahead/behind)
# Exit: 0 = healthy, 1 = warnings found (non-blocking), 2 = fatal
set -euo pipefail
ROOT="${1:-.}"
cd "$ROOT"

WARNINGS=0

# Check 1: Git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "FAIL: Not a git repository: $ROOT"
  exit 2
fi

# Check 2: Branch
BRANCH=$(git branch --show-current)
echo "Branch: $BRANCH"

# Check 3: Uncommitted changes
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
  echo "WARN: Uncommitted changes detected"
  WARNINGS=$((WARNINGS + 1))
fi

# Check 4: Stale worktrees
WT_COUNT=$(git worktree list | wc -l | tr -d ' ')
if [ "$WT_COUNT" -gt 1 ]; then
  echo "WARN: $WT_COUNT worktrees found (expected 1)"
  git worktree list
  WARNINGS=$((WARNINGS + 1))
fi

# Check 5: Remote sync
if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
  AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
  BEHIND=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0)
  [ "$AHEAD" -gt 0 ] && echo "INFO: $AHEAD commits ahead of remote"
  [ "$BEHIND" -gt 0 ] && echo "WARN: $BEHIND commits behind remote" && WARNINGS=$((WARNINGS + 1))
fi

echo "Health check: $WARNINGS warnings"
if [ "$WARNINGS" -gt 0 ]; then
  exit 1
else
  exit 0
fi
