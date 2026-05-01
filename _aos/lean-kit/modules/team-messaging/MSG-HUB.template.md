---
id: MSG-HUB-YYYYMMDD-NNN
schema_version: aos_v1_team_messaging
from_team: team_XX
to_team: team_YY
type: informal
subject: One-line summary
date: YYYY-MM-DDTHH:MM:SSZ
related_wp: ""
expects_response: false
status: SENT
# Continuation fields (REQUIRED in formal artifacts: PHASE_REPORT_*, MANDATE_*, VERDICT_*, CLOSURE_*, RESPONSE_*)
# Per ADR043 v1.3.0 §13. Optional for informal/status/question types.
next_step: "[imperative sentence: what the receiving agent should do immediately]"
handoff_to: team_NN  # canonical team identifier; team_00 = human decision gate
handoff_context_pointer: path/to/most_critical_file.md  # single most important file to read next
---

## One-line summary

Message body (markdown). This template uses **hub** keys `from_team` / `to_team`.
Module 12 file drops use `from`/`to` as `mac|server` — do not mix.

## Continuation

> **For formal artifact types** (PHASE_REPORT, MANDATE, VERDICT, CLOSURE, RESPONSE):
> `next_step`, `handoff_to`, and `handoff_context_pointer` are REQUIRED in frontmatter per ADR043 v1.3.0 §13.
> Remove this section for informal/status/question messages where continuation fields are optional.
