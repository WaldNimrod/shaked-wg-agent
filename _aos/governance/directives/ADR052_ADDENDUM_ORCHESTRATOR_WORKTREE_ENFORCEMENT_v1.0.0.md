---
id: ADR052_ADDENDUM_ORCHESTRATOR_WORKTREE_ENFORCEMENT
extends: ADR052_AOS_OPERATING_ENVIRONMENT_AND_SESSION_MODEL_v1.0.0.md (Decision #2 — SOLO mode, worktree-isolated)
status: ACCEPTED (2026-07-15) — team_00 direct approval, authored by team_100 under IR#12 governance-authority
authority: team_00 (Principal) — mandate MANDATE_team_00_via_team_120_TO_team_100_WORKTREE_ISOLATION_LOCKDOWN_2026-07-15_v1.0.0.md
authoring_team: team_100
wp: (ad hoc mandate, no WP id — EXPRESS-track governance fix)
date: 2026-07-15
new_iron_rule: "Iron Rule #17 (AOS_CONCEPT_AND_PRINCIPLES.md Iron Rule #11)"
---

# ADR052 — Addendum: Orchestrator Worktree Enforcement

> **Status: ACCEPTED.** team_00 pre-authorized this addendum directly in the mandate that requested it
> ("this recurs all the time, so it's very important to lock it down well in our governance" — IR#12
> governance-change authority to team_100 is explicit in the mandate).

## §0 — Why this addendum exists

ADR052 already states the SOLO-mode principle: "multiple concurrent sessions, **worktree-isolated**,
local-first" — and its own Context section had *already logged two prior instances* of the exact failure
this addendum closes (an uncommitted `_aos/` drift from nimrod-bio; a QA-harness session's uncommitted
files entangling commits). The principle existed. It was never mechanically enforced for the one class of
session most likely to violate it: **the fleet-mutating orchestrator itself.**

## §1 — The 2026-07-15 incident (empirical origin)

A team_100 session ran `aos_sync_all.sh --all` from the shared primary hub checkout
(`/Users/nimrod/Documents/AOS_V5/agents-os`) to fix a genuine bug it had found in the propagation
pipeline (`propagate_governance.sh`'s Phase-5 spoke-validation running before `aos_sync_all.sh` Step 2
had refreshed the spoke's lean-kit cache — a transient false-positive on every full sync). It authored a
correct, minimal, well-tested fix (`AOS_PROPAGATE_ORCHESTRATED=1`, matched pair across both scripts) but
**left it uncommitted** in the shared working tree. Concurrently, team_120 was landing three merged PRs
(#41–#43) in/around that same shared tree. The tangle looked like a possible overwrite. Forensics (team_120,
`STATUS_RESET_...2026-07-15`) proved **zero data loss, zero force-push, zero clobbering** — but the fix was
one `git checkout -f` / `reset --hard` away from being gone before team_120 preserved it out-of-band as
PR #44. team_00 flagged the near-miss and issued this mandate.

## §2 — Root cause (examined, not just the one instance)

Three compounding gaps, confirmed live on 2026-07-15:

1. **Every fleet-mutating entrypoint resolves its working root from where it was invoked, not from any
   worktree-aware policy.** `aos_sync_all.sh` (`AOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"`),
   `propagate_governance.sh` (same pattern), and `sync_definition_snapshots.sh`
   (`REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`) all derive their root from `$0`'s
   location — i.e. wherever the script file happens to live on disk when invoked. None of them ever asked
   "is this the primary checkout or a dedicated worktree?" `sync_definition_snapshots.sh` and
   `aos_sync_all.sh` (Steps 3b/4c) `git commit` — occasionally `git push` (TikTrack `live_server: true`) —
   directly against that ambient location.

2. **The existing isolation mechanism was decorative for the actual mutation path.**
   `ensure_automation_worktree.sh` creates `../agents-os-automation` and IS called by `aos_sync_all.sh`
   Step 3b — but *only* for a side-call to `aos_session_ctl.sh register` (session bookkeeping). The real
   propagation/commit logic still runs against `$AOS_ROOT`, wherever that resolved to. The automation
   worktree existed in name, not in the mutation path — a false sense of safety.

3. **The one mechanism that could have caught this at gate-time — `validate_aos.sh` Check 52
   (concurrent-session enforcement) — was silently degraded in this exact session, and is degraded in
   essentially every normal local-mac session.** Its SKIP message reads "register backend degraded (DB
   offline advisory)" — but the DB was confirmed `status: online` throughout. Reproduced live: calling
   `session_register_client.py detect` with no `AOS_API_BASE` set returns `HTTP 0 / connection refused`
   (defaults to unreachable `127.0.0.1:8092` — `session_register_client.py`'s `_api_base()` does **not**
   fall back to `core/.env`'s `AOS_V3_PUBLIC_API_BASE` the way the DB probe does); with the canonical
   Tailscale base (`AOS_API_BASE=http://100.125.98.56:8092`) but no `AOS_ACTOR_API_KEY`, it returns
   `HTTP 401 INVALID_ACTOR_KEY`. Check 52's advisory text mislabels an **auth/API-base gap** as an
   **infra outage**, so operators (this session included) have been reading it as harmless noise. Its
   enforcement has likely never actually fired in practice. **Not fixed by this addendum** (out of the
   mandate's binding scope — recorded here as a finding for a future WP); the primary enforcement built
   below is deliberately git-native and has no dependency on this backend, so it works regardless.
   `aos_governance_bootstrap.sh` was also examined and found **not** to carry this exposure — it copies
   cache files only, no `git commit` calls.

## §3 — Decision (the binding rule + enforcement)

**Binding rule (Iron Rule #17 / `AOS_CONCEPT_AND_PRINCIPLES.md` Iron Rule #11):** Any session running
fleet-mutating orchestration (`aos_sync_all.sh`, `propagate_governance.sh` standalone,
`sync_definition_snapshots.sh` standalone, or any future hub→spoke propagation entrypoint) MUST run from a
dedicated isolated worktree — never the shared primary hub checkout. A script/canon fix authored mid-run
MUST be committed to a branch + PR — never left uncommitted in the shared primary checkout.

**Enforcement — two independent, defense-in-depth layers, neither dependent on the DB/register backend:**

1. **`scripts/lib/aos_worktree_guard.sh`** — a shared guard function
   (`aos_require_isolated_worktree "<caller>"`), sourced by all three entrypoints immediately after their
   own argument parsing, gated on the mutating path only (`--dry-run`/`--check`/legacy modes are exempt —
   they never commit). Detection is pure git: compares `git rev-parse --show-toplevel` against
   `git worktree list --porcelain`'s first (`main`) entry. Primary checkout + mutating flags → refuses
   with exit 12 and a remediation command. Documented, audited override:
   `AOS_ALLOW_PRIMARY_CHECKOUT_SYNC=1`. `aos_sync_all.sh` exports `AOS_WORKTREE_VERIFIED=1` on success so
   the sub-scripts it invokes (which inherit its environment) do not re-prompt.

2. **`validate_aos.sh` Check 76 (hub-only)** — independently FAILs if the primary checkout ever carries
   uncommitted changes under `scripts/`, `lean-kit/`, `core/governance/`, `methodology/`, or
   `governance/directives/`. This is the safety net for however residue might land there regardless of
   cause (a bypassed guard, a manual edit, a future entrypoint that forgets to source the guard). Isolated
   worktrees (feature branches, the automation worktree) are explicitly exempt — legitimate WIP there is
   expected, not a violation.

**Proof (2026-07-15, this build):**
- Guard, from the primary checkout: `⛔ FATAL (... / Iron Rule #17): ... exit code: 12`.
- Guard, from an isolated worktree: passes silently, exports `AOS_WORKTREE_VERIFIED=1`.
- Guard, with the documented override: warns, passes.
- Check 76, primary checkout clean: `[PASS]`.
- Check 76, isolated worktree with real WIP: `[SKIP]` (not primary — correctly exempt).
- Check 76, primary checkout with a simulated dangling change: `[FAIL]` (reverted immediately after proof).

## §4 — Consequences

- **Positive:** closes the exact 2026-07-15 near-miss class mechanically, not just by documentation. Two
  independent layers (pre-flight refuse + post-hoc detect) mean a bypass of one is still caught by the
  other. Zero new infrastructure dependency (pure git) — works even while Check 52's DB-register path
  stays degraded.
- **Cost:** an operator running `aos_sync_all.sh --all` interactively from the primary checkout for the
  first time after this lands must create a worktree first (one `git worktree add` — the guard's own error
  message gives the exact command).
- **Deliberately out of scope:** repairing Check 52's degraded-by-default auth/API-base gap (§2.3) — a
  real, separate finding, recommended as a future WP, not required for this mandate's binding outcome.

## §5 — Alternatives considered

- **Rely on Check 52 alone (DB-backed concurrent-session detection)** — REJECTED as the *sole* mechanism:
  it was the thing that failed to catch this exact incident (§2.3), and fixing its degraded-by-default
  state is a larger, separable piece of work than this mandate's binding scope.
- **Route the actual git operations of `aos_sync_all.sh` through the automation worktree instead of adding
  a guard** — considered, REJECTED for this pass: it would require rewriting every path variable
  (`$path`, `$AOS_ROOT`) used across ~700 lines to resolve through a second checkout, a much larger and
  riskier change than a refuse-and-redirect guard. Left as a future hardening option if the guard proves
  insufficient in practice.

## §6 — Rollout

Lands as `feat/orchestrator-worktree-isolation-lockdown` → PR → merge → `aos_sync_all.sh --all` run from
this same isolated worktree (dogfooding the rule being built) to propagate the guard, the new Check 76,
this ADR addendum, and the Iron Rule #17 canon text to all 13 spokes.
