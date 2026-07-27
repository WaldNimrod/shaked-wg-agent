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
# Branch reference fields (ADR043 v1.5.0 §6.1 + §13 update).
# mandate_branch: set when handoff_context_pointer or artifact_paths live on a non-main branch.
#   Receiving session MUST run: git fetch origin {mandate_branch} before access.
#   OMIT (or leave "") when artifacts on main.
# artifact_paths: list of up to 5 additional paths on mandate_branch (spec, dispatch, etc.).
mandate_branch: ""   # e.g. claude/strange-mcnulty-651551
artifact_paths: []   # e.g. [_COMMUNICATION/team_10/DISPATCH_WP004_v1.md]
---

## One-line summary

Message body (markdown). This template uses **hub** keys `from_team` / `to_team`.
Module 12 file drops use `from`/`to` as `mac|server` — do not mix.

## Branch Context  *(include only when mandate_branch is set)*

> **Artifacts on non-main branch `{mandate_branch}`.**
> Before reading `handoff_context_pointer`, run:
> ```
> git fetch origin {mandate_branch}
> git checkout origin/{mandate_branch} -- {handoff_context_pointer}
> ```
> Additional artifacts on this branch (from `artifact_paths`):
> - {artifact_paths[0]}
> - {artifact_paths[1]}
> *(Remove placeholder lines not applicable.)*

## Continuation

> **For formal artifact types** (PHASE_REPORT, MANDATE, VERDICT, CLOSURE, RESPONSE):
> `next_step`, `handoff_to`, and `handoff_context_pointer` are REQUIRED in frontmatter per ADR043 v1.3.0 §13.
> `mandate_branch` + `artifact_paths` are OPTIONAL (ADR043 v1.5.0 §6.1) — set when artifacts live on a non-main branch.
> Remove this section for informal/status/question messages where continuation fields are optional.
