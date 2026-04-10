# L-GATE_S — Spec + Authorization Gate

**When to run:** After L-GATE_E PASS (Track A) or L-GATE_C PASS (Track B).  
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
- **PASS** → advance to L-GATE_B; builder is authorized to begin
- **FAIL** → return to architecture agent for spec revision; record blocking findings

## roadmap.yaml update on L-GATE_S PASS
```yaml
    lod_status: LOD400_APPROVED
    current_lean_gate: L-GATE_B
    gate_history:
      - gate: L-GATE_S
        result: PASS
        date: [YYYY-MM-DD]
        approved_by: [TEAM_ID]
```
