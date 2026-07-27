# Cursor Cloud Environment — Per-Domain Fill-In Template
# AOS-V5-M11-WP-CURSOR-CLOUD-ENVIRONMENT (A6) | Owner: team_60 (per-domain DevOps operator) |
# Authority: hub ships this template ONCE; each domain fills its own copy — not a silent defer.

## What this is

The hub `cursor-cloud` environment (new session `environment` value, sibling of `cowork` —
`methodology/AOS_OPERATING_ENVIRONMENT_v1.0.0.md` §3) is defined ONCE, hub-side, and propagated to
every domain (`aos_sync_all.sh`). But the actual cursor-cloud VM per domain needs domain-specific
fill-ins: DB port/creds, dependency-pinning policy, egress/secrets, and test policy. This doc is the
checklist; `.cursor/environment.json.template` (repo root) is the paired machine-readable template.

**Do NOT silently defer these fill-ins.** Copy this file into the domain repo (or fill the hub's own
copy for the hub-first pilot), answer every section, and keep it alongside the domain's
`.cursor/environment.json`.

## 1. DB port + credentials

Every domain's cursor-cloud VM runs its OWN throwaway/dev Postgres for isolated testing. It is
**NEVER** the same instance as the authoritative hub DB — the A1 guard
(`core/modules/management/db.py::is_authoritative_hub_db` / `is_authoritative_hub_connection`)
treats any Postgres that is not the known hub host (`100.125.98.56` / `waldhomeserver`, or the
loopback address ONLY when the running process's own hostname is the hub) as **non-authoritative**,
regardless of what this VM's local DB reports.

| Domain | Cursor-cloud VM DB target | User/DB name | Notes |
|---|---|---|---|
| agents-os (hub) | `127.0.0.1:5434` (dev pattern) | `aos`/`aos_v5_dev` | Fill in the ACTUAL cursor-cloud VM port if it differs from the Mac dev default — a cloud VM is a fresh machine, not a clone of the Mac's `core/.env`. |
| TikTrack | `127.0.0.1:5432` (dev pattern) | TBD | Routed to TikTrack team_100/team_00 — their own decision, not the hub's (per LOD300 §2 item 7 / RULING_team_120_CURSOR_CLOUD_ENV_CANON §"Secrets/egress"). |
| *(new domain)* | | | |

DB **start** may be part of `.cursor/environment.json`'s `install`/`start` steps (starting the
service is infra bootstrap, not a data mutation). DB **migrate + seed** are **runtime** steps
documented in `AGENTS.md`, invoked explicitly by the agent/operator — never baked into the
environment image (team_00/team_100 ruling, 2026-07-05).

## 2. Floating vs. pinned requirements

- **Pinned (direct deps):** `core/requirements.lock` (hub convention) — `pip install -r
  core/requirements.lock` in the `install` step. Regenerate the lock when `requirements.txt` changes;
  do not hand-edit pins inside `environment.json`.
- **Floating (transitive deps):** left unpinned by design — the lock only pins direct dependencies
  (see `core/requirements.lock` header comment).
- TikTrack equivalent: prefer pinning `api/requirements.txt` for parity (per the ruling's disposition
  on the "pytest-asyncio / undeclared test deps" ask).

## 3. Egress / secrets manifest

List every secret this domain's cursor-cloud env needs, provisioned via the **Cursor Cloud Agent
Secrets panel** (redacted type — never committed to git, never placed in `environment.json` or
`AGENTS.md`), and every external network egress target required.

| Domain | Secrets | Egress targets | Notes |
|---|---|---|---|
| agents-os (hub) | none required for this WP's build | none beyond standard package registries (PyPI) | `CURSOR_API_KEY` for headless `cursor-agent` cross-engine auth is tracked in `engines.yaml` §5 as an open item (D3) — **out of scope for this WP's build**. |
| TikTrack | JWT secret, ENCRYPTION key, `DATABASE_URL`, `ALPHA_VANTAGE` API key | market-data provider allowlist (Yahoo Finance / Alpha Vantage endpoints) | Routed to TikTrack team_100/team_00 — their decision, not the hub's. |
| *(new domain)* | | | |

## 4. Test policy

- Note any test-suite dependency this VM image needs beyond `core/requirements.lock` (e.g.
  `pytest-asyncio`, Playwright browsers) — add to a test-extras manifest, don't silently assume it's
  present.
- Any test that assumes a **Mac-only `local_path`** (hardcoded `/Users/...` paths, macOS-only
  tooling) must be skipped or parameterized off this VM — a cursor-cloud VM is Linux, not the Mac.
  Do not let such a test silently fail or silently pass for the wrong reason; mark it explicitly.

## 5. References

- `.cursor/environment.json.template` (repo root) — the paired machine-readable template (Cursor
  Cloud Agent schema: `snapshot` | `build` | `install` | `start` | `terminals`).
- `AGENTS.md` (repo root) — runtime steps (DB start/migrate/seed, validate) live here, not in the
  environment image.
- `methodology/AOS_OPERATING_ENVIRONMENT_v1.0.0.md` §3 — the `cursor-cloud` environment taxonomy row.
- `core/modules/management/db.py` — the A1 authoritative-hub-DB guard this environment must respect.
- `governance/directives/ADR034_ADDENDUM_R8_OFFLINE_CHANGELOG_PROTOCOL_v1.0.0.md` — the offline
  structured-mutation path (`PENDING_DB_SYNC.yaml`) this environment uses instead of a direct
  non-authoritative DB write.
- `_aos/work_packages/AOS-V5-M11-WP-CURSOR-CLOUD-ENVIRONMENT/` — full WP design + reconciliation.
