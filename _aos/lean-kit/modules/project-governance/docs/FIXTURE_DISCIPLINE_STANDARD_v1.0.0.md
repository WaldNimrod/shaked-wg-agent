---
id: FIXTURE_DISCIPLINE_STANDARD
version: v1.0.0
status: ACTIVE
date: 2026-04-20
authors: [team_100]
scope: AOS-hub — all spokes (L2/L2.5 with structured input)
promoted_from: TikTrack S004-P005-WP001 (§6.2)
---

# Fixture Discipline Standard v1.0.0

## Rule

If a WP parses or consumes any structured input (CSV, JSON, XML, YAML, binary formats, etc.), the builder team (Team 20 / Team 30 / Team 10) MUST commit test fixtures to `tests/fixtures/<source>/` **before L-GATE_BUILD routing**.

Minimum fixture set per source:

| Fixture | File convention | Purpose |
|---------|----------------|---------|
| Happy path | `sample_complete.<ext>` | Valid, representative input — covers all expected fields and flows |
| Error path | `sample_errors.<ext>` | Invalid/malformed input — exercises parser error handling and validation messages |

## Rationale

Deterministic QA (Team 50) requires stable, committed input data. Without fixtures:
- Team 50 must construct its own test data, introducing risk of drift from real-world formats
- Enum value hallucinations in QA_REQUEST AC tables (e.g., requesting verification of a field that doesn't exist in the schema) go undetected until runtime
- Re-QA rounds caused by "this data format doesn't match the parser" are fully preventable

**Evidence from WP S004-P005-WP001:** Broker enum values (`WITHHOLDING_TAX`, `BROKER_INTEREST_PAID/RECEIVED`) in the QA_REQUEST were not in the DB CheckConstraint — cost one round of AC-10 confusion. Committed fixtures with the real schema would have caught this before mandate routing.

## Where to commit

```
tests/fixtures/<source_name>/
├── sample_complete.<ext>     # happy path
└── sample_errors.<ext>       # error/edge cases
```

Examples:
- `tests/fixtures/ibkr/sample_complete.csv`
- `tests/fixtures/ibkr/sample_errors.csv`
- `tests/fixtures/api_responses/sample_complete.json`

## When this applies

- **Required:** Any L2/L2.5 WP whose implementation parses structured external input
- **Not required:** L0 WPs, infrastructure WPs, documentation WPs, WPs with no structured input

## Team obligations

| Team | Obligation |
|------|-----------|
| Team 20 (Backend) | Commit fixtures before issuing build complete signal |
| Team 30 (Frontend) | Commit fixtures for any client-side parser |
| Team 10 (Gateway/Builder) | Same as Team 20/30 in Mode B |
| Team 50 (QA) | Use committed fixtures as primary test input; flag missing fixtures as `prerequisite_missing` BLOCKED |

## Enforcement

Fixture presence is checked at L-GATE_BUILD intake by Team 50. If fixtures are absent:
- Return QA_REQUEST with `blocked_reason_code: prerequisite_missing`
- `blocked_unblock_owner: builder team (Team 20/30/10) — commit tests/fixtures/<source>/`

---

*AOS Lean Kit — Fixture Discipline Standard v1.0.0 | 2026-04-20*
*Promoted from TikTrack S004-P005-WP001 by team_100 | Cross-ref: team_20.md, team_30.md*
