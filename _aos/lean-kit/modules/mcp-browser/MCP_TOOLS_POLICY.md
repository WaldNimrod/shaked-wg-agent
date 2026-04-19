# MCP Tools Policy — Cross-Engine

This document defines which MCP-style tool surfaces are expected per **engine** and deployment **profile** (`mcp_profile` in project metadata). It complements `MCP_BROWSER_STANDARD.md`.

## Priority matrix (highest first)

| Capability | Cursor | Claude Code | OpenAI Codex |
|------------|--------|-------------|--------------|
| In-IDE browser / preview | cursor-ide-browser (FULL) | Claude Preview (FULL) | PARTIAL / sandbox-dependent |
| Repo / git context | git MCP (L2+) | git MCP | PARTIAL |
| DB introspection | postgres MCP (L2+) | postgres MCP | NONE typical |
| Filesystem project reads | filesystem MCP (L2+) | filesystem MCP | PARTIAL |
| GitHub API | github MCP (L2.5+) | github MCP | NONE typical |
| Issue tracking | linear (global template) | linear | NONE typical |

## Profile → template file

| mcp_profile | Template under `templates/` | Committed path |
|-------------|------------------------------|----------------|
| `none` | *(no generation)* | — |
| `L0` | `mcp_json_L0.template` | `.cursor/mcp.json` |
| `L2` | `mcp_json_L2.template` | `.cursor/mcp.json` |
| `L2.5` | `mcp_json_L2.5.template` | `.cursor/mcp.json` |

Global user config (optional): `mcp_json_global.template` → `~/.cursor/mcp.json`.  
Claude Code workspace: `mcp_json_claude_code.template` → `.mcp.json`.

## Regeneration

Configs are **generated** by `generate_context.sh` from templates; do not hand-edit `.cursor/mcp.json` in normal workflow—re-run Deploy / `generate_context.sh` after changing `mcp_profile`.
