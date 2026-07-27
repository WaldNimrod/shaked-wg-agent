---
id: ADR054_GOVERNANCE_DISTRIBUTION_MODEL_B
title: "ADR-054 — Governance Distribution Model B (git-ignored local cache + pull; decouple governance from each domain's git lifecycle)"
version: "1.0.0"
status: LOCKED             # HG-2 sign-off 2026-06-06 (team_00) after decisive L-GATE_VALIDATE Tier-2 PASS + fleet rollout
author: Team 100 (Chief System Architect)
approved_by:
  - team_00            # direction approved 2026-06-05; HG-1 authorized S2 2026-06-06
  - team_100
approval_date: "2026-06-06"
adr_ref: ADR-054
wp: AOS-V4.5-WP-GOV-DISTRIBUTION-MODELB
amends: "Iron Rule #2 (physical copy → physical copy OR git-ignored local cache; never symlink)"
based_on:
  - _COMMUNICATION/team_100/ANALYSIS_AOS_GOVERNANCE_DISTRIBUTION_MODEL_v1.0.0.md
  - _COMMUNICATION/team_100/AOS-V4.5-WP-GOV-DISTRIBUTION-MODELB/LOD200_PLAN_OF_RECORD_v1.0.0.md
related: [ADR052 session model, ADR053 tiered validation, ADR040 gov authority, ADR034 data authority]
---

# ADR-054 — Governance Distribution Model B

> **One line:** Governance snapshots become a **git-ignored local cache refreshed by sync**, with a tracked `_aos/AOS_GOVERNANCE_VERSION.yaml` stamp for audit — so governance never touches a domain's git history / branch / push / CI.

## 1. Context

Governance was distributed as a **286-file snapshot committed onto each domain's working branch** (`aos_sync_all.sh` Step 3b) and dragged through the domain's push/CI. This coupled a one-directional *distribution* concern to each domain's *development* git lifecycle, producing every observed gov-sync collision: nimrod-bio push blocked by its own stale-MSG-LOG CI check, EyalAmit's 16 unrelated commits dragged along, dirty-tree blocks, branch non-determinism, work/gov interleaving. Full analysis + 3 candidate models: the analysis artifact (based_on).

## 2. Decision

Adopt **Model B**: `_aos/{governance, methodology, lean-kit}` (**Tier A**) are a **git-ignored local cache**, hydrated from the hub by sync / bootstrap. A small **tracked** `_aos/AOS_GOVERNANCE_VERSION.yaml` stamp records the hub SHA + sync time per domain. The hub remains the single audit SSoT.

- **Tier A (cached, git-ignored):** `_aos/governance/`, `_aos/methodology/`, `_aos/lean-kit/`.
- **Everything else stays tracked:** spoke-owned `_aos/` files (roadmap, definition, metadata, context, work_packages…), `CLAUDE.md`, `.cursorrules`, `scripts/`, `.github/`.
- **Iron Rule #2 amended:** "physical copy, never symlink" → "physical copy **OR** git-ignored local cache refreshed by sync; never a symlink." (Conflict-check: IR#11/#3/ADR040 preserved.)

**Rejected:** Model A (submodule — residual pointer-commit + UX friction), Model C (orphan branch — reintroduces friction on use). Fallback to Model A reserved for any future regulated-audit / long-offline domain (none today — R2/R4).

## 3. Mechanism

1. `.gitignore` the 3 Tier-A paths per domain; `git rm -r --cached` (working tree kept) — one cleanup commit per domain (`aos_modelb_apply.sh`).
2. `aos_sync_all.sh` refreshes the cache in place + writes the stamp; commits an **enumerated tracked set** that **excludes Tier-A** (never blanket `_aos/`). Hub dogfoods (Step 4c same treatment).
3. `propagate_governance.sh` never commits/pushes the cache (Model-B guard).
4. `aos_governance_bootstrap.sh` hydrates Tier-A on cold clone / session start (wired into `aos_session_ctl.sh register`); normative hub resolution (`--hub` → `AOS_HUB_ROOT` → `git archive` → on-hub `projects.yaml`).
5. `validate_aos.sh` Check 50 — advisory staleness + "still-tracked" signal; **never FAIL**.

## 4. Consequences

**Positive:** all five collisions eliminated; governance invisible to domain git/branch/push/CI; trivial refresh; hub stays audit SSoT; per-domain version answerable from the tracked stamp. **Residual (accepted, v1):** rare low-churn coupling for `CLAUDE.md`/`.cursorrules`/`definition.yaml` team-blocks (rendered/merged, stay tracked) — LOD200 §2.2; zero-residual is a future follow-up. **Bootstrap dependency:** cold clone needs one sync before governance-dependent ops (mitigated — C/D tracked, bootstrap is step 0).

## 5. Validation & rollout

- L-GATE_ELIGIBILITY PASS (team_190/codex, Tier-1); L-GATE_SPEC PASS R2 (team_190/codex, Tier-1, R1 caught 3 blockers); **L-GATE_BUILD PASS Tier-2 cross-engine** (team_90/cursor-composer-2, builder claude-code, 11/11) on the **aos-sandbox-lean pilot**.
- Rollout: pilot → batched fleet (low-stakes → active → **hub last**) under HG-1.
- Status → **LOCKED** at HG-2 after the decisive **L-GATE_VALIDATE** (Tier-2, team_190).

## 6. Reversibility

Per-domain reversible: remove the `.gitignore` block + `git add` the paths (working-tree snapshot never deleted). Tooling: `git revert` the rework commits. If reverted fleet-wide, this ADR → SUPERSEDED.

## 7. Cross-references

| Topic | Artifact |
|---|---|
| Analysis (3 models + R1–R5) | `_COMMUNICATION/team_100/ANALYSIS_AOS_GOVERNANCE_DISTRIBUTION_MODEL_v1.0.0.md` |
| Plan of record | `.../AOS-V4.5-WP-GOV-DISTRIBUTION-MODELB/LOD200_PLAN_OF_RECORD_v1.0.0.md` |
| Build spec + record | `_aos/work_packages/AOS-V4.5-WP-GOV-DISTRIBUTION-MODELB/LOD400_BUILD_SPEC_v1.0.0.md` (+ `_BUILD_RECORD_`) |
| IR#2 conflict-check | `.../AOS-V4.5-WP-GOV-DISTRIBUTION-MODELB/CONFLICT_CHECK_IR2_v1.0.0.md` |
| Tiered validation | `governance/directives/ADR053_TIERED_VALIDATION_MODEL_v1.0.0.md` |

*Authored by team_100 under AOS-V4.5-WP-GOV-DISTRIBUTION-MODELB. PROPOSED → LOCKED at HG-2.*
