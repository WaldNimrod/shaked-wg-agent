# Decision Ledger (ADD-ONLY)

<!-- AOS lean-kit template — Harvest A1 / Train-1 v5.2.1 DOC fold -->
<!-- Copy to `_COMMUNICATION/team_00/DECISION_LEDGER.md` (or domain equivalent) and append rows only. -->

**Version:** v1.0.0 | **Module:** `lean-kit/modules/project-governance/templates/DECISION_LEDGER.md`
**Disposition:** `file:///Users/nimrod/Documents/AOS_V5/agents-os/_COMMUNICATION/team_100/HARVEST_DISPOSITION_A1_A10_TRAIN1_2026-07-26_v1.0.0.md`

---

## Purpose

Durable, git-tracked record of owner decisions so they are not lost to context compaction. Every binding `DECISION_*.md` gets a ledger row in the **same commit** (Wiring Rule).

## Rules

1. **ADD-ONLY** — never delete or rewrite history rows; supersede with a new row pointing at the prior id.
2. **Gate walk** — every phase-gate / L-GATE report MUST walk this ledger; a signed row that never reached its enforcement locus **BLOCKS** the gate.
3. **Wiring Rule** — new binding artifact ⇒ ledger row + pointer from parent doc + handoff mention; run a wiring scan at session close.
4. **Pairs A10** — prefer one decision item per brief (`/AOS_decide`); record row when owner signs.

## Ledger

| decision_id | date | binding_effect | enforcement_locus | artifact_path | status | notes |
|-------------|------|----------------|-------------------|---------------|--------|-------|
| *(example)* DEC-YYYY-MM-DD-N | YYYY-MM-DD | one-line effect | who/what consumes it | `_COMMUNICATION/.../DECISION_*.md` | PENDING \| WIRED \| ENFORCED \| SUPERSEDED | |

**status values:** `PENDING` (signed, not wired) · `WIRED` (enforcement locus knows) · `ENFORCED` (live in code/canon) · `SUPERSEDED` (replaced by later row).
