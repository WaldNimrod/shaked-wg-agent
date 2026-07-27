# AOS Domain Documentation & Archival Sweep — Version-Hygiene Procedure

**Module:** project-governance
**Version:** v1.0.0
**Date:** 2026-07-05 (fleet-run refinement addendum 2026-07-09 — case-insensitive enumeration fix (§2.1, CRITICAL),
non-WP-correspondence classification row, RULE-E v4.0.0-title-vs-v4-legacy-WP-ID disambiguation, SSoT-silent-WP +
version-marker-mismatch rows, V-5 path-ref check, `.claude`/`.cursor` P-5 escape hatch — no semver bump; filename
stays `_v1.0.0` per existing cross-reference convention, see 20+ inbound refs)
**Authority:** team_00 (mandate 2026-07-05) + team_100 (co-ratify)
**Author / centralized reviewer:** team_120 (Ambassador — DOC_CANON / drift-audit)
**Applies to:** the hub + every enabled domain in `_aos/projects.yaml`
**Executed by:** one session per domain — **ANY engine, including a weak/cheap engine**
**Origin:** post-v5-consolidation old-version drift tail (team_00 directive, 2026-07-05)

> **Why this exists.** After the long v5 cleanup, each domain still carries a *tail* of old artifacts and
> v4-era structures. Left in place they read as current → agents derive new v5 work from a v4 base → drift.
> Even small drift corrupts the v5 line. This procedure makes every domain **document its code, archive what is
> closed, and explicitly quarantine what is still open but belongs to v4** — uniformly, so no v4 structure is ever
> mistaken for a v5 template again.

---

## 0. DESIGN CONTRACT (read first — this is what makes the procedure weak-engine-safe)

This procedure is written so a **weak engine can execute it with no questions and no judgment calls.** It obeys
five invariants. If you (the executing engine) are ever unsure, you are violating an invariant — STOP and escalate.

- **INV-1 — Determinism.** Every decision is a lookup in a table with inputs you can read mechanically from a file
  (a frontmatter field, a status, a date). You never *interpret* — you *match*.
- **INV-2 — Escalate, don't guess.** If an artifact does not match exactly one row of a decision table, you do
  **NOT** choose. You put it in the report's **`ESCALATE`** list and leave it untouched. Ambiguity is team_120's to
  resolve, never yours. (This is how "no questions" is guaranteed — the unknowns become a list, not a decision.)
- **INV-3 — Non-destructive.** You only ever **move** (archive) or **tag** (quarantine). You **NEVER delete**, and
  you **NEVER edit application source or another domain's files.** Documentation edits are additive.
- **INV-4 — Idempotent + resumable.** Every step first checks "already done?" and skips if so. Re-running the whole
  procedure is safe and converges to the same state.
- **INV-5 — Report everything.** Every classification, every move, every tag, every escalation, and the
  before/after metrics go into the single standardized report (§10). No silent action.

If a command errors, a precondition is unmet, or you cannot read a required field → **STOP**, write what you have to
the report with `run_status: BLOCKED`, and return. Do not improvise a fix.

---

## 1. DEFINITIONS (fixed vocabulary)

| Term | Exact meaning |
|------|---------------|
| **v5-CURRENT** | Belongs to the active AOS v5 line (version marker = 5.x; milestone `AOS-V5-*` or a v5 spoke sprint). Keep in place. |
| **v4-LEGACY** | Belongs to AOS v4 / v3 / pre-v5 structure (IDs like `AOS-V4-*`, `AOS-V4.5-WP-*`, `agents_os_v3`, version 3.x/4.x) **and is still OPEN** (not archived). Must be QUARANTINE-tagged. |
| **CLOSED artifact** | An artifact of a WP whose `status: COMPLETE` and `lod_status: LOD500_LOCKED`. → ARCHIVE. |
| **ARCHIVE** | Move the artifact into `_archive/<WP-ID>/` per `POST_GATE_ARCHIVE_PROCEDURE.md` (never delete). |
| **QUARANTINE** | Stamp an OPEN v4-legacy artifact with the `V4_LEGACY_QUARANTINE` marker (§8) so it is flagged "not a v5 template, not a base for continuation." Leaves the file in place; adds a marker + index entry. |
| **KEEP** | Leave a v5-current, still-relevant WP or artifact exactly as is. |
| **KEEP-IN-PLACE** | Same no-op action as KEEP, used specifically for a **standing non-WP correspondence file** judged still-active (§5) — kept distinct in wording only so a report reader can tell "active WP" from "active loose correspondence" apart at a glance. |
| **ESCALATE** | Cannot be classified deterministically → list in the report for team_120. No action taken on the file. |

---

## 2. PRECONDITIONS (STOP gates — verify ALL before Phase 0)

Run each; if any fails, STOP and report `run_status: BLOCKED` with the failing check.

```bash
# P-1: you are in the domain's canonical local_path (from the hub's _aos/projects.yaml). Confirm CWD.
pwd
# P-2: git tree is readable + you are on the domain's canonical branch (record it; do not switch).
git rev-parse --abbrev-ref HEAD && git rev-parse HEAD
# P-3: concurrency isolation — if another session may share this tree, you MUST be in a git worktree (ADR052 W2).
#      If unsure, STOP: creating clutter under a concurrent writer risks clobber.
# P-4: the domain declares a version marker (Phase 0 reads it). If NO version marker exists at all → STOP + ESCALATE
#      (a domain with no version identity cannot be swept safely).
# P-5: no uncommitted changes you did not make. `git status --porcelain` — if dirty with foreign edits → STOP.
git status --porcelain | head
```

**Hard STOP conditions (never proceed):** a dirty tree with edits you did not author; a detached/unknown branch; no
version marker; a concurrent lock/worktree ambiguity. In every case: report `BLOCKED`, return, do nothing else.

**P-5 exception — `.claude`/`.cursor` escape hatch.** Dirtiness confined to `.claude/` or `.cursor/` (session/tool
working state — worktree bookkeeping, local settings caches) does **not** count as a "foreign edit" for P-5. This
sweep is a read-only classification pass with respect to those dirs; do not STOP on them alone. Any dirty file
**outside** `.claude/`/`.cursor/` that you did not author still triggers the hard STOP.

## 2.1 CASE-INSENSITIVITY (CRITICAL — read before running any enumerate command)

**Finding (smallfarmsagents domain sweep, 2026-07-09):** every `find`/`ls`/glob in this procedure that matches team
directories under `_COMMUNICATION/` (e.g. `_COMMUNICATION/team_*`) is a **shell glob**, and shell globs are
**case-sensitive** on this stack. smallfarmsagents' uppercase `TEAM_NN` directories were **silently skipped** by
every such command — no error, just an undercount (~5.5x file undercount; likely why its original ~34-file estimate
was wrong). Reported in `COMPLETION_team_60_PHASEB-LAND-AND-ACTIVE-DOMAINS_2026-07-09_v1.0.0.md`.

**Fix — use case-insensitive matching for every team/WP directory enumeration:**
- Prefer `find <dir> -mindepth N -type f -ipath '*/team_*/*' ...` (BSD find on macOS and GNU find both support
  `-ipath`/`-iname`) over a bare shell glob like `_COMMUNICATION/team_*`.
- Where a `-name`/pattern match is used instead of a path glob, use `-iname` or an explicit bracket-class pattern
  (`[Tt][Ee][Aa][Mm]_*`) — never a bare-case literal.
- This applies to **every** enumerate/count command in Phase 0 (§3) and Phase 2 (§5) below — they have been updated
  accordingly. If you add a new enumerate command, it MUST follow this same case-insensitive form.

**⚠ Re-sweep notice:** any domain swept **before this fix landed (2026-07-09)** with mixed-case team directories was
**UNDER-counted** — its baseline metrics (§3), classification counts (§5), and archive/quarantine actions (§6/§7) may
have silently missed every artifact under an uppercase `TEAM_NN` dir. Any such domain's prior `SWEEP_REPORT_*` is
**not reliable** and that domain needs a **re-sweep** with the case-insensitive commands above before its report can
be trusted. team_120 tracks this in R-1/R-2 (§11).

---

## 3. PHASE 0 — Baseline snapshot (record, do not change)

Record these into the report header (§10). This is the before-state and the domain's version identity.

```bash
DOMAIN_ID="<from projects.yaml>"; DATE="$(date +%F)"; SHA="$(git rev-parse --short HEAD)"
# Version markers (read whichever exist; record the literal values):
[ -f _aos/AOS_GOVERNANCE_VERSION.yaml ] && cat _aos/AOS_GOVERNANCE_VERSION.yaml
[ -f _aos/lean-kit/LEAN_KIT_VERSION.md ] && head -5 _aos/lean-kit/LEAN_KIT_VERSION.md
[ -f _aos/roadmap.yaml ] && grep -E 'active_milestone|version' _aos/roadmap.yaml | head
# Baseline counts (before-metrics):
# NOTE: -ipath (case-insensitive) is required here — see §2.1. A bare `_COMMUNICATION/team_*` shell
# glob silently misses uppercase TEAM_NN directories and undercounts the domain.
echo "un-archived _COMMUNICATION files: $(find _COMMUNICATION -mindepth 2 -type f -ipath '*/team_*/*' -not -path '*/_archive/*' 2>/dev/null | wc -l | tr -d ' ')"
echo "open WPs: $(find _aos/work_packages -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
echo "_archive WP dirs: $(find _archive -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
```

**Success criterion:** all baseline values recorded. If the version marker literal is **4.x / 3.x / blank** → note
`domain_version_flag: V4_OR_MISSING` in the report (team_120 tracks these as top-priority domains).

---

## 4. PHASE 1 — Code documentation completeness (deterministic checks only)

**Goal:** the domain's code is *documented* to the AOS standard **before** its artifacts are archived — so the
archive captures a documented state, not an undocumented one. You do **not** write prose docs by judgment; you bring
the **required documentation artifacts** to a present + consistent state, verified by checks.

Run each check. Each is PASS / GAP. Record the result; for each GAP, take the listed additive action **only if it is
mechanical**, else ESCALATE.

| # | Documentation check | How to verify (mechanical) | GAP action |
|---|---------------------|----------------------------|-----------|
| D-1 | **DOC_CANON present + well-formed** | `python3 -m core.modules.management.doc_canon --check` → `CHECK59 OK` (hub); on a spoke with no `core/`, this SKIPs — record `N/A-spoke` | If `CHECK59 WARN` → ESCALATE (do not fabricate DOC_CANON entries) |
| D-2 | **Every completed WP has a locked as-built record** | For each `status: COMPLETE` WP, confirm a `LOD500` / as-built doc exists in its WP dir | If missing → ESCALATE (as-built authoring is a judgment task, not weak-engine) |
| D-3 | **Module / directory indexes match reality** | Where an `INDEX.md` / `MODULE.md` exists, confirm it references files that still exist (no dangling) | Dangling reference to a MOVED file whose `_archive` redirect exists → mechanical fix (repoint); otherwise ESCALATE |
| D-4 | **Code-standards citation present where required** | `validate_aos.sh` Check 26 (LOD400 bare-CS-cite scan) advisory result | Record only; advisory |

**Success criterion for Phase 1:** D-1..D-4 each PASS or `N/A-spoke` or listed in ESCALATE. **No document content is
invented.** Phase 1 never blocks the sweep on its own; unmet doc items become ESCALATE rows.

---

## 5. PHASE 2 — Deterministic artifact classification (the core decision)

Enumerate every candidate artifact, then classify each by the table below. **Read the inputs mechanically; match
exactly one row; if none match → ESCALATE.**

### 5.0 — Five disambiguation rules you MUST apply first (they pre-resolve the traps a weak engine hits)

These are absolute. They override any instinct to read meaning from a filename or body text.

- **RULE-A — Classify by WP-ID + status FIELDS, never by prose.** The deciding inputs are the **WP-ID pattern** and
  the structured `status` / `lod_status` / `milestone_ref` fields. A file that merely *mentions* "v4" / `V4_GAP_MATRIX`
  in its name or body is **NOT** thereby v4-legacy. Prose mentions never trigger QUARANTINE. Only an artifact whose
  **owning WP-ID** is `AOS-V4*` (etc.) is v4-legacy.
- **RULE-B — Governance version ≠ WP-ID scheme.** A spoke's WP IDs look like `S###-P###-WP###` — these are the
  **v5 framework** (they use the v5 lean-kit + v5 gates). They are **NOT** v4. "Am I v4 or v5?" is answered ONLY by
  `lean_kit_version` (5.x/3.4.0-line = v5) + profile + lean-kit module refs — never by the local WP numbering.
- **RULE-C — Read WP status from the right SSoT (ADR034).** For **hub** WPs (`AOS-V*` IDs): the DB is SSoT when
  online — read status via the v5 ops API, not a possibly-stale `roadmap.yaml`. For **spoke** WPs
  (`S###-P###-WP###`): `_aos/roadmap.yaml` is the file-SSoT (ADR034 R9). If the correct source is unreachable →
  ESCALATE that WP (do not read the wrong source).
- **RULE-D — "Retired / deprecated non-WP artifact with no active reader" = ARCHIVE, not quarantine.** A loose folder
  like `_aos/context/_retired_v4/` (already marked deprecated, superseded, no current function) is a **CLOSED
  artifact** → move it to `_archive/` (§6). QUARANTINE (§7) is only for artifacts that are **still OPEN / still
  referenced** but belong to v4.
- **RULE-E — A "v4.0.0" release/charter **name** is not a v4-legacy **WP-ID**.** Some canonical, currently-binding v5
  documents carry a literal `v4.0.0` (or similar) string in their own **title/filename** because that was the release
  that *introduced* the content (e.g. `ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL_v1.0.0.md` — the Track Model it
  defines is still the live v5 classifier). That is a **proper-noun release tag**, not an artifact-owning WP-ID, and
  is **KEEP**, full stop — it is never quarantined by RULE-A's "prose mention" logic either. Contrast this with an
  artifact whose **owning WP-ID itself** matches `AOS-V4-*` / `AOS-V4.5-WP-*` (the ID field, not a title string) —
  that one IS v4-legacy and follows the normal QUARANTINE-V4 row. Deciding input: is the `v4.0.0`-shaped token sitting
  in a **document title** (KEEP) or in the **WP-ID field** (QUARANTINE-V4)? Never guess from vibes — read the field.

**Enumerate:**
```bash
# A) Open WP dirs
find _aos/work_packages -maxdepth 1 -type d
# B) team artifacts not yet archived
# NOTE: -ipath + -iname (case-insensitive) — see §2.1. Do NOT use a bare `_COMMUNICATION/team_*` glob.
find _COMMUNICATION -mindepth 2 -type f -ipath '*/team_*/*' -not -path '*/_archive/*' -iname '*.md'
```

**Classification decision table** (inputs are read from frontmatter / the WP `metadata.yaml` / the ID string):

| If the artifact… | Classify as | Then (phase) |
|------------------|-------------|--------------|
| is a WP with `status` ∈ {`COMPLETE`, `CLOSED`, `COMPLETE_SUPERSEDED`, `SUPERSEDED`} (any terminal "done" status) | **ARCHIVE** | Phase 3 |
| is a WP with `status: ARCHIVED` **or** already lives under `_archive/` | **KEEP** (already archived) | — (skip) |
| has a `status` that is not a valid status enum value (e.g. a **lod value like `LOD500_LOCKED` sitting in the status field**, or an unknown token) | **ESCALATE** (subtype `MALFORMED-STATUS`) | report only — data-quality fix |
| has an ID / `milestone_ref` matching **v5** (`AOS-V5-*`, or a spoke sprint on the current v5 line) **AND** is OPEN | **KEEP** (v5-current) | — |
| has an ID / version matching **v4/v3** (`AOS-V4*`, `AOS-V4.5-WP-*`, `agents_os_v3`, version `3.x`/`4.x`) **AND** is OPEN (not COMPLETE/archived) | **QUARANTINE-V4** | Phase 4 |
| is already stamped `aos_lifecycle: V4_LEGACY_QUARANTINE` | **KEEP** (already quarantined) | — (skip; idempotent) |
| is a **retired/deprecated non-WP artifact with no active reader** (RULE-D — e.g. a `_retired_v4/` template folder, a legacy milestone inventory JSON) | **ARCHIVE** to `_archive/<descriptive-legacy-id>/` | Phase 3 (variant §6.1) |
| is a WP with `status` ∈ {`DRAFT`, `PLANNED`, `DEFERRED`} **AND** `milestone_ref` points at a **CLOSED milestone** (not the domain's active milestone) — a **STALE-MILESTONE-WP** | **ESCALATE** (subtype `STALE-MILESTONE-WP`) | report only — team_120 disposition |
| is real WP-shaped work (has a WP directory / LOD artifact chain, an assigned builder, etc.) but has **no matching row** in `roadmap.yaml` (file-SSoT) or the DB (hub SSoT) — a **SSoT-silent WP** | **ESCALATE** (subtype `SSOT-SILENT-WP`) | report only — team_120 arranges a roadmap/DB backfill; never invent the missing row yourself |
| is a **standing non-WP `_COMMUNICATION` correspondence file** — no owning WP-ID in filename or frontmatter (e.g. `MSG-*`, `HANDOFF_*`, `STATUS_*`, `ROUTING_*`, `RATIFICATION_*`, `GCR_*`, `RULING_*`, `PROPOSAL_*`, `DRIFT_AUDIT_*`) **AND** nothing marks it superseded/stale | **KEEP-IN-PLACE** (active correspondence — not a sweep target) | — |
| is the same non-WP correspondence shape **but** you cannot determine active-vs-superseded (conflicting signals — e.g. a newer same-topic file exists, or the body claims "superseded" with no formal marker) | **ESCALATE** (subtype `NON-WP-CORRESPONDENCE-AMBIGUOUS`) | report only — team_120 disposition |
| has a `version:` field (frontmatter or body) that does **not match** the version embedded in its own filename (e.g. filename `..._v1.0.0.md` but frontmatter says `version: 1.1.0`) | **ESCALATE** (subtype `VERSION-MARKER-MISMATCH`) | report only — do not guess which is authoritative |
| is a loose non-WP note/report **dated older than the domain's current-milestone open date** with no version tag | **ESCALATE** | report only |
| matches **none** of the above, or you cannot read the deciding field | **ESCALATE** | report only |

> **Note — non-WP correspondence (fleet refinement 2026-07-09).** The microgreens domain sweep found 135
> un-archived files of which **124** were loose, non-WP `_COMMUNICATION` correspondence with no classification-table
> row to match — every one landed in ESCALATE for lack of a row, not because any were actually ambiguous. The
> KEEP-IN-PLACE / ESCALATE rows above close that gap: a standing correspondence file (MSG/HANDOFF/STATUS/etc., no
> owning WP-ID) is KEEP-IN-PLACE by default, and only escalates on a genuine active-vs-superseded conflict.
> Reported in `COMPLETION_team_60_PHASEB-LAND-AND-ACTIVE-DOMAINS_2026-07-09_v1.0.0.md`.

> **Note — retroactive archival (pilot refinement 2026-07-05).** For an **already-CLOSED** WP, archival does NOT
> re-require `LOD500_LOCKED` — the LOD granularity is informational once `status` is terminal. The `LOD500_LOCKED`
> precondition in `POST_GATE_ARCHIVE_PROCEDURE` governs a *fresh* close, not the retroactive archival of a WP that
> was closed under an earlier convention. **STALE-MILESTONE-WP** is a distinct drift class the hub pilot surfaced:
> a `DRAFT`/`PLANNED` WP whose milestone is already closed reads as open v5 work but is effectively abandoned —
> team_120 rules each (archive-as-abandoned / re-home to the active milestone / keep with justification). It is
> **never** auto-archived (a DRAFT is not CLOSED) and **never** guessed.

**Success criterion:** every enumerated artifact carries exactly one label (`ARCHIVE` / `KEEP` / `KEEP-IN-PLACE` /
`QUARANTINE-V4` / `ESCALATE`). The counts per label go into the report. **A weak engine that is unsure chose
`ESCALATE` — that is correct behavior, not failure.**

---

## 6. PHASE 3 — Archive execution (for every `ARCHIVE`-labelled WP)

Delegate to the existing canon — **do not reinvent archiving:**
`lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md` (v1.2.0), or the command `/AOS_archive <WP-ID>`.

For each `ARCHIVE` WP-ID:
```bash
# Preferred (thin, canonical):
# /AOS_archive <WP-ID>
# — or follow POST_GATE_ARCHIVE_PROCEDURE steps 1-10 exactly (move, ARCHIVE_MANIFEST.md with Path-redirects, verify).
```
**Success criterion (per WP):** `_archive/<WP-ID>/ARCHIVE_MANIFEST.md` exists with a Path-redirects table; the WP's
`_COMMUNICATION/team_*/<WP-ID>/` sources are moved (not deleted); `roadmap.yaml` refs updated;
`validate_aos.sh` still passes. If the archive command errors → STOP that WP, record it under ESCALATE, continue
with the others (one bad WP never aborts the sweep). **Never delete on failure.**

### 6.1 — Variant: archiving a retired non-WP artifact (RULE-D items)
For a deprecated folder/file that is not a WP (no WP-ID, so `/AOS_archive` does not apply), archive by a plain
`git mv` into a descriptively-named `_archive/` dir + a manifest — never delete:
```bash
LEG="_archive/<DESCRIPTIVE-LEGACY-ID>_$(date +%F)"      # e.g. _archive/RETIRED_V4_ACTIVATION_TEMPLATES_2026-07-05
mkdir -p "$LEG"
git mv <retired-path> "$LEG"/                            # move, do not copy+delete
# write $LEG/ARCHIVE_MANIFEST.md: source path, date, reason ("retired v4, no active reader"), file count.
```
**Success criterion:** the retired artifact now lives only under `_archive/`; a manifest records the move; nothing
deleted. List each such move in the report's Phase-3 section (mark `kind: non-wp-legacy`).

---

## 7. PHASE 4 — V4-legacy quarantine tagging (for every `QUARANTINE-V4` artifact)

Apply the `V4_LEGACY_QUARANTINE` marker (full schema: `V4_LEGACY_QUARANTINE_CONVENTION_v1.0.0.md`). Two mechanical
actions per artifact — both additive, non-destructive:

**7.1 — Stamp the artifact frontmatter** (prepend if missing; skip if already present — INV-4):
```yaml
aos_lifecycle: V4_LEGACY_QUARANTINE
not_a_template: true
quarantined_by: <your team_id>
quarantine_date: <YYYY-MM-DD>
quarantine_reason: "v4-legacy structure, still open — NOT a v5 base/template; do not derive new work from it"
successor_ref: <path to the v5 equivalent, or "none-yet">
```
And insert a one-line banner at the very top of the body:
`> ⚠️ **V4-LEGACY (QUARANTINED $DATE)** — belongs to AOS v4; NOT a v5 template or base. See _aos/V4_QUARANTINE_INDEX.md.`

**7.2 — Append one row to the domain quarantine index** `_aos/V4_QUARANTINE_INDEX.md` (create if absent):
```markdown
| <artifact path> | <WP/ID or "loose"> | <quarantine_date> | <reason short> | <successor_ref> |
```

**Success criterion:** every `QUARANTINE-V4` artifact has the frontmatter marker + banner **and** an index row.
Re-running finds them already stamped and skips (idempotent). If an artifact's format cannot take frontmatter (e.g.
binary) → ESCALATE.

---

## 8. PHASE 5 — Anti-drift verification (prove the tail is gone)

After Phases 3-4, verify the domain no longer presents v4 structure as current:

```bash
# V-1: no OPEN, un-quarantined v4 identifier remains outside _archive/ and outside the quarantine index.
grep -rIl 'AOS-V4\|AOS_V4\|agents_os_v3\|AOS-V4.5-WP' . \
  | grep -v -E '/_archive/|/\.git/|V4_QUARANTINE_INDEX.md' | head
#    Expected: every hit is either (a) inside a dated/archived artifact, or (b) already stamped V4_LEGACY_QUARANTINE.
#    Any UN-stamped, non-archived, active hit → add to ESCALATE.
# V-2: version markers all read v5 (from Phase 0). If any still 4.x/blank → ESCALATE (domain-version remediation).
# V-3: validate_aos passes for the domain profile.
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh . | tail -20
# V-4: DOC_CANON still OK (hub) / N-A (spoke).
# V-5: every WP row's path-like field resolves. For each WP in roadmap.yaml, if it carries `spec_ref`,
#      `decision_record`, or a `path`/`local_path` field, confirm the referenced file/dir still exists
#      (post-move, these should point at _archive/<WP-ID>/... per M.1 of POST_GATE_ARCHIVE_PROCEDURE).
python3 -c "
import yaml, os
rm = yaml.safe_load(open('_aos/roadmap.yaml'))
for wp in rm.get('work_packages', []):
    for field in ('spec_ref', 'decision_record', 'path', 'local_path'):
        ref = wp.get(field)
        if ref and not os.path.exists(ref):
            print(f'V-5 BROKEN PATH: {wp[\"id\"]}.{field} -> {ref}')
"
```

**Success criterion:** V-1 shows zero un-stamped active v4 hits; V-2 markers are v5 or flagged; V-3 `0 FAIL`; V-4
OK/N-A; V-5 prints nothing (every WP row's path-like field resolves). Any residual → ESCALATE row (subtype
`BROKEN-PATH-REF` for V-5) — not a silent pass.

---

## 9. PHASE 6 — (execution complete) → produce the standardized report (§10) and STOP.

Do not commit/push unless the domain's git policy owner (team_60 / the domain's git lane) has authorized it in this
session. Default: leave the changes staged in the working tree and let the report drive review. **The report is the
deliverable.**

---

## 10. STANDARDIZED DOMAIN REPORT (fixed template — fill every field)

Write to `_COMMUNICATION/team_120/SWEEP_REPORT_<DOMAIN_ID>_<DATE>_v1.0.0.md` (in the domain repo) **and** deliver a
copy/notice to team_120 (DB mail `kind=note`, or file-channel if the bus is down). Fill EVERY field; use `0` / `none`
explicitly, never blank.

```markdown
---
id: SWEEP_REPORT_<DOMAIN_ID>_<DATE>_v1.0.0
type: DOMAIN_DOC_ARCHIVE_SWEEP_REPORT
from: <team_id>@<DOMAIN_ID>
to: team_120
date: <YYYY-MM-DD>
procedure: DOMAIN_DOC_ARCHIVE_SWEEP_PROCEDURE_v1.0.0
run_status: COMPLETE | BLOCKED | PARTIAL
---
## Baseline (Phase 0)
domain_id: … | branch: … | sha: … | domain_version_flag: V5 | V4_OR_MISSING
version_markers: { governance: "…", lean_kit: "…", active_milestone: "…" }
before: { unarchived_comm_files: N, open_wps: N, archive_dirs: N }
## Phase 1 — documentation
D-1 DOC_CANON: PASS|WARN|N/A-spoke  · D-2 asbuilt: PASS|gaps=N  · D-3 indexes: PASS|fixed=N  · D-4 CS-cite: advisory=…
## Phase 2 — classification counts
ARCHIVE: N · KEEP(v5): N · KEEP-IN-PLACE(non-WP correspondence): N · QUARANTINE-V4: N · ESCALATE: N
## Phase 3 — archive
archived_wps: [ <WP-ID> … ]  · manifests_written: N  · archive_failures(->ESCALATE): [ … ]
## Phase 4 — quarantine
quarantined: [ <path> … ]  · index_file: _aos/V4_QUARANTINE_INDEX.md (rows: N)
## Phase 5 — anti-drift verify
V-1 residual_v4_active_hits: N (list if >0) · V-2 markers_v5: yes|no · V-3 validate: 0 FAIL? yes|no · V-4 doc_canon: OK|N-A · V-5 broken_path_refs: N (list if >0)
## ESCALATE (team_120 decides — DO NOT guess)
- <path> — <why it could not be classified/actioned>
## After (metrics)
after: { unarchived_comm_files: N, open_wps: N, archive_dirs: N, quarantined: N }
delta: { archived: N, quarantined: N, comm_files_cleared: N }
```

**Report success criterion:** `run_status` set; every section filled; the ESCALATE list is exhaustive (every
non-deterministic case is here). A report with empty required fields is itself a procedure failure.

---

## 11. team_120 CENTRALIZED REVIEW (systemic — run after all domain reports land)

team_120 aggregates every `SWEEP_REPORT_*` and assesses the fleet, not just each domain:

- **R-1 Coverage:** every enabled domain in `projects.yaml` returned a report? Missing domain → chase (BLOCKED count).
- **R-2 Drift-tail closed:** sum `V-1 residual_v4_active_hits` across the fleet → target **0**. Any domain > 0 → a
  remediation follow-up (that domain still leaks v4 as current).
- **R-3 Version identity:** all `domain_version_flag` = V5? Any `V4_OR_MISSING` → top-priority version-marker fix.
- **R-4 ESCALATE adjudication:** team_120 rules each escalated artifact → ARCHIVE / QUARANTINE / KEEP, and (if a
  pattern repeats across domains) proposes a new classification-table row so next run auto-handles it (the procedure
  gets smarter; the weak engine keeps escalating only true novelties).
- **R-5 Quarantine ledger:** consolidate all `_aos/V4_QUARANTINE_INDEX.md` into a fleet index; track that each
  quarantined item has (or gets) a `successor_ref` so v4 legacy is retired over time, not parked forever.
- **R-6 Systemic finding:** does the tail cluster by cause (un-archived closures? un-tagged v4 templates? stale
  version markers?) → one systemic fix > many local ones. Feed to team_00/team_100.

**team_120 output:** a single `FLEET_VERSION_HYGIENE_REVIEW_<DATE>.md` → team_00 + team_100: coverage, drift-tail
number, escalation rulings, systemic recommendation, and a go/no-go on "fleet is v4-drift-clean."

---

## 12. IDEMPOTENCY & RESUME
Re-running is safe: archived WPs are skipped (manifest exists), quarantined artifacts are skipped (marker present),
KEEP/v5 untouched. A `BLOCKED` run resumes from the failing precondition after it is cleared. Nothing is ever
deleted, so no re-run can lose data.

## 13. APPENDIX — command cheatsheet (copy-paste order)
`Preconditions §2` → `Phase 0 §3` → `Phase 1 §4` → `Phase 2 §5 (classify)` → `Phase 3 §6 (/AOS_archive per ARCHIVE)`
→ `Phase 4 §7 (stamp + index per QUARANTINE-V4)` → `Phase 5 §8 (verify)` → `Phase 6 §10 (report → team_120)` → STOP.

## 14. APPENDIX — worked examples (grounded in the 2026-07-05 hub survey) + scale note

**The tail is mostly UN-ARCHIVED VOLUME, not version-marker regression.** The 2026-07-05 survey found every enabled
domain already on the v5 line (`lean_kit_version 3.4.0`) — no active v4 config, no v4 version markers. The tail is:
(a) a large **un-archived backlog** (hub ≈1734, TikTrack ≈3918 files under `_COMMUNICATION/team_*/` never archived),
and (b) a few **specific v4 legacy items**. So Phase 3 (archive backlog) is the heavy lifter; v4 handling is small.

**Worked classifications (apply the table + rules; these are the real hub items):**

| Real artifact | Reads as | Applies | → |
|---------------|----------|---------|---|
| `_aos/context/_retired_v4/` (3 `ACTIVATION_*.md`, marked DEPRECATED 2026-06-12, superseded) | retired non-WP, no active reader | RULE-D | **ARCHIVE** → `_archive/RETIRED_V4_ACTIVATION_TEMPLATES_2026-07-05/` (§6.1) |
| `ws1_inventory.json` (44 `AOS-V4.x` WP IDs, all DB-CLOSED — a legacy milestone inventory) | retired non-WP inventory | RULE-D | **ARCHIVE** → `_archive/AOS-V4-MILESTONE-INVENTORY_2026-07-05/` (§6.1) |
| a completed WP dir `AOS-V5-M9-P1-WP7/` (`status: COMPLETE`, `lod_status: LOD500_LOCKED`) | closed v5 WP | table row 1 | **ARCHIVE** via `/AOS_archive` (§6) |
| `pytest.ini` comment mentioning `AOS-V4.5-WP-CI-LOCAL-MINIMAL` | prose mention only, active config file | RULE-A | **KEEP** (prose ≠ v4-legacy) |
| a methodology doc citing "v4.0.0" as historical decision context (e.g. ADR044 era) | historical citation in a v5-current doc | RULE-A | **KEEP** (optionally team_120 adds a "historical ref" header — not the engine's call) |
| an OPEN spoke WP `S008-P024-WP002` on TikTrack (`lean_kit_version 3.4.0`) | spoke v5-framework WP | RULE-B | **KEEP (v5-current)** — S-scheme is NOT v4 |
| a genuinely OPEN artifact whose owning WP-ID is `AOS-V4-*` (rare) | open v4-legacy | table QUARANTINE row | **QUARANTINE-V4** (§7) |

**Scale note (weak-engine ergonomics).** With ~1.7k–3.9k files, do Phase 3 in **batches by WP-ID** (archive one WP's
full artifact set per `/AOS_archive` call; loop the COMPLETE WP list). Do not attempt a single mega-move. The report
records per-WP results; a failure on one WP → ESCALATE that WP and continue. Commit boundaries follow the domain's
git policy (team_60 / the domain git lane) — the sweep itself does not push.

---
*team_120 (author/custodian) + team_00 (mandate) | Domain Documentation & Archival Sweep v1.0.0 | 2026-07-05, refinement addendum 2026-07-09 | anti-v4-drift*
