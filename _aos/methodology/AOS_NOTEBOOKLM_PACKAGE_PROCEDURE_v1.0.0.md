# AOS NotebookLM Package Procedure

**Version:** 1.0.0  
**Status:** ACTIVE  
**Author:** Team 100  
**Date:** 2026-04-22  
**Scope:** All AOS domains and spoke projects  

---

## Purpose

This procedure defines how to generate a **NotebookLM information package** for any AOS domain or project. It enables any team to produce a well-structured, audience-calibrated set of Markdown documents that load efficiently into Google NotebookLM and support high-quality AI-assisted exploration.

The procedure is parameterized. A single command invocation with the right parameters produces the correct file set, naming scheme, folder structure, and README for any combination of domain, audience, depth, and language.

**Why this exists:** Ad-hoc document dumps into NotebookLM perform poorly. Research shows that 3–20 consolidated, well-structured sources produce 83% better answer relevance and 64% fewer hallucinations compared to 40+ small raw files. AOS methodology files are not optimized for direct upload — this procedure produces consolidated, restructured outputs from source files that are NotebookLM-optimal.

---

## Phase 0 — Parameter Collection

Invoke with: `[AOS_notebooklm]` or inline parameters.

Collect the following parameters. If any are missing, display the confirmation box (§0.1) and wait for input before proceeding.

| Parameter | Values | Default |
|-----------|--------|---------|
| `domain` | `aos` / `tiktrack` / `smallfarmsagents` / `nimrod-book` / `{project-id}` | — (required) |
| `package_type` | `BASE` / `PERSONAL` / `TECHNO` / `MARKETING` / `USER` | `BASE` |
| `delta` | `none` / `personal` / `techno` / `both` | `none` |
| `depth` | `OVERVIEW` / `STANDARD` / `COMPREHENSIVE` | `STANDARD` |
| `language` | `en` / `he` / `mixed` | `en` |
| `purpose` | Free text (e.g., "investor pitch", "team onboarding", "client demo") | — |
| `output_path` | Folder path for output | `_COMMUNICATION/team_100/{domain} notebooklm {date}/` |

### §0.1 — Confirmation Box

```
📦 NotebookLM Package — אשר פרמטרים:
┌──────────────────────────────────────────────────────────────────┐
│  0  ← צור חבילה                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [1] דומיין:     {domain}                                         │
│ [2] סוג:        {package_type}  → BASE / PERSONAL / TECHNO /     │
│                 MARKETING / USER                                  │
│ [3] דלטה:       {delta}  → none / personal / techno / both       │
│ [4] עומק:       {depth}  → OVERVIEW / STANDARD / COMPREHENSIVE   │
│ [5] שפה:        {language}  → en / he / mixed                    │
│ [6] מטרה:       "{purpose}"                                      │
│ [7] תיקייה:     {output_path}                                    │
├──────────────────────────────────────────────────────────────────┤
│  9  ← בטל                                                        │
└──────────────────────────────────────────────────────────────────┘
```

**Processing shortcuts:**
- `0` → proceed with shown parameters
- `[N]` → enter new value for that field inline
- `9` → cancel

### §0.2 — File Count Preview

Before generation, display expected output:

```
📁 {output_path}/
   ├── README.md
   ├── {PREFIX}_01_*.md  ×  {core_count} core files
   ├── GUIDE_*.md        ×  {guide_count} guide extracts   [if depth ≥ STANDARD]
   ├── personal/         ×  5 PERSONAL_*.md files          [if delta=personal|both]
   └── techno/           ×  5 TECH_*.md files              [if delta=techno|both]
   Total: {total} files, estimated {word_estimate} words
```

---

## Phase 1 — Source Discovery

Select source files based on `domain`, `package_type`, and `depth`. Use the matrix below.

### §1.1 — Universal AOS Sources (all domains, all depths)

These files are always read for any AOS-governed domain:

```
CLAUDE.md                                           ← Iron Rules, boundaries, identity
_aos/roadmap.yaml                                   ← WP status, gate history
methodology/AOS_CONCEPT_AND_PRINCIPLES.md           ← core philosophy
methodology/AOS_IDENTITY_ONBOARDING_v1.0.0.md      ← team model
core/definition.yaml                                ← platform parameters, active stage
_aos/context/PROJECT_CONTEXT.md                     ← domain-specific context
```

### §1.2 — Depth-Gated Sources

| Source | OVERVIEW | STANDARD | COMPREHENSIVE |
|--------|----------|----------|---------------|
| `lean-kit/PROFILE_SELECTION_GUIDE.md` | ✓ | ✓ | ✓ |
| `lean-kit/modules/managed-pipeline/L25_QUICK_REFERENCE.md` | — | ✓ | ✓ |
| `methodology/lod-standard/TEAM_100_LOD_STANDARD_v0.3.md` | — | ✓ | ✓ |
| `_aos/context/CODE_STANDARDS.md` | — | — | ✓ |
| `_aos/ideas.json` | summary only | full | full |
| All `governance/directives/ADR0*.md` | — | ADR031–036 | ADR031–043 |
| `lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml` | — | ✓ | ✓ |
| All 8 `core/ui/guides/*.html` | — | ✓ | ✓ |

### §1.3 — Archetype-Specific Sources

**SOFTWARE archetype** (TikTrack, SFA, agros-insite):
```
{spoke}/_aos/roadmap.yaml
{spoke}/_aos/context/PROJECT_CONTEXT.md
{spoke}/CLAUDE.md
{spoke}/_aos/governance/   ← team contracts relevant to domain
```

**CONTENT_SUBSTRATE archetype** (nimrod-book, content projects):
```
{project}/docs/structure/   ← content outline and taxonomy
{project}/docs/audience/    ← reader profile
{project}/_aos/ (if present) or equivalent governance layer
```

**3D_CREATIVE archetype** (HobbitHome, microgreens-blender):
```
{project}/docs/brief/       ← creative brief
{project}/docs/milestones/  ← deliverable phases
```

**DOMAIN_AGENT archetype** (team_99 ops, SmallFarmsAgents logic):
```
{project}/_aos/governance/  ← team mandate
{project}/docs/domain/      ← domain-specific glossary + rules
```

### §1.4 — Package Type Source Selection

| Package Type | Primary Audience | Source Emphasis |
|---|---|---|
| `BASE` | Partners, investors, external | Vision, outcomes, team model, scenarios — minimal internals |
| `PERSONAL` | Team 00 (Nimrod) | Operational heuristics, decision rationale, gotchas, daily ops, shortcuts |
| `TECHNO` | Engineers, integrators | API contracts, architecture internals, DB state, infrastructure, extension guide |
| `MARKETING` | Clients, future users | Use cases, value propositions, portfolio outcomes, comparison vs. alternatives |
| `USER` | Active AOS users | Command reference, session startup, authority map, messaging guide |

---

## Phase 2 — File Architecture

### §2.1 — Core File Set

**OVERVIEW depth:** 5 files

| # | File | Content |
|---|------|---------|
| 01 | `{PREFIX}_01_VISION_AND_MISSION.md` | What it is, the problem, why it matters |
| 02 | `{PREFIX}_02_SYSTEM_ARCHITECTURE.md` | Hub-spoke, engine, data authority |
| 03 | `{PREFIX}_03_TEAM_MODEL_AND_GOVERNANCE.md` | Teams, Iron Rules, authority map |
| 04 | `{PREFIX}_04_WORK_METHODOLOGY.md` | LOD, gates, profiles |
| 05 | `{PREFIX}_05_SCENARIOS.md` | 3–4 key workflows |

**STANDARD depth:** 8 files (adds 3)

| # | File | Content |
|---|------|---------|
| 06 | `{PREFIX}_06_FEATURES_AND_CAPABILITIES.md` | Dashboard, commands, messaging |
| 07 | `{PREFIX}_07_WORK_ENVIRONMENT.md` | Physical + digital environments |
| 08 | `{PREFIX}_08_PROJECT_PORTFOLIO.md` | Projects, archetypes, ideas pipeline |

**COMPREHENSIVE depth:** 8 core + 4 guide extracts (total 12)

| # | File | Source |
|---|------|--------|
| G1 | `GUIDE_COMMANDS_AND_MESSAGING.md` | Command reference + messaging guide HTML |
| G2 | `GUIDE_GOVERNANCE_AND_LIFECYCLE.md` | Iron Rules + Gate Lifecycle HTML |
| G3 | `GUIDE_OPERATIONS.md` | Startup + API reference + Authority map HTML |
| G4 | `GUIDE_PORTFOLIO_OVERVIEW.md` | Projects portfolio HTML |

### §2.2 — Delta File Set

**`personal/` subfolder** (5 files, prefix `PERSONAL_`):

| File | Content Focus |
|------|---------------|
| `PERSONAL_DAILY_OPS_AND_HEURISTICS.md` | Session startup ritual, daily workflow, calibrated rules-of-thumb |
| `PERSONAL_DECISION_RATIONALE.md` | Key architectural decisions and why, ADR reasoning in plain terms |
| `PERSONAL_PROJECT_CONTEXT_AND_STATUS.md` | Current WP status, open items, dependencies, what's next |
| `PERSONAL_GOTCHAS_AND_LESSONS.md` | Known failure modes, expensive mistakes, things that look right but aren't |
| `PERSONAL_SHORTCUTS_AND_EFFICIENCY.md` | Fast paths, optimized flows, how to move faster within constraints |

**`techno/` subfolder** (5 files, prefix `TECH_`):

| File | Content Focus |
|------|---------------|
| `TECH_API_CONTRACTS_AND_EXAMPLES.md` | All endpoints with request/response schemas and curl examples |
| `TECH_ARCHITECTURE_INTERNALS.md` | Module structure, call chains, DB schema, FastAPI routing |
| `TECH_EXTENSION_AND_INTEGRATION.md` | How to add commands, endpoints, new spoke projects, custom modules |
| `TECH_DATABASE_AND_STATE.md` | PostgreSQL schema, ADR034 authority model, offline protocol, sync patterns |
| `TECH_INFRASTRUCTURE_AND_DEPLOYMENT.md` | Port registry, Docker setup, waldhomeserver, Mac dev environment, deploy flows |

### §2.3 — Naming Conventions

**Folder name:** `{domain} notebooklm {YYYY-MM-DD}/` or custom via `output_path`.  
Store under `_COMMUNICATION/team_100/` (within team_100 write authority).

**File prefix by package type:**

| `package_type` | File prefix applied to core files |
|---|---|
| `BASE` | `{DOMAIN_ABBREV}_` (e.g., `AOS_`, `TT_`, `SFA_`) |
| `PERSONAL` | `PERSONAL_` (delta only; core files keep BASE prefix) |
| `TECHNO` | `TECH_` (delta only; core files keep BASE prefix) |
| `MARKETING` | `MKT_` |
| `USER` | `USER_` |

**Domain abbreviation mapping:**

| Domain | Abbreviation |
|--------|-------------|
| `aos` | `AOS` |
| `tiktrack` | `TT` |
| `smallfarmsagents` | `SFA` |
| `nimrod-book` | `BOOK` |
| `agros-insite` | `AI` |
| Custom | First 3–4 uppercase chars of project name |

---

## Phase 3 — Content Generation Rules

### §3.1 — NotebookLM Format Requirements

Every generated file MUST follow these structural rules for optimal NotebookLM indexing:

1. **Single H1** per file — the file's primary topic, stated as noun phrase
2. **H2 for major sections** — 4–8 sections per file
3. **H3 for subsections** — used sparingly (max 3 levels total)
4. **Bold key terms on first use** — `**Agents OS (AOS)**`, `**Iron Rules**`, `**LOD Standard**`
5. **One idea per paragraph** — 3–6 sentences, no multi-topic paragraphs
6. **Tables preferred** over prose for structured data (teams, parameters, feature lists)
7. **Code blocks** for commands, file paths, API endpoints, YAML excerpts
8. **No inline HTML** — plain Markdown only
9. **HTML comment header** — frontmatter at top of each file:
   ```
   <!--
   package: {domain} NotebookLM Package
   file: {filename}
   date: {YYYY-MM-DD}
   audience: {audience description}
   depth: {OVERVIEW|STANDARD|COMPREHENSIVE}
   -->
   ```

### §3.2 — Audience Calibration

**BASE audience (partners/investors):**
- Lead with value and outcomes, not mechanics
- Explain every AOS term before using it
- Frame technical details in terms of business impact
- Avoid internal jargon (LOD, ADR, WP) without explanation
- Emphasize the "one-person software house" thesis throughout
- Use concrete numbers: team count, WP count, validation checks, word counts

**PERSONAL audience (Team 00 / Nimrod):**
- Skip all introductory explanation — assume full system knowledge
- Lead with actionable operational detail
- Include exact file paths, command syntax, error patterns
- Capture heuristics as decision rules: "If X → do Y, not Z, because..."
- Flag known gotchas with ⚠️ markers
- Reference specific ADRs, Iron Rules by number
- Language: `mixed` (Hebrew for operational commentary, English for technical terms)

**TECHNO audience (engineers/integrators):**
- Assume Python/FastAPI/PostgreSQL familiarity
- Lead with architecture, data model, and API contracts
- Include actual code signatures (function names, parameters, return types)
- Document extension points explicitly
- Include full request/response schemas with field names and types
- Reference specific files by exact path

**MARKETING audience (clients/prospects):**
- Lead with pain points and outcomes
- Avoid all technical detail unless it demonstrates capability
- Use analogies: "like an OS for AI teams", "like Jira but for AI agents"
- Emphasize unique differentiators (cross-engine validation, Iron Rules enforcement)

**USER audience (active AOS operators):**
- Lead with task-oriented sections ("How to do X")
- Include step-by-step procedures
- Reference commands by exact slash syntax
- Include troubleshooting tables

### §3.3 — Word Count Targets

| Depth | Core files (each) | Guide extracts (each) | Delta files (each) |
|-------|----------|---------|-------|
| OVERVIEW | 1,500–2,500 | — | — |
| STANDARD | 2,500–4,000 | 1,500–2,500 | 1,500–2,500 |
| COMPREHENSIVE | 3,000–5,000 | 2,000–3,500 | 2,000–3,500 |

Total package target: 25,000–50,000 words (COMPREHENSIVE with deltas).

### §3.4 — Content Prohibition List

Never include in any NotebookLM package file:
- Raw YAML frontmatter blocks from source files (excerpt and restructure instead)
- Full commit history or git log output
- Internal session logs or conversation excerpts
- `[PLACEHOLDER]` or `TODO` text
- CSS, JavaScript, or HTML markup (for HTML guide extracts: strip all markup, keep text)
- Direct copies of CLAUDE.md Iron Rules sections without rewriting for audience

### §3.5 — HTML Guide Extraction Rules

When extracting content from `core/ui/guides/*.html`:
1. Strip all `<style>` blocks
2. Strip all `<script>` blocks
3. Strip all HTML tags — convert structure to Markdown equivalents
4. Convert `<h1>` → `#`, `<h2>` → `##`, `<h3>` → `###`, `<table>` → Markdown table
5. Convert `<code>` and `<pre>` → fenced code blocks with appropriate language tag
6. Strip `class=`, `id=`, `data-*` attributes
7. Preserve all semantic content: tables, code examples, numbered steps
8. Add the HTML comment header with `package:`, `file:`, `date:`, `audience:`

---

## Phase 4 — README Generation

Every package folder gets a `README.md` as the **first file to upload** to NotebookLM.

README structure:

```markdown
# {Domain} — {Package Title}: NotebookLM Information Package

**Prepared for:** {audience}
**Date:** {YYYY-MM-DD}
**System:** {domain} {version}
**Prepared by:** Team 100 (Chief System Architect)
**Package type:** {BASE|PERSONAL|TECHNO|MARKETING|USER} / {depth}

## What Is This Package

{2–3 sentence description: what domain, what audience, what these files enable}

## Recommended Upload Order

{Numbered list of all files in the package in recommended reading order}
{Delta files at end: personal/ first, then techno/}

## Suggested First Queries for NotebookLM

{5–8 audience-calibrated starter questions}
{For BASE: vision, differentiators, how it works}
{For PERSONAL: gotchas, current status, shortcuts}
{For TECHNO: API usage, extension points, data model}

## Generate an Audio Overview

After uploading all sources, use the Audio Overview feature...
{Customize instruction per audience type}

## Delta Packages (if present)

{Explain what personal/ and techno/ subfolders contain and when to upload them}
```

---

## Phase 5 — Folder Structure and Commit Pattern

### §5.1 — Folder Layout

```
_COMMUNICATION/team_100/{domain} notebooklm {YYYY-MM-DD}/
├── README.md                          ← upload first
├── {PREFIX}_01_*.md
├── {PREFIX}_02_*.md
├── ...
├── {PREFIX}_08_*.md                   [STANDARD+]
├── GUIDE_*.md                         [COMPREHENSIVE only]
├── personal/                          [if delta=personal|both]
│   ├── PERSONAL_DAILY_OPS_AND_HEURISTICS.md
│   ├── PERSONAL_DECISION_RATIONALE.md
│   ├── PERSONAL_PROJECT_CONTEXT_AND_STATUS.md
│   ├── PERSONAL_GOTCHAS_AND_LESSONS.md
│   └── PERSONAL_SHORTCUTS_AND_EFFICIENCY.md
└── techno/                            [if delta=techno|both]
    ├── TECH_API_CONTRACTS_AND_EXAMPLES.md
    ├── TECH_ARCHITECTURE_INTERNALS.md
    ├── TECH_EXTENSION_AND_INTEGRATION.md
    ├── TECH_DATABASE_AND_STATE.md
    └── TECH_INFRASTRUCTURE_AND_DEPLOYMENT.md
```

### §5.2 — Verification Before Commit

Run these checks after generation, before committing:

```bash
# 1. Count files
ls "_COMMUNICATION/team_100/{folder}/" | wc -l
# Expected: README + core_count + guide_count (no delta subfolders in root count)

# 2. Check for placeholder text
grep -r "\[PLACEHOLDER\]\|TODO\|FIXME" "_COMMUNICATION/team_100/{folder}/"
# Expected: 0 matches

# 3. Word count spot check (each core file should be ≥ depth minimum)
wc -w "_COMMUNICATION/team_100/{folder}/"*.md

# 4. Validate AOS integrity
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Expected: 0 FAIL
# (new folder is in _COMMUNICATION/team_100/ — within write authority, no Check 32 risk)
```

### §5.3 — Commit Pattern

```bash
git add "_COMMUNICATION/team_100/{folder}/"
git commit -m "feat: NotebookLM package — {domain} {package_type} {depth} ({date})"
```

Commit message format:
- `feat:` for new packages
- `fix:` for corrections to existing packages
- `update:` for content refreshes (§6.1)

---

## Phase 6 — Maintenance and Updates

### §6.1 — When to Refresh

A package should be regenerated or updated when:

| Trigger | Scope of update |
|---------|----------------|
| Major AOS version release (e.g., v3.3.0 → v4.0.0) | Full regeneration |
| New Iron Rule added | File 03/04 (governance) |
| New slash command added | File 03 (features) + GUIDE_COMMANDS |
| Gate lifecycle change | File 05 + GUIDE_GOVERNANCE |
| New spoke project added | File 07 (portfolio) |
| Environment change (new server, new team) | File 06 (environment) + File 04 (teams) |
| Major WP completed | File 03 (features), File 08 (scenarios) |
| Active status changes (gotchas, current WPs) | `personal/` delta only |
| API endpoint added/changed | `techno/` delta only |

### §6.2 — Versioning

Package folders are dated, not versioned. When refreshing:
1. Create a new dated folder: `{domain} notebooklm {new-date}/`
2. Do NOT modify the original folder — it remains as a historical snapshot
3. If storage is a concern, archive old folders to `_archive/notebooklm-packages/`

### §6.3 — Staleness Detection

A package is considered stale if:
- It is older than 30 days and more than 3 WPs have changed status since its generation
- It references a domain version that is ≥ 2 minor releases behind current
- The `personal/` delta was generated more than 14 days ago (operational context changes fast)

---

## Appendix A — Source Discovery Quick Reference

### AOS Hub Package (`domain=aos`)

**Always read:**
```
CLAUDE.md
_aos/roadmap.yaml
methodology/AOS_CONCEPT_AND_PRINCIPLES.md
methodology/AOS_IDENTITY_ONBOARDING_v1.0.0.md
core/definition.yaml
_aos/context/PROJECT_CONTEXT.md
lean-kit/PROFILE_SELECTION_GUIDE.md
```

**STANDARD+ additional:**
```
lean-kit/modules/managed-pipeline/L25_QUICK_REFERENCE.md
methodology/lod-standard/TEAM_100_LOD_STANDARD_v0.3.md
lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml
_aos/ideas.json
governance/directives/ADR031_*.md through ADR036_*.md
core/ui/guides/AOS_COMMAND_REFERENCE_v1.0.0.html
core/ui/guides/AOS_TEAM_MESSAGING_USER_GUIDE_v1.0.0.html
core/ui/guides/AOS_IRON_RULES_v1.0.0.html
core/ui/guides/AOS_GATE_LIFECYCLE_v1.0.0.html
core/ui/guides/AOS_SESSION_STARTUP_v1.0.0.html
core/ui/guides/AOS_API_QUICK_REFERENCE_v1.0.0.html
core/ui/guides/AOS_AUTHORITY_MAP_v1.0.0.html
core/ui/guides/AOS_PROJECTS_PORTFOLIO_v1.0.0.html
```

**COMPREHENSIVE additional:**
```
governance/directives/ADR037_*.md through ADR043_*.md
_aos/context/CODE_STANDARDS.md
_aos/governance/team_*.md  ← all canonical team contracts
```

### TikTrack Package (`domain=tiktrack`)

**Additional sources:**
```
/Users/nimrod/Documents/TikTrack-Phoenix_AOSProject/CLAUDE.md
/Users/nimrod/Documents/TikTrack-Phoenix_AOSProject/_aos/roadmap.yaml
/Users/nimrod/Documents/TikTrack-Phoenix_AOSProject/_aos/context/PROJECT_CONTEXT.md
/Users/nimrod/Documents/TikTrack-Phoenix_AOSProject/_aos/governance/  ← domain team contracts
```

Note: Hub governance files (`CLAUDE.md` Iron Rules, `core/definition.yaml`) apply to all spokes. Do not duplicate — reference hub package files instead.

### nimrod-book Package (`domain=nimrod-book`)

```
/Users/nimrod/Documents/{nimrod-book-path}/
├── docs/structure/       ← chapter outline, taxonomy
├── docs/audience/        ← reader profile
├── _aos/ (if present)    ← governance snapshot
└── README.md             ← project brief
```

Content archetype: `CONTENT_SUBSTRATE` — emphasize output structure and audience over technical governance.

---

## Appendix B — NotebookLM Format Cheatsheet

### What NotebookLM indexes well
- H1/H2/H3 hierarchy — used for topic segmentation and navigation
- Bold terms — treated as key concepts for extraction
- Tables — parsed as structured data, excellent for Q&A
- Numbered lists — treated as ordered procedures
- Code blocks — indexed as technical reference (good for "how do I do X" queries)
- Paragraph breaks — each paragraph is an independent semantic unit

### What NotebookLM handles poorly
- Long unbroken prose (>500 words without headings)
- Raw YAML/JSON without explanatory prose around it
- HTML markup (strips tags but loses structure)
- Files larger than ~10,000 words (indexed but lower retrieval quality)
- Files with no H1 (treated as orphan content)
- Multiple unrelated topics in one file (creates retrieval confusion)

### Optimal file size
- **Sweet spot:** 2,000–5,000 words per file
- **Minimum useful:** 500 words (below this, upload as inline note instead)
- **Maximum useful:** 8,000 words (above this, split into two files)

### Audio Overview tips
- Upload README first — sets framing for the AI hosts
- After all sources are loaded, click "Audio Overview" → "Customize"
- Suggested customizations by audience:
  - BASE/investor: "Focus on the business case and ROI. Explain what problem this solves and why it's hard to replicate."
  - PERSONAL: "Focus on operational detail. What does a typical day look like? What are the key risks and gotchas?"
  - TECHNO: "Focus on architecture and implementation. How are the components connected? What are the extension points?"

### Source count recommendations
| Package | File count | Notes |
|---------|-----------|-------|
| OVERVIEW | 5–6 | All fit in one NotebookLM notebook |
| STANDARD | 10–13 | Optimal for free tier (max 50 sources) |
| COMPREHENSIVE + both deltas | 23 | Still within free tier; excellent coverage |
| Full + both deltas | 23 | Verified working — AOS package as of 2026-04-22 |

---

## Appendix C — Example Confirmation Blocks

### Example 1: AOS BASE STANDARD (investor pitch)

```
📦 NotebookLM Package — אשר פרמטרים:
┌──────────────────────────────────────────────────────────────────┐
│  0  ← צור חבילה                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [1] דומיין:     aos                                              │
│ [2] סוג:        BASE                                             │
│ [3] דלטה:       none                                             │
│ [4] עומק:       STANDARD                                         │
│ [5] שפה:        en                                               │
│ [6] מטרה:       "investor pitch — Q2 2026"                       │
│ [7] תיקייה:     _COMMUNICATION/team_100/aos notebooklm 2026-04   │
├──────────────────────────────────────────────────────────────────┤
│  9  ← בטל                                                        │
└──────────────────────────────────────────────────────────────────┘
📁 Output: README + 8 core files + 4 guide extracts = 13 files
```

### Example 2: AOS COMPREHENSIVE with both deltas (Team 00 full context)

```
📦 NotebookLM Package — אשר פרמטרים:
┌──────────────────────────────────────────────────────────────────┐
│  0  ← צור חבילה                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [1] דומיין:     aos                                              │
│ [2] סוג:        BASE                                             │
│ [3] דלטה:       both                                             │
│ [4] עומק:       COMPREHENSIVE                                    │
│ [5] שפה:        mixed                                            │
│ [6] מטרה:       "Team 00 full operational context"               │
│ [7] תיקייה:     _COMMUNICATION/team_100/aos notebooklm full 2026-04 │
├──────────────────────────────────────────────────────────────────┤
│  9  ← בטל                                                        │
└──────────────────────────────────────────────────────────────────┘
📁 Output: README + 8 core + 4 guides + 5 personal + 5 techno = 23 files
   Estimated: ~45,000 words
```

### Example 3: TikTrack BASE OVERVIEW (client demo)

```
📦 NotebookLM Package — אשר פרמטרים:
┌──────────────────────────────────────────────────────────────────┐
│  0  ← צור חבילה                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [1] דומיין:     tiktrack                                         │
│ [2] סוג:        BASE                                             │
│ [3] דלטה:       none                                             │
│ [4] עומק:       OVERVIEW                                         │
│ [5] שפה:        en                                               │
│ [6] מטרה:       "client demo — TikTrack social analytics"        │
│ [7] תיקייה:     _COMMUNICATION/team_100/tiktrack notebooklm 2026-04 │
├──────────────────────────────────────────────────────────────────┤
│  9  ← בטל                                                        │
└──────────────────────────────────────────────────────────────────┘
📁 Output: README + 5 core files = 6 files
   Note: TikTrack domain sources supplement AOS hub governance files
```

### Example 4: nimrod-book PERSONAL (author working context)

```
📦 NotebookLM Package — אשר פרמטרים:
┌──────────────────────────────────────────────────────────────────┐
│  0  ← צור חבילה                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [1] דומיין:     nimrod-book                                      │
│ [2] סוג:        PERSONAL                                         │
│ [3] דלטה:       personal                                         │
│ [4] עומק:       STANDARD                                         │
│ [5] שפה:        mixed                                            │
│ [6] מטרה:       "author working context — book v3.0 sprint"      │
│ [7] תיקייה:     _COMMUNICATION/team_100/book notebooklm 2026-04  │
├──────────────────────────────────────────────────────────────────┤
│  9  ← בטל                                                        │
└──────────────────────────────────────────────────────────────────┘
📁 Output: README + 8 core files + 5 PERSONAL_ files = 14 files
   Note: CONTENT_SUBSTRATE archetype — emphasize chapter structure and audience
```

---

*Procedure version 1.0.0 — covers AOS profiles L0, L2, L2.5 — all lifecycle archetypes (SOFTWARE, CONTENT_SUBSTRATE, 3D_CREATIVE, DOMAIN_AGENT)*
