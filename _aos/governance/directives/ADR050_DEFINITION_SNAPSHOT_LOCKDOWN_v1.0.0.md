# ADR050 — Definition Snapshot Lockdown (`core/definition.yaml` as sole canonical, drift-detected)

## 0. Status

**Status:** ACCEPTED — pending team_190 L-GATE_VALIDATE (STANDARD-track, cross-engine; Iron Rule #1)
**Date:** 2026-05-25
**Authors:** team_200 (Cowork — implementation) on team_00 directive
**Validated by:** team_190 (Senior Constitutional Validator) — L-GATE_VALIDATE PENDING
**Companion to:** ADR049 (Registry SSoT Lockdown)
**Related:** ADR034 (Data Authority — DB SSoT), ADR040 (Governance Authority Lockdown), `methodology/AOS_DIRECTORY_CANON_v1.0.0.md`

---

## 1. Context

ADR049 closed one of three drift-vector classes identified in the 2026-05-25 audit: the **registry** class (`_aos/projects.yaml` ↔ derived surfaces). This ADR closes the second class: **team definition snapshots**.

Hub `core/definition.yaml` is the canonical L2 engine seed for team definitions — WHO/HOW for every team (id, label, engine, gate_authority, writes_to, iron_rules, role_description, etc.). At project-canonization time, each spoke is initialized with `_aos/definition.yaml` carrying a **subset** of the hub's team blocks (those activated for that spoke per `team_assignments` plus universal teams). The intent has always been that each spoke's team_NN block be a **verbatim slice** of the corresponding hub team_NN block — no spoke-side edits, no hand-maintenance.

The reality (audit 2026-05-25):

| Observation | Detail |
|---|---|
| Spokes carry abbreviated `team_NN:` blocks (often 8 lines) | Hub equivalents are 25–49 lines (full `role_description`, full `iron_rules`, etc.) |
| No mechanical enforcement existed | Spoke definition.yaml was never compared to hub definition.yaml after the initial seed |
| Drift accumulated silently | Spoke agents read stale governance fields (engine assignments, gate authority, iron rules) |
| 106 drift records across 12 spokes | Surfaced by the new `check_definition_snapshot_consistency.sh` script (see §4) |

**Drift mechanism:** `/AOS_project-init` seeds spoke `_aos/definition.yaml` once. Subsequent hub team-block changes (e.g., team_35 activation, team_190 role expansion) are not propagated to existing spokes' snapshots. `aos_sync_all.sh` propagates hub governance but did not previously include a definition-snapshot consistency gate.

**Why this matters:**
- Spoke agents that hydrate context from `_aos/definition.yaml` read incomplete role descriptions, missing iron rules, and stale gate authority — leading to incorrect operating behavior in spoke sessions.
- Cross-engine validation (Iron Rule #1) assumes both engines see the same team definitions; drift breaks this assumption silently.

## 2. Decision

Hub `core/definition.yaml` is the **sole canonical SSoT** for team definitions. Spoke `_aos/definition.yaml` files are **snapshots** that must contain verbatim copies of the team blocks they include from the hub. Drift is **detected** (not auto-fixed) by `validate_aos.sh` Check 47 (hub-only, BLOCKING FAIL on any drift).

### 2.1 Snapshot semantics

For each enabled spoke in `_aos/projects.yaml` that carries `_aos/definition.yaml`:
- Every `team_NN:` block present in the spoke MUST equal the corresponding hub `team_NN:` block byte-for-byte (modulo trailing whitespace).
- A spoke may carry a **subset** of hub teams — it is not required to carry all hub teams. The subset is determined by the spoke's `team_assignments` plus universal teams.
- A spoke MAY NOT carry a team that does not exist in the hub (ORPHAN — drift).
- A spoke that does not carry `_aos/definition.yaml` at all is SKIPPED (some lifecycle archetypes don't materialize the snapshot).

### 2.2 Enforcement (`validate_aos.sh` Check 47)

- Hub-only (SKIP on spokes — they have no `_aos/projects.yaml`).
- Runs `scripts/check_definition_snapshot_consistency.sh --quiet`.
- PASS if zero drift records.
- FAIL on any drift; reports count + invocation path for the human-readable details.
- Auto-fix is **out of scope** (see §5). FAIL surfaces the drift to team_00 + team_100 for manual remediation.

### 2.3 Drift kinds

| Kind | Meaning |
|---|---|
| `SNAPSHOT_DRIFT` | Spoke carries team_NN but its block content differs from the hub block |
| `ORPHAN` | Spoke carries team_NN that does not exist in hub |
| `PARSE_ERROR` | Spoke `_aos/definition.yaml` is unparseable |

## 3. Consequences

### 3.1 Positive
- **Drift becomes visible.** Today: 106 records hidden. Tomorrow: Check 47 surfaces every regression at the very next `validate_aos.sh` run.
- **Cross-engine integrity preserved.** Iron Rule #1 validators (different engine) now see the same team definitions the builder saw, because both read the same canonical text.
- **Companion pattern to ADR049.** Two of three drift classes are now mechanically detected. The third (per-spoke `forbidden_patterns` drift, etc.) remains a candidate for a future ADR.

### 3.2 Negative / costs
- The audit surfaces 106 existing drift records. These were always there; ADR050 makes them visible. Remediation is a separate WP (manual, per-spoke, with team_00 + team_100 approval). Until remediation, hub `validate_aos.sh` will FAIL Check 47.
- New surface (`scripts/check_definition_snapshot_consistency.sh`) + new check (Check 47) = small ongoing maintenance.
- Detection without auto-fix means a human decision loop sits in the middle. This is **intentional** — see §5.

### 3.3 Risk
- LOW for the detection mechanism. The script is read-only and reports text-slice diffs.
- MEDIUM for the policy of "fail on drift" before bulk remediation lands — hub will be in FAIL state on Check 47 until remediation WP runs. Acceptable: Check 47 is one of 47 checks; the FAIL is informative, not a build-blocker for other work (team_00 may continue work; surface but do not gate on Check 47 alone during the remediation window).

## 4. Implementation summary (delivered 2026-05-25)

| Deliverable | Type | Path |
|---|---|---|
| Drift-detection script | NEW | `scripts/check_definition_snapshot_consistency.sh` (default / `--quiet` / `--json` modes) |
| Hub-only validate check | EDIT | `lean-kit/modules/validation-quality/scripts/validate_aos.sh` → new `check_47()` + wired into execution; banner bumped to "47 checks" |
| Snapshot mirror | EDIT | `_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh` (mirrors canonical edit for hub call path) |
| This ADR | NEW | `governance/directives/ADR050_DEFINITION_SNAPSHOT_LOCKDOWN_v1.0.0.md` |

## 5. Out of scope (explicit non-goals)

- **Auto-fix mechanism.** Regenerating spoke `_aos/definition.yaml` from hub is a *separate decision* requiring team_00 + team_100 sign-off per spoke. Reasons: (a) spoke definition.yaml may legitimately deviate in *which teams it carries* (subset), and an auto-fix tool risks accidentally adding teams not assigned to that spoke; (b) the act of bringing a spoke into sync is itself a governance event (a spoke gets new iron rules, new gate authority text, etc.) that should be reviewed not rubber-stamped. Future WP candidate: `AOS-V4.x-WP-DEFINITION-SNAPSHOT-REMEDIATION`.
- **Spokes that do not carry `_aos/definition.yaml`.** Out of scope here. Some lifecycle archetypes (e.g., CONTENT_SUBSTRATE, certain L0 spokes) may not materialize the snapshot; Check 47 SKIPs them.
- **Drift remediation.** Manual, per-spoke, with team_00 + team_100 approval. Tracked in the follow-up WP above.
- **Auto-trigger after hub team_block edits.** Same reasoning as ADR049 §5 deferral of auto-trigger for sync_derived_registries.sh — Check 47 is the safety net; the editor of `core/definition.yaml` sees the FAIL on the next `validate_aos.sh` run.

## 6. References

- **ADR049** — Registry SSoT Lockdown (companion pattern, applied to `_aos/projects.yaml`).
- **`methodology/AOS_DIRECTORY_CANON_v1.0.0.md`** — binding directory structure; hub vs spoke authority.
- **Audit context:** `_COMMUNICATION/team_200/AOS-V4.4-WP-TAILS-CLEANUP/PLAN_OF_RECORD_2026-05-25_v1.0.0.md` §1 ITEM B2.
- **First drift report:** invocation `bash scripts/check_definition_snapshot_consistency.sh` from the hub on 2026-05-25 surfaced 106 records across 12 spokes.

---

*Decision record — ADR050 Definition Snapshot Lockdown | AOS Hub | 2026-05-25 | STATUS: ACCEPTED (pending team_190 L-GATE_VALIDATE)*
