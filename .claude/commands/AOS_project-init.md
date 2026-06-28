---
summary: "Guide the creation of a complete new AOS project — never miss a required file again."
category: project
---

Guide the creation of a complete new AOS project — never miss a required file again.

Reference: `lean-kit/modules/project-governance/GETTING_STARTED.md`
Templates: `lean-kit/modules/project-governance/config_templates/`

## Phase 0 — Collect Inputs

Collect and confirm: `project_id` (lowercase), `display_name`, `profile` (L0/L2/L2.5), `local_path` (absolute), `domain`, `owner_name`, `source_root` (L2 only), `active_teams`.

## Phase 1 — Create Skeleton via API

```bash
# dry run — review planned_files
curl -s -X POST "${AOS_V3_PUBLIC_API_BASE:-http://localhost:8090}/api/projects/create" \
  -H "Content-Type: application/json" -H "X-Actor-Team-Id: team_00" \
  -d '{"project_id":"[project_id]","profile":"[profile]","path":"[local_path]","dry_run":true}'
# execute
curl -s -X POST "${AOS_V3_PUBLIC_API_BASE:-http://localhost:8090}/api/projects/create" \
  -H "Content-Type: application/json" -H "X-Actor-Team-Id: team_00" \
  -d '{"project_id":"[project_id]","profile":"[profile]","path":"[local_path]"}'
```

## Phase 2 — Copy Lean Kit (physical snapshot — NEVER symlink)

```bash
HUB=/Users/nimrod/Documents/agents-os
cp -r "$HUB/lean-kit/modules/" "[local_path]/_aos/lean-kit/modules/"
cp "$HUB/lean-kit/"{MODULE_INDEX.md,LEAN_KIT_VERSION.md,PROFILE_SELECTION_GUIDE.md,VERSION_POLICY.md} "[local_path]/_aos/lean-kit/"
```

## Phase 3 — Governance Propagation

```bash
cd /Users/nimrod/Documents/agents-os
bash lean-kit/modules/project-governance/scripts/propagate_governance.sh \
  /Users/nimrod/Documents/agents-os [local_path]
```

Verify `[local_path]/_aos/governance/` contains one `team_*.md` per active team.

## Phase 4 — Validate (gate — do NOT declare done until this passes)

```bash
bash [local_path]/_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh [local_path]
```

Expected: **0 FAIL** (hub: 29 PASS / 2 SKIP; spoke count varies by profile). Fix failures, re-run, repeat until clean.

## Phase 5 — Register Project in Hub

Add to hub `_aos/projects.yaml`:
```yaml
- id: [project_id]
  name: "[display_name]"
  type: spoke
  local_path: "[local_path]"
  profile: [profile]
  enabled: true
```

## Phase 6 — Summary

Report `created_count` / `skipped_count` from Phase 1, validation result, then next steps:
1. `git init [local_path] && git add . && git commit -m "init: [project_id] AOS project setup"`
2. Fill in `_aos/MILESTONE_MAP.md` and `_aos/roadmap.yaml`
3. Run `/AOS_domain-health` to confirm new project appears in the network audit

## Error Handling

| Error | Action |
|---|---|
| API non-200 | Show error body; verify API server on port 8090 |
| Hub lean-kit not found | STOP — ask user for correct hub path |
| Builder = validator engine | STOP — cross-engine rule violation |
| `validate_aos.sh` fails | Do NOT declare done — fix and re-run |
