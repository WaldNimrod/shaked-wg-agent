# Module 14 — MCP Browser Standard

Documents browser-based verification tools for AOS dashboard development.

## Usage

### Check server availability
```bash
bash scripts/mcp_availability_check.sh <port> [timeout_seconds]
```
Exit 0 = responding, Exit 1 = no response.

## Contents

- **MCP_BROWSER_STANDARD.md** — Full standard for MCP tools per engine
- **templates/launch_json_L2.template** — VS Code launch config for L2 dashboard
- **scripts/mcp_availability_check.sh** — Port availability checker
