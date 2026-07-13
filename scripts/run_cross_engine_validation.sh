#!/usr/bin/env bash
# run_cross_engine_validation.sh — drive a cross-engine validator HEADLESS (no human paste).
#
# Thin wrapper over agents_os.modules.management.cross_engine_validation_cli (Iron Rule #13).
# Canon: methodology/AOS_CROSS_ENGINE_AUTONOMOUS_VALIDATION_v1.0.0.md
#
# Usage:
#   scripts/run_cross_engine_validation.sh <validator_team> <workspace> <mandate_path> [--dry-run]
#
# Hub: auto-detects via _aos/projects.yaml. Spoke: auto-detects a sibling agents-os/ under the
# standard AOS_V5 layout (…/AOS_V5/<spoke>, …/AOS_V5/agents-os); set AOS_HUB_ROOT to override
# (e.g. a non-standard layout) or when auto-detect can't find the hub.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$REPO_ROOT/_aos/projects.yaml" ]]; then
  HUB_ROOT="$REPO_ROOT"
elif [[ -n "${AOS_HUB_ROOT:-}" ]]; then
  HUB_ROOT="$AOS_HUB_ROOT"
elif [[ -f "$(dirname "$REPO_ROOT")/agents-os/_aos/projects.yaml" ]]; then
  # Spoke auto-detect (no env var needed in the common layout): every AOS_V5 project is a
  # sibling of the hub. Found by the drift report DRIFT-REPORT-CROSS-ENGINE-VALIDATION-TOOLING
  # (EyalAmit.co.il-2026 team_100, 2026-07-12) — AOS_HUB_ROOT was previously undocumented and
  # unset anywhere in the fleet, so a propagated copy of this script would still fail without it.
  HUB_ROOT="$(dirname "$REPO_ROOT")/agents-os"
else
  echo "ERROR: cannot resolve hub — set AOS_HUB_ROOT to the agents-os hub path (spoke invocation)" >&2
  exit 2
fi
export PYTHONPATH="${HUB_ROOT}${PYTHONPATH:+:$PYTHONPATH}"

exec python3 -m agents_os.modules.management.cross_engine_validation_cli "$@"
