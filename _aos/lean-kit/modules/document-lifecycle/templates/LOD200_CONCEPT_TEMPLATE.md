---
lod_target: LOD200
lod_status: DRAFT
track: A  # or B — determines whether LOD300 is required next
authoring_team: [TEAM_ID]
consuming_team: [TEAM_ID]
date: [YYYY-MM-DD]
version: v1.0.0
supersedes: null
---

# [FEATURE/PROGRAM NAME] — LOD200 Concept

**work_package_id:** [S00X-P00X-WP00X]
**domain:** [domain name]
**track:** [A — direct to LOD400 / B — requires LOD300 first]
**approved_by:** [TEAM_ID]
**approved_at:** [YYYY-MM-DD]

## 1. Problem statement
[What specific problem does this solve? 2-4 sentences. User/system perspective.]

## 2. Proposed solution (concept only)
[High-level approach. Not implementation details. What the system will do, not how.]

## 3. Scope
### 3.1 In scope
- [item]

### 3.2 Out of scope (explicit)
- [item]

## 4. Affected components
| Component | Nature of change |
|-----------|-----------------|
| [name] | [add/modify/none] |

## 5. Dependencies
- [dependency 1: what, why]

## 6. Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| [risk] | LOW/MED/HIGH | LOW/MED/HIGH | [mitigation] |

## 7. Success criteria (LOD200 level)
- [ ] [criterion 1]
- [ ] [criterion 2]

## 8. Track decision
- **Track A** (LOD200 → LOD400 direct): choose if all criteria met:
  - [ ] Single component or pattern-following
  - [ ] No new state machine or async coordination
  - [ ] No new persisted data model
  - [ ] Single team execution
- **Track B** (LOD200 → LOD300 → LOD400): choose if ANY:
  - [ ] 2+ backend systems or APIs
  - [ ] New or modified state machine
  - [ ] New persisted data model (schema changes)
  - [ ] Multiple teams in build sequence
  - [ ] Cannot determine component interfaces without resolving behavior

**Decision:** TRACK_[A/B]

## 9. Gate approval record
| Gate | Approver | Date | Status |
|------|---------|------|--------|
| L-GATE_S (spec+auth) | [TEAM_ID] | [date] | PENDING |

> **Iron Rule:** L-GATE_V validation MUST use a different engine than the builder. See `gates/L-GATE_V_VALIDATE_AND_LOCK.md`.
