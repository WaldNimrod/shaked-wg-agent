---
id: PROJECT_CREATION_PROCEDURE_v1.0.0
from: Team 100 (Chief System Architect)
authority: Team 00 (Principal)
date: 2026-04-02
version: v1.0.0
status: ACTIVE
type: OPERATIONAL_PROCEDURE
profiles_covered: L0 (Lean/Manual), L2 (AOS v3/Dashboard)
linked_standard: TEAM_100_LOD_STANDARD_v0.3.md
linked_adr: ARCHITECT_DIRECTIVE_METHODOLOGY_DEPLOYMENT_SPLIT_v1.0.0.md
---

# Project Creation Procedure v1.0.0

**Purpose:** Define the manual procedure for creating a new project environment
in either Lean (L0) or AOS v3 (L2) mode.

> **Note:** This procedure is currently manual. Future canonical WPs in AOS
> will automate these steps (BUILD_PROJECT_SCAFFOLDING_CLI).
> When the CLI is available, this document is superseded by the tool's output.

---

## Part 1 — Choosing a Profile

Answer these questions to determine which profile to use:

| Question | If YES → |
|----------|----------|
| Does the project have 5+ concurrent work packages? | L2 |
| Do you need a persistent audit trail (DB-backed)? | L2 |
| Will the project run for 6+ months with multiple stages? | L2 |
| Is there a team of 4+ active agents simultaneously? | L2 |
| Does the project span multiple operational domains? | Strongly suggests L2 |
| Is this a short, bounded project (1–3 WPs)? | L0 |
| Is setup speed the priority? | L0 |
| Is this a proof-of-concept or experimental build? | L0 |
| Will you likely upgrade to AOS later? | L0 (roadmap.yaml ensures clean upgrade) |

**If uncertain: start with L0.** The upgrade path to L2 is defined and supported.

---

## Part 2 — Profile L0: Lean / Manual

### Step 1 — Clone the Lean Kit

```bash
git clone [lean-kit-repo-url] my-project-name
cd my-project-name
```

Note the version in `LEAN_KIT_VERSION.md` — this is your snapshot version.

### Step 2 — Configure team assignments

Edit `team_assignments.yaml`:

```yaml
project_id: my-project-name
lean_kit_version: v1.0.0   # from LEAN_KIT_VERSION.md

roles:
  architect:
    engine: claude-code     # choose your LLM engine
    context_file: prompts/architect_context.md

  builder:
    engine: cursor-composer
    context_file: prompts/builder_context.md

  validator:
    engine: openai-codex    # MUST be different provider from builder
    context_file: prompts/validator_context.md
    # Iron Rule: engine MUST differ from builder engine
```

**Validation check:** `validator.engine` provider ≠ `builder.engine` provider.

### Step 3 — Customize context files

For each role in `prompts/`, fill in:
- Project name and domain
- Active stage and program
- Current work package (if known)
- Reference to LOD Standard snapshot
- Any project-specific Iron Rules

### Step 4 — Initialize roadmap

Edit `roadmap.yaml`:

```yaml
project_id: my-project-name
active_stage: S001
active_program: S001-P001
lean_kit_version: v1.0.0
created_at: 2026-04-02

work_packages: []  # add WPs as they are defined
```

### Step 5 — Create first work package

```bash
cp -r work_packages/TEMPLATE_WP work_packages/S001-P001-WP001
```

Add the WP to `roadmap.yaml`:

```yaml
work_packages:
  - id: S001-P001-WP001
    label: "Describe the WP here"
    status: PLANNED
    current_lean_gate: null
    track: null              # A or B — declared at L-GATE_SPEC
    lod_status: null
    assigned_builder: cursor-composer
    assigned_validator: openai-codex
    created_at: 2026-04-02
    spec_ref: null
```

### Step 6 — Begin L-GATE_ELIGIBILITY for first WP

Open `work_packages/S001-P001-WP001/gate_log.md` and fill in the
**L-GATE_ELIGIBILITY eligibility section**:

```markdown
## L-GATE_ELIGIBILITY — Eligibility — 2026-04-02
**WP ID:** S001-P001-WP001
**Label:** [feature name]
**Domain:** [what system/area this touches]
**Scope in 2 sentences:** [what will be built]
**Out of scope:** [explicit exclusions]
**Risk classification:** Low / Medium / High / Critical
**Track:** A / B (preliminary — confirmed at L-GATE_SPEC)

**Decision:** PASS
**Orchestrator:** [your name]
```

Update `roadmap.yaml`: `status: IN_PROGRESS`, `current_lean_gate: L-GATE_SPEC`

### Step 7 — Verify setup

```
✓ team_assignments.yaml: validator engine ≠ builder engine
✓ roadmap.yaml: WP exists with status IN_PROGRESS
✓ gate_log.md: L-GATE_ELIGIBILITY PASS recorded
✓ work_packages/S001-P001-WP001/ exists
✓ prompts/ context files filled in for each role
```

**Total time: ~15–20 minutes.**

---

## Part 3 — Profile L2: AOS v3 / Dashboard

### Prerequisites

- Python 3.11+, PostgreSQL 14+, Node.js (for dashboard build)
- Git access to TikTrack AOS repository
- `.env` configured (DB credentials, API keys)

### Step 1 — Clone and configure AOS repository

```bash
git clone [aos-repo-url] my-project-aos
cd my-project-aos
cp .env.example .env
# Edit .env: set DATABASE_URL, SECRET_KEY, etc.
```

### Step 2 — Initialize database

```bash
cd agents_os_v3
python3 seed.py                    # creates DB schema + bootstrap records
# Run migrations if needed:
python3 db/run_migrations.py
```

### Step 3 — Register new project in definition.yaml

Open `agents_os_v3/definition.yaml` and add:

**Under `stages`:**
```yaml
stages:
  - id: "S001"
    label: "Stage 1"
    status: ACTIVE
```

**Under `programs`:**
```yaml
programs:
  - id: "S001-P001"
    label: "Program name"
    stage_id: "S001"
    status: ACTIVE
    domain: "my-domain"
```

**Under `work_packages`:**
```yaml
work_packages:
  - id: "S001-P001-WP001"
    label: "First work package"
    status: PLANNED
    stage_id: "S001"
    program_id: "S001-P001"
    domain: "my-domain"
    track: "A"
```

### Step 4 — Configure team assignments

In `definition.yaml`, verify that team assignments exist for your domain.
If this is a new domain, add team entries following the existing pattern.

Confirm:
- `assigned_builder` engine ≠ `assigned_validator` engine (Iron Rule)
- Gate authority is correct for your domain
- `domain_scope` is set correctly

### Step 5 — Start AOS server

```bash
bash scripts/start-aos-v3-server.sh
```

*(Canonical port: **8090**. `--reload` is prohibited in agent sessions. The script handles venv activation, port conflict detection, and background PID tracking. For foreground mode: `bash scripts/start-aos-v3-server.sh --foreground`.)*

Verify health:
```bash
curl -s http://localhost:8090/api/health
```
Expected: `{"status":"ok"}`

### Step 6 — Verify pipeline state

```bash
curl http://localhost:8090/api/governance/status
```

Expected response shape:
```json
{
  "summary": {
    "total_teams": <N>,
    "teams_with_governance": <N>,
    ...
  },
  "matrix": [
    {"team_id": "...", "engine": "...", "routing_rule_count": <N>, "has_governance_file": true, "file_size_bytes": <N>},
    ...
  ]
}
```
*(Endpoint is mounted on the `business_router` at prefix `/api` — not `/api/v1/`)*

### Step 7 — Begin first WP

Option A — Dashboard:
```
Open browser → http://localhost:[dashboard-port]
Select domain → Click "Start Run" on S001-P001-WP001
```

Option B — CLI:
```bash
./pipeline_run.sh
# generates GATE_0 prompt → paste to architect team
./pipeline_run.sh pass    # after GATE_0 review
```

### Step 8 — Verify first run

```
✓ GET /api/governance/status: returns summary + matrix (200 OK)
✓ Dashboard shows WP as IN_PROGRESS
✓ GATE_0 prompt generated successfully
✓ DB work_packages table: WP record with status IN_PROGRESS
```

**Total time: 30–60 minutes (including infrastructure setup).**

---

## Part 4 — Upgrade Path: L0 → L2

When a Lean project needs to upgrade to full AOS:

### Step 1 — Verify roadmap.yaml is complete

All WP statuses, LOD statuses, and assignments must be current.

### Step 2 — Set up AOS infrastructure (Part 3, Steps 1–4)

### Step 3 — Import roadmap.yaml to AOS DB

```bash
# [Future: BUILD_LEAN_TO_AOS_UPGRADE tool]
# Manual (until tool is available):
python3 tools/import_lean_roadmap.py roadmap.yaml
```

The import script (future WP) reads `roadmap.yaml` and populates:
- `work_packages` table
- `stages` and `programs` entries in `definition.yaml`

### Step 4 — Copy work_packages/ documents to AOS artifact storage

Link spec documents in `work_packages/` to the AOS artifact system.

### Step 5 — Verify parity

Compare roadmap.yaml WP statuses to DB state. Resolve any discrepancies.
Decommission `roadmap.yaml` once DB is confirmed accurate.

---

## Part 5 — Methodology Update Propagation (L0)

When a critical methodology update is published in the lean-kit SSoT:

### Determine if update applies

1. Read the lean-kit release notes for the new version
2. Check: does the change affect Iron Rules, LOD level definitions, or gate model?
   - **Yes → propagation required**
   - **No (template refinement, guidance text) → optional, adopt at next project**

### Propagate update

```bash
# In your project directory:
git clone [lean-kit-repo-url] /tmp/lean-kit-update
cd /tmp/lean-kit-update
git checkout [new-version-tag]

# Compare and selectively copy changed files:
diff /tmp/lean-kit-update/gates/LEAN_GATE_MODEL.md ./gates/LEAN_GATE_MODEL.md
# Review diff, adopt changes manually

# Update version reference:
echo "v[new-version] (updated [date])" >> LEAN_KIT_VERSION.md
```

---

## Part 6 — Index Links

Cross-references (canonical paths relative to repository root). Indexed **2026-04-02** (Team 170 — session indexing).

| Reference | Link |
|-----------|------|
| Governance procedures index | [GOVERNANCE_PROCEDURES_INDEX.md](../../documentation/docs-governance/00-INDEX/GOVERNANCE_PROCEDURES_INDEX.md) |
| LOD Standard (canonical v1.0.0; Lean overlay) | [LOD_STANDARD_v1.0.0.md](../../documentation/docs-governance/01-FOUNDATIONS/LOD_STANDARD_v1.0.0.md) — source snapshot: [TEAM_100_LOD_STANDARD_v0.3.md](TEAM_100_LOD_STANDARD_v0.3.md) |
| Methodology / Deployment Split (Iron Rule) §3 | [ARCHITECT_DIRECTIVE_METHODOLOGY_DEPLOYMENT_SPLIT_v1.0.0.md](../_Architects_Decisions/ARCHITECT_DIRECTIVE_METHODOLOGY_DEPLOYMENT_SPLIT_v1.0.0.md) |
| AOS v3 agent context / setup | [AGENTS.md](../../agents_os_v3/AGENTS.md) |
| Repository master index | [00_MASTER_INDEX.md](../../00_MASTER_INDEX.md) |

This procedure is also listed under **§ _COMMUNICATION — indexed session 2026-04-02** in the governance procedures index.

---

**log_entry | TEAM_100 | PROJECT_CREATION_PROCEDURE_v1.0.0 | 2026-04-02**
