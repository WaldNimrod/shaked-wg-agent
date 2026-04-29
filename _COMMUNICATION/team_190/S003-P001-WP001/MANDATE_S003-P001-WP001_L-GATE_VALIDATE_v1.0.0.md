---
id: MANDATE_S003-P001-WP001_L-GATE_VALIDATE_v1.0.0
from: Team 100 (Chief System Architect)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-20
type: L-GATE_VALIDATE_MANDATE
wp: S003-P001-WP001
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
he_title: מנדט ולידציה (L-GATE_VALIDATE — אחרי מימוש)
engine_constraint: "validator engine MUST differ from builder engine (Iron Rule — L-GATE_V / L-GATE_VALIDATE)"
prerequisite_gates: L-GATE_S PASS, L-GATE_B PASS, implementation complete per LOD400
---

# מנדט ולידציה — S003-P001-WP001: L-GATE_VALIDATE (חוקה / cross-engine)

## מטרה

**ולידציה חוקתית** של **היישום** אחרי ש-**L-GATE_B** הושלם: לוודא שהמימוש עומד ב-**LOD400**, ב-Iron Rules, ב-`validate_aos.sh`, בבדיקות, וברמת **LOD500** / as-built כמוסכם בפרויקט.

מנדט זה **לא** מחליף את **מנדט L-GATE_S** (בדיקת אפיון pre-build) — מופעל **רק לאחר** קוד ממומש ו- build PASS.

## 1. כותרת

| Field | Value |
|-------|-------|
| Gate | **L-GATE_VALIDATE** (שקול L-GATE_V / constitutional lock במסמכי lean-kit) |
| Work Package | S003-P001-WP001 |
| Label | Multi-tenant data model — tenants, profiles, users, results |
| Track | B |
| Profile | L2.5 |
| Precondition | L-GATE_S (spec) **PASS**; L-GATE_B **PASS**; `lod_status` progression per roadmap rules |

## 2. Precondition Checklist (must be TRUE before invoking)

- [ ] `gate_history` shows **L-GATE_S** → `PASS` or `PASS_WITH_FINDINGS` (material findings closed).
- [ ] **EXT-CP1** satisfied per project canon (where required for L2.5 pipeline entry) — see `_COMMUNICATION/team_00/AOS_CANONIZATION_WORK_PLAN.md` §4.5.
- [ ] **Builder engine** recorded (e.g. cursor-composer) for cross-engine contrast with **validator engine** (e.g. openai).
- [ ] `PERSISTENCE_BACKEND=postgresql` path tested; `json` default regression green.

## 3. Scope — What This Gate Validates

1. **Fidelity to LOD400** — all AC-00…AC-17 met or explicitly waived in writing by Team 00.
2. **Test coverage** — unit + integration (where specified); `pytest` green.
3. **Repository governance** — `validate_aos.sh` → 17+ PASS, no new FAIL; Check 4 `spec_ref` resolution.
4. **Iron Rules** — API-only DB mutations (ADR034) on canonical fields; no spoke→hub illegal writes.
5. **Security posture** (within WP001) — tenant alignment on writes; no auth secrets in code.
6. **As-built** — `LOD500` or `LOD500_asbuilt` stub filed per project convention before COMPLETE.
7. **Cross-engine** — validator engine ≠ builder engine; documented in verdict.

## 4. Validation Criteria (VC)

| VC | Criterion | Evidence |
|----|------------|----------|
| V-01 | Code matches DDL appendix (Alembic applied) | Migration revision + `alembic current` |
| V-02 | Parity: JSON vs PG for listings/runs | Test logs / golden outputs |
| V-03 | Import CLI idempotency | Second run no duplicate rows |
| V-04 | Ruff + pytest in CI / local | CI output |
| V-05 | `validate_aos.sh .` | Screenshot or log line |
| V-06 | No JWT/RLS in WP001 code | Grep or path deny-list |
| V-07 | Verdict independence | Solo read of primary artifacts first |

## 5. Artifacts to Review (implementation phase)

| Path | Purpose |
|------|---------|
| `shaked_wg_agent/db/**` (or as implemented) | ORM, repos, context |
| `alembic/versions/*.py` | Schema |
| `shaked_wg_agent/persistence.py` (or package) | Dual dispatch |
| `scripts/import_json_to_postgres.py` (or package entry) | Migration tool |
| `tests/**` | New + regression |
| `_aos/work_packages/S003-P001-WP001/LOD400_*.md` | Spec of record |
| `_aos/roadmap.yaml` | Gate history, `lod_status` |

## 6. Output

**Verdict file (Team 190 writes):**  
`_COMMUNICATION/team_190/S003-P001-WP001/VERDICT_S003-P001-WP001_L-GATE_VALIDATE_v1.0.0.md`

**Verdict options:**

- `PASS` — L-GATE_VALIDATE satisfied; `lod_status` may advance to **LOD500** / **COMPLETE** per Team 00 + ADR034 sync rules.
- `PASS_WITH_FINDINGS` — pass with minor/correctable findings; roadmap notes required.
- `FAIL` — must remediate and re-validate; **not** a release candidate.

**Optional alias filename** (if project standard uses `L-GATE_V_result`): may duplicate pointer in verdict body.

## 7. Notes

- This mandate is **staged in advance** so Team 110/builder know the **bar** before coding ends.
- Do **not** execute L-GATE_VALIDATE before implementation exists — premature runs invalidate the process.

---
*L-GATE_VALIDATE mandate v1.0.0 — team_100 → team_190 — 2026-04-20*
