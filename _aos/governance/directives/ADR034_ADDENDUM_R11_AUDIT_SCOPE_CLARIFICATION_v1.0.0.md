# ADR034 Addendum R11 — Audit-Trail Scope Clarification + Optional SMB Pattern

**Type:** Architecture Decision Record — Addendum to ADR034
**Status:** LOCKED
**Date:** 2026-05-22
**Authority:** Team 00 (Principal) + Team 100 (Chief Architect)
**Parent ADR:** `ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`
**Trigger:** `GCR_AOS_ADR034_SYNC_LOG_SMB_ACTOR_IDENTITY_v1.0.0` filed by team_100@tiktrack 2026-05-22
**Triage ref:** `_COMMUNICATION/team_100/TRIAGE_GCR_ADR034_SMB_2026-05-22_v1.0.0.md`

---

## §0 Why this addendum exists

A TikTrack-spoke artifact (`PILOT_PROGRAM_CHARTER_v1.1.0_ADDENDUM.md`) cited ADR034 as the authority for an audit-column requirement (`sync_log` must record `actor_team_id` + `timestamp` + `query_type`) on a spoke product-domain table. Hub-side verification (grep `actor_team_id` across `governance/`, `methodology/`, `lean-kit/`, `core/governance/` → 0 matches) confirmed **ADR034 does not contain this requirement**. ADR034's audit-trail mention (line 80) is about `deploy_log` — a hub-internal table tracking `deploy_cascade()` operations on hub-canonical entities.

The misattribution was good-faith but propagated through a spoke pilot program's R3 spec authoring (Sonnet cube-spec subagent), Codex EXT-CP1/EXT-CP2 verdicts, and team_50 QA — all of whom validated the **amendment chain** as principled without independently verifying ADR034's source text.

This addendum **clarifies the scope of ADR034** so that:
1. Future spokes don't repeat the misattribution.
2. The TikTrack pilot R3 R.7 close stands without spoke-side governance drift.
3. Spokes that voluntarily adopt ADR034-style audit patterns have explicit SMB guidance.

---

## §A — Scope clarification (binding)

**ADR034 governs HUB-CANONICAL data.** Specifically, the API-only mutation requirement (ADR034 R1, R2) applies to:

| Hub-canonical data class | DB table | File (deployed snapshot) |
|---|---|---|
| Work package state | `work_packages` | `roadmap.yaml` |
| Team configuration | `teams` | `definition.yaml` |
| Project metadata | `projects` | `_aos/projects.yaml` |
| Deploy audit trail | `deploy_log` | (DB-only) |

The audit-trail clause in ADR034 rationale §5 ("`deploy_log` table records every deploy with actor, trigger, timestamp, and file hashes") refers to the **`deploy_log` hub-internal table**. It is NOT a generic requirement that all audit tables across all spokes must include `actor_team_id`.

**Spoke product-domain audit tables are spoke-architecture decisions.** Examples of tables that are NOT governed by ADR034:
- TikTrack's `user_data.sync_log` (IBKR sync audit) — TikTrack-domain
- HobbitHome's WordPress activity audits — HobbitHome-domain
- SmallFarmsAgents' agent activity logs — SmallFarmsAgents-domain
- Any other spoke product table that records app-level operations on user/business data

Hub canon does NOT mandate audit-column schemas on spoke product data. Each spoke owns its product-domain audit design.

### §A.1 — Consequences

1. **Spoke claims of "per ADR034" requirements on product-domain tables are out-of-scope unless explicitly named in this clarification.** Spokes adopting ADR034 patterns voluntarily MUST cite §B (below) rather than invent "per ADR034" clauses in their charters.
2. **Hub `deploy_log` audit columns remain bound by ADR034 R1+R2** — the DB-as-SSoT API-only mutation path is unchanged.
3. **The TikTrack `PILOT_PROGRAM_CHARTER_v1.1.0_ADDENDUM.md` citation** ("`sync_log` records broker connection events with `actor_team_id`, `timestamp`, `query_type` per ADR034 audit trail") is **retroactively re-scoped** under §B below as an optional spoke pattern. No spoke-side charter edit is required; the citation now reads as an opt-in adoption of an ADR034-inspired pattern rather than a mandate.

---

## §B — Optional SMB pattern (non-binding template for spokes)

Spokes that VOLUNTARILY choose to adopt ADR034-style audit-trail patterns on their product-domain tables MAY follow the template below. This is a **spoke architecture choice**, not a hub mandate.

### §B.1 — Standard audit-trail tuple (multi-tenant / multi-team-actor deployments)

For deployments where multiple agent teams or tenants concurrently mutate product data, the recommended audit-trail tuple is:

| Column | Purpose |
|---|---|
| `actor_team_id` | Team identifier responsible for the mutation (or equivalent multi-tenant actor) |
| `timestamp` (or `started_at`, `created_at`, etc.) | When the mutation occurred |
| `query_type` (or `operation_type`, `event_type`, etc.) | Semantic type of the operation |

### §B.2 — SMB single-user carve-out

For deployments that are **Single-User SMB by design** (i.e., the product runs for a single human user; multiple agent-team distinction is not modeled in the data layer), the audit-trail requirement above is satisfied by:

| Column | Purpose |
|---|---|
| `user_id` | Single-user actor identity proxy (when `actor_team_id` is structurally absent) |
| `timestamp` (or equivalent timestamp column) | When the mutation occurred |
| `query_type` (or equivalent semantic op type) | Semantic type of the operation |

**Rationale:** In an SMB single-user deployment, `user_id` IS the actor identity. The forensic-trace purpose of the audit-trail (who triggered this operation, when, what kind) is fully preserved. Mandating `actor_team_id` on a product table that has no multi-team concept would add a placeholder column without operational value.

### §B.3 — Migration guidance

Spokes whose product audit tables existed prior to this clarification (e.g., TikTrack `sync_log` with `query_type` + `started_at` + `user_id`):
- **NO migration required.** The existing schema satisfies §B.2.
- Spoke charter citations that read "per ADR034 audit trail" are now valid as voluntary adoption of §B.

Spokes designing NEW product audit tables under SMB context:
- Adopt §B.2 directly (3 columns: `user_id`, timestamp, `query_type`).
- Cite this addendum (`ADR034 R11 §B.2`) rather than ADR034 main body.

Spokes designing NEW product audit tables under multi-tenant context:
- Adopt §B.1.
- Use this addendum (`ADR034 R11 §B.1`) as a template; spoke architecture documents the multi-tenant model.

---

## §C — Effect on Codex EXT-CP2 VC-8 verdict (TikTrack R3)

Codex EXT-CP2 VC-8 verdict (`amendment_chain_principled: READY`, 2026-05-22, on `tiktrack:_COMMUNICATION/team_190/VERDICT_R3_TRADING_ACCOUNTS_EXT-CP2.md`) is **affirmed by this addendum**.

The amendment chain (cube-spec finding → R3 R.5 disposition as SMB semantics → R3 R.7 close → GCR filing → hub R11 resolution) IS principled. The chain rested on a misattributed citation (ADR034 main vs. R11), but the underlying engineering judgement — that SMB single-user deployments use `user_id` in lieu of `actor_team_id` — is sound and is now codified at the right level (hub) with the right scope (optional pattern for spoke product audit).

Codex did not need to verify ADR034 source text fidelity because Codex's VC-8 was scoped to amendment-chain logic, not source-citation fidelity. The retrospective correction lives at the hub level (this addendum), not at the spoke level (TikTrack R3 R.7 close stands).

---

## §D — Iron Rule alignment

This addendum does NOT modify Iron Rule #7 (DB-as-SSoT for hub-canonical data). It clarifies scope:

- Iron Rule #7 + ADR034 R1+R2: **binding on hub-canonical entities** (work_packages, projects, teams, deploy_log)
- Iron Rule #7 + ADR034 R11 §A: **does NOT extend to spoke product-domain audit tables**
- Iron Rule #7 + ADR034 R11 §B: **provides voluntary patterns** for spokes that wish to apply ADR034-style audit thinking to their own product data

`methodology/AOS_CONCEPT_AND_PRINCIPLES.md` Iron Rule #7 wording remains unchanged.

---

## §E — Precedent governance

This addendum sets the following precedents:

1. **Spokes may NOT invent "per ADR034" requirements on product-domain tables** without first filing a GCR to clarify scope (or to extend ADR034 with team_00 approval).
2. **External validation engines (e.g., Codex)** are not expected to verify source-citation fidelity beyond their stated VC scope; spoke-side spec authors retain responsibility for accurate hub canon citations.
3. **Hub clarifications via addenda** (this R11) are preferred over scope-creeping the original ADR text.
4. **Architectural misattributions surfaced via GCR** are treated as good-faith and resolved by the smallest principled change to hub canon, preserving prior validator verdicts where the underlying engineering judgement is sound.

---

## §F — Implementation

- **Hub canonical:** `governance/directives/ADR034_ADDENDUM_R11_AUDIT_SCOPE_CLARIFICATION_v1.0.0.md` (this file)
- **Spoke snapshot:** auto-generated by `scripts/aos_sync_all.sh` at `_aos/governance/directives/ADR034_ADDENDUM_R11_*.md` in each registered spoke (read-only per Iron Rule #11)
- **CHARTER alignment (TikTrack):** existing `PILOT_PROGRAM_CHARTER_v1.1.0_ADDENDUM.md` AC for `sync_log` stands as voluntary §B.2 adoption; no charter edit required. Spokes may optionally update their citations to read `per ADR034 R11 §B.2`.
- **Other addenda:** R10 (`ADR034_ADDENDUM_R10_HUB_NATIVE_WP_FILE_SSOT_v1.0.0.md`) is being authored separately under V4.3 milestone; R11 (this) is the SMB clarification.

---

## §G — Approval signature

| Role | Team | Sign-off |
|---|---|---|
| Principal | team_00 | Approved Option C in-session 2026-05-22 (triage §10 selection) |
| Chief Architect | team_100 | Authored this addendum |
| External validator (cross-engine, IR#1) | team_190 | Codex EXT-CP2 VC-8 PASS (2026-05-22) — affirmed by §C; no fresh validation cycle required for this scope-clarification addendum (no spoke product code change) |

---

*ADR034 ADDENDUM R11 | Audit-Trail Scope Clarification + Optional SMB Pattern | LOCKED 2026-05-22 | hub canon at `governance/directives/`*
