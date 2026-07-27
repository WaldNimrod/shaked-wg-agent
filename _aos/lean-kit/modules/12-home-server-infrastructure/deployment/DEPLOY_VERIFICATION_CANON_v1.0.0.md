# Deploy Verification Canon

**Module:** 12-home-server-infrastructure / deployment
**Version:** v1.1.1
**Date:** 2026-07-05 (v1.1.0: 2026-07-09 — DV-4 release-asset seeding added by team_100, routed back from team_60; **v1.1.1: 2026-07-17** — DV-1 endpoint/field corrected against live prod + DV-2 scope fix per team_120 GCR; ✅ team_00 co-signed 2026-07-17 (Nimrod, in session — second key on the M12 W7 canon batch) — M12 W7)
**Authority:** team_00 (mandate 2026-07-05) + team_100 (co-ratify at next gov cycle)
**Author/custodian:** team_120 (Ambassador — drift-audit + DOC_CANON); DV-4 authored by team_100 (2026-07-09)
**Origin:** tiktrack prod deploy-pipeline drift, 2026-07-05 (`DRIFT_REPORT_2026-07-05_DEPLOY-PIPELINE-DECOUPLED-HOOK`); DV-4 origin: exit-15 port-canon cold-host gap (agros-insite / tiktrack, 2026-07-08)
**Applies to:** hub + ALL spokes running a long-running service deployed via a git hook / deploy script

> **Ratification status:** DV-1..DV-3 ENACTED under the 2026-07-05 team_00 directive routed to team_120; team_100
> co-ratify stamp pending (additive; no override of existing Iron Rules). A proposal to elevate DV-1 to a full Iron
> Rule (**Iron Rule #16**) is filed as GCR-1 — **team_00 co-signed 2026-07-08** (see
> `DECISION_team_100_M11_CLEANDESK_RULINGS_AND_RATIFICATIONS_2026-07-08` §D); team_120 drafts the numbered rule.
> **DV-4** (release-asset seeding) authored into canon by team_100 **2026-07-09** (verbatim from
> `MSG_team_60_TO_team_100_DV4_ROUTE_BACK_2026-07-08`) — **team_00 co-signed 2026-07-09**
> (`COSIGN_team_00_DV-4_RELEASE_ASSET_SEEDING_2026-07-09`); team_60 CLEARED to resume DV-4.3/DV-4.4 implementation.

---

## Why this exists (the drift it prevents)

A deploy mechanism that **reports success without verifying the served artifact changed** is a silent-drift
generator: prod can lag `main` indefinitely while every signal says "green."

**The 2026-07-05 tiktrack incident:** the bare-repo `post-receive` hook was rewritten to `git reset --hard` a
**working-clone** (`/data/projects/tiktrack`) and curl `/health` → log `DEPLOY OK`. But the live service serves
from a **release symlink** (`tiktrack-api.service` `WorkingDirectory=/opt/tiktrack/current` →
`/opt/tiktrack/releases/<tag>`), updated by a *separate* `deploy-staging.sh`. The hook never touched the served
path. Result: `deploy.log` showed `HEAD is now at 984bd88f` while `/health` returned `git_sha=6ec0b769` on the
**same** push — a **false-positive** `DEPLOY OK`. The served SHA never changed.

**This is not isolated.** team_120's 2026-07-05 fleet audit found the **same two-path fingerprint** on
**agros-insite** (hook pulls `/opt/agros-insite-staging/releases/…`, logs to `/data/projects/agros-insite`, no
state verify — HIGH) and on the **hub** (`aos-api-v5` post-receive targets `/data/projects/agents-os-v5` with no
symlink release mechanism — HIGH). Hook definitions live in-repo at `scripts/deploy_server_hooks.sh`.

---

## DV-1 — Verify a deploy by prod STATE, never by an exit code or a log line (BINDING)

A deploy is **VERIFIED GREEN only when prod state is asserted equal to the intended release**:

1. **Served SHA matches:** the served-SHA field **==** the pushed/expected commit SHA.

   **⚠ On the AOS hub `aos-api-v5` the endpoint is `/api/system/health` and the field is `build_sha`.** Both
   halves matter, and both were wrong in the canon at some point. Verified live against
   `100.125.98.56:8092` on **2026-07-17** (content v1.1.1):

   | Endpoint | Returns |
   |---|---|
   | `/health` | **HTTP 404 — does not exist.** Do not use it; ADR056 v1.0.0 named it. |
   | `/api/health` | `200 {"status":"ok"}` — **no SHA at all** ⇒ by DV-1's own last paragraph, **not DV-1-compliant**. |
   | **`/api/system/health`** | ✅ the DV-1 endpoint — `build_sha` (40-char), `built_at`, `gov_hub_sha`, `schema_version` |

   The field is **`build_sha`**, NOT `git_sha` — a DV-1 check that greps `git_sha` reads **empty** and
   **false-rollbacks** (hit on the 2026-07-12 M11 deploy). `build_sha = AOS_BUILD_SHA env or _git_head()`
   (`build_info.py:8`); with `AOS_BUILD_SHA` unset it is the tree HEAD, so a deploy-tree FF + service restart
   updates it. Also present: `gov_hub_sha` (governance-cache currency).

   Canonical probe:
   ```bash
   curl -s http://<host>/api/system/health | python3 -c 'import sys,json; print(json.load(sys.stdin)["build_sha"])'
   ```
2. **Release symlink matches:** `readlink /opt/<project>/current` **==** the intended `/opt/<project>/releases/<tag>`.

A deploy is **NEVER** declared successful on the basis of:
- ❌ a git hook / ssh **exit code** (0 can mean "hook ran", not "service reloaded new code"),
- ❌ a `"DEPLOY OK"` / `"DEPLOY GREEN"` **log line** emitted by the deploy script itself,
- ❌ a health curl that returns `200` **without** comparing the returned **served-SHA** (an old-but-healthy process
  returns 200 too — that is exactly the false positive above). *(On `aos-api-v5` that means `/api/system/health` →
  `build_sha`. A bare `200` from `/api/health` is the textbook case: it carries no SHA at all.)*

The health endpoint MUST expose the **served SHA** under a documented field name — `build_sha` on `aos-api-v5`,
`git_sha` on the tiktrack-era services — for DV-1 to be checkable. A host whose health endpoint cannot report the
served SHA is **not** DV-1-compliant. **Per host, record which endpoint and which field**; do not assume, and do
not carry `git_sha` forward as a universal — that assumption is what produced the 2026-07-12 false rollback.

## DV-2 — One authoritative deploy mechanism per host (BINDING)

Each host has exactly **one** path that mutates what the service serves: a **release-symlink** mechanism —
`releases/<tag>` checkout → atomic `ln -sfn` flip of `current` → restart → health-verify → **auto-rollback** on
failure (the `deploy-staging.sh` pattern). The bare-repo `post-receive` hook MUST **delegate** to that mechanism
(local source, no external creds) and MUST NOT run a **parallel working-clone reset** (`git reset --hard
/data/projects/<x>`) **as a DEPLOY mechanism**. A working-clone path that the `WorkingDirectory` does not
point at is **deploy** drift by construction.

> **SCOPE — content v1.1.1, 2026-07-17 — BINDING.** *(team_120 GCR `…ADR056_DATA_PROJECTS_IS_AN_API_READ_PATH_v1.0.0`
> item (b) — **ACCEPTED**. ✅ team_00 co-signed 2026-07-17 (Nimrod, in session — second key on the M12 W7 canon batch).)*
>
> This clause forbids a working-clone reset **as a deploy path**. It does **NOT** assert that
> `/data/projects/<x>` is unread, and it does **NOT** license letting that checkout go stale.
> The prior wording — *"that the service does not read"* — is **false on the API host**.
>
> **On waldhomeserver, `/data/projects/<x>` is an ACTIVE READ PATH.** The L0 roadmap endpoint resolves it via
> `server_path` **by explicit design** — *"the API may run on a host where a Mac-only spoke's `local_path` is
> unreachable"* (`l0_project_io.py:38-42`; same fallback `projects_registry.py:81-93`). `server_path` is
> `/data/projects/<x>` for **12 of 14** registry projects.
>
> Both statements were **true for the deploy path they govern** and became false when resolver commit
> `f77f4db` (2026-05-03) gave the directory a **second, unrelated role**. This is a **scope collision, not an
> authoring error** — but its cost was real: the canon told operators to stop refreshing the path the live API
> reads from, and the endpoint then served a stale `active_milestone` for **every** domain (eyalamit **450
> commits behind**; only tiktrack fresh).
>
> **Freshness of the READ path is governed separately and is owned:**
> `DECISION_team_100_L0_ROADMAP_SERVE_PATH_2026-07-16_v1.0.0` (T-1) + **`AOS-V5-M12-WP-L0-READ-PATH-FRESHNESS`
> (W5)**. The read-path class has no freshness rule and no `validate_aos.sh` check today; W5 owns closing that.
>
> **DV-3 blind spot (same root).** The drift fingerprint requires a host referencing **both**
> `/data/projects/<x>` **and** an `/opt/<x>` release. Read-only spokes have **no `/opt` path at all**, so they
> are **structurally invisible** to the audit meant to find exactly this. DV-3 remains correct for the deploy
> class it was written for; the read-path class is W5's.

## DV-3 — Audit the fingerprint on every host (BINDING)

The silent-drift **fingerprint** is: *a host references BOTH a `/data/projects/<x>` working clone AND an
`/opt/<x>/current` (or `releases/`) served symlink, and the hook writes the former while the service reads the
latter.* Every host running a service MUST be audited for it — on initial deploy, after any hook/deploy-script
change, and after any home-server migration. Any committed hook in `scripts/deploy_server_hooks.sh` MUST be
state-verified per DV-1 (readlink + git_sha compare), not exit-code-verified.

## DV-4 — Seed deploy-critical Model-B assets into every release (BINDING)

A release MUST have its **runtime deploy-critical assets** available at deploy time even though they live in the
**git-ignored Model-B cache** (ADR054 C-MB1) — chiefly the port-canon cache (`port_canon_lookup.py` +
`port-registry.yaml`) and any other `_aos/lean-kit/` runtime asset. A `git clone/fetch/checkout` never carries them
(they are git-ignored) and MUST NOT be made to (un-ignoring them violates ADR054 C-MB1 / `validate_aos.sh` Check 61
on the spoke). Therefore:

- **DV-4.1 — Seed, never checkout.** Release-creation SEEDS these assets into the release from the live host cache.
  A deploy MUST NOT rely on a VCS operation to deliver them (it never will — they are ignored), and MUST NOT
  un-ignore them.
- **DV-4.2 — Fail loud.** A deploy pre-flight that cannot resolve a required canon asset FAILS LOUD (non-zero,
  named) — never a silent skip, never a hardcoded default (that is the DV-1 anti-pattern team_60 found in agros's
  `|| echo '8284'`).
- **DV-4.3 — Cold-host bootstrap.** The self-heal pattern (seed from the most-recently-populated sibling release)
  covers **recurring** deploys but NOT a **cold host with zero prior releases** (confirmed: agros-insite's
  `/opt/agros-insite/` real state). DV-4 therefore REQUIRES a **persistent host-level cache path independent of any
  release's lifecycle** — seeded once by `aos_governance_bootstrap.sh` at a fixed location and refreshed on
  `aos_sync_all`, so every deploy (including the first) has a source — OR, where that is not yet in place, an
  explicit one-time manual seed step in the first-deploy runbook. Self-heal is the recurring path; the persistent
  host cache is the cold-start path. Both are DV-4.
- **DV-4.4 — Reference-model pattern (portable, not a per-spoke hack — "canon reads the same for every domain").**
  The canonical self-heal shape is lifted VERBATIM into the reference `deploy-staging.sh`: (a) if the target's own
  cache is missing, scan sibling releases for the most-recently-populated `_aos/lean-kit/.../deployment/` and
  `cp -a` it in (git-ignored destination, never `git add`); (b) forward-seed the just-checked-out release too
  (breaks the recurrence where only pre-flip `current` got fixed); (c) fail loud on total absence; (d) idempotent
  guard (no-op when present). Ship a `--dry-run` (self-heal + fetch + reachability, exit before any DB/service
  mutation) for rehearsal.

---

## Reference implementation (the positive model)

`TikTrack-Phoenix_AOSProject/scripts/deploy-staging.sh` (v1.5.0) is the canonical pattern:
- `_PREV_RELEASE=$(readlink /opt/tiktrack/current)` — capture state **before** mutation;
- checkout `/opt/tiktrack/releases/<TAG>`; atomic `ln -sfn <TARGET> /opt/tiktrack/current`;
- 15s warmup + 5×3s health-retry loop (not a single sleep+curl);
- **auto-rollback**: on health fail, re-point `current` → `_PREV_RELEASE`, restart, re-verify — exit `21`
  (rolled back OK) / `22` (rollback also failed), never a false `0`;
- `RELEASE_PROCEDURE.md` verifies by state (readlink + served SHA), not by the hook exit.

The **DV-4 reference-model** (release-asset self-heal + cold-host seed) is implemented in `deploy-staging.sh` v1.6.0
— under review as PRs [agros-insite #2](https://github.com/WaldNimrod/agros-insite/pull/2) +
[TikTrack #105](https://github.com/WaldNimrod/TikTrack-Phoenix_AOSProject/pull/105) (team_100 N4 review → team_60 merge).

Spokes SHOULD adopt this shape. New projects: fold DV-1..DV-4 into `NEW_PROJECT_STANDARD.md` deploy setup.

---

## Propagation

1. Hub SSoT = this file. Snapshots to spokes via `aos_sync_all.sh` (module 12 deployment).
2. Each spoke's `RELEASE_PROCEDURE.md` MUST state the DV-1 state-verify step (readlink + git_sha) explicitly.
3. team_60 owns the server-side remediation of the hooks flagged HIGH by the 2026-07-05 audit
   (agros-insite, hub `aos-api-v5`) + the tiktrack legacy-hook disable/retarget.
4. Advisory `validate_aos.sh` check (future WP): flag a committed `deploy_server_hooks.sh` hook that lacks a
   readlink/git_sha state-verify → SKIP:WARN.

---

*team_120 (custodian) + team_00 (mandate) | Deploy Verification Canon v1.0.0 | 2026-07-05 | origin: tiktrack deploy drift*
