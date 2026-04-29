#!/usr/bin/env bash
# Merge uPress-related keys from SmallFarmsAgents .env into this repo's .env.
# Same FTP host/user as SFA; mezoohost password often lives as MEZOOHOST_PASS or UPRESS_MEZOO_PASS in SFA.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/.env"
SFA_CANDIDATES=(
  "${SMALLFARMSAGENTS_ROOT:-}/.env"
  "${HOME}/Documents/SmallFarmsAgents/.env"
  "${HOME}/projects/SmallFarmsAgents/.env"
  "/data/projects/smallfarmsagents/.env"
)

SFA_ENV=""
for p in "${SFA_CANDIDATES[@]}"; do
  if [[ -n "$p" && -f "$p" ]]; then
    SFA_ENV="$p"
    break
  fi
done

if [[ -z "$SFA_ENV" ]]; then
  echo "No SFA .env found. Tried:" >&2
  printf '  %s\n' "${SFA_CANDIDATES[@]}" >&2
  echo "Set SMALLFARMSAGENTS_ROOT to the SmallFarmsAgents repo path and re-run." >&2
  exit 1
fi

echo "Using SFA env: ${SFA_ENV}"

{
  echo "# Generated in part from SFA (${SFA_ENV}). Same uPress server; do not commit."
  grep -E "^UPRESS_SFTP_HOST|^UPRESS_SFTP_PORT|^UPRESS_WP_REST_BASE|^UPRESS_WP_APP_USER|^UPRESS_WP_APP_PASS" "$SFA_ENV" || true
  MEZOO_PASS=""
  MEZOO_PASS=$(grep -E "^MEZOOHOST_PASS=|^UPRESS_MEZOO_PASS=|^UPRESS_SFTP_PASS=" "$SFA_ENV" 2>/dev/null | head -1 | cut -d= -f2- || true)
  if [[ -z "${MEZOO_PASS// /}" ]]; then
    echo "WARNING: No MEZOOHOST_PASS / UPRESS_MEZOO_PASS / UPRESS_SFTP_PASS in SFA .env — set UPRESS_SFTP_PASS manually for mezoohost@nimrod.bio" >&2
  fi
  echo "UPRESS_SFTP_USER=mezoohost@nimrod.bio"
  echo "UPRESS_SFTP_PASS=${MEZOO_PASS:-}"
  echo "UPRESS_PUBLIC_BASE=https://www.nimrod.bio"
  echo "# Omit UPRESS_UPLOAD_PATH here so dror → wp-content/uploads/shaked-wg/dror, default → …/shaked-wg"
} > "${OUT}.tmp"

mv "${OUT}.tmp" "$OUT"
echo "Wrote ${OUT}"
echo "Review UPRESS_SFTP_PASS if empty; then: python -m shaked_wg_agent run --profile dror"
