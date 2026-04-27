---
id: ADR038_GOVERNANCE_FILE_SOURCE_MIRROR_ARCHITECTURE
title: "ADR-038 — Governance File Source/Mirror Architecture"
version: "1.0.0"
status: APPROVED
author: Team 200 (Cowork) — ratified by Team 00
approved_by:
  - team_00
  - team_100
approval_date: "2026-04-18"
supersedes: null
adr_ref: ADR-038
wp_ref: S003-P018-WP001 (AOS-V322 Prompt Quality Upgrade)
related:
  - ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES (Iron Rule #7)
  - AOS_DIRECTORY_CANON_v1.0.0
---

# ADR-038 — Governance File Source/Mirror Architecture

## 1. Purpose

Eliminate ambiguity about which directory is authoritative for team governance files (`team_*.md`) and which is derived. Without this clarification, editors risk writing to the wrong location and having their edits silently overwritten by the deploy pipeline.

## 2. Background — the dual-directory observation

The agents-os repo contains two directories holding byte-identical team governance files:

| Directory | Files | Role |
|-----------|-------|------|
| `core/governance/team_*.md` | 17 | **SOURCE** — authored by Team 00 / Team 100; DB's `teams.gate_authority/writes_to/iron_rules/mandatory_reads` are materialized here by the deploy pipeline |
| `_aos/governance/team_*.md` | 17 | **MIRROR** — built from `core/governance/` by the deploy pipeline (`core/modules/governance/deploy.py:162`, Step 6) |

Prior to this ADR, external observers (including Team 80's Claude engine in RESEARCH_REPORT_PROMPT_QUALITY_v1.0.0.md) flagged this as "duplication / SSoT drift risk". It is not duplication — it is a designed source→mirror pipeline. This ADR makes the contract explicit.

## 3. Canonical contract

**SSoT (source):**
```
core/governance/team_[ID].md
```
- Authored by Team 00 + Team 100 only.
- DB-derived sections (`## Permissions`, `gate_authority`, `writes_to`, `iron_rules`, `mandatory_reads`) are materialized into these files by the deploy pipeline (`core/modules/governance/deploy.py` Step 5) from the `teams` table per ADR034.
- Manual prose edits (identity, role description, protocol sections, domain-specific rules) happen here.

**Mirror (deploy output):**
```
_aos/governance/team_[ID].md
```
- Built by `shutil.copy2(core/governance/*.md → _aos/governance/*.md)` in deploy Step 6.
- **MUST NEVER be edited directly.** Any manual edit to `_aos/governance/` will be silently overwritten on the next deploy.
- This is the snapshot that agents read for operational context (see §4).

## 4. Read paths — who reads where

| Consumer | Reads from | Why |
|----------|-----------|-----|
| Backend prompt generator (`dashboard_routes.py::get_prompts_generate`, line 834) | `core/governance/` (via `Path(__file__).resolve().parents[2] / "governance"`) | Generates prompts from the authoritative source so no deploy-lag affects accuracy |
| Agent sessions (onboarding, governance sync) | `_aos/governance/` (as instructed in prompt Instructions step 4) | Agents read the deployed snapshot — matches the directory canon path `_aos/governance/team_[ID].md` |
| `validate_aos.sh` Check 8 + 12 | `_aos/governance/` | Validates the deployed state, not the source |
| Spoke propagation | `core/governance/` → spoke `_aos/governance/` | Deploy Step 7 mirrors hub source into each spoke's `_aos/` |

## 5. Write rules

| Target | Who | How |
|--------|-----|-----|
| `core/governance/team_[ID].md` prose sections | Team 00 / Team 100 | Direct file edit; commit |
| `core/governance/team_[ID].md` ## Permissions section | Deploy pipeline | Materialized from DB `teams` row; never hand-edited |
| `_aos/governance/team_[ID].md` | Deploy pipeline ONLY | Step 6 mirror; manual edits forbidden |
| Spoke `_aos/governance/team_[ID].md` | Deploy Step 7 propagation ONLY | Manual edits forbidden |

Enforcement: any PR that modifies `_aos/governance/` without a corresponding `core/governance/` change is a protocol violation. Consider adding a `validate_aos.sh` Check 26 (future) asserting `_aos/governance/` content-hash ≡ deploy-derived hash from `core/governance/`.

## 6. Consequences

**Positive:**
- Eliminates the "which copy is canonical?" question raised by external audits.
- Confirms the backend prompt reader (`core/governance/`) is correct as-designed.
- Unblocks Phase 7 of AOS-V322-WP-PROMPT-QUALITY-UPGRADE: item 1.3 (dedup) is withdrawn; items 1.2 (H1 normalization) + 1.4 (engine alignment) apply to **source only**, and the deploy pipeline propagates the fix to the mirror.

**Negative:**
- Requires future Check 26 (mirror integrity) for full enforcement — not blocking for v1.0.0.

## 7. Scope withdrawn from AOS-V322

- Original Phase 7.0 plan proposed removing `core/governance/` and repointing backend at `_aos/governance/`. **That plan is withdrawn.** The backend already reads from the correct source; `_aos/governance/` is a deploy mirror and must remain.

## 8. Implementation

No code change required for ADR038 itself. The contract is documented; the existing pipeline continues. All future V322 phases apply their edits to `core/governance/` only and rely on the deploy pipeline to mirror.

## 9. Amendment rules

- Amendment requires Team 00 + Team 100 co-approval.
- Adding Check 26 (mirror integrity) can be done via minor version bump (v1.1.0).
- Any change to the source→mirror direction requires a new ADR.

---

*ADR-038 | Governance File Source/Mirror Architecture | v1.0.0 | 2026-04-18*
*Approved by: Team 00 (Principal) + Team 100 (Chief System Architect)*
