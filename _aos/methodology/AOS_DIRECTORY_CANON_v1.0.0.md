---
id: AOS_DIRECTORY_CANON_v1.0.0
from: Team 100 (Chief System Architect)
date: 2026-04-16
version: 1.1.1
status: ACTIVE
authority: Team 00 + Team 100
purpose: SSoT for AOS file structure — every path is canonical and binding
---

# AOS Directory Canon v1.0.0

This document is the **Single Source of Truth** for directory structure across all AOS-managed projects. Every path listed here is canonical. Files not listed here are either project-specific application code or require a canon amendment to be introduced.

---

## Terminology

| Term | Directory | Scope | Description |
|------|-----------|-------|-------------|
| **AOS Engine** | `core/` | AOS project only | Pipeline engine source code, DB schema, seed data, API. |
| **AOS Kit** | `lean-kit/` | AOS project only | Methodology source — modules, templates, profiles. Copied to projects as snapshots. |
| **Project Governance** | `_aos/` | Every project | Operational snapshot — team definitions, governance contracts, roadmap, ideas, lean-kit copy. Self-contained per Iron Rule #8. |
| **AOS Project** | `agents-os` repo | Source of truth | The project that IS the AOS system. Contains engine + kit + its own governance. Source for all snapshots. |
| **Spoke Project** | Other repos | Snapshot consumer | Projects managed by AOS. Contain `_aos/` governance snapshot only. No `core/` or `lean-kit/` source. |

**Source-of-truth chain:**
- `core/governance/` (AOS project) = **source** for team governance contracts
- `_aos/governance/` (AOS project) = snapshot of `core/governance/` (AOS project governs itself)
- `_aos/governance/` (spoke projects) = snapshot from AOS project's `core/governance/`
- `__ONBOARDING` files = generated from template, reference `_aos/governance/` (never `core/governance/` directly)
- Spoke projects may add local overrides in `_aos/governance/overrides/` but cannot modify base files

Changes originate in the AOS project → propagate to `_aos/` in all projects (including AOS itself).

**Session write isolation (binding):** Write authority is always scoped to the active session's repository. An agent operating in a spoke session (TikTrack, SmallFarms, etc.) may NOT write to or push from the `agents-os` hub. AOS-level concerns identified during a spoke session are filed as artifacts in the spoke's `_COMMUNICATION/team_XX/` with `for_hub: true` frontmatter, committed to the spoke repo, and routed to the hub by Team 00 in a separate AOS session. "Push everything" means push the active session's repo only — never cross-repo.

**Platform vs domain (binding):**

- **Platform layer (AOS hub):** Repository `agents-os` — `core/`, `lean-kit/`, `methodology/`, and hub `core/governance/` as SSoT. Changing platform governance or methodology follows this canon and `methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.0.0.md` (Team 100 executes hub `core/governance/` edits; Team 00 approves as defined there).
- **Domain layer (each spoke):** Product code, product documentation, and domain conventions live in the spoke repository (`_aos/context/`, project docs, application trees). The **lead architect for that domain** (per `core/definition.yaml` and project routing) owns architectural decisions **within that domain**; the hub does not substitute for a product team’s domain owner.
- **Overrides:** Any change that **overrides** a default AOS mechanism (including material use of `_aos/governance/overrides/`) requires **Team 00 written approval** in a communication artifact plus **AOS authorization** — confirmation from the hub layer (Team 100) that the platform permits the override. Additive domain-only material that does not alter AOS defaults remains in domain scope. Where a domain publishes **domain iron rules** in hub contracts (e.g. `## TikTrack Domain Rules` in `core/governance/team_*.md`), those rules apply **when operating in that domain** in addition to universal rules.

---

## Part 1: Project-Level Structure (Every Project)

Every AOS-managed project MUST have this structure at its root:

```
[project-root]/
│
│── _aos/                              # GOVERNANCE LAYER (canonical, required)
│   ├── definition.yaml                # Team definitions snapshot (from hub, Iron Rule #8)
│   ├── roadmap.yaml                   # WP state registry (WHAT/WHEN)
│   ├── ideas.json                     # Idea pipeline (pre-GATE_0 incubator)
│   ├── team_assignments.yaml          # Team-to-role mapping (WHO)
│   ├── metadata.yaml                  # Provenance: lean_kit_version, SHA, profile
│   ├── README.md                      # What _aos/ is and single-writer rule
│   ├── MILESTONE_MAP.md               # Milestone descriptions
│   │
│   │
│   ├── governance/                    # PER-TEAM GOVERNANCE CONTRACTS (required)
│   │   └── team_[ID].md              # Operational contract: iron rules, trigger protocol, boundaries
│   │
│   ├── context/                       # AGENT ACTIVATION (required)
│   │   ├── PROJECT_CONTEXT.md         # **First read** — thin AOS layer + team entry + domain (see schema below)
│   │   ├── ACTIVATION_ARCH.md         # Architecture agent activation
│   │   ├── ACTIVATION_BUILDER.md      # Builder agent activation
│   │   └── ACTIVATION_VALIDATOR.md    # Validator agent activation
│   │
│   ├── work_packages/                 # LOD CHAIN — two-level structure (amended v1.0.0+2)
│   │   ├── S[N]/                      # STAGE DIRECTORY (one per milestone)
│   │   │   └── LOD300_milestone.md    # Milestone Scope Doc — planning artifact covering all WPs
│   │   │                              # in this stage. Recognized artifact type. NOT a WP spec.
│   │   │                              # Required: named LOD300_milestone.md (not LOD300_spec.md)
│   │   └── S[N]-P[M]-WP[K]/          # WP DIRECTORY (one per work package, ID = dir name)
│   │       ├── LOD100_scope.md        # Scope statement (at L-GATE_ELIGIBILITY)
│   │       ├── LOD200_concept.md      # Concept design (Track B only, at L-GATE_CONCEPT)
│   │       ├── LOD400_spec.md         # Executable spec with ACs (required at L-GATE_SPEC)
│   │       └── LOD500_asbuilt.md      # As-built fidelity record (required at L-GATE_BUILD)
│   │
│   │   # WP ID FORMAT: S[stage]-P[program]-WP[number]  (e.g. S003-P003-WP005)
│   │   # Full standard: lean-kit/modules/project-governance/WP_ID_STANDARD.md
│   │
│   │   # SPRINT (v4.0.0 — ADR044 §5): sub-WP execution unit
│   │   # A sprint is ≤3 days / 1 engine / 1 writer / 1 deliverable (project-level charter)
│   │   # Sprint ID format: S[N].M[m].S[s]  (e.g. S006.M1.S1 = Stage 6, Milestone 1, Sprint 1)
│   │   # 1 WP = 1–3 sprints; 4+ sprints → restructure as Program (S[N]-P[M] level)
│   │   # Sprint artifacts live in the WP directory; sprint is a logical unit, not a directory
│   │
│   └── lean-kit/                      # METHODOLOGY SNAPSHOT (physical copy, NEVER symlink)
│       ├── LEAN_KIT_VERSION.md
│       ├── MODULE_INDEX.md
│       ├── VERSION_POLICY.md
│       ├── profiles/
│       │   ├── L0.yaml
│       │   ├── L2.yaml
│       │   └── L3.yaml
│       └── modules/                   # See Part 3 for module breakdown
│
│── _archive/                           # COMPLETED WP ARTIFACTS (canonical archive)
│   └── [WP-ID]/                       # One directory per completed WP
│       ├── ARCHIVE_MANIFEST.md        # Manifest: source, date, file count, team
│       └── [archived artifacts]       # Moved from _COMMUNICATION/ at WP closure
│
│── _COMMUNICATION/                    # INTER-TEAM ARTIFACTS (required)
│   ├── team_00/                       # System Designer
│   ├── team_100/                      # Architecture Agent
│   ├── team_110/                      # Builder Agent
│   ├── team_190/                      # Validator Agent
│   └── [additional teams as needed]
│
│── .cursorrules                       # ENGINE CONTEXT: Cursor (required)
│── CLAUDE.md                          # ENGINE CONTEXT: Claude Code (required)
│── AGENTS.md                          # ENGINE CONTEXT: Codex/Generic agents (required)
│── .github/workflows/
│   └── aos-governance-integrity.yml   # REQUIRED CI module: run validate_aos.sh on push/PR
│── .claude/
│   └── settings.json                  # ENGINE SETTINGS: Claude Code (required)
│
│── [application code]                 # PROJECT-SPECIFIC (not governed by canon)
```

### L2 Projects Additionally Have:

```
[project-root]/
│── aos_engine/                        # L2 ENGINE (sibling to _aos/, not inside)
│   └── [engine code]
```

`metadata.yaml` must include `aos_engine_version` for L2 profiles.

---

## Part 1a — `PROJECT_CONTEXT.md` schema (all projects)

**Purpose:** One thin file every agent reads first. Avoid duplicating full governance prose or other domains’ product text.

**Required top-level sections (exact `##` headings):**

| Section | Content |
|---------|---------|
| `## AOS environment (read first)` | Repo role (hub vs spoke), profile (L0/L2), pointers only: `_aos/roadmap.yaml`, `_aos/project_identity.yaml`, `_aos/governance/` (snapshots). **Max ~15 lines.** |
| `## Team entry` | **Single primary pointer** — path to the activation file for the default builder/architect role *or* latest handoff under `_COMMUNICATION/team_XXX/` when session-scoped. Example: `_aos/context/ACTIVATION_ARCH.md`. |
| `## Domain profile` | Product/domain facts for **this** repo only — fixed subheadings: `### What this product is`, `### Current focus`, `### Standards / SSOT` (paths into domain docs). No TikTrack (or other spoke) content in a non-TT repo. |

**Template (copy per new project):** `lean-kit/modules/project-governance/config_templates/PROJECT_CONTEXT.md.template`

**TikTrack-only rules on demand:** reference `_aos/lean-kit/modules/project-governance/TT_DOMAIN_RULES_CANON_v1.0.0.md` from `PROJECT_CONTEXT` *or* from team contracts (pointer); do not paste long TT prose into hub-wide files.

---

## Part 2: AOS Project Structure (agents-os only)

The AOS Project has additional directories that spoke projects do NOT have:

```
agents-os/
│
│── _aos/                              # Same as Part 1 (self-governing)
│   ├── projects.yaml                  # Managed project registry (AOS Project only, amendment v1.0.0a)
│── _archive/                           # Same as Part 1 (completed WP artifacts)
│── _COMMUNICATION/                    # Same as Part 1 (expanded team list)
│── .cursorrules                       # Same as Part 1
│── CLAUDE.md                          # Same as Part 1
│── .claude/settings.json              # Same as Part 1 (+ additionalDirectories to ALL spokes)
│
│── lean-kit/                          # METHODOLOGY SOURCE (canonical, modules live here)
│   ├── LEAN_KIT_VERSION.md
│   ├── MODULE_INDEX.md
│   ├── VERSION_POLICY.md
│   ├── profiles/
│   └── modules/                       # See Part 3
│
│── methodology/                       # METHODOLOGY DOCS (governance standards, not code)
│   ├── AOS_CONCEPT_AND_PRINCIPLES.md  # Vision, evolution, iron rules
│   ├── AOS_DIRECTORY_CANON_v1.0.0.md  # THIS FILE — SSoT for structure
│   ├── gate-model/                    # Gate lifecycle, Team 190 constitution
│   │   ├── 00_INDEX_CANONICAL.md      # Gate model index
│   │   └── [gate protocols, iron rules, registries]
│   ├── lod-standard/                  # LOD specification standard
│   └── iron-rules/                    # Iron rules (constitutional)
│
│── governance/                        # LOCKED DECISIONS (directives + standards)
│   ├── directives/                    # 187+ architect directives (historical + active)
│   │   └── 00_MASTER_INDEX.md         # Directives catalog
│   ├── standards/                     # Documentation standards
│   ├── KNOWN_BUGS_REGISTER_v1.0.0.md
│   └── TIKTRACK_REFERENCE_POINTERS.md # Migration reference
│
│── core/                              # L2 ENGINE CODE (Python pipeline)
│   ├── definition.yaml                # SSoT: teams, gates, phases (WHO/HOW for DB)
│   ├── pipeline_state.json            # L2 pipeline state
│   ├── FILE_INDEX.json                # Engine file catalog
│   ├── seed.py                        # Database seeding
│   ├── cli/                           # Pipeline CLI
│   ├── db/                            # Database migrations
│   ├── governance/                    # Team role definitions (from definition.yaml)
│   ├── modules/                       # Python modules (audit, governance, routing, state, etc.)
│   ├── tests/                         # Engine tests
│   └── ui/                            # Legacy UI (v3 dashboard)
│
│── dashboard/                         # V3.1.2 DASHBOARD (HTML/CSS/JS)
│   ├── index.html                     # Dashboard entry
│   ├── mockups/                       # Mockup prototypes
│   ├── data/                          # Dashboard data files
│   ├── js/                            # Dashboard JavaScript
│   └── scripts/                       # Build/serve scripts
│
│── documentation/                     # SYSTEM DOCUMENTATION (migrated from TikTrack)
│   ├── 00_AGENTS_OS_MASTER_INDEX.md   # Master entry point
│   ├── 01-OVERVIEW/                   # System overviews
│   ├── 02-ARCHITECTURE/               # Architecture docs + API reference
│   ├── 03-CLI-REFERENCE/              # Pipeline CLI reference
│   ├── 04-PROCEDURES/                 # Developer runbooks
│   └── 05-TEMPLATES/                  # Validation checklists
│
│── scripts/                           # UTILITY SCRIPTS
│   └── db/check_db_connectivity.py    # REQUIRED DB-first connectivity checker (hub)
│── projects/                          # PROJECT CONFIGS (spoke registrations)
│── idea_scan.sh                       # Idea pipeline scanner → _aos/ideas.json
│── idea_submit.sh                     # Idea pipeline submitter → _aos/ideas.json
│── pipeline_run.sh                    # L2 pipeline runner
└── AGENTS.md                          # Agent definitions (legacy, review needed)
```

---

## Part 3: Lean-Kit Module Structure

11 modules, each self-contained:

| # | Module ID | Purpose | Required By |
|---|-----------|---------|-------------|
| 01 | project-governance | `_aos/` layout, YAML schemas, ideas.json, examples | L0, L2, L3 |
| 02 | gate-workflow | Gate definitions (E, C, S, B, V) | L0, L2, L3 |
| 03 | team-model | Role definitions (SD, arch, builder, validator, doc, gateway) | L0, L2, L3 |
| 04 | document-lifecycle | LOD templates (100, 200, 300, 400, 500) | L0, L2, L3 |
| 05 | dashboard-observability | Dashboard data build scripts | L2, L3 |
| 06 | agent-activation | ACTIVATION_*.md.template files | L0, L2, L3 |
| 07 | automation-cli | CLI automation (future) | L3 |
| 08 | validation-quality | validate_aos.sh (15 checks) | L0, L2, L3 |
| 09 | version-identity | Version tracking | L0, L2, L3 |
| 10 | migration-lifecycle | L0→L2 migration procedures | L2, L3 |
| 11 | standards-conventions | RTL/BiDi, naming conventions | L0, L2, L3 |

Each module contains:
```
modules/[module-id]/
  MODULE.md              # Module metadata + contents list
  [module-specific dirs and files]
```

---

## Part 4: SSoT Path Registry

These paths are **binding** — the system (code, agents, dashboard) must use exactly these paths:

### Governance Data (per project)

| Data | Canonical Path | Format | Owner |
|------|---------------|--------|-------|
| Team definitions | `_aos/definition.yaml` | YAML | Snapshot from hub (Iron Rule #8) |
| Team governance | `_aos/governance/team_[ID].md` | Markdown | Per-team operational contracts (iron rules, trigger protocol, boundaries) |
| Work packages | `_aos/roadmap.yaml` | YAML v1.1 | Active agent (per gate) |
| Ideas | `_aos/ideas.json` | JSON v1.1 | team_100 / team_00 |
| Teams | `_aos/team_assignments.yaml` | YAML | System designer |
| Provenance | `_aos/metadata.yaml` | YAML | Build process |
| Project context | `_aos/context/PROJECT_CONTEXT.md` | Markdown | Architecture agent |
| Activation (arch) | `_aos/context/ACTIVATION_ARCH.md` | Markdown | From template |
| Activation (builder) | `_aos/context/ACTIVATION_BUILDER.md` | Markdown | From template |
| Activation (validator) | `_aos/context/ACTIVATION_VALIDATOR.md` | Markdown | From template |
| LOD300 milestone scope | `_aos/work_packages/S[N]/LOD300_milestone.md` | Markdown | Stage planning artifact — covers all WPs in milestone. Not a WP spec. |
| LOD specs (per WP) | `_aos/work_packages/S[N]-P[M]-WP[K]/LOD[N]_*.md` | Markdown | Per LOD level. WP directory name = canonical WP ID. |
| Methodology | `_aos/lean-kit/` | Physical copy | Snapshot at onboarding |
| DB checker status artifact | `_aos/db_connectivity_status.json` | JSON | Generated by DB checker on failure or explicit evidence run |

### Hub-Only Data (agents-os)

| Data | Canonical Path | Format | Owner |
|------|---------------|--------|-------|
| Managed projects | `_aos/projects.yaml` | YAML | Team 00 |
| Engine seed | `core/definition.yaml` | YAML | Team 00 |
| Pipeline state | `core/pipeline_state.json` | JSON | Pipeline engine |
| Methodology source | `lean-kit/` | Directories | Team 100 |
| Governance directives | `governance/directives/` | Markdown | Team 00 / Team 100 |
| Gate model | `methodology/gate-model/` | Markdown | Team 00 |
| LOD standard | `methodology/lod-standard/` | Markdown | Team 100 |
| Directory canon | `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` | Markdown | Team 100 |
| Vision | `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` | Markdown | Team 100 |

### Archive (per project)

| Data | Canonical Path | Format | Owner |
|------|---------------|--------|-------|
| Completed WP artifacts | `_archive/[WP-ID]/` | Directory | Team 191 (under Team 00 mandate) |
| Archive manifest | `_archive/[WP-ID]/ARCHIVE_MANIFEST.md` | Markdown | Team 191 |

### Engine Context (per project)

| Engine | Context File | Settings File |
|--------|-------------|---------------|
| Claude Code | `CLAUDE.md` | `.claude/settings.json` |
| Cursor | `.cursorrules` or `.cursor/rules/*.mdc` | — |
| OpenAI Codex | `_aos/context/ACTIVATION_VALIDATOR.md` | — |

### Inter-Team Communication (per project)

| Path | Purpose |
|------|---------|
| `_COMMUNICATION/team_[ID]/` | Team-specific artifacts. Own team: full write. Any team: may deliver inter-team MSG/RESPONSE/mandate/verdict artifacts here (inbox delivery — see Part 5). |
| `_COMMUNICATION/team_[ID]/__ONBOARDING_TEAM_[ID].md` | **Required.** Team onboarding file — identity, iron rules, project context, mandatory reads. Prefix `__` ensures it sorts first in directory listings. Every team directory MUST have this file. |
| `_COMMUNICATION/team_[ID]/[WP-ID]/` | WP-scoped artifacts. Files produced in the context of a specific WP MUST be placed here. WP-ID must match an `id:` entry in `_aos/roadmap.yaml`. |
| `_COMMUNICATION/_ARCHITECT_INBOX/` | Agent submission queue (hub only) |
| `_COMMUNICATION/_Architects_Decisions/` | Locked architectural decisions (hub only) |

#### WP Subfolder Rule (Iron Rule #12)

When a file is associated with a specific Work Package, it MUST be placed in a subfolder
named after the WP ID, not at the flat team directory root.

- **WP-scoped file:** `_COMMUNICATION/team_[ID]/[WP-ID]/FILENAME_v1.0.0.md`
- **Non-WP file (root):** `_COMMUNICATION/team_[ID]/HANDOFF_TEAM_100_TO_110_2026-04-11.md`
- **Onboarding (always root):** `_COMMUNICATION/team_[ID]/__ONBOARDING_TEAM_[ID].md`

`__` prefix = always root. Any filename beginning with `__` is exempt from this rule.

Forward-looking only. Existing flat files are grandfathered. WP IDs sourced from `_aos/roadmap.yaml`.

---

## Part 5: Per-Team Write Authority (Iron Rule)

This table is the **canonical source of truth** for which teams may write to `_aos/`.
All governance contracts, activation prompts, cursorrules, CLAUDE.md, and AGENTS.md
MUST be consistent with this table.

| Team | `_aos/roadmap.yaml` | `_aos/work_packages/` | `_aos/lean-kit/` | `_aos/governance/` | `_COMMUNICATION/` |
|------|:-------------------:|:---------------------:|:----------------:|:------------------:|:-----------------:|
| team_00 | W | W | R | W (via hub) | W |
| team_100 | W | W | R | R | W (own dir) |
| team_110 | — | W (mandated) | R | R | W (own dir) |
| team_191 | mandate only | mandate only | R | propagation | W (own dir) |
| team_10/20/30/40/50/60/70/80/90/99/170/190 | — | — | R | R | W (own dir) |

**W** = write authorized. **R** = read only. **—** = forbidden (no writes without explicit Team 00 mandate).

**Inbox delivery exception (all teams):** Any team may write `MSG-*.md`, `*-RESPONSE.md`, mandate, and verdict artifacts to **any** `_COMMUNICATION/team_[ID]/` folder for inter-team message delivery. This is the only cross-team write permitted in `_COMMUNICATION/`. Receiving team folders are publicly writable for these inter-team artifact types only. All other artifact types remain own-dir-only.

**Iron Rule:** Non-governance teams (all except team_00/100/110/191) MUST route any `_aos/`
change request as an artifact to `_COMMUNICATION/team_100/`. They MUST NOT write to any
subdirectory of `_aos/` directly — this includes roadmap.yaml, work_packages/, lean-kit/, and governance/.

**Enforcement:** Each non-governance team's governance contract in `core/governance/team_[ID].md`
carries an explicit `iron_rules:` entry prohibiting `_aos/` writes. `validate_aos.sh` **Check 18**
verifies `_aos/` write authority across governance snapshots. **Check 19** verifies that every
`team_*.md` snapshot includes the **API-only structured-data** clause (Iron Rule #7 extension) per
`methodology/AOS_CONCEPT_AND_PRINCIPLES.md` and `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`.

---

## Part 6: Iron Rules for Directory Structure

1. **`_aos/lean-kit/` = physical copy.** Never symlink. `diff -rq lean-kit/ _aos/lean-kit/` must produce no output at snapshot time.

2. **`_aos/` is self-contained.** A project cloned without the hub must still have all governance artifacts.

3. **`_COMMUNICATION/` = artifact only.** No data files (ideas, roadmaps, configs). Data lives in `_aos/`.

4. **Engine context files at project root.** `.cursorrules` and `CLAUDE.md` are root-level, not inside `_aos/`.

5. **Hub additional directories in settings.json.** All spokes must list agents-os in `.claude/settings.json` `additionalDirectories`.

6. **No legacy naming.** PHOENIX_IDEA_LOG → ideas.json. All paths use current canonical names.

7. **Modules are self-contained.** Each lean-kit module has MODULE.md. No cross-module file dependencies without explicit declaration in MODULE.md `depends_on`.

8. **Project repos function independently.** Every AOS-managed project repository must be operational when cloned and accessed in isolation from the agents-os hub. This includes: all governance artifacts in `_aos/`, engine context at root, methodology in `_aos/lean-kit/`, and team definitions in `_aos/definition.yaml` (snapshot from hub). Required for: remote developer environments, CI/CD pipelines, archival, and local development without network access. Independence verified by `validate_aos.sh`.

9. **Team numbers are universal.** Team ID numbers represent roles (10=Gateway/Builder, 20=Backend, 30=Frontend, 50=QA, 60=DevOps, 70=Docs, 110=Domain Architect). Same number = same role across all projects. No domain-suffix numbering. Team 10 is dual-mode: orchestrator in layered-team WPs, solo builder in single-team WPs — mode decided by Team 00 at the human gate. See `_COMMUNICATION/_Architects_Decisions/ARCHITECT_DIRECTIVE_TEAM_10_DUAL_MODE_v1.0.0.md`.

10. **No stale worktrees on disk.** Git worktrees created by mobile/app environments (e.g. Claude Code phone sessions) leave full repository copies inside `.claude/worktrees/`. These must be removed after use (`git worktree remove` + `git worktree prune`). Stale worktrees contain old file versions that pollute `grep` and `find` results, causing validation failures. `.claude/worktrees/` must be in `.gitignore`.

11. **Governance flows source → snapshot.** Team governance contracts originate in the AOS project's `core/governance/`. They propagate to `_aos/governance/` in the AOS project itself (self-governance) AND to all spoke projects via snapshot copy. Onboarding files (`__ONBOARDING`) are generated from the lean-kit template and reference `_aos/governance/` — never `core/governance/` directly. Spoke projects may add local overrides in `_aos/governance/overrides/` but cannot modify base governance files. Every update to `core/governance/` requires re-propagation to all `_aos/governance/` instances.

12. **WP-scoped communication artifacts in WP subfolders.** Any `_COMMUNICATION/team_[ID]/` file that belongs to a specific Work Package MUST be placed in a subfolder named after the WP ID (e.g., `_COMMUNICATION/team_110/AOS-V312-WP-GOV/`). Non-WP files (onboarding, general handoffs) stay at the directory root. `__`-prefix files always at root. Forward-looking — existing flat files grandfathered. WP IDs from `_aos/roadmap.yaml`.

13. **WP IDs use canonical three-segment format.** All Work Package IDs registered after 2026-04-11 MUST use the format `S[stage]-P[program]-WP[number]` (e.g., `S003-P003-WP005`). Informal labels (WP-A1, WP-A2, WP-1...) are execution shorthand only — never canonical IDs and never used in `roadmap.yaml`, `spec_ref`, or directory names. WP MUST be registered in `roadmap.yaml` no later than L-GATE_SPEC. **Grandfathering clause:** WPs registered before 2026-04-11 (including all `AOS-V310-*`, `AOS-V311-*`, and `AOS-V312-*` IDs in the hub roadmap) retain their existing IDs — no renaming required. Forward-looking only: all new WPs from 2026-04-11 must use the canonical format. Full standard: `lean-kit/modules/project-governance/WP_ID_STANDARD.md`.

14. **AOS system commands use the `AOS_` prefix.** All Claude Code commands (`.claude/commands/*.md`) that implement AOS methodology operations MUST use the filename prefix `AOS_` (e.g., `AOS_qa.md`, `AOS_gate-mandate.md`, `AOS_gov-sync.md`). This applies to hub and all spoke projects. Rationale: namespace isolation — distinguishes AOS methodology commands from general-purpose tools, anthropic-skills, and project-specific commands. Project-specific commands (not part of AOS methodology) MAY omit the prefix. Commands defined before 2026-04-12 have been migrated — no grandfathering.

15. **Completed WP artifacts archive to `_archive/`.** When a WP reaches status=COMPLETE (LOD500_LOCKED after L-GATE_VALIDATE PASS), all communication artifacts from `_COMMUNICATION/team_*/[WP-ID]/` MUST be moved to `_archive/[WP-ID]/`. Each archived WP directory MUST contain an `ARCHIVE_MANIFEST.md` listing: source paths, archive date, file count, archiving team. The archive procedure MUST include a misplaced artifact scan — detect WP-scoped files incorrectly placed at team root directories instead of WP subdirectories (violation of Iron Rule #12). `_archive/` is flat (one level of WP-ID directories, no nesting). Team 191 executes archiving under Team 00 mandate. No permanent deletions — only moves. `_COMMUNICATION/99-ARCHIVE/` is deprecated; `_archive/` at project root is the canonical archive path.

---

## Part 7: Compliance Verification

Run on any project: `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh [project-root]`

Additional checks (not yet automated):
- [ ] `_aos/ideas.json` exists and is valid JSON
- [ ] `.cursorrules` exists
- [ ] `CLAUDE.md` exists
- [ ] `.claude/settings.json` exists with `additionalDirectories` pointing to hub
- [ ] `_COMMUNICATION/` has at minimum: team_00, team_100, team_110, team_190
- [ ] DB checker available at `scripts/db/check_db_connectivity.py` (hub) and used before offline exception writes

---

*Team 100 | AOS Directory Canon v1.1.0 | 2026-04-06 | Amended 2026-04-11 (v1.0.0+3 — two-level work_packages/, WP ID Iron Rule #13 + grandfathering clause)*
*Amendment: Added WP Subfolder Rule (Iron Rule #12) for `_COMMUNICATION/` structure.*
*Amended 2026-04-12 (v1.0.0+4 — Iron Rule #9: Team 10 dual-mode Gateway/Builder; mode decision protocol at human gate)*
*Amended 2026-04-12 (v1.0.0+5 — Iron Rule #14: AOS_ command prefix convention)*
*Amended 2026-04-15 (v1.0.0+6 — `_archive/` canonical path, Iron Rule #15: archive compliance, SSoT Path Registry archive section)*
*Amended 2026-04-15 (v1.0.1 — Platform vs domain layers; override authorization; domain lead architect scope — see Terminology)*
*Amended 2026-04-15 (v1.0.2 — Part 1a: PROJECT_CONTEXT.md schema; TT-DOM canon file in lean-kit; pointer-only team contracts)*
*Amended 2026-04-15 (v1.1.0 — Part 5 added: Per-Team Write Authority table; Parts renumbered 5→6, 6→7; _aos/ write authority enforced via iron rules + Check 18)*
*Amended 2026-04-16 (v1.1.1 — Part 5 enforcement: `validate_aos.sh` Check 19 — API-only / Iron Rule #7 clause in all team contracts; aligns with V320)*
*Status: ACTIVE — all projects must comply. Amendments require Team 00 approval.*
