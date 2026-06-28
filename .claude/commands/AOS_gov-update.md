---
summary: "DEPRECATED — use /AOS_gov-sync (unified canonical command since 2026-05-23)."
category: governance
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8090`); (3) `http://127.0.0.1:8090` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team).

## Phase 0 — Redirect (DEPRECATED)

This command is deprecated. **Stop here and use `/AOS_gov-sync` instead.**

`/AOS_gov-sync` now has `--scope=full` as default — equivalent to what this command did, plus offline fallback and `--push` support.

## Migration guide

| Old invocation | New equivalent |
|----------------|---------------|
| `/AOS_gov-update` | `/AOS_gov-sync` (full scope by default) |
| `/AOS_gov-sync` (old narrow) | `/AOS_gov-sync --scope=teams` |

## Why consolidated

Two separate commands created a fragmentation risk: governance updates on one path did not propagate lean-kit content. Since lean-kit IS minimal governance, a single command with `--scope` is the correct architecture. The new command also has a mandatory offline fallback (no more STOP on API-offline).

## Error Handling

No errors to handle — this command does nothing. Run `/AOS_gov-sync` instead.

---

*Deprecated: 2026-05-23 | Superseded by: `/AOS_gov-sync` | Decision: team_100 GCR triage session*
