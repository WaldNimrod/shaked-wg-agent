# Post-Gate Archive Procedure

**Module:** gate-workflow (Module 02)
**Version:** v1.1.0
**Date:** 2026-04-15
**Authority:** Team 00 + Team 100
**Executor:** Team 191 (Git, Archive & File Governance) or any team under Team 00 mandate
**Trigger:** L-GATE_VALIDATE PASS → WP status=COMPLETE, lod_status=LOD500_LOCKED
**Iron Rule:** #15 (Archive)

---

## Purpose

This procedure ensures that all communication artifacts for a completed Work Package are moved from active `_COMMUNICATION/` directories to `_archive/`, maintaining a clean and canonical file structure. It includes mandatory detection of misplaced artifacts (Iron Rule #12 violations).

---

## Mandatory — Post-Archive Reference Integrity (binding)

**Status:** REQUIRED for every execution of this procedure. Omission is a procedure failure.

After files move from `_COMMUNICATION/` to `_archive/<WP-ID>/`, any **unchanged** path in dependent documents is indistinguishable from **broken references** (false drift / false positives in audits). The following rules prevent that.

### M.1 — Update `roadmap.yaml` for the archived WP

For the WP row and **only** where paths pointed at moved artifacts:

1. **`spec_ref`** — must resolve to an existing repo-relative path (typically under `_archive/<WP-ID>/...` after the move).
2. **`gate_history`** — update every `verdict_path`, `report_path`, and `verdict_ref` that referenced a file that was moved. Do not leave stale `_COMMUNICATION/...` paths to archived blobs.
3. **`notes`** — if a note embeds a full path to a moved file, update the path or replace with a short pointer to `_archive/<WP-ID>/ARCHIVE_MANIFEST.md`.

### M.2 — `ARCHIVE_MANIFEST.md` redirect table (mandatory)

In `_archive/<WP-ID>/ARCHIVE_MANIFEST.md`, include a section **Path redirects** (machine- and human-readable):

```markdown
## Path redirects

| Former path (before archive) | Archived path |
|------------------------------|---------------|
| _COMMUNICATION/team_XX/...   | _archive/<WP-ID>/... |
```

Every moved artifact that was previously cited from `roadmap.yaml` or cross-team docs SHOULD appear on this table.

### M.3 — Optional stub (transition only)

Where an external link cannot be updated immediately, a **stub** file MAY be left at the former path containing only: `artifact_status: ARCHIVED`, `relocated_to:`, `archive_date:`, `wp_id:`, and one line instructing readers to open `relocated_to`. No duplicate of the full verdict body. Remove stubs when consumers are updated.

### M.4 — Audits and custom scripts

Any checker that reports “missing file” MUST treat a path as **satisfied** if `ARCHIVE_MANIFEST.md` lists a redirect for that former path or the file exists under `_archive/<WP-ID>/` with the same basename — **not** as drift.

---

## When to Execute

Execute this procedure **immediately** after a WP reaches COMPLETE status:
- L-GATE_VALIDATE PASS recorded in `roadmap.yaml`
- LOD500 as-built record locked
- `status: COMPLETE` and `lod_status: LOD500_LOCKED` set

Can be invoked via `/AOS_archive <wp-id>` or executed manually following this runbook.

---

## Procedure — Step by Step

### Step 1: Identify Target WP

```bash
# Verify WP is COMPLETE in roadmap
python3 -c "
import yaml
with open('_aos/roadmap.yaml') as f:
    rm = yaml.safe_load(f)
for wp in rm.get('work_packages', []):
    if wp['id'] == '<WP-ID>':
        print(f'Status: {wp[\"status\"]}')
        print(f'LOD: {wp.get(\"lod_status\", \"?\")}')
        break
"
```

**Gate:** WP must be `status: COMPLETE` and `lod_status: LOD500_LOCKED`. If not, STOP.

### Step 2: Scan WP Subdirectories

Locate all WP-scoped artifact directories across teams:

```bash
find _COMMUNICATION/team_* -maxdepth 1 -type d -name "<WP-ID>" 2>/dev/null
```

Record all found directories — these are the primary sources to archive.

### Step 3: Misplaced Artifact Scan (Iron Rule #12)

Scan team root directories for files that reference the WP ID but are incorrectly placed at root instead of in a WP subdirectory:

```bash
# Search for files containing the WP-ID at team root (not in subdirs)
for team_dir in _COMMUNICATION/team_*/; do
    find "$team_dir" -maxdepth 1 -type f -name "*.md" | while read f; do
        if grep -ql "<WP-ID>" "$f" 2>/dev/null; then
            echo "MISPLACED: $f"
        fi
    done
done
```

**Also check for naming patterns:**
- `ROUTING_*<WP-SHORTNAME>*` at team root
- `VERDICT_*<WP-SHORTNAME>*` at team root
- `MANDATE_*<WP-ID>*` at team root
- `HANDOFF_*<WP-ID>*` at team root

All misplaced files are included in the archive move.

### Step 4: Scan Evidence Directories

Check `_COMMUNICATION/team_50/evidence/` (and any other QA evidence locations) for evidence directories related to the completed WP:

```bash
find _COMMUNICATION/team_*/evidence/ -maxdepth 1 -type d -name "*<WP-ID>*" 2>/dev/null
```

### Step 5: Create Archive Directory

```bash
mkdir -p _archive/<WP-ID>
```

### Step 6: Move Artifacts

Move all identified files and directories to the archive:

```bash
# WP subdirectories from each team
for team_dir in _COMMUNICATION/team_*/<WP-ID>; do
    team_name=$(basename $(dirname "$team_dir"))
    mkdir -p "_archive/<WP-ID>/$team_name"
    mv "$team_dir"/* "_archive/<WP-ID>/$team_name/" 2>/dev/null
    rmdir "$team_dir" 2>/dev/null
done

# Misplaced files from Step 3
# mv each identified file to _archive/<WP-ID>/

# Evidence from Step 4
# mv each evidence directory to _archive/<WP-ID>/evidence/
```

**NEVER permanently delete.** Only move.

### Step 7: Create ARCHIVE_MANIFEST.md

Create `_archive/<WP-ID>/ARCHIVE_MANIFEST.md`:

```markdown
# Archive Manifest: <WP-ID>

**archive_date:** <YYYY-MM-DD>
**archived_by:** <Team ID> (<Team Name>)
**mandate:** <Reference to Team 00 mandate or L-GATE_VALIDATE closure>
**file_count:** <N>
**source:** `_COMMUNICATION/team_*/` (various teams)

## Archived Files

- <relative path to each file>
- ...

## Misplaced Artifacts Detected

- <file> — was at team root, should have been in WP subdir (Iron Rule #12)
- ... (or "None detected")

## Path redirects

| Former path (before archive) | Archived path |
|------------------------------|---------------|
| ... | ... |

---
*Generated by post-gate archive procedure | <YYYY-MM-DD>*
```

The **Path redirects** table is mandatory (see **Mandatory — Post-Archive Reference Integrity** above).

### Step 8: Apply Mandatory Reference Integrity + verify paths

1. Fulfill **Mandatory — Post-Archive Reference Integrity** (M.1–M.4) for this `<WP-ID>`.
2. Run a quick existence check on `spec_ref` (extend to cover `gate_history` path fields as needed):

```bash
python3 -c "
import yaml, os
with open('_aos/roadmap.yaml') as f:
    rm = yaml.safe_load(f)
for wp in rm.get('work_packages', []):
    if wp.get('id') != '<WP-ID>':
        continue
    ref = wp.get('spec_ref', '')
    if ref and not os.path.isfile(ref):
        print(f'BROKEN spec_ref: {wp[\"id\"]} → {ref}')
"
```

### Step 9: Validate

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

All checks must PASS for the repo profile. **Check 15** enforces **gate_history ordering** in `roadmap.yaml`, not archive file placement; archive compliance is this procedure + Mandatory section.

### Step 10: Commit

```bash
git add _archive/<WP-ID>/ _COMMUNICATION/ _aos/roadmap.yaml
git commit -m "archive: <WP-ID> post-gate archive (Iron Rule #15)"
```

---

## Checklist (Quick Reference)

- [ ] WP is COMPLETE + LOD500_LOCKED in roadmap.yaml
- [ ] All `_COMMUNICATION/team_*/<WP-ID>/` directories identified
- [ ] Misplaced artifact scan completed (team roots checked)
- [ ] Evidence directories checked (team_50/evidence/)
- [ ] `_archive/<WP-ID>/` created
- [ ] All artifacts moved (never deleted)
- [ ] ARCHIVE_MANIFEST.md created with file list + misplaced report + **Path redirects** table
- [ ] **Mandatory — Post-Archive Reference Integrity** satisfied (roadmap + manifest + audit rule)
- [ ] validate_aos.sh passes
- [ ] Changes committed

---

## Batch Execution (Multiple WPs)

When archiving multiple completed WPs at once (e.g., milestone closure):

1. List all COMPLETE WPs: `python3 -c "import yaml; [print(wp['id']) for wp in yaml.safe_load(open('_aos/roadmap.yaml'))['work_packages'] if wp.get('status')=='COMPLETE']"`
2. For each WP, check if `_archive/<WP-ID>/` already exists (skip if so)
3. Execute Steps 2-9 for each remaining WP
4. Single commit for all moves

---

## Cross-Project Deployment

This procedure applies to **all AOS-managed projects**. It propagates via:

1. **lean-kit snapshot** → `_aos/lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md`
2. **validate_aos.sh** — project checks (including Check 15 gate ordering); archive compliance is **this procedure**, not a single check number
3. **Team governance contracts** → `_aos/governance/team_*.md` reference archive boundaries
4. **AOS_archive command** → available in all projects via `.claude/commands/`

---

*Team 100 | Post-Gate Archive Procedure v1.1.0 | 2026-04-15 | Iron Rule #15*
