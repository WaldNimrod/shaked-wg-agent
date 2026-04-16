#!/bin/bash
# prompt_staleness_check.sh — Detect stale mandate/routing prompts
# V316 Deliverable D3

set -uo pipefail

# Global variables
PROMPT_FILE=""
PROJECT_ROOT=""
SIDECAR_FILE=""
AUTO_REGENERATE=false
DRY_RUN=false

# usage() — print usage to stderr, exit 1
usage() {
    cat >&2 <<'EOF'
Usage: prompt_staleness_check.sh <prompt_file> [--auto-regenerate] [--dry-run]

Exit codes:
  0 = fresh (all state hashes match)
  1 = stale (one or more state files changed)
  2 = no sidecar (first-time check)

Options:
  --auto-regenerate  Print regeneration instruction if stale
  --dry-run          Do not create/modify sidecar file
EOF
    exit 1
}

# parse_args() — parse PROMPT_FILE, flags; derive PROJECT_ROOT; set SIDECAR_FILE
parse_args() {
    if [[ $# -lt 1 ]]; then
        usage
    fi

    PROMPT_FILE="$1"

    # Validate that PROMPT_FILE is a file
    if [[ ! -f "$PROMPT_FILE" ]]; then
        echo "Error: PROMPT_FILE '$PROMPT_FILE' does not exist or is not a file" >&2
        exit 1
    fi

    # Parse flags
    for arg in "${@:2}"; do
        case "$arg" in
            --auto-regenerate)
                AUTO_REGENERATE=true
                ;;
            --dry-run)
                DRY_RUN=true
                ;;
            *)
                echo "Error: Unknown option '$arg'" >&2
                usage
                ;;
        esac
    done

    # Derive PROJECT_ROOT by walking up from PROMPT_FILE directory (up to 5 levels)
    local dir
    dir="$(cd "$(dirname "$PROMPT_FILE")" && pwd)"
    local level=0

    while [[ $level -lt 5 ]]; do
        if [[ -d "${dir}/_aos" ]]; then
            PROJECT_ROOT="$dir"
            break
        fi
        dir="$(dirname "$dir")"
        ((level++))
    done

    # Fallback to pwd
    if [[ -z "$PROJECT_ROOT" ]]; then
        PROJECT_ROOT="$(pwd)"
    fi

    SIDECAR_FILE="${PROMPT_FILE}.prompt_state"
}

# compute_hash(file_path) — output hash or FILE_NOT_FOUND
compute_hash() {
    local file_path="$1"
    if [[ ! -f "$file_path" ]]; then
        echo "FILE_NOT_FOUND"
        return 0
    fi
    shasum -a 256 "$file_path" | awk '{print "sha256:" $1}'
}

# get_state_files() — echo 3 paths (one per line)
get_state_files() {
    echo "${PROJECT_ROOT}/_aos/roadmap.yaml"
    echo "${PROJECT_ROOT}/_aos/team_assignments.yaml"
    echo "${PROJECT_ROOT}/core/definition.yaml"
}

# create_sidecar(prompt_file) — extract WP/gate, compute hashes, write JSON
create_sidecar() {
    local prompt_file="$1"

    # Extract WP and GATE from YAML frontmatter using python3
    local wp gate
    wp=$(python3 << 'PYTHON_END'
import sys
import re

try:
    with open(sys.argv[1]) as f:
        content = f.read()

    # Look for YAML frontmatter (between --- markers)
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        fm = match.group(1)
        # Extract wp field
        wp_match = re.search(r'^wp:\s*(\S+)', fm, re.MULTILINE)
        if wp_match:
            print(wp_match.group(1), end='')
except Exception:
    pass
PYTHON_END
    )
    gate=$(python3 << 'PYTHON_END'
import sys
import re

try:
    with open(sys.argv[1]) as f:
        content = f.read()

    # Look for YAML frontmatter (between --- markers)
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        fm = match.group(1)
        # Extract gate field
        gate_match = re.search(r'^gate:\s*(\S+)', fm, re.MULTILINE)
        if gate_match:
            print(gate_match.group(1), end='')
except Exception:
    pass
PYTHON_END
    )

    # Default to empty if not found
    wp="${wp:-}"
    gate="${gate:-}"

    # Compute hashes for each state file
    local state_hashes_json=""
    local first=true
    while IFS= read -r state_file; do
        local hash
        hash=$(compute_hash "$state_file")
        local rel_path
        rel_path="${state_file#${PROJECT_ROOT}/}"

        if [[ "$first" = true ]]; then
            state_hashes_json="\"${rel_path}\": \"${hash}\""
            first=false
        else
            state_hashes_json="${state_hashes_json}, \"${rel_path}\": \"${hash}\""
        fi
    done < <(get_state_files)

    # Build JSON sidecar with python3
    python3 << PYTHON_END
import json
from datetime import datetime, timezone

sidecar = {
    "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    "wp": "${wp}",
    "gate": "${gate}",
    "state_hashes": {
        ${state_hashes_json}
    },
    "prompt_file": "${prompt_file}"
}

print(json.dumps(sidecar, indent=2))
PYTHON_END
}

# check_staleness(sidecar_file) — check hashes, report staleness
check_staleness() {
    local sidecar_file="$1"

    # If no sidecar, first-time check
    if [[ ! -f "$sidecar_file" ]]; then
        echo "[FIRST-TIME] No sidecar found. Generating baseline state record..."
        if [[ "$DRY_RUN" != true ]]; then
            create_sidecar "$PROMPT_FILE" > "$sidecar_file"
        fi
        exit 2
    fi

    # Parse sidecar JSON and compare hashes
    local stale_count=0
    local fresh_count=0
    local skip_count=0

    local state_hashes_json
    state_hashes_json=$(python3 << 'PYTHON_END'
import json
import sys

try:
    with open(sys.argv[1]) as f:
        sidecar = json.load(f)
    print(json.dumps(sidecar.get("state_hashes", {})))
except Exception as e:
    print("{}")
PYTHON_END
    "$sidecar_file")

    # Iterate through each state file and compare
    local file_index=0
    while IFS= read -r state_file; do
        local rel_path="${state_file#${PROJECT_ROOT}/}"
        local current_hash
        current_hash=$(compute_hash "$state_file")

        # Extract stored hash from sidecar
        local stored_hash
        stored_hash=$(python3 << PYTHON_END
import json
import sys

try:
    sidecar_json = '''${state_hashes_json}'''
    hashes = json.loads(sidecar_json)
    print(hashes.get("${rel_path}", ""), end='')
except Exception:
    print("", end='')
PYTHON_END
        )

        # Compare hashes
        if [[ "$stored_hash" == "" ]]; then
            echo "[SKIP] ${rel_path} (not in baseline)"
            ((skip_count++))
        elif [[ "$current_hash" == "$stored_hash" ]]; then
            echo "[FRESH] ${rel_path}"
            ((fresh_count++))
        else
            echo "[STALE] ${rel_path} (stored: ${stored_hash}, current: ${current_hash})"
            ((stale_count++))
        fi

        ((file_index++))
    done < <(get_state_files)

    # Summary line
    echo ""
    echo "Summary: ${fresh_count} fresh, ${stale_count} stale, ${skip_count} skipped"

    # If stale, print warning and optionally regen instruction
    if [[ $stale_count -gt 0 ]]; then
        echo ""
        echo "⚠️  STALENESS DETECTED: Prompt may reference outdated governance state."
        if [[ "$AUTO_REGENERATE" = true ]]; then
            echo ""
            echo "To regenerate this prompt, run:"
            echo "  # Regeneration instruction (implementation dependent)"
        fi
        exit 1
    fi

    # All fresh
    exit 0
}

# main() — orchestrate
main() {
    parse_args "$@"
    check_staleness "$SIDECAR_FILE"
}

main "$@"
