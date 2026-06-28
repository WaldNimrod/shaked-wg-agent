---
summary: "Session register + worktree isolation — status, list, worktree, reap (ADR052 W2/W3)."
category: session
---

## AOS_session — session register + worktree isolation (thin orchestrator)

Delegates to `scripts/aos_session_ctl.sh`, `scripts/start_worktree.sh`, `scripts/hooks/session_preflight.sh`,
`scripts/session_reap.sh`. Mutations via hub API (Iron Rule #13 / ADR034).

**Invocation:** `/AOS_session [--worktree <wp>] [--status] [--list] [--reap] [--force] [--close]`

Env: `AOS_SESSION_ENV` (default `local-mac`). Exempt: `cowork`, `claude-design`, `web-research`, `home-server`.

## Phase 0 — Parse flags (default: `--status`)

| Flag | Action |
|------|--------|
| `--worktree <wp>` | pre-flight + worktree add |
| `--status` | register + heartbeat + `detect_concurrency(register)` JSON |
| `--list` | render register-view (LOD300 §5) |
| `--reap` | `session_reap.sh` (add `--confirm` after review) |
| `--force` | pass to pre-flight → `session_force.log` |
| `--close` | API close + optional lock cleanup |

## Phase 1 — Execute (repo root)

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
export AOS_SESSION_ID="${AOS_SESSION_ID:-$(bash scripts/aos_session_ctl.sh session-id)}"
CTL="bash scripts/aos_session_ctl.sh"
```

**Start (all actions except `--close`):** `$CTL register [wp]` then `$CTL heartbeat`

**`--status` / default:**
```bash
bash scripts/start_worktree.sh --json register
bash scripts/start_worktree.sh
```

**`--list`:** `$CTL list`

**`--worktree <wp>`:** `bash scripts/hooks/session_preflight.sh --wp "<wp>" ${FORCE_FLAG}` then worktree add per W2.

**`--reap`:** `bash scripts/session_reap.sh` (confirm: `--confirm`)

**`--close`:** `$CTL close [wp]` — W4: auto-captures a `completion` notice to the orchestrator inbox
**before** the API close (degrade-safe; LOD300 §4.2 / Finding 1). Set `AOS_COMPLETION_REF` to the
completion-report path for the inbox `body_ref`.

**Startup auto-read (W4 / Finding 5):** `$CTL register` ALSO runs `aos_inbox_check` so pending mail for
this session/team/env is surfaced at session start — no operator memory required.

## Phase 2 — Display

Show `detect_concurrency` fields: `state`, `evidence`, `recommended_worktree`, `backend`.

## Error Handling

- Not a git repo → STOP.
- API down → `detect_concurrency` degrades to `backend: interim` (F3, non-blocking).
- Do **not** wire `session_preflight.sh` into `install_hooks.sh` (W2 constraint).

## References

- `_aos/work_packages/AOS-V4.5-WP-SESSION-W3-DB-REGISTER/LOD400_BUILD_SPEC_v1.0.0.md`
- `methodology/AOS_OPERATING_ENVIRONMENT_v1.0.0.md` §3
