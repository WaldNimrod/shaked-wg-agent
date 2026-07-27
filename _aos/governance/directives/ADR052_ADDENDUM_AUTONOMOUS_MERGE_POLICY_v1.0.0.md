---
id: ADR052_ADDENDUM_AUTONOMOUS_MERGE_POLICY
extends: ADR052_ADDENDUM_M7_AUTONOMOUS_DISPATCH_DOCTRINE_v1.0.0.md ("Merge to main → KEEP HUMAN")
status: ACCEPTED (2026-07-15) — team_00 direct approval, authored by team_100 under IR#12 governance authority
authority: team_00 (Principal) — approved the architecture in-session 2026-07-15
authoring_team: team_100
track: OPS
date: 2026-07-15
enforced_by: scripts/hooks/gh_merge_guard.sh (PreToolUse) + validate_aos.sh Check 77
---

# ADR052 — Addendum: Autonomous Merge Policy

> **Status: ACCEPTED.** team_00 approved this architecture directly in-session (2026-07-15) after reviewing
> the trade-offs. It refines — does not weaken — ADR052's M7 doctrine "**autonomous to the gate, human at
> the gate**" by defining the *precise, machine-checkable* slice of `gh pr merge` that is safe to run
> autonomously, and routing everything else to a human prompt.

## §0 — Why this addendum exists

The M7 addendum states "**Merge to main → KEEP HUMAN**." In practice, the enforcement of that line was a
**fuzzy LLM classifier** ("[Merge Without Review]") plus, as a stop-gap, a **blanket
`Bash(gh pr merge:*)` allow rule** in a machine-local `.claude/settings.local.json`. Both are wrong tools:

- The classifier is non-deterministic and prompts even on the safe, routine case (merging one's own green
  feature-branch PR), producing repetitive friction.
- The blanket allow is the opposite failure: **machine-local, un-audited, over-broad** — it matches
  `gh pr merge --admin` (which bypasses branch protection and required checks) and *any* PR including other
  sessions' unreviewed drafts, and it applies to only one machine, so fleet behavior is non-uniform.

Neither expresses the actual policy. This addendum makes the policy **explicit, deterministic, auditable,
and fleet-uniform**.

## §1 — The policy (balanced)

A `gh pr merge` invocation is **auto-ALLOWED** only when **ALL** of the following hold:

1. The target PR is **OPEN** and **not a draft**.
2. Checks have passed — GitHub `mergeStateStatus` ∈ **{CLEAN, HAS_HOOKS}** (mergeable, required checks
   satisfied, not BLOCKED/BEHIND/DIRTY/UNSTABLE/UNKNOWN).
3. The PR's **head branch matches a `.git-branch-allowlist` pattern** (the same branch SSoT the pre-commit
   branch guard uses — a sanctioned dev branch, not an ad-hoc one).
4. The command does **not** contain **`--admin`** (which would bypass branch protection).

Anything else → **ASK** (the normal human prompt). Any inability to evaluate the policy — `gh` or `jq`
unavailable, PR metadata not resolvable — **degrades to ASK**, never to a silent allow. `--admin` is
**always** human-gated regardless of PR state.

This carves the safe autonomous slice precisely: the routine "merge my own green, reviewed-by-CI,
sanctioned-branch PR" flows without friction; every risk vector (admin bypass, unreviewed/failing/draft
PRs, rogue branches, tool failure) is routed to the human.

## §2 — Enforcement (deterministic, DB-independent, fleet-uniform)

1. **PreToolUse hook** — `scripts/hooks/gh_merge_guard.sh`, wired in the **committed** hub
   `.claude/settings.json` under `hooks.PreToolUse` (matcher `Bash`, `if "Bash(gh pr merge:*)"`). It reads
   the tool command from stdin, resolves the PR via `gh pr view --json state,isDraft,mergeStateStatus,headRefName`,
   applies §1, and emits `permissionDecision: "allow"` or `"ask"`. The decision logic is a pure, unit-tested
   function (`_merge_guard_decide`). Pure git/gh/jq — no DB dependency.
2. **`validate_aos.sh` Check 77** — asserts (hub + every spoke) that `.claude/settings.json` carries the
   merge-guard PreToolUse wiring AND `scripts/hooks/gh_merge_guard.sh` is present + executable. FAILs on
   drift, so the policy cannot silently fall out of a domain. Same shape as Check 76 (IR#17).
3. **Fleet propagation** — the hook script + the canonical hooks block (SSoT:
   `lean-kit/modules/project-governance/templates/settings_hooks_block.json`) are propagated to every spoke
   by `aos_sync_all.sh` (source→snapshot, IR#11), the same machinery that fans out the pre-push hook. The
   per-spoke `.claude/settings.json` is a **surgical merge** — only the `hooks` block is injected; each
   domain's existing `permissions` are preserved.

## §3 — Consequences

- **Positive:** replaces a fuzzy prompt + an over-broad local allow with one explicit rule, uniform across
  all domains and machines, auditable in git, and enforced by a check. `--admin` and unreviewed/failing
  merges are always human-gated; the routine safe merge is frictionless.
- **Cost:** the hook makes a `gh pr view` call (~1s, bounded by `timeout: 30`) on each `gh pr merge`. A
  newly-wired project hook may require one `/hooks` reload or a session restart before it activates (the
  settings watcher only tracks directories that had a settings file at session start).
- **Removed:** the machine-local `Bash(gh pr merge:*)` blanket allow in `agents-os/.claude/settings.local.json`
  — superseded by the hook.

## §4 — Alternatives considered

- **Keep the classifier / do nothing** — REJECTED: non-deterministic, prompts on the safe case, not
  fleet-uniform.
- **Blanket allow (what we had)** — REJECTED: over-broad (`--admin`, any PR), un-audited, machine-local.
- **A narrower static allow rule** — REJECTED: Claude Code permission rules are prefix globs and cannot
  express "not `--admin`", "checks green", or "my own sanctioned branch". Only a hook can encode conditions.
- **Committed blanket allow in `.claude/settings.json`** — REJECTED: fleet-uniform but still over-broad;
  loses the conditional guard.

## §5 — Rollout

Built from a dedicated isolated worktree (IR#17), landed via PR, and propagated fleet-wide by
`aos_sync_all.sh --all` run from that worktree — dogfooding both IR#17 and (on its own merge) this policy.
