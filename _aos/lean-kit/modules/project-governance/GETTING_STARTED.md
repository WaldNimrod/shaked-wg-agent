# Getting Started with AOS Governance

How to set up a new project with AOS in-repo governance.

> **Shortcut:** Use the `/project-init` skill to automate steps 1–17 interactively.

---

## 1. The `_aos/` Directory

Every AOS-managed project has an `_aos/` directory at its root. This is the governance layer.

```
my-project/
  _aos/
    roadmap.yaml              # WP registry + gate_history; when engine DB is online, canonical structured fields are DB/API + deploy (see hub `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`)
    ideas.json                # Idea pipeline (pre-GATE_0 incubator)
    team_assignments.yaml     # Team-to-role mapping
    metadata.yaml             # Lean-kit version + active modules
    README.md                 # What _aos/ is and how to use it
    MILESTONE_MAP.md          # Human-readable milestone index
    project_identity.yaml     # Cross-project boundary declaration (REQUIRED — Check 12)
    governance/               # Read-only snapshots (propagated from hub)
      definition.yaml
      team_*.md               # One file per active team
    context/
      PROJECT_CONTEXT.md      # Project background for agents
      ACTIVATION_ARCH.md      # Architecture agent activation
      ACTIVATION_BUILDER.md   # Builder agent activation
      ACTIVATION_VALIDATOR.md # Validator agent activation
    lean-kit/                 # Physical copy of methodology (NEVER symlink)
      modules/
    work_packages/
      [WP-ID]/
        LOD100_scope.md
        LOD200_concept.md
        LOD400_spec.md
        LOD500_asbuilt.md
  _COMMUNICATION/             # Inter-team artifact exchange
    team_00/                  # System Designer
    team_99/                  # Home Server DevOps (if deployed services)
      __ONBOARDING_TEAM_99.md
    team_100/                 # Architecture Agent
    team_110/                 # Builder Agent
    team_190/                 # Validator Agent
  CLAUDE.md                   # Claude Code project instructions
  .cursorrules                # AI agent context rules (all engines)
  .claude/settings.json       # Claude Code settings (additionalDirectories → hub)
```

---

## 2. Choose Your Profile

→ **Full guide:** `lean-kit/PROFILE_SELECTION_GUIDE.md`

| Profile | What it means | Research rounds | Human gates | Example |
|---------|--------------|-----------------|-------------|---------|
| **L0** | Lean governance only, no engine | Optional | 0 | AOS-Sandbox-Lean |
| **L2** | Full governance + engine + dashboard | Optional | 0 | TikTrack, AOS-Sandbox-Full |
| **L2.5** | Managed agent pipeline (complex WPs) | R1/R2/R3 mandatory | 2 (Team 00 only) | SBXF-P001-WP-L25-001 |
| **L3** | CLI-driven, future | TBD | TBD | Not yet built |

**Use L2.5 when:** ≥2 teams with integration contracts, MEDIUM/HIGH risk, new state machine (≥5 states), or new API/data model.

L0/L2 projects use `_aos/` for governance. L2 adds the `core/` engine. L2.5 extends L2 with the managed pipeline module.

---

## 3. New Project Setup — 17-Item Checklist

Complete all 17 items. Run `validate_aos.sh .` at the end — must reach **PASS / 0 FAIL** on the checks your profile runs (minimal L0 spoke bootstrap often **12** checks; **agents-os hub** with full modules: **19** checks as of Lean Kit 3.1.7 — see Module 08).

### Phase A — Directory Structure

**□ 1. Create `_aos/` directory tree**

```bash
mkdir -p _aos/{context,lean-kit/modules,work_packages,governance}
mkdir -p _COMMUNICATION/{team_00,team_100,team_110,team_190}
mkdir -p _COMMUNICATION/team_99
```

**□ 2. Copy Lean Kit (physical snapshot — NEVER symlink)**

```bash
cp -r /path/to/agents-os/lean-kit/modules/ _aos/lean-kit/modules/
cp /path/to/agents-os/lean-kit/MODULE_INDEX.md _aos/lean-kit/
cp /path/to/agents-os/lean-kit/LEAN_KIT_VERSION.md _aos/lean-kit/
cp /path/to/agents-os/lean-kit/PROFILE_SELECTION_GUIDE.md _aos/lean-kit/
cp /path/to/agents-os/lean-kit/VERSION_POLICY.md _aos/lean-kit/
```

---

### Phase B — Core `_aos/` Files

**□ 3. Create `_aos/roadmap.yaml`**

Source: `lean-kit/modules/project-governance/config_templates/roadmap.yaml.template`

Fill in: `project.id`, `project.name`, `project.profile`, `project.active_milestone`, `work_packages` list.

**□ 4. Create `_aos/ideas.json`**

Source: `lean-kit/modules/project-governance/config_templates/ideas.json.template`

Fill in project-specific incubation ideas, or initialize with empty array.

**□ 5. Create `_aos/team_assignments.yaml`**

Source: `lean-kit/modules/project-governance/config_templates/team_assignments.yaml.template`

Fill in: team IDs, engines. Verify cross-engine rule: builder engine ≠ validator engine.

**□ 6. Create `_aos/metadata.yaml`**

No template — create directly:

```yaml
lean_kit_source_date: 'YYYY-MM-DD'
lean_kit_source_sha: <sha from hub git log>
lean_kit_version: <version from lean-kit/LEAN_KIT_VERSION.md>
profile: <L0|L2|L2.5>
active_modules:
  - '01'  # project-governance
  - '02'  # gate-workflow
  - '03'  # team-model
  - '04'  # document-lifecycle
  - '06'  # agent-activation
  - '08'  # validation-quality
  - '11'  # standards-conventions
  - '12'  # managed-pipeline (L2.5)
# Modules 05/07/09/10 deprecated by W9 (see CLOSURE_AOS-V4-WP-INTERFACE-AUDIT_v1.0.0.md)
```

Remove modules not applicable to your profile.

**□ 7. Create `_aos/README.md`**

Source: `lean-kit/modules/project-governance/config_templates/README.md.template`

Fill in project name and profile.

**□ 8. Create `_aos/MILESTONE_MAP.md`**

No template — write manually. Columns: ID | Name | Status | Description

```markdown
# MILESTONE_MAP — [Project Name]

## Active Milestone
**[ID]** — [Name]: [one-line description]

## Milestone Table

| ID | Name | Status | Description |
|----|------|--------|-------------|
| [ID] | [Name] | ACTIVE | [description] |
```

**□ 9. Create `_aos/project_identity.yaml`**  ⚠️ Required for validate_aos.sh Check 12

Source: `lean-kit/modules/project-governance/config_templates/project_identity.yaml.template`

Fill in: `project_id`, `display_name`, `domain`, `profile`, `is_hub: false`, `allowed_write_roots`, `forbidden_patterns`, `cross_project_routing`.

---

### Phase C — Governance

**□ 9b. Create `_aos/definition.yaml`**  ⚠️ Required for validate_aos.sh Check 13

Source: `lean-kit/modules/project-governance/config_templates/definition.yaml.template`

Fill in: `{{PROJECT_ID}}`, `{{DATE}}`, `{{AUTHOR}}`, `{{PROFILE}}`.

**Rule:** include ONLY teams that appear in `team_assignments.yaml`. The template pre-fills the 3 always-required teams (team_00, team_100, team_190) and team_110 (domain builder). Remove any other team entry that is not assigned.

**Iron Rule:** every `team_XX` key in this file must have a corresponding `_aos/governance/team_XX.md` — Check 13 enforces this. Ghost teams (defined here but not governed) will fail validation.

---

**□ 10. Run governance propagation (creates `_aos/governance/`)**

New projects are not yet in the `--all` registry. Use legacy (single-target) mode from hub:

```bash
cd /Users/nimrod/Documents/agents-os
bash lean-kit/modules/project-governance/scripts/propagate_governance.sh \
  /Users/nimrod/Documents/agents-os \
  /path/to/new-project
```

This populates `/path/to/new-project/_aos/governance/` from `core/governance/` on the hub.

Once the project is registered in `propagate_governance.sh`'s `TARGETS` array, future syncs can use `--all`.

Verify: `_aos/governance/` contains `definition.yaml` + one `team_*.md` per active team.

**□ 11. Create `_aos/context/PROJECT_CONTEXT.md`**

Write manually: what the project is, current state, key directories, constraints.

---

### Phase D — Activation Prompts

**□ 12. Create `_aos/context/ACTIVATION_ARCH.md`**

Source: `lean-kit/modules/agent-activation/context/ACTIVATION_ARCH.md.template`

Replace all `[placeholder]` values with project-specific data.

**□ 13. Create `_aos/context/ACTIVATION_BUILDER.md`**

Source: `lean-kit/modules/agent-activation/context/ACTIVATION_BUILDER.md.template`

**□ 14. Create `_aos/context/ACTIVATION_VALIDATOR.md`**

Source: `lean-kit/modules/agent-activation/context/ACTIVATION_VALIDATOR.md.template`

---

### Phase E — Team Communication Directories

**□ 15. Create `__ONBOARDING_TEAM_*.md` for each active team**

Source: `lean-kit/modules/project-governance/config_templates/__ONBOARDING_TEAM.md.template`

One file per team directory in `_COMMUNICATION/`. File stays at root of the team directory (not in a WP subfolder).

**QA requests (when Team 50 is active):** Any team may request functional acceptance testing by submitting a QA request artifact to `_COMMUNICATION/team_50/[WP-ID]/`. Use the template:

Source: `lean-kit/modules/project-governance/config_templates/QA_REQUEST.md.template`

See `_aos/governance/team_50.md` §QA Request Intake for the intake validation rules Team 50 applies before starting any test run.

---

### Phase F — IDE / Claude Settings

**□ 16. Create `CLAUDE.md` (project root)**

Instantiate from: `lean-kit/modules/project-governance/config_templates/CLAUDE.md.template` (replace all `{{PLACEHOLDER}}` values).

Must include: Identity, §BOUNDARY, Mandatory startup, **Directory Authority** (align with `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` Part 5), Key paths, Team model, Iron Rules.

Hub reference: `agents-os/CLAUDE.md`.

**□ 17. Create `.cursorrules` (project root)**

Source: `lean-kit/modules/project-governance/config_templates/cursorrules.template`

Choose Variant A (L0) or Variant B (L2). Fill in all `{{PLACEHOLDER}}` values.

Optionally create `.claude/settings.json` with `additionalDirectories` pointing to hub:

```json
{
  "additionalDirectories": ["/path/to/agents-os"]
}
```

---

### Final Validation

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

**Expected result:** New spoke bootstrap (minimal modules): **at least `12 PASS / 0 SKIP / 0 FAIL`** when only the lean subset is active. Full **agents-os** hub with all active modules: typically **`19 PASS / 0 SKIP / 0 FAIL`** (includes Checks 16–19: slash commands, `PROJECT_CONTEXT` headings, `_aos/` write authority, API-only clause in team contracts).

If any check fails, the output will state exactly what is missing. Fix and re-run.

---

## 4. The Gate Model

Each work package progresses through gates:

```
L-GATE_ELIGIBILITY  →  L-GATE_SPEC  →  L-GATE_BUILD  →  L-GATE_VALIDATE
 (Entry)      (Spec)       (Build)      (Validate)
```

| Gate | Who | What |
|------|-----|------|
| L-GATE_ELIGIBILITY | Architect | Scope defined, team assigned |
| L-GATE_SPEC | Architect | LOD400 spec approved |
| L-GATE_BUILD | Builder | Implementation complete, self-QA passed |
| L-GATE_VALIDATE | Validator (Team 190) | Independent cross-engine validation |

Track B adds L-GATE_CONCEPT (Concept) between E and S for complex WPs.

---

## 5. The LOD Chain

| Level | Name | Purpose | Gate |
|-------|------|---------|------|
| LOD100 | Scope | What and why | L-GATE_ELIGIBILITY |
| LOD200 | Concept | How (architecture level) | L-GATE_CONCEPT (Track B) |
| LOD400 | Spec | Acceptance criteria, interfaces, file paths | L-GATE_SPEC |
| LOD500 | As-Built | What was actually delivered, fidelity record | L-GATE_BUILD |

---

## 6. WP Hierarchy — Naming, Structure & Registration

Every Work Package uses the canonical three-segment ID: **`S[stage]-P[program]-WP[number]`**

| Segment | Meaning | Example |
|---------|---------|---------|
| `S[stage]` | Major product milestone — corresponds to MILESTONE_MAP.md | S003 |
| `P[program]` | Delivery stream within the stage (one or more per stage) | P003 |
| `WP[number]` | Atomic execution unit (001, 002, …) | WP005 |

**Directory structure:**
```
_aos/work_packages/
  S003/                          ← Stage directory
    LOD300_milestone.md          ← Milestone scope (covers ALL WPs in stage, optional)
  S003-P003-WP001/               ← WP directory (full ID = directory name)
    LOD400_spec.md               ← Required at L-GATE_SPEC
    LOD500_asbuilt.md            ← Required at L-GATE_BUILD
```

**Registration rule:** Every WP MUST be in `roadmap.yaml` no later than L-GATE_SPEC.
- Before LOD400 exists: `spec_ref` may point to `S[N]/LOD300_milestone.md`
- At L-GATE_SPEC: `spec_ref` MUST be updated to `S[N]-P[M]-WP[K]/LOD400_spec.md`

**Anti-patterns (forbidden):**
- `WP-A1`, `WP-1`, `GATE-A-WP1` — execution shorthand only, never canonical IDs
- Milestone-level LOD300 as the spec_ref at L-GATE_SPEC
- Starting L-GATE_BUILD without a roadmap.yaml entry

→ Full standard: `lean-kit/modules/project-governance/WP_ID_STANDARD.md`

---

## 7. Iron Rules (Always Apply)

1. **Cross-engine:** Builder engine MUST differ from validator engine
2. **Physical lean-kit:** `_aos/lean-kit/` is always a physical copy, never symlink
3. **Repo-internal refs:** `spec_ref` paths never point outside the repo
4. **Single-writer roadmap:** One agent writes `roadmap.yaml` at a time
5. **L-GATE_VALIDATE independence:** Always Team 190, constitutional, cross-engine, immutable
6. **Inter-team = artifact:** Communication via file in `_COMMUNICATION/`, not chat
7. **WP subfolder rule:** WP-scoped files go in `_COMMUNICATION/team_[ID]/[WP-ID]/[filename].md`
8. **project_identity.yaml required:** Every spoke project must have this file (Check 12)
9. **WP canonical ID required:** Every WP uses `S[N]-P[M]-WP[K]` format, registered in roadmap.yaml before L-GATE_SPEC

---

## 8. Directory Authority — who may write where

`_aos/` is the **governance layer**. It is NOT a working directory for feature teams.

See canonical table: `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` Part 5.

Quick reference: only Team 00/100/110/191 may write to `_aos/` (per paths in that table).
All other teams: `_COMMUNICATION/team_[ID]/` and application source only.

| Team | `_aos/roadmap.yaml` | `_aos/work_packages/` | `_aos/lean-kit/` | `_aos/governance/` | `_COMMUNICATION/` |
|------|:-------------------:|:---------------------:|:----------------:|:------------------:|:-----------------:|
| team_00 | ✓ | ✓ | read only | ✓ (via hub) | ✓ |
| team_100 | ✓ | ✓ | read only | ✗ (via hub) | ✓ team_100/ |
| team_110 | ✗ | ✓ (mandated) | read only | ✗ | ✓ team_110/ |
| team_191 | mandate only | mandate only | read only | propagation only | ✓ team_191/ |
| team_10/20/30/40/50/60/70/80/90/99/170/190 | ✗ | ✗ | read only | ✗ | ✓ own team/ only |

**Rule:** If you are not Team 00/100/110/191, produce your output in `_COMMUNICATION/team_[ID]/`
and let Team 100 make any required `_aos/` updates.
Non-governance teams must never create or edit files under `_aos/` — even when `_aos/` is present
as a snapshot in their project folder.

---

## 9. Reference Projects

| Project | Profile | What it demonstrates |
|---------|---------|---------------------|
| **AOS-Sandbox-Lean** | L0 | Minimal governance, 2 WPs, no engine |
| **AOS-Sandbox-Full** | L2 | Engine + governance, 3 WPs across 2 programs |
| **agents-os** | L0 | Hub project (self-governing, lean-kit source) |
| **TikTrack** | L2 | Production project with dual-profile mode |

Clone a sandbox to see a complete working example.

---

*AOS Lean Kit | Module 01 — Project Governance | v3.1.5*
