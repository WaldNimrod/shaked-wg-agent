# AOS Hub ↔ Spoke Communication — the Ambassador conduit (v5)

- **Version:** v1.0.0
- **Date:** 2026-06-27
- **Owner:** team_100 (Chief System Architect) + team_00 (Principal)
- **Status:** CANON — binding for all spoke→hub traffic in the v5 single-DB topology
- **Origin:** Problem surfaced 2026-06-27 — a domain `team_100` session tried to message the hub and the
  message landed in *its own* inbox. Root-caused below.

---

## 1. The defect, root-caused

A domain session authenticated as `team_100` sent a report "to the hub" and then found it sitting in **its
own** inbox. This is **not a bug in the send** — it is a direct consequence of the v5 topology:

- **v5 runs ONE database (`aos_v5`) shared by the hub and all 13 spokes.** (That consolidation was the whole
  point of the cutover.)
- **Universal team IDs are global, not per-domain.** `team_00, 100, 110, 120, …` each name **exactly one
  row / one identity** in that shared DB.
- **The inbox query scopes by recipient only:** `messages.inbox()` =
  `WHERE recipient_kind = %s AND recipient = %s AND status = %s` — **no `project_id`, no environment filter**
  (`core/modules/management/messages.py:342`). The `project_id` *column exists* and is stored, but it tags the
  message's *subject matter*; it does **not** partition the mailbox.

**Therefore:** "send to `team_100`, kind `team`" writes to the **one** `team_100` mailbox that the *sending
domain's own* `team_100` session also reads. There is no separate "hub team_100" mailbox to receive it. The
domain talked to itself. **Q1 answer: there is no domain separation for shared universal-team mailboxes — and
by design there should not be one, because the fix is to address a hub-only role, not to shard `team_100`.**

---

## 2. The rule (how a domain reports to the hub in v5) — Q2

> **A spoke NEVER addresses the hub as `team_100`.** A spoke reaches the hub through one of two channels,
> in priority order:

### Channel 1 (canonical) — DB mail to the **Ambassador**, `team_120`

`team_120` is a **hub-only role** (domain scope `universal`, but **no spoke ever instantiates a `team_120`
session** — spokes run `team_100`/`team_110`/validators only). So `recipient = team_120, kind = team` is
**unambiguously hub-bound**: nothing on the spoke side reads that mailbox. The Ambassador triages and routes
to hub `team_100` / `team_00`.

```bash
# from a spoke session (set X-Project-Id so the hub knows the origin domain):
curl -s -X POST "$AOS_API_BASE/api/messaging/v2/send" \
  -H "X-Actor-Team-Id: team_100" -H "X-Actor-Api-Key: $AOS_ACTOR_API_KEY" \
  -H "X-Project-Id: <your_domain_id>" -H 'Content-Type: application/json' \
  -d '{"sender":"team_100","recipient":"team_120","recipient_kind":"team","kind":"note",
       "subject":"<domain>: <one-line>","body_inline":"<≤2KB summary>",
       "body_ref":"<spoke artifact path>","project_id":"<your_domain_id>"}'
```

`kind` picks the lane the Ambassador uses: `note` (status/report) · `request` (needs a hub action) ·
`governance_change_request` (an AOS-layer change — Ambassador routes to team_100 per IR#12). Always set
`project_id` **and** `X-Project-Id` to the origin domain — that is how the hub recovers "who sent this" once
it's in the single shared `team_120` mailbox.

### Channel 2 (degrade-safe / cross-tree) — the file outbox

When the DB is down, or for a heavy artifact, drop a message file in the cross-project relay:
`~/Documents/_agent_comm/outbox/MSG-<DOMAIN>-<YYYYMMDD>-NNN.md` (front-matter: `from`, `to: team_120`,
`X-Project-Id`, `full_report:` pointer). The hub sweeps this outbox. *(This is the path the tiktrack cutover
report `MSG-TIKTRACK-20260627-001.md` actually used — correctly.)*

**Never** use Channel-0 (write into your own `_COMMUNICATION/team_100/` and hope the hub sees it) — the hub
does not read spoke-internal team folders.

---

## 3. The Ambassador (team_120) — activation & use — Q3

**Role (from `core/governance/team_120.md`):** governance propagation, GCR handling, cross-spoke drift audit,
DOC_CANON stewardship — the hub's **single inbound conduit** for the whole spoke fleet. It inherited the
`_aos/` propagation-write authority from the dissolved team_191.

### 3a. How the hub activates team_120 (inbound triage)

team_120 is **not a long-running daemon** — it is a role a hub session assumes. Activate it whenever the hub
processes spoke traffic:

```bash
# hub session, on the hub repo:
export AOS_ACTOR_TEAM_ID=team_120          # assume the Ambassador role for this pass
/AOS_mail check                            # reads the team_120 mailbox (DB) + sweeps the file outbox
```

`/AOS_mail check` already reads all three recipient kinds for the active team; assuming `team_120` makes the
Ambassador mailbox the one it drains. For each item the Ambassador:
1. recovers the origin domain from `project_id` / `X-Project-Id`,
2. classifies: `note` → log + ack; `request` → action or route to the owning hub team; `GCR` → route to
   team_100 (IR#12 — only team_00/team_100 may *decide* an AOS-layer change),
3. replies to the spoke (DB mail back to `team_100`+`X-Project-Id`, or a `RESPONSE_*` file in the spoke's
   `_COMMUNICATION/team_100/INBOX/`),
4. for fleet-wide changes, propagates via `scripts/aos_sync_all.sh --all` (the propagation authority it holds).

### 3b. How a spoke "sends a request to the Ambassador"

Exactly Channel 1 above with `recipient: team_120`. A spoke does **not** run `/AOS_dispatch` at the hub or
push to hub `_aos/` — it files the message/GCR and the Ambassador carries it across the boundary
(one-directional, source→snapshot only — Iron Rule #11).

### 3c. The two-line mental model

```
spoke team_100/team_110  --(DB mail → team_120, X-Project-Id)-->  HUB Ambassador (team_120)
                          \--(or file: _agent_comm/outbox → team_120)-->  triage → team_100 / team_00
HUB  --(aos_sync_all / propagate_governance, snapshot only)-->  spoke _aos/  (read-only on the spoke)
```

Inbound (spoke→hub) = **messages to team_120**. Outbound (hub→spoke) = **governance propagation only**. The two
never cross: a spoke's `_aos/` is a read-only snapshot; a hub change a spoke needs is a **GCR to team_120**.

---

## 4. The proper fix — "which domain you send to" (chartered as a MANAGED WP)

The Ambassador conduit (§2–§3) makes the collision a non-issue operationally *today*. The structural fix —
so the mail system natively carries **which domain a message is addressed to** — is already half-built and
follows a proven in-repo pattern:

- **The FILE path already scopes by domain.** `team_messaging.py` (routes `/api/messaging/*`) resolves an
  `X-Project-Id` header through `_resolve_messaging_project_id()` into a per-spoke `_COMMUNICATION/` folder,
  with `test_team_messaging_multidomain.py` (8 passing tests) pinning the isolation. Universal/cross-domain
  teams there resolve to the hub's **main environment folder** (`agents-os/_COMMUNICATION/`) because callers
  omit `project_id`.
- **The DB path does NOT** (routes `/api/messaging/v2/*`, `messages.inbox()`): no `project_id` column, inbox
  filters recipient only. That asymmetry is the whole bug.

**Fix = port the file-path pattern onto the DB path** (one MANAGED WP):
1. Add a nullable `messages.project_id` (destination-domain scope; **NULL = the hub/central "main environment
   folder"**) via migration `029`.
2. Scope `inbox()` by the **recipient team's `domain_scope`** (already a seeded DB column): a
   **cross-domain / universal team** (team_00/10/.../100/110/120) → reads the single hub inbox
   (`project_id IS NULL`), *never* scoped by the sender's domain — this is the "cross-domain teams operate
   against the main environment folder" rule; a **per-invocation team** (e.g. team_200) → scoped to its
   domain.
3. **Write-side stamp:** sending to a universal team forces `project_id = NULL` (single mailbox), which closes
   the exact "team_100 → landed in its own inbox" bug. `"agents-os"` ≡ NULL (the two token spaces unify).
4. Backward-compatible (all existing rows NULL = hub); `send`/`capture`/`inbox` gain an optional `project_id`;
   API reuses the existing `X-Project-Id` header convention.

This is **MANAGED** (touches the shared messaging schema every session uses, cross-domain, HIGH blast-radius)
and needs cross-engine (IR#1) validation. Full design: `AOS-V5-WP-MAIL-DOMAIN-SCOPE` (see the cutover plan).
Until it lands, the binding canon remains: **spokes address `team_120`, never `team_100`.**

---

## 5. Propagation

This canon is hub-authored; the Ambassador propagates it to every spoke `_aos/methodology/` on the next
`aos_sync_all.sh --all`. Spokes treat it as a read-only snapshot.

*team_100 (hub) + team_00 | AOS_HUB_SPOKE_COMMUNICATION v1.0.0 | 2026-06-27*
