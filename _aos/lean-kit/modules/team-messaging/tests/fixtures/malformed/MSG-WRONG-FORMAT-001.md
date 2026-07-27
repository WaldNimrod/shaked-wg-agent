---
id: MSG-WRONG-FORMAT-001
schema_version: aos_v1_team_messaging
from_team: team_100
to_team: team_110
type: informal
subject: Malformed fixture — invalid filename pattern
date: '2026-04-30T10:03:00Z'
expects_response: false
status: SENT
---

## Malformed fixture — invalid filename pattern

This MSG has an invalid filename: `MSG-WRONG-FORMAT-001.md`.
The required pattern is `MSG-HUB-YYYYMMDD-NNN.md`.
The pre-commit hook must reject this when staged in a _COMMUNICATION/team_*/ directory.
