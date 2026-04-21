---
standard: 11.2
id: multi-project-docker
title: Multi-Project Docker Workstation
version: 1.2.0
date: 2026-04-20
origin: SmallFarmsAgents domain (identified issue)
canonical_owner: Team 100 (Chief System Architect)
applies_to: Every AOS-managed project that runs Docker services locally
---

# AOS Standard 11.2 — Multi-Project Docker Workstation

## Policy

Every repository that runs local Docker services **must** publish **fixed, version-controlled host ports** for those services.

- Port values are defined in committed files (`docker-compose.yml`, `.env.example`, CLI defaults).
- Each project documents its ports in one canonical place: a table in their troubleshooting doc or README, plus their `.env.example`.
- **Port assignments are registered in this document.** No new port may be used without updating the registry below.
- Ad-hoc port changes without updating the docs break teammates, CI, and QA evidence.

## Port Priority Rule

**TikTrack is the primary project — its port assignments are immutable.**
All other projects yield when a conflict with TikTrack exists.
For conflicts between non-TikTrack projects: the established project keeps its port; the newer project re-assigns.

## AOS Multi-Project Port Registry

**This table is a human-readable summary. The authoritative SSoT is `port-registry.yaml` v2.2.0.**

### Port bands

| Band | Range | Purpose |
|------|-------|---------|
| postgres_db | 5432–5499 | Project Postgres ports (dev base; staging +100; prod +200) |
| web_api | 8080–8499 | HTTP listeners — UI, API, dashboard, tooling |
| mysql_host | 3307–3399 | MySQL/MariaDB Docker host-mapped ports |
| cache_store | 6370–6499 | Redis/cache Docker host-mapped ports |
| admin_utility | 5001–5099 | Flask admin, misc UI |

**Forbidden:** 0–1023 (privileged), 3306 (MySQL default), 5000 (macOS AirPlay), 6379 (Redis default), 7000–7001 (macOS AirPlay), ephemeral ranges.

### Canonical port assignments (dev base)

| Project | Service | Host Port | Container Name | Notes |
|---------|---------|-----------|----------------|-------|
| TikTrack | PostgreSQL | **5432** | `tiktrack-phoenix-postgres-dev` | IMMUTABLE |
| TikTrack | API (FastAPI) | **8082** | — | IMMUTABLE |
| TikTrack | Frontend (Vite) | **8080** | — | IMMUTABLE |
| agents-os | PostgreSQL | **5434** | `aos-postgres-dev` | |
| agents-os | API (uvicorn) | **8090** | — | |
| agents-os | Dashboard static | **8099** | — | |
| SmallFarmsAgents | PostgreSQL | **5433** | `oma-postgres` | waldhomeserver + mac_local |
| SmallFarmsAgents | Admin UI (Flask) | **5001** | — | |
| SmallFarmsAgents | Static viewer | **8081** | — | |
| HobbitHome | WordPress (Apache) | **8083** | `hobbithome-wp` | waldhomeserver + mac_local |
| HobbitHome | MySQL 8 | **3308** | `hobbithome-db` | |
| EyalAmit.co.il-2026 | WordPress | **8088** | `local-wordpress-1` | mac_local only |
| EyalAmit.co.il-2026 | Redis | **6380** | — | mac_local only |
| wordpress-dev | WordPress | **8089** | `wordpress-dev` | mac_local sandbox |
| wordpress-dev | MySQL | **3307** | `wordpress-mysql` | mac_local sandbox |
| wordpress-dev | phpMyAdmin | **8091** | `wordpress-phpmyadmin` | mac_local sandbox |
| wordpress-dev | Redis | **6381** | `wordpress-redis` | mac_local sandbox |

**Reserved / do not use on any host or environment:** 5432 · 8080 · 8081 · 8082 · 8090 (and all environment offsets thereof).

## Per-Project Requirements

Every project with Docker services must maintain all four of the following:

1. **`docker-compose.yml`** with explicit `ports:` mapping and `container_name:` set to a unique value.
2. **`.env.example`** with the canonical `DATABASE_URL` (or equivalent) using the registered host port.
3. **A port table** in `documentation/` or README (the SmallFarmsAgents `DOCKER_SHARED_WORKSTATION.md` is the reference model).
4. **`COMPOSE_PROJECT_NAME`** set in `docker-compose.yml` or `.env` to namespace Docker networks and volumes.

## Registering a New Project

When a new project joins AOS governance and introduces Docker services:

1. Check this registry for all currently assigned ports.
2. Choose a port in an unallocated range (next available in the 543x / 808x ranges).
3. Update this document with the new row.
4. Create the project-local troubleshooting doc with the port table.
5. Commit both changes (registry + project doc) in the same commit.

## Conflict Resolution Protocol

If two projects are found to use the same host port:

1. Identify which project has **TikTrack** priority (TikTrack always wins).
2. If TikTrack is not involved: the project with the earlier AOS milestone assignment keeps its port.
3. The yielding project updates: `docker-compose.yml` ports binding, `.env.example`, all `DATABASE_URL` references in config files and IDE settings.
4. Update this registry.
5. Document the change with date in the "Notes" column.

## Diagnostics

Check who holds a port:
```bash
lsof -nP -iTCP:<port> -sTCP:LISTEN
```

List all running containers and their port bindings:
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

Check for container name collisions:
```bash
docker ps -a --format "{{.Names}}" | sort
```

## Project-Local Documents

Each project maintains its own instance of this standard, aligned with the canonical registry above:

| Project | Local document |
|---------|---------------|
| SmallFarmsAgents | `documentation/08-troubleshooting/DOCKER_SHARED_WORKSTATION.md` |
| TikTrack | `AGENTS.md` §Multi-Project Docker Workstation Protocol |
| agents-os | `docker-compose.yml` comments + this document |
| HobbitHome | `docs/DOCKER_PORTS.md` |

---

## Appendix A — Port canon v2.2.0 (tiered environments + cross-env reservation)

Port-registry canon history:
- **v2.0.0** (2026-04-20): tiered per-host, per-environment — `hosts[]` + `projects[].instances[]`
- **v2.1.0** (2026-04-20): SSH key, HobbitHome mac_local, system_ports allowlist, port_range_policy bands
- **v2.2.0** (2026-04-20): R10 cross-env reservation rule, cache_store band, EyalAmit.co.il-2026, wordpress-dev, SFA mac_local; legacy retired; TikTrack postgres corrected to canon 5432

### Canonical environment offsets

| Environment | Offset | Example (TikTrack api=8082) |
|---|---|---|
| dev        | **+0**   | 8082 |
| staging    | **+100** | 8182 |
| production | **+200** | 8282 |
| qa         | **+300** | 8382 |

Rule: a project that registers any env implicitly **reserves all four offsets**
across its `base_triplet`. Cross-project assignments within reserved offsets are FORBIDDEN.
Enforced by `validate_aos.sh` Check 24 v2.

### Binding rules (summary)

| Rule | Statement |
|------|-----------|
| R1 | Every long-running listener MUST be registered before first start |
| R2 | Start scripts MUST pre-flight against the instances[] entry; fail fast if missing or held |
| R3 | Never silently bump to an unregistered port |
| R4 | Canon edits require joint team_60 + team_100 + team_00 sign-off |
| R5 | validate_aos.sh Check 24 enforces schema, duplicates, offset rule, reality-diff |
| R6 | Every deploy-spec MUST declare `env:` explicitly and resolve ports via canon lookup |
| R7 | No host runs an unregistered listener beyond one validate_aos cycle |
| R8 | `project_id` is immutable; display names may change freely |
| R9 | Registry scope = listeners only; outbound-only clients are NOT registered |
| **R10** | **Cross-env reservation: a port assigned to any project in any environment is RESERVED globally — no other project may bind it on any host or env, even if the original project has no instance there** |

### SSoT-no-grandfathering (Team 00 directive 2026-04-20)

> "הקאנון חייב להיות מקור האמת וכל הסביבות מחוייבות אליו."

- Every listener on every registered host MUST match a `projects[].instances[]` entry.
- Unregistered listeners = FAIL, not "legacy carve-out".
- Reality diff via `ss -tlnp` / `lsof` is mandatory; drift = FAIL after first-cycle grace (2026-05-01).
- Canon edits require joint team_60 (ops) + team_100 (arch) + team_00 sign-off.

### Resolution flow (all deploy scripts)

1. Deploy-spec declares `project:` + `env:` + `target.host:` (MANDATORY).
2. Deploy script calls `port_canon_lookup.py <project> <env> <host> <service>` per port.
3. Lookup failure → deploy fails fast; register via canon revision first.
4. Hardcoded ports in deploy-specs are a `validate_aos.sh` violation.

### Hub sources

- Registry: `lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml`
- Helper: `lean-kit/modules/12-home-server-infrastructure/deployment/port_canon_lookup.py`
- Template: `lean-kit/modules/12-home-server-infrastructure/deployment/deploy-spec.yaml.template`
- Ratification: `_COMMUNICATION/team_100/RATIFICATION_PORT_CANON_v2.2.0_2026-04-20.md`

---

*AOS Standard 11.2 | Multi-Project Docker Workstation | v1.2.0 | 2026-04-20*
*v1.2.0: port table updated for v2.2.0 canon (R10, cache_store band, all registered projects).*
