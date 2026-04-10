---
lod_target: LOD500
lod_status: DRAFT
track: A  # or B
authoring_team: [TEAM_ID — implementing team]
consuming_team: [TEAM_ID — documentation/validation team]
date: [YYYY-MM-DD]
version: v1.0.0
supersedes: null
fidelity: FULL_MATCH  # FULL_MATCH | DEVIATIONS_DOCUMENTED | PARTIAL
verifying_team: [TEAM_ID — must differ from authoring_team]
spec_ref: [path/to/LOD400_spec.md]
---

# [FEATURE NAME] — LOD500 As-Built Record

**work_package_id:** [S00X-P00X-WP00X]
**spec_ref:** [path/to/LOD400_spec.md v1.X.X]
**gate:** L-GATE_V
**fidelity:** [FULL_MATCH / DEVIATIONS_DOCUMENTED / PARTIAL]

## 1. What was built
[Summary of what was implemented. 2-4 sentences. Matches LOD400 scope.]

## 2. Fidelity record
[Compare against each LOD400 AC:]

| AC | LOD400 requirement | As-built result | Fidelity |
|----|-------------------|----------------|---------|
| AC-01 | [requirement] | [what was built] | ✅ MATCH / ⚠️ DEVIATION / ❌ MISSING |
| AC-02 | ... | ... | ... |

## 3. Deviations from spec (if any)
[For each deviation: what changed, why, and whether a spec update (LOD400 vX.Y) was issued.]

| Deviation | Reason | Spec updated? |
|---------|--------|--------------|
| [deviation] | [reason] | YES (LOD400 v1.1) / NO (approved variance) |

## 4. Test evidence
- Unit tests: [N] tests, [N] PASS, [N] FAIL
- Integration tests: [N] tests, [N] PASS, [N] FAIL
- Cross-engine validation: [Team ID] | [date] | [result]

## 5. Files changed
| File | Change type | Notes |
|------|------------|-------|
| [path] | ADD/MODIFY/DELETE | [notes] |

## 6. Verifying team sign-off
> I confirm this as-built record is accurate. Fidelity classification above is correct.
> All deviations are documented. Evidence is linked.
> **Signature:** [TEAM_ID — different from authoring team] | [date]

---

## Cross-Engine Validation — Iron Rule

Documents at LOD400+ require cross-engine validation at L-GATE_V.
**The validator engine MUST differ from the builder engine — IRON RULE.**
No exception. No waiver. See `gates/L-GATE_V_VALIDATE_AND_LOCK.md`.
