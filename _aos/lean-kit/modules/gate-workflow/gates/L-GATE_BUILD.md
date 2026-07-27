# L-GATE_BUILD — Build + QA Gate

**When to run:** After L-GATE_SPEC PASS. Builder has completed implementation.  
**This gate merges:** build complete + same-engine QA (builder self-review).

**Templates:** `../templates/LOD500_ASBUILT_TEMPLATE.md`

## Part A — Build completeness

- [ ] All LOD400 acceptance criteria have been attempted (none skipped)
- [ ] All LOD400 components are implemented
- [ ] No known blocking bugs
- [ ] LOD500 §1b documentation layers complete: all applicable layers marked ✅ Done or ➖ N/A with justification
- [ ] LOD500 as-built record is FULL (not draft) — ready for cross-engine review

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
- **PASS** → advance to L-GATE_VALIDATE (cross-engine validation)
- **FAIL** → builder corrects issues; re-run this gate; document cycle count

## Critical: what does NOT happen here
- **Cross-engine validation does NOT happen at L-GATE_BUILD**
- L-GATE_BUILD is self-assessment by the **same builder engine**
- The independent validator is **RESERVED for L-GATE_VALIDATE** — never substitute

### Team 50 Pre-Flight (V318+)
Run before starting QA:
```bash
./lean-kit/modules/validation-quality/scripts/validate_lod.sh <wp-dir>
```
After QA verdict filed, Team 100 runs:
```bash
./lean-kit/modules/validation-quality/scripts/validate_verdicts.sh --team team_50 --wp <wp-id>
```

## Iron Rule
L-GATE_VALIDATE is **never** merged into L-GATE_BUILD. Validator engine **must** differ from builder engine at L-GATE_VALIDATE.
