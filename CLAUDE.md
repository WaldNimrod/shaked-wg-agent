# CLAUDE.md — shaked-wg-agent

<!-- AOS-CANONICAL-TEMPLATE v1.0.0 — rendered by scripts/aos_sync_all.sh. DO NOT hand-edit content between <!-- aos:canonical:start --> and <!-- aos:canonical:end -->. Project-specific additions go in the "Domain rules" section below. -->

<!-- aos:canonical:start -->
## ⚠ AOS Spoke Notice (READ FIRST)

You are working inside an **AOS spoke** — repo `shaked-wg-agent`, profile `L0`.

- **AOS = multi-domain, multi-engine infrastructure** for managing agents and projects across the organization. It is NOT a product. It governs how agents collaborate across product repos (spokes).
- **AOS hub:** `/Users/nimrod/Documents/AOS_V5/agents-os-merge-policy` — SSOT for governance, lean-kit, canon, directives.
- **`_aos/` in this repo is a READ-ONLY SNAPSHOT** propagated from the hub via `aos_sync_all.sh` / `propagate_governance.sh`.
- **Do NOT edit** `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`, or any other AOS-layer file directly.
- **To request a governance change:** file `GOVERNANCE_CHANGE_REQUEST` artifact in `_COMMUNICATION/team_XX/` → route to `team_100` in the hub. Template: `/Users/nimrod/Documents/AOS_V5/agents-os-merge-policy/lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template`
- **Governance procedures are LOCKED to AOS teams** (`team_00`, `team_100`) per Iron Rule #12 / ADR040. Non-AOS teams cannot invoke `/AOS_gov-update` or `/AOS_gov-sync`.

## Identity

- **Repo:** `shaked-wg-agent`
- **Path:** `/Users/nimrod/Documents/AOS_V5/shaked-wg-agent`
- **Profile:** `L0`
- **AOS hub:** `/Users/nimrod/Documents/AOS_V5/agents-os-merge-policy`
- **Domain:** `shaked-wg-agent`

## Mandatory session startup (canonical — uniform across all AOS domains)

0. **[CTX-03] Step 0 — Identity + connectivity (server / agent / non-interactive sessions):** Interactive Mac shells already have `AOS_API_BASE` + `AOS_ACTOR_API_KEY` exported from `~/.aos/actor.env` (auto-sourced by `~/.zshrc`). The v5 server (DB + API) is at the Tailscale-canonical `http://100.125.98.56:8092` (ADR043 §15.4).
   - **Verify env:** `echo ${AOS_API_BASE:-UNSET}` and `echo ${AOS_ACTOR_API_KEY:+KEY_SET}`. If `UNSET`/empty → `source ~/.aos/actor.env` (interactive), or run `bash /Users/nimrod/Documents/AOS_V5/agents-os-merge-policy/scripts/provision_actor_key.sh <team>` once from a team_00/team_99 issuer session. Never commit the key.
   - **Identity (so messages/handoffs attribute to THIS domain, not the hub team_100 default — read at send time by the messaging path):** `export AOS_SESSION_TEAM_ID=<this domain's team>` and `export AOS_PROJECT_ID=<this spoke id>`.
   - **Reachability:** `curl -s -o /dev/null -w '%{http_code}' --max-time 3 ${AOS_API_BASE:-http://100.125.98.56:8092}/api/system/health` → expect **200**.
   - **Authenticated check:** `curl -s -o /dev/null -w '%{http_code}' --max-time 3 -H "Authorization: Bearer ${AOS_ACTOR_API_KEY}" "${AOS_API_BASE}/api/messaging/v2/inbox?recipient_kind=team&recipient=<your team>"` → expect **200**, not **401**.
   - Full procedure (key retrieval, auth matrix): hub `governance/directives/ADR043` §15.4 + §16 — do NOT duplicate it here (Iron Rule #11, one-directional flow).
1. Read `_aos/roadmap.yaml` — current WP and gate position
2. Read `_aos/context/PROJECT_CONTEXT.md` — project background
3. Read `_aos/definition.yaml` (L2) or `_aos/context/ACTIVATION_*.md` (L0) — your role
4. **[CTX-05] DB/API health probe (mandatory — LIVE):** `_api="${AOS_API_BASE:-http://100.125.98.56:8092}"; curl -s --max-time 3 "$_api/api/system/health"` then parse JSON `db.status`:
   - `online` → API + DB online; all structured mutations go via API (Iron Rule #7 / ADR034).
   - `offline` **or** HTTP **410** → **STOP**: report to Team 00, wait for Team 00 guidance before proceeding (ADR034 R8 protocol on a named branch — never main).
   - HTTP **000** → API unreachable (check Tailscale connectivity to the v5 server).
   - *Degraded fallback only (may be stale):* `cat "/Users/nimrod/Documents/AOS_V5/agents-os-merge-policy/_aos/db_connectivity_status.json"` — hub-written file; use ONLY if the live curl cannot run. The fallback URL is the **:8092** v5 server — never `:8090` (v3/Mac-stub port).
5. **Validation:** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — expect **0 FAIL** on this spoke
6. **AOS identity onboarding (first session only):** read `/Users/nimrod/Documents/AOS_V5/agents-os-merge-policy/methodology/AOS_IDENTITY_ONBOARDING_v1.0.0.md`

## Iron Rules (uniform across all AOS domains)

1. Cross-engine: builder engine ≠ validator engine
2. Governance snapshots (`_aos/lean-kit/`, `_aos/governance/`, `_aos/methodology/`) are a physical copy or a git-ignored local cache refreshed by sync — never a symlink (Model B / ADR054; version held in tracked `_aos/AOS_GOVERNANCE_VERSION.yaml`)
3. Repo-internal `spec_ref` paths only
4. Single logical writer on `roadmap.yaml` (subject to API-only rule when DB online)
5. Final validation owned by `team_190` (constitutional, cross-engine, immutable)
6. Inter-team communication via canonical artifact in `_COMMUNICATION/`
7. **API-only structured mutations when DB online** (ADR034)
8. **Port canon** — `lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml` is SSOT for all long-running listeners (Team 60)
9. Universal team numbering
10. Governance flows source → snapshot only; no reverse (Iron Rule #11)
11. **Iron Rule #12: `gov-update` + `gov-sync` locked to `team_00` / `team_100` only** (ADR040). Other teams must file canonical GCR.
12. **Iron Rule #13** (ADR041): every deterministic AOS command is a thin orchestrator (≤150 lines + required `summary:` / `category:` frontmatter) over a hub API endpoint in `core/modules/management/`. SSoT Python modules carry data + logic. Cross-engine (Claude Code / Cursor / Codex / Desktop) call same API. Canon: `/Users/nimrod/Documents/AOS_V5/agents-os-merge-policy/methodology/AOS_COMMAND_ARCHITECTURE_v1.0.0.md`.

## Directory Authority (uniform)

| Team | May write to |
|------|-------------|
| `team_00` (Principal) | Anywhere (final human authority) |
| `team_100` (Chief Architect) | `_COMMUNICATION/team_100/`, `_aos/roadmap.yaml`, `_aos/work_packages/` (hub only — SSOT edits) |
| `team_191` (Git/Files) | `_COMMUNICATION/team_191/`, `_archive/`, `_aos/` (bootstrap/propagation under mandate) |
| **All other teams** | `_COMMUNICATION/team_[ID]/` + application source ONLY — NEVER `_aos/` |

## Governance File Protection

- `_aos/governance/team_*.md` files in this repo are READ-ONLY snapshots of the hub SSOT at `/Users/nimrod/Documents/AOS_V5/agents-os-merge-policy/core/governance/team_*.md`
- Any direct edit will be reverted on next `aos_sync_all.sh` run
- Validated by hub `validate_aos.sh` Checks 27–29
- Change-request workflow: GCR artifact → team_100 → Team 00 approval → hub edit + sync

## Dev/Staging TLS & Browser-QA Discipline (uniform)

- **Dev/staging TLS is often invalid BY DESIGN** — many hosts issue a valid certificate only on the primary/production domain. A cert error on a **dev/staging** URL is **expected** and is NOT a defect to fix; a cert error on **production** IS a real defect.
- **Cert-bypass flags are DEV-ONLY:** `curl -k` · chrome `--ignore-certificate-errors` · `requests verify=False`. Never use them in production QA.
- **Never use `curl` alone to validate layout** — curl sees only HTML, never the rendered box model, so horizontal-overflow / RTL / responsive bugs pass curl and ship. For any layout/overflow/visual check, run the dependency-free browser-QA runner: `_aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs` (Node 18+, no pip/npm). Discipline + curl-vs-CDP-vs-Lighthouse guidance: `_aos/lean-kit/modules/validation-quality/docs/BROWSER_QA_HARNESS_CANON_v1.0.0.md`.
- Dev SEO/Performance scores (noindex edge headers, cache misses) are **artifacts** — re-measure on the production domain.
<!-- aos:canonical:end -->

<!-- aos:project-specific:start -->

## Domain rules

<!-- Project-specific rules, commands, paths, and conventions go here.
     This section is PRESERVED across aos_sync_all.sh runs. -->
<!-- aos:project-specific:end -->
