# V4_LEGACY_QUARANTINE — Marker Convention

**Module:** project-governance
**Version:** v1.0.0
**Date:** 2026-07-05
**Authority:** team_00 (mandate) + team_100 (co-ratify)
**Author/custodian:** team_120
**Companion to:** `DOMAIN_DOC_ARCHIVE_SWEEP_PROCEDURE_v1.0.0.md` (Phase 4 applies this)
**Problem it solves:** today "this is old/deprecated" is expressed only as **human header prose** (e.g. the
`_aos/context/_retired_v4/` warnings). Prose is invisible to a weak engine and to validators. This convention makes
v4-legacy status **machine-readable** so no engine ever derives new v5 work from a v4 artifact.

---

## When to apply (scope)
Apply ONLY to an artifact that is **still OPEN / still referenced** but belongs to AOS v4 (its owning WP-ID is
`AOS-V4*`, or it is a v4-era structure kept live for reference). Do **NOT** apply it to:
- **Closed** artifacts → those ARCHIVE (`_archive/`), they need no marker.
- **Retired non-WP** artifacts with no active reader → those ARCHIVE too (RULE-D).
- **v5-current** artifacts → KEEP, untouched.
(The sweep procedure's decision table routes each case; this file only defines the marker itself.)

## The marker — three parts, all additive, all mechanical

### Part 1 — Frontmatter block (the machine-readable SSoT for the marker)
Prepend to the artifact's YAML frontmatter (create a frontmatter block if none exists). Idempotent: if
`aos_lifecycle: V4_LEGACY_QUARANTINE` is already present, do nothing.

```yaml
aos_lifecycle: V4_LEGACY_QUARANTINE      # the machine-readable flag validators/agents key on
not_a_template: true                     # explicit: never use as a base/example for new work
quarantined_by: <team_id>                # who stamped it
quarantine_date: <YYYY-MM-DD>
quarantine_reason: <one line — why it is v4-legacy and still present>
successor_ref: <path to the v5 equivalent, or "none-yet">   # the retirement pointer
```

### Part 2 — Body banner (human-visible, top of file)
Insert as the first body line (after frontmatter):
```
> ⚠️ **V4-LEGACY — QUARANTINED <YYYY-MM-DD>.** Belongs to AOS v4; **NOT** a v5 template or base for continuation.
> Do not derive new work from this file. Registry: `_aos/V4_QUARANTINE_INDEX.md`.
```

### Part 3 — Domain quarantine index (`_aos/V4_QUARANTINE_INDEX.md`)
One append-only table per domain (create on first quarantine). Every quarantined artifact = one row:
```markdown
# V4 Legacy Quarantine Index — <DOMAIN_ID>
> Machine + human registry of v4-legacy artifacts kept live under quarantine (not v5 templates).
> Convention: lean-kit project-governance/V4_LEGACY_QUARANTINE_CONVENTION_v1.0.0.md

| artifact path | owning WP/ID | quarantine_date | reason | successor_ref |
|---------------|--------------|-----------------|--------|---------------|
| … | … | … | … | … |
```

## How consumers MUST treat a quarantined artifact
- **Agents / engines:** an artifact with `aos_lifecycle: V4_LEGACY_QUARANTINE` or `not_a_template: true` is
  **read-only reference at most** — never copied, extended, or used as the scaffold for a new WP/template. If your
  task seems to require deriving from one, STOP and route to team_120 (its `successor_ref` is the correct base).
- **Validators:** `validate_aos.sh` (advisory check, future WP) SHOULD flag a NEW artifact that appears
  copy-derived from a quarantined one, and SHOULD verify every `_aos/V4_QUARANTINE_INDEX.md` row still resolves.
- **team_120 (custodian):** owns retirement — every quarantined item should acquire a real `successor_ref` over
  time and then move to `_archive/` once nothing references it. Quarantine is a **holding state, not a parking lot.**

## Lifecycle
`OPEN v4-legacy` → **QUARANTINE** (this marker) → (successor built / references removed) → **ARCHIVE** → done.
Never delete.

## Relationship to existing markers
Supersedes the ad-hoc prose header used in `_aos/context/_retired_v4/` (which is itself a RULE-D **archive**
candidate, not a quarantine candidate — it has no active reader). Going forward, "old but still present" is
expressed by THIS structural marker, not by free-text warnings.

---
*team_120 (custodian) + team_00 (mandate) | V4_LEGACY_QUARANTINE Convention v1.0.0 | 2026-07-05*
