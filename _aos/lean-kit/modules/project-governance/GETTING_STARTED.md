# Getting Started with AOS Governance

How to set up a new project with AOS in-repo governance.

---

## 1. The `_aos/` Directory

Every AOS-managed project has an `_aos/` directory at its root. This is the governance layer.

```
my-project/
  _aos/
    roadmap.yaml              # WP state registry (SSoT for work packages)
    ideas.json                # Idea pipeline (pre-GATE_0 incubator)
    team_assignments.yaml     # Team-to-role mapping
    README.md                 # What _aos/ is and how to use it
    context/
      PROJECT_CONTEXT.md      # Project background for agents
      ACTIVATION_ARCH.md      # Architecture agent activation
      ACTIVATION_BUILDER.md   # Builder agent activation
      ACTIVATION_VALIDATOR.md # Validator agent activation
    lean-kit/                 # Physical copy of methodology (NEVER symlink)
      ...
    work_packages/
      WP-001/
        LOD100_scope.md       # Scope statement
        LOD200_concept.md     # Concept design
        LOD400_spec.md        # Executable spec with ACs
        LOD500_asbuilt.md     # As-built fidelity record
  _COMMUNICATION/             # Inter-team artifact exchange
    team_00/                  # System Designer
    team_100/                 # Architecture Agent
    team_110/                 # Builder Agent
    team_190/                 # Validator Agent
  .cursorrules                # AI agent context rules
```

## 2. Choose Your Profile

| Profile | What it means | Engine directory? | Example |
|---------|--------------|-------------------|---------|
| **L0** | Lean governance only | No | AOS-Sandbox-Lean |
| **L2** | Full governance + engine | Yes (`aos_engine/`) | AOS-Sandbox-Full, TikTrack |
| **L3** | CLI-driven (future) | Yes | Not yet built |

L0 projects use `_aos/` for governance without any automation engine.
L2 projects add an engine directory that runs pipelines alongside `_aos/`.

## 3. Create a Project from Scratch

### Step 1: Initialize `_aos/`

```bash
mkdir -p _aos/{context,lean-kit,work_packages}
mkdir -p _COMMUNICATION/{team_00,team_100,team_110,team_190}
```

### Step 2: Copy Lean Kit

Copy the lean-kit from agents-os as a **physical snapshot** (Iron Rule: never symlink):

```bash
cp -r /path/to/agents-os/lean-kit/modules/ _aos/lean-kit/modules/
cp /path/to/agents-os/lean-kit/MODULE_INDEX.md _aos/lean-kit/
```

### Step 3: Create Configuration Files

Use the templates in `lean-kit/modules/project-governance/config_templates/`:

- `roadmap.yaml.template` → `_aos/roadmap.yaml`
- `team_assignments.yaml.template` → `_aos/team_assignments.yaml`
- `README.md.template` → `_aos/README.md`

Fill in your project name, milestone IDs, and team assignments.

### Step 4: Write ACTIVATION Files

Use the templates in `lean-kit/modules/agent-activation/context/`:

- `ACTIVATION_ARCH.md.template` → `_aos/context/ACTIVATION_ARCH.md`
- `ACTIVATION_BUILDER.md.template` → `_aos/context/ACTIVATION_BUILDER.md`
- `ACTIVATION_VALIDATOR.md.template` → `_aos/context/ACTIVATION_VALIDATOR.md`

Replace all `[placeholder]` values with your project-specific data. Every section in the template must appear in the instantiated file.

### Step 5: Write PROJECT_CONTEXT.md

Create `_aos/context/PROJECT_CONTEXT.md` with:
- What the project is
- Current state (active milestone, WP, profile)
- Key directories
- Any project-specific constraints

### Step 6: Add Cursor Rules

Create `.cursorrules` at the project root with:
- Project identity and profile
- Team model
- Iron Rules
- Directory authority table
- Mandatory session startup steps

### Step 7: Validate

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Exit code 0 = valid structure.

## 4. The Gate Model

Each work package progresses through gates:

```
L-GATE_E  →  L-GATE_S  →  L-GATE_B  →  L-GATE_V
 (Entry)      (Spec)       (Build)      (Validate)
```

| Gate | Who | What |
|------|-----|------|
| L-GATE_E | Architect | Scope defined, team assigned |
| L-GATE_S | Architect | LOD400 spec approved |
| L-GATE_B | Builder | Implementation complete, self-QA passed |
| L-GATE_V | Validator (Team 190) | Independent cross-engine validation |

Track B adds L-GATE_C (Concept) between E and S for complex WPs.

## 5. The LOD Chain

| Level | Name | Purpose | Gate |
|-------|------|---------|------|
| LOD100 | Scope | What and why | L-GATE_E |
| LOD200 | Concept | How (architecture level) | L-GATE_C (Track B) |
| LOD400 | Spec | Acceptance criteria, interfaces, file paths | L-GATE_S |
| LOD500 | As-Built | What was actually delivered, fidelity record | L-GATE_B |

## 6. Iron Rules (Always Apply)

1. **Cross-engine:** Builder engine MUST differ from validator engine
2. **Physical lean-kit:** `_aos/lean-kit/` is always a physical copy, never symlink
3. **Repo-internal refs:** `spec_ref` paths never point outside the repo
4. **Single-writer roadmap:** One agent writes roadmap.yaml at a time
5. **L-GATE_V independence:** Always Team 190, constitutional, cross-engine, immutable
6. **Inter-team = artifact:** Communication via file in `_COMMUNICATION/`, not chat

## 7. Reference Projects

| Project | Profile | What it demonstrates |
|---------|---------|---------------------|
| **AOS-Sandbox-Lean** | L0 | Minimal governance, 2 WPs, no engine |
| **AOS-Sandbox-Full** | L2 | Engine + governance, 3 WPs across 2 programs |
| **agents-os** | L0 | Hub project (self-governing, lean-kit source) |
| **TikTrack** | L2 | Production project with dual-profile mode |

Clone a sandbox to see a complete working example.

---

*AOS Lean Kit | Module 01 — Project Governance | v3.1.1*
