# L-GATE_B — Build + QA Gate

**When to run:** After L-GATE_S PASS. Builder has completed implementation.  
**This gate merges:** build complete + same-engine QA (builder self-review).

**Templates:** `../templates/LOD500_ASBUILT_TEMPLATE.md`

## Part A — Build completeness

- [ ] All LOD400 acceptance criteria have been attempted (none skipped)
- [ ] All LOD400 components are implemented
- [ ] No known blocking bugs
- [ ] LOD500 as-built draft exists (can be revised before L-GATE_V)

## Part B — Same-engine QA (builder's self-review)

- [ ] Builder has reviewed own output against every LOD400 AC
- [ ] Each AC marked: ✅ MATCH / ⚠️ DEVIATION / ❌ MISSING in LOD500 §2
- [ ] Any deviation: LOD400 correction issued (new version) or deviation documented with justification
- [ ] Unit tests run: N/N PASS
- [ ] Integration tests run (if applicable): N/N PASS

## Part C — Deviation handling

If any AC is marked DEVIATION or MISSING:
- [ ] Is the deviation approved by Architecture Agent? If not → spec correction required
- [ ] LOD400 updated to reflect approved deviations
- [ ] LOD500 §3 deviations table is complete

## Gate decision
- **PASS** → advance to L-GATE_V (cross-engine validation)
- **FAIL** → builder corrects issues; re-run this gate; document cycle count

## Critical: what does NOT happen here
- **Cross-engine validation does NOT happen at L-GATE_B**
- L-GATE_B is self-assessment by the **same builder engine**
- The independent validator is **RESERVED for L-GATE_V** — never substitute

## Iron Rule
L-GATE_V is **never** merged into L-GATE_B. Validator engine **must** differ from builder engine at L-GATE_V.
