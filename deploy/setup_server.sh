#!/bin/bash
# setup_server.sh — Deploy shaked-wg-agent on waldhomeserver
# Run as: bash /tmp/setup_server.sh
set -euo pipefail

PROJECT_DIR="/data/projects/shaked-wg-agent"
REPO="https://github.com/WaldNimrod/shaked-wg-agent.git"
LOG_FILE="/data/projects/shaked-wg-agent/run.log"

echo "[1/6] Clone or update repo..."
if [ -d "$PROJECT_DIR/.git" ]; then
  git -C "$PROJECT_DIR" pull
else
  mkdir -p /data/projects
  git clone "$REPO" "$PROJECT_DIR"
fi

echo "[2/6] Create virtual environment..."
cd "$PROJECT_DIR"
python3 -m venv .venv
.venv/bin/pip install -q -e .

echo "[3/6] Create .env from SFA credentials..."
# Copy relevant upress vars from SFA .env (already on server)
SFA_ENV="/data/projects/smallfarmsagents/.env"
if [ -f "$SFA_ENV" ]; then
  grep -E "^UPRESS_SFTP_HOST|^UPRESS_SFTP_PORT|^UPRESS_SFTP_USER|^UPRESS_SFTP_PASS|^UPRESS_PUBLIC_BASE|^UPRESS_WP_REST_BASE|^UPRESS_WP_APP_USER|^UPRESS_WP_APP_PASS" "$SFA_ENV" > "$PROJECT_DIR/.env"
  echo "UPRESS_UPLOAD_PATH=wp-content/uploads/shaked-wg" >> "$PROJECT_DIR/.env"
  echo ".env created from SFA credentials"
else
  echo "WARNING: SFA .env not found at $SFA_ENV — .env must be created manually"
fi

echo "[4/6] Test installation..."
.venv/bin/python -m shaked_wg_agent status

echo "[5/6] Create log file..."
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

echo "[6/6] Add cron entries..."
# Remove any existing shaked-wg-agent cron entries, then add fresh
(crontab -l 2>/dev/null | grep -v "shaked-wg-agent"; \
 echo "# shaked-wg-agent — Basel WG scan (3x daily, project ends 2026-06-08)"; \
 echo "0 7,13,19 * * * $PROJECT_DIR/.venv/bin/python -m shaked_wg_agent run >> $LOG_FILE 2>&1") \
 | crontab -

echo ""
echo "=============================="
echo "✅ DEPLOY COMPLETE"
echo "   Project: $PROJECT_DIR"
echo "   Cron: 0 7,13,19 * * *"
echo "   Log: $LOG_FILE"
echo "   Test with: $PROJECT_DIR/.venv/bin/python -m shaked_wg_agent run"
echo "   Live URL: https://www.nimrod.bio/wp-content/uploads/shaked-wg/index.html"
echo "=============================="
