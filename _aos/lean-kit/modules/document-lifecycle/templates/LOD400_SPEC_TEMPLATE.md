---
lod_target: LOD400
lod_status: DRAFT
track: A  # or B
authoring_team: [TEAM_ID]
consuming_team: [TEAM_ID]
date: [YYYY-MM-DD]
version: v1.0.0
supersedes: null
---

# [FEATURE NAME] — LOD400 Implementation Spec

**work_package_id:** [S00X-P00X-WP00X]
**parent_lod200:** [path]
**parent_lod300:** [path or N/A — Track A only]
**approved_by:** [TEAM_ID — consuming team sign-off]
**approved_at:** [YYYY-MM-DD]

## 1. Scope reminder
[One paragraph: what this WP builds. Taken from LOD200 §2.]

## 2. Technical specification

### 2.1 [Component/Layer name]
**What to implement:**
[Specific, unambiguous instructions. Use numbered lists for sequential steps.]

**Acceptance criteria:**
- [ ] AC-01: [testable criterion]
- [ ] AC-02: [testable criterion]

### 2.2 [Next component]
[Repeat as needed.]

## 3. Data model changes (if any)
```sql
-- Exact DDL or ORM model changes required
```

## 4. API contract changes (if any)
| Endpoint | Method | Request | Response | Notes |
|---------|--------|---------|----------|-------|
| [path] | GET/POST/... | [schema] | [schema] | [notes] |

## 5. Error handling requirements
| Error case | Expected behavior |
|-----------|-------------------|
| [case] | [behavior] |

## 6. Out of scope (explicit)
- [item] — NOT included in this WP

## 7. Test requirements
[What must be tested? By which team?]
- Unit: [scope]
- Integration: [scope]
- Cross-engine validation: [scope — required at L-GATE_V]

## 8. Consuming team sign-off
> I confirm this spec is executable and unambiguous. All open questions are resolved.
> **Signature:** [TEAM_ID] | [date]

---

## Cross-Engine Validation — Iron Rule

Documents at LOD400+ require cross-engine validation at L-GATE_V.
**The validator engine MUST differ from the builder engine — IRON RULE.**
No exception. No waiver. See `gates/L-GATE_V_VALIDATE_AND_LOCK.md`.
