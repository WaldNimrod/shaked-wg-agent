# ADR052 — AOS Operating Environment & Session Model

**Status:** ACCEPTED
**Date:** 2026-06-01
**Decided by:** Team 00 (Principal)
**Authors:** Team 100 (Chief System Architect)
**Program:** AOS-SESSION-MODEL (W1/5) · **Track:** STANDARD
**Relates to:** ADR051 (local-first CI — first instance of this reframe), Iron Rule #1 (cross-engine
validation), Iron Rule #4 (inter-team artifacts), Iron Rules #11/#12 (governance source→snapshot),
ADR034 (DB-as-SSoT). **Doctrine only** — mechanisms land in program WPs W2–W5.

## Context

AOS inherited assumptions from **multi-developer team software houses**: branches as collaboration
boundaries, CI as a contributor gate, artifacts as human-to-human handoffs, git as people-sync. The
**real** operating environment is different and must be stated explicitly:

> **One human (team_00) orchestrating ephemeral AI sessions on one Mac**, plus a small set of
> environment-isolated teams (cowork, Claude Design, web research, home server).

Because the assumption was implicit, real data-integrity hazards have occurred and were observed
directly during this very program's lead-up:
- **nimrod-bio** uncommitted `_aos/` drift blocked a hub gov-sync (Check 32).
- A **QA-harness** session's uncommitted files entangled commits in the shared tree.
- A **parallel session** left an uncommitted fix in the shared working tree (no isolation).

ADR051 (local-first CI) was the first correction — it recognized CI's multi-contributor value is ~0
for a single developer. This ADR generalizes the insight into doctrine.

## Decision

1. **Coordination is repointed people → sessions.** AOS's coordination machinery (branches, gates,
   artifacts) exists to coordinate *ephemeral AI sessions and assure quality*, not to coordinate
   multiple humans. Git serves **backup + deploy + session isolation**, not people-sync. Mechanisms
   that existed purely for human-to-human coordination are candidates for calibration; mechanisms that
   serve quality (cross-engine #1) or ephemeral-session context (artifacts #4) are retained or strengthened.

2. **Two operating modes:**
   - **SOLO** (default): single developer, multiple concurrent sessions, **worktree-isolated**, local-first.
   - **COLLAB** (canonical but **dormant**): external developer(s); requires **explicit declaration** to
     activate, which re-activates multi-dev machinery (branch protection, PR review, CI-as-contributor-gate).

3. **Special-teams environment taxonomy.** Every session carries an `environment`. The worktree-isolation
   rule (W2/W3) applies **only** to sessions sharing the local Mac tree; environment-isolated teams are
   **exempt from worktrees but still register** (W3).

4. **DB-as-SSoT reaffirmed (no file-SSoT for structured state).** Files drift (demonstrated repeatedly);
   structured session/coordination state lives in the DB via API. Files are for documents only.

5. **Phase-1 non-silent.** Session-coordination mechanisms ship **visible to team_00** first; promotion to
   **Phase-2 (automatic)** is a separate, later decision per mechanism.

6. **This ADR is doctrine.** The pre-flight (W2), DB register (W3), smart-mail/handoff (W4) and
   DB-friction reduction (W5) implement it.

## Consequences

- **Positive:** eliminates silent cross-session data clobbering; gives the single operator a clear model;
  calibrates ceremony to the real environment (less human-handoff overhead, more session-context rigor).
- **Cost:** adds a SOLO/COLLAB branch to the mental model; worktree discipline is a (small) habit change.
- **Becomes mandatory (W2–W5):** worktree isolation for concurrent local sessions; DB session register;
  auto-captured handoffs; lower-friction DB mutation paths.

## Alternatives Considered

- **Keep multi-dev assumptions implicit** — REJECTED (caused the observed hazards; mismatched reality).
- **File-based session state** — REJECTED (drift; contradicts ADR034 and team_00 directive — DB stays SSoT).
- **Drop the external-developer path** — REJECTED (team_00 requires COLLAB as a canonical, if dormant, mode).

## Rollout

W1 publishes this ADR + `methodology/AOS_OPERATING_ENVIRONMENT_v1.0.0.md` + startup pointers, then hands
off to W2. Each subsequent WP is gated by team_00 approval (charter §5). Propagated to spokes via
`propagate_governance.sh` after program-level closure.
