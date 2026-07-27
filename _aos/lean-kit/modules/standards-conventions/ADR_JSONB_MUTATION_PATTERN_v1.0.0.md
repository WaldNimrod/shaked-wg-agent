---
id: ADR_JSONB_MUTATION_PATTERN
version: v1.0.0
status: ACTIVE
date: 2026-04-20
authors: [team_100]
scope: Optional — SQLAlchemy-backed spokes only (TikTrack, future Python/PostgreSQL spokes)
promoted_from: TikTrack S004-P005-WP001 (§6.4)
---

# ADR — JSONB Mutation Pattern (SQLAlchemy / PostgreSQL)

## Problem

SQLAlchemy's change-detection does **not** track nested mutations to JSONB columns by default. If you modify a sub-key of a JSONB field in-place (e.g., `model.data["key"] = value`), SQLAlchemy will not mark the row dirty and will silently skip the `UPDATE`.

This manifested twice in S004-P005-WP001:
- **R3:** `normalized_data` JSONB — sub-key updates silently dropped
- **R5:** `pipeline_metadata.stages` JSONB — stage entries updated in-place, not persisted

Both bugs passed unit tests (in-memory state looked correct) and only failed at DB round-trip verification.

## Decision

For any SQLAlchemy model with a JSONB column, use one of two patterns when mutating nested values:

### Pattern A — Reassignment (preferred)

```python
# Instead of: model.json_col["key"] = value  ← SILENT FAIL
# Do this:
new_val = dict(model.json_col)  # shallow copy
new_val["key"] = value
model.json_col = new_val        # triggers dirty tracking
```

### Pattern B — flag_modified (when reassignment is impractical)

```python
from sqlalchemy.orm.attributes import flag_modified

model.json_col["key"] = value
flag_modified(model, "json_col")  # forces SQLAlchemy to include in UPDATE
session.flush()
```

## When to use each

| Pattern | Use when |
|---------|---------|
| A — Reassignment | New dict is small; nested update is top-level key |
| B — flag_modified | Deep nesting; performance-sensitive; partial update of large JSONB |

## Acceptance criterion

Every Team 20 backend WP that writes to a JSONB column MUST include a DB-round-trip test:
1. Perform the mutation via the API endpoint
2. Query the DB directly (separate session / `db.refresh(model)`)
3. Assert the persisted value matches the expected value

This proves the write landed in the DB, not just in SQLAlchemy's in-memory state.

## References

- SQLAlchemy docs: [Mutable Column Types](https://docs.sqlalchemy.org/en/14/orm/extensions/mutable.html)
- TikTrack fix commit: `30ed461` (normalized_data shallow-copy fix)
- TikTrack R5 fix: `pipeline_metadata.stages` reassignment pattern

---

*AOS Lean Kit — JSONB Mutation Pattern ADR v1.0.0 | 2026-04-20*
*Opt-in per spoke — applies to SQLAlchemy + PostgreSQL backends only*
*Cross-ref: team_20.md Iron Rules (SQLAlchemy-backed spokes)*
