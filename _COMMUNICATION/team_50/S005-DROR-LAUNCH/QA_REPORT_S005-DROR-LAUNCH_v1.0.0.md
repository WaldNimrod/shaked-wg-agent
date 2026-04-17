# QA Report — S005-DROR-LAUNCH | Team 50

## Context bundle

- Work Package: S005-DROR-LAUNCH
- LOD400 Spec: `_COMMUNICATION/team_110/MANDATE_S005_DROR_QA_TEAM50_v1.0.0.md`
- Requestor: Team 110
- Write to: `_COMMUNICATION/team_50/S005-DROR-LAUNCH/`
- Expected file: `QA_REPORT_S005-DROR-LAUNCH_v1.0.0.md`

---

## 1. Verdict

**PASS**

All acceptance criteria were executed and validated with automation-first checks.  
AC-04 was re-run with live FTPS credentials via `scripts/run_dror_launch.sh` and produced an observed `run_record.report_url` equal to `https://www.nimrod.bio/wp-content/uploads/shaked-wg/dror/index.html`. Public URL health check returned HTTP 200.

---

## 2. AC table (Expected / Observed / Verdict)

| AC-ID | Expected | Observed | Verdict |
|-------|----------|----------|---------|
| **AC-01** | `python3 -m shaked_wg_agent status --profile dror` succeeds; shows profile **Dror Ground-House Long-Term** | Exit **0**. Output includes `Profile   : Dror Ground-House Long-Term`, `Budget    : ILS 5000–30000`, `Listings  : 0 total` | **PASS** |
| **AC-02** | City id resolves to `dror-carmel-region`; no config errors | `status` does not print `city_id` (CLI limitation). Supplement: `python3 -c 'from shaked_wg_agent.config import load_config; print(load_config("dror").city.city_id)'` → stdout **`dror-carmel-region`**, exit **0** | **PASS** |
| **AC-03** | Active resolved sources include `homeless` | `python3 -c 'from shaked_wg_agent.config import load_config; print([s.source_id for s in load_config("dror").active_sources])'` → **`['homeless']`**, exit **0** | **PASS** |
| **AC-04** | With `UPRESS_UPLOAD_PATH=wp-content/uploads/shaked-wg/dror` and upload credentials, `run_record.report_url` equals `.../shaked-wg/dror/index.html` | Live execution: `DROR_UPLOAD_PATH=wp-content/uploads/shaked-wg/dror ./scripts/run_dror_launch.sh dror` → run `run-20260417-000606-4b94`, observed report URL `https://www.nimrod.bio/wp-content/uploads/shaked-wg/dror/index.html`; `curl -I` returned HTTP 200 | **PASS** |
| **AC-05** | Report for Dror contains Dror listings only (two-profile fixture) | Ephemeral script: `generate_report` with listings filtered by `profile_id == load_config("dror").profile.profile_id`; fixture titles **DROR_UNIQUE_MARKER_QA_S005** present, **DEFAULT_UNIQUE_MARKER_QA_S005** absent. Printed **`AC-05 PASS`**, exit **0** | **PASS** |
| **AC-06** | Stale cleanup does not remove non-dror rows when scoped to dror | `pytest tests/test_persistence.py::test_mark_stale_scopes_removal_to_profile -v` → **`1 passed`**, exit **0** | **PASS** |
| **AC-07** | Non-dror listings not modified by dror verification merge path | Ephemeral script mirroring `run_scan` merge: non-dror row **same object identity** as input; dror row received verification fields. Printed **`AC-07 PASS`**, exit **0** | **PASS** |
| **AC-08** | `python3 -m shaked_wg_agent status --profile default` remains operational | Exit **0**. Output includes `Profile   : Shaked Basel WG Search`, `Listings  : 59 total` | **PASS** |
| **AC-09** | `data/cities/dror-carmel-region.json` documents settlement list + regional notes | File present: **16** settlements (e.g. פרדס חנה, בנימינה, זכרון יעקב, …); `region_notes` includes אלונה / חוף כרמל דרומי per `filters.region_notes` | **PASS** |
| **AC-10** | `_COMMUNICATION/team_110/STATS_S005_DROR_BASELINE_v1.0.0.md` has baseline metrics + post-run KPI template | File contains **Baseline metrics** (`runs_total`, `listings_total`, etc.), **Dror link target**, and **Post-run KPI template** fields (`run_id`, `report_url`, …) | **PASS** |

---

## 3. Blocking findings

None.

---

## 4. Open findings

None.

---

## 5. Environment + evidence log

**Session metadata**

| Field | Value |
|-------|--------|
| Date | 2026-04-17 |
| Host OS | Darwin 24.6.0, arm64 |
| Python | 3.11.15 |
| Git HEAD | `7f6569787ab98134f1bf6537e7f9af248f3b8829` |
| Repo | `/Users/nimrod/Documents/shaked-wg-agent` |

**AC testability preflight (mandatory)**

All ACs in `_COMMUNICATION/team_110/MANDATE_S005_DROR_QA_TEAM50_v1.0.0.md` were judged **testable** before execution: observable commands or file reads; AC-02 city id evidenced via supplemental `load_config` one-liner where CLI omits `city_id`.

**Commands executed (order)**

| Step | Command | Result |
|------|---------|--------|
| 1 | `pytest tests/ -v` | **82 passed**, exit **0** |
| 2 | `ruff check shaked_wg_agent/ tests/` | **All checks passed!**, exit **0** |
| 3 | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` | **17 PASS / 2 SKIP / 0 FAIL**, exit **0** |
| 4 | `python3 -m shaked_wg_agent status --profile dror` | Exit **0** (see AC-01) |
| 5 | `python3 -m shaked_wg_agent status --profile default` | Exit **0** (see AC-08) |
| 6 | `pytest tests/test_persistence.py::test_mark_stale_scopes_removal_to_profile -v` | **1 passed**, exit **0** |
| 7 | `DROR_UPLOAD_PATH=wp-content/uploads/shaked-wg/dror ./scripts/run_dror_launch.sh dror` | Exit **0**; observed report URL `https://www.nimrod.bio/wp-content/uploads/shaked-wg/dror/index.html` |
| 8 | `python3 - <<'PY' ... read runs.json for dror ... PY` | Exit **0**; latest Dror run `run-20260417-000606-4b94`, `report_url` matches expected |
| 9 | `curl -I -s \"https://www.nimrod.bio/wp-content/uploads/shaked-wg/dror/index.html\"` | HTTP **200** |

**Independence note:** This verdict is based solely on the commands and outputs above. No Team 110 QA conclusions were used as evidence.
