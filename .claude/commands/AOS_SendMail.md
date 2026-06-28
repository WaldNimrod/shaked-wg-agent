---
summary: "ALIAS SHIM → /AOS_mail send (W4 consolidation, AOS-V4.5-WP-SESSION-W4-SMART-MAIL). Removed next minor version."
category: infrastructure
---

# /AOS_SendMail — ALIAS SHIM

> **Consolidated into `/AOS_mail send` (W4, 2026-06-04).** This shim forwards for **one minor version**, then is removed.

## Phase 0 — Redirect

Run `/AOS_mail send` with the same arguments. All field inference, the confirm box, and delivery now live in
the unified mail surface backed by the `messages` API (`core/modules/management/messages.py`,
`POST /api/messaging/v2/send`).

```
/AOS_mail send <same args>
```

## Legacy fallback (compat window — ADR043 §4/§5, AC10)

When the v2 DB surface is unavailable (`503 DB_UNAVAILABLE`), the file transport stays operational: run
`source lean-kit/modules/team-messaging/scripts/msg_preflight.sh --verbose`, then on API-offline write the MSG
file and `msg_deliver_file <path>` (branch-safe push to origin/main). DB-first; file is the dual-write mirror.

## Error Handling

All invocations forward to `/AOS_mail send`. See `/AOS_mail` Error Handling.
