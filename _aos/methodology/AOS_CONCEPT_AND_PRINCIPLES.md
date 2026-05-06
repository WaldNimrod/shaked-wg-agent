# AOS — Concept & Principles

> "A software house with one person."

---

## What AOS Is

AOS (Agents OS) is a software house with one human. It is an operating environment that optimizes process management, creates the right agents for each task, generates optimal prompts, and produces the highest-quality code possible — all directed by a single System Designer who defines what gets built and why.

AOS is not a product. It is the team that builds products. It is not a framework you install — it is a living system that evolves with its operator and the AI capabilities available at any given moment.

## Purpose

The entire purpose of AOS is optimization: given a product vision defined by Team 00 (the human), produce the most accurate and highest-quality implementation across every domain. This means:

- **Process optimization** — minimize friction, maximize throughput, enforce quality at every gate
- **Agent creation** — assign the right engine, role, and governance contract to each task
- **Prompt engineering** — generate layered prompts that give agents precise identity, authority, context, and task definitions
- **Quality assurance** — cross-engine validation, structured feedback, audit trails

AOS is inherently dynamic. Three months ago it was something fundamentally different, and the pace of change only accelerates. The system must accommodate rapid evolution without losing governance integrity.

## Origin

AOS emerged from a simple observation: the work that once required a team of 8 people over a month can now be done by one person and AI agents in a day. But without structure, agents drift, validate themselves, lose context between sessions, and communicate through ephemeral chat. AOS solves this by providing:

- **Defined roles** with clear boundaries (who does what, who must NOT do what)
- **A gate model** that enforces quality checkpoints before work progresses
- **Artifact-based communication** (files, not chat — auditable, persistent, routeable)
- **Cross-engine validation** (the builder never validates its own work)
- **Physical methodology snapshots** (each project carries its own governance copy)

## The Human Role

The System Designer (Team 00) does not write code. The System Designer:

1. Defines product vision (what to build and why)
2. Designs at concept level (LOD200 — architecture-level "how")
3. Makes architectural decisions that shape the system's direction
4. Manages the process (routing artifacts, making decisions, approving gates)
5. Turns fantasy into reality — through the team, not through the keyboard

This is intentional. AOS is built for someone who thinks in products, not in code.

## Evolution Model

AOS evolves in levels. Each level adds automation while keeping lower levels operational.

### L0 — Lean (Governance Only)

The foundation. Contains:
- Team definitions with roles, skills, and contracts
- Work packages, roadmaps, and milestone tracking
- Templates, canon files, communication standards
- Modular lean-kit (portable methodology)

All orchestration is manual — Team 00 routes everything. This is the most flexible level: it could govern film production, research projects, or any structured creative process. The methodology is domain-agnostic.

### L2 — Pipeline (Governance + Engine)

The production tier. Adds:
- A defined 5-gate process from spec to approved deliverable
- Pipeline + database managing gate progression
- Roadmap locked by code (agents cannot edit it directly)
- Code-driven validation replacing manual checks (significant token savings)

The key difference from L0: in L2, the process itself is enforced by software, not by human discipline alone.

### L3 — Autonomous (Future Vision)

The target state. The System Designer:
- Builds LOD200 with the architect agent
- Approves the human-gate in the process
- Makes decisions when agents escalate

Everything else is autonomous. Not being built yet — agent capabilities improve so rapidly that the right moment to build L3 has not arrived.

### L1 — Deprecated

An early experiment that did not work. Not referenced in current methodology.

## The Self-Referential Nature

AOS is both a container for projects and a project within itself. The hub repo (`agents-os`) manages other projects while also being managed by its own governance layer. This creates a real architectural tension:

- `core/definition.yaml` operates at meta-level (all projects, all stages)
- `_aos/roadmap.yaml` operates at project-level (agents-os as a project)

This is not a bug — it is a fundamental property of a system that must be able to evolve itself through its own process. It requires careful architectural attention.

## Data Authority Model

AOS separates data into two layers: **structured data** (parameters, status, configuration) and **extending content** (specs, governance prose, methodology documents). When the engine database is online, the database holds structured data; files extend it with specs and narrative. **Canonical binding:** `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` (V320 / IDEA-040 closure).

### The Rule

> When the AOS v3 database is **available and reachable**, it is the single source of truth for all **structured** data it represents. Mutations go through the API; `roadmap.yaml`, `definition.yaml`, and `projects.yaml` receive **deployed snapshots** via `deploy_cascade()` — they must not be hand-edited for canonical fields while the DB is running (Iron Rule #7). **Extending** files (LOD specs, mandates, methodology) may be authored in git; they must not contradict the DB for structured fields. When **no** database is available (offline branch or pre-bootstrap), files hold authority until reconciled via API or seed. **Profile (L0 / L2 / L2.5 / L3) describes automation and operational mode — not whether structured data is file-backed when the DB is online.**

### By Profile

Profile affects **how much** the engine automates (gates, dashboard, pipeline depth), not whether PostgreSQL is authoritative for WP/team/project state when connected.

| Profile | Typical automation | Structured data when DB is online | Gate / audit trail |
|---------|-------------------|-----------------------------------|----------------------|
| **L0** | Lean kit; manual routing; hub may run without DB in some setups | **DB SSoT + API** — same as other profiles (ADR034) | `gate_history[]` and notes in `roadmap.yaml` remain human-file-authored; deploy does not overwrite them |
| **L2** | Full pipeline; engine enforced | **DB SSoT + API** for hub-registered WPs (AOS-V* format). **File-based SSoT** for spoke-native WPs (SNNN-PNNN-WPNNN) — no hub DB row exists; spoke team_100 direct edit + git commit as audit record (ADR034 R9) | DB `events` and related tables where implemented |
| **L2.5** | Managed pipeline; optional connectivity | **DB SSoT + API** when connected | Mix of YAML narrative + DB per deployment |
| **L3** | Future autonomous loop (not built) | **DB SSoT + API** | DB events + trust metrics (target) |

### Three Data Layers

1. **DB (SSoT)** — All canonical parameters: teams, gates, WPs (id, status, track, assigned teams, lod_status), projects, permissions, routing, templates. All mutations through API only.
2. **Deployed Snapshots** — definition.yaml, roadmap.yaml, projects.yaml. One-way deployment from DB. Read-only. Never edited manually when DB exists.
3. **Extending Files** — LOD specs (100-500), governance contract prose, mandates, verdicts, onboarding, lean-kit methodology, CLAUDE.md. Written by agents as part of normal work. Referenced by dashboard drill-down for detail views.

### Offline Work (Git Branch Isolation)

Work without database access is performed on an isolated git branch. The merge back to main includes validation tools that:
- Extract status changes and generate API calls to update DB
- Detect and alert on forbidden mutations (structured data edited in files)
- Ensure main branch always reflects DB-synchronized state

## Tracks

AOS v4.0.0 introduces a **Track Model** as the primary WP classifier. Tracks replace the v3 practice of using L-tier (L0/L2/L3) as a WP property — L-tiers describe AOS installation capability; Tracks describe the nature and shape of work.

**Canonical reference:** `governance/directives/ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL_v1.0.0.md` (binding definition; this section is a summary only).

### Six Tracks + One Modifier

| # | Track | Hebrew | Distinguishing trigger | Default engine |
|---|-------|--------|----------------------|----------------|
| 1 | **EXPRESS** | מהיר | ≤2 files OR ≤50 LOC, doc/config, risk LOW | claude-code or any-open |
| 2 | **STANDARD** | תקני | Code deliverable, single domain, design clear | claude-code or codex |
| 3 | **MANAGED** | מנוהל | HIGH risk, multi-team, new state machine, PARADIGM_SHIFT | cowork + claude-code |
| 4 | **RESEARCH** | חקר | No code deliverable; output = report/findings | gemini or any |
| 5 | **OPS** | תפעול | Infra/server/port/deploy; team_99 or port-registry edit | claude-code + team_99 |
| 6 | **CONTENT** | תוכן | Non-code artifact (book, video, design) | claude-desktop or cowork |
| + | **HOTFIX** | דחוף | Drop-everything modifier on any track; ≤4h worktree cap | any |

### Track Selection (binding decision tree)

```
START
  ├─ no code deliverable?
  │    ├─ findings/report? → RESEARCH
  │    └─ artifact (book/video/design)? → CONTENT
  ├─ infra/server/port/deploy? → OPS
  ├─ ≤2 files OR ≤50 LOC, doc/config? → EXPRESS
  ├─ HIGH risk OR multi-team OR new state machine? → MANAGED
  └─ otherwise → STANDARD

THEN: is it a production blocker / drop-everything? → attach HOTFIX modifier
```

### Sprint Discipline (project-level charter — NOT an Iron Rule)

AOS v4.0.0 establishes Sprint Discipline as a **project-level charter constraint** (ADR044 §5), NOT a System Iron Rule. The distinction matters: Iron Rules are constitutional and cannot be overridden even by team_00; Charter constraints can be adjusted by team_00 + team_100 with explicit justification.

Sprint Discipline: a sprint is ≤3 days / 1 engine / 1 writer / 1 deliverable. A WP spans 1–3 sprints; 4+ sprints requires restructure as Program. Sprint IDs use format `S[N].M[m].S[s]` (e.g., `S006.M1.S1`).

### L-Tier Redefinition (v4.0.0)

**L-tier is AOS install capability tier ONLY — never a WP property.** (ADR044 §4)

- **L0** (Lean): manual governance, no pipeline engine
- **L2** (Pipeline): full pipeline + DB + dashboard
- **L3** (Autonomous): full AUTO-ACTIVATION + autonomous routing (future)
- **L2.5**: RETIRED as of v4.0.0; replaced by MANAGED track for WP classification

Every AOS domain retains L0 as a valid operating mode regardless of installed tier ("תמיד יש fallback ל-L0" — team_00 directive, 2026-04-29).

*Team 100 | 2026-04-30 | "Tracks" section added — v4.0.0 Track Model summary per AOS-V4-WP-CHARTER; L-tier redefined; Sprint Discipline noted as project charter not IR*

---

## Iron Rules

These rules are constitutional. They apply at every level and cannot be overridden.

1. **Cross-engine validation:** The builder engine must differ from the validator engine
2. **Physical lean-kit:** `_aos/lean-kit/` is always a physical copy, never a symlink
3. **Repo-internal references:** `spec_ref` paths never point outside the repository
4. **Single-writer roadmap:** One agent holds write authority over roadmap.yaml at a time
5. **L-GATE_VALIDATE independence:** Always Team 190, constitutional, cross-engine, immutable
6. **Artifact communication:** Inter-team communication via file in `_COMMUNICATION/`, not chat
7. **Data authority — API-only mutations:** When a database is available, it is the single source of truth for all structured data **it represents**. Files are read-only deployed snapshots produced by `deploy_cascade`. ALL mutations to structured data (WP status, gate, lod_status, team engine/environment, project metadata) MUST go through the API for hub-native WPs (AOS-V* format, L0). Direct file edits to `roadmap.yaml`, `definition.yaml`, or `projects.yaml` for these fields are FORBIDDEN when the DB is running. **L2 spoke WP exception (ADR034 R9):** For spoke-native WPs (SNNN-PNNN-WPNNN format) with no hub DB row, the spoke `_aos/roadmap.yaml` is the file-based SSoT; spoke team_100 may edit operational state directly; git commit = audit record. This exception applies only where no hub DB row exists. Offline work is permitted only on an isolated git branch; the merge-back must go through the API or a reconciliation script that writes to DB first.

8. **Environment base / Domain override with approval:** The AOS environment (hub canon, lean-kit, governance, Iron Rules, directives) is the **base layer**. A domain (spoke) may define extensions or overrides — its own interaction protocols, glossaries, stage models, templates — **only** after: (a) explicit approval by **Team 00 (Principal)**, and (b) a conflict-check by **Team 100 (hub — Chief System Architect)** confirming the extension does not conflict with hub governance. Defaults inherit from the base; the domain layer adds on top without altering the base. Unauthorized spoke-side overrides of hub canon are violations under Iron Rules #11 (source→snapshot only) and #12 / ADR040 (authority lockdown). The mechanism for a sanctioned extension is: spoke files a GOVERNANCE_CHANGE_REQUEST (for base-layer change) OR a DOMAIN_PROTOCOL_PROPOSAL in `_COMMUNICATION/team_100/` (for local extension) → team_100 reviews conflict surface → team_00 signs off → extension is registered in spoke-side artifacts only (not propagated back to hub).

8b. **Port-registry SSoT ownership model:** "Team 60 is the SSoT owner of port-registry.yaml" means Team 60 holds **approval authority** over port assignments — any team may propose a port; Team 60 approves; the commit is made by whichever session owns the active WP. This is governance authority, not commit obligation. No server-session push rights to `lean-kit/` paths are required or granted for this role.

9. **IPv6-only WAN compatibility (Iron Rule #15):** Any AOS spoke running a service that initiates outbound connections from a Linux server (cloudflared, sync jobs, third-party API clients) MUST verify dual-stack outbound on initial deploy AND after any home-network change. When operating on an IPv6-only WAN — regardless of whether the ISP provides NAT64 — Linux servers MUST apply a mitigation matched to the specific scenario per the canonical mitigation matrix (`lean-kit/modules/12-home-server-infrastructure/WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md` §7). `clatd` alone is NOT sufficient when the ISP does not provide NAT64. Verification commands: `curl -4 https://1.1.1.1` (IPv4 outbound), `curl -6 https://www.cloudflare.com` (IPv6 outbound), `dig +short AAAA ipv4only.arpa` (NAT64 presence). Status artifact: `_aos/server_dual_stack_status.json` (refreshed by `wan_dual_stack_probe.sh`; surfaced by `validate_aos.sh` Check 45 in advisory `[SKIP:WARN]` mode). Architectural decision record: ADR048. Operational clause: `core/governance/team_99.md` "WAN Dual-Stack Verification" section. Empirical origin: 2026-05-01 TikTrack pilot-launch outage on Bezeq be fiber (IPv6-only WAN, no ISP-side NAT64).

## Why Not Jump Straight to L3

Two reasons:

1. **Complexity:** The gap between L0 (fully manual) and L3 (fully autonomous) is too large for a single architectural leap
2. **Agent improvement velocity:** AI agents improve dramatically every month. Building L3 too early means building it twice. L2 provides structured production capability while the ecosystem matures.

---

*Team 100 | 2026-04-12 | Revised: Purpose section, Data Authority Model, Iron Rule #7 — per System Designer direction*
*Team 100 | 2026-04-16 | Iron Rule #7 extended: API-only mutations for ALL profiles including L0; DB is SSoT across all managed projects (V320 DB Full Migration)*
*Team 100 | 2026-04-16 | Data Authority Model: "The Rule" + By Profile table aligned with ADR034; profile = automation mode, not file-SSoT for structured data when DB online*
*Team 100 | 2026-04-25 | Iron Rule #7 + Data Authority L2 row: L2 spoke WPs (SNNN-PNNN-WPNNN, no hub DB row) are file-based SSoT per ADR034 R9; spoke team_100 direct edit permitted*

---

## Team Classification — `gate_participation`

Every team carries a `gate_participation` classification that describes its
relationship to the canonical gate process. This is complementary to
`operating_mode` (which describes the team's **technical operating behavior**):
`gate_participation` describes **how the team relates to gates**, `operating_mode`
describes **how the team runs technically**.

### Canonical values

| Value | Meaning | Teams |
|-------|---------|-------|
| `IN_GATE` | Operates inside the canonical gate process — builder/validator/QA role | team_10, team_20, team_50, team_60, team_90, team_100, team_110, team_170, team_190, team_191, team_40, team_70, team_80, team_30 |
| `OUT_OF_GATE_ISOLATED` | Works outside the gate process in an isolated environment; merges require post-hoc L-GATE_VALIDATE by team_190 | **team_98**, **team_99**, **team_200** |
| `PIPELINE_FEEDER` | Produces artifacts that feed the gate pipeline (e.g., design, research) but does not operate gates | **team_35** |
| `PRINCIPAL` | Human operator — above the gate process, authorizes everything | team_00 |

---

## `OUT_OF_GATE_ISOLATED` Pattern (v1.7.0 — 2026-04-22)

### Rationale

Three teams operate **outside the canonical gate process** on **immediate-execution**
tasks: team_98 (Phone Joker via Dispatch), team_99 (Home Server Team via SSH),
team_200 (Cowork Bundle via Claude Desktop Project). They share the same operating
model despite different technical environments.

What protects governance integrity for these teams — given that they bypass the
gate flow — is **strict environmental isolation** from the general development
workflow. Each operates in a space separated from the day-to-day dev environments
of the standard gate teams.

### Three canonical rules (team_00 directive 2026-04-22)

**Rule 1 — Authorization.** Work outside the gate process is permitted ONLY when:
- **(a)** the team is configured with `gate_participation: OUT_OF_GATE_ISOLATED` as
  its permanent default (team_98, team_99, team_200), **OR**
- **(b)** an individual team receives explicit **team_00 formal approval** with a
  predefined scope artifact in `_COMMUNICATION/team_00/APPROVAL_*.md`.

No team may self-declare or improvise out-of-gate operation.

**Rule 2 — Environment isolation (mandatory).** All out-of-gate work REQUIRES an
isolated environment separated from general development environments. Isolation is
realized per team:
- team_98: ephemeral Claude Desktop Dispatch worktrees (random-name branches)
- team_99: separate physical machine (home server) + SSH tunnel
- team_200: Claude Desktop Project with locked Custom Instructions + dedicated bundle branch

**Rule 3 — Canonical validation before merge.** Code changes produced out-of-gate
MUST pass L-GATE_VALIDATE by **team_190** (cross-engine Iron Rule #1) before any
merge to `main`. Self-tests run by the out-of-gate team are pre-validation, not
a substitute. For team_99 specifically, infrastructure/server operations without
repo commits do not trigger this rule — it applies only to code merges.

### Why these teams cannot self-validate

Iron Rule #1 (cross-engine validation) requires builder engine ≠ validator engine.
The three out-of-gate teams cannot satisfy this because:
- Each session is independent; there is no way to hand work off to a different
  engine within the same session.
- The tests they run are self-tests (unit/integration), not cross-engine
  constitutional validation.

Therefore team_190 (Constitutional Validator, cursor-composer-2 engine) provides
the required cross-engine validation post-hoc, before merge.

### Shared operational attributes (verified per team contract)

- `operating_model: ISOLATED_BRANCH`
- `canonical_validator: team_190`
- `in_gate_process: 0`
- No worktree or branch creation without explicit team_00 approval
- All work on feature branch — never direct commit to main
- Self-tests required before requesting canonical validation
- Identity header mandatory on every artifact

### Lineage

Pattern canonicalized 2026-04-22 following CLARIFICATION-TEAM98-OPERATING-MODEL
from team_98 (Dispatch session) and in-session directive by team_00 (Principal).
Prior governance (pre-v1.7.0) incorrectly labeled team_98 as advisory-only.
The corrected model recognizes team_98/99/200 as isolated-branch builders with
post-hoc canonical validation.

*Team 100 | 2026-04-22 | `gate_participation` classification + `OUT_OF_GATE_ISOLATED` pattern — per team_00 directive, closes CLARIFICATION-TEAM98-OPERATING-MODEL-2026-04-22*
