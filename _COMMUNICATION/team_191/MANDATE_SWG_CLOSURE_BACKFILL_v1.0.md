---
id: MANDATE_SWG_CLOSURE_BACKFILL_v1.0
from: team_100 (Chief System Architect)
to: team_191 (Git, Archive & File Governance)
date: 2026-04-24
type: ARCHIVE_CLOSURE_BACKFILL
project: shaked-wg-agent (spoke)
status: OPEN
authority: ADR042_WP_CLOSURE_PROTOCOL_v1.0.0.md
---

# Archive Closure Backfill Mandate — shaked-wg-agent

Audit of 12 COMPLETE WPs: **3 CLEAN, 9 need action.**

---

## Cat A — LOD500_LOCKED, missing ARCHIVE_MANIFEST (6 WPs)

| WP ID |
|-------|
| S002-P001-WP002 |
| S002-P002-WP002 |
| S003-P003-WP001 |
| S003-P003-WP002 |
| S004-P002-WP001 |

Action: create `_archive/{WP_ID}/` if missing, write ARCHIVE_MANIFEST.md. DB already locked.

---

## Cat B — lod_status=LOD500, not LOD500_LOCKED (2 WPs)

| WP ID | lod_status | Archive dir |
|-------|-----------|------------|
| S001-P001-WP001 | LOD500 | exists |
| S001-P002-WP001 | LOD500 | exists |

Action: write ARCHIVE_MANIFEST.md + update DB to LOD500_LOCKED.

---

## Cat C — lod_status=LOD200 (legacy), no archive (2 WPs)

| WP ID | lod_status |
|-------|-----------|
| S002-OPS-WP001 | LOD200 |
| S002-RND-WP001 | LOD200 |

Action: create `_archive/{WP_ID}/`, write minimal manifest (closure_type: LEGACY_PARTIAL_LOD).
Flag for team_100 review. Do NOT update DB lod_status.

---

## Completion

Write report to: `_COMMUNICATION/team_191/REPORT_SWG_CLOSURE_BACKFILL_v1.0.md`

Working directory: /Users/nimrod/Documents/shaked-wg-agent/
