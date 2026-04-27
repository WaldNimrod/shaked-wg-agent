# ADR040 — AOS Domain Authority Lockdown

**Status:** LOCKED
**Version:** v1.0.0
**Date:** 2026-04-19
**Owner:** Team 00 (Principal)
**Executor of propagation:** Team 100 (Chief Architect)

---

## Context

AOS is a multi-domain, multi-engine infrastructure (see `methodology/AOS_IDENTITY_ONBOARDING_v1.0.0.md`). The hub (`agents-os`) propagates governance (`core/governance/team_*.md`, `lean-kit/`, canon, directives) to 9+ spoke repos as read-only snapshots in each spoke's `_aos/` directory.

Prior to this ADR, the governance-update and governance-sync commands (`/AOS_gov-update`, `/AOS_gov-sync`) had **no runtime authority enforcement**. The procedure documented that only `team_00` (approval) and `team_100` (execution) may perform governance changes, but the commands and scripts did not verify caller identity. This created a real incident vector: any agent invoking these commands in the hub could propagate changes that Team 00 never approved.

A concrete incident triggered this lockdown: on 2026-04-19, hub `CLAUDE.md` and `.cursorrules` were edited for a DB-connectivity fix but only 3 of 9 spokes received the same edit (no canonical spoke template existed; propagation script scope was too narrow). This demonstrated both authority drift and propagation scope drift.

## Decision

### 1. Iron Rule #12 (NEW)

> **`/AOS_gov-update` and `/AOS_gov-sync` are permitted only to `team_00` (Principal) and `team_100` (Chief Architect). Any other team attempting to invoke these commands MUST be rejected with a pointer to the `GOVERNANCE_CHANGE_REQUEST` workflow.**

This rule is added as Iron Rule #12 to the uniform Iron Rules list maintained in `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` and mirrored in all `CLAUDE.md` / `.cursorrules` canonical templates.

### 2. Three-layer authority enforcement

**Layer A — Slash command preamble (Phase -1 Authority Check):**
- Both `/AOS_gov-update.md` and `/AOS_gov-sync.md` start with a mandatory Phase -1 block
- Phase -1 must: identify caller team (via `AOS_ACTOR_TEAM_ID` env, `.claude/.actor` file, or explicit user prompt); STOP and output rejection message if team is not in `{team_00, team_100}`
- Rejection message must point to GCR template location and procedure doc

**Layer B — Script-level gate (`propagate_governance.sh` + `aos_sync_all.sh`):**
- Scripts require `AOS_ACTOR_TEAM_ID` env var set to `team_00` or `team_100`
- Missing or unauthorized value → exit code 10 with actionable message
- Hub identity verifier: check `_aos/project_identity.yaml` exists at `AOS_ROOT`; exit code 11 if not a hub

**Layer C — Validation checks (`validate_aos.sh`):**
- Check 27: canonical `CLAUDE.md` invariants (hub + all spokes) — AOS Spoke Notice, Iron Rule #12, canonical startup sequence must be present
- Check 28: canonical `.cursorrules` invariants (same)
- Check 29: spoke `_aos/lean-kit/LEAN_KIT_VERSION.md` matches hub `lean-kit/LEAN_KIT_VERSION.md`

### 3. Phase 0.5 — Team 00 Approval Gate (gov-update only)

Before Phase 1 (Understand) in `/AOS_gov-update` proceeds:
- If caller is `team_100`: require explicit Team 00 approval capture. Agent must either reference an existing approval artifact (`_COMMUNICATION/team_00/APPROVAL_*.md`) OR ask the user "Is this change approved by Team 00? Please confirm yes/no."
- If `no` or ambiguous → STOP. Instruct caller to obtain explicit approval before proceeding.
- If caller is `team_00`: approval is implicit; proceed directly.

Rationale: Team 00 is the final human authority on all governance. This gate prevents Team 100 from drive-by edits that bypass principal review.

### 4. Governance Change Request (GCR) is the ONLY path for non-AOS teams

Any team other than `team_00` / `team_100` that needs a governance or `_aos/` change MUST:
1. Copy template: `lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template`
2. Fill with: requesting team ID, proposed change (exact section + wording), rationale, precise prompt for team_100, impact assessment
3. Save as: `_COMMUNICATION/team_XX/GOVERNANCE_CHANGE_REQUEST_{TOPIC}_v1.0.0.md` in the hub (teams edit only their own `_COMMUNICATION/team_XX/` directory)
4. Route to team_100 via canonical routing artifact
5. Wait for team_00 approval → team_100 execution → snapshot arrives on next sync

No out-of-band edits. No direct `_aos/` modifications by domain teams. GCR is the only allowed request path.

### 5. Canonical templates (RC3 fix)

Going forward, every spoke's `CLAUDE.md` and `.cursorrules` is **rendered from a canonical template** at:
- `lean-kit/modules/project-governance/templates/SPOKE_CLAUDE_TEMPLATE.md`
- `lean-kit/modules/project-governance/templates/SPOKE_CURSORRULES_TEMPLATE.md`

The template contains a locked canonical section (between `<!-- aos:canonical:start -->` and `<!-- aos:canonical:end -->` markers) that is overwritten on every sync, plus a project-specific section (between `<!-- aos:project-specific:start -->` and `<!-- aos:project-specific:end -->` markers) that is preserved.

This eliminates drift: any future edit to the canonical section happens once in the hub template and propagates to all spokes via `scripts/aos_sync_all.sh`.

### 6. Full-scope sync (RC1 fix)

`scripts/aos_sync_all.sh` (new) replaces the narrow scope of `propagate_governance.sh --all`. Full-scope covers:
- `core/governance/team_*.md` → spoke `_aos/governance/`
- `lean-kit/**` (physical copy) → spoke `_aos/lean-kit/`
- Rendered spoke `CLAUDE.md` + `.cursorrules` from canonical templates
- `_aos/project_identity.yaml` integrity verification per spoke

`propagate_governance.sh` is preserved for its narrow-scope use case (team-contract-only fast sync).

## Consequences

**Immediate (on lockdown):**
- Any non-AOS team attempting `/AOS_gov-update` or `/AOS_gov-sync` gets a hard stop + GCR pointer
- Team 100 must capture Team 00 approval before every gov-update execution
- `AOS_ACTOR_TEAM_ID` env var becomes required for propagation scripts

**Short-term (post-lockdown):**
- All 10 domains receive canonical CLAUDE.md / .cursorrules via `aos_sync_all.sh`
- Drift becomes impossible (template-driven)
- Three validation checks (27/28/29) enforce uniformity on every `validate_aos.sh` run

**Long-term (governance clarity):**
- New agents receive `AOS_IDENTITY_ONBOARDING_v1.0.0.md` as mandatory first read
- The domain/infrastructure boundary is explicit in every repo via the "AOS Spoke Notice" block
- Non-AOS teams know the exact path (GCR) for any governance concern

## Supersedes / relates to

- **Relates to:** ADR034 (Data Authority — DB SSOT), Iron Rule #7 (API-only when DB online)
- **Relates to:** ADR038 (Governance File Source-Mirror Architecture)
- **Relates to:** AOS_GOVERNANCE_UPDATE_PROCEDURE — bumps to v1.1.0 to reference this ADR and Phase 0.5

## References

- `methodology/AOS_IDENTITY_ONBOARDING_v1.0.0.md`
- `methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.1.0.md` (bumped by this ADR)
- `lean-kit/modules/project-governance/templates/SPOKE_CLAUDE_TEMPLATE.md`
- `lean-kit/modules/project-governance/templates/SPOKE_CURSORRULES_TEMPLATE.md`
- `lean-kit/modules/project-governance/scripts/propagate_governance.sh` (authority gate added)
- `scripts/aos_sync_all.sh` (new — full-scope sync)
- `_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh` (Checks 27/28/29 added)

---

**LOCKED 2026-04-19 — Iron Rule #12 is immutable. Any amendment requires a new ADR that supersedes this one.**
