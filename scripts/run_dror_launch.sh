#!/usr/bin/env bash
set -euo pipefail

PROFILE_ID="${1:-dror}"
UPLOAD_PATH="${DROR_UPLOAD_PATH:-wp-content/uploads/shaked-wg/dror}"

export UPRESS_UPLOAD_PATH="${UPLOAD_PATH}"

echo "Running scan for profile: ${PROFILE_ID}"
echo "Publishing report path: ${UPRESS_UPLOAD_PATH}/index.html"

PYTHON_BIN="python3"
if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
fi

"${PYTHON_BIN}" -m shaked_wg_agent run --profile "${PROFILE_ID}"

echo "Expected public URL:"
echo "https://www.nimrod.bio/${UPRESS_UPLOAD_PATH}/index.html"
