# WP ID Standard — Work Package Naming, Hierarchy & Registration

> **Authority:** AOS Directory Canon v1.0.0 + this document
> **Status:** CANONICAL — binding for all AOS-managed projects
> **Scope:** All WP IDs, directory structures, and roadmap.yaml entries

---

## 1. The WP Identifier — Structure & Meaning

Every Work Package has a canonical three-segment identifier:

```
S[stage] - P[program] - WP[number]
  │            │            │
  │            │            └── WP number: 001, 002, 003, ...
  │            │                Sequential within the program.
  │            │                Frozen on assignment. Never reused.
  │            │
  │            └── Program number: 001, 002, 003, ...
  │                Groups related WPs within a stage.
  │                Represents a coherent delivery stream or team cohort.
  │                Sequential within the stage. Frozen on assignment.
  │
  └── Stage number: 001, 002, 003, ... (or S003, S004, ...)
      A major product milestone. Corresponds to MILESTONE_MAP.md entries.
      Frozen on project creation. Never renumbered.
```

**Example:** `S003-P003-WP005`
- Stage 3: GATE-A Essential Data Layer milestone
- Program 3: Frontend implementation program within Stage 3
- WP 5: Fifth work package in Program 3 (Settings pages: D39, D40, D41)

---

## 2. The Three Levels — Definitions & Artifacts

### Level 1 — Stage

**What it is:** A major product milestone. Represents a coherent phase of product development that can be shipped, validated, or demonstrated independently.

**Corresponds to:** An entry in `_aos/MILESTONE_MAP.md`.

**Directory:** `_aos/work_packages/S[N]/`

**Canonical artifact at this level:**

| File | Name | LOD | Purpose |
|------|------|-----|---------|
| `LOD300_milestone.md` | Milestone Scope Document | LOD300 | Full scope of the stage: all WPs, user journeys, business rules, data model, API surface, acceptance definition. This is the planning document that pre-dates per-WP LOD400s. |

**Rules:**
- Every stage with ≥1 WP should have a `LOD300_milestone.md` (or the scope must appear at program or WP level)
- The `LOD300_milestone.md` is authored by the architecture team (Team 100/110) before WPs are split
- It is a planning artifact — does NOT substitute for per-WP LOD400 at L-GATE_SPEC
- The file MUST be named `LOD300_milestone.md` (not `LOD300_spec.md`) to be distinguishable from per-WP LODs

---

### Level 2 — Program

**What it is:** A coherent delivery stream within a stage. Groups WPs that share a team, technology track, or functional domain. A stage can have 1..N programs.

**Program number allocation:**
- P001 = first program in the stage (default for single-program stages)
- P002, P003, ... = additional programs, numbered by creation order
- Program numbers are project-scoped (not global across stages)
- In practice: `S003-P003` means "the third program created within Stage 3"

**Directory:** No dedicated directory. Programs are identified via the WP ID prefix only.

**Artifacts at program level:** Optional. If a program needs a concept document (Track B), place it in the stage directory:
- `_aos/work_packages/S[N]/LOD200_P[M]_concept.md` (only if needed — not required)

**Rules:**
- If a stage has only one program, use P001
- Program numbers are assigned when the first WP of that program is identified
- Once assigned, a program number is frozen — never reassigned

---

### Level 3 — Work Package (WP)

**What it is:** The atomic execution unit of AOS. One WP = one builder, one validator, one gate sequence, one LOD chain.

**Directory:** `_aos/work_packages/S[N]-P[M]-WP[K]/` (flat — the full WP ID is the directory name)

**Canonical artifacts at this level:**

| File | LOD | Gate | Required? |
|------|-----|------|-----------|
| `LOD100_scope.md` | LOD100 | L-GATE_ELIGIBILITY | YES — before L-GATE_ELIGIBILITY |
| `LOD200_concept.md` | LOD200 | L-GATE_CONCEPT (Track B only) | Track B only |
| `LOD400_spec.md` | LOD400 | L-GATE_SPEC | YES — before L-GATE_SPEC |
| `LOD500_asbuilt.md` | LOD500 | L-GATE_BUILD | YES — before L-GATE_BUILD |

**Rules:**
- WP directory is created when LOD100 is authored (may be deferred to L-GATE_ELIGIBILITY)
- LOD400 MUST exist and be referenced in `spec_ref` before L-GATE_SPEC can be declared
- If the LOD300_milestone.md is sufficient scope, LOD100 may point to it via `spec_ref`
- LOD500 documents what was actually built — never edited retroactively

---

## 3. Registration in roadmap.yaml

**Registration rule:** Every WP MUST be registered in `_aos/roadmap.yaml` no later than **L-GATE_SPEC** (spec gate). Best practice: register as PLANNED at first identification.

**Minimal valid entry (before LOD400 exists — WP is at pre-spec stage):**
```yaml
- id: "S003-P003-WP005"
  label: "Settings pages — Preferences, System Management, Admin (D39, D40, D41)"
  status: IN_PROGRESS
  track: A
  current_lean_gate: L-GATE_SPEC             # ← pre-spec stage; LOD400 needed before this gate
  lod_status: LOD300                       # milestone LOD300 is the best available spec
  assigned_builder: tiktrack_build
  assigned_validator: tiktrack_val
  created_at: "2026-04-11"
  milestone_ref: "S003"
  spec_ref: "_aos/work_packages/S003/LOD300_milestone.md"  # → per-WP LOD400 when authored
  gate_history: []
  notes: "Executing via cowork package. Canonical ID assigned 2026-04-11. LOD400 to be authored before L-GATE_SPEC."
```

> **Gate/LOD rule:** `lod_status: LOD300` means the WP has only a milestone-level scope. The next required gate is therefore `L-GATE_SPEC` (spec gate). Setting `current_lean_gate: L-GATE_BUILD` with `lod_status: LOD300` would be a contradiction — L-GATE_BUILD requires LOD400 to already exist.

**At L-GATE_SPEC, spec_ref MUST be updated to the per-WP LOD400:**
```yaml
  spec_ref: "_aos/work_packages/S003-P003-WP005/LOD400_spec.md"
```

**ID format validation regex:** `^S\d{3,}-P\d{3,}-WP\d{3,}$`

---

## 4. Directory Structure — Full Example

```
_aos/work_packages/
  S003/                                     ← Stage 3 directory
    LOD300_milestone.md                     ← Milestone scope (planning doc, LOD300)
  S003-P003-WP001/                          ← WP directory (ID = directory name)
    LOD100_scope.md                         ← Scope statement
    LOD400_spec.md                          ← Executable spec (required at L-GATE_SPEC)
    LOD500_asbuilt.md                       ← As-built record (required at L-GATE_BUILD)
  S003-P003-WP002/
    LOD400_spec.md
  S003-P003-WP005/                          ← Currently IN_PROGRESS
    LOD400_spec.md
  S004/
    LOD300_milestone.md
  S004-P001-WP001/
    LOD400_spec.md
    LOD500_asbuilt.md
```

---

## 5. LOD Chain at Each Level — Summary Table

| LOD | Level | File | Gate | Notes |
|-----|-------|------|------|-------|
| LOD100 | WP | `WP-ID/LOD100_scope.md` | L-GATE_ELIGIBILITY | What + why, team assignment |
| LOD200 | WP | `WP-ID/LOD200_concept.md` | L-GATE_CONCEPT (Track B) | How (architecture) |
| LOD300 | **Stage** | `S[N]/LOD300_milestone.md` | Pre-planning | Milestone scope covering all WPs |
| LOD400 | WP | `WP-ID/LOD400_spec.md` | L-GATE_SPEC | Acceptance criteria, interfaces |
| LOD500 | WP | `WP-ID/LOD500_asbuilt.md` | L-GATE_BUILD | What was actually delivered |

**Key rule:** LOD300_milestone.md is a STAGE-level planning artifact. It does NOT satisfy the LOD400 requirement at L-GATE_SPEC. Per-WP LOD400 must be authored before L-GATE_SPEC.

---

## 6. Enforcement Checklist (per WP)

Before each gate:

**Before L-GATE_ELIGIBILITY:**
- [ ] WP has canonical ID in format `S[N]-P[M]-WP[K]`
- [ ] WP registered in `_aos/roadmap.yaml` with at minimum: id, label, status, milestone_ref
- [ ] `spec_ref` points to an existing file (LOD300_milestone.md is acceptable at this stage), OR is set to `TBD` if the spec artifact has not been authored yet

> **`spec_ref: TBD` rule:** `validate_aos.sh` Check 4 skips file-resolution for `spec_ref: TBD`. Use this for WPs registered early (e.g., at roadmap planning, before LOD300 or LOD400 exists). `spec_ref` MUST be updated to a real file path no later than L-GATE_SPEC.

**Before L-GATE_SPEC:**
- [ ] Per-WP directory `_aos/work_packages/[WP-ID]/` exists
- [ ] `LOD400_spec.md` authored and in the WP directory
- [ ] `spec_ref` in `roadmap.yaml` updated to point to per-WP LOD400
- [ ] `lod_status` in `roadmap.yaml` updated to LOD400

**Before L-GATE_BUILD:**
- [ ] LOD500 being authored during build
- [ ] roadmap.yaml `current_lean_gate` = L-GATE_BUILD

**At L-GATE_BUILD:**
- [ ] `LOD500_asbuilt.md` written and in WP directory
- [ ] `roadmap.yaml` status updated to COMPLETE (or gate_history updated)
- [ ] `lod_status` = LOD500

---

## 7. Anti-Patterns (explicitly forbidden)

| Anti-pattern | Problem | Fix |
|---|---|---|
| Informal labels as IDs (WP-A1, WP-A2...) | Not searchable, not canonical, breaks roadmap.yaml | Assign `S[N]-P[M]-WP[K]` ID before execution |
| Cowork/execution shorthand ≠ canonical ID | Creates ID drift between execution docs and governance | The cowork doc is internal; canonical ID goes in roadmap.yaml and spec_ref |
| Milestone-level LOD300 as spec_ref at L-GATE_SPEC | LOD300_milestone is planning; LOD400 is the spec | Create per-WP LOD400 before L-GATE_SPEC |
| `spec_ref` pointing to a non-existent file (not TBD) | Check 4 FAIL; spec_ref must always resolve | Either create the file or set `spec_ref: TBD` (Check 4 skips TBD) |
| `[PROJECT-PREFIX]-P001-WP001` format | Doesn't encode stage; breaks hierarchy legibility | Always use `S[N]-P[M]-WP[K]` |
| Work_packages/ directory named by stage only (`S003/WP001/`) | Hides program level; breaks canonicality of ID | Use full ID as directory name: `S003-P003-WP001/` |
| Starting WP execution without roadmap.yaml entry | Status untracked, WP invisible to governance | Register in roadmap.yaml no later than L-GATE_SPEC (best practice: at identification or L-GATE_ELIGIBILITY) |

---

## 8. Grandfathering — Existing Non-Conforming IDs

Iron Rule #13 is **forward-looking**. It applies to all WPs registered from 2026-04-11 onward.

WPs registered before 2026-04-11 retain their existing IDs permanently:

| ID Pattern | Source | Status |
|---|---|---|
| `AOS-V310-WP0` .. `AOS-V310-WP8` | Hub roadmap (pre-rule) | Grandfathered — keep as-is |
| `AOS-V311-WP-A`, `AOS-V311-WP-B` | Hub roadmap (pre-rule) | Grandfathered — keep as-is |
| `AOS-V312-WP-CONSISTENCY` | Hub roadmap (same session as rule) | Grandfathered — keep as-is |
| Any other pre-2026-04-11 WP ID in any roadmap.yaml | Pre-rule | Grandfathered — no rename required |

**Rule for grandfathered WPs:**
- Do NOT rename grandfathered WP IDs in roadmap.yaml — renaming would break spec_ref paths and gate_history
- Do NOT rename associated `_COMMUNICATION/team_[ID]/[WP-ID]/` directories
- DO use canonical format (`S[N]-P[M]-WP[K]`) for all new WPs from 2026-04-11 onward

**The canon example in Iron Rule #12** (`_COMMUNICATION/team_110/AOS-V312-WP-GOV/`) demonstrates the subfolder pattern using a pre-rule WP ID. This example remains valid — the subfolder pattern is what the rule governs, not the ID format.

---

## 9. Cowork Package Reconciliation

When cowork packages use informal execution labels (e.g., WP-A1, WP-A2), reconciliation is required at WP completion:

1. Identify the canonical WP ID from roadmap.yaml that corresponds to the cowork work
2. Add a mapping note to the cowork doc header:
   ```
   > Canonical IDs: WP-A1 = S003-P003-WP005, WP-A4 = S003-P003-WP002
   ```
3. Update roadmap.yaml `gate_history` and `lod_status` to reflect completion
4. Author LOD500_asbuilt.md in the per-WP directory
5. No need to rename or restructure the cowork execution doc itself

---

## 10. CONTENT_SUBSTRATE — Nimrod Book WP ID profile (exception path)

**Scope:** Project id `nimrod-book` (`lifecycle_archetype: CONTENT_SUBSTRATE`), milestone bands `NB-Vn`.

**Pattern (reserved):** `NB-V{n}-WP-{token}` where `{n}` is a positive integer milestone band and `{token}` is an alphanumeric token (e.g. `A`, `B1`, `B2`, `G`).

**Regex:** `^NB-V[0-9]+-WP-[A-Za-z0-9]+(-[0-9]+)?$`

**Rules:**

| Rule | Detail |
|------|--------|
| **Uniqueness** | WP ids are unique within the project roadmap and in DB when synced |
| **API** | Hub `create_work_package` accepts NB IDs matching §10 regex (Team 00 Option B, 2026-04-17). L0 file-first + seed remain valid for spoke registration |
| **Hierarchy** | Ordering uses `depends_on` and `milestone_ref`; optional `parent_work_package_id` in DB (migration 010+) when epic/sub-WP is modeled |
| **vs default canon** | This profile is an **exception** to §1 for this project; **Team 00** may direct migration to `S[N]-P[M]-WP[K]` later |

**Cross-ref:** `_COMMUNICATION/team_100/TEAM100_BRIEF_CANONICAL_WP_HIERARCHY_NIMROD_BOOK_v1.0.0.md`, `RECOMMENDATION_TEAM00_CONTENT_SUBSTRATE_WP_ID_NIMROD_BOOK_v1.0.0.md`.

---

## 11. Global uniqueness of `work_packages.id` (hub database)

In the AOS v3 hub Postgres schema, `work_packages.id` is the **primary key for all projects**. It is **not** namespaced per `project_id` at the key level.

**Implications:**

- The default `SNNN-PNNN-WPNNN` pattern can still collide across unrelated spokes if two projects reuse the same triple (e.g. two L0 roadmaps both use `S001-P001-WP001`).
- **Mitigation:** Use **project-prefixed** or otherwise unique IDs for L0 spokes when syncing to the shared hub DB (examples from practice: `SFA-…`, `HH-…`, or distinct `S/P` staging). See `_COMMUNICATION/team_100/RISK_SUMMARY_DUAL_SPOKE_WP_ID_COLLISIONS_v1.0.3.md`.
- **CONTENT_SUBSTRATE** NB IDs (`NB-Vn-WP-*`) are reserved for project `nimrod-book` and are distinct from generic `S-P-WP` collisions by pattern.

**Rule:** Before adding a new WP to the hub DB, confirm the id does not already exist for another project (query or seed ordering).

---

*AOS Lean Kit | Module 01 — Project Governance | WP ID Standard | 2026-04-17*
