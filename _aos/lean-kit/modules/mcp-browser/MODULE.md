---
id: mcp-browser
title: "MCP Tools Standard"
module: "14"
version: "1.0.0"
profile_min: L2
required_by_profiles:
  - L2
  - L2.5
description: "Documents MCP tool availability per engine (browser + Linear, Git, PostgreSQL, filesystem, GitHub), launch.json for L0/L2, fallback chain, templates for .cursor/mcp.json, and troubleshooting."
dependencies: []
scripts:
  check: scripts/mcp_availability_check.sh
---

# Module 14 — MCP Tools Standard

## Purpose
Documents MCP tool availability per engine, `mcp_profile`-driven `.cursor/mcp.json` generation, launch.json configuration for L0/L2 profiles, fallback chain (MCP → Selenium → curl), and troubleshooting.

## Contents
| File | Description |
|------|-------------|
| MCP_BROWSER_STANDARD.md | Tool availability, configuration, fallback chain |
| MCP_TOOLS_POLICY.md | Cross-engine policy and profile → template mapping |
| templates/mcp_json_*.template | MCP JSON profiles for Cursor / Claude Code |
| templates/launch_json_L2.template | launch.json for L2 dashboard (uvicorn + DB) |
| scripts/mcp_availability_check.sh | Checks server responds on port |

## Scripts
- `check`: `scripts/mcp_availability_check.sh`
