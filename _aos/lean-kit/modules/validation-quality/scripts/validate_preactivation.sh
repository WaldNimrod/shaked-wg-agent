#!/bin/bash
# validate_preactivation.sh — Pre-activation prerequisite validation
# V316 Deliverable D2

set -uo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# usage() — Print usage to stderr, exit 1
# ─────────────────────────────────────────────────────────────────────────────
usage() {
    cat >&2 <<'EOF'
Usage: validate_preactivation.sh <roadmap_yaml> <wp_id> <target_gate> [--force] [--dry-run]

Arguments:
  roadmap_yaml    Path to roadmap.yaml (must be a file)
  wp_id           Work package ID (e.g., "S001-P001-WP001")
  target_gate     Target gate for validation (e.g., "L-GATE_BUILD")
  --force         Override blocking failures (produces audit trail, exit 0)
  --dry-run       Display plan without executing validation

Exit codes:
  0 = All prerequisites met (or forced)
  1 = Blocking failure detected
  2 = Advisory warnings only (no blockers)
EOF
    exit 1
}

# ─────────────────────────────────────────────────────────────────────────────
# parse_args() — Parse arguments and derive paths
# ─────────────────────────────────────────────────────────────────────────────
parse_args() {
    if [[ $# -lt 3 ]]; then
        usage
    fi

    ROADMAP_YAML="$1"
    WP_ID="$2"
    TARGET_GATE="$3"
    FORCE=0
    DRY_RUN=0

    # Parse optional flags
    shift 3
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --force)
                FORCE=1
                ;;
            --dry-run)
                DRY_RUN=1
                ;;
            *)
                usage
                ;;
        esac
        shift
    done

    # Validate that roadmap_yaml is a file
    if [[ ! -f "$ROADMAP_YAML" ]]; then
        echo "ERROR: roadmap_yaml must be a file: $ROADMAP_YAML" >&2
        exit 1
    fi

    # Derive PROJECT_ROOT by stripping /_aos/roadmap.yaml
    if [[ "$ROADMAP_YAML" =~ ^(.*)/_aos/roadmap\.yaml$ ]]; then
        PROJECT_ROOT="${BASH_REMATCH[1]}"
    else
        echo "ERROR: roadmap_yaml path must match pattern */_aos/roadmap.yaml" >&2
        exit 1
    fi

    TEAM_ASSIGNMENTS="$PROJECT_ROOT/_aos/team_assignments.yaml"

    # Find ORDERING_SCHEMA
    if [[ -f "$PROJECT_ROOT/lean-kit/modules/validation-quality/schemas/pre_gate_ordering.yaml" ]]; then
        ORDERING_SCHEMA="$PROJECT_ROOT/lean-kit/modules/validation-quality/schemas/pre_gate_ordering.yaml"
    elif [[ -f "$PROJECT_ROOT/_aos/lean-kit/modules/validation-quality/schemas/pre_gate_ordering.yaml" ]]; then
        ORDERING_SCHEMA="$PROJECT_ROOT/_aos/lean-kit/modules/validation-quality/schemas/pre_gate_ordering.yaml"
    else
        echo "ERROR: pre_gate_ordering.yaml not found in expected locations" >&2
        exit 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# resolve_alias() — Resolve gate alias to canonical name
# ─────────────────────────────────────────────────────────────────────────────
resolve_alias() {
    local gate_name="$1"

    python3 << PYTHON_EOF
import sys
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed", file=sys.stderr)
    sys.exit(1)

schema_path = "$ORDERING_SCHEMA"
try:
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
except Exception as e:
    print(f"ERROR: Failed to load schema: {e}", file=sys.stderr)
    sys.exit(1)

aliases = schema.get('aliases', {})
gate_name = "$gate_name"
canonical = aliases.get(gate_name, gate_name)
print(canonical)
PYTHON_EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# detect_track() — Detect track from WP in roadmap
# ─────────────────────────────────────────────────────────────────────────────
detect_track() {
    local wp_id="$1"

    python3 << PYTHON_EOF
import sys
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed", file=sys.stderr)
    sys.exit(1)

roadmap_path = "$ROADMAP_YAML"
wp_id = "$wp_id"

try:
    with open(roadmap_path) as f:
        roadmap = yaml.safe_load(f)
except Exception as e:
    print(f"ERROR: Failed to load roadmap: {e}", file=sys.stderr)
    sys.exit(1)

work_packages = roadmap.get('work_packages', [])
for wp in work_packages:
    if wp.get('id') == wp_id:
        track = wp.get('track')
        if track == 'A':
            print('L0_TRACK_A')
            sys.exit(0)
        elif track == 'B':
            print('L0_TRACK_B')
            sys.exit(0)
        elif track == 'L2':
            print('L2')
            sys.exit(0)
        elif track == 'L2.5':
            print('L2_5')
            sys.exit(0)
        else:
            print(f'ERROR: Unknown track: {track}', file=sys.stderr)
            sys.exit(1)

print(f'ERROR: Work package not found: {wp_id}', file=sys.stderr)
sys.exit(1)
PYTHON_EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# check_prerequisites() — Core validation logic (python3 heredoc)
# ─────────────────────────────────────────────────────────────────────────────
check_prerequisites() {
    local roadmap_path="$1"
    local wp_id="$2"
    local target_gate="$3"
    local track="$4"
    local schema_path="$5"
    local team_assignments_path="$6"

    python3 << PYTHON_EOF
import sys
import re
from datetime import datetime

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed", file=sys.stderr)
    sys.exit(1)

roadmap_path = "$roadmap_path"
wp_id = "$wp_id"
target_gate = "$target_gate"
track = "$track"
schema_path = "$schema_path"
team_assignments_path = "$team_assignments_path"

# Load YAML files
try:
    with open(roadmap_path) as f:
        roadmap = yaml.safe_load(f)
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
    with open(team_assignments_path) as f:
        team_assignments = yaml.safe_load(f)
except Exception as e:
    print(f"ERROR: Failed to load YAML files: {e}", file=sys.stderr)
    sys.exit(1)

# Extract aliases for normalization
aliases = schema.get('aliases', {})

def normalize_gate(gate_name):
    """Normalize gate name using aliases"""
    return aliases.get(gate_name, gate_name)

# Find the work package
work_packages = roadmap.get('work_packages', [])
wp = None
for w in work_packages:
    if w.get('id') == wp_id:
        wp = w
        break

if not wp:
    print(f"[FAIL] Work package not found: {wp_id}")
    sys.exit(1)

# Get gate history
gate_history = wp.get('gate_history', [])
gate_history_normalized = {}
for entry in gate_history:
    gate_name = normalize_gate(entry.get('gate', ''))
    result = entry.get('result', '')
    date = entry.get('date', '')
    gate_history_normalized[gate_name] = {'result': result, 'date': date}

# Get schema for track
track_schema = schema.get('tracks', {}).get(track)
if not track_schema:
    print(f"[FAIL] Track not found in schema: {track}")
    sys.exit(1)

# Find target gate in sequence
target_gate_entry = None
for gate_entry in track_schema.get('sequence', []):
    if normalize_gate(gate_entry.get('gate')) == normalize_gate(target_gate):
        target_gate_entry = gate_entry
        break

if not target_gate_entry:
    print(f"[FAIL] Target gate not found in track {track}: {target_gate}")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 1: Prerequisites
# ─────────────────────────────────────────────────────────────────────────────
check1_pass = True
prerequisites = target_gate_entry.get('prerequisites', [])

for prereq_gate in prerequisites:
    prereq_normalized = normalize_gate(prereq_gate)
    if prereq_normalized in gate_history_normalized:
        result = gate_history_normalized[prereq_normalized].get('result', '')
        date = gate_history_normalized[prereq_normalized].get('date', '')
        if result in ['PASS', 'PASS_WITH_FINDINGS', 'CLEAR', 'APPROVED']:
            print(f"[PASS] Prior gate {prereq_normalized}: {result} ({date})")
        else:
            print(f"[FAIL] Prior gate {prereq_normalized}: {result} (expected PASS/PASS_WITH_FINDINGS/CLEAR/APPROVED)")
            check1_pass = False
    else:
        print(f"[FAIL] Prior gate not found in history: {prereq_normalized}")
        check1_pass = False

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 2: LOD level
# ─────────────────────────────────────────────────────────────────────────────
check2_pass = True
lod_required = target_gate_entry.get('lod_required')
lod_status = wp.get('lod_status', '')

if lod_required:
    # Extract numeric LOD from lod_status using regex r'LOD(\d+)'
    lod_match = re.search(r'LOD(\d+)', lod_status)
    if lod_match:
        lod_current = int(lod_match.group(1))
    else:
        print(f"[FAIL] LOD status malformed: {lod_status} (expected LODnnn format)")
        check2_pass = False
        lod_current = None

    if lod_current is not None:
        # Extract required LOD number
        lod_req_match = re.search(r'LOD(\d+)', lod_required)
        if lod_req_match:
            lod_req = int(lod_req_match.group(1))
            if lod_current >= lod_req:
                print(f"[PASS] LOD status: LOD{lod_current} (required: {lod_required})")
            else:
                print(f"[FAIL] LOD status: LOD{lod_current} (required: {lod_required})")
                check2_pass = False
        else:
            print(f"[FAIL] Required LOD malformed: {lod_required}")
            check2_pass = False
else:
    print(f"[PASS] LOD status: {lod_status} (no requirement for this gate)")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 3: Team assignments (advisory)
# ─────────────────────────────────────────────────────────────────────────────
check3_pass = True
teams = team_assignments.get('teams', [])
has_validator = any(t.get('role_type') in ['validator_agent', 'qa_agent'] for t in teams)
has_qa = any(t.get('role_type') == 'qa_agent' for t in teams)

if has_validator or has_qa:
    print(f"[PASS] Team assignments: validator/QA team found")
else:
    print(f"[WARN] Team assignments: no validator/QA team found")
    check3_pass = False

# ─────────────────────────────────────────────────────────────────────────────
# Summary and exit code
# ─────────────────────────────────────────────────────────────────────────────
print("─────────────────────────────────────────────────────────────")

if check1_pass and check2_pass and check3_pass:
    print("PREACTIVATION: CLEAR (all checks passed)")
    sys.exit(0)
elif (check1_pass and check2_pass) and not check3_pass:
    print("PREACTIVATION: WARNING (1 WARN, 2 PASS)")
    sys.exit(2)
else:
    print("PREACTIVATION: BLOCKED (prerequisites not satisfied)")
    sys.exit(1)

PYTHON_EOF
    local python_exit=$?
    return $python_exit
}

# ─────────────────────────────────────────────────────────────────────────────
# main() — Main function orchestrating the validation flow
# ─────────────────────────────────────────────────────────────────────────────
main() {
    parse_args "$@"

    # Resolve alias
    RESOLVED_GATE=$(resolve_alias "$TARGET_GATE")
    if [[ $? -ne 0 ]]; then
        echo "ERROR: Failed to resolve gate alias" >&2
        exit 1
    fi

    # Detect track
    TRACK=$(detect_track "$WP_ID")
    if [[ $? -ne 0 ]]; then
        echo "ERROR: Failed to detect track for WP: $WP_ID" >&2
        exit 1
    fi

    # Print header
    echo "Validating prerequisites for: $WP_ID → $RESOLVED_GATE (track: $TRACK)"

    # Dry-run check
    if [[ $DRY_RUN -eq 1 ]]; then
        echo "[DRY-RUN] Not executing validation checks"
        return 0
    fi

    # Run check_prerequisites
    check_prerequisites \
        "$ROADMAP_YAML" \
        "$WP_ID" \
        "$RESOLVED_GATE" \
        "$TRACK" \
        "$ORDERING_SCHEMA" \
        "$TEAM_ASSIGNMENTS"

    local result=$?

    # Handle --force override
    if [[ $result -eq 1 && $FORCE -eq 1 ]]; then
        echo "[FORCED] Blocking failures overridden by --force flag"
        echo "[FORCED] Actor: $USER at $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        echo "[FORCED] Audit: prerequisites were NOT satisfied — proceeding under override"
        return 0
    fi

    return $result
}

# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
main "$@"
exit $?
