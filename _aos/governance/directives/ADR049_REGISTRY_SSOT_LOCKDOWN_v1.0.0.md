# ADR049 — Registry SSoT Lockdown (`_aos/projects.yaml` as sole canonical, drift-enforced)

**Status:** ACCEPTED
**Date:** 2026-05-25
**Authors:** team_200 (Cowork — implementation) on team_00 directive; ratified by team_00 (Principal)
**Validated by:** team_190 (Senior Constitutional Validator) — L-GATE_VALIDATE re-pass pending
**Supersedes:** none (clarifies existing `_aos/projects.yaml` SSoT role; eliminates competing surfaces)
**Related:** ADR034 (Data Authority — DB SSoT), ADR040 (Governance Authority Lockdown), Iron Rules #7 (API-only mutations), #8 (Port canon)

---

## 1. Context

Audit 2026-05-25 (triggered by a faulty nimrod-bio GCR for team_35 propagation) discovered **5 surfaces** holding project/spoke registry information:

| # | Surface | Reality |
|---|---|---|
| 1 | `_aos/projects.yaml` | Functionally canonical. Read by 7+ code paths (`projects_registry.py`, `dashboard_routes.py`, `team_messaging.py`, `health.py`, `dashboard_service.py`, `prompts_activation.py`, `aos_sync_all.sh`). |
| 2 | `_aos/project_identity.yaml.managed_projects` | **Zero code readers.** Template-set at hub creation; never refreshed. Was stale (3 of 12 spokes listed). |
| 3 | `CLAUDE.md` prose lists (2 sections) | Human/AI session-startup; never refreshed. Was stale. |
| 4 | `lean-kit/.../msg_preflight.sh` Tier 3 case block | Code-level fallback used only when Tier 1 (cache) + Tier 2 (live `/api/projects`) both unavailable. Was missing 3 spokes. |
| 5 | DB `projects` table | Auto-mirrored from `_aos/projects.yaml` when DB online; not a drift source. Out of scope. |

**Drift mechanism:** `/AOS_project-init` writes to surface #1 only. Surfaces #2-#4 have no update path tied to spoke creation. They were set at hub bootstrap and forgotten.

**Why this matters:**
- #4 (`msg_preflight.sh` Tier 3) silently misroutes MSGs when both cache and API are unavailable — a real operational risk in offline + cold-cache scenarios.
- #2 and #3 mislead human/AI readers (the closure artifact for the nimrod-bio GCR documents exactly this confusion).

## 2. Decision

`_aos/projects.yaml` is the **sole canonical registry**. All other surfaces are either eliminated or mechanically derived from it. Drift is enforced by `validate_aos.sh` Check 46 (hub-only, BLOCKING FAIL on drift).

### 2.1 Surface dispositions

| Surface | Disposition |
|---|---|
| `_aos/projects.yaml` | **CANONICAL SSoT.** No change. |
| `_aos/project_identity.yaml.managed_projects` | **DEPRECATED + REMOVED** from hub file and template. No code reads it; removed without replacement. |
| `CLAUDE.md` prose lists | **COLLAPSED** to a single pointer line referencing `_aos/projects.yaml`. The duplicate hand-maintained lists are gone. |
| `msg_preflight.sh` Tier 3 | **AUTO-GENERATED** from `_aos/projects.yaml` by `scripts/sync_derived_registries.sh`. Wrapped in `# BEGIN GENERATED ... # END GENERATED` markers. Hand edits inside markers will be overwritten. |
| DB `projects` table | Unchanged — auto-mirrored from projects.yaml per ADR034. |

### 2.2 Enforcement

`validate_aos.sh` **Check 46** (hub-only; SKIP on spokes that lack `_aos/projects.yaml`):
- Runs `scripts/sync_derived_registries.sh --check`.
- PASS if all derived surfaces match a fresh derivation from `_aos/projects.yaml`.
- FAIL if any derived surface drifts.
- Fix instruction printed: `bash scripts/sync_derived_registries.sh`.

### 2.3 Pattern-derivation algorithm (msg_preflight.sh Tier 3)

For each enabled project entry in `_aos/projects.yaml`:
1. Always include `*<id>*` as a match pattern (output value = `id`).
2. If `repo` is set (e.g., `WaldNimrod/SmallFarmsAgents`): include `*<basename>*` and `*<basename_lower>*`.
3. If `local_path` basename differs from above: include `*<basename>*` (with spaces converted to `*` for glob).

Output sorted: hub entry (type `aos_project`) first, then alphabetical by id. The fallback `*)` arm (defaulting to `agents-os`) is preserved AFTER the generated case entries.

## 3. Consequences

### 3.1 Positive
- **Zero documentation drift possible** — duplicate lists eliminated.
- **Zero code-fallback drift possible** — Check 46 blocks commits that introduce it.
- **Single edit point** — adding a spoke = `/AOS_project-init` writes to `projects.yaml`; running `sync_derived_registries.sh` propagates to msg_preflight.sh.
- **Reduced cognitive load** — humans/agents see one canonical list, not three.

### 3.2 Negative / costs
- Anyone wanting a human-readable spoke list must read `_aos/projects.yaml` (CLAUDE.md provides a one-liner `python3 -c ...`).
- New surface (`scripts/sync_derived_registries.sh`) + new check (Check 46) = small ongoing maintenance.
- The `managed_projects` field deprecation is a minor schema change. Existing spokes' `project_identity.yaml` still have `managed_projects: []`; leave alone (harmless empty list). New projects via the updated template will not have the field.

### 3.3 Risk
- LOW. The sync script is idempotent + tested for drift detection (induced fake drift → Check 46 FAIL → revert → PASS). The Check 46 SKIP path on spokes is safe — spokes don't carry the registry.

## 4. Implementation summary (delivered 2026-05-25)

| Phase | Artifact | Status |
|---|---|---|
| Phase 1 | Removed `managed_projects` from `_aos/project_identity.yaml` + template | ✅ |
| Phase 1 | Collapsed CLAUDE.md duplicate listings into single pointer | ✅ |
| Phase 2 | `scripts/sync_derived_registries.sh` (idempotent; `--check` mode for CI) | ✅ |
| Phase 2 | `msg_preflight.sh` Tier 3 wrapped in BEGIN/END markers, regenerated from projects.yaml | ✅ |
| Phase 3 | `validate_aos.sh` Check 46 — hub-only drift gate | ✅ |
| Phase 5 | This ADR | ✅ |

## 5. Deferred (follow-up)

**Phase 4 (auto-trigger)** — explicitly deferred to a follow-up WP. Risk-weighted decision: wiring `project_create.py` (the POST /api/projects/create handler) to run `sync_derived_registries.sh` as a subprocess after every successful project creation adds a surface that could regress request handling. Without Phase 4, a human runs `/AOS_project-init` → adds spoke to `projects.yaml` → must remember to run `sync_derived_registries.sh`. If they forget, the very next `validate_aos.sh` (mandatory hub startup step) FAILs Check 46 and prints the fix command. Drift cannot reach commit. Acceptable trade — Check 46 is the safety net.

Follow-up WP (`AOS-V4.x-WP-REGISTRY-SYNC-AUTOTRIGGER`) should:
- Wire `project_create.py` to call sync script post-creation.
- Wire `aos_sync_all.sh` phase 0.4 pre-flight to call sync script.
- Document in `/AOS_project-init` skill output.

## 6. Out of scope

- **Team definition drift** (hub `core/definition.yaml` vs spoke `_aos/definition.yaml` snapshots) — same problem class, different solution path. Separate WP.
- **Per-spoke `forbidden_patterns` drift** — per-spoke config, not registry SSoT.
- **DB↔projects.yaml** — already governed by ADR034 R7.

## 7. Rejected alternatives

**Option B (auto-derive all surfaces with markers).** Kept all surfaces but wrapped each in BEGIN/END markers + sync script regenerates all. Rejected: more surfaces = more maintenance + more places where humans see auto-edits and get confused. Option A eliminates 2 surfaces entirely; only 1 remains, and it's a code-level fallback (humans rarely read it).

**Option C (status quo + advisory warnings).** Document SSoT precedence + add non-blocking advisory check. Rejected: this is what was producing drift. Will recur.

## 8. References

- Audit trail: `_COMMUNICATION/team_100/PROPOSAL_REGISTRY_SSOT_LOCKDOWN_2026-05-25_v1.0.0.md`
- Trigger context: `_COMMUNICATION/team_190/MANDATE_AOS-HUB-2026-05-25-REGISTRY-HYGIENE-AND-TEAM-35-ACTIVATION_L-GATE_VALIDATE_v1.0.0.md`
- Iron Rule corollary (no new Iron Rule introduced): this is a derived-state-cannot-drift principle that strengthens Iron Rule #7 (API-only mutations) and Iron Rule #8 (port canon SSoT).

---

*Decision record — ADR049 Registry SSoT Lockdown | AOS Hub | 2026-05-25*
