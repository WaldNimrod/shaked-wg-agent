#!/usr/bin/env bash
# validate_lod.sh — AOS LOD Document Validator
# Usage: ./validate_lod.sh [<wp-dir>|--all] [--lod <level>]
# Exit: 0=all PASS/SKIP, 1=any FAIL
# Requires: python3, PyYAML

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/validate_lod.py" "$@"
