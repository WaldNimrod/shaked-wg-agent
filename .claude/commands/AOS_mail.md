---
summary: "Unified mail: check inbox (DB v2 auto-read), send a message, or capture a handoff. Thin over /api/messaging/v2/*."
category: infrastructure
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8090`); (3) `http://127.0.0.1:8090` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team).

# /AOS_mail [check|send|handoff]

One mail surface for all AOS engines (W4, AOS-V4.5-WP-SESSION-W4-SMART-MAIL). Default verb: `check`.
All logic lives in the `messages` API (`core/modules/management/messages.py`) — this command is a thin
orchestrator (Iron Rule #13). The **v2 inbox is DB-only** (Finding 6); legacy file messages remain readable
via the old `/AOS_mail`-era `/api/messaging/inbox` and `_COMMUNICATION/team_*/MSG-HUB-*.md` scan (compat window).

> **No gate-progression state machine.** W4 surfaces verdict/handoff as a **hint only** — advancing a gate is a
> deliberate operator / `/AOS_gate-status` action (scope guard AC12). **No *unbounded interval* watcher;** the
> M7 server dispatcher (`aos-server-dispatcher`, M7-P2-WP1) is **event-gated** — it wakes a bounded session ONLY
> on a proven deliverable and fires `/AOS_mail check` only, never task logic and never a gate-advance/merge.

## Phase 0 — Parse verb

`$ARGUMENTS` → first token is the verb: `check` (default) · `send` · `handoff`. Identify self:
`TEAM=${AOS_SESSION_TEAM_ID:-${AOS_ACTOR_TEAM_ID:-team_100}}`, `ENV=${AOS_SESSION_ENV:-local-mac}`,
`SID=$(bash scripts/aos_session_ctl.sh session-id)`.

---

## Verb: check (default) — on-turn auto-read (F3, AC4/AC11)

Read pending mail addressed to self across all three recipient kinds (team + session + environment), render
the inbox view, then flip each row `pending→read` so it is presented **exactly once** (loop-guard).

```bash
for pair in "team:$TEAM" "session:$SID" "environment:$ENV"; do
  rk="${pair%%:*}"; rv="${pair#*:}"; [ -z "$rv" ] && continue
  python3 scripts/session_register_client.py inbox \
    --recipient-kind "$rk" --recipient "$rv" --status pending --limit 20
done
```

Render the inbox view (LOD300 §8 — CLI/text is the canonical surface):

```
AOS inbox — {TEAM}                                   now: {ISO-Z}
┌──────────────────┬────────────┬──────────┬──────────────────────────────┬──────────┬───────────┐
│ msg              │ from       │ kind     │ subject / wp                 │ status   │ age       │
├──────────────────┼────────────┼──────────┼──────────────────────────────┼──────────┼───────────┤
│ MSG-YYYYMMDD-NNN │ team_190   │ verdict  │ L-GATE_VALIDATE PASS — W4     │ pending  │ 2m ago    │
└──────────────────┴────────────┴──────────┴──────────────────────────────┴──────────┴───────────┘
  N pending · M read
```

For each pending message (oldest first):
1. `python3 scripts/session_register_client.py read --msg-id "$MSG"` — flips `pending→read` (loop-guard).
2. If `body_ref` present → fetch + present the artifact to the operator.
3. If `kind ∈ {verdict, handoff}` → surface a **next-action hint only** (e.g. `gate PASS — advance via /AOS_gate-status`). Never auto-advance.

**COMM-06 (v5 ENV) — one unified inbox across ALL THREE transports** (so no handoff is missed because it
arrived on a file surface). After the DB v2 rows, ALSO surface unacked file messages:

```bash
# Channel 2 — in-repo MSG-HUB-*.md (branch-safe):
source lean-kit/modules/team-messaging/scripts/msg_preflight.sh --verbose 2>/dev/null || true
#   list MSG-HUB-*.md for $TEAM, frontmatter status ∉ {READ,ARCHIVED}, no matching -RESPONSE.md.
# Channel 3 — canonical file-inbox + cross-domain relay (AOS-V5-WP-MAIL-SURFACE-UNIFORMITY T3):
python3 scripts/session_register_client.py file-inbox --recipient "$TEAM"
#   sweeps _COMMUNICATION/$TEAM/INBOX/ + ~/Documents/_agent_comm/{inbox,outbox}/ for to:$TEAM unacked.
```
Render every file row in the SAME table (`src=file` for MSG-HUB, `src=file-inbox|relay-*` for channel 3);
"unacked" = frontmatter lifecycle / a missing sibling `-RESPONSE.md` (no DB ack column). All three shown
together — a degraded-DB or cross-domain outbox message is never invisible.

If all inbox calls return `count==0` AND no unacked file message (channel 2 MSG-HUB **or** channel 3 file-inbox/relay) → `📭 inbox empty` → continue turn.
On API-down / non-200 → the client returns `{"degrade":true,count:0}` (read-only path is non-blocking); the
file-MSG scan still runs (so a degraded DB never hides a file handoff).

---

## Verb: send — human/agent-initiated message (AC2)

Infer fields from context; confirm with the operator in one compact box, then `POST /messaging/v2/send`:

```bash
curl -s -X POST "$AOS_API_BASE/api/messaging/v2/send" \
  -H "X-Actor-Team-Id: $TEAM" -H "X-Actor-Api-Key: $AOS_ACTOR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"sender":"'"$TEAM"'","recipient":"<to>","recipient_kind":"team","kind":"note",
       "subject":"<subject>","body_inline":"<short body, ≤2KB>","body_ref":"<artifact path or null>",
       "wp_id":"<wp or null>"}'
```

- `201` → `{msg_id,status:pending}`; echo the `msg_id`.
- `400 VALIDATION_ERROR` → fix fields (bad `recipient_kind`/`kind`, missing subject, oversized `body_inline`).
- `503 DB_UNAVAILABLE` → DB offline; fall back to legacy `/AOS_SendMail` file transport (still operational, AC10).

---

## Verb: handoff — generate HANDOFF_TO_NEXT + capture (AC3, §A.4c — dogfoods W4)

1. Generate the handoff artifact (server-assembled): `GET {AOS_API_BASE}/api/prompts/generate?mode=handoff&team_id={next_team}&wp_id={next_wp}` → write to `_COMMUNICATION/team_{next_team}/`.
2. Capture a `handoff` notice into the next WP's owning-team inbox (degrade-safe, one thin call):

```bash
bash scripts/aos_session_ctl.sh capture handoff \
  "$(bash scripts/aos_session_ctl.sh resolve-orchestrator "{next_wp}")" team \
  "HANDOFF_TO_NEXT → {next_wp}" \
  "_COMMUNICATION/team_{next_team}/HANDOFF_{next_wp}_v1.0.0.md" \
  "" "{next_wp}"
```

`recipient_kind=session` if the next session is live (use its `session_id`), else `team`. Recipient resolution
= `$AOS_ORCHESTRATOR_TEAM` → next-WP owning-team from register → `team_100` (Finding 4). On API-down / non-2xx →
the helper appends `event=capture … degrade=1` to `_COMMUNICATION/_log/messages.log` and continues (AC5/AC9).

---

## Error Handling

| Condition | Action |
|-----------|--------|
| API 503 `DB_UNAVAILABLE` | v2 surface down → legacy file transport (`/AOS_SendMail`, `/api/messaging/inbox`) — AC10 |
| API 400 `VALIDATION_ERROR` | bad `recipient_kind`/`kind`/missing subject/oversized inline → fix + retry |
| API 404 `MESSAGE_NOT_FOUND` | stale `msg_id` (read/ack/archive) — re-check inbox |
| capture non-2xx (handoff) | degrade to `messages.log`; session NOT blocked (AC5) |

## Legacy file transport (compat window — AC10 / Finding 6: v2 inbox is DB-only)

The v2 inbox above is **DB-only**. Legacy file-based MSGs (`MSG-HUB-*.md`) remain readable in parallel during
the compat window via the unchanged file surface (ADR043 §4/§5):

- **Read fallback:** `source lean-kit/modules/team-messaging/scripts/msg_preflight.sh --verbose`; on API-offline scan `_COMMUNICATION/team_{id}/MSG-HUB-*.md` (branch-safe).
- **Archive a legacy file MSG:** `msg_curl POST "/api/messaging/archive" '{"msg_id":"MSG-HUB-YYYYMMDD-NNN","team_id":"team_NN"}'` (the existing `/api/messaging/archive` endpoint; v2 rows archive via `/api/messaging/v2/archive`).

The two surfaces run parallel until a post-program cleanup; no data loss, no route collision (v2 path-distinct).

**Compat-window close (COMM-06 / v5 ENV).** Both surfaces now converge on ONE identity/routing model: the
DB v2 bus carries `origin_team` + `project_id` (X-Project-Id, migr 029) and rejects self-routes
(INVALID_ROUTE, COMM-04) — matching the file surface's virtues. Target: file MSG-HUB is **read-only** as of
this round and the file→DB cutover (one-time import of unacked MSG-HUB rows into the v2 bus) completes by
the next milestone close; after cutover the file scan above is dropped from `check`. Until then, `check`
renders both (one unified view) so nothing is missed during the window.

## References

- `core/modules/management/messages.py` (send/capture/inbox/read/ack/archive — all logic)
- `core/db/migrations/012_messages.sql` (schema) · LOD300 §6 (flow) / §8 (mockup)
- `scripts/aos_session_ctl.sh` (`capture` / `inbox-check` / `resolve-orchestrator` helpers)
