---
summary: "Unified AOS environment sync — propagate all hub governance (team contracts + lean-kit + methodology + directives) to all active spokes, both locally and in git."
category: governance
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8090`); (3) `http://127.0.0.1:8090` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team).

# /AOS_gov-sync — Unified AOS Environment Sync

**Authority:** `team_00` or `team_100` ONLY (ADR040 / Iron Rule #12).
**Single canonical command** for all AOS propagation. No separate path for lean-kit, methodology, or partial sync.

**Parameters:** `[--scope=full|teams] [--dry-run] [--push] [--no-push] [--spoke=<id>]`

| `--scope=full` (default) | `--scope=teams` |
|--------------------------|-----------------|
| team_*.md + ADRs + methodology + lean-kit + CLAUDE.md + COWORK_CONTEXT | team_*.md only (fast) |

## Phase 0 — Authority check

Identify caller. If not `team_00` or `team_100` → reject with ADR040 block. Stop.

## Phase 0.5 — Pre-check + Delta Display (automatic)

`aos_sync_all.sh` reads `_aos/last_gov_sync.yaml` from each spoke and displays:
- Hub SHA, changed file counts by category (governance / lean-kit / commands / methodology)
- Per-spoke status: `✓ up-to-date` / `⟳ <last> → <hub>` / `○ never synced`

This runs before Step 1 — purely informational, no gate. After each spoke commit, the script writes `_aos/last_gov_sync.yaml` with `hub_sha`, `sync_ts`, `scope`, `synced_by` to bootstrap future delta displays.

## Phase 1 — Parse + confirm

State: `scope / dry-run / target spokes / push intent`. Ask user to confirm before proceeding.

## Phase 2 — Execute sync

**Path A — API online:**
```
POST {AOS_API_BASE}/api/governance/sync
X-Actor-Team-Id: {actor_team_id}
{"scope": "full|teams", "dry_run": true|false, "spoke_filter": "all|<id>"}
```

**Path B — API offline (do NOT stop — fallback is mandatory):**

`scope=full`:
```bash
AOS_ACTOR_TEAM_ID={actor} bash scripts/aos_sync_all.sh --all [--dry-run]
```
`scope=teams`:
```bash
AOS_ACTOR_TEAM_ID={actor} bash lean-kit/modules/project-governance/scripts/propagate_governance.sh --all [--dry-run]
```

Display script stdout summary. Nonzero exit → flag failure, continue to Phase 3.

## Phase 3 — Hub self-validation

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Report `RESULT: N PASS / M FAIL`. If any FAIL → list them. Do not proceed to Phase 4 until 0 FAIL.

## Phase 4 — Git push

If `--no-push` → skip. If `--push` → push without extra prompt.

If neither flag, ask once: "Push propagated commits to git remotes for all synced spokes?"

On yes:
```bash
git -C {spoke_path} push origin HEAD  # per spoke with remote
```

Report per spoke: ✓ pushed / ✗ failed. Hub commit + push is the caller's responsibility.

## Phase 5 — Command surface check

```bash
git diff HEAD --name-only | grep "\.claude/commands/AOS_"
```

If any command file changed → run `lean-kit/modules/project-governance/docs/WP_COMMAND_SHIPPING_CHECKLIST_v1.0.0.md`.

## Error Handling

| Condition | Action |
|-----------|--------|
| API offline | Fallback Path B — do NOT stop |
| 403 from API | File GCR; actor not authorized |
| Script exit nonzero | Log; continue to validation |
| Spoke path missing | Skip spoke; warn; continue |
| git push fails | Log per spoke; report at end |

> `/AOS_gov-update` is deprecated (2026-05-23) — it was a narrow alias for `scope=full` with no offline fallback. Use this command instead.
