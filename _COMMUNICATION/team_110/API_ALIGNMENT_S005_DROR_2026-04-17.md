# Team 110 API Alignment Attempt — S005 Dror Launch

## Context
- Date: 2026-04-17
- Requested mode: DB-online API alignment
- Requested owner: Team 110

## What was executed
1. Verified home server AOS API health on `http://127.0.0.1:8090/api/health` (`200`).
2. Verified run-alignment endpoints exist (`/api/runs/{run_id}/advance`, `/fail`).
3. Attempted direct Team 110 calls on 8090:
   - result: actor verification not configured (`ACTOR_VERIFICATION_DISABLED`).
4. Started temporary trusted API instance with DB settings for runtime validation (`127.0.0.1:8092`).
5. Attempted Team 110 run creation for `shaked-wg-agent`:
   - `DOMAIN_NOT_FOUND` for `domain_id=shaked-wg-agent`.
6. Attempted Team 110 project-level alignment via API:
   - `PUT /api/projects/shaked-wg-agent` returned `INSUFFICIENT_AUTHORITY` (requires `team_00`).
7. Attempted Team 110 gate advance on probe run:
   - `Internal Server Error` from API runtime (`KeyError` in `post_advance` handler).

## Hard blockers identified
1. **Authority blocker**: project milestone update endpoint requires Team 00 authority.
2. **Domain registration blocker**: run creation for `shaked-wg-agent` domain fails (`DOMAIN_NOT_FOUND`) in current DB context.
3. **Runtime blocker**: `POST /api/runs/{run_id}/advance` throws server-side exception (`KeyError`) on tested instance.

## Decision
- Team 110 alignment **cannot be completed safely** in current DB-online runtime conditions without Team 00/API owner intervention.
- No direct YAML structured-field mutation was performed (kept Iron Rule #7 compliance).

## Required next action
1. Team 00 (or API owner with principal authority) to:
   - enable valid actor verification on the active API runtime,
   - ensure `shaked-wg-agent` is registered as a valid run domain in DB,
   - fix `post_advance` runtime error.
2. Re-run Team 110 alignment API call after those corrections.

