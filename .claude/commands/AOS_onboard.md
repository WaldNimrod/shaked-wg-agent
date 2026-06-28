---
summary: "Generate a canonical activation/onboarding prompt for a team to open a new session or topic."
category: session
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8090`); (3) `http://127.0.0.1:8090` — localhost fallback (HTTP 410 on Mac unless the legacy stub runs). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. **Front door (shell):** `scripts/aos_api_server_call.sh <team_id> GET <path>` (W5 W-S1) applies the same base resolution + actor headers in one place.

Generate a **canonical activation prompt** — a copy-paste block that turns a fresh session (any engine) into a properly-onboarded AOS team, so you never write it by hand. Thin orchestrator over `GET /api/prompts/generate` (`prompts_activation.py`, ADR041 / Iron Rule #13). The default `team_100` then generates the other teams.

API endpoint:
`GET {HUB_API_BASE}/api/prompts/generate?type=onboard_agent&team_id={team}&governance_depth={lean|full}&session_topic={topic}`
(`HUB_API_BASE` defaults to `http://127.0.0.1:8090`; override via `AOS_API_BASE`.)

## Phase 0 — Parse arguments
Parse `$ARGUMENTS`:
- `team_id` — default **`team_100`** (the architect that spins up the rest). Accept `team_90`, `team_190`, etc.
- `topic` / `--topic "<text>"` — the session topic (expands the prompt with matching active-WP context). Remainder of `$ARGUMENTS` = topic if no flag.
- `--wp <WP_ID>` — optional direct WP context injection.
- `--depth lean|full` — default **`full`** (whole team contract). `lean` = universal sections only (Iron Rules, Authority).
- `--mode activation|handoff` — default `activation`. (`handoff` returns the 7-section handoff artifact instead.)

## Phase 1 — Generate
Build the query and call the endpoint (prefer the front door):
```bash
bash scripts/aos_api_server_call.sh "${team_id:-team_100}" GET \
  "/api/prompts/generate?type=onboard_agent&team_id=${team_id:-team_100}&governance_depth=${depth:-full}&session_topic=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "$topic")${wp:+&wp_id=$wp}${mode:+&mode=$mode}"
```
Or raw: `curl -s "${AOS_API_BASE:-http://100.125.98.56:8090}/api/prompts/generate?type=onboard_agent&team_id=team_100&governance_depth=full&session_topic=<topic>"`.

## Phase 2 — Present
Return the generated activation prompt as a **single fenced copy-paste block** (Iron Rule #7 / ADR032 routing-display convention) — ready to paste into a fresh Claude Code / Cursor / Codex session. Note the target engine if the team's canonical engine differs from where it will run.

## Error Handling
- **API 410 (Mac legacy stub):** set `AOS_API_BASE=http://100.125.98.56:8090` and retry (CLAUDE.md startup §4b).
- **API 000 / unreachable:** emit the **manual fallback** block so the operator is never blocked:
```
You are AOS {team_id} · engine Claude Code · repo agents-os (/Users/nimrod/Documents/agents-os).
STARTUP: read CLAUDE.md startup steps 1–10; DB probe; validate_aos.sh (expect 0 FAIL); then /AOS_session start.
MODEL: SOLO, multi-session, worktree isolation (ADR052); tiered validation (sub-agent intermediate · cross-engine L-GATE_VALIDATE).
TOPIC: <topic>. Read _COMMUNICATION/team_100/AOS_OPERATOR_COCKPIT_*.md and propose a first step.
```
- **Unknown team_id:** list valid teams from `core/definition.yaml` / `team_options`.

## Notes
- Thin orchestrator (≤150 lines, IR#13): all compilation logic lives in `prompts_activation.py`; this command only shapes args + presents.
- Companion: `/AOS_handoff` (mode=handoff) for end-of-session handoff; `/AOS_session start` for the receiving session's first action.
