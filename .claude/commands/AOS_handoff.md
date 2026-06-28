---
summary: "Permanent thin alias → /AOS_mail handoff (W4 consolidation, AOS-V4.5-WP-SESSION-W4-SMART-MAIL)."
category: session
---

# /AOS_handoff — permanent thin alias

> **Permanent thin alias → `/AOS_mail handoff`** (W4, 2026-06-04). ORCH-10 (v5 ENV): the handoff is a
> first-class orchestration primitive (carries next-owner, artifact, bus capture), so this stable named
> entry point is KEPT — it is NOT scheduled for removal. The recipient resolves non-NULL via
> `aos_resolve_orchestrator` (ORCH-08), and the captured notice carries machine routing (COMM-08).

## Phase 0 — Redirect

Run `/AOS_mail handoff` with the same arguments. The unified verb still generates the canonical handoff artifact
via `GET /api/prompts/generate?mode=handoff`, then captures a `handoff` notice into the next WP's owning-team
inbox via the shared `aos_capture` helper (`POST /api/messaging/v2/capture kind=handoff`, degrade-safe).

```
/AOS_mail handoff <same args>
```

## Legacy fallback (compat window — ADR043 §4/§5, AC10)

When the v2 DB surface is unavailable, the file transport stays operational: run
`source lean-kit/modules/team-messaging/scripts/msg_preflight.sh --verbose`, then on API-offline write the
handoff MSG file and `msg_deliver_file <path>` (branch-safe push to origin/main). DB-first; file is the mirror.

## Error Handling

All invocations forward to `/AOS_mail handoff`. See `/AOS_mail` Error Handling.
