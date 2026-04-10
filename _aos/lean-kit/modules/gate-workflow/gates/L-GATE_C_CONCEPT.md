# L-GATE_C — Concept Gate (Track B only)

**When to run:** After L-GATE_E PASS. **Track B work packages only.**  
**Templates:** `../templates/LOD300_DESIGN_TEMPLATE.md`  
**Normative definitions:** `../../methodology/gate-model/LOD_STANDARD_v1.0.0.md`

## Checklist — ALL must be ✅

### LOD300 completeness
- [ ] LOD300 document exists and follows the LOD300 template
- [ ] All component interactions are documented
- [ ] All interface contracts are defined
- [ ] All open design questions are RESOLVED (none marked open)
- [ ] Consuming team (builder) has confirmed: "executable from this design"

### No implementation detail leakage
- [ ] LOD300 describes behavior, not code
- [ ] No specific function names, class names, or SQL schemas in LOD300

## Gate decision
- **PASS** → advance to L-GATE_S
- **FAIL** → return to architecture agent with findings list

## Iron Rule reminder
Track B exists because interfaces/behavior must be resolved before LOD400. Do not skip LOD300 on TRACK_B.
