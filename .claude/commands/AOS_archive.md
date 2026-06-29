---
summary: "Archive completed Work Package artifacts — move from _COMMUNICATION/ to _archive/ per Iron Rule #15."
category: project
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8092`); (3) `http://127.0.0.1:8092` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team).

Archive completed Work Package artifacts from `_COMMUNICATION/` to `_archive/`.

API endpoint: `POST {HUB_API_BASE}/api/artifacts/archive`  
(`HUB_API_BASE` defaults to `http://127.0.0.1:8092`; override via `AOS_API_BASE` env)

**Invocation:** `/AOS_archive [wp_id]`

## Phase 0 — Parse arguments

Accept: `wp_id` (e.g. `AOS-V322-WP-PROMPT-QUALITY-UPGRADE`).  
If missing, ask for it. Verify WP is COMPLETE in `_aos/roadmap.yaml` before proceeding.

## Phase 1 — Dry run preview

```
POST {HUB_API_BASE}/api/artifacts/archive
{"wp_id": "{wp_id}", "dry_run": true}
```

**If API unreachable:** STOP. Instruct user: `bash scripts/start_aos_api_local.sh`

Display move plan:
```
Files to archive for {wp_id} ({N} files):
  _COMMUNICATION/team_190/MANDATE_{WP_ID}_... → _archive/{WP_ID}/team_190/...
  _COMMUNICATION/team_50/VERDICT_{WP_ID}_...  → _archive/{WP_ID}/team_50/...
  ...
```

Confirm with user: "Archive {N} files? (y/n)"

## Phase 2 — Execute archive

```
POST {HUB_API_BASE}/api/artifacts/archive
{"wp_id": "{wp_id}", "dry_run": false}
```

## Phase 3 — Verify + report

Display `moved` list + any `errors`. Run validate_aos.sh to confirm no Check 15 regressions.  
Update `_aos/roadmap.yaml` WP entry if not already `lod_status: LOD500`.

## Phase 3b — Command shipping check (if WP shipped commands)

Check if this WP added or modified any `.claude/commands/AOS_*.md`:
```bash
git log --diff-filter=AM --name-only --format="" {first_wp_commit}..HEAD | grep "\.claude/commands/AOS_"
```
If **any command files changed** → run full checklist before closing:
`lean-kit/modules/project-governance/docs/WP_COMMAND_SHIPPING_CHECKLIST_v1.0.0.md`
Includes mandatory `git push` + MSG to team_99.

## Error Handling

- API 4xx → parse detail, present to user
- No files found → confirm with user before proceeding (may be already archived)
- git mv errors → display per-file errors; partial archive is recoverable
