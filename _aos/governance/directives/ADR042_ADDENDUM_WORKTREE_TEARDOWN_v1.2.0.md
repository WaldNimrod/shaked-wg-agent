---
id: ADR042_ADDENDUM_WORKTREE_TEARDOWN
title: "ADR042 WP Closure Protocol — Addendum: Step 5 worktree teardown (terminal, best-effort)"
status: LOCKED
version: v1.2.0
date: 2026-07-22
authors: [team_100]
cosigned: [team_00]   # co-signed 2026-07-22 (team_00 session decision — recorded in AOS_STRATEGY_TWO_HORIZONS_2026-07-22.md; merge-with-deferred-Tier-2 ruling same date)
scope: AOS-hub
extends: ADR042 v1.0.0 [immutable]
supersedes: none   # ADDS Step 5 to the Mandatory Closure Sequence; changes no existing step
relates_to: ADR042_ADDENDUM_TEAM191_DISSOLUTION v1.1.0 (both additive addenda to the immutable ADR042 v1.0.0)
wp: AOS-V5-WP-WORKTREE-LIFECYCLE (D1)
---

# ADR042 — Addendum v1.2.0: Step 5 — worktree teardown (terminal, best-effort)

## Why this addendum

`ADR042_WP_CLOSURE_PROTOCOL_v1.0.0.md` (LOCKED, 2026-04-19) defines the Mandatory Closure Sequence that
runs after L-GATE_VALIDATE PASS — archive, DB state transition, propagation, command shipping — and
`LOD500_LOCKED` as the terminal WP state. It says nothing about the **worktree** a WP was built in. AOS has
mature worktree *creation/isolation* (`start_worktree.sh`, `aos_session_ctl.sh register`,
`aos_worktree_guard.sh`, Iron Rule #17) but **no canonical teardown**: after a WP's branch merges on GitHub,
its worktree + local branch linger indefinitely. That residue accumulates stale worktrees and branches that
later confuse reapers and `feat/v4`-style base heuristics.

This addendum **ADDS** a **Step 5 — worktree teardown** to the Mandatory Closure Sequence: a strictly-terminal,
best-effort, idempotent/skippable cleanup that runs after the four existing steps. It is **NOT a gate** — it
never fails closure. The safe removability predicate and the `session_reap.sh --wp-id` closer entrypoint it
invokes are built by team_60 under `AOS-V5-WP-WORKTREE-LIFECYCLE` D2–D4; this addendum is the D1 *discipline*
that names **when** and **how** the closer calls them.

This addendum does **not** introduce a merge hook — that is technically impossible (the merge lands on GitHub
via `gh pr merge`; there is no `post-fetch` hook, and `post-merge` fires only on `git pull` with no
merged-branch identity). The only viable trigger is the closer-step poll defined below.

## Step 5 — worktree teardown (the new terminal step)

**Placement.** Step 5 is **strictly terminal** — it runs only AFTER Steps 1–4 of the Mandatory Closure
Sequence (archive → DB state transition → propagation → command shipping) have completed. It is **idempotent
and skippable**: WPs with no dedicated worktree (EXPRESS / OPS / RESEARCH, and hub-native file-canonical WPs
built in the primary checkout) no-op cleanly and NEVER fail closure. Owner = the closure owner (team_100
hub-native; team_110 under an ADR045 `execution_authority: full` mandate) + **team_60** for the git operation.

**The precondition gate — dual `LOD500_LOCKED` (DB *or* file-canonical).** Step 5 removes a worktree only
when the WP is provably at its terminal state, asserted by **STATE** (never by a hook exit code) — this
resolves the ADR034-R10 hub-native case where no DB row exists:

- **DB-backed WP** (a DB row exists): DB `lod_status = LOD500_LOCKED` **AND** `_archive/{WP_ID}/ARCHIVE_MANIFEST.md`
  present on disk.
- **Hub-native file-canonical WP** (`AOS-V*` id, **no DB row** per ADR034 R10 — `POST` returns
  `INVALID_WP_ID_FORMAT`): `lod_status: LOD500_LOCKED` in **both** `metadata.yaml` and `roadmap.yaml` **AND**
  `_archive/{WP_ID}/ARCHIVE_MANIFEST.md` present. No DB probe is attempted.

If the gate does not hold → **SKIP** (log `Step 5 skipped — not LOD500_LOCKED`); closure is unaffected.

**Runbook (the closer follows this verbatim — 7 steps).**

1. **Precondition:** the dual `LOD500_LOCKED` gate above holds; else SKIP.
2. **Resolve THIS WP's worktree — canonical order** (use each candidate only if its resolved path EXISTS on
   disk — `[ -e "$p/.git" ]` — else fall through; never guess):
   - (a) `$AOS_WORKTREE_PATH` if the operator exported it;
   - (b) the **session registry** (authoritative) — `worktree_path` for `$WP_ID` via
     `session_register_client.py owners --wp-id "$WP_ID"` / `aos_session_ctl.sh list-json` /
     `GET /api/sessions/list?live=true` filtered on `wp_id`. It records the real `worktree_path` AND the
     `branch` the operator used. **DB-offline / hub-native (ADR034 R10) degrade:** skip the API, use (c)/(d);
   - (c) `recommended_worktree_for_wp "$WP_ID"` (`start_worktree.sh`) — computes a **path** only
     (`../${REPO}-${slug}`); it does NOT mint a branch;
   - (d) scan `git worktree list --porcelain` for the worktree whose checked-out branch matches the WP's
     recorded closure branch (branch source of truth, in precedence: the session-registry `branch` field →
     the WP `metadata.yaml` `branch`/`work_branch`/`base_branch` if present → else no match).
   - If NONE resolves to an existing path → **no-op SKIP** (the common EXPRESS/OPS/hub-native case; never fail
     closure). Branch names are NOT derivable from the WP id alone — the session registry is the only reliable
     id→branch map.
3. **Derive the branch:** the branch checked out in that resolved worktree
   (`git -C <wt> rev-parse --abbrev-ref HEAD`); if **detached** → worktree-only removal (no branch delete).
4. **End the WP's own session FIRST** (resolves the "closer-is-owner" deadlock): the closer deregisters this
   WP's live session so the worktree has **zero owners** — `aos_session_ctl.sh ... deregister` (or the API
   session-end) for `$WP_ID`. Only then does the live-owner safety clause pass. Skip-fallback: if deregister
   is not possible, the single-target reap MAY proceed when the **sole** remaining owner is the closing
   session itself — identity rule: the owner's `session_id` == `$AOS_SESSION_ID` (normative pid-ancestry
   fallback when `$AOS_SESSION_ID` is unset) — AND `AOS_REAP_CONFIRM=YES`. **NEVER** when a *different*
   session owns it.
5. **Remove EXACTLY this WP's worktree (single-target — NOT a fleet sweep) via the pinned closer entrypoint:**

   ```bash
   AOS_REAP_CONFIRM=YES bash scripts/session_reap.sh --wp-id "$WP_ID" --confirm
   ```

   Single-target mode resolves the one worktree via step 2's order, asserts it passes the D2 safe predicate
   (substituting the WP's `LOD500_LOCKED` state as the merge proof — because GitHub delete-branch-on-merge can
   make a live `gh pr view <branch>` unresolvable), then `git worktree remove <that-path>` (**never
   `--force`**) + the §2 squash-aware branch-delete policy + verify. Do **NOT** use the un-scoped
   `session_reap.sh --confirm` **batch** sweep as the closer — that reaps *every* predicate-passing worktree
   and stays an explicit **operator** hygiene action.
6. **Failure handling:** any safety-clause failure (dirty tree / a *foreign* live session / no
   `LOD500_LOCKED`-or-operator merge proof) ⇒ **leave the worktree, log a WARN, do NOT fail closure.** Step 5
   is best-effort terminal cleanup, not a gate.
7. **Verify-after-mutate:** confirm the worktree directory is gone; a phantom removal is an **error**, not
   success.

**Execution context.** The hub closer runs on the Mac (where `gh` is reachable — Iron Rule #15); on a spoke,
the spoke's closer runs it with the §2b spoke semantics of the WP build spec (GitHub-PR spokes = full
predicate; local-merge / no-remote spokes = **report-only**, never auto-removed; `gh` unreachable ⇒ **ABSTAIN**).

## Immutability of the base

`ADR042_WP_CLOSURE_PROTOCOL_v1.0.0.md` is an **immutable decision record** (status LOCKED, 2026-04-19). This
addendum does **not** edit it — it **ADDS** Step 5 as a new terminal row of the Mandatory Closure Sequence,
exactly as the Team-191-dissolution addendum (v1.1.0) added its superseding text without a history rewrite.
The base's four existing steps, the `LOD500_LOCKED` terminal-state definition, the exemptions, the ordering
constraint, and Check-15 enforcement all stand unchanged.

## Base-file citation correction (recorded here — base is LOCKED)

ADR042 v1.0.0 cites the archive runbook as **`POST_GATE_ARCHIVE_PROCEDURE.md` v1.1.0** at two places — the
Mandatory Closure Sequence Step-1 row (`ADR042:38`) and the References list (`ADR042:66`). The current
canonical runbook is **v1.3.0** (2026-07-09, verify-and-move invariant — the same version the v1.1.0 addendum
already cites). Because the base is LOCKED, the stale `v1.1.0` cites are **corrected here, not edited in
place**: read every `POST_GATE_ARCHIVE_PROCEDURE.md v1.1.0` reference in ADR042 v1.0.0 as **v1.3.0**. (The
editable surface `core/governance/team_100.md`, which carried the same stale cite, IS corrected in place under
this WP's D1.)

## Pre-existing Step-4 drift (noted, out of scope)

`core/governance/team_100.md`'s WP Closure Protocol table carries only Steps 1–3; it **omits** the base's
**Step 4 — Command shipping**. This omission pre-dates this WP and is **out of scope** — D1 adds Step 5
(worktree teardown) to that table and does **NOT** silently reconcile the missing Step 4. A separate hygiene
pass should reconcile `team_100.md`'s table with the ADR042 base (Steps 1–4) if desired.

## Team-roster note

Per D-191auth, Team 191 is dissolved and its `_aos/` + procedure-custodian authority is inherited by
**team_120**; the archive executor is the closing orchestrator (team_100 / team_110) via `archive.py`. This
addendum names **team_120** (custodian) + **team_60** (git op) accordingly and does **not** re-introduce
"Team 191". The ADR042 base and this addendum are reconciled through the v1.1.0 addendum; do **not** assert
the base table and `team_100.md`'s table are byte-identical.

## What is NOT changed

- ADR042 v1.0.0's Steps 1–4, the `LOD500_LOCKED` terminal state, exemptions, ordering constraint, and
  Check-15 enforcement — all unchanged.
- The v1.1.0 (Team-191 dissolution) addendum — unchanged and still in force; this v1.2.0 addendum is additive
  and coexists with it.
- **No history rewrite:** ADR042 v1.0.0 and every artifact citing it remain as-is.

## References

- `governance/directives/ADR042_WP_CLOSURE_PROTOCOL_v1.0.0.md` — the immutable base (Steps 1–4; `LOD500_LOCKED` terminal state)
- `governance/directives/ADR042_ADDENDUM_TEAM191_DISSOLUTION_v1.1.0.md` — the precedent addendum (immutable base + addendum pattern; D-191auth)
- `_aos/work_packages/AOS-V5-WP-WORKTREE-LIFECYCLE/LOD400_BUILD_SPEC_WORKTREE_LIFECYCLE_v1.0.0.md` — the D1–D4 build spec (§2 safe predicate, §2b spoke semantics, §3 D1 runbook) this Step 5 invokes
- `scripts/session_reap.sh` — the reaper hardened under D2 (the `--wp-id` single-target closer entrypoint Step 5 calls)
- `lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md` v1.3.0 — the archive runbook; carries the Step-5 checklist line under D1
- `core/governance/team_100.md` — WP Closure Protocol table; carries the Step-5 row under D1
- `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` — Iron Rule #17 (orchestrator worktree isolation), the creation-side companion to this teardown discipline

## team_00 co-sign (human gate) — SIGNED

- [x] **team_00 co-sign:** Nimrod (team_00) · date: **2026-07-22** — given as an explicit session decision
  ("merge after co-sign"), recorded in `AOS_STRATEGY_TWO_HORIZONS_2026-07-22.md` (הכרעות team_00 §1).
- Authored by **team_100** (Claude / `claude-opus-4-8`), 2026-07-22.

## Decisive-gate record (honest, per team_00 ruling 2026-07-22)

- **Design (the §2 predicate):** cross-engine validated pre-build — **10 adversarial rounds**
  (composer-2.5 + cursor-grok-4.5), including a genuine fail-closed BLOCKER caught by the second engine.
- **Implementation (D2–D4 scripts):** Tier-1 independent validation achieved — builder `claude-sonnet` (team_60
  sub-agent), adversarial line-review + functional ACs by `claude-opus-4-8` (validate 0-FAIL; live-tree dry-run
  excludes primary/automation; report-only default; `-D` gh-MERGED-gated). **Tier-2 (non-Claude engine) is an
  OPEN DEBT:** six cursor-agent attempts (grok-4.5 ×3, composer-2.5 ×2 + initial) returned empty (known CLI
  empty-choke; gpt-5.x budget-blocked until 2026-08-10). Per explicit **team_00 ruling 2026-07-22**: merged with
  the Tier-2 implementation re-validation **deferred to the next release train**. This note is that debt's record.

---
*team_100 (author) · team_00 co-signed 2026-07-22 · ADR042 Addendum v1.2.0 · Step 5 worktree teardown · AOS-V5-WP-WORKTREE-LIFECYCLE D1*
