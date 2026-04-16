#!/bin/bash
# advance_stage.sh -- Safe stage transition for roadmap.yaml WPs
# Part of AOS lean-kit validation-quality module
#
# USAGE: advance_stage.sh <roadmap_yaml> <wp_id> <target_gate> <actor> [--verdict-ref PATH] [--dry-run]
#
# EXIT CODES:
#   0  Transition successful (or dry-run valid)
#   1  Invalid transition (prerequisite check failed)
#   2  Lock contention or invalid arguments
#
# DEPENDENCIES: python3 + PyYAML (for YAML parsing), flock (optional, mkdir fallback)
set -euo pipefail

# --- Dependency check ---
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required but not found" >&2
  exit 2
fi
if ! python3 -c "import yaml" 2>/dev/null; then
  echo "Error: PyYAML is required. Install via: pip3 install pyyaml" >&2
  exit 2
fi

# --- Gate Alias Normalization (§0.1) ---
normalize_gate() {
  case "$1" in
    L-GATE_E) echo "L-GATE_ELIGIBILITY" ;;
    L-GATE_C) echo "L-GATE_CONCEPT" ;;
    L-GATE_S) echo "L-GATE_SPEC" ;;
    L-GATE_B) echo "L-GATE_BUILD" ;;
    L-GATE_V) echo "L-GATE_VALIDATE" ;;
    *) echo "$1" ;;
  esac
}

# --- File Locking ---
# Uses flock if available; falls back to mkdir-based atomic lock
acquire_lock() {
  LOCK_FILE="${1}.lock"
  if command -v flock >/dev/null 2>&1; then
    exec 9>"$LOCK_FILE"
    if ! flock -n 9; then
      echo "Error: Could not acquire lock on $1 (another process is writing)" >&2
      exit 2
    fi
  else
    # POSIX fallback: mkdir is atomic
    if ! mkdir "$LOCK_FILE" 2>/dev/null; then
      echo "Error: Could not acquire lock on $1 (another process is writing)" >&2
      exit 2
    fi
    trap "rmdir '$LOCK_FILE' 2>/dev/null" EXIT
  fi
}

release_lock() {
  LOCK_FILE="${1}.lock"
  if command -v flock >/dev/null 2>&1; then
    flock -u 9 2>/dev/null || true
  else
    rmdir "$LOCK_FILE" 2>/dev/null || true
  fi
}

# --- Gate Ordering Lookups ---
# Gate sequence lookup — returns space-separated canonical gate IDs for a track
get_gate_sequence() {
  local track="$1"
  case "$track" in
    A|L0_TRACK_A) echo "L-GATE_ELIGIBILITY L-GATE_SPEC L-GATE_BUILD L-GATE_VALIDATE" ;;
    B|L0_TRACK_B) echo "L-GATE_ELIGIBILITY L-GATE_CONCEPT L-GATE_SPEC L-GATE_BUILD L-GATE_VALIDATE" ;;
    *) echo "Error: Unknown track: $track" >&2; exit 1 ;;
  esac
}

# LOD requirement lookup — returns minimum LOD level number for a target gate
get_required_lod() {
  case "$1" in
    L-GATE_ELIGIBILITY) echo "100" ;;
    L-GATE_CONCEPT)     echo "200" ;;
    L-GATE_SPEC)        echo "400" ;;
    L-GATE_BUILD)       echo "400" ;;
    L-GATE_VALIDATE)    echo "500" ;;
    *) echo "Error: Unknown gate: $1" >&2; exit 1 ;;
  esac
}

# --- Python Helper Functions ---
# Python helper: extract WP fields from roadmap.yaml
read_wp_field() {
  local roadmap="$1" wp_id="$2" field="$3"
  python3 -c "
import yaml, sys
with open('$roadmap') as f:
    data = yaml.safe_load(f)
for wp in data.get('work_packages', []):
    if wp.get('id') == '$wp_id':
        print(wp.get('$field', ''))
        sys.exit(0)
sys.exit(1)
" 2>/dev/null
}

# Python helper: get last gate_history result for a specific gate
read_gate_result() {
  local roadmap="$1" wp_id="$2" gate="$3"
  python3 -c "
import yaml, sys
with open('$roadmap') as f:
    data = yaml.safe_load(f)
for wp in data.get('work_packages', []):
    if wp.get('id') == '$wp_id':
        results = [e.get('result','') for e in wp.get('gate_history',[]) if e.get('gate') == '$gate']
        if results:
            print(results[-1])
            sys.exit(0)
sys.exit(1)
" 2>/dev/null
}

# --- Usage function ---
usage() {
  cat >&2 <<EOF
Usage: advance_stage.sh <roadmap_yaml> <wp_id> <target_gate> <actor> [--verdict-ref PATH] [--dry-run]

Arguments:
  <roadmap_yaml>  Path to roadmap.yaml file
  <wp_id>         Work package ID (e.g., AOS-V316-WP-PIPELINE-HARDENING)
  <target_gate>   Target gate: L-GATE_E, L-GATE_C, L-GATE_S, L-GATE_B, L-GATE_V (or canonical forms)
  <actor>         Actor name/ID performing the transition

Options:
  --verdict-ref PATH  Optional path to verdict reference file
  --dry-run           Validate without writing changes

Exit Codes:
  0   Transition successful (or dry-run valid)
  1   Invalid transition (prerequisite check failed)
  2   Lock contention or invalid arguments
EOF
}

# --- Main Validation and Advance Function ---
validate_and_advance() {
  local ROADMAP="$1"
  local WP_ID="$2"
  local TARGET_GATE="$3"
  local ACTOR="$4"
  local VERDICT_REF="$5"
  local DRY_RUN="$6"

  # Step 1: Find WP and extract fields
  TRACK=$(read_wp_field "$ROADMAP" "$WP_ID" "track") || {
    echo "[FAIL] WP not found: $WP_ID" >&2; exit 1;
  }
  CURRENT_GATE_RAW=$(read_wp_field "$ROADMAP" "$WP_ID" "current_lean_gate")
  CURRENT_GATE=$(normalize_gate "$CURRENT_GATE_RAW")
  LOD_STATUS=$(read_wp_field "$ROADMAP" "$WP_ID" "lod_status")

  echo "Validating transition for $WP_ID"

  # Step 2: Validate target gate is next in sequence
  # Normalize target gate (accepts both short aliases and canonical forms)
  TARGET_GATE=$(normalize_gate "$TARGET_GATE")

  # Get gate sequence for track
  GATE_SEQ=$(get_gate_sequence "$TRACK")  # returns space-separated list
  # Find current gate position
  CURRENT_POS=$(echo "$GATE_SEQ" | tr ' ' '\n' | grep -n "^${CURRENT_GATE}$" | cut -d: -f1)
  # Find target gate position
  TARGET_POS=$(echo "$GATE_SEQ" | tr ' ' '\n' | grep -n "^${TARGET_GATE}$" | cut -d: -f1)

  if [ -z "$TARGET_POS" ]; then
    echo "[FAIL] Target gate $TARGET_GATE is not valid for track $TRACK" >&2
    exit 1
  fi
  EXPECTED_POS=$((CURRENT_POS + 1))
  if [ "$TARGET_POS" -ne "$EXPECTED_POS" ]; then
    echo "[FAIL] Cannot skip gates: current=$CURRENT_GATE (pos $CURRENT_POS), target=$TARGET_GATE (pos $TARGET_POS), expected pos=$EXPECTED_POS" >&2
    exit 1
  fi
  echo "[PASS] Target gate: $TARGET_GATE -- valid next in $TRACK"

  # Step 3: Verify current gate has PASS verdict
  # Check gate_history for current gate with result: PASS or PASS_WITH_FINDINGS
  # Note: roadmap.yaml gate_history uses short aliases (L-GATE_E, L-GATE_S, etc.)
  # We check both the canonical form and the short alias
  GATE_RESULT=$(read_gate_result "$ROADMAP" "$WP_ID" "$CURRENT_GATE_RAW")
  if [ -z "$GATE_RESULT" ]; then
    # Try canonical form in case gate_history uses canonical
    GATE_RESULT=$(read_gate_result "$ROADMAP" "$WP_ID" "$CURRENT_GATE")
  fi
  if [ "$GATE_RESULT" != "PASS" ] && [ "$GATE_RESULT" != "PASS_WITH_FINDINGS" ]; then
    echo "[FAIL] Current gate $CURRENT_GATE has no PASS verdict (result: ${GATE_RESULT:-null})" >&2
    exit 1
  fi
  echo "[PASS] Current gate: $CURRENT_GATE -- result: $GATE_RESULT"

  # Step 4: Check LOD status meets target gate requirements
  # LOD requirements per gate (see get_required_lod function):
  # L-GATE_ELIGIBILITY: 100, L-GATE_CONCEPT: 200, L-GATE_SPEC: 400,
  # L-GATE_BUILD: 400, L-GATE_VALIDATE: 500
  LOD_NUM=$(echo "$LOD_STATUS" | sed 's/LOD\([0-9]*\).*/\1/')
  REQUIRED_NUM=$(get_required_lod "$TARGET_GATE")
  if [ "$LOD_NUM" -lt "$REQUIRED_NUM" ]; then
    echo "[FAIL] LOD status $LOD_STATUS does not meet requirement LOD${REQUIRED_NUM} for $TARGET_GATE" >&2
    exit 1
  fi
  echo "[PASS] LOD status: $LOD_STATUS -- meets requirement LOD${REQUIRED_NUM}"

  # Step 5: Advisory check on verdict_ref
  if [ -n "$VERDICT_REF" ] && [ ! -f "$VERDICT_REF" ]; then
    echo "[WARN] Verdict ref file not found: $VERDICT_REF (advisory)"
  fi

  # Step 6: Handle dry-run or proceed with write
  if [ "$DRY_RUN" = true ]; then
    echo "-------------------------------------"
    echo "DRY RUN: $CURRENT_GATE -> $TARGET_GATE (would advance)"
    exit 0
  fi

  # Acquire file lock (uses flock or mkdir fallback)
  acquire_lock "$ROADMAP"

  TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

  # Update roadmap.yaml using python3+PyYAML
  # Writes the short-form gate alias back to roadmap.yaml to maintain consistency
  # with existing gate_history entries (roadmap.yaml convention is short forms)
  python3 -c "
import yaml, sys

with open('$ROADMAP') as f:
    data = yaml.safe_load(f)

# Reverse map: canonical -> short alias for roadmap.yaml consistency
REVERSE = {
    'L-GATE_ELIGIBILITY': 'L-GATE_E',
    'L-GATE_CONCEPT': 'L-GATE_C',
    'L-GATE_SPEC': 'L-GATE_S',
    'L-GATE_BUILD': 'L-GATE_B',
    'L-GATE_VALIDATE': 'L-GATE_V',
}
target_short = REVERSE.get('$TARGET_GATE', '$TARGET_GATE')

for wp in data.get('work_packages', []):
    if wp.get('id') == '$WP_ID':
        wp['current_lean_gate'] = target_short
        if 'gate_history' not in wp:
            wp['gate_history'] = []
        wp['gate_history'].append({
            'gate': target_short,
            'result': 'PENDING',
            'date': '$TIMESTAMP',
            'actor': '$ACTOR',
        })
        break

with open('$ROADMAP', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
"

  # Append audit trail
  AUDIT_FILE=$(dirname "$ROADMAP")/audit/stage_transitions.log
  mkdir -p "$(dirname "$AUDIT_FILE")"
  echo "$TIMESTAMP | $WP_ID | $CURRENT_GATE -> $TARGET_GATE | actor:$ACTOR | verdict_ref:${VERDICT_REF:-none}" >> "$AUDIT_FILE"

  # Release lock
  release_lock "$ROADMAP"

  echo "-------------------------------------"
  echo "ADVANCE: $CURRENT_GATE -> $TARGET_GATE"
  echo "Audit: appended to $AUDIT_FILE"
}

# --- Main Entry Point ---
main() {
  if [ $# -lt 4 ]; then usage; exit 2; fi

  ROADMAP="$1"
  WP_ID="$2"
  TARGET_GATE="$3"
  ACTOR="$4"
  VERDICT_REF=""
  DRY_RUN=false

  shift 4
  while [ $# -gt 0 ]; do
    case "$1" in
      --verdict-ref) VERDICT_REF="$2"; shift 2 ;;
      --dry-run) DRY_RUN=true; shift ;;
      *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
  done

  if [ ! -f "$ROADMAP" ]; then
    echo "Error: File not found: $ROADMAP" >&2
    exit 2
  fi

  validate_and_advance "$ROADMAP" "$WP_ID" "$TARGET_GATE" "$ACTOR" "$VERDICT_REF" "$DRY_RUN"
}

main "$@"
