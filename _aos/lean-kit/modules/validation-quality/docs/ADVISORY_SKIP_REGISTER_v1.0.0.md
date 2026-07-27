# Advisory SKIP Register — validate_aos.sh

**Module:** 08 — validation-quality
**Version:** v1.0.0
**Authority:** team_100 (Chief Architect) / team_191 — under team_00 mandate
**Created:** 2026-06-15
**Refs:** ADR037 (CS cites), ADR048 / IR#15 (WAN dual-stack), ADR054 (Model-B cache), W9 (module 05/09 deprecation)

## Purpose

`validate_aos.sh` returns exit 0 when there are **0 FAIL** (SKIP is permitted). A
SKIP is *not* a failure, but an unexplained SKIP looks like hidden debt. This
register documents every check that **legitimately SKIPs** on the agents-os hub
with the full module set active, so a reviewer can confirm each remaining SKIP is
**justified** rather than a masked problem.

As of 2026-06-15 the hub gate is **48 PASS / 3 SKIP / 0 FAIL**. All three SKIPs
below are justified. They are *advisory by design* — the checks deliberately log
SKIP (not FAIL) so the L-GATE_BUILD exit criterion stays satisfiable while the
underlying legacy debt is scheduled separately.

> History: prior to the 2026-06-15 governance-hardening pass the hub showed
> 12 SKIPs in a fresh worktree (cache-not-hydrated ×5, dead checks 3/10,
> data/schema debt 21/23, doc-debt 26, ops-freshness 45, permanent-N/A 43).
> Nine were remediated; the three below remain by deliberate decision.

---

## Check 21 — Gate structure (`validate_gates.sh`) — **JUSTIFIED SKIP**

**Status:** Advisory SKIP. Clearing to PASS is **deferred** to a dedicated
architect-led migration WP (team_100 + team_00). Decision: 2026-06-15.

**Scope of the legacy debt** (measured 2026-06-15 over `_aos/roadmap.yaml`,
68 historical WPs `AOS-V310-*` … `AOS-V327-*`): **190 violations**.

| Rule | Count | Nature |
|------|-------|--------|
| V-GATE-1 (BR-16 lod_status enum) | 68 | Pre-enum vocabulary: `LOD500` (×17), `LOD200` (×8), `LOD400` (×3), `LOD200_DRAFT`, `LOD100_BRIEF`, plus `LOD500_LOCKED` with empty `gate_history` (BR-17). Required enum: `DRAFT / LOD100_APPROVED / LOD200_APPROVED / LOD300_APPROVED / LOD400_APPROVED / LOD500_LOCKED / SUPERSEDED / ARCHIVED`. |
| V-GATE-2 (BR-18 report_path) | 170 | PASS gate entries lacking a recognised, on-disk evidence path. |

**Why it cannot be cleared by automated/mechanical means** (143 PASS entries):

| Entry shape | Count | Remediable? |
|-------------|-------|-------------|
| `report_path` present, file exists | 1 | already PASS |
| `report_path` present, file missing | 1 | stale path — needs lookup |
| `verdict_ref` (legacy alias) | 8 | accepted (SKIP) — ok |
| legacy path field (`verdict_path` etc.), file **exists** | 27 | **safely migratable** → `report_path` |
| legacy path field, file missing | 2 | stale path |
| **notes-only, no artifact path at all** | **104** | **cannot fix without fabrication** |

The blocking factor is the **104 notes-only entries**: they record an outcome in
prose (`notes:`) but reference no artifact. Synthesising a `report_path` for them
would either point at a non-existent file (the validator checks existence → still
FAIL) or at an unrelated existing file (**falsifying the audit trail**). Per AOS
data-integrity principles this is forbidden, so Check 21 **cannot reach PASS**
without a human/architect migration that decides, per WP, whether to locate a real
artifact, backfill from primary records, or `ARCHIVE`/`SUPERSEDE` the entry.

**Recommended remediation (when prioritised):** a dedicated LOD-tracked migration
WP that (a) normalises the 68 `lod_status` values to the enum, (b) migrates the 27
real-artifact entries to `report_path` and resolves the 2 stale ones, (c) decides
archive-vs-backfill for the 104 notes-only entries against primary governance
records. Until then this SKIP is justified.

**Reproduce:** `bash lean-kit/modules/validation-quality/scripts/validate_gates.sh --roadmap _aos/roadmap.yaml`

---

## Check 23 — Verdict schema (`validate_verdicts.sh`) — **JUSTIFIED SKIP**

**Status:** Advisory SKIP. Deferred to the same migration WP as Check 21.

**Scope** (measured 2026-06-15, 140 verdict files scanned): **90 PASS · 23 FAIL ·
27 SKIP**. The 23 FAIL files (mostly `team_190/VERDICT_*`) miss standardised
fields — typically `work_package`, `criteria_total`, `criteria_pass`,
`criteria_fail` (sometimes `to`). These are **factual claims about a past
validation outcome**: backfilling `criteria_total/pass/fail` requires reading each
verdict's body and asserting the counts the validator actually reached. That is a
per-file, judgement-bearing migration — not a mechanical default — and is owned by
the verdict authors (team_90 / team_190), so it is deferred rather than guessed.

**Reproduce:** `bash lean-kit/modules/validation-quality/scripts/validate_verdicts.sh`

---

## Check 43 — Milestone completeness — **JUSTIFIED (PERMANENT) SKIP**

**Status:** Permanent N/A until AOS adopts milestone-definition files.

`_aos/milestones/` is absent (pre-MS001). The check has no milestone definitions
to validate against and logs SKIP with "acceptable pre-MS001". This is the
**expected** state for the current AOS install: milestones are tracked in
`roadmap.yaml` / charter ADRs, not as discrete `_aos/milestones/` definition files.
The SKIP becomes actionable only if/when AOS adopts a milestone-files convention,
at which point `_aos/milestones/` definitions would be added and this check would
begin validating them. No action required now.

---

## Maintenance

When a check listed here is remediated (or a new advisory SKIP is introduced),
update this register in the same commit. A SKIP that is **not** explained here
should be treated as suspect during review.
