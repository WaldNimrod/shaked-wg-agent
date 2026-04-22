---
module: 12
id: home-server-infrastructure
title: Home Server Infrastructure
version: 1.0.0
status: ACTIVE
category: TOOLING
canonical_owner: Team 60 (AOS DevOps & Platform)
applies_to: All AOS-managed projects requiring server deployment
date: 2026-04-18
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

### 2. Port Registry (SSOT)
A global, project-agnostic port registry prevents conflicts:
- Canonical location: `lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml`
- Enforces Multi-Project Port Discipline standard
- TikTrack ports are immutable (primary project)
- All port allocations must be registered before deployment

### 3. Deployment Specs
Each project gets a deployment specification in its `_aos/deploy-spec.yaml`:
- Which server to target (from server-registry)
- Service mode (always-on, on-demand, cron)
- Port allocations (must match global port-registry)
- Database requirements
- Environment variables (secrets in .env only)
- Backup strategy and retention

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
│   ├── deploy-spec.yaml.template      # Template for projects
│   ├── port-registry.yaml             # GLOBAL SSOT (canonical)
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

## Validation Rules

All deployments must satisfy:

1. **Port Registry Compliance**
   - Every port in deploy-spec.yaml must appear in port-registry.yaml
   - No port can be assigned without registering first

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

**Version:** 1.0.0  
**Status:** ACTIVE  
**Owner:** Team 60 (AOS DevOps & Platform)  
**Created:** 2026-04-18  
**Last Updated:** 2026-04-18
