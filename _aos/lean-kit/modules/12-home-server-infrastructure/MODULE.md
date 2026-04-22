---
module: 12
id: home-server-infrastructure
title: Home Server Infrastructure
version: 2.2.0
status: ACTIVE
category: TOOLING
canonical_owner: Team 60 (AOS DevOps & Platform) + Team 100 (AOS HUB — joint canon authorship)
applies_to: All AOS-managed projects requiring server deployment
date: 2026-04-20
port_registry_version: 2.2.0
ratification: _COMMUNICATION/team_100/RATIFICATION_PORT_CANON_v2.2.0_2026-04-20.md
---

# Module 12: Home Server Infrastructure

## Purpose

Establish canonical governance for home server infrastructure management across all AOS-managed projects. This module is the single source of truth for:

- Server identity and specifications (waldhomeserver)
- Port allocation and conflict prevention (port-registry.yaml)
- Deployment specifications per project
- Agent-to-agent communication protocol
- Service lifecycle and bootstrap procedures

## Module Dependencies

```yaml
depends_on:
  - module_01: project-governance      # Requires _aos/ structure
  - module_03: team-model              # Agent identity for communication
  - module_11: standards-conventions   # Multi-project port discipline
```

## Profile Inclusion

| Profile | Status | Rationale |
|---------|--------|-----------|
| L0 | OPTIONAL | L0 projects may run locally only |
| L2 | REQUIRED | L2 projects run engine + DB on server |
| L3 | REQUIRED | L3 autonomous operation requires server |

## Core Concepts

### 1. Server Registry
Each managed server (e.g., waldhomeserver) is registered with an identity card containing:
- Hostname, IP addresses (LAN + Tailscale)
- Hardware specs (RAM, disk, CPU)
- Software installed (Python, Node, Docker, Tailscale)
- SSH configuration and key management
- Directory structure for projects, backups, agent communication

### 2. Port Registry (SSOT — v2.2.0 tiered)
A global, project-agnostic port registry prevents conflicts across hosts AND environments:
- Canonical location: `lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml`
- Schema v2.2.0 (updated 2026-04-20): `hosts[]` + `projects[].instances[]` with (host, env) tuples
- Canonical `environment_offsets`: dev +0, staging +100, production +200, qa +300
- Every listener MUST trace back to a registered `instances[]` entry
- Reality-diff enforcement: `validate_aos.sh` Check 24 v2 (feature-flagged by `CHECK_24_REALITY_DIFF`)
- No grandfathering: unregistered listeners are violations, not accommodations
- Canon edits require joint team_60 (ops) + team_100 (arch) + team_00 sign-off
- **Cross-env reservation (R10):** a port assigned to any project in any environment is RESERVED globally across all hosts and all environments — no other project may use it anywhere, even if the original project has no instance there

### 3. Deployment Specs (v1.1.0)
Each project's `_aos/deploy-spec.yaml` describes ONE (project, env, host) tuple:
- `project:` + `env:` + `target.host:` — MUST resolve against port-registry
- Ports resolved at deploy time via `port_canon_lookup.py` — **NEVER hardcoded**
- Secrets in `.env.<env>` files only (git-ignored)
- Pre-flight contract: canon version check, port-free check, lookup resolves
- Multi-env projects author one deploy-spec per (env, host) OR use single-file `envs:` map

### 4. Agent Communication Protocol
Defines Mac <-> Server message exchange:
- Message format (markdown frontmatter + body)
- Directory structure (inbox/outbox on both sides)
- Message lifecycle (send, receive, process, archive)
- Constraints (Mac initiates; server cannot push)

## Files in This Module

```
lean-kit/modules/12-home-server-infrastructure/
├── MODULE.md                          # This file
├── README.md                          # Human-readable overview
│
├── server-registry/
│   ├── server.yaml.template           # Template for new servers
│   └── waldhomeserver.yaml            # Production server identity
│
├── deployment/
│   ├── deploy-spec.yaml.template      # Template for projects (v1.1.0 — env + host mandatory)
│   ├── port-registry.yaml             # GLOBAL SSOT (v2.0.0 — tiered env offsets)
│   ├── port_canon_lookup.py           # Canonical port resolver (deploy-time helper)
│   └── service-map.yaml.template      # Systemd/cron service definitions
│
├── agent-comm/
│   ├── PROTOCOL.md                    # Agent communication protocol
│   └── message.md.template            # Message format template
│
├── bootstrap/
│   ├── bootstrap-plan.md.template     # Server bootstrap template
│   └── phase-checklist.md.template    # Validation checklist
│
└── scripts/
    ├── send_message.sh                # Mac: push message to server
    ├── pull_responses.sh              # Mac: pull responses from server
    ├── check_inbox.sh                 # Server: list pending messages
    └── verify_server.sh               # Health check across services
```

## Key Decisions

### Port Registry is Global
The port-registry.yaml is NOT per-project. It lives in Module 12 and is owned by Team 60. This ensures:
- No duplicate port assignments across multi-project environments
- Single point of truth for firewall and network configuration
- Clear conflict resolution (TikTrack immutable, others resolved by date)

### waldhomeserver is Canonical
The waldhomeserver.yaml is the identity card for the primary development/staging server. Other servers (if created) follow the same template structure.

### Agent Communication Uses Markdown
Messages are markdown files with frontmatter (metadata) + body (content). This allows:
- Version control (git log shows communication history)
- Human readability (no JSON parsing needed for manual review)
- Easy templating (markdown is universal)

## Integration with Projects

### For TikTrack-Phoenix_AOSProject
Create `_aos/deploy-spec.yaml` that references:
- `server_target: waldhomeserver` (from server-registry)
- `ports: [...]` (must appear in port-registry.yaml)

### For SmallFarmsAgents
Create `_aos/` directory and `deploy-spec.yaml` with same structure.

### For agents-os (AOS hub itself)
AOS engine deployment uses its own deploy-spec.yaml (API on port 8090, DB on 5434).

## Port resolution (canonical flow)

Deploy scripts MUST resolve ports through the canon helper, not by reading
deploy-spec.yaml literals. Two supported call patterns:

**Python import:**
```python
from port_canon_lookup import lookup
port = lookup("TikTrack-Phoenix_AOSProject", "staging", "waldhomeserver", "api")
# → 8182
```

**Shell (CI, bash deploy scripts):**
```bash
PORT=$(python3 lean-kit/modules/12-home-server-infrastructure/deployment/port_canon_lookup.py \
       "<project>" "<env>" "<host>" "<service>")
[ -z "$PORT" ] && { echo "canon lookup failed"; exit 1; }
```

**Failure modes (exit codes):**
- `2` canon not found (set `PORT_REGISTRY_YAML` or run from repo root)
- `3` (project, env, host, service) not registered → canon revision needed
- `4` canon parse / schema error → joint team_60 + team_100 review

Hardcoded ports in deploy-specs are a `validate_aos.sh` violation.

## Validation Rules

All deployments must satisfy:

1. **Port Registry Compliance (v2.2.0)**
   - Every `(host, env, service)` in deploy-spec.yaml must resolve via `port_canon_lookup.py`
   - No port can be bound without a matching `projects[].instances[]` entry
   - Reality-diff (Check 24 v2) enforces registry ↔ running-listener equivalence
   - Cross-env reservation (R10): ports are globally reserved from first definition — no per-host exceptions

2. **Server Availability**
   - Target server must exist in server-registry/
   - Server must have required software (Docker, Python, etc.)

3. **Environment Variables**
   - Secrets (passwords, tokens) NEVER in deploy-spec.yaml
   - Secrets ONLY in `.env` files (git-ignored)

4. **Archive Compliance**
   - Agent communication messages follow PROTOCOL.md format
   - All messages archived after processing

## Non-Goals

This module does NOT:
- Replace docker-compose.yml in project repos
- Manage cloud infrastructure (AWS, GCP, etc.)
- Handle CI/CD (GitHub Actions stay in repos)
- Define monitoring/alerting (future module)
- Manage server backups (defined in deploy-spec.yaml but not executed by this module)

## Future Enhancements (Phase 6+)

- Module 13: Monitoring & Alerting
- Systemd socket activation for critical services
- Distributed message queue for async task dispatch
- Mobile-specific CLI tool (wrapper around AOS API)
- Persistent session logging (audit trail)

---

**Version:** 2.2.0  
**Status:** ACTIVE  
**Owner:** Team 60 (AOS DevOps & Platform) + Team 100 (co-author)  
**Created:** 2026-04-18  
**Last Updated:** 2026-04-20 (port-registry v2.2.0 — R10, cache_store band, 2 new projects, SFA mac_local, legacy retired)
