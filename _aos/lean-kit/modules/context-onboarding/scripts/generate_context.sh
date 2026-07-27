#!/usr/bin/env bash
# Usage: generate_context.sh <project_root> <engine> [--output <path>]
# Engines: claude-code, cursor, openai
# Output: rendered context file to stdout or --output path
set -euo pipefail

PROJECT_ROOT="${1:?Usage: generate_context.sh <project_root> <engine> [--output <path>]}"
ENGINE="${2:?Usage: generate_context.sh <project_root> <engine> [--output <path>]}"
OUTPUT=""
if [ "${3:-}" = "--output" ]; then
  OUTPUT="${4:?--output requires a path}"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODULE_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$MODULE_DIR/templates"

# Resolve template based on engine
case "$ENGINE" in
  claude-code) TEMPLATE="$TEMPLATES_DIR/CLAUDE_MD.template" ;;
  cursor)      TEMPLATE="$TEMPLATES_DIR/CURSORRULES.template" ;;
  openai)      TEMPLATE="$TEMPLATES_DIR/SYSTEM_PROMPT.template" ;;
  *)
    echo "ERROR: Unknown engine '$ENGINE'. Use: claude-code, cursor, openai" >&2
    exit 1
    ;;
esac

if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: Template not found: $TEMPLATE" >&2
  exit 1
fi

# Resolve variables from _aos/ files using python3
RENDERED=$(python3 -c "
import yaml, os, sys

root = '$PROJECT_ROOT'
identity_path = os.path.join(root, '_aos/project_identity.yaml')
metadata_path = os.path.join(root, '_aos/metadata.yaml')
teams_path = os.path.join(root, '_aos/team_assignments.yaml')
context_path = os.path.join(root, '_aos/context/PROJECT_CONTEXT.md')

# Load identity
identity = {}
if os.path.isfile(identity_path):
    with open(identity_path) as f:
        identity = yaml.safe_load(f) or {}

# Load metadata
metadata = {}
if os.path.isfile(metadata_path):
    with open(metadata_path) as f:
        metadata = yaml.safe_load(f) or {}

# Load teams
teams = {}
if os.path.isfile(teams_path):
    with open(teams_path) as f:
        teams = yaml.safe_load(f) or {}

# Load mandatory reads
mandatory_reads = ''
if os.path.isfile(context_path):
    with open(context_path) as f:
        mandatory_reads = f.read().strip()

# Resolve variables
project_id = identity.get('project_id', os.path.basename(root))
display_name = identity.get('display_name', project_id)
profile = metadata.get('profile', identity.get('profile', 'L0'))

# Team model
team_list = teams.get('teams', teams.get('team_assignments', []))
if isinstance(team_list, list):
    team_model = '\n'.join('- ' + str(t.get('team_id', '')) + ': ' + str(t.get('label', t.get('role', ''))) for t in team_list if isinstance(t, dict))
elif isinstance(team_list, dict):
    team_model = '\n'.join('- ' + k + ': ' + str(v) for k, v in team_list.items())
else:
    team_model = '(none defined)'

# Iron rules
iron_rules_data = teams.get('iron_rules', identity.get('iron_rules', []))
if isinstance(iron_rules_data, list):
    iron_rules = '\n'.join('- ' + str(r) for r in iron_rules_data)
else:
    iron_rules = str(iron_rules_data) if iron_rules_data else '(none defined)'

# Boundaries
boundaries = identity.get('boundaries', {})
if not isinstance(boundaries, dict):
    boundaries = {}
forbidden = boundaries.get('forbidden_patterns', [])
forbidden_str = ', '.join(str(p) for p in forbidden) if forbidden else '(none)'
allowed = boundaries.get('allowed_write_roots', [])
allowed_str = ', '.join(str(p) for p in allowed) if allowed else '(none)'

# Read template
with open('$TEMPLATE') as f:
    content = f.read()

# Replace
content = content.replace('{{PROJECT_ID}}', project_id)
content = content.replace('{{DISPLAY_NAME}}', display_name)
content = content.replace('{{PROFILE}}', str(profile))
content = content.replace('{{TEAM_MODEL}}', team_model)
content = content.replace('{{IRON_RULES}}', iron_rules)
content = content.replace('{{MANDATORY_READS}}', mandatory_reads or '(none)')
content = content.replace('{{FORBIDDEN_PATTERNS}}', forbidden_str)
content = content.replace('{{ALLOWED_WRITE_ROOTS}}', allowed_str)

print(content)
")

if [ -n "$OUTPUT" ]; then
  echo "$RENDERED" > "$OUTPUT"
  echo "Written to: $OUTPUT"
else
  echo "$RENDERED"
fi

# ─── MCP Profile: generate .cursor/mcp.json ────────────────────────────────
# SCRIPT_DIR = .../context-onboarding/scripts → parent/.. = lean-kit/modules/
LEAN_KIT_MODULES_PATH="$(dirname "$SCRIPT_DIR")/.."

generate_mcp_config() {
  local project_root="$1"
  local metadata_file="$project_root/_aos/metadata.yaml"

  local mcp_profile
  mcp_profile=$(python3 -c "
import yaml, sys
try:
    d = yaml.safe_load(open('${metadata_file}'))
    print(d.get('mcp_profile', 'none'))
except Exception:
    print('none')
" 2>/dev/null)

  if [[ "$mcp_profile" == "none" || -z "$mcp_profile" ]]; then
    echo "INFO: mcp_profile not set — skipping .cursor/mcp.json generation"
    return 0
  fi

  local template="${LEAN_KIT_MODULES_PATH}/mcp-browser/templates/mcp_json_${mcp_profile}.template"
  if [ ! -f "$template" ]; then
    echo "WARN: MCP template not found: $template" >&2
    return 1
  fi

  mkdir -p "$project_root/.cursor"
  cp "$template" "$project_root/.cursor/mcp.json"
  echo "INFO: Generated .cursor/mcp.json (mcp_profile=$mcp_profile)"
}

generate_mcp_config "${PROJECT_ROOT}"
# ────────────────────────────────────────────────────────────────────────────
