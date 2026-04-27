---
id: TEAM_50_E2E_STANDARD
version: v1.0.0
status: ACTIVE
date: 2026-04-24
authors: [team_70]
authority: Team 50 (QA) + Team 100 (Spec reviewer)
scope: AOS hub — all spokes (L2/L2.5 with web UI)
promoted_from: AOS-V324-WP-E2E-SCAFFOLD
---

# Team 50 E2E Evidence Standard v1.0.0

## Rule

When a QA_REQUEST covers any flow that **cannot be fully verified** by screenshot,
snapshot, or MCP browser tooling alone, the builder team MUST supply E2E evidence
before the mandate may be marked PASS.

---

## When E2E Evidence Is Required

E2E evidence (Playwright run report or trace) is **mandatory** in any of the following conditions:

| Trigger | Explanation |
|---------|-------------|
| File upload | MCP tools cannot drive `<input type="file">` — a real browser via Playwright is required |
| Multi-step interaction with state mutation | Flows where each step depends on the previous step's server-side state (e.g., wizard, checkout, multi-page form) |
| Session-dependent state | Features that change based on prior user actions within the same session |
| Drag-and-drop / canvas interaction | Non-standard UI elements that MCP screenshot tools cannot interact with |
| Any flow where MCP tooling returns no actionable signal | If Team 50 cannot confirm the feature works from screenshot + network trace alone, E2E is required |

When in doubt: Team 50 declares E2E required in the QA_REQUEST. Builder team runs and attaches evidence before resubmission.

---

## When Screenshot + Snapshot Suffices

E2E evidence is **not required** when ALL of the following are true:

| Condition | Examples |
|-----------|---------|
| Static page render | Landing pages, read-only dashboard views, error pages |
| Read-only data display | Tables, charts, lists that show DB/API data without mutation |
| Single API call visible in network trace | A button click that triggers one POST and the response is visible in MCP network tools |
| Form fill without file upload | Simple text/select forms where MCP fill + snapshot confirms the result |

---

## Evidence Attachment Protocol

When E2E evidence is required, the builder team (Team 20, Team 30, or Team 10) MUST:

1. Run the E2E test suite with HTML report output:
   ```bash
   pytest tests/e2e/ --html=tests/e2e/report.html --self-contained-html
   ```

2. Optionally capture Playwright trace for complex failures:
   ```bash
   pytest tests/e2e/ --tracing=on
   # Produces: test-results/<test-name>/trace.zip
   ```

3. Commit or attach the report to the QA_REQUEST artifact using the field name:

   | Evidence artifact | QA_REQUEST field |
   |-------------------|-----------------|
   | HTML test report | `evidence_e2e_report` |
   | Playwright trace zip | `evidence_e2e_trace` |

4. Reference the committed path or paste the summary table (pass/fail counts) directly into the QA_REQUEST body.

---

## Team Obligations

| Team | Obligation |
|------|-----------|
| Team 50 (QA) | Declare E2E required in QA_REQUEST when trigger conditions are met; flag `blocked_reason_code: e2e_evidence_missing` if evidence is absent on resubmission |
| Team 20 (Backend) | Run E2E suite and attach report before issuing build complete signal when QA_REQUEST requires it |
| Team 30 (Frontend) | Same as Team 20 for frontend-owned flows |
| Team 10 (Gateway/Builder) | Same as Team 20/30 in Mode B |
| Team 100 (Validator) | Confirm `evidence_e2e_report` field is present before routing L-GATE_BUILD mandate |

---

## Enforcement

If E2E evidence is required per the trigger table above and the builder team does not attach it:

- Team 50 returns the QA_REQUEST with:
  - `status: BLOCKED`
  - `blocked_reason_code: e2e_evidence_missing`
  - `blocked_unblock_owner: builder team — run pytest tests/e2e/ and attach report`

The QA round does not count toward resubmission count when blocked for missing evidence.

---

## Scaffold Reference

The canonical Playwright harness for AOS spokes lives in:

```
lean-kit/modules/testing-e2e/
├── templates/conftest.py.template   ← session-scoped login + storage-state fixtures
└── templates/README.md.template     ← setup and evidence instructions
```

Adoption instructions: `lean-kit/modules/testing-e2e/MODULE.md` § Adoption.

---

*AOS Lean Kit — Team 50 E2E Evidence Standard v1.0.0 | 2026-04-24*
*Promoted from AOS-V324-WP-E2E-SCAFFOLD by team_70 | Authority: Team 50 + Team 100*
