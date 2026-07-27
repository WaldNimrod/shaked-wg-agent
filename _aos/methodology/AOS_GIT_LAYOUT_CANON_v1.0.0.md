# AOS Git Layout Canon — v1.0.0

**Status:** Canonical · **Owner:** Team 100 · **Date:** 2026-06-07
**Origin:** AOS-V4.5-WP-GIT-HYGIENE (recurring hub `core.bare` re-baring + multi-session worktree loose-ends).
**Related:** ADR052 (Operating Environment & Session Model), ADR054 (Governance Distribution Model B), `methodology/AOS_OPERATING_ENVIRONMENT_v1.0.0.md`.

## 1. The supported layout (canonical)

AOS runs **SOLO / multi-session** (ADR052): one developer, several concurrent agent sessions. The canonical git layout is:

- A **normal working checkout** of `main` at the repo root (e.g. `/Users/nimrod/Documents/agents-os`).
  - `core.bare` **MUST be `false`** on this checkout. It has files on disk and a working tree.
- **Linked `feat/*` worktrees** for concurrent sessions, created with `git worktree add`, living under `.claude/worktrees/…` (or any path outside the main tree).
  - Each session works in its **own** worktree and **never touches `main` directly** (ADR052 program AOS-SESSION-MODEL W2 — worktree isolation).

This is a **"normal main + linked worktrees"** layout, not a bare-central-store layout.

## 2. Hard rules

1. **`core.bare=false` on every working checkout.** A working checkout that flips to `core.bare=true` silently breaks merges, `validate_aos.sh`, and governance bootstrap. This is the recurring fault that motivated this canon.
2. **No session, test, or script may flip `core.bare` on a shared working tree.** Tests doing git ops MUST isolate (their own `tmp` repo / `GIT_DIR`), never reconfigure the shared tree. If you ever find the hub bared, remediate immediately:
   ```
   git -C <repo> config core.bare false
   ```
   The defensive guard `scripts/aos_bare_guard.sh` (wired into `aos_session_ctl.sh register`) surfaces this at session start; `validate_aos.sh` Check 51 reports it advisory.
3. **Worktrees inherit config from the shared gitdir.** Hooks and config registered against the main gitdir (e.g. `merge.ours.driver`, `pull.rebase=false`, the AOS hooks) apply to all linked worktrees because they share `.git/hooks` and `.git/config`. Therefore: **run `scripts/install_hooks.sh` once per clone** (not per worktree) — it uses `git rev-parse --git-path hooks` so it resolves the shared hooks dir from inside any worktree.
4. **Prune stray worktrees.** Removed worktree directories leave admin entries; run `git worktree prune` (Check 51 / `scripts/session_reap.sh` flag this).

## 3. The bare+worktrees alternative — and when NOT to use it

A "bare central store + linked worktrees" layout (a bare `agents-os.git` with every branch as a worktree) is a legitimate git pattern. **AOS does NOT use it for the working checkouts**, because:

- It adds a moving part (a separate bare store) that the rest of AOS tooling (validate, bootstrap, session_ctl, hooks) does not assume.
- The recurring failure mode here was a *working* checkout becoming bare — the opposite of the intended layout. Formalizing a bare store would not have prevented that; a clear rule + guard does.

Use the bare+worktrees layout **only** if a future ADR explicitly relocates the store to `agents-os.git` and updates all tooling. Until then: **a working checkout is never bare.** A genuinely bare store (no working tree) legitimately has `core.bare=true` and is out of scope for the working-checkout rule.

## 4. Quick reference

| Item | Rule |
|------|------|
| `main` checkout | normal, `core.bare=false` |
| concurrent sessions | linked `git worktree` on `feat/*`, isolated |
| `core.bare` on working tree | always `false` — never flipped by tooling |
| hooks / merge driver | `scripts/install_hooks.sh` once per clone (shared gitdir) |
| bare central store | NOT used unless a future ADR adopts it |
| detection | `scripts/aos_bare_guard.sh` (session start) + `validate_aos.sh` Check 51 (advisory) |

— Team 100, Chief System Architect.
