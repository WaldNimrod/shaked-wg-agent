---
standard: 11.2
id: multi-project-docker
title: Multi-Project Docker Workstation
version: 1.0.0
date: 2026-04-09
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

All known port assignments for AOS-managed projects. This table is the single source of truth.

| Project | Service | Host Port | Container Name | Notes |
|---------|---------|-----------|----------------|-------|
| TikTrack | PostgreSQL | **5432** | `tiktrack-postgres-dev` | IMMUTABLE (primary project) |
| TikTrack | API (FastAPI) | **8082** | — | IMMUTABLE |
| TikTrack | Frontend (Vite) | **8080** | — | IMMUTABLE |
| TikTrack + agents-os | AOS API (uvicorn) | **8090** | — | Shared by design — same engine |
| agents-os | PostgreSQL | **5434** | `aos-postgres-dev` | Moved from 5432 (TikTrack conflict, 2026-04-09) |
| agents-os | Dashboard static | **8099** | — | Clean |
| SmallFarmsAgents | PostgreSQL | **5433** | `oma-postgres` | Clean |
| SmallFarmsAgents | Admin UI (Flask) | **5001** | — | Clean |
| SmallFarmsAgents | Static viewer | **8081** | — | Moved from 8080 (TikTrack conflict, 2026-04-09) |

**Reserved / do not use:** 5432 (TikTrack PG), 8080 (TikTrack frontend), 8082 (TikTrack API), 8090 (AOS API).

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

---

*AOS Standard 11.2 | Multi-Project Docker Workstation | v1.0.0 | 2026-04-09*
*Origin: SmallFarmsAgents domain. Canonicalized by Team 100.*
