# MANDATE — S005 Dror Profile Fast Launch (Team 110)

## Mandatory Identity Header
- `team_id`: team_110
- `role`: domain_architect
- `authority`: team_00
- `milestone`: S005 (ACTIVE)
- `date`: 2026-04-17
- `mode`: temporary shared-instance production launch

---

## Team 110 Mandate in This Project

Team 110 is the domain architect function for packaging scope, risks, and cross-team execution handoffs.  
Authoritative references: `_aos/governance/team_110.md`, `_aos/definition.yaml`, `_aos/context/ACTIVATION_ARCH.md`.

Execution implications for this launch:
- Team 110 defines architecture, constraints, acceptance boundaries, and QA handoff.
- True multi-user isolation remains S003 scope; this launch is a temporary bridge in S005.
- Team 00 decision authority remains supreme for risk acceptance.

---

## Roadmap Alignment

- Current state is `S005` (Israel Market Expansion) per `_aos/roadmap.yaml`.
- This task is implemented as an S005 operational bridge for a second user profile.
- Multi-user architecture (tenant isolation, per-user auth/data model) is intentionally deferred to S003.

---

## Dror Client Requirements → System Mapping

| Client requirement | Current system parameterization |
|---|---|
| בית צמוד קרקע להשכרה ארוכת טווח | `profile_id=dror`, `rental_duration=permanent`, custom tags for detached house preference |
| כניסה בין 2026-07-01 ל-2026-10-01 | `move_in_from=2026-07-01` + `custom_tags` window upper bound `entry_until_2026-10-01` |
| 6-7 חדרים, 5 חדרי שינה + קליניקה, העדפה ליחידה נפרדת | encoded in profile `custom_tags` for parser/scoring compatibility |
| חצר מעל 250 מ\"ר, דשא/אדמה, לא סינטטי | encoded in profile `custom_tags` for filtering/scoring pipeline use |
| אזור מורחב (פרדס חנה, בנימינה, זכרון, אלונה, חוף כרמל דרומי וכו') | new city definition `data/cities/dror-carmel-region.json` with settlement coverage list |

---

## Temporary Production Link Strategy (Approved Risk)

Shared instance with unique publish path:
- `profile_id`: `dror`
- `UPRESS_UPLOAD_PATH`: `wp-content/uploads/shaked-wg/dror`
- expected link to send: `https://www.nimrod.bio/wp-content/uploads/shaked-wg/dror/index.html`

Operational guardrails implemented:
- report publishing is filtered by `profile_id` (no mixed-profile report page)
- stale-removal is filtered by `profile_id` (no cross-profile cleanup)
- listing verification is filtered by `profile_id` (no cross-profile side effects)

Residual risk accepted (until S003):
- shared `data/listings.json` and `data/runs.json` remain global files
- API key model is still single-key (S002 model), not per-user credentials

---

## Delivery Artifacts

- Profile: `data/profiles/dror.json`
- Region: `data/cities/dror-carmel-region.json`
- Source registry update: `data/sources.json`
- Profile-isolation guardrails:
  - `shaked_wg_agent/persistence.py`
  - `shaked_wg_agent/runner.py`
- Team 50 package:
  - `_COMMUNICATION/team_110/MANDATE_S005_DROR_QA_TEAM50_v1.0.0.md`
  - `_COMMUNICATION/team_110/ACTIVATION_S005_DROR_QA_TEAM50_v1.0.0.md`
- Launch stats:
  - `_COMMUNICATION/team_110/STATS_S005_DROR_BASELINE_v1.0.0.md`

