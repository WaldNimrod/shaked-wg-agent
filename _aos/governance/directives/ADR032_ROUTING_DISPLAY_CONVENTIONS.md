---
id: ADR032_ROUTING_DISPLAY_CONVENTIONS
title: "ADR-032 — Agent Output Display Conventions for Routing Prompts and Activation Blocks"
version: "1.4.0"
status: APPROVED
author: Team 100 (Chief System Architect)
approved_by:
  - team_00
  - team_100
  - team_110
approval_date: "2026-04-14"
amended: "2026-04-22"
supersedes: null
adr_ref: ADR-032
wp_ref: AOS-V314-WP-CANONICAL-GATES
---

# ADR-032 — Agent Output Display Conventions for Routing Prompts and Activation Blocks

## 1. Purpose

This directive defines the canonical display rule for all agent-generated routing prompts and activation blocks across all AOS command operations and sessions. It governs when a prompt is shown inline (copy-paste block) versus referenced by file path only (cmd+click / hyperlink).

The rule exists to prevent terminal overflow for long prompts while maintaining zero-friction copy-paste for short ones. Inconsistent display behavior wastes principal time and degrades inter-agent handoff quality.

---

## 2. Scope

This convention applies to all AOS output operations that produce a routing prompt or activation block intended for another agent to consume. This includes:

| Output Type | Produced by | Section |
|-------------|------------|---------|
| Gate routing prompt | `/AOS_gate-mandate` | Phase 7 |
| Session activation prompt | `/AOS_handoff` | Section 6 |
| Decision routing prompt | `/AOS_decide` (when routing output) | Phase 5 |
| Any future command producing a copy-paste activation block | All commands | Output section |

---

## 3. Canonical Display Rule

### Rule: Always Inline (v1.2.0 — amended by Team 00, 2026-04-18)

**All routing prompts and activation blocks are ALWAYS displayed inline as a fenced copy-paste block, regardless of line count.**

The prior 30-line gate (§3.1/§3.2) is retired. The principal's workflow requires zero file-hops — every routing prompt must be immediately copy-paste ready in the chat.

```
── Copy this block ─────────────────────────────────────────
[full prompt content — fenced block]
─────────────────────────────────────────────────────────────
```

**The routing artifact file** (`_COMMUNICATION/team_100/ROUTING_*.md`) remains mandatory as the durable record and audit trail. The inline block is the **delivery mechanism**; the file is the **SSoT**.

### 3.1 — Inline Block (all prompts)

Display the full prompt directly in the conversation, inside a fenced code block:

```
── Copy this block ─────────────────────────────────────────
[prompt content here — fenced block, any length]
─────────────────────────────────────────────────────────────
```

### 3.2 — File Reference (always accompany the block)

After the inline block, also reference the file path for the permanent record:

```
Full artifact: _COMMUNICATION/team_{ID}/ROUTING_{WP}_{GATE}.md
```

### 3.3 Exception — Session handoff activation (`/AOS_handoff` Section 6)

**Unchanged.** Already inline per prior §3.3. Continues to apply: always full block in chat, file is SSoT.

---

## 4. Rationale

**v1.2.0 change:** The 30-line gate created principal friction. Every routing mandate requires a context switch to the file system before the agent session could start. The correct model is: file = audit trail, chat = delivery. Inline display always is simpler, more robust, and matches how all routing prompts are actually consumed (copy-paste into a new session).

| Scenario | v1.1.0 behavior | v1.2.0 behavior |
|----------|----------------|----------------|
| Short prompt (≤30 lines) | Inline block | Inline block (unchanged) |
| Long prompt (>30 lines) | File path only — friction | **Inline block** — zero friction |
| Handoff Section 6 | Inline (§3.3 exception) | Inline (unchanged) |

---

## 5. Implementation Locations

Every command that generates a routing prompt MUST implement this rule in its output phase. Current implementations:

| Command | Implementation Phase | Status |
|---------|---------------------|--------|
| `/AOS_gate-mandate` | Phase 4 — Mail-pointer routing prompt (§3.5) | UPDATED v1.4.0 |
| `/AOS_handoff` | Section 6 — Activation Prompt (§3.3 exception: always inline in chat) | IMPLEMENTED |
| `/AOS_gate-mandate` (Cursor equiv.) | `.cursorrules §AOS Gate Operations — Gate Mandate → Step 5` | PENDING |

---

## 6. Engine-Specific Notes

### Claude Code (`.claude/commands/`)
- Short path: fenced block with `── Copy this block ──` header
- Long path: `── Open this file ──` with Cmd+click instruction

### Cursor Composer (`.cursorrules`)
- Short path: same fenced block convention
- Long path: same file path display — Cursor renders file paths as clickable hyperlinks in chat

### OpenAI Codex (`SYSTEM_PROMPT.template`)
- Tier 1 commands (gate-mandate): §3.2 path-only for long routing prompts unless the host supports long inline paste.
- **`/AOS_handoff`:** §3.3 applies — output the full Section 6 block in the assistant response when generating handoff artifacts.

---

## 7. Cross-Reference

- **CLAUDE.md Iron Rule #7** — references this directive
- **`.cursorrules` §Output Display Convention** — Cursor-native encoding of this rule
- **`/AOS_gate-mandate` Phase 7** — gate routing implementation
- **`/AOS_handoff` Section 6** — handoff activation implementation
- **Iron Rule #5** (activation prompt copy-paste) — this directive is the implementation specification for that rule's display requirement

---

## 8. Amendment Rules

- This directive may be amended by Team 100 with Team 00 co-approval.
- The 30-line threshold may be adjusted by minor version bump (v1.1.0) with rationale.
- Engine-specific overrides require a new section in §6 and a version bump.

---

*ADR-032 | Routing Display Conventions | v1.2.0 | 2026-04-18*
*Approved by: Team 00 (System Designer) + Team 100 (Chief System Architect)*
*Amendment 2026-04-17 (v1.1.0): §3.3 — `/AOS_handoff` Section 6 always shown in chat (exception to §3.2).*
*Amendment 2026-04-18 (v1.2.0): §3 — All routing prompts always shown inline (30-line gate retired). Team 00 directive.*

---

## §3.4 — Decision Brief display (amendment 2026-04-22, v1.3.0)

**Scope:** `/AOS_decide` output and any other structured decision brief produced by hub agents.

**Problem observed (2026-04-22):** Decision briefs rendered inside fenced code blocks are unreadable to the human when the content mixes Hebrew (RTL) and English (LTR). Column alignment collapses, indentation breaks, and the user cannot parse trade-offs at a glance.

**Rule:**

1. Decision-brief content — options, attributes, comparison matrix, recommendations — MUST be rendered as human-readable markdown: `###` sub-headings per option, two-column markdown tables (attribute → value), and bullet lists for advantages/disadvantages.
2. Decision-brief content MUST NOT be wrapped in fenced code blocks.
3. The ONLY fenced code block allowed in a decision brief is the final **response snippet** at the end (the copy-paste template the user fills in).
4. Bilingual labels: Hebrew terminology appears inline in parentheses alongside English canonical labels. Example: *Advantages (יתרונות)* — not Hebrew-only, not English-only when Hebrew exists in the canon for that term.
5. A comparison matrix (one markdown table summarizing all options across key attributes) is mandatory when there are 2+ options.

**Enforcement:** `AOS_decide.md` command file Phase 2 specifies the display rule; any decision brief that violates §3.4 is a bug in the command, not a rendering preference.

**Rationale:** Hebrew is the operator's primary working language; English is the canonical documentation language (per Team 00 policy 2026-04-22: "all documentation in English, important concepts include Hebrew terminology in parallel to prevent drift"). A fenced code block defeats the bilingual mix — readable markdown preserves both.

*Amendment 2026-04-22 (v1.3.0): §3.4 — Decision brief display rule. Team 00 directive in-session.*

---

## §3.5 — Mail-pointer routing prompt (amendment 2026-04-22, v1.4.0)

**Scope:** `/AOS_gate-mandate` Phase 4 and any command that delivers a mandate or activation artifact to a team's inbox via the messaging API (ADR043).

**Background:** When a mandate is delivered via `POST /api/messaging/send` (with `activation_hint` embedded), the full mandate content is already in the recipient's inbox. Displaying a 50-line full routing prompt inline is redundant — the recipient should run `/AOS_mail` to read their task.

**Rule:**

When a mandate has been delivered to the recipient's inbox (Phase 3 of `/AOS_gate-mandate` succeeded or used fallback file write), the inline routing prompt MUST be a **mail-pointer block**, not a full context block.

**Mail-pointer block format — Round #1 (fresh session):**

```
── Copy this block ──────────────────────────────────────────────
You are Team {to_team} — {role_title}.
Repo: {repo_path} | Engine: {engine}
Read your governance contract: _aos/governance/team_{to_team}.md

ACTION: Run /AOS_mail — your mandate for {gate} / {wp_id} is in your inbox.
Verdict path: _COMMUNICATION/team_{to_team}/VERDICT_{wp_id}_{gate}_v1.0.0.md
─────────────────────────────────────────────────────────────────
```

**Mail-pointer block format — Round #2+ (continuation / resubmission):**

```
── Copy this block ──────────────────────────────────────────────
Run /AOS_mail — new task in inbox: {gate} for {wp_id} (Round #{round_number}).
─────────────────────────────────────────────────────────────────
```

**Key properties:**
1. The block is still always inline (§3.1 rule unchanged).
2. The full activation context (identity, iron rules, mandatory reads) is delivered via `activation_hint` in the MSG artifact — not in the routing prompt shown to the sender.
3. The `ROUTING_TEAM_*.md` file is no longer required when a MSG artifact is created — the MSG artifact IS the durable record. If a ROUTING file already exists it is not deleted, but new mandates no longer create one.
4. **Fallback:** If the messaging API is unavailable AND fallback file write failed, revert to the full Level 3 routing prompt (original §3.1 behavior) and note the messaging failure explicitly.

*Amendment 2026-04-22 (v1.4.0): §3.5 — Mail-pointer routing prompt. Team 110 in-session, co-approval Team 00.*
