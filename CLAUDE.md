# CLAUDE.md — shaked-wg-agent

<!-- AOS-CANONICAL-TEMPLATE v1.0.0 — rendered by scripts/aos_sync_all.sh. DO NOT hand-edit content between <!-- aos:canonical:start --> and <!-- aos:canonical:end -->. Project-specific additions go in the "Domain rules" section below. -->

<!-- aos:canonical:start -->
## ⚠ AOS Spoke Notice (READ FIRST)

You are working inside an **AOS spoke** — repo `shaked-wg-agent`, profile `L0`.

- **AOS = multi-domain, multi-engine infrastructure** for managing agents and projects across the organization. It is NOT a product. It governs how agents collaborate across product repos (spokes).
- **AOS hub:** `/Users/nimrod/Documents/agents-os` — SSOT for governance, lean-kit, canon, directives.
- **`_aos/` in this repo is a READ-ONLY SNAPSHOT** propagated from the hub via `aos_sync_all.sh` / `propagate_governance.sh`.
- **Do NOT edit** `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`, or any other AOS-layer file directly.
- **To request a governance change:** file `GOVERNANCE_CHANGE_REQUEST` artifact in `_COMMUNICATION/team_XX/` → route to `team_100` in the hub. Template: `/Users/nimrod/Documents/agents-os/lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template`
- **Governance procedures are LOCKED to AOS teams** (`team_00`, `team_100`) per Iron Rule #12 / ADR040. Non-AOS teams cannot invoke `/AOS_gov-update` or `/AOS_gov-sync`.

## Identity

- **Repo:** `shaked-wg-agent`
- **Path:** `/Users/nimrod/Documents/shaked-wg-agent`
- **Profile:** `L0`
- **AOS hub:** `/Users/nimrod/Documents/agents-os`
- **Domain:** `shaked-wg`

## Mandatory session startup (canonical — uniform across all AOS domains)

1. Read `_aos/roadmap.yaml` — current WP and gate position
2. Read `_aos/context/PROJECT_CONTEXT.md` — project background
3. Read `_aos/definition.yaml` (L2) or `_aos/context/ACTIVATION_*.md` (L0) — your role
4. **DB probe (mandatory):** `cat "/Users/nimrod/Documents/agents-os/_aos/db_connectivity_status.json"` — hub canonical DB status (refreshed by hub session). If `status: online` → all structured mutations go via API (Iron Rule #7 / ADR034). If `status: offline` → **STOP**: report `reason` field to Team 00, wait for Team 00 guidance before proceeding (ADR034 R8 protocol on a named branch — never main). To refresh hub status: run the hub DB probe from a hub session.
5. **Validation:** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — expect **0 FAIL** on this spoke
6. **AOS identity onboarding (first session only):** read `/Users/nimrod/Documents/agents-os/methodology/AOS_IDENTITY_ONBOARDING_v1.0.0.md`

## Iron Rules (uniform across all AOS domains)

1. Cross-engine: builder engine ≠ validator engine
2. Physical lean-kit snapshots only (no symlinks in `_aos/lean-kit/`)
3. Repo-internal `spec_ref` paths only
4. Single logical writer on `roadmap.yaml` (subject to API-only rule when DB online)
5. Final validation owned by `team_190` (constitutional, cross-engine, immutable)
6. Inter-team communication via canonical artifact in `_COMMUNICATION/`
7. **API-only structured mutations when DB online** (ADR034)
8. **Port canon** — `lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml` is SSOT for all long-running listeners (Team 60)
9. Universal team numbering
10. Governance flows source → snapshot only; no reverse (Iron Rule #11)
11. **Iron Rule #12: `gov-update` + `gov-sync` locked to `team_00` / `team_100` only** (ADR040). Other teams must file canonical GCR.
12. **Iron Rule #13** (ADR041): every deterministic AOS command is a thin orchestrator (≤150 lines + required `summary:` / `category:` frontmatter) over a hub API endpoint in `core/modules/management/`. SSoT Python modules carry data + logic. Cross-engine (Claude Code / Cursor / Codex / Desktop) call same API. Canon: `/Users/nimrod/Documents/agents-os/methodology/AOS_COMMAND_ARCHITECTURE_v1.0.0.md`.

## Directory Authority (uniform)

| Team | May write to |
|------|-------------|
| `team_00` (Principal) | Anywhere (final human authority) |
| `team_100` (Chief Architect) | `_COMMUNICATION/team_100/`, `_aos/roadmap.yaml`, `_aos/work_packages/` (hub only — SSOT edits) |
| `team_191` (Git/Files) | `_COMMUNICATION/team_191/`, `_archive/`, `_aos/` (bootstrap/propagation under mandate) |
| **All other teams** | `_COMMUNICATION/team_[ID]/` + application source ONLY — NEVER `_aos/` |

## Governance File Protection

- `_aos/governance/team_*.md` files in this repo are READ-ONLY snapshots of the hub SSOT at `/Users/nimrod/Documents/agents-os/core/governance/team_*.md`
- Any direct edit will be reverted on next `aos_sync_all.sh` run
- Validated by hub `validate_aos.sh` Checks 27–29
- Change-request workflow: GCR artifact → team_100 → Team 00 approval → hub edit + sync
<!-- aos:canonical:end -->

<!-- aos:project-specific:start -->

## Domain rules

<!-- Project-specific rules, commands, paths, and conventions go here.
     This section is PRESERVED across aos_sync_all.sh runs. -->
<!-- aos:project-specific:end -->
