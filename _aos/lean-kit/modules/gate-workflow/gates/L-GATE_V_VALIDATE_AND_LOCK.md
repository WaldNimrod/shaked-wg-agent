# L-GATE_V — Validate + Lock Gate

**When to run:** After L-GATE_B PASS.

**IRON RULE: This gate is never compressed, never merged, never optional.**

**Validator engine MUST differ from builder engine.**  
If `assigned_validator` uses the **same** engine as `assigned_builder`, **STOP** — correct `team_assignments.yaml` before proceeding.

## Part A — Validator independence verification

- [ ] Validator is declared in `team_assignments.yaml`
- [ ] **Validator engine ≠ builder engine** (**IRON RULE** — blocking if violated)
- [ ] Validator has NOT been involved in building or spec-writing for this WP

## Part B — Independent validation

Validator performs independently (no discussion with builder beforehand):

- [ ] Validator reads LOD400 spec independently
- [ ] Validator reviews builder output (code, config, docs) against each LOD400 AC
- [ ] Validator completes their own fidelity assessment (independent of LOD500 draft)
- [ ] Validator produces findings list: BLOCKER / MAJOR / MINOR

## Part C — Fidelity reconciliation

- [ ] LOD500 §2 fidelity table matches validator's independent assessment
- [ ] Any discrepancy between builder's LOD500 and validator findings: resolved
- [ ] Final fidelity classification agreed: FULL_MATCH / DEVIATIONS_DOCUMENTED

## Part D — Documentation lock

- [ ] LOD500 `lod_status` = LOCKED
- [ ] LOD500 §6 verifying team sign-off is complete
- [ ] `roadmap.yaml` updated: WP `status` = COMPLETE, `lod_status` = LOD500_LOCKED

## Gate decision
- **PASS (0 blockers)** → WP is COMPLETE; lock LOD500; update `roadmap.yaml`
- **CONDITIONAL PASS** → only if: 0 blockers + minor findings documented
- **FAIL** → any blocker or unresolved major finding; return to builder; cycle counted

## Human orchestrator note
The System Designer **routes** validation and removes blockers — the human **does not** replace the validator engine. Human approval at L-GATE_V does **not** satisfy cross-engine validation.

## roadmap.yaml update on L-GATE_V PASS
```yaml
    status: COMPLETE
    lod_status: LOD500_LOCKED
    current_lean_gate: COMPLETE
    gate_history:
      - gate: L-GATE_V
        result: PASS
        date: [YYYY-MM-DD]
        validator: [TEAM_ID]
        validator_engine: [engine-name]
        builder_engine: [engine-name]
        fidelity: FULL_MATCH
```
