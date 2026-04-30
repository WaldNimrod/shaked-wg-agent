---
id: ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL
version: 1.0.0
status: ACTIVE
from: team_100 (Chief System Architect)
approved_by: team_00 (Principal)
date: 2026-04-30
wp: AOS-V4-WP-CHARTER
supersedes: null
folded_in: ADR045 (Sprint Discipline — per team_00 decision G4, no separate ADR045 file)
successor_dependencies:
  - ADR046 (Engine and Execution Tiering)
  - AOS-V4-WP-ENGINE-MATRIX
  - AOS-V4-WP-ENGINE-ADAPTER
  - AOS-V4-WP-VALIDATE-CHECKS-39-43
  - AOS-V4-WP-CONTINUATION-AND-FANOUT
  - AOS-V4-WP-INTERFACE-AUDIT
sources:
  primary_strategic_plan:
    name: 100-lovely-kahan.md
    location: ~/.claude/plans/100-lovely-kahan.md
    in_repo: false
    rationale: |
      Nimrod's (team_00) canonical strategic plan for v4.0.0; kept in the user's
      private plans directory (`~/.claude/plans/`) by design — it is a personal
      planning artifact, not a repo deliverable. ADR044 is the in-repo binding
      governance projection of that plan; in-repo companions for traceability are
      `_COMMUNICATION/team_00/V4_MILESTONE_AOS-V4-MS001_LOD200_v1.0.0.md` and
      `_COMMUNICATION/team_00/V4_GAP_MATRIX_v1.1.0_AMENDMENT.md`.
  in_repo_companions:
    - _COMMUNICATION/team_00/V4_MILESTONE_AOS-V4-MS001_LOD200_v1.0.0.md
    - _COMMUNICATION/team_00/V4_GAP_MATRIX_v1.1.0_AMENDMENT.md
    - _aos/work_packages/AOS-V4-WP-CHARTER/LOD200_spec.md
---

# ADR044 — AOS v4.0.0 Charter and Track Model

> "The difference between L0 and L3 is not features — it is trust. v4.0.0 is the first release designed to earn that trust mechanically."
> — team_00 (Principal), 2026-04-29

---

## §0 — v4.0.0 Charter

### §0.0 Release Identity

| Field | Value |
|-------|-------|
| **Codename** | "Autonomous" |
| **Tag** | v4.0.0 |
| **Predecessor** | v3.1.2 (Dashboard) |
| **Type** | Major release — breaking methodology changes |
| **Why major** | Track model replaces L-tier as WP classifier (vocabulary change); Sprint Discipline is a new structural constraint; L2.5 retired; 6-track model is additive but incompatible with v3 WP metadata schema |
| **Branch** | feat/v4 → merge to main at GA |
| **Milestone** | AOS-V4-MS001 (10 WPs, 3 sprints per milestone cap) |

### §0.1 Why v4.0.0 Is a Major Release

AOS v3 accumulated at least 5 critical failure modes that required architectural intervention:

- **F1 — L-tier vocabulary collapse:** L0/L2/L3 served as both AOS install capability tier AND WP classifier. These are orthogonal concepts. By v3.1.2, no agent could reliably resolve "what track is this WP?" from its L-tier label alone.
- **F2 — No RESEARCH track:** Research mandates (taxonomy analyses, tool evaluations, "should we adopt X?") were squeezed into STANDARD track despite having no code deliverable, no LOD400, and no V gate. Output was ungoverned.
- **F3 — No OPS track:** Infrastructure WPs went through STANDARD's LOD200→LOD500 pipeline, designed for code features — adding overhead with zero governance value for operational work.
- **F5 — Marathon drift:** WPs had no mechanical scope limit. "Almost done" WPs persisted weeks. The only brake was team_00 judgment, making Team 00 a bottleneck for scope decisions.
- **F2/F3 combined — Agent misclassification:** Without discrete track definitions and a binding decision tree, agents repeatedly applied wrong LOD paths, wrong gate sequences, and wrong engine defaults.

v4.0.0 addresses all of these by establishing: (a) a 6-track model with a binding decision tree, (b) L-tier redefinition as installation capability tier only, (c) sprint discipline as a project-level charter constraint, and (d) a completeness gate preventing milestone closure with unresolved items.

### §0.2 GA Success Metrics (§0.1)

The following 15 criteria must ALL pass before v4.0.0 is marked GA. Team_190 validates each criterion with codex engine (IR#1).

| # | Criterion | Measured by |
|---|-----------|-------------|
| 1 | Every WP created since alpha declares `track:` in metadata.yaml | `grep "track:" _aos/work_packages/*/metadata.yaml` → all files return a hit |
| 2 | Track Model decision tree is referenced in at least 2 WP metadata comments | `grep "ADR044\|track.*decision" _aos/work_packages/*/metadata.yaml` |
| 3 | L2.5 removed from all active methodology files (no new L2.5 references post-v4.0.0) | `grep -rn "L2\.5" methodology/ CLAUDE.md` → only historical/deprecation references |
| 4 | Sprint Discipline constraint in at least 2 LOD200 specs | `grep -rn "sprint cap\|Sprint.*cap\|≤3 days" _aos/work_packages/*/LOD200_spec.md` |
| 5 | ADR044 present and ACTIVE | `ls governance/directives/ADR044_*` → exits 0 |
| 6 | validate_aos.sh 0 FAIL across hub | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL |
| 7 | All 10 v4.0.0 WPs reach LOD500_LOCKED | `grep "LOD500_LOCKED" _aos/work_packages/AOS-V4-*/metadata.yaml` → 10 hits |
| 8 | Cost caps schema present (W2 deliverable) | `ls core/config/cost_caps.yaml` → exits 0 |
| 9 | Engine Matrix registered (W2 deliverable) | `ls core/config/engines.yaml` → exits 0 |
| 10 | Sprint discipline Check 42 operational (W7 deliverable) | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh . 2>&1 | grep "Check 42"` → PASS |
| 11 | At least one RESEARCH-track WP closed under proper gates | `grep "track: RESEARCH" _aos/work_packages/*/metadata.yaml` + corresponding closure |
| 12 | At least one OPS-track WP closed under proper gates | `grep "track: OPS" _aos/work_packages/*/metadata.yaml` + corresponding closure |
| 13 | Engine routing rule present in ADR046 | `ls governance/directives/ADR046_*` → exits 0 |
| 14 | engines.yaml contains at least Haiku + Sonnet + Codex entries | `grep -c "haiku\|sonnet\|codex" core/config/engines.yaml` → ≥3 |
| 15 | MASTER_CLOSURE artifact filed for v4.0.0 | `ls _COMMUNICATION/team_00/MASTER_CLOSURE_*v4*` → exits 0 |

---

## §1 — Track Model

### §1.1 Overview

The Track Model is the **primary WP classifier** in AOS v4.0.0. It replaces the v3 practice of using L-tier (L0/L2/L3) as a WP property. Tracks describe the **nature and shape of work**; L-tiers describe the **AOS installation capability** of a domain. These are orthogonal concepts.

Six tracks are defined, plus one orthogonal modifier:

| # | Track | Hebrew | English |
|---|-------|--------|---------|
| 1 | **EXPRESS** | מהיר | Fast, small-scope, low-risk |
| 2 | **STANDARD** | תקני | Standard feature/governance work |
| 3 | **MANAGED** | מנוהל | Complex, multi-team, high-risk |
| 4 | **RESEARCH** | חקר | Investigation, no code deliverable |
| 5 | **OPS** | תפעול | Infrastructure, server, deploy |
| 6 | **CONTENT** | תוכן | Non-code artifact production |
| + | **HOTFIX** | דחוף | Emergency modifier (any track) |

### §1.2 Per-Track Attribute Tables

#### Track 1 — EXPRESS / מהיר

| Attribute | Value |
|-----------|-------|
| **Trigger** | Bug fix ≤2 files, doc/config tweak, ADR text amendment, propagation chore |
| **LOD path** | LOD400 only (skip 100/200/300; spec lives in commit message) |
| **Gates** | L-GATE_BUILD only |
| **Validator** | team_90 quick check OR self-verify if doc-class trivial |
| **Default engine** | claude-code or any-open |
| **Sprint count** | 1 |
| **Wall-clock cap** | ≤1 day |
| **Audit** | git commit message |
| **Examples** | ADR034 R9 propagation fixes, MSG template tweak, lean-kit doc bump |

#### Track 2 — STANDARD / תקני

| Attribute | Value |
|-----------|-------|
| **Trigger** | Product/governance WPs; clear scope, single domain, single team writer |
| **LOD path** | LOD200 → LOD400 → LOD500 |
| **Gates** | L-GATE_SPEC → L-GATE_BUILD → L-GATE_V → L-GATE_COMPLETE_QA |
| **Validator** | team_90 (BUILD); team_190 (SPEC + V final) |
| **Default engine** | claude-code or codex |
| **Sprint count** | 1–3 |
| **Wall-clock cap** | 1 milestone (3 sprints) |
| **Audit** | verdict artifacts + commit chain + roadmap.yaml gate_history |
| **Examples** | MSG-LOG, MSG-HARDENING, most governance WPs, this WP (W1) |

#### Track 3 — MANAGED / מנוהל

| Attribute | Value |
|-----------|-------|
| **Trigger** | HIGH risk, multi-team, new state machine, cross-domain, PARADIGM_SHIFT |
| **LOD path** | LOD200 → LOD300 → LOD400 → LOD500 |
| **Gates** | L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_V → L-GATE_COMPLETE + 2 human gates |
| **Validator** | team_190 (final V) + named domain validator |
| **Default engine** | cowork (design) + claude-code (build) |
| **Sprint count** | up to 1 Stage (8 weeks max) |
| **Wall-clock cap** | 1 Stage |
| **Audit** | full artifact set + phase gates |
| **Examples** | AUTO-ACTIVATION-DRYRUN, future ROADMAP-API, complex cross-domain features |
| **Note** | L2.5 is retired; MANAGED is its replacement with cleaner naming |

#### Track 4 — RESEARCH / חקר (gap-fill — new in v4.0.0)

| Attribute | Value |
|-----------|-------|
| **Trigger** | Investigation, taxonomy, market scan, tooling evaluation — no code deliverable |
| **LOD path** | LOD100 (question) → research report |
| **Gates** | None — team_00 reads-and-decides |
| **Validator** | team_00 personally |
| **Default writer team** | team_80 (Research) |
| **Default engine** | gemini (long synthesis) or any |
| **Sprint count** | 1–2 |
| **Wall-clock cap** | Per mandate, typically ≤1 week |
| **Audit** | Report artifact in `_COMMUNICATION/team_80/RESEARCH_REPORT_*.md` |
| **Examples** | Cursor optimal usage research, MCP adoption analysis, validation taxonomy |
| **Addresses** | F2 — no track for research work in v3 |

#### Track 5 — OPS / תפעול (gap-fill — new in v4.0.0)

| Attribute | Value |
|-----------|-------|
| **Trigger** | Infra change: server config, port-registry, deploy script, MCP install, service provisioning |
| **LOD path** | LOD400 inline OR runbook (no LOD200/300 needed; ops is procedural) |
| **Gates** | L-GATE_BUILD (post-hoc verify on real infra) |
| **Validator** | team_60 (Infrastructure) self-verify OR team_99 (Server) attest |
| **Default writer team** | team_60 OR team_99 |
| **Default engine** | claude-code + team_99 |
| **Sprint count** | 1–2 |
| **Wall-clock cap** | Typically ≤1 day |
| **Audit** | port-registry diff + commit + service health check log |
| **Examples** | Port-registry add, AOS API deployment, MCP server install, server hardening |
| **Addresses** | F3 — no track for infrastructure work in v3 |

#### Track 6 — CONTENT / תוכן

| Attribute | Value |
|-----------|-------|
| **Trigger** | Non-code project: book chapter, presentation, video, design, marketing |
| **LOD path** | LOD100 → LOD200 → shipped artifact (no LOD400/500) |
| **Gates** | L-GATE_SPEC → L-GATE_DELIVER (custom) |
| **Validator** | team_00 personally OR domain expert |
| **Default writer team** | team_35 (Design Studio) |
| **Default engine** | claude-desktop / cowork / gemini |
| **Sprint count** | Variable (CONTENT often iterative) |
| **Wall-clock cap** | Per project |
| **Audit** | Artifact in domain repo + DECISION_RECORDED in `_COMMUNICATION/team_00/` |
| **Examples** | nimrod-book chapters, microgreens blender, Eyal Amit content, dispatch bot UX docs |

#### Modifier — HOTFIX / דחוף

| Attribute | Value |
|-----------|-------|
| **What it is** | A flag attachable to ANY track (typically EXPRESS or STANDARD) |
| **Effect** | Forces worktree branch; pre-empts current work; cap 4h wall-clock; post-hoc V allowed |
| **Trigger** | Production blocker, security finding, broken main, validate_aos.sh × spoke FAIL |
| **Wall-clock cap** | ≤4h |
| **Branch** | Worktree mandatory |
| **Scope** | Single-file or single-config preferred |
| **Recovery** | Mandatory artifact: `HOTFIX_RECOVERY_*.md` |
| **Audit** | Dedicated commit + post-hoc verdict + recovery plan |
| **NOT a track** | Does not change LOD or gates of the underlying track; modifies execution mode only |

---

## §2 — Track Selection Decision Tree

The following decision tree is **binding**. Every WP metadata.yaml MUST have a `track:` field that can be justified by traversing this tree. Source: `STRATEGIC_BRIEF_TRACK_MODEL_DEEP_ANALYSIS_v1.0.0.md` §A.5 (authoritative).

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

**Rules for applying the tree:**
1. Traverse top-to-bottom; take the first matching branch.
2. When in doubt between STANDARD and MANAGED, default to MANAGED (higher governance).
3. HOTFIX modifier may be applied AFTER track selection — it does not change the track.
4. Track assignment is recorded in `metadata.yaml` field `track:` (required for all v4.0.0 WPs).
5. Retroactive reclassification of closed v3 WPs is FORBIDDEN (per `~/.claude/plans/100-lovely-kahan.md` §15 — strategic plan, out-of-repo by design; see frontmatter `sources`). Only forward-created WPs use this tree.

---

## §3 — Effort Levels

Effort levels are orthogonal to track. They describe the **resource intensity** of a WP, not the nature of its work. Every WP metadata.yaml carries an `effort:` field.

### §3.1 Effort Level Definitions

| Effort | Description | When to use |
|--------|-------------|-------------|
| **LOW** | Trivial work, no design, 1 builder, auto-validate | Bug fix, config patch, doc update |
| **NORMAL** | Standard work, standard design, 1 builder, team_190 V | Most product/governance WPs |
| **HI** | Complex work, full design (LOD300 where applicable), may need multi-builder | MANAGED track, complex STANDARD, novel architecture |

### §3.2 Effort Level Attribute Table

| Attribute | LOW | NORMAL | HI |
|-----------|-----|--------|----|
| **Validators** | team_90 quick | team_90 BUILD + team_190 V | team_190 all gates + named domain validator |
| **Test coverage** | Self-verify only | AC-based verification | Full AC + integration + regression |
| **Builder engine tier** | Any (haiku OK) | claude-code or codex | Premium (claude-code Sonnet, codex GPT-5) |
| **LOD depth** | LOD400 only | LOD200 → LOD400 | LOD100/200/300 → LOD400 |
| **Per-WP/day cost cap** | $1 | $5 | $20 |
| **Per-WP total cost cap** | $5 | $30 | $100 |
| **Sprint flex** | 1 sprint max | 1–3 sprints | Up to 1 Stage |
| **Documentation** | Commit message | Closure artifact | Full audit trail + MASTER_CLOSURE |

### §3.3 Effort Flex Rules

- **LOW effort with overrun:** If a LOW-effort WP exceeds 1 day, escalate to NORMAL and re-evaluate scope.
- **NORMAL effort with overrun:** If a NORMAL-effort WP reaches sprint 3 without closure signal, builder escalates to team_100 for scope trim review.
- **HI effort milestone:** Check-in with team_00 at each sprint boundary (end of sprint 1 and sprint 2) before authorizing sprint 3+.

---

## §4 — L-Tier Redefinition

### §4.1 Binding Rule (v4.0.0 forward)

**L-tier = AOS install capability tier ONLY. L-tier is NEVER a WP property.**

This rule is **effective immediately** for all WPs created on or after 2026-04-30.

### §4.2 L-Tier Definitions (install capability only)

| Tier | Name | Install capability | WP property? |
|------|------|-------------------|--------------|
| **L0** | Lean | Manual governance only; no pipeline engine | **NEVER** |
| **L2** | Pipeline | Full pipeline + DB + dashboard | **NEVER** |
| **L3** | Autonomous | Full AUTO-ACTIVATION + autonomous routing | **NEVER** (future) |

**L1:** Deprecated early experiment. Not referenced in active methodology.

**L2.5:** RETIRED as of v4.0.0. L2.5 was invented mid-flight to cover Cowork sessions (team_200). In v4.0.0:
- L2.5 is replaced by the **MANAGED track** for WP classification
- team_200 (Cowork Bundle) remains an operational team but is no longer an "L-tier"
- All existing L2.5 references in spoke CLAUDE.md files are migration targets for W7 propagation

### §4.3 Historical Note

In v3, L-tier was used both ways — a domain might say "this project is L2" AND a WP might say "track: L2.5". This dual use caused systematic misclassification (F1). The fix is simple: use Track for WP classification; use L-tier for install capability. Do not conflate.

### §4.4 L0 Fallback — Always Preserved

> **תמיד יש fallback ל-L0.** — team_00 directive, 2026-04-29

Every AOS domain retains L0 as a valid operating mode regardless of installed tier. Specifically:

- A domain running L2 may operate in L0 mode (file-only, manual routing) during DB outage
- L0 is not a degraded state — it is a first-class operating mode
- Sprint discipline, Track Model, and all v4.0.0 improvements apply to L0 domains
- The Lean Kit is the instrument of L0 governance; it must remain functional in all v4.0.0 domains
- ADR034 R8 (Offline Changelog Protocol) codifies the DB-offline variant of L0 operation for L2 domains

**No v4.0.0 change removes or degrades L0 capability. L0 fallback is constitutional.**

---

## §5 — Sprint Discipline

> **Note: This section is a PROJECT-LEVEL CHARTER, not a System Iron Rule.** Sprint Discipline was proposed as IR#15 in the STRATEGIC_BRIEF_TRACK_MODEL_DEEP_ANALYSIS_v1.0.0.md Block B, but per team_00 decision G4 it is FOLDED INTO this ADR044 charter as a project-level constraint — not elevated to a constitutional Iron Rule. The distinction matters: Iron Rules cannot be overridden even by team_00; Charter constraints can be adjusted by team_00 + team_100 for a specific WP with explicit justification.

### §5.1 Sprint Definition

A **sprint** is a single ≤3-day burst with:
- **1 engine** (one AI engine instance per sprint)
- **1 writer team** (one team holds write authority per sprint)
- **1 deliverable** (one named artifact or coherent file set per sprint)

These constraints are mechanical, not aspirational. A sprint that produces two unrelated deliverables or uses two engines is a process violation — the WP should have been split.

### §5.2 Milestone and WP Scope

| Unit | Definition | Sprint count | What triggers restructure |
|------|------------|--------------|--------------------------|
| **Sprint** | ≤3 days, 1 engine, 1 writer, 1 deliverable | 1 | n/a |
| **WP** | One coherent work unit with single ownership | 1–3 sprints | 4+ sprints needed → restructure as Program |
| **Milestone** | Bounded delivery checkpoint with gate | 3 sprints ("300m") | Stage boundary |
| **Program** | Multi-WP structure for 4+ sprint scope | N/A | WP scope too large |

**Sprint ID format:** `S[N].M[m].S[s]` — e.g., `S006.M1.S1` (Stage 6, Milestone 1, Sprint 1).

This format is parallel to the canonical S/P/WP grammar (`S[N]-P[M]-WP[K]`) and is searchable/sortable.

### §5.3 Sprint Sync Windows

| Sprint type | Rest/sync window |
|-------------|-----------------|
| **Inline sprints** (laptop, single session) | End of working day |
| **Cowork sprints** (team_200 bundle) | ≤90 min wall-clock (depletion-aligned per IR-13 in team_200.md) |
| **Back-to-back sub-agent fan-out** | No mandatory rest — sub-agents are parallel by design |

### §5.4 HOTFIX Sprint Exception

When the HOTFIX modifier is applied to any sprint:
- Wall-clock cap tightens to **≤4h**
- Worktree branch is **mandatory**
- Scope MUST be single-file or single-config preferred
- Recovery plan (`HOTFIX_RECOVERY_*.md`) MUST be filed before merge

### §5.5 Effort Flex Rules for Sprints

| Effort level | Sprint cap per WP | Overrun escalation |
|--------------|-------------------|--------------------|
| LOW | 1 sprint | Escalate to NORMAL immediately |
| NORMAL | 1–3 sprints | team_100 scope review at sprint 3 start |
| HI | Up to 1 Stage | team_00 check-in at each sprint boundary |

### §5.6 Sub-Agent Fan-Out Pattern

When a WP's LOD400 session hits token budget mid-execution, the pre-authorized split pattern is:
1. **Part A** (primary sub-agent): Core deliverable + primary methodology file(s)
2. **Part B** (secondary sub-agent): Supporting file updates (governance, CLAUDE.md, etc.)
3. **Synthesis**: Part A commits to feature branch; Part B rebases on Part A before committing

This pattern is canonical per TT S005-P006-WP002 precedent (2026-04-29). W8 (CONTINUATION-AND-FANOUT) will canonicalize the full methodology in `methodology/AOS_SUBAGENT_FANOUT_PATTERN_v1.0.0.md`.

### §5.7 Addresses F5 (Marathon Drift)

Sprint Discipline directly addresses F5 by:
- Making "is this WP too big?" a mechanical check (Check 42: sprint count ≤3)
- Requiring restructure as Program for 4+ sprint needs
- Providing HOTFIX modifier for emergency bypass with strict cap
- Providing sub-agent fan-out for token-budget splits without losing audit trail

---

## §6 — L0 Fallback Preservation (Mandatory)

This section implements team_00 directive (2026-04-29): **"תמיד יש fallback ל-L0"** (there is always a fallback to L0).

### §6.1 Constitutional Guarantee

**L0 fallback is preserved for every AOS domain, regardless of installed tier.** This is not a soft preference — it is an architectural requirement of AOS v4.0.0.

Specific guarantees:
1. The Lean Kit remains a functional, self-contained governance instrument in all v4.0.0 domains.
2. Track Model, Sprint Discipline, and ADR044 apply equally to L0 domains (no L0 exemption needed — these are methodology constraints, not engine constraints).
3. No v4.0.0 change introduces a dependency on DB, API, or automation that blocks L0 operation.
4. When a L2 domain loses DB access, ADR034 R8 (Offline Changelog Protocol) restores L0-mode file authority.
5. The Lean Kit's `profiles/L0.yaml` is the canonical operating mode descriptor for L0 domains; it must remain current with all v4.0.0 Track Model additions.

### §6.2 What L0 Fallback Means In Practice

| Scenario | L0 fallback action |
|----------|--------------------|
| DB unreachable in L2 domain | ADR034 R8 offline protocol; PENDING_DB_SYNC.yaml tracks mutations |
| No API available | File-based WP tracking in roadmap.yaml with git commit as audit record |
| No automation tooling | Manual routing by team_00; all gates pass via artifact file exchange |
| New domain not yet L2-capable | Start at L0; upgrade to L2 when infrastructure ready; governance contracts identical |

---

## §7 — Migration Notes (v3 → v4)

### §7.1 Forward-Only Changes

Per `~/.claude/plans/100-lovely-kahan.md` §15 (strategic plan, out-of-repo — see frontmatter `sources`):
- Retroactive reclassification of **closed** v3 WPs is **FORBIDDEN**
- In-flight WPs at v4.0.0 launch are reclassified by their owner team before next gate
- `track:` field is required for all new WPs (Check 42 enforces; W7 implements)

### §7.2 L2.5 Migration Path

| v3 artifact | v4 treatment |
|-------------|-------------|
| `L2.5` references in spoke CLAUDE.md files | Replace with "MANAGED track" where WP-classifier; leave "L2.5 (retired)" note |
| L2.5 governance contracts | Remain readable as history; flagged `deprecated: true` |
| New WPs with L2.5 characteristics | Classified as MANAGED track with NORMAL or HI effort |
| team_200 Cowork bundles | Remain operational; now described as "MANAGED track execution mode" |

### §7.3 Team Governance Updates (v4.0.0)

The following team contracts are updated in this WP (W1) to reflect Track Model:
- **team_100.md** — Track Model authority paragraph added
- **team_99.md** — Terminal-managed execution mode + OPS track authority added
- **team_98.md** — HOTFIX modifier and EXPRESS track cross-reference added
- **team_35.md** — CONTENT track cross-reference and PIPELINE_FEEDER linkage added
- **team_200.md** — MANAGED track linkage paragraph added (additive only)

---

## §8 — Authority and Maintenance

### §8.1 Track Assignment Authority

- **team_100** owns track assignment and ADR044 interpretation for all hub-native WPs (AOS-V* format)
- **Domain lead architect** (team_110 or equivalent) owns track assignment for spoke-native WPs (SNNN-PNNN-WPNNN format)
- **team_00** is the final arbiter for any track assignment dispute

### §8.2 ADR044 Amendment Protocol

Changes to this ADR require:
1. team_100 authors amendment (ADDENDUM or new version)
2. team_190 validates amendment at L-GATE_SPEC
3. team_00 approves
4. `validate_aos.sh` Check 43 passes before release

Minor clarifications (no semantic change) may be authored by team_100 without full gate cycle, with team_00 awareness.

### §8.3 Completeness Gate (G4 enforcement)

Per team_00 decision G4 ("תכנון התהליך והחבילות חייב להבטיח השלמה מלאה"):
- Every LOD200 spec MUST list explicit DoD criteria; deferred DoDs are forbidden at spec time
- team_190 validates DoD presence at L-GATE_SPEC
- Check 43 (`validate_aos.sh` W7 deliverable) enforces milestone completeness at merge time
- MASTER_CLOSURE artifact required at v4.0.0 GA

---

## §9 — Checks Introduced (W7 implements)

The following `validate_aos.sh` checks are **defined here** and implemented by W7 (AOS-V4-WP-VALIDATE-CHECKS-39-43):

| Check # | Purpose | ADR044 §reference |
|---------|---------|-------------------|
| 42 | Sprint discipline: WP sprint count ≤3 in all metadata.yaml files | §5.2 |
| 43 | Milestone completeness gate: all WP DoDs PASS, no placeholder strings, MASTER_CLOSURE filed | §8.3 |

---

## Revision History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-04-30 | team_100 (AOS-V4-WP-CHARTER, builder: team_110 claude-code Sonnet) | Initial — v4.0.0 charter, 6-track model, sprint discipline (ADR045 folded per G4), L-tier redefinition, L0 fallback |

*Filed by team_110 (sub-agent builder) per AOS-V4-WP-CHARTER LOD200 spec — 2026-04-30*
*ADR045 (Sprint Discipline) was proposed separately but FOLDED INTO this ADR044 per team_00 decision G4 (V4_GAP_MATRIX_v1.1.0_AMENDMENT.md §1): "Fold into ADR044 + completeness gate required — no tails left behind."*
