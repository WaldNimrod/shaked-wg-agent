# L-GATE_E — Eligibility Gate

**When to run:** Before any work begins. This is the intake filter.

**Templates:** See `../templates/LOD100_IDEA_TEMPLATE.md` for LOD100 shape. Normative definitions: `../../methodology/gate-model/LOD_STANDARD_v1.0.0.md` (or `../../methodology/lod-standard/TEAM_100_LOD_STANDARD_v0.3.md`).

## Checklist — ALL must be ✅ before proceeding

### Readiness
- [ ] WP has a clear, written LOD100 (idea/intent) — not just a verbal description
- [ ] WP is assigned to a program and stage in `roadmap.yaml`
- [ ] WP has no unresolved dependency blocks (all predecessors are COMPLETE in `roadmap.yaml` — i.e. prior WPs reached L-GATE_V PASS / locked — or not required)

### Team readiness
- [ ] Builder agent is identified and available (declared in `team_assignments.yaml`)
- [ ] Validator agent is identified (**different engine than builder**) — **IRON RULE**
- [ ] Architecture agent (spec author) is identified

### Track assignment
- [ ] Track decision made: TRACK_A or TRACK_B
  - If TRACK_B: LOD300 is planned in the sequence after LOD200

## Gate decision
- **PASS** → advance to L-GATE_S (Track A) or L-GATE_C (Track B)
- **FAIL** → document blocking reason in `roadmap.yaml`; do not proceed

## roadmap.yaml update on L-GATE_E PASS
```yaml
work_packages:
  - id: [WP_ID]
    current_lean_gate: L-GATE_S  # or L-GATE_C for Track B
    gate_history:
      - gate: L-GATE_E
        result: PASS
        date: [YYYY-MM-DD]
        notes: "[any notes]"
```
