---
procedure_id: P-OPS-3
date: 2026-04-13
status: ACTIVE
authored_by: team_110
approved_by: team_00
---

# P-OPS-3: Cowork Package Submission Standard

## Rule

Every work package submitted for execution via the Cowork channel **must** be delivered as a self-contained folder. The recipient (Team 00 or the executing agent) receives **one path** and **one main file name** — nothing else is needed to start.

## Cowork Environment Capabilities

The Cowork executing agent runs on a **sandboxed Linux VM** with persistent file access. It is a full development environment, not a chat-only interface.

### Available Capabilities

| Capability | Description | Use For |
|-----------|-------------|---------|
| **Shell (Bash)** | Ubuntu 22 with Python 3.10, grep, diff, pytest | Verification gates, file diffs |
| **File Tools** | Read, Write, Edit tools on mounted folders | Reading source, writing modified files |
| **Python Execution** | pip install, script execution, module imports | Running tests, validation scripts |
| **TodoList** | Built-in progress tracking | Per-WP and per-AC tracking |
| **Mounted Folders** | Host folders mounted at `/sessions/.../mnt/` | All source, specs, data, tests |

### Key Constraints

1. **No git.** Files are mounted copies, not a repo. No `git diff`, no rollback. Use a separate output directory so originals stay intact.
2. **Ephemeral session.** Temporary files are cleared between sessions. Output must be written to the mounted workspace.
3. **Context window limit.** Very large files (700+ lines) should be read in sections using grep to locate specific lines first. Specs and mandates should be read on-demand per WP, not all upfront.
4. **Mounted paths, not repo paths.** Files are accessed via mount points (e.g., `mnt/S005-P004/assets/src/...`), not repo-relative paths. All Instructions and prompts must use anchored paths with a `SOURCE_ROOT` variable.
5. **Folder names must be ASCII-safe.** Avoid spaces, em-dashes, and Unicode in mounted folder names — they cause shell quoting issues.

### File Access Rules

- Files are accessed via **mounted paths**, not uploads. Use `SOURCE_ROOT` variable to anchor all paths.
- Output files **must** be written to a dedicated output directory (e.g., `SOURCE_ROOT/output/`) preserving directory structure. This enables diff review and safe re-runs.
- Never reference files as "uploaded" — use "mounted", "available at", or "located at".
- Never instruct the agent to "output complete file contents" as text — instruct it to **write files** using Edit/Write tools.

### Verification Strategy

- Instructions should **encourage** shell tool use for verification, not restrict it.
- Use actual `grep` commands with expected results (e.g., `grep -rn "price_chf" ... → Expected: zero hits`).
- Use `pytest` when test files are present and ACs require test passage.
- Prefer `Edit` tool (targeted diffs) over `Write` (full replace) for modifications.
- Track progress with TodoList tool, not by re-summarizing in text.

## Instructions vs Activation Prompt — Critical Distinction

PACKAGE.md **must** contain both an **Instructions** section and an **Activation Prompt** section. They serve fundamentally different roles:

### Instructions (Project-Level Context)

**What it is:** The system-level context that the agent carries throughout the entire session. This is pasted into the Cowork project's "Instructions" field. The agent reads this **before** any message.

**Purpose:** Establish identity, environment constraints, project understanding, and behavioral rules.

**Must contain:**
- **Agent identity** — who you are, which project, which team
- **Environment capabilities** — Cowork VM with shell, Python, file tools. SOURCE_ROOT and OUTPUT_ROOT paths.
- **Codebase overview** — what the application does, architecture summary, data flow between components
- **File roles by WP** — which files each WP modifies, with key change summary. Do not include static line numbers (the agent reads files directly and sees current line numbers). Use the pattern: `MODIFY: file1, file2. Key changes: description.`
- **Behavioral rules** — use Edit tool for changes, Write for new files, shell for verification, TodoList for progress
- **WP dependency map** — why linear execution is required, which WP produces what for the next

**Token budget:** Keep Instructions under 2000 tokens — they are loaded into every message.

**Character:** Declarative. Describes the world the agent works in. Does not say "do this" — says "this is what exists, this is how it works, these are the rules."

### Activation Prompt (Execution Trigger)

**What it is:** The first message sent to the agent after the project is set up with Instructions and files. This is pasted into the chat as a user message.

**Purpose:** Command the agent to start executing. Tells it exactly what to do, in what order, with what verification.

**Must contain:**
- **SOURCE_ROOT / OUTPUT_ROOT** — exact mount paths at the top
- **Per-WP workflow** — read mandate → read spec → read source → apply changes → write to output → verify
- **WP chaining rule** — WP002+ must read from OUTPUT_ROOT (not SOURCE_ROOT) for files already modified by prior WPs
- **Verification gates per phase** — actual shell commands with expected results (e.g., `grep -rn ... → Expected: zero hits`)
- **Scope boundaries per phase** — reference mandate DO NOT lists
- **Iron rules** — execution discipline, output format

**Character:** Imperative. Says "do this now." Assumes the agent already knows the codebase (from Instructions) and just needs the work order.

### Why Both Are Required

| Without Instructions | Without Activation Prompt |
|---------------------|--------------------------|
| Agent doesn't know what the files are or how they relate. It will guess, hallucinate structure, or ask clarifying questions. | Agent understands the codebase but has no work order. It sits idle or asks "what should I do?" |
| Every phase instruction must re-explain the architecture. Wastes tokens, risks inconsistency. | Context is wasted — the agent has all the knowledge but no directive. |

**The split keeps context (Instructions) separate from commands (Activation Prompt).** If the agent needs to restart or a new phase begins, the Instructions persist while a new Activation Prompt can be sent.

## Folder Structure

```
_COMMUNICATION/cowork/{PACKAGE_ID}/
├── PACKAGE.md                          ← main file (identity, setup checklist, manifest)
├── {PACKAGE_ID}_INSTRUCTIONS.txt       ← plain text, copy-paste into Cowork Instructions field
├── {PACKAGE_ID}_ACTIVATION_PROMPT.txt  ← plain text, copy-paste as first chat message
└── assets/                             ← all required files, organized by role
    ├── specs/                          ← LOD400 specs, mandates (read-only guidance)
    ├── src/                            ← source code files (current versions to edit)
    ├── data/                           ← data files (current versions to edit)
    └── tests/                          ← test files (update assertions for renamed fields; do not change test logic or add new tests)
```

### Standalone Copy-Paste Files

Instructions and Activation Prompt **must** be delivered as separate `.txt` files alongside PACKAGE.md, named `{PACKAGE_ID}_INSTRUCTIONS.txt` and `{PACKAGE_ID}_ACTIVATION_PROMPT.txt`. These files contain **only** the exact text to paste — no markdown headers, no code fences, no commentary. This eliminates copy-paste errors from extracting content embedded in code blocks within PACKAGE.md. PACKAGE.md references these files in a setup checklist rather than embedding their content.

## PACKAGE.md — Required Sections

| Section | Content | Destination |
|---------|---------|-------------|
| **Identity** | Package ID, date, version, sprint, WP list, authoring team, authority | Reference |
| **Purpose** | What the codebase is, what this package does, why | Reference |
| **Cowork Setup** | Setup checklist referencing the two `.txt` files. Step-by-step: create project, mount folder, paste Instructions, start chat, paste Activation Prompt. | Operator guide |
| **File Manifest** | Every file in the folder (copy-paste files + assets/) with: name, description, role (modify/read-only), WP | Reference |
| **Validation Criteria** | Per-phase assertions. Team 00 runs these after integrating agent output. | Post-execution |
| **Expected Output** | List of files the agent produces with description of changes | Reference |

## Rules

1. **Self-contained.** Everything the builder needs is inside the folder. No external references.
2. **Current copies.** Files in `assets/` are copies at submission time.
3. **One path, one file.** Submission = folder path + `PACKAGE.md`.
4. **Manifest is truth.** Not in manifest = not in scope. In manifest = must be in `assets/`.
5. **Immutable after submission.** Changes require a new version (new folder, e.g., `S005-P004-v3/`).
6. **Instructions assume zero context.** The agent knows nothing. Instructions explain everything from scratch.
7. **Activation Prompt assumes Instructions are loaded.** Do not repeat codebase architecture in the prompt — reference it.
8. **Use shell for verification.** Verification gates are actual `grep`/`pytest` commands the agent runs in Cowork's shell, not textual assertions.
9. **Output to dedicated directory.** Agent writes modified files to `OUTPUT_ROOT/` preserving directory structure. Originals in `SOURCE_ROOT/` stay intact for diff and re-run.
10. **Anchored paths.** All file references use `SOURCE_ROOT` / `OUTPUT_ROOT` variables defined at the top of the Activation Prompt.
11. **ASCII-safe folder names.** No spaces, em-dashes, or Unicode in mounted folder names.
12. **Test files: align assertions only.** Update field name references in test assertions to match new schema. Do not change test logic or add new tests.
13. **Archive on close.** Completed packages move to `_archive/cowork/{PACKAGE_ID}/` at repo root.

## Archive Procedure

When package execution is complete:

```bash
mv _COMMUNICATION/cowork/{PACKAGE_ID}/ _archive/cowork/{PACKAGE_ID}/
```

Archive preserves the exact submission state for audit trail. Archived packages are never modified.

## Delivery Format

```
Path:  _COMMUNICATION/cowork/{PACKAGE_ID}/
Files: PACKAGE.md
       {PACKAGE_ID}_INSTRUCTIONS.txt
       {PACKAGE_ID}_ACTIVATION_PROMPT.txt
```

---

## Template: PACKAGE.md

Below is the canonical template. Every PACKAGE.md must follow this structure. Instructions and Activation Prompt content lives in the standalone `.txt` files, not embedded in PACKAGE.md.

````markdown
# {PACKAGE_ID} — {Title}

## Identity

| Field | Value |
|-------|-------|
| **Package ID** | {PACKAGE_ID} |
| **Sprint** | {Sprint ID} — {Sprint name} |
| **Date** | {YYYY-MM-DD} |
| **Version** | {vN — description} |
| **Work Packages** | {WP list with short names} |
| **Total ACs** | {number} |
| **Authoring Team** | {team} |
| **Authority** | {approver} |

---

## Purpose

{What the codebase is. What this package does. Why it's needed. 2-3 paragraphs.}

---

## Cowork Setup

### Copy-Paste Files

| File | Paste Into | Content |
|------|-----------|---------|
| **`{PACKAGE_ID}_INSTRUCTIONS.txt`** | Cowork project "Instructions" field | Agent identity, environment, architecture, execution rules, file roles |
| **`{PACKAGE_ID}_ACTIVATION_PROMPT.txt`** | First chat message | Phase-by-phase execution plan, verification gates, iron rules |

### Setup Checklist

1. Create a Cowork project named `{PACKAGE_ID}-{ShortTitle}`
2. Mount this folder as the workspace
3. Open `{PACKAGE_ID}_INSTRUCTIONS.txt` → copy entire content → paste into project Instructions
4. Create a new chat session
5. Open `{PACKAGE_ID}_ACTIVATION_PROMPT.txt` → copy entire content → paste as first message
6. Output directory will be created by the agent at `SOURCE_ROOT/output/`

---

## File Manifest

### Root — Copy-Paste Files (2 files)

| File | Content |
|------|---------|
| `{PACKAGE_ID}_INSTRUCTIONS.txt` | Exact text for Cowork project Instructions field |
| `{PACKAGE_ID}_ACTIVATION_PROMPT.txt` | Exact text for first Cowork chat message |

### assets/specs/ ({N} files)

| File | What it is | Used by |
|------|-----------|---------|
| `{filename}` | {one sentence} | {Phase N} |

### assets/src/ ({N} files)

| File | Role | WP |
|------|------|-----|
| `{filename}` | **modify** / read-only | {WP} |

### assets/data/ ({N} files)

| File | Role | WP |
|------|------|-----|
| `{filename}` | **modify** / read-only | {WP} |

### assets/tests/ ({N} files)

| File | Role |
|------|------|
| `{filename}` | Update assertions for renamed fields only. |

---

## Validation Criteria

### After Phase 1
- {grep command} → {expected result}

### After Phase N
- {grep command} → {expected result}

### Final Comprehensive
- {cross-phase assertion}

---

## Expected Output

| Phase | File | Changes |
|-------|------|---------|
| 1 | `{filename}` | {what changed} |

---

*Package prepared by {team} on authority of {approver} | {project} | {PACKAGE_ID} | {date}*
````

---

## Appendix A: Design Decisions and Lessons Learned

This appendix documents the full evolution of the Cowork package standard through the S005-P004 implementation (2026-04-13). It captures original problems, Team 00 directives, Team 20 (Builder) findings, and resolved decisions. This material is intended for canonicalization of the Cowork process in the AOS system.

### A.1 — Self-Contained Folder Requirement

**Origin:** Team 00 directive. The initial package was presented as a list of 39 individual files for manual upload. Team 00 rejected this ("מה אני עובד אצלכם???") and mandated a self-contained folder with a single main file.

**Decision:** Every submission must be a folder at `_COMMUNICATION/cowork/{PACKAGE_ID}/` containing `PACKAGE.md` (main file) and `assets/` (all required files organized by role: specs/, src/, data/, tests/).

**Rationale:** The operator receives one path and one file name. No assembly required, no file-hunting. The folder is portable — it can be mounted into Cowork, zipped for transfer, or moved to archive as a unit.

### A.2 — Instructions vs Activation Prompt Split

**Origin:** Team 00 rejected a combined single-section prompt: "הקובץ הראשי חייב לכלול גם instructions וגם פרומט הפעלה... לבחון לעומק את מהות ההבדל."

**Problem:** A single combined section mixed declarative context (what the codebase is) with imperative commands (what to do now). This caused token waste (architecture re-explained in every phase) and made it impossible to restart a phase without re-sending context.

**Decision:** Two distinct sections with different characters:
- **Instructions** = declarative system context. Loaded into every message. Describes the world.
- **Activation Prompt** = imperative execution trigger. Sent once as first message. Commands action.

**Example of what belongs where:**

| Content | Belongs In | Why |
|---------|-----------|-----|
| "config.py contains CityDefinition at line 40" | Instructions | Declarative fact about the codebase |
| "In config.py, add currency: str = 'CHF' after country" | Activation Prompt | Imperative change command |
| "WP001 must complete before WP002" | Instructions | Persistent architectural constraint |
| "Run: grep -rn 'price_chf' ... → Expected: zero hits" | Activation Prompt | Phase-specific verification gate |
| "Use Edit tool for changes, Write for new files" | Instructions | Behavioral rule (persistent) |
| "Start from WP001 output, not original source" | Activation Prompt | Phase-specific chaining instruction |

### A.3 — Cowork Environment Discovery (Critical Pivot)

**Origin:** Team 20 (Builder) Cowork Adaptation Report, after first execution attempt failed.

**Problem (v1-v2):** The original Instructions stated: "You cannot run shell commands, execute Python, or access the repository." This was written assuming a chat-only interface. In reality, Cowork provides a full Linux VM with shell, Python, file tools, and mounted directories.

**Impact:** The agent refused to use its most powerful capabilities. It tried to output complete file contents as text (flooding context window) instead of writing files. Verification was textual ("check that X is true") instead of executable (`grep -rn ...`).

**5 Critical Issues Identified by Team 20:**

| # | Issue | Severity | Resolution |
|---|-------|----------|------------|
| 1 | Environment instruction disables agent capabilities | CRITICAL | Reversed: "FULL capabilities: Shell, File Tools, Python, TodoList" |
| 2 | File paths don't match mount structure | CRITICAL | Anchored all paths to `SOURCE_ROOT = mnt/{PACKAGE_ID}/assets` |
| 3 | Output workspace undefined | CRITICAL | Added `SOURCE_ROOT/output/` with directory structure preservation |
| 4 | Folder name has special characters (em-dash, spaces) | HIGH | Rule 11: ASCII-safe folder names only |
| 5 | "Uploaded" file metaphor is wrong | HIGH | Changed to "mounted", "available at", "located at" |

**Decision:** Complete rewrite of environment section, file access rules, and verification strategy. The procedure now documents Cowork as a full development environment, not an isolated chat.

### A.4 — Output Directory Strategy

**Origin:** Team 20 recommendation, confirmed by Team 00.

**Problem:** If the agent modifies files in-place and makes a mistake, there is no rollback (no git in Cowork). The original source is lost.

**Decision:** Separate output directory (`SOURCE_ROOT/output/`) preserving the original directory structure. Original files in `SOURCE_ROOT/` remain untouched.

**Implication for WP chaining:** When WP002 needs a file already modified by WP001 (e.g., config.py), it must read from `output/` not from the original `src/`. The Activation Prompt must explicitly state this for each phase.

**Example (from S005-P004):**
```
PHASE 2 — Step 2:
  IMPORTANT: Start from WP001 output files (SOURCE_ROOT/output/), not original source.
  For config.py and flatfox.py, read from output/ since WP001 already modified them.
  For runner.py and sources.json, read from SOURCE_ROOT/src/ and SOURCE_ROOT/data/ (unmodified by WP001).
```

### A.5 — Verification Strategy Evolution

**v1 (Chat-oriented):** Textual assertions: "✓ No field named price_chf in any .py file"
- Problem: The agent has no way to mechanically verify. It self-checks by reasoning, which is unreliable.

**v2 (Transitional):** Same textual assertions, shorter.
- Problem: Still no executable verification.

**v3-v4 (Cowork-native):** Actual shell commands with expected results:
```
grep -rn "price_chf" SOURCE_ROOT/output/src/ --include="*.py" | grep -v "\.get\("
→ Expected: zero hits
```
- The agent runs the command, sees the output, and can fix issues before proceeding.
- Python validation scripts for complex checks (e.g., verifying Locale dataclass has exactly 10 fields).

### A.6 — Activation Prompt Length Problem

**Origin:** v1 Activation Prompt was ~175 lines inside a code block. Cowork rejected it with a length error.

**Root cause:** The prompt duplicated all per-file change instructions that already existed in the LOD400 specs and mandates (which were uploaded as files).

**Decision (v2):** Replace inline instructions with references to uploaded documents:
```
Step 1 — Read scope:
  • Read SOURCE_ROOT/specs/MANDATE_S005-P004-WP001_TEAM20.md
  • Read SOURCE_ROOT/specs/LOD400_S005-P004-WP001.md
Step 2 — Implement per LOD400 spec §2.1–§2.10
```

**Result:** Activation Prompt reduced from ~175 lines to ~85 lines. The agent reads the actual spec files on-demand per WP, which is more reliable than a summary.

### A.7 — Standalone Copy-Paste Files

**Origin:** Team 00 directive: "instraction + promt בנוסף לקובץ חבילה יש לייצר קובץ טקסט פשוט המכיל רק את התוכן המדוייק להעתקה"

**Problem:** In v1-v3, Instructions and Activation Prompt were embedded inside PACKAGE.md in markdown code blocks (`` ``` ``). Copy-pasting required: open PACKAGE.md → find the right code block → carefully select inside the fences → copy → paste. This introduced errors (accidentally including the fences, missing the last line, copying from the wrong section).

**Decision (v4):** Two standalone `.txt` files alongside PACKAGE.md:
- `{PACKAGE_ID}_INSTRUCTIONS.txt` — exact text for Instructions field
- `{PACKAGE_ID}_ACTIVATION_PROMPT.txt` — exact text for first chat message

These files contain only the content to paste — no markdown, no headers, no commentary. PACKAGE.md references them in a setup checklist instead of embedding content.

**Naming convention:** `{PACKAGE_ID}_INSTRUCTIONS.txt` and `{PACKAGE_ID}_ACTIVATION_PROMPT.txt` — the package ID prefix ensures the files are identifiable outside the folder context.

### A.8 — Test File Policy

**Origin:** Contradiction discovered by Team 20 Adaptation Report (§6.2.2).

**Problem:** Instructions said test files are "read-only (must not break)" but also "review test files and update assertions that reference renamed fields." These are contradictory — if test assertions reference `price_chf` and the field is renamed to `price`, the assertions must change.

**Decision:** Test files are modifiable, but narrowly scoped: "Update assertions referencing renamed fields. Do not change test logic or add new tests — only align field name references with the new schema."

**Rationale:** This preserves the intent (don't break test coverage) while acknowledging the mechanical reality (renamed fields require updated assertions).

### A.9 — Static Line Numbers in Instructions

**Origin:** Team 20 Adaptation Report (§6.2.4).

**Problem (v1-v2):** Instructions included static line numbers: "CityDefinition at line 40, SearchProfile at line 88." In Cowork, the agent reads files directly with Read tool and sees current line numbers. Static references can be stale (file sizes didn't match reported counts) and waste tokens.

**Decision:**
- **Instructions:** No static line numbers. Use file roles by WP: `MODIFY: config.py, scorer.py. Key changes: price_chf→price, +currency.`
- **LOD400 specs:** Line numbers may remain as implementation guidance — the agent reads the spec on-demand per WP and can verify against the actual file.

### A.10 — Archive Location

**Origin:** Team 00 directive: "תקיית ארכיון צריכה להיות מוכנה להוצאה מהרפו ולכן חייבת לשבת תחת תקיית הארכיון הראשית ולא תחת התקיה שלנו."

**Problem:** Initial archive was at `_COMMUNICATION/cowork/_archive/`. This placed archive inside the team communication folder, making it impossible to separate from the repo independently.

**Decision:** Archive at repo root: `_archive/cowork/{PACKAGE_ID}/`. The `_archive/` folder can be extracted from the repo as a standalone artifact set.

### A.11 — Version History (S005-P004)

| Version | Date | Changes | Trigger |
|---------|------|---------|---------|
| v1 | 2026-04-13 | Initial: combined Instructions+Prompt, chat-oriented, no shell | First submission |
| v2 | 2026-04-13 | Shortened prompt with spec references, added file index | Prompt too long for Cowork |
| v3 | 2026-04-13 | Full Cowork adaptation: shell, mounted paths, output dir, grep verification | Team 20 Adaptation Report |
| v4 | 2026-04-13 | Standalone .txt files for copy-paste, PACKAGE.md as setup guide | Team 00 directive |
| v5 | 2026-04-13 | Shell variable resolution fix, mkdir, validator-certified (99.1% PASS) | AOS Package Validator findings |
| v6 | 2026-04-13 | Mount-path alignment, cross-ref fix, Instructions/Prompt separation, validator v1.1 (CHECK 11) | Team Cowork v5 quality review |
| v7 | 2026-04-13 | grep BRE regex fix — `\(` in double quotes → single-quoted `'\.get('` | Team Cowork v6 quality review |

### A.12 — Reference Documents

The following documents were produced during the S005-P004 Cowork adaptation process and are preserved at `_aos/lean-kit/modules/managed-pipeline/procedures/`:

| Document | Author | Content |
|----------|--------|---------|
| `Cowork_Adaptation_Report_S005-P004.docx` | Team 20 (Builder) | 9-section report: environment capabilities, 5 critical issues, 8 recommendations, before/after comparison |
| `COWORK_OPTIMIZED_INSTRUCTIONS.md` | Team 20 (Builder) | Ready-to-use Instructions + Activation Prompt + setup checklist + comparison table |

---

## Appendix B: Automated Validation Integration (Improvement Round v4→v5)

This appendix documents the fifth improvement round: integration of an automated validation tool into the package submission workflow. This is working material intended as a foundation for future canonicalization into AOS procedure, not a finalized standard.

### B.1 — Background

After 4 rounds of manual review (v1→v4), Team Cowork developed `aos_package_validator.py` — a generic Python tool that performs automated structural validation of Cowork packages. The tool was run against S005-P004-v4 and revealed a systemic issue invisible to all prior human reviews.

**Key finding:** All shell commands in the activation prompt used `SOURCE_ROOT/output/src/...` as literal text instead of `$SOURCE_ROOT/output/src/...` (shell variable expansion). In Cowork's Bash environment, the literal string tries to access a directory named "SOURCE_ROOT" — which doesn't exist. This would cause every verification gate to fail silently during execution.

This single issue affected 15 of 15 shell commands in the activation prompt. No human reviewer (Team 110, Team 00, Team 20) caught it across 4 review cycles.

### B.2 — AOS Package Validator Tool

**Location:** `_aos/lean-kit/modules/managed-pipeline/procedures/aos_package_validator.py`
**Config template:** `_aos/lean-kit/modules/managed-pipeline/procedures/aos_validator_config_template.json`

The validator performs 10 categories of automated checks:

| # | Check | What It Validates |
|---|-------|-------------------|
| 1 | FILE_EXISTS | All manifest files exist on disk (source, specs, mandates, Instructions, Prompt) |
| 2 | PATH_RESOLUTION | Shell commands don't use unresolved variable labels as literal text |
| 3 | SOURCE_ROOT_CONSISTENCY | SOURCE_ROOT is defined identically in all documents and exported as shell variable |
| 4 | CROSS_REFERENCE | Paths referenced in specs/mandates actually exist in the package |
| 5 | WORK_PACKAGE_COMPLETENESS | Each WP has spec, mandate, and all target files present |
| 6 | OUTPUT_STRUCTURE | Output directory instructions exist and mkdir commands are present |
| 7 | COWORK_CAPABILITIES | Instructions declares required capabilities (Shell, Python, etc.) without contradictions |
| 8 | FIELD_RENAMES | Old field names exist in source (confirming rename needed) and new names appear in specs |
| 9 | VERIFICATION_GATES | grep/python verification commands exist, are correctly formed |
| 10 | WP_DEPENDENCY_CHAIN | Activation prompt enforces linear WP order and output chaining |

**Severity levels:** CRITICAL (blocks submission), HIGH, MEDIUM, LOW, INFO

**Usage:**
```bash
python3 aos_package_validator.py <config.json>
```

Produces both text report (stdout) and JSON report (`<config>_report.json`).

**Pass criteria:** 0 CRITICAL findings. Score should be > 95%.

### B.3 — Validator Config Structure

Each package requires a validator config JSON file. The config template (`aos_validator_config_template.json`) documents all fields. Key sections:

- `package_id`, `version`, `package_root` — Package identity and local path
- `source_root_label`, `source_root_rel` — How SOURCE_ROOT is named and where it points
- `instruction_file`, `prompt_file`, `doc_files` — Files to scan for correctness
- `manifest` — Complete file manifest with roles (`modify`/`create`/`read-only`) and WP assignments
- `work_packages` — Per-WP spec, mandate, and target file lists
- `field_renames` — Old→new field name mappings with optional fallback patterns
- `path_references` — Known path references in docs mapped to actual paths (or `"INVALID"`)
- `cowork_capabilities` — List of capabilities that Instructions should declare

### B.4 — Bugs Found and Fixed in Validator

During the v4→v5 cycle, Team 110 identified and fixed 3 bugs in the validator tool:

| # | Bug | Impact | Fix |
|---|-----|--------|-----|
| 1 | Regex `(?<!["\'])\bSOURCE_ROOT/` matched `$SOURCE_ROOT/` as unresolved | False positives: properly resolved `$VAR` references flagged as CRITICAL | Added `$` to negative lookbehind: `(?<![$"\'])` + explicit `$` check for quoted labels |
| 2 | `CROSS_REF_INVALID` entries (known bad paths marked in config) scored as MEDIUM failures | Inflated failure count for paths explicitly marked as expected-invalid | Changed severity to INFO and counted as passed (config explicitly marks them INVALID) |
| 3 | `grep -rn` on single file flagged as "recursive without --include" | False positive: `-rn` on a file path (not directory) doesn't need `--include` | Added path analysis: only flag when target ends with `/` (directory) |

### B.5 — v4→v5 Changes Applied

**In the activation prompt (`S005-P004_ACTIVATION_PROMPT.txt`):**

| Change | Before (v4) | After (v5) | Lines Affected |
|--------|-------------|------------|----------------|
| SOURCE_ROOT definition | `SOURCE_ROOT = "mnt/S005-P004/assets"` | `export SOURCE_ROOT="mnt/S005-P004/assets"` | 4-5 |
| mkdir output dirs | (missing) | `mkdir -p "$SOURCE_ROOT/output/src/..."` | 6 |
| Shell command paths | `grep ... SOURCE_ROOT/output/src/` | `grep ... "$SOURCE_ROOT/output/src/"` | 15 locations |
| Python one-liners | `open('SOURCE_ROOT/output/...')` | `open(os.environ['SOURCE_ROOT']+'/output/...')` | 2 locations |
| Redundant -r flag | `grep -rn ... single_file.py` | `grep -n ... single_file.py` | 2 locations |

**In the Instructions (`S005-P004_INSTRUCTIONS.txt`):**

| Change | Before | After |
|--------|--------|-------|
| SOURCE_ROOT definition | `SOURCE_ROOT = mnt/S005-P004/assets` | `export SOURCE_ROOT="mnt/S005-P004/assets"` |

### B.6 — Validation Results Comparison

| Metric | v4 (before) | v5 (after) |
|--------|-------------|------------|
| **Score** | 82.4% | **99.1%** |
| **Verdict** | FAIL | **PASS** |
| CRITICAL | 16 | **0** |
| HIGH | 0 | 0 |
| MEDIUM | 5 | **0** |
| LOW | 1 | **0** |
| INFO | 1 | 4 |

### B.7 — Requirement: Pre-Submit Validation

Based on this improvement round, every Cowork package submission MUST include:

1. **Validator tool** — `aos_package_validator.py` in the package `validation/` directory
2. **Validator config** — Filled `validate_{PACKAGE_ID}-{VERSION}.json` config file
3. **Passing report** — `validate_{PACKAGE_ID}-{VERSION}_report.json` showing 0 CRITICAL findings
4. **PACKAGE.md reference** — Pre-Submit Validation Report section with score table

The validator config template (`aos_validator_config_template.json`) serves as the reference for creating per-package configs.

**Pre-submit checklist addition:**
- [ ] Run `python3 validation/aos_package_validator.py validation/validate_*.json`
- [ ] Confirm verdict: PASS with 0 CRITICAL findings
- [ ] Include report JSON in `validation/` directory
- [ ] Add validation results table to PACKAGE.md

### B.8 — Post-Submit Usage

The validator and config are included in the package so they can be run inside Cowork after execution to verify the agent's output. The Cowork agent can run:

```bash
cd validation/
python3 aos_package_validator.py validate_S005-P004-v5.json
```

This enables a verification loop: pre-submit validation by the authoring team + post-submit self-check by the executing agent.

### B.9 — Lessons Learned

1. **Automated checks catch what humans miss:** The literal-vs-variable distinction in shell commands is invisible to human review but instantly detectable by regex. After 4 human review cycles (including Team 20 Cowork experts), this fundamental error persisted.

2. **Validator-driven development:** Running the validator against each version creates a feedback loop. The v4→v5 cycle was completed in under 30 minutes because the validator pinpointed exact lines and provided specific fix suggestions.

3. **Tool quality matters:** The validator itself had 3 bugs that produced false positives. A validator that cries wolf undermines trust. Bug fixes must be applied to the canonical tool copy, not just local patches.

4. **Config as documentation:** The validator config (`validate_*.json`) serves double duty — it drives automated checks AND documents the complete package structure (manifest, WPs, field renames, capabilities) in machine-readable form.

5. **Severity calibration:** Not all findings are equal. Known-invalid cross-references should be INFO, not MEDIUM. Severity inflation obscures real issues.

### B.10 — Reference Documents (v4→v5 Round)

| Document | Location | Content |
|----------|----------|---------|
| `aos_package_validator.py` | `_aos/lean-kit/modules/managed-pipeline/procedures/` | Canonical validator tool (with bug fixes) |
| `aos_validator_config_template.json` | `_aos/lean-kit/modules/managed-pipeline/procedures/` | Config template with all field documentation |
| `validate_S005-P004-v4_report.json` | `_COMMUNICATION/cowork/S005-P004/` | Original Team Cowork validation run (82.4% FAIL) |
| `validate_S005-P004-v5_report.json` | `_COMMUNICATION/cowork/S005-P004-v5/validation/` | Final passing report (99.1% PASS) |

---

## Appendix C: Mount-Path Alignment and Cross-Reference Fix (Improvement Round v5→v6)

This appendix documents the sixth improvement round: fixing the mount-path mismatch, removing stale cross-references, and adding a new validator check.

### C.1 — Background

Team Cowork reviewed v5 and found that while all v4 CRITICAL findings were resolved, a new CRITICAL issue emerged: the `SOURCE_ROOT` path (`mnt/S005-P004/assets`) did not match the package folder name (`S005-P004-v5`). When Cowork mounts `S005-P004-v5` as a workspace, the actual path becomes `mnt/S005-P004-v5/assets` — making every shell command fail with "No such file or directory."

This issue was invisible to the validator because no check verified that SOURCE_ROOT aligns with the package folder name.

### C.2 — Issues Found by Team Cowork Review

| # | Severity | Issue | Resolution |
|---|----------|-------|------------|
| 1 | CRITICAL | SOURCE_ROOT path `mnt/S005-P004/assets` doesn't match folder `S005-P004-v5` | Changed to `mnt/S005-P004-v6/assets` in v6 |
| 2 | MEDIUM | Validator config contains host-local path (`/Users/.../`) — unusable in Cowork | Config now uses `SET_BEFORE_RUN` placeholder; user sets `package_root` before execution |
| 3 | MEDIUM | Mandates reference `_aos/work_packages/...` paths that don't exist in Cowork | Replaced with Cowork-local `specs/LOD400_S005-P004-WP00X.md` paths |
| 4 | LOW | `export` keyword in Instructions (declarative text, not shell) | Instructions uses `SOURCE_ROOT = ...`; only Activation Prompt uses `export` |
| 5 | PROCESS | v4 files were retroactively modified (bit-identical to v5) | v6 is a clean new folder; prior versions are not modified |

### C.3 — New Validator Check: MOUNT_PATH_ALIGNMENT (CHECK 11)

**Problem it solves:** The folder name becomes part of the Cowork mount path. If SOURCE_ROOT says `mnt/X/assets` but the folder is named `Y`, all commands fail.

**How it works:**
1. Extract folder name from `package_root` config field
2. Find all SOURCE_ROOT definitions in Instructions and Activation Prompt
3. Check if the defined path contains the folder name
4. If not → CRITICAL finding with suggested fix

**Example:**
- Package folder: `S005-P004-v6`
- SOURCE_ROOT: `mnt/S005-P004-v6/assets` → PASS
- SOURCE_ROOT: `mnt/S005-P004/assets` → CRITICAL (folder name mismatch)

### C.4 — Instructions vs Activation Prompt: export Separation

**Rule discovered:** The Instructions file is declarative system context — it should NOT contain shell syntax like `export`. The Activation Prompt is imperative execution — it SHOULD contain `export` to actually set the variable.

| File | Role | SOURCE_ROOT Format |
|------|------|--------------------|
| Instructions (.txt) | Declarative context (loaded every message) | `SOURCE_ROOT = mnt/S005-P004-v6/assets` |
| Activation Prompt (.txt) | Imperative execution (first message) | `export SOURCE_ROOT="mnt/S005-P004-v6/assets"` |

### C.5 — Validator Config Portability

**Problem:** v5 config had hardcoded host path (`/Users/nimrod/.../S005-P004-v5`), useless in Cowork.

**Solution:** Config uses `"package_root": "SET_BEFORE_RUN"` placeholder. Before running the validator (pre-submit or post-submit), the user sets `package_root` to the actual path:
- Local pre-submit: `/absolute/path/to/S005-P004-v6`
- Cowork post-submit: `/sessions/.../mnt/S005-P004-v6`

### C.6 — Cross-Reference Cleanup

Mandates referenced `_aos/work_packages/S005-P004-WP00X/LOD400_...` — internal AOS repo paths that don't exist in the Cowork-mounted package. Fixed to `specs/LOD400_S005-P004-WP00X.md` (the actual location within SOURCE_ROOT).

The `path_references` section in the validator config was also cleaned — no more `INVALID` entries since all references now point to real files.

### C.7 — v6 Validation Results

| Metric | v5 | v6 |
|--------|-----|-----|
| Score | 99.1% PASS | **99.1% PASS** |
| CRITICAL | 0* | **0** |
| Total checks | 112 | **112** |
| Findings | 4 INFO | **1 INFO** |
| Checks categories | 10 | **11** (+ MOUNT_PATH_ALIGNMENT) |

\* v5 had 0 CRITICAL per validator, but Team Cowork manual review found 1 CRITICAL that the validator couldn't detect.

### C.8 — Reference Documents (v5→v6 Round)

| Document | Location | Content |
|----------|----------|---------|
| `aos_package_validator.py` | `_aos/lean-kit/modules/managed-pipeline/procedures/` | Canonical validator v1.1 (11 checks, including MOUNT_PATH_ALIGNMENT) |
| `validate_S005-P004-v6_report.json` | `_COMMUNICATION/cowork/S005-P004-v6/validation/` | Final passing report (99.1% PASS, 1 INFO) |

---

## Appendix D: grep BRE Regex Fix (Improvement Round v6→v7)

This appendix documents the seventh improvement round: fixing a shell regex quoting issue in verification gate commands.

### D.1 — Background

Team Cowork reviewed v6 and found one remaining issue: the `grep -v` commands in the Activation Prompt used double-quoted BRE patterns containing `\(`, which is interpreted as a regex group opener in Basic Regular Expressions. On Ubuntu 22's grep (BRE mode by default), `"\.get\("` triggers `grep: Unmatched ( or \(` because `\(` opens a group with no matching `\)`.

This issue was not caught by the AOS Package Validator because it validates path resolution and structure, not shell command syntax correctness.

### D.2 — Issue Found by Team Cowork Review

| # | Severity | Issue | Resolution |
|---|----------|-------|------------|
| 1 | MEDIUM-HIGH | `grep -v "\.get\("` — double-quoted `\(` is BRE group opener on Ubuntu grep → `Unmatched ( or \(` error | Changed to single quotes: `grep -v '\.get('` |

### D.3 — Technical Explanation

In Bash, double-quoted strings undergo variable expansion but pass backslash sequences to the program. `grep` in BRE mode interprets `\(` as "start capture group" and `\)` as "end capture group." Since there's no `\)`, grep errors with "Unmatched ( or \(".

**Single quotes** prevent this: `'\.get('` passes the literal characters `\.get(` to grep, where `\.` matches a literal dot and `(` matches a literal parenthesis. This is the correct behavior for the verification gate — filtering out backward-compatible `.get("price_chf")` fallback reads.

**Affected locations in v6:**
- `S005-P004_ACTIVATION_PROMPT.txt` line 30 (WP001 verification gate)
- `S005-P004_ACTIVATION_PROMPT.txt` line 105 (final comprehensive verification)
- `PACKAGE.md` validation criteria section (human-readable documentation)

### D.4 — v7 Changes Summary

| File | Change |
|------|--------|
| `S005-P004_ACTIVATION_PROMPT.txt` | Lines 30, 105: `grep -v "\.get\("` → `grep -v '\.get('` |
| `S005-P004_INSTRUCTIONS.txt` | Line 13: `SOURCE_ROOT = mnt/S005-P004-v7/assets` |
| `PACKAGE.md` | Version bump to v7, grep fix in validation criteria, updated references |
| `validate_S005-P004-v7.json` | Version and shell_variables updated to v7 paths |

### D.5 — v7 Validation Results

| Metric | v6 | v7 |
|--------|-----|-----|
| Score | 99.1% PASS | **99.1% PASS** |
| CRITICAL | 0 | **0** |
| Total checks | 112 | **112** |
| Findings | 1 INFO | **1 INFO** |
| Grep BRE error | Yes (runtime) | **No** |

### D.6 — Lessons Learned

1. **Shell quoting matters for verification gates.** grep patterns with metacharacters should use single quotes to avoid BRE interpretation. Double quotes should be reserved for patterns requiring variable expansion.
2. **The validator doesn't catch runtime shell errors.** It validates structure and paths, not command syntax. A future enhancement could add a `SHELL_SYNTAX` check that validates grep patterns for common BRE pitfalls.
3. **Testing on the target platform is essential.** macOS grep (ERE-leaning) may not reproduce this bug; Ubuntu 22 grep (strict BRE) does. Cowork runs Ubuntu 22.

### D.7 — Reference Documents (v6→v7 Round)

| Document | Location | Content |
|----------|----------|---------|
| `validate_S005-P004-v7_report.json` | `_COMMUNICATION/cowork/S005-P004-v7/validation/` | Final passing report (99.1% PASS, 1 INFO) |

---

*Procedure authored by Team 110 on authority of Team 00 | shaked-wg-agent | 2026-04-13*
