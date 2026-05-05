---
adr_id: ADR-049
title: Server-Side Team Push Authority
status: ACCEPTED
date: 2026-05-06
supersedes: ~
related: [ADR-043, ADR-040]
authors: [team_110]
approved_by: [team_100, team_00]
---

# ADR-049 — Server-Side Team Push Authority

This ADR is the hub-canonical rationale for **`session_archetype: server_session` teams MAY push narrowly scoped artifacts directly to `origin/main`**, aligning with **[`core/governance/team_99.md`](../../core/governance/team_99.md) §“Push Authority (origin/main)”** (first concrete implementation).

---

## §1 Principle

Server-side AOS teams **team_99**, **team_60**, **team_61**, and **any future** team whose governance contract designates a **`server_session`** archetype (or equivalent wording) **MAY** push canonical artifacts directly to **`origin/main`** only within the path classes enumerated in §3 below. Those teams **MUST NOT** push application source trees, governance SSoT in `core/`, hub methodology, `_aos/` layer artifacts, lean-kit source, application configuration blobs, or ad-hoc port/infrastructure churn outside **`port-registry.yaml`** governance (§2 tertiary constraint).

---

## §2 Authority basis

| Role | Basis | Normative implication |
|------|--------|------------------------|
| **Affirmative** | **Iron Rule #6 — Artifact communication** (`methodology/AOS_CONCEPT_AND_PRINCIPLES.md`): inter-team canonical work is delivered via files in **`_COMMUNICATION/`**. | Canonical delivery MUST be mechanically possible from long-lived server sessions — **narrow `origin/main` push** is bounded as in §3. |
| **Primary constraint** | **Iron Rule #11 — Governance flows source → snapshot only** (`CLAUDE.md` §Iron Rules; mirror: hub `core/governance/` vs spoke `_aos/governance/`). | **`_aos/governance/`** MUST NOT appear in ANY server-team push ALLOW list; **`core/`** MUST NOT appear in ALLOW list outside normal Team 00/Team 100 processes. Gov-update remains **ADR040 / Iron Rule #12** — **exclusive** of this ADR (`governance/directives/ADR040_AOS_DOMAIN_AUTHORITY_LOCKDOWN_v1.0.0.md`). |
| **Secondary constraint** | **Port canon** — **Iron Rule numbering per `CLAUDE.md` §Iron Rules clause 9** (listeners registered in **`lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml`**; Team 60 SSoT; `validate_aos.sh` Check 24). | Server-side deployments MUST NOT widen listener binding ad hoc beyond port-registry governance. |

*`Iron Rule #7` (ADR034 structured data/API authority) restricts canonical **field** edits when the hub DB is online — it governs **`roadmap`/DB-shaped state**, not whether a server session may **`git push` communication artifacts`; see rationale in **`core/governance/team_99.md`** lines **309–312**.*

---

## §3 Allowed / forbidden path classes

For each server-session team **`team_XX`**, the following pattern applies (matches **`core/governance/team_99.md`** lines **277–287**, generalized from literal `team_99` prefixes to **`{team_id}`**):

### MAY push (`origin/main`)

- `_COMMUNICATION/team_XX/**`
- `_COMMUNICATION/*/REPORT_team_XX_*.md`
- `_COMMUNICATION/*/MSG_team_XX_*.md`
- `_COMMUNICATION/*/archive/MSG-*.md`
- `_archive/**` — **deploy logs and operational artifacts ONLY** — **no application code**, **no governance files**

### MUST NOT push

- `api/`, `ui/`, `scripts/`, `lean-kit/`, `_aos/`, `core/`, `methodology/`
- `CLAUDE.md` and **`*.md`** files **outside** `_COMMUNICATION/` **and** `_archive/`
- **`_aos/governance/**`** (Iron Rule **#11** — read-only snapshot lineage)

*(Rationale, unchanged from **`team_99`** lines **289–291**): forbid list excludes **production source + governance propagation surfaces** — not post-execution canonical reports.*

---

## §4 Cross-reference

- **[`governance/directives/ADR043_TEAM_MESSAGING_PROTOCOL_v1.4.0.md`](ADR043_TEAM_MESSAGING_PROTOCOL_v1.4.0.md) §4** — *Branch Independence for MSG delivery* — mandates that MSG artifacts land on **`origin/main`** promptly in file mode; ADR-049 **generalizes** the same **`main`-visibility invariant** beyond MSG alone to REPORT + archive choreography for **server_session** archetypes first executed by **team_99**.
- **`core/governance/team_99.md` §Push Authority** — **first canonical implementation**.
- **`ADR040` / Iron Rule #12**: server push NEVER substitutes **`/AOS_gov-update`**, **`/AOS_gov-sync`**, or direct edits to **`core/governance/`** by non-privileged actors — **`GOVERNANCE_CHANGE_REQUEST`** remains the escalation shape for forbidden paths.

ADR-049 **explicitly excludes** procedural detail of **`POST /api/messaging/send`** (remaining subject to ADR043).

---

## §5 Applicability

1. Binding on **every** hub + spoke governance contract whose operating model declares **`session_archetype: server_session`** (or synonym).
2. **Current enumerants:** **`team_99`**, **`team_60`**, **`team_61`** — MUST maintain a **`## Push Authority (origin/main)`** section materially identical to **`team_99`** (lines **277–287**, substituted with their ID) plus **explicit forward reference** **`ADR049_SERVER_SIDE_TEAM_PUSH_AUTHORITY_v1.0.0.md`** .
3. **New** infra-side teams adopting server sessions MUST copy the PUSH pattern before first operational gate.

---

## Changelog

| Version | Date | Notes |
|---------|------|-------|
| v1.0.0 | 2026-05-06 | Authored Team 110 per mandate **AOS-V4.1-WP-ADR049-SERVER-PUSH** (EXPRESS LOD400-only). |

## References

- `core/governance/team_99.md` §Push Authority (lines 277–291)
- `governance/directives/ADR043_TEAM_MESSAGING_PROTOCOL_v1.4.0.md` §4
- `governance/directives/ADR040_AOS_DOMAIN_AUTHORITY_LOCKDOWN_v1.0.0.md`
- `methodology/AOS_CONCEPT_AND_PRINCIPLES.md`
- `CLAUDE.md` §Iron Rules
