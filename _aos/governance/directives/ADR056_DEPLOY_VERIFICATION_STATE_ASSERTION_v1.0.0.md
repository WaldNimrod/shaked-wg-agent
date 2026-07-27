---
id: ADR056
title: Deploy Verification by Prod-State Assertion — DV-1..DV-4 binding + DV-1 elevated to Iron Rule #16
status: LOCKED
version: v1.0.1                 # v1.0.1 = ERRATA ONLY (see the ERRATA block). No normative clause changed.
date: 2026-07-10
errata_date: 2026-07-17
authors: [team_120]
cosigned: [team_00, team_100]   # GCR-1 co-signed 2026-07-08 (DECISION_team_100_M11_CLEANDESK_RULINGS_AND_RATIFICATIONS_2026-07-08 §D)
errata_cosigned: [team_00, team_100]   # ✅ team_00 co-signed 2026-07-17 (Nimrod, in session — second key on the M12 W7 canon batch). v1.0.1 errata is NORMATIVE.
errata_source:
  - _COMMUNICATION/team_120/GOVERNANCE_CHANGE_REQUEST_ADR056_DATA_PROJECTS_IS_AN_API_READ_PATH_v1.0.0.md   # E2 — ACCEPTED
  - live production probe http://100.125.98.56:8092/api/system/health, 2026-07-17                          # E1 — build_sha, not git_sha
work_package: AOS-V5-M12-WP-L0-CANON-RECONCILIATION   # W7
scope: AOS-hub + ALL spokes running a long-running service deployed via a git hook / deploy script
supersedes: none (additive — no prior ADR or Iron Rule overridden)
origin: DRIFT_REPORT_2026-07-05_DEPLOY-PIPELINE-DECOUPLED-HOOK (tiktrack) + team_120 2026-07-05 fleet audit
canon: lean-kit/modules/12-home-server-infrastructure/deployment/DEPLOY_VERIFICATION_CANON_v1.0.0.md   # content v1.1.0 (incl. DV-4)
---

# ADR056 — Deploy Verification by Prod-State Assertion

## Context

A deploy mechanism that **reports success without verifying the served artifact changed** is a silent-drift
generator: prod can lag `main` indefinitely while every signal reads "green."

**The 2026-07-05 tiktrack incident.** The bare-repo `post-receive` hook was rewritten to `git reset --hard` a
**working clone** (`/data/projects/tiktrack`) and curl `/health` → log `DEPLOY OK`. But the live service serves from
a **release symlink** (`WorkingDirectory=/opt/tiktrack/current` → `/opt/tiktrack/releases/<tag>`), flipped by a
*separate* `deploy-staging.sh`. The hook never touched the served path: `deploy.log` printed `HEAD is now at 984bd88f`
while `/health` returned `git_sha=6ec0b769` on the **same** push — a false-positive `DEPLOY OK`; the served SHA never
changed. team_120's 2026-07-05 fleet audit found the **same two-path fingerprint** on **agros-insite** and on the
**hub** `aos-api-v5` post-receive (both HIGH). This is exactly the class of silent, self-reporting failure the Iron
Rules exist to foreclose.

## Decision

1. **`DEPLOY_VERIFICATION_CANON` (DV-1..DV-4) is BINDING** for the hub and every spoke running a service deployed via
   a git hook / deploy script. DV-1 (state-assert), DV-2 (one authoritative mechanism per host), DV-3 (audit the
   fingerprint), DV-4 (seed deploy-critical Model-B assets into every release; fail loud; cold-host persistent cache;
   portable reference-model) are the normative text. Canon file:
   `lean-kit/modules/12-home-server-infrastructure/deployment/DEPLOY_VERIFICATION_CANON_v1.0.0.md` (content v1.1.0).

2. **DV-1 is elevated to a numbered constitutional Iron Rule — Iron Rule #16.** Inserted into
   `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` (positional item 10) and the hub `CLAUDE.md` Iron Rules list. This ADR
   is its decision record; the Iron Rule cites ADR056 back.

**Iron Rule #16 — canonical text (as inserted):**

> **Deploy verification by prod STATE.** A deploy is GREEN only when prod state is asserted equal to the intended
> release — the served-SHA field returned by the host's health endpoint **==** the pushed/expected commit SHA **AND**
> `readlink /opt/<project>/current` **==** the intended `/opt/<project>/releases/<tag>`. A git-hook / ssh **exit
> code**, a `"DEPLOY OK"`/`"DEPLOY GREEN"` **log line**, or a `200` **without** a served-SHA compare is **never**
> sufficient (an old-but-healthy process also returns 200). Each host has exactly **one** authoritative deploy
> mechanism — a release-symlink flip (`ln -sfn … current`) with health-verify + auto-rollback; the bare-repo
> `post-receive` hook MUST **delegate** to it and MUST NOT run a parallel working-clone reset (`git reset --hard
> /data/projects/<x>`) **as a DEPLOY mechanism**. Deploy-critical Model-B assets (port-canon cache et al.) are
> **seeded** into each release from the live host cache — never delivered by a VCS checkout, never un-ignored
> (DV-4 / ADR054 C-MB1 / Check 61). Every host is audited for the two-path drift fingerprint on initial deploy, after
> any hook/deploy-script change, and after any home-server migration. Canon:
> `…/deployment/DEPLOY_VERIFICATION_CANON_v1.0.0.md` (DV-1..DV-4). Decision record: ADR056.

### ERRATA — v1.0.1, 2026-07-17 (team_100, M12 W7 · AOS-V5-M12-WP-L0-CANON-RECONCILIATION)

Three factual corrections. Each was **true when written** and became false as the system moved underneath it.
None weakens DV-1..DV-4; all three make them *executable as written*, which they were not.

**E1 — the endpoint and the field.** The decision text above originally said `curl <host>/health` → `git_sha`.
Verified against live production `100.125.98.56:8092` on 2026-07-17:

| Endpoint | Returns |
|---|---|
| `/health` | **HTTP 404** — the endpoint does not exist |
| `/api/health` | `200 {"status":"ok"}` — **no SHA field**; by this ADR's own `:60-61` it is **not DV-1-compliant** |
| **`/api/system/health`** | **the DV-1 endpoint** — carries the served SHA in field **`build_sha`** (`build_info.py:8`), plus `built_at`, `schema_version`, `gov_hub_sha` |

**The field is `build_sha`, not `git_sha`.** A DV-1 check that reads `git_sha` gets an empty value, compares it
against the pushed SHA, and evaluates **false → spurious rollback**. Canonical DV-1 probe:

```bash
curl -s http://<host>/api/system/health | python3 -c 'import sys,json; print(json.load(sys.stdin)["build_sha"])'
# MUST equal the pushed SHA. And: readlink /opt/<project>/current == the intended releases/<tag>.
```

`AOS_BUILD_SHA` unset falls back to `_git_head()`, so a fast-forward + restart does update it.
*(Origin: M11 — a DV-1 check reading `git_sha` returned empty→false. The canon has said `git_sha` throughout.)*

**E2 — `/data/projects/<x>` is NOT universally unread.** *(team_120 GCR
`GOVERNANCE_CHANGE_REQUEST_ADR056_DATA_PROJECTS_IS_AN_API_READ_PATH_v1.0.0`, item (a) — ACCEPTED.)*
The DV-2 clause said the working clone is one *"the service never reads."* **False on the API host.**
`l0_project_io.py:38-42` resolves the L0 roadmap from exactly that path via `server_path`, by explicit design —
"the API may run on a host (waldhomeserver) where a Mac-only spoke's `local_path` is unreachable." The same
fallback exists at `projects_registry.py:81-93`, and `server_path` is `/data/projects/<x>` for **12 of 14**
projects.

> **Scoped restatement (binding).** DV-2 forbids a working-clone reset as a **deploy path** for a
> release-symlink host. It does **NOT** assert that `/data/projects/<x>` is unread, and it does **NOT** license
> letting the API's read checkout go stale. On the API host that directory is an **ACTIVE READ PATH**. Freshness
> of the READ path is governed separately — see `DECISION_team_100_L0_ROADMAP_SERVE_PATH_2026-07-16_v1.0.0`
> (T-1) and `AOS-V5-M12-WP-L0-READ-PATH-FRESHNESS` (W5), which owns it.

Both statements were true for the *deploy* path they govern; they became false when resolver commit `f77f4db`
(2026-05-03) gave the same directory a second, unrelated role. **This is a scope collision, not an authoring
error** — and its cost was real: the L0 endpoint served a stale `active_milestone` for every domain, with
eyalamit **450 commits behind** and only tiktrack fresh.

**E3 — the DV-3 audit trigger is blind to exactly this class.** The drift fingerprint (`:71`) requires a host
referencing **both** `/data/projects/<x>` **and** an `/opt/<x>` release. Read-only spokes have **no `/opt` path at
all** — so they are structurally invisible to the audit meant to find them. **W5 owns the freshness rule for the
read-path class; DV-3's fingerprint remains correct for the deploy class it was written for.**

## Consequences

- A host whose `/health` cannot report the served `git_sha` is **not DV-1-compliant** — the health endpoint MUST
  expose `git_sha` (or an equivalent build id) for the rule to be checkable.
- The hub `aos-api-v5` post-receive (no symlink release mechanism, targets `/data/projects/agents-os-v5`) and
  agros-insite's hook are pre-existing HIGH findings that MUST be remediated to DV-1 (team_60 / team_99; register tail
  C1 — the top M11 deploy blocker).
- New projects: `NEW_PROJECT_STANDARD.md` deploy setup folds DV-1..DV-4 into first-deploy.

## Enforcement (staged)

Additive; no existing Iron Rule is overridden. Enforcement starts **advisory** — a `validate_aos.sh` `SKIP:WARN`
check flagging a committed `deploy_server_hooks.sh` hook that lacks a `readlink`/`git_sha` state-verify (future
validation-quality WP) — and hardens to FAIL once the fleet is compliant.

## References

- `lean-kit/modules/12-home-server-infrastructure/deployment/DEPLOY_VERIFICATION_CANON_v1.0.0.md` — DV-1..DV-4 (content v1.1.0)
- `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` — Iron Rule #16 (positional item 10)
- `governance/directives/ADR054_GOVERNANCE_DISTRIBUTION_MODEL_B_v1.0.0.md` — C-MB1 (git-ignored cache; DV-4 seed rationale)
- `_COMMUNICATION/team_120/GCR_team_120_DEPLOY-CANON-AND-TEAM191-DISSOLUTION_2026-07-05_v1.0.0.md` — GCR-1 (source proposal)
- `_COMMUNICATION/team_100/DECISION_team_100_M11_CLEANDESK_RULINGS_AND_RATIFICATIONS_2026-07-08_v1.0.0.md` §D — co-sign
- Origin drift: `DRIFT_REPORT_2026-07-05_DEPLOY-PIPELINE-DECOUPLED-HOOK` (tiktrack) + team_120 2026-07-05 fleet audit

---
*team_120 (author, Ambassador — drift-audit + DOC_CANON custodian) · team_00 + team_100 co-signed 2026-07-08 · ADR056 · 2026-07-10*
