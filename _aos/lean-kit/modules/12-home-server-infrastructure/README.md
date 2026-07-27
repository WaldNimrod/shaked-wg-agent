# Module 12: Home Server Infrastructure — Quick Start

This module establishes governance for all home server infrastructure across AOS-managed projects.

## What This Module Does

✅ **Canonical Server Registry** — Defines server identity, specs, and access methods  
✅ **Global Port SSOT** — Prevents port conflicts across multi-project environments  
✅ **Deployment Specs** — Per-project deployment configuration templates  
✅ **Agent Communication** — Defines Mac ↔ Server message protocol  
✅ **Bootstrap Procedures** — Server setup and validation checklists  

## Who Uses This Module

- **Team 60 (DevOps):** Implements and maintains infrastructure
- **Teams 10-190 (Builders/Validators):** Reference deployment specs
- **Teams 51 (QA):** Validates infrastructure readiness
- **Team 00 (Principal):** Approves major infrastructure changes

## Quick Links

| File | Purpose |
|------|---------|
| `MODULE.md` | Module metadata and definitions |
| `server-registry/waldhomeserver.yaml` | Server identity card |
| `deployment/port-registry.yaml` | Global port allocation (SSOT) |
| `deployment/deploy-spec.yaml.template` | Deployment spec template for projects |
| `agent-comm/PROTOCOL.md` | Agent communication protocol |
| `bootstrap/bootstrap-plan.md.template` | Server bootstrap template |

## Getting Started

### For Infrastructure Builders (Team 60)

1. **Understand the current server state** → Read `server-registry/waldhomeserver.yaml`
2. **Check port allocations** → Review `deployment/port-registry.yaml`
3. **Review the protocol** → Understand `agent-comm/PROTOCOL.md`
4. **Add new ports** → Update port-registry.yaml (must register before deploying)

### For Project Builders (Team 10-190)

1. **Create deployment spec** → Copy `deployment/deploy-spec.yaml.template` to your project's `_aos/deploy-spec.yaml`
2. **Register ports** → Add your service ports to the global `port-registry.yaml`
3. **Verify deployment** → Follow bootstrap and validation checklist

### For QA Validators (Team 51)

1. **Use the checklist** → See `bootstrap/phase-checklist.md.template`
2. **Verify each component** → Cross-check against server-registry and port-registry
3. **Test connectivity** → SSH, Tailscale, ports all reachable
4. **Sign off** → Complete validation and archive evidence

## Module Concepts

### 1. Server Registry

Each server (e.g., waldhomeserver) has an identity card containing:
- Hostname, IP addresses, SSH configuration
- Hardware specs (RAM, disk, CPU)
- Software installed (Docker, Python, Node, etc.)
- Purpose and owner
- Directory structure for projects/backups/communication

**File:** `server-registry/waldhomeserver.yaml`

### 2. Global Port Registry (SSOT)

All port allocations for ALL projects on a server are registered in ONE place:

```yaml
ports:
  - port: 8090
    service: "AOS API"
    project: "agents-os"
    scope: "localhost,lan,tailscale"
```

**Why?** Prevents duplicate port assignments when multiple projects run on the same hardware.

**File:** `deployment/port-registry.yaml`

### 3. Deployment Specs (Per Project)

Each project defines HOW it deploys to a server:

```yaml
# In project/_aos/deploy-spec.yaml
project_id: "agents-os"
server_target: "waldhomeserver"
service:
  mode: "always-on"
  systemd_unit: "aos-api.service"
ports:
  - name: "API"
    port: 8090
    protocol: "tcp"
```

**File:** `deployment/deploy-spec.yaml.template`

### 4. Agent Communication Protocol

How Mac and Server exchange messages:

- **Format:** Markdown files with YAML frontmatter
- **Naming:** `MSG-YYYYMMDD-NNN.md` → `MSG-YYYYMMDD-NNN-RESPONSE.md`
- **Transport:** scp over SSH (Mac initiates)
- **Constraint:** Mac must poll; server cannot push

**File:** `agent-comm/PROTOCOL.md`

## Common Tasks

### Deploying a New Project

1. Create `_aos/deploy-spec.yaml` in your project (use template)
2. Add service ports to global `port-registry.yaml`
3. Verify no conflicts: `port-registry.yaml` must be unique per port
4. Reference server: Use `server_target: "waldhomeserver"` in deploy-spec
5. Submit to Team 51 QA for validation

### Registering a New Service/Port

1. Choose a port from unallocated range (543x for DB, 808x for services)
2. Add entry to `deployment/port-registry.yaml`
3. Include: port, service name, project, scope, mode, notes
4. Commit both: port-registry.yaml + your project's deploy-spec.yaml

### Checking Server Health

```bash
# SSH to server
ssh nimrodw@10.100.102.2

# Run health check
./verify_server.sh

# Check Docker containers
docker ps

# Check Systemd services
systemctl list-units --type=service --state=running

# Check ports in use
ss -tlnp
```

### Sending a Message to Server

```bash
# Create message file
cat > MSG-20260418-001.md <<EOF
---
id: MSG-20260418-001
from: mac
to: server
type: task
priority: high
expects_response: true
related_wp: AOS-V320-WP-HOMESERVER
---

## Subject
Deploy Module 12 infrastructure

## Body
[task description]
EOF

# Send to server
./scripts/send_message.sh MSG-20260418-001.md

# Check for response later
./scripts/pull_responses.sh
```

## Standards & Compliance

### Multi-Project Docker Workstation Standard

This module enforces:
- ✅ Fixed, version-controlled host ports (no ad-hoc assignments)
- ✅ Port registry documented in one canonical place
- ✅ TikTrack ports are immutable (primary project priority)
- ✅ Conflict resolution based on project establishment date

**Reference:** `lean-kit/modules/standards-conventions/MULTI_PROJECT_DOCKER_WORKSTATION_v1.0.0.md`

### AOS Iron Rules

- ✅ **Infrastructure only** — No application logic
- ✅ **Team 00 awareness** — Infrastructure changes require approval
- ✅ **Port discipline** — All ports registered in global SSOT
- ✅ **Team 51 submission** — All work validated before production
- ✅ **No governance layer writes** — Team 60 writes to `_COMMUNICATION/` only

## FAQ

**Q: Can I assign a port without registering it?**  
A: No. All ports must be in port-registry.yaml before deployment. Unregistered ports violate Multi-Project standard.

**Q: What if two projects need the same port?**  
A: Use port-registry.yaml's conflict resolution rule. TikTrack wins (immutable). For other projects, the established one keeps it; the newer one re-assigns.

**Q: How do I know which ports are free?**  
A: Check `deployment/port-registry.yaml`. Any port not listed is available. Choose from unallocated ranges (543x for databases, 808x for services).

**Q: Can the server push messages to Mac?**  
A: No. The protocol is one-way pull (Mac initiates). Server cannot push due to firewall constraints.

**Q: What if deployment fails?**  
A: Create a response message documenting the failure. Mac will pull it on next poll cycle. Include error logs, blockers, and remediation steps.

## Support

- **Infrastructure Issues:** Contact Team 60 (AOS DevOps)
- **Port Conflicts:** Report to Team 60 for resolution
- **QA Validation:** Contact Team 51
- **Architecture Questions:** Escalate to Team 00 (Principal)

---

**Version:** 1.0.0  
**Module Owner:** Team 60 (AOS DevOps & Platform)  
**Last Updated:** 2026-04-18
