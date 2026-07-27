---
id: PERPLEXITY_MCP_INSTALL_v1.0.0
type: RUNBOOK
author: Team 60 (AOS DevOps & Platform)
date: 2026-04-25
status: VERIFIED
strategic_anchor: "AOS v4.0.0 charter — engine matrix v2; unblocks team_80 auto-live research mode"
references:
  - MANDATE_OPS_PERPLEXITY_MCP_INSTALL_2026-04-25_v1.0.0.md
  - lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml
---

# Runbook — Perplexity MCP Server Install (Claude Code)

## Purpose

Install and configure the Perplexity AI MCP server in Claude Code so that
agents can perform live web research with citations in AUTO-LIVE mode.
This enables team_80 (and any research-capable team) to switch from
manual browser research to automated Perplexity-grounded queries.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| macOS with Claude Code installed | Tested on Darwin 24.6.0 |
| Node.js + npx | Required to run `@perplexity-ai/mcp-server` |
| `PERPLEXITY_API_KEY` procured | From https://www.perplexity.ai/settings/api |
| Key stored securely | macOS Keychain (recommended) — see §Key Storage |

---

## §Key Storage — how to store the API key

**NEVER paste the key in chat or commit it to any git repo.**

### Option A — macOS Keychain (recommended)

```bash
# Run once in terminal — replace <YOUR_KEY> with actual key
security add-generic-password \
  -a perplexity \
  -s PERPLEXITY_API_KEY \
  -w <YOUR_KEY>
```

Retrieve during scripting (without exposing to stdout):
```bash
PPLX_KEY=$(security find-generic-password -a perplexity -s PERPLEXITY_API_KEY -w)
```

### Option B — untracked local .env

```bash
# Ensure the file is in .gitignore before writing
echo "PERPLEXITY_API_KEY=<YOUR_KEY>" >> core/.env.local
```

---

## Install Steps

### Step 1 — Verify key is accessible

```bash
PPLX_KEY=$(security find-generic-password -a perplexity -s PERPLEXITY_API_KEY -w 2>/dev/null)
echo "Key length: ${#PPLX_KEY}"
# Expected: Key length: 50+ (non-zero)
```

### Step 2 — Add MCP server to Claude Code

```bash
PPLX_KEY=$(security find-generic-password -a perplexity -s PERPLEXITY_API_KEY -w 2>/dev/null) && \
claude mcp add perplexity \
  --env PERPLEXITY_API_KEY="$PPLX_KEY" \
  -- npx -y @perplexity-ai/mcp-server
```

This adds the server to `~/.claude.json` (project-scoped or global,
depending on working directory). The key is stored in the local claude
config, which is NOT tracked by git.

### Step 3 — Verify registration

```bash
claude mcp list
# Expected output includes:
# perplexity: npx -y @perplexity-ai/mcp-server - ✓ Connected
```

### Step 4 — End-to-end test (new Claude Code session)

Open a new Claude Code session in the hub directory and run:

> "Using Perplexity, what is a major AI news headline from today?
>  Please cite your source."

Expected: A response grounded in real-time web data with at least one
citation URL (e.g. `[source](https://...)`) returned by the
`perplexity_search_web` tool.

---

## Port discipline (Iron Rule #9)

**This server is stdio-only.** It spawns as a child process via `npx`
and communicates over stdin/stdout. No network port is used or opened.

No entry in `port-registry.yaml` is required. This is documented here
as the explicit port-discipline record per IR#9.

---

## Package details

| Field | Value |
|---|---|
| Package | `@perplexity-ai/mcp-server` |
| Source | https://github.com/perplexityai/modelcontextprotocol |
| npm | https://www.npmjs.com/package/@perplexity-ai/mcp-server |
| Transport | stdio |
| Auth | `PERPLEXITY_API_KEY` env var |
| Models available | sonar, sonar-pro, sonar-deep-research, sonar-reasoning-pro |

---

## Troubleshooting

### `✗ Failed` in `claude mcp list`

1. **Auth error** — key is wrong or expired. Regenerate at
   https://www.perplexity.ai/settings/api and re-run Step 2.
2. **npx not found** — install Node.js: `brew install node`
3. **Network blocked** — check VPN or firewall; `@perplexity-ai/mcp-server`
   calls `api.perplexity.ai` over HTTPS.

### Rate limit errors in queries

Default sonar-small is low-cost. If hitting limits, switch to pay-per-query
billing at https://www.perplexity.ai/settings/api.

### Key not in keychain after reboot

The keychain entry persists across reboots. If missing, verify with:
```bash
security find-generic-password -a perplexity -s PERPLEXITY_API_KEY -g 2>&1 | grep "keychain:"
```

### Re-adding the server (e.g., key rotation)

```bash
claude mcp remove perplexity
# Update key in keychain, then re-run Step 2
```

---

## Uninstall

```bash
claude mcp remove perplexity
# Optionally remove key from keychain:
security delete-generic-password -a perplexity -s PERPLEXITY_API_KEY
```

---

## Replication for other engines / machines

This runbook applies to any machine with Claude Code installed. For
server-side installs (team_99), coordinate with team_99 first; the
procedure is identical but the config lands in the server's `~/.claude.json`.

For other MCP engines (Cursor, VS Code), follow the respective IDE's
MCP server config documentation using the same package and env var.

---

## Verification record (2026-04-25)

- `claude mcp list` → `perplexity: npx -y @perplexity-ai/mcp-server - ✓ Connected`
- Key stored in macOS Keychain (not committed to git)
- `git grep -i perplexity_api_key` → 0 hits for actual key value (documentation strings only)
- Transport: stdio (no port registration required)
- Config location: `~/.claude.json` (outside all git repos)

---

*Authored by Team 60 / 2026-04-25 / AOS v4.0.0 M-4*
