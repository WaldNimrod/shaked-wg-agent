#!/usr/bin/env bash
# Usage: validate_context_consistency.sh <project_root>
# Checks: CLAUDE.md, .cursorrules exist and contain same iron rules, boundaries
# Exit: 0 = consistent, 1 = drift detected
set -euo pipefail

PROJECT_ROOT="${1:?Usage: validate_context_consistency.sh <project_root>}"
DRIFT=0

CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"
CURSORRULES="$PROJECT_ROOT/.cursorrules"
IDENTITY="$PROJECT_ROOT/_aos/project_identity.yaml"

# Check files exist
if [ ! -f "$CLAUDE_MD" ]; then
  echo "WARN: CLAUDE.md not found at $CLAUDE_MD"
  DRIFT=1
fi

if [ ! -f "$CURSORRULES" ]; then
  echo "INFO: .cursorrules not found — optional for L0 projects"
fi

if [ ! -f "$IDENTITY" ]; then
  echo "WARN: project_identity.yaml not found — cannot verify boundaries"
  exit 1
fi

# Extract forbidden_patterns from identity
FORBIDDEN=$(python3 -c "
import yaml
with open('$IDENTITY') as f:
    d = yaml.safe_load(f) or {}
b = d.get('boundaries', {})
if not isinstance(b, dict): b = {}
for p in b.get('forbidden_patterns', []):
    print(p)
" 2>/dev/null || true)

# Boundary check: prefer delegation to project_identity (avoids duplicating every pattern in long files)
check_patterns_in_file() {
  local file="$1"
  local label="$2"
  if [ ! -f "$file" ] || [ -z "$FORBIDDEN" ]; then
    return 0
  fi
  if grep -q "project_identity.yaml" "$file" 2>/dev/null; then
    return 0
  fi
  while IFS= read -r pattern; do
    if ! grep -qF "$pattern" "$file" 2>/dev/null; then
      echo "DRIFT: $label missing forbidden_pattern: $pattern"
      DRIFT=1
    fi
  done <<< "$FORBIDDEN"
}

if [ -f "$CLAUDE_MD" ] && [ -n "$FORBIDDEN" ]; then
  check_patterns_in_file "$CLAUDE_MD" "CLAUDE.md"
fi

if [ -f "$CURSORRULES" ] && [ -n "$FORBIDDEN" ]; then
  check_patterns_in_file "$CURSORRULES" ".cursorrules"
fi

if [ "$DRIFT" -eq 0 ]; then
  echo "PASS: Context files are consistent with project_identity.yaml"
else
  echo "FAIL: Context drift detected — regenerate with generate_context.sh"
fi
exit "$DRIFT"
