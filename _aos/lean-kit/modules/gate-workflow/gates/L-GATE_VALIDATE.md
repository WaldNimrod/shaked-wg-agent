# L-GATE_VALIDATE — Validate + Lock Gate

**When to run:** After L-GATE_BUILD PASS.

**IRON RULE: This gate is never compressed, never merged, never optional.**

**Validator engine MUST differ from builder engine.**  
If `assigned_validator` uses the **same** engine as `assigned_builder`, **STOP** — correct `team_assignments.yaml` before proceeding.

## Precondition — Documentation completeness (BLOCKING)

Before cross-engine validation begins, the validator checks:

- [ ] LOD500 §1b documentation layers table is present
- [ ] All applicable layers (L1–L4) are marked ✅ Done or ➖ N/A with justification
- [ ] No layer is blank or left as placeholder text

**If precondition is not met → status = BLOCKED** (not FAIL).  
Return LOD500 to the builder team. L-GATE_VALIDATE does not start until all documentation layers are complete.  
BLOCKED does not count as a gate cycle failure — it is a pre-entry check.

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

## Part C.5 — Documentation quality review (PAC-DOC)

Validator independently reviews the documentation layers declared in LOD500 §1b:

- [ ] **L2 Architecture docs** (if applicable): accurate, complete, reflects as-built design
- [ ] **L3 API/Interface docs** (if applicable): contracts match actual implementation; no phantom endpoints or stale interfaces
- [ ] **L1 + L4** (if applicable): spot-check for correctness; no obviously missing user-facing or inline docs

**PAC-DOC verdict:**
- **ACCEPTED** — documentation is accurate and complete for all applicable layers
- **REJECTED** — one or more layers are inaccurate, incomplete, or missing content that is clearly required

If PAC-DOC = REJECTED → treated as a **BLOCKER** (same weight as a functional blocker).  
Document each rejection reason. Builder must fix and resubmit; cycle count increments.

## Part D — Documentation lock

- [ ] LOD500 `lod_status` = LOCKED
- [ ] LOD500 §6 verifying team sign-off is complete
- [ ] `roadmap.yaml` updated: WP `status` = COMPLETE, `lod_status` = LOD500_LOCKED

## Gate decision
- **PASS (0 blockers + PAC-DOC ACCEPTED)** → WP is COMPLETE; lock LOD500; update `roadmap.yaml`
- **CONDITIONAL PASS** → only if: 0 blockers + PAC-DOC ACCEPTED + minor findings documented
- **FAIL** → any functional blocker, unresolved major finding, or PAC-DOC REJECTED; return to builder; cycle counted
- **BLOCKED** → precondition not met (§1b incomplete); not a cycle failure; return to builder for documentation

## Human orchestrator note
The System Designer **routes** validation and removes blockers — the human **does not** replace the validator engine. Human approval at L-GATE_VALIDATE does **not** satisfy cross-engine validation.

### Pre-Conditions (V318+)
Before routing to Team 190 final validation:
```bash
./lean-kit/modules/validation-quality/scripts/validate_gates.sh --wp <wp-id>
./lean-kit/modules/validation-quality/scripts/validate_verdicts.sh --wp <wp-id>
```
Both must exit 0. If either fails, resolve before routing.

## roadmap.yaml update on L-GATE_VALIDATE PASS
```yaml
    status: COMPLETE
    lod_status: LOD500_LOCKED
    current_lean_gate: COMPLETE
    gate_history:
      - gate: L-GATE_VALIDATE
        result: PASS
        date: [YYYY-MM-DD]
        validator: [TEAM_ID]
        validator_engine: [engine-name]
        builder_engine: [engine-name]
        fidelity: FULL_MATCH
```

## Post-Gate Actions (after L-GATE_VALIDATE PASS)

After a WP is closed (status=COMPLETE, LOD500_LOCKED), the following post-gate actions are **mandatory**:

### 1. Archive communication artifacts (Iron Rule #15)
- Move all files from `_COMMUNICATION/team_*/[WP-ID]/` to `_archive/[WP-ID]/`
- Preserve subdirectory structure within the WP archive
- Create `ARCHIVE_MANIFEST.md` in `_archive/[WP-ID]/` listing: source paths, date, file count, archiving team

### 2. Misplaced artifact scan (Iron Rule #12 enforcement)
- Scan all `_COMMUNICATION/team_*/` root directories for files referencing the closed WP ID
- Detect routing prompts, verdicts, mandates, and handoffs incorrectly placed at team root instead of WP subdirectories
- Move any misplaced WP-scoped artifacts to `_archive/[WP-ID]/`
- Log all moves in the ARCHIVE_MANIFEST.md

### 3. Roadmap verification
- Confirm `roadmap.yaml` has: status=COMPLETE, lod_status=LOD500_LOCKED, full gate_history
- Confirm LOD500 as-built record exists in `_aos/work_packages/[WP-ID]/`

### 4. Governance sync verification
- Run `validate_aos.sh` — must return 0
- Verify Check 15 passes (no stale artifacts in `_COMMUNICATION/` for completed WPs)

**Executor:** Team 191 (Git, Archive & File Governance) under Team 00 mandate.
**Timing:** Within the same session as L-GATE_VALIDATE closure, or as first action in next session.
