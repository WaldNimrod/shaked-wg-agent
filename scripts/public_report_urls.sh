#!/usr/bin/env bash
# Echo canonical public report URLs (no FTPS — for bookmarks / QA).
# Upload path matches shaked_wg_agent.publisher.ftps_upload.resolve_upload_path
set -euo pipefail
BASE="${UPRESS_PUBLIC_BASE:-https://www.nimrod.bio}"
BASE="${BASE%/}"
echo "Shaked / Basel (profile default):"
echo "  ${BASE}/wp-content/uploads/shaked-wg/index.html"
echo "Dror (profile dror):"
echo "  ${BASE}/wp-content/uploads/shaked-wg/dror/index.html"
