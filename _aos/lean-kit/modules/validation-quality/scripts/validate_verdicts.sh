#!/usr/bin/env bash
# validate_verdicts.sh — AOS Verdict File Validator
# Usage: ./validate_verdicts.sh [--team <team_id>] [--wp <wp_id>]
# Exit: 0=all PASS, 1=any FAIL
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/validate_verdicts.py" "$@"
