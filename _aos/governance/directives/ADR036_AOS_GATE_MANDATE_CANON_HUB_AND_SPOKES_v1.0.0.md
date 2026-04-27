# ADR036 — Gate Mandate Canon: Single Source of Truth (Hub + Spokes)

**Type:** Architecture Decision Record (addendum to methodology commands)  
**Status:** LOCKED  
**Date:** 2026-04-17  
**Authority:** Team 00 (principal) + Team 100 (chief architect)

---

## Decision

The **full** `/AOS_gate-mandate` procedure (defaults, Tables A/B, Phases 0–7, routing templates) lives in **one** file:

- `lean-kit/modules/validation-quality/docs/AOS_GATE_MANDATE_CANON_v1.0.0.md`

The hub and every spoke that carries a **physical** `lean-kit/` (or `_aos/lean-kit/`) copy **must** contain the same document at the paths above. `.claude/commands/AOS_gate-mandate.md` is a **pointer stub only** — no forked policy text.

---

## Rationale

1. **Cross-project parity:** TikTrack, Sandboxes, and domain repos must behave identically to agents-os for gate operations.  
2. **No drift:** Cursor, Claude Code, and Codex surfaces reference the CANON file; duplicate prose in IDE stubs caused divergence risk.  
3. **Iron Rule alignment:** One writer (Team 100 + Team 00 approval for LOCKED canon) for methodology mechanics.

---

## Compliance

| Surface | Requirement |
|---------|-------------|
| Hub `agents-os` | CANON at both `lean-kit/...` and `_aos/lean-kit/...` (physical copy) |
| Spoke projects | Same paths after `propagate_governance.sh` / lean-kit bootstrap |
| ADR031 sync table | `gate-mandate` row tracks stub + CANON version |

---

**log_entry | ADR036 | LOCKED | 2026-04-17 | AOS_gate-mandate SSoT — hub and spokes**
