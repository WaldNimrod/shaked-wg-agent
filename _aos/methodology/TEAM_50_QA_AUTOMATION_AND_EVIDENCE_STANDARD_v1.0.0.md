---
id: TEAM_50_QA_AUTOMATION_AND_EVIDENCE_STANDARD
version: v1.0.0
status: ACTIVE
authority: Team 00 + Team 100 + Team 50 practice
date: 2026-04-13
applies_to: All AOS-managed projects (L0–L3 profiles)
---

# Team 50 — QA Automation & Evidence Standard (v1.0.0)

## Purpose

Define **how Team 50 produces acceptable evidence** so that:

- Re-QA and regression cycles are **fast, repeatable, and exit-code driven** (minutes, not hours).
- **MCP IDE browser** and **manual screenshots** are **not** the primary proof path for the same AC on every run.
- Every project can implement the **same hierarchy** with project-specific scripts (`tests/`, CI).

This document complements:

- `core/governance/team_50.md` — role, intake, verdict states.
- Per-project `tests/TEAM_50_SELENIUM_E2E_REGISTRY.md` (or equivalent) — **inventory of automated checks**.

---

## Evidence hierarchy (mandatory order)

| Priority | Mechanism | When to use | Verdict evidence |
|----------|-----------|-------------|------------------|
| **1 — Primary** | **Automated**: API (`curl` / `fetch`) + **headless browser** (Selenium/Playwright) + **exit code 0** | Default for AC that can be observed via DOM or HTTP | Paste **command + full output**; state **script name** and **commit SHA** |
| **2 — Secondary** | **Scripted smoke** in repo (`npm run test:…`, `pytest`, `bash scripts/…`) | Full suite or nightly | Same as (1) |
| **3 — Supplementary** | **MCP `cursor-ide-browser`** | Exploratory UX, one-off layout checks, **after** automation passes | Snapshot refs + short note; **not** a substitute for (1) on repeated Re-QA |
| **4 — Optional** | **Manual screenshots** | Visual parity / stakeholder sign-off when explicitly requested | Attach files under `_COMMUNICATION/team_50/…/assets/` |

**Iron rule for Re-QA:** If an AC was failed for a **deterministic** bug (wrong text, wrong JSON shape), the **fix verification** MUST use **(1)** or **(2)**. Do not re-run multi-hour screenshot loops.

---

## Anti-patterns (do NOT)

| Anti-pattern | Why it fails | Replace with |
|--------------|--------------|--------------|
| Same AC proven only by MCP screenshot on every run | Slow, flaky, not diffable in CI | Headless script asserting DOM text / `data-testid` |
| “PASS” with no command output | Not reproducible | Log + exit code in verdict |
| Expanding/collapsing UI sections manually to chase one column | Brittle | Target stable selectors (`#id`, `[data-testid]`) in automation |

---

## Project implementation checklist (Team 60 + Team 30 + Team 50)

For each **product** repo (spoke):

1. **`tests/`** (or `api/tests/`) — add **focused** scripts for hot-path Re-QA (example: `s004-p006-wp001-reqa-d26.mjs`).
2. **`package.json`** — one `npm run test:…` per focused flow; **`HEADLESS=true`** supported for CI.
3. **`tests/TEAM_50_SELENIUM_E2E_REGISTRY.md`** — register script ID, scope, npm command, WP ref.
4. **Verdict markdown** — primary evidence = **automation output**; screenshots optional.
5. **CI** (optional but recommended) — run focused Re-QA script on PR touching the same surface.

For **agents-os** (hub): Pytest / dashboard checks remain as today; same hierarchy applies.

---

## Promotion to Hub (SSoT)

| Location | Role |
|----------|------|
| **This file** | Cross-project methodology — **canonical** |
| `core/governance/team_50.md` | Role contract — **evidence hierarchy** summary + pointer here |
| Spoke `_aos/governance/team_50.md` | **Snapshot** — refresh from hub after hub updates (`propagate_governance.sh` or manual per `AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.0.0.md`) |

---

## Version history

| Version | Date | Notes |
|---------|------|--------|
| v1.0.0 | 2026-04-13 | Initial — automation-first evidence; Re-QA discipline |

---

*log_entry | TEAM_50_METHODOLOGY | TEAM_50_QA_AUTOMATION_AND_EVIDENCE_STANDARD | CREATED | 2026-04-13*

---

## V318 Pre-flight

Pre-flight step: `validate_lod.sh <wp-dir>` — must exit 0 before QA begins. Evidence of PASS run must be recorded in QA session log.
