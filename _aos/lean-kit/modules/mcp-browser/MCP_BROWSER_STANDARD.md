# MCP Tools Standard (Browser + Connected Servers)

This module documents **browser-oriented** QA tooling and **additional MCP servers** (Linear, Git, PostgreSQL, filesystem, GitHub) used in L2+ profiles. See `MCP_TOOLS_POLICY.md` for the cross-engine matrix.

## 1. MCP Tools per Engine

| Engine | Browser / preview | Other MCP servers (typical L2+) |
|--------|-------------------|--------------------------------|
| Claude Code | Claude Preview — preview_start, preview_screenshot, preview_click | postgres, filesystem, git (see templates) |
| Cursor | cursor-ide-browser — IDE-integrated preview | postgres, filesystem, git, github (L2.5) |
| OpenAI Codex | None / sandbox | Linear, Git — not assumed in sandbox |

### Non-browser servers (priority reference)

| Server key | Role |
|------------|------|
| **Linear** | Issue / project tracking (`mcp_json_global.template`) |
| **git** | Repository context |
| **postgres** | Database introspection (dashboard / AOS v3) |
| **filesystem** | Controlled project file reads |
| **github** | GitHub API (L2.5 template) |

## 2. Launch Configuration

### L0 (Static HTML)
```bash
python3 -m http.server 8080 -d dashboard/mockups/
```
No database, no env vars needed.

### L2 (FastAPI + Database)
Use the `launch_json_L2.template` or start manually:
```bash
AOS_V3_DATABASE_URL=postgresql://aos:aos_dev_local@127.0.0.1:5434/aos_v3 \
  python3 -m uvicorn core.modules.management.api:app --host 127.0.0.1 --port 8090
```

Required:
- Docker container `aos-postgres-dev` running on port 5434
- `AOS_V3_DATABASE_URL` environment variable set

## 3. Fallback Chain

When the primary MCP browser tool is unavailable:

1. **MCP Browser** (preferred) — Claude Preview or cursor-ide-browser
2. **Selenium/Playwright** — if programmatic browser needed
3. **curl + snapshot** — API-level verification only

## 4. Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Port conflict | Another process on same port | `lsof -i :<port>` to identify, kill or use different port |
| Missing env vars | Server started without `AOS_V3_DATABASE_URL` | Check process env: `ps eww -p <pid>`, restart with correct env |
| Docker not running | `aos-postgres-dev` container stopped | `docker start aos-postgres-dev` |
| CORS errors | Browser blocking cross-origin | Dashboard is same-origin — check port match |
| 500 on API calls | DB connection failure | Verify Docker, verify env var, check `docker logs aos-postgres-dev` |

## 5. Verification Script

Run `mcp_availability_check.sh` to verify server is responding:
```bash
bash scripts/mcp_availability_check.sh 8090 5
```
