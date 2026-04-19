# L-GATE_SPEC — Spec + Authorization Gate

**When to run:** After L-GATE_ELIGIBILITY PASS (Track A) or L-GATE_CONCEPT PASS (Track B).  
**This gate merges:** L0 equivalents of spec approval + execution authorization (see LOD Standard §Lean gate mapping).

**Templates:** `../templates/LOD400_SPEC_TEMPLATE.md`

## Part A — Spec review (LOD400 completeness)

- [ ] LOD400 document exists and follows the LOD400 template
- [ ] All acceptance criteria are **TESTABLE** (not vague)
- [ ] All components listed in LOD200 §4 are covered in LOD400
- [ ] Out-of-scope is explicit — no ambiguity about what is NOT built
- [ ] Data model changes are specified with exact DDL or ORM schema
- [ ] API changes are specified with exact contract (endpoint, method, request, response)
- [ ] Test requirements are specified (who tests what)
- [ ] LOD400 frontmatter is complete: all required fields present

## Part B — Consuming team sign-off

- [ ] Builder agent (consuming team) has reviewed the spec
- [ ] Builder agent has confirmed: "This spec is executable. I have no blocking questions."
- [ ] Builder agent signature is in LOD400 §8

## Part C — Authorization

- [ ] Architecture agent confirms: "This spec is approved for execution"
- [ ] `roadmap.yaml` updated: `lod_status` = LOD400_APPROVED, `assigned_builder` declared

## Gate decision
- **PASS** → advance to L-GATE_BUILD; builder is authorized to begin
- **FAIL** → return to architecture agent for spec revision; record blocking findings

### Pre-Condition (V318+)
Before routing to Team 190, Team 100 MUST run:
```bash
./lean-kit/modules/validation-quality/scripts/validate_lod.sh <wp-dir>
```
Exit code must be 0. If exit 1, return to developer — do NOT route to Team 190.

## roadmap.yaml update on L-GATE_SPEC PASS
```yaml
    lod_status: LOD400_APPROVED
    current_lean_gate: L-GATE_BUILD
    gate_history:
      - gate: L-GATE_SPEC
        result: PASS
        date: [YYYY-MM-DD]
        approved_by: [TEAM_ID]
```
