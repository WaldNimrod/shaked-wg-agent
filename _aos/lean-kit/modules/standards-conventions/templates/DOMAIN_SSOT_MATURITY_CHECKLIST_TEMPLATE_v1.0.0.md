# Domain SSOT maturity checklist (template) v1.0.0

**Module:** standards-conventions (optional)  
**Use:** Per-domain documentation — not a substitute for `validation-quality` gate templates (MANDATE/VERDICT).

Copy this file into the domain project (e.g. `_aos/context/` or domain docs) and fill rows. Adapt KPI IDs to the domain.

| KPI ID | Question (answer PASS/FAIL) | Evidence (path or note) | Owner |
|--------|------------------------------|-------------------------|-------|
| K1 | Critical standards have an SSOT file or explicit exception map | | |
| K2 | LOD400 AC rows can be traced to a standard or ADR | | |
| K3 | Drift between research and production is tracked with an owner | | |
| K4 | New WPs declare which standards apply | | |
| K5 | Gate spec-debt is visible before L-GATE_BUILD | | |

_Add or remove rows per domain. Do not duplicate hub `validate_aos.sh` checks — this is a **domain** maturity overlay._
