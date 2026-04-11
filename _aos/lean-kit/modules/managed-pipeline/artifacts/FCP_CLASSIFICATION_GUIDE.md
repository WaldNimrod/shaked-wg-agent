# FCP Classification Guide — L2.5
# Finding Classification Protocol: decision tree for routing rejections and failures

---

## FCP DECISION TREE

```
A finding or rejection arrives
         │
         ▼
Is it canonical naming, wording, header, doc fix, or minor UI string?
  YES → FCP-1 (PWA fix)
  NO  ↓
         ▼
Is it a bounded issue in ONE team's scope, no API/DDL change, ≤2 files, ≤50 lines?
  YES → FCP-2 (targeted team fix)
  NO  ↓
         ▼
Does it require multiple teams or architectural re-design?
  YES → FCP-3 (full mandate regeneration)
  NO  ↓
         ▼
Is the LOD400 spec itself wrong or insufficient?
  YES → FCP-4 (spec failure — STOP, escalate)
```

---

## FCP-1 — PWA Fix (Pen-and-Whiteboard Authority)

**Definition:** Small, non-structural correction the Gateway Agent can apply directly.

**Scope:**
- Canonical naming corrections
- Documentation / comment fixes
- Header or metadata corrections
- Minor UI string wording (exact copy fix, not layout change)
- Single file, ≤20 lines

**Who fixes:** Gateway Agent (Team 10 analogue) — no team re-activation
**Re-entry point:** Re-validate from the phase that flagged the issue
**Logging:** Log in gate_history as `{type: FCP-1, files_changed: X}`

**Circuit breaker:** > 3 FCP-1 cycles on same issue → escalate to FCP-2

---

## FCP-2 — Targeted Team Fix

**Definition:** Bounded issue within one team's domain. Requires team re-activation but not full restart.

**Scope:**
- Single team responsible (e.g., backend only, or frontend only)
- No DDL changes, no API contract changes
- ≤2 files, ≤50 lines
- No cross-team dependency

**Who fixes:** Original implementing team (re-activated with targeted mandate)
**Re-entry point:** Phase 4D (QA) — re-run only affected ACs
**Logging:** Log in gate_history as `{type: FCP-2, team: team_XX, scope: "..."}`

---

## FCP-3 — Full Mandate Regeneration

**Definition:** Multi-team issue, architectural inconsistency, or scope failure. Requires Gateway Agent to rebuild mandates.

**Scope:**
- Multiple teams affected
- API contract change required
- Architectural misalignment with LOD400
- Scope drift identified
- Business logic error

**Who fixes:** Gateway Agent re-decomposes LOD400 → new mandates → Phase 4C full restart
**Re-entry point:** Phase 4C (Implementation restart)
**Logging:** Log in gate_history as `{type: FCP-3, root_cause: "..."}`

**Circuit breaker:**
- 1st FCP-3 → Nimrod notified (non-blocking, continues)
- 2nd FCP-3 → Nimrod notified + must acknowledge before restart
- 3rd FCP-3 → FULL STOP. Mandatory Nimrod review with complete diff.

---

## FCP-4 — Spec Failure (LOD400 Defect)

**Definition:** The LOD400 specification is wrong or insufficient. Implementation correctly followed the spec, but the spec itself has a defect.

**Triggers:**
- Acceptance criteria cannot be tested (too vague even at LOD400)
- Technical impossibility discovered during implementation
- LOD400 contradicts LOD300 (spec regression)
- Missing requirement discovered (not scope drift — genuine omission)

**Who fixes:** Back to Phase 4A — Spec Agent rewrites LOD400 with gap explicitly documented
**Re-entry point:** Phase 4A
**Nimrod notification:** MANDATORY AND IMMEDIATE. Do not restart without acknowledgment.
**Logging:** `{type: FCP-4, spec_gap: "...", nimrod_notified: true}`

**Circuit breaker:** ANY FCP-4 → STOP immediately. No exceptions.

---

## PHASE 5 REJECTION ROUTING

When Nimrod rejects at Phase 5 Gate:

```
Nimrod's feedback
      │
      ▼
Orchestrator classifies:

"Small visual issue / copy error / minor layout" → FCP-1 → fix in dev env → re-present
"One component wrong / single feature broken" → FCP-2 → re-activate team → re-QA specific ACs
"Multiple things wrong / flow broken / wrong behavior" → FCP-3 → full Phase 4C restart
"This is not what was specified / spec was wrong" → FCP-4 → Phase 4A restart + STOP
```

**Key principle:** Small interface bugs at Phase 5 do NOT trigger full loop restart.
FCP-1 path allows a simple fix agent to correct within the dev environment as part
of the approval process itself — no Phase 4C restart required.

---

## CIRCUIT BREAKER SUMMARY

| Condition | Action |
|-----------|--------|
| FCP-1 same issue > 3 cycles | Escalate to FCP-2 |
| FCP-2 same issue > 2 cycles | Escalate to FCP-3 |
| FCP-3 first occurrence | Nimrod notified, continue |
| FCP-3 second occurrence | Nimrod must acknowledge |
| FCP-3 third occurrence | FULL STOP |
| FCP-4 any occurrence | FULL STOP, immediate escalation |
