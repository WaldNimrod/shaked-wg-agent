---
id: ADR042
title: WP Closure Protocol — Mandatory 3-Step Sequence After L-GATE_VALIDATE PASS
status: LOCKED
version: v1.0.0
date: 2026-04-19
authors: [team_100]
scope: AOS-hub
---

# ADR042 — WP Closure Protocol v1.0.0

## Context

Three mandatory closure actions are defined across multiple AOS methodology documents:

1. **Archive** — Iron Rule #15 + GATE_MANDATE_CANON Signal B.0 mandate Team 191 archival
2. **DB state transition** — Iron Rule #7 / ADR034 mandates API-only mutations when DB online
3. **Multi-engine propagation** — team_100 multi-engine completeness rule mandates `aos_sync_all.sh` after every `core/governance/` edit

In practice, WPs were being declared COMPLETE without all three steps executing. The root cause: each rule exists in isolation with no single team_100 closure checklist that names all three steps in order as a unit.

## Decision

A WP is **NOT closed** until all three steps below are complete. L-GATE_VALIDATE PASS by Team 190 is a necessary but not sufficient condition for WP closure.

**LOD500_LOCKED** is the terminal state. It is only reached when:
- `_archive/{WP_ID}/ARCHIVE_MANIFEST.md` exists (Team 191 archival complete)
- DB `lod_status = LOD500_LOCKED` (API-updated, not hand-edited)
- `validate_aos.sh` Check 15 (archive compliance) passes

## Mandatory Closure Sequence (team_100 only)

When Team 190 issues an L-GATE_VALIDATE PASS verdict, team_100 MUST execute all three steps before the WP is considered closed. **Partial execution = WP is NOT closed.**

| Step | Trigger | Action | Reference |
|------|---------|--------|-----------|
| **1. Archive mandate** | Immediately on PASS receipt | `/AOS_gate-mandate` Signal B.0 → issue Team 191 archival mandate; do NOT proceed to Step 2 until Team 191 confirms ARCHIVE_MANIFEST.md written | GATE_MANDATE_CANON v1.6.0 Signal B.0; Iron Rule #15; `lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md` v1.1.0 |
| **2. DB state transition** | After Team 191 archival complete | `POST /api/work-packages/{wp_id}` body `{"lod_status": "LOD500_LOCKED", "status": "COMPLETE"}` — NEVER edit `_aos/roadmap.yaml` directly for canonical fields when DB online | Iron Rule #7 / ADR034 |
| **3. Multi-engine propagation** | If `core/governance/` was modified during the WP lifecycle | `AOS_ACTOR_TEAM_ID=team_100 bash scripts/aos_sync_all.sh --all` | team_100 multi-engine completeness rule (team_100.md) |
| **4. Command shipping** | If WP added/modified `.claude/commands/AOS_*.md` | Run full checklist: `lean-kit/modules/project-governance/docs/WP_COMMAND_SHIPPING_CHECKLIST_v1.0.0.md` — includes `git push`, team_99 governance update, MSG to server | ADR041 / Iron Rule #13 |

## Ordering constraint

Steps 1 → 2 → 3 are ordered. Step 1 (archive) must complete before Step 2 (DB lock), because the archive manifest is written by Team 191 and confirms the artifact set is stable. Step 3 (propagation) is independent of Step 2 but MUST complete before the session closes.

## Exemptions

- **Step 3 only:** If `core/governance/` was NOT modified during the WP, Step 3 is skipped. Team_100 MUST explicitly verify before skipping.
- **Step 4 only:** If no `.claude/commands/AOS_*.md` file was added or modified during the WP, Step 4 is skipped.
- **Offline mode (ADR034 R8):** If DB is offline during closure, Step 2 is deferred to a PENDING_DB_SYNC.yaml entry on a named branch. Steps 1 and 3 are not deferred.

## Consequences

- WPs closed without full 3-step execution are retroactively non-compliant and must be remediated.
- `validate_aos.sh` Check 15 (archive compliance) is the automated enforcement gate.
- Any future validator (Team 90 / Team 190) finding a WP with status=COMPLETE and missing ARCHIVE_MANIFEST.md MUST raise a BLOCK.

## Supersedes

This ADR defines no new rules — it consolidates existing rules (Iron Rule #7, Iron Rule #15, team_100 multi-engine completeness rule, GATE_MANDATE_CANON Signal B.0) into a single ordered checklist. No prior ADR is superseded; this ADR is additive.

## References

- `lean-kit/modules/validation-quality/docs/AOS_GATE_MANDATE_CANON_v1.0.0.md` — Signal B.0
- `lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md` — archive runbook v1.1.0
- `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` — Iron Rule #7
- `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` — Iron Rule #15 (archive compliance)
- `core/governance/team_100.md` — multi-engine completeness rule
