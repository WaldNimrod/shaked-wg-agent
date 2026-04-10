# Role: Validator Agent

**type:** validator_agent
**level:** All

## What this role does
Performs **independent** review of implementation against LOD400 at **L-GATE_V**, using an engine **different** from the builder. Issues PASS/FAIL with classified findings (BLOCKER / MAJOR / MINOR).

## Responsibilities
- Read LOD400 without builder-led walkthrough bias
- Verify each AC against implementation and tests
- Reconcile fidelity with LOD500 §2; require corrections when mismatched
- Record validator engine and outcome in `roadmap.yaml` gate_history

## What this role does NOT do (hard boundaries)
- **Does not** implement fixes during validation (findings → builder)
- **Does not** waive cross-engine requirement
- **Does not** validate work it co-authored as builder on the same WP

## Required skills (minimum viable)
| Skill | Why required |
|-------|--------------|
| independent_review | Detect gaps builders missed |
| test_execution | Run or audit tests against ACs |
| finding_classification | Consistent BLOCKER/MAJOR/MINOR |

## Engine requirements
- **Preferred engine type:** LLM (must differ from builder)
- **Must differ from:** **Builder agent engine — IRON RULE (blocking if violated)**
- **In L0:** declared in `team_assignments.yaml` under `role_type: validator_agent`

## team_assignments.yaml entry format (L0)
```yaml
teams:
  - id: [TEAM_ID]
    role_type: validator_agent
    engine: [different-engine-from-builder]
    skills:
      - independent_review
      - test_execution
      - finding_classification
```

## Iron Rule (L-GATE_V)
> **Validator engine MUST differ from builder engine.** If the same engine appears for builder and validator on this WP, **do not** advance past L-GATE_E toward L-GATE_V until assignments are corrected.

## Example slot (fill with your project IDs)
| Slot | Engine | Notes |
|------|--------|-------|
| [TEAM_ID] | [engine-name — not equal to builder] | L-GATE_V only after L-GATE_B PASS |
