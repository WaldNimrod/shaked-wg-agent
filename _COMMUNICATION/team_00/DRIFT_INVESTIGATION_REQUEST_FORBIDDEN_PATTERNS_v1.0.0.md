# Drift Investigation Request — Forbidden Pattern Self-Contamination
# From: Team 00 (Nimrod) via Team 110 (shaked-wg-agent)
# To: Team 110 (Hub Domain Architect — AOS)
# Date: 2026-04-12
# Priority: MINOR (process improvement, not blocking)

---

## Problem Statement

During shaked-wg-agent S002 session startup (2026-04-12), `validate_aos.sh` Check 12 (cross-project contamination) failed with **2 FAIL** against files that had previously passed validation.

The root cause: **agents writing governance artifacts that quote `forbidden_patterns` literals trigger the very check those patterns protect.**

---

## Evidence

### Affected files (shaked-wg-agent repo)

| File | Patterns found | How they got there |
|------|---------------|-------------------|
| `_COMMUNICATION/team_190/VERDICT_INDEPENDENT_REVALIDATION_v1.0.0.md` | hub path variants, sibling project name | Team 190 validator quoted `project_identity.yaml` `forbidden_patterns` list verbatim in its findings |
| `_COMMUNICATION/team_110/HANDOFF_S001_CLOSE_S002_ENTRY_v1.0.0.md` | hub path in boundary docs | Team 100 arch referenced hub registry path and hub write-prohibition rule |

### Timeline

1. **2026-04-11** — Team 190 (Cursor Composer 2) ran independent re-validation. Initial verdict: FAIL (Check 12 on activation file). Fix applied. Resubmission: 12/12 PASS.
2. **2026-04-12** — The verdict file itself (committed post-resubmission) and the handoff file both contain the same forbidden literals → Check 12 fails again on next session startup.

### Additional finding

`roadmap.yaml` had 3 DEFERRED WPs with `current_lean_gate: null`. Check 5 treats `null` as a missing required field. This may affect other spoke projects with DEFERRED WPs.

---

## Root Cause Hypotheses

1. **No guidance in activation prompts** telling agents to avoid quoting `forbidden_patterns` literals in their output files. Validators and architects naturally cite what they find — the forbidden strings themselves.

2. **Check 12 scans all tracked files without exclusions.** Governance artifacts (`_COMMUNICATION/`) are tracked and contain cross-project references by design (hub paths, sibling project names in boundary rules).

3. **`null` vs missing field** — `validate_aos.sh` Check 5 does not distinguish between YAML `null` and absent field. DEFERRED WPs logically have no gate, but the validator rejects this.

---

## Requested Actions

### For the AOS domain team (Team 110 Hub)

1. **Investigate:** Is this pattern present in other spoke projects? Run `validate_aos.sh` on all registered spokes with `forbidden_patterns` defined and check for self-contamination in `_COMMUNICATION/` artifacts.

2. **Decision needed — Choose one mitigation path for Check 12:**
   - **(A)** Add an `exclude_paths` list to `project_identity.yaml` (e.g., `_COMMUNICATION/team_190/`, `_COMMUNICATION/team_110/`) so governance artifacts can reference external projects without triggering contamination.
   - **(B)** Update activation prompts for all agent roles to include an iron rule: "Never quote `forbidden_patterns` literals in output files. Use descriptions instead."
   - **(C)** Update `validate_aos.sh` to exclude `_COMMUNICATION/` from Check 12 scanning.
   - **(D)** Other approach the domain team sees fit.

3. **Decision needed — Check 5 null handling:**
   - Should `current_lean_gate: null` be valid for DEFERRED WPs?
   - If yes, update `validate_aos.sh` to accept `null` when `status: DEFERRED`.
   - If no, document that DEFERRED WPs must still carry `L-GATE_E`.

---

## Fixes Applied Locally (shaked-wg-agent, 2026-04-12)

| Fix | Detail |
|-----|--------|
| Check 12 | Replaced literal hub/sibling references with generic descriptions in 2 files |
| Check 5 | Set `current_lean_gate: L-GATE_E` for 3 DEFERRED WPs in `roadmap.yaml` |
| Validation | `validate_aos.sh`: 12 PASS / 0 SKIP / 0 FAIL |

These are local workarounds. The systemic issue remains until the AOS domain team addresses the root cause.

---

*Prepared by Team 110 (Builder Agent) on behalf of Team 00 | shaked-wg-agent | 2026-04-12*
