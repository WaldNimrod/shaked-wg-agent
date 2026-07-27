#!/usr/bin/env bash
# validate_gates.sh — AOS Gate History Validator
# Usage: ./validate_gates.sh [--wp <wp_id>] [--roadmap <path>]
# Exit: 0=all PASS/SKIP, 1=any FAIL
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/validate_gates.py" "$@"
