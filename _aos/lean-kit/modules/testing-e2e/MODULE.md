---
module: 15
id: testing-e2e
title: Playwright E2E Scaffold
version: 1.0.0
status: ACTIVE
category: TOOLING
required_by_profiles: [L2, L2.5]
lifecycle_archetype: TOOLING_SCAFFOLD
depends_on: [validation-quality]
---

# Module 15 — Playwright E2E Scaffold

## Purpose

Provides a canonical L0 scaffold (templates + docs only; no runtime code) that any AOS spoke
with a web UI can adopt to bootstrap Playwright E2E coverage with AOS conventions pre-wired.

Addresses the recurring cost of independently rebuilding a Playwright harness on each spoke.
Once adopted, a spoke inherits: session-scoped authentication, storage-state reuse, AOS env-var
naming, and Team 50 evidence expectations — before writing a single test spec.

## Contents

| File | Description |
|------|-------------|
| `templates/conftest.py.template` | Session-scoped login + storage-state fixtures; fill `{{PLACEHOLDER}}` values at spoke adoption |
| `templates/README.md.template` | Env vars, setup steps, test-run conventions, storage-state pattern explanation |
| `docs/TEAM_50_E2E_STANDARD_v1.0.0.md` | Team 50 evidence hierarchy extension: when E2E evidence is required vs. optional |

## Dependencies

- Module 08 (validation-quality): `validate_aos.sh` checks that L-GATE_BUILD exit criterion is met
- AOS env-var canon: `AOS_E2E_BASE_URL`, `AOS_E2E_USER`, `AOS_E2E_PASS` (uniform across all spokes)

## Profile Inclusion

| Profile | Status |
|---------|--------|
| L0 | NOT APPLICABLE (no web UI) |
| L2 | OPTIONAL (adopt when spoke has web UI and E2E coverage is required) |
| L2.5 | OPTIONAL (same trigger as L2) |
| L3 | OPTIONAL |

## Adoption

1. Copy `templates/conftest.py.template` → `tests/e2e/conftest.py`; replace all `{{PLACEHOLDER}}` markers
2. Copy `templates/README.md.template` → `tests/e2e/README.md`; replace `{{PROJECT_NAME}}`
3. Read `docs/TEAM_50_E2E_STANDARD_v1.0.0.md` — governs when Team 50 will require E2E evidence in QA_REQUEST

## Promoted from

AOS-V324-WP-E2E-SCAFFOLD (2026-04-24) — canonicalized from TikTrack S004-P005-WP001 QA experience
