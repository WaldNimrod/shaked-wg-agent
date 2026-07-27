# ADR045 — Team 110 Autonomous Execution Authority

**Type:** Architecture Decision Record
**Status:** LOCKED
**Date:** 2026-05-23
**Authority:** Team 00 (principal) + Team 100 (chief architect)
**Work Package:** AOS-V4.3-WP-TEAM110-EXEC-AUTHORITY
**Trigger:** team_00 in-session direction 2026-05-23 — proven in practice (WP AOS-V4.3-WP-ADR034-R10-HUB-NATIVE-SSOT full orchestration)

---

## Decision

When team_110 receives a mandate that contains the field `execution_authority: full`,
it operates as the **primary WP executor** for the full mandate lifecycle — from
implementation through gate chain through closure. No mid-execution approvals from
team_100 are required. team_100 receives a single COMPLETION_REPORT upon LOD500_LOCKED.

---

## Context

team_110 (AOS Domain Architect) was defined as an approval-only role (GATE_2/2.1).
In practice, team_110 has full architectural understanding of a WP from spec review
and is best positioned to orchestrate its execution. The existing model required every
sub-mandate (team_90, team_190, team_191) and every closure action to route through
team_100, adding latency and context-switching without governance value.

On 2026-05-23, WP AOS-V4.3-WP-ADR034-R10-HUB-NATIVE-SSOT was executed in full by
team_110 (implementation + team_90 L-GATE_BUILD + team_190 L-GATE_VALIDATE + ADR042
3-step closure) with team_00 direction. The model worked. This ADR codifies it.

---

## Ruling

### R1 — Execution Mandate Trigger

A mandate is an "execution mandate" when it contains:
```yaml
execution_authority: full
```
Without this field (or with `execution_authority: approval_only`), team_110 operates
in its existing GATE_2 approval-only mode. No existing mandate is affected.

### R2 — Expanded Authority in Execution Mandate Mode

When team_110 holds an active execution mandate:

1. **Sub-agent mandating:** team_110 MAY independently issue mandates to:
   - team_90 (L-GATE_BUILD validation)
   - team_190 (L-GATE_VALIDATE constitutional review)
   - team_191 (archive / Signal B.0 closure)
   Without routing through team_100.

2. **API mutations (WP lifecycle only):** team_110 MAY call
   `POST /api/work-packages/{wp_id}` for fields:
   `status`, `lod_status`, `current_lean_gate` — and no others.
   Iron Rule #7 / ADR034 R2 applies; direct YAML edits to canonical fields remain forbidden.

3. **Closure artifacts:** team_110 MAY write directly:
   - `_archive/{WP_ID}/ARCHIVE_MANIFEST.md`
   - `_aos/work_packages/{WP_ID}/metadata.yaml` (lifecycle fields only)
   - `_aos/roadmap.yaml` (WP entry update to COMPLETE/LOD500_LOCKED)

4. **Inter-team routing:** team_110 MAY deliver mandate and verdict artifacts to
   `_COMMUNICATION/team_90/`, `_COMMUNICATION/team_190/`, `_COMMUNICATION/team_191/`
   per Directory Canon Part 5 Inbox delivery exception.

### R3 — What Does NOT Change

1. **Iron Rule #1 (cross-engine validation):** team_110 MUST NOT validate its own
   implementation. team_90 and team_190 are independent validators — team_110 delegates
   to them, never substitutes for them.

2. **team_190 constitutional independence:** team_190 remains the sole L-GATE_VALIDATE
   owner. team_110 routes to them; the mandate must not constrain their verdict.

3. **team_00 override authority:** Absolute at all times. team_00 may redirect, pause,
   or assume any step regardless of active execution mandate.

4. **team_100 fallback:** team_100 resumes ownership of WP closure if:
   (a) team_110 session ends without LOD500_LOCKED (mandate abandoned), or
   (b) team_00 issues an explicit override instruction.

### R4 — Completion Reporting

Upon LOD500_LOCKED, team_110 MUST file a COMPLETION_REPORT:
- Path: `_COMMUNICATION/team_110/{WP_ID}/COMPLETION_REPORT_{WP_ID}_v1.0.0.md`
- Recipients: team_00 + team_100
- Contents: gate chain summary, verdict artifact paths, ADR042 3-step audit,
  minor findings disposition, deferred items.

This report replaces all mid-execution check-ins. No interim approvals are needed.

### Scope

| Mandate field | Mode | Closure owner | team_100 role |
|---|---|---|---|
| `execution_authority: full` | Autonomous execution | team_110 | receives COMPLETION_REPORT only |
| `execution_authority: approval_only` (default) | GATE_2 approval only | team_100 | full orchestrator (existing model) |
| `execution_authority: none` | Excluded | team_100 | full orchestrator |

---

## Rationale

1. **Proven in practice:** The WP AOS-V4.3-WP-ADR034-R10-HUB-NATIVE-SSOT execution
   demonstrated the pattern works with zero team_100 mid-execution involvement.
2. **No constitutional risk:** Iron Rule #1 (cross-engine) is preserved — team_110
   delegates to independent validators, never self-validates.
3. **Backward compatible:** Existing mandates without `execution_authority: full` are
   unaffected. team_100 coordination model remains the default.
4. **Parallel to R9/R10:** Same "explicit carve-out for documented exception" pattern.

---

## Cross-References

| Document | Relevance |
|---|---|
| `governance/directives/ADR034_ADDENDUM_R9_L2_SPOKE_ROADMAP_FILE_SSOT_v1.0.0.md` | Precedent: explicit exception pattern |
| `governance/directives/ADR042_WP_CLOSURE_PROTOCOL_v1.0.0.md` | Closure steps team_110 now owns in execution mode |
| `lean-kit/modules/validation-quality/docs/AOS_GATE_MANDATE_CANON_v1.0.0.md` | Signal B.0 (archive); team_110 routes independently in execution mode |
| `core/governance/team_110.md` | Primary contract — amended by this ADR |
| `core/governance/team_100.md` | Amended — delegation clause added to Closure Protocol |
| `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` Part 5 | Write authority table — team_110 row updated |

---

**log_entry | ADR045 | LOCKED | 2026-05-23 | team_110 autonomous execution authority — execution_authority: full trigger; team_100 fallback preserved; Iron Rule #1 intact**
