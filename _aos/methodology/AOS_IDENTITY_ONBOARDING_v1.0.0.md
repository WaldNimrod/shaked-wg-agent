# AOS Identity Onboarding — v1.0.0

**Mandatory first-session read for every AOS agent.**
Locked 2026-04-19 by Team 00.

---

## What AOS is

**AOS (Agents OS)** is a multi-domain, multi-engine **infrastructure** for managing AI agents and software projects across an organization.

- It is **not a product**. It is the platform on which products are built by agents.
- It supports **multiple domains** (product repos — "spokes") and a single **hub** (this repo: `agents-os`).
- It supports **multiple engines** (Claude Code, Cursor, OpenAI Codex, Claude Desktop, and others) and **multiple IDEs** in the same organization.
- It defines the **governance, methodology, and operational contracts** that all agents follow regardless of which engine or IDE they run in.

## Hub vs spoke

| | Hub (`agents-os`) | Spoke (any product repo) |
|---|---|---|
| Role | SSOT for governance, lean-kit, canon, directives, templates | Consumes AOS governance as read-only snapshot in `_aos/` |
| Writes to `_aos/` | Yes (via `gov-update` + `gov-sync` by team_00/team_100) | **NO** — `_aos/` is read-only snapshot |
| Owns product code? | No — hub is governance-only | Yes — product code lives here |
| Can edit governance contracts? | Yes — `core/governance/team_*.md` | No — must file GCR to hub |
| Propagation authority | Executes `aos_sync_all.sh` | Receives snapshot |

## The boundary rule (the most important rule you'll learn)

**Every agent must know:**

> "I am operating in **{domain X}**. My repo has an `_aos/` directory — that is **AOS infrastructure** running inside my domain as a read-only snapshot. The hub at `/Users/nimrod/Documents/agents-os` owns it. If I need an AOS change, I file a `GOVERNANCE_CHANGE_REQUEST` to `team_100`. I never edit `_aos/` directly."

## Authority hierarchy

| Role | Team | May do |
|------|------|--------|
| Principal | `team_00` (Nimrod, human) | Final authority on all governance + Iron Rule changes |
| Chief Architect | `team_100` | Executes `/AOS_gov-update` + `/AOS_gov-sync` (only Team 100 may run these) |
| Domain Architect | `team_110` | Specs + LOD review; executes in hub only under mandate |
| Git/Files | `team_191` | `_aos/` bootstrap + propagation under explicit mandate |
| All other teams (`team_10, team_20 ... team_80, team_90, team_190, team_200, team_XX`) | Domain work; **NEVER edit `_aos/`** | Use `_COMMUNICATION/team_[ID]/` + application source only |

Iron Rule #12 (ADR039): `/AOS_gov-update` and `/AOS_gov-sync` are **LOCKED** to `team_00` and `team_100`. Any other invocation must be rejected with a pointer to `GOVERNANCE_CHANGE_REQUEST` template.

## Multi-engine, multi-IDE

The same governance is read by agents running in different engines:

- **Claude Code** (this session) reads `CLAUDE.md` + `.claude/commands/` + `_aos/`
- **Cursor IDE** reads `.cursorrules` + `.cursor/` + `_aos/`
- **OpenAI Codex / Team 190** reads `_aos/governance/team_190.md` when activated
- **Claude Desktop + Project** (Team 200 bundles) reads hub-supplied activation packs

For uniformity: `CLAUDE.md` and `.cursorrules` are rendered from canonical templates at `lean-kit/modules/project-governance/templates/`. The canonical startup sequence is the same across all engines and IDEs.

## Session startup you should do first

Every session, in every AOS repo (hub or spoke):

1. Read `_aos/roadmap.yaml` (spoke) or `core/definition.yaml` (hub) — current work
2. Read `_aos/context/PROJECT_CONTEXT.md` or hub equivalent — project background
3. Read `_aos/definition.yaml` (spoke L2) or `_aos/context/ACTIVATION_*.md` (spoke L0) — your role
4. **DB probe** — check `_aos/db_connectivity_status.json` at hub path; if offline, fix before proceeding
5. Run `validate_aos.sh` on your current directory — must show 0 FAIL
6. **If this is your first AOS session ever:** read this file (AOS_IDENTITY_ONBOARDING_v1.0.0.md)

## How to request a change to AOS governance

If you are **not** team_00 or team_100 and you need a change to `_aos/` content:

1. Copy template: `{hub}/lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template`
2. Fill in: your team ID, proposed change (exact section + wording), rationale, precise prompt for team_100, impact assessment
3. Save as: `_COMMUNICATION/team_XX/GOVERNANCE_CHANGE_REQUEST_{TOPIC}_v1.0.0.md` in the hub
4. Notify team_100 via canonical routing artifact
5. Team 00 reviews → approves or rejects
6. If approved, team_100 executes `/AOS_gov-update` in hub → propagates via `/AOS_gov-sync` or `aos_sync_all.sh`
7. Snapshot arrives at your spoke; you read it on next session startup

## Where to learn more

- `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` — full principles + Iron Rules list
- `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` — directory structure canon
- `methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.1.0.md` — full gov-update procedure
- `governance/directives/ADR034_*.md` — data authority (DB-first, API-only)
- `governance/directives/ADR039_AOS_DOMAIN_AUTHORITY_LOCKDOWN_v1.0.0.md` — authority lockdown (Iron Rule #12)

---

**When unsure about whether you may touch a file or run a command: default to NO. File a GCR instead. Infrastructure teams protect infrastructure; domain teams build products. Clear boundaries, clear safety.**
