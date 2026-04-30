# LOD200 — SWG-PLAT-M4 — Outreach lifecycle tracking
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110)
**WP:** SWG-PLAT-M4
**Type:** LOD200_SPEC

---

## 1. Problem Statement

Every listing in `data/listings.json` has `status: "neu"` indefinitely. When Shaked contacts a
landlord, receives a reply, or rejects a listing, there is no way to record that transition. On the
next scan run, the listing resurfaces as if nothing happened, causing duplicate outreach and wasted
effort.

## 2. Solution Overview

Extend the listing schema and CLI with a minimal outreach lifecycle:

- **New status values** added to the existing `status` field (a plain string field in JSON):
  `contacted`, `replied`, `replied_negative`, `viewed`, `rejected`
- **Optional lifecycle timestamp/note fields** added to listings: `contacted_at`,
  `reply_received_at`, `rejection_reason`, `outreach_notes`
- **Four new CLI subcommands** (`mark-contacted`, `mark-replied`, `mark-viewed`, `mark-rejected`)
  that mutate `data/listings.json` atomically
- **Scan protection** in the runner: listings whose status is in the "active outreach" set are
  never reset to `neu` on re-scan
- **HTML report** renders distinct visual badges for each lifecycle status and moves
  `rejected`/`replied_negative` listings to a "Closed" section
- **Scorer** excludes `rejected`/`replied_negative` listings from top-N ranking

## 3. Architecture

### 3.1 Data Model

`data/listings.json` entries gain five optional fields:

| Field | Type | Description |
|---|---|---|
| `contacted_at` | `str \| null` | ISO-8601 datetime of first outreach |
| `reply_received_at` | `str \| null` | ISO-8601 datetime landlord replied |
| `rejection_reason` | `str \| null` | Free-text reason for rejection/decline |
| `outreach_notes` | `str \| null` | General notes on outreach progress |

The `status` field gains these new values (existing values unchanged):

| Value | Meaning |
|---|---|
| `contacted` | Shaked sent an enquiry |
| `replied` | Landlord responded positively or neutrally |
| `replied_negative` | Landlord declined or Shaked declined |
| `viewed` | Shaked viewed the property in person |
| `rejected` | Listing removed from consideration for any reason |

### 3.2 Component Map

```
shaked_wg_agent/
  __main__.py       ← four new subcommands (mark-contacted, mark-replied, mark-viewed, mark-rejected)
  outreach.py       ← NEW: atomic lifecycle mutation helpers (read/mutate/write listings.json)
  runner.py         ← scan-protection: preserve outreach statuses on re-scan
  scorer.py         ← top-N filter: exclude rejected/replied_negative
  publisher/
    html_report.py  ← new badge styles + "Closed" section for rejected/declined

tests/
  test_outreach_lifecycle.py  ← NEW: 8 test cases covering all lifecycle mutations
```

### 3.3 Key Design Decisions

1. **No new status enum / dataclass** — `status` remains a plain `str` in JSON; the CLI validates
   input at subcommand level. This avoids schema migration complexity.
2. **Atomic write** — `outreach.py` uses `write_to_temp + rename` for safe atomic updates.
3. **Scan protection is in `persistence.upsert_listing`** — already preserves `status`/`note`/`tags`
   from existing rows. The runner needs no change for upsert. However the runner also calls
   `score_listing` and re-assigns `relevance_score`, which is fine; status is a separate field.
4. **`score_all` filter** — `scorer.py` adds a pre-filter in `score_all` to skip closed listings.
5. **HTML "Closed" section** — appended below main tables, dimmed via `opacity: 0.5`.

## 4. Acceptance Criteria Summary

- CLI commands update `status` + timestamp atomically
- Re-scan does NOT reset a `contacted` listing to `neu`
- HTML report renders per-status badges and a Closed section
- Top-5 generation excludes `rejected` / `replied_negative`
- All 8 lifecycle tests pass; ruff clean on touched files
