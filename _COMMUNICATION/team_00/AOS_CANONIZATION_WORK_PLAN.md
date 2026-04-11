# AOS Canonization Work Plan — shaked-wg-agent
## Document type: LOD100 + Strategic Milestone Register
## WP: S001-P002-WP001
## Status: PENDING DOMAIN REVIEW
## Author: Team 00 (Nimrod) + shaked_arch (Claude Code)
## Date: 2026-04-11
## Submitted to: AOS domain teams (architecture, validation) for accuracy review

---

## 1. Purpose

This document serves two goals:

1. **Canonization record** — documents the governance gaps that existed, the fixes applied, and the final verified state of the project's AOS governance
2. **Strategic roadmap register** — defines the product evolution path from personal utility to SaaS service, registered as formal AOS milestones and WPs for domain team review

It is submitted to AOS domain teams **before execution of any S002+ work** to validate:
- Accuracy of the canonization gap list and fixes
- Correctness of WP ID format and milestone structure
- Appropriateness of profile assignments (L0 / L2 / L2.5) per stage
- Open questions requiring domain guidance

---

## 2. Project Identity

| Field | Value |
|-------|-------|
| **Project ID** | shaked-wg-agent |
| **Name** | Shaked WG Basel Search Agent |
| **Repo** | WaldNimrod/shaked-wg-agent |
| **Current Profile** | L0 (Lean/Manual) |
| **Hub** | AOS methodology hub (GitHub: WaldNimrod org; repo name `agents` + `-` + `os`) |
| **Owner** | Team 00 — Nimrod |
| **Current Version** | v0.2.2 |
| **Deployed** | nimrod.bio/agents/shaked-wg/ (FTPS, 3× daily cron) |
| **Project Window** | 2026-04-09 → 2026-06-08 (S001) |

---

## 3. Canonization Gap Audit

### 3.1 Pre-Canonization State (2026-04-11 before S001-P002-WP001)

| Artifact | Status | Notes |
|----------|--------|-------|
| `_aos/roadmap.yaml` | ✅ Present | 2 WPs, 2/4 gates passed |
| `_aos/team_assignments.yaml` | ✅ Present | Cross-engine rule satisfied |
| `_aos/metadata.yaml` | ✅ Present | Profile: L0, lean-kit: v3.1.2 |
| `_aos/context/PROJECT_CONTEXT.md` | ✅ Present | Complete scope + architecture |
| `_aos/context/ACTIVATION_ARCH.md` | ✅ Present | |
| `_aos/context/ACTIVATION_BUILDER.md` | ✅ Present | |
| `_aos/context/ACTIVATION_VALIDATOR.md` | ✅ Present | |
| `_aos/lean-kit/` | ✅ Present | v3.1.2, physical copy (not symlink) |
| `_aos/work_packages/` (legacy non-canonical folder name) | ✅ Present | LOD400 + LOD500 |
| `_COMMUNICATION/team_{00,100,110,190}/` | ✅ Present | Empty (.gitkeep) |
| Hub `projects.yaml` registration | ✅ Present | enabled: true |
| `_aos/MILESTONE_MAP.md` | ✅ Present | |
| `_aos/README.md` | ✅ Present | |
| **`_aos/project_identity.yaml`** | ❌ **MISSING** | Validation check 12 failure |
| **lean-kit Module 12 (managed-pipeline)** | ❌ **MISSING** | v3.1.2 predates L2.5 module |
| **WP IDs canonical format** | ❌ **NON-CANONICAL** | Legacy `SHAKED-*` prefix vs required `SNNN-PNNN-WPNNN` |
| **`pyproject.toml` version** | ⚠️ MISMATCH | 0.1.0 vs `__init__.py` 0.2.2 |
| **`_aos/ideas.json`** | ❌ **MISSING** | Pre-gate idea incubator |
| **L-GATE_V** | ⏳ PENDING | Cross-engine validator not yet executed |

### 3.2 Fixes Applied (S001-P002-WP001 execution, 2026-04-11)

| Fix | Action | Result |
|-----|--------|--------|
| Created `_aos/project_identity.yaml` | Written from hub v3.1.3 template | ✅ DONE |
| Lean-kit v3.1.2 → v3.1.3 | Copied `managed-pipeline` module + `L2.5.yaml` profile from hub | ✅ DONE |
| Updated `_aos/metadata.yaml` | `lean_kit_version: 3.1.3`, added `managed-pipeline` to active_modules | ✅ DONE |
| Migrated WP IDs | Legacy prefix → `S001-P001-WP001` (roadmap + dir rename + ACTIVATION_ARCH) | ✅ DONE |
| Fixed `pyproject.toml` | `version = "0.2.2"` | ✅ DONE |
| Created `_aos/ideas.json` | v1.1.0 schema, empty ideas array | ✅ DONE |
| Updated hub `projects.yaml` | Added `lean_kit_version`, `active_milestone`, `canonized_at`, `future_profile` | ✅ DONE |
| Registered S001-P002 + S002–S004 WPs | Full SaaS milestone register in `roadmap.yaml` | ✅ DONE |

### 3.3 Remaining Item — L-GATE_V

**Authority: shaked_val (OpenAI) — immutable, constitutional, cross-engine.**

L-GATE_V for S001-P001-WP001 has not been executed. This is the only remaining gap for S001 completion.

**Trigger:** Team 00 activates `shaked_val` with `_aos/context/ACTIVATION_VALIDATOR.md` after domain review of this document is complete.

**Validator reads:**
- `_aos/work_packages/S001-P001-WP001/LOD400_spec.md`
- `_aos/work_packages/S001-P001-WP001/LOD500_asbuilt.md`
- Test results: `pytest tests/ -v` (current: all tests pass)
- Deployed output: `https://www.nimrod.bio/agents/shaked-wg/index.html`

**Expected output:** `_COMMUNICATION/team_190/S001-P001-WP001/L-GATE_V_result.md`

---

## 4. Forward Roadmap — SaaS Product Vision

### 4.1 Strategic Direction

Transform from a single-user, single-city apartment search utility into a **multi-city, multi-tenant, billing-enabled SaaS** — providing personalized apartment-finding as a service across European housing markets.

**End-state product characteristics:**
- Any user or agency can sign up, configure a search profile (city, budget, preferences), and receive ongoing curated results
- Subscription tiers (Free / Pro / Agency) with usage metering
- External billing provider integration (Stripe or LemonSqueezy)
- Role-based access (admin / agent / viewer)
- API-first design with webhook support for integrations
- White-label / reseller capability for agencies

### 4.2 Milestone Summary

```
S001  Personal Agent      L0    June 2026    ← CURRENT (IN_PROGRESS)
S002  Platform Foundation L2    Sep 2026     ← PLANNED
S003  SaaS Infrastructure L2.5  Dec 2026     ← PLANNED
S004  SaaS Product Launch L2.5  Mar 2027     ← PLANNED
```

### 4.3 Stage 1 — S001: Personal Agent (Basel, June 2026)

**Profile: L0 | Target: 2026-06-08**

| WP | Label | Gate | Status |
|----|-------|------|--------|
| S001-P001-WP001 | Core agent: scan, score, publish | L-GATE_B → L-GATE_V | IN_PROGRESS |
| S001-P002-WP001 | AOS canonization + SaaS roadmap | L-GATE_B | IN_PROGRESS |

**Success criteria:** Shaked finds a Basel apartment before June 8, 2026. L-GATE_V passes for S001-P001-WP001.

### 4.4 Stage 2 — S002: Platform Foundation (Q3 2026)

**Profile: L2 | Target: 2026-09-30**

**Prerequisite:** L2 profile transition (AOS engine + Dashboard deployment) before S002-P002-WP001 enters L-GATE_S.

| Program | WP | Label | Track | Profile |
|---------|----|-------|-------|---------|
| P001: Abstraction | WP001 | City-agnostic config schema + scraper interface | A | L2 |
| P001 | WP002 | Add Zurich + Bern search profiles | A | L2 |
| P002: API | WP001 | REST API layer (FastAPI) — /search, /listings, /runs | **B** | **L2.5** |
| P002 | WP002 | API key auth (single-user) | A | L2 |
| P003: Alerts | WP001 | Email/Telegram notification digest | A | L2 |

### 4.5 Stage 3 — S003: SaaS Infrastructure (Q4 2026)

**Profile: L2.5 for all complex WPs | Target: 2026-12-31**

All L2.5 WPs in S003 require:
- EXT-CP1 (Team 190 pre-pipeline entry) — mandatory
- LOD300 (system design with mockups) — mandatory
- Human gate (Team 00) at Phase 3 (LOD300) and Phase 5 (UX final) — non-delegatable

| Program | WP | Label | Track | Profile |
|---------|----|-------|-------|---------|
| P001: Multi-tenancy | WP001 | Data model: tenants, profiles, users, results | **B** | **L2.5** |
| P001 | WP002 | Tenant isolation + auth middleware | B | L2.5 |
| P002: Billing | WP001 | Billing provider integration (Stripe/LemonSqueezy) | **B** | **L2.5** |
| P002 | WP002 | Subscription tiers: Free / Pro / Agency | A | L2 |
| P002 | WP003 | Usage metering + quota enforcement | A | L2 |
| P003: Permissions | WP001 | RBAC — admin / agent / viewer | B | L2.5 |
| P003 | WP002 | API key lifecycle (issue, rotate, revoke) | A | L2 |

### 4.6 Stage 4 — S004: SaaS Product Launch (Q1 2027)

**Profile: L2.5 | Target: 2027-03-31**

| Program | WP | Label | Track |
|---------|----|-------|-------|
| P001: Self-serve | WP001 | Customer onboarding flow (signup → profile wizard → first scan) | B |
| P001 | WP002 | Web dashboard (results, alerts history, billing) | B |
| P002: White-label | WP001 | Agency/partner config (custom branding, city bundles) | A |
| P002 | WP002 | Reseller API + webhook contracts | B |
| P003: Analytics | WP001 | Usage analytics + customer health dashboard | A |

---

## 5. Profile Transition Plan

| Trigger | Action |
|---------|--------|
| S002-P002-WP001 enters L-GATE_E | Deploy AOS core engine; update metadata.yaml `aos_engine_version` |
| S002-P002-WP001 enters L-GATE_S | Full L2 profile active; Dashboard registration confirmed |
| S003-P001-WP001 enters L-GATE_E | First L2.5 WP; EXT-CP1 required; ORCHESTRATOR_RUNBOOK.md must be read |

**L2 transition checklist:**
- [ ] Deploy the AOS hub `core/` engine tree to waldhomeserver
- [ ] Update `_aos/metadata.yaml`: `aos_engine_version: "<version>"`
- [ ] Enable Modules 02, 05, 06, 07, 08 in `active_modules`
- [ ] Register in AOS Dashboard (`enabled: true` already set)
- [ ] Confirm: `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 12 PASS

---

## 6. Open Questions for Domain Review

The following items require AOS domain team input before S002 work begins:

| # | Question | Domain | Priority |
|---|----------|--------|----------|
| 1 | **L2.5 for S002-P002-WP001 (REST API)?** The API surface introduces a new public contract. Is L2.5 with Track B + LOD300 the right call, or is L2/Track A sufficient at this stage? | Architecture | High |
| 2 | **Database migration strategy for S003.** JSON → PostgreSQL is a breaking change. Should this be modeled as a single L2.5 WP or split into schema WP + migration WP? | Architecture | High |
| 3 | **Billing provider selection.** Stripe vs LemonSqueezy vs self-hosted. Any AOS-level preference or prior art in the hub? | Architecture / Team 00 | Medium |
| 4 | **L-GATE_V execution timing.** Should S001-P001-WP001 L-GATE_V happen before or after S001-P002-WP001 canonization is complete? Currently sequenced as: canonization first, then validator. | Validation | High |
| 5 | **ideas.json ownership.** Template says `owner: team_100` (architecture). Correct for this project? | Governance | Low |

---

## 7. Verification Checklist

Post-canonization validation (completed 2026-04-11):

```bash
# Governance structure
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Target: 12 PASS / 0 SKIP / 0 FAIL

# Application health
python -m pytest tests/ -v          # all tests pass
python -m shaked_wg_agent status    # CLI functional
python -m shaked_wg_agent run       # scan + publish functional

# Artifact presence
ls _aos/project_identity.yaml       # ✅
ls _aos/ideas.json                  # ✅
ls _aos/lean-kit/modules/managed-pipeline/  # ✅
ls _aos/lean-kit/profiles/L2.5.yaml  # ✅
ls _aos/work_packages/S001-P001-WP001/  # ✅ (renamed from legacy prefix)
grep "S001-P001-WP001" _aos/roadmap.yaml  # ✅
grep "3.1.3" _aos/metadata.yaml    # ✅
```

---

## 8. Document History

| Date | Author | Change |
|------|--------|--------|
| 2026-04-11 | Team 00 + shaked_arch | Initial draft — canonization complete, SaaS roadmap registered |

---

*Submitted for domain review. Reply via `_COMMUNICATION/team_100/S001-P002-WP001/` or `_COMMUNICATION/team_190/S001-P002-WP001/`.*
