# Handoff Guide — Working with Team 35 (Design Studio / Claude Design)

**Version:** 1.0.0
**Date:** 2026-04-22
**Author:** team_35 (Design Studio / claude-design) — source; team_100 — canonical normalization
**Audience:** Team 100 (Chief Architect) — *primary*; Team 00 (Principal) — *reference*
**Canonical location:** `lean-kit/modules/design-studio/HANDOFF_GUIDE_v1.0.0.md`

---

## 0 · How to read this document

- **§1–§3** — For **Team 100** (the architect who briefs Team 35). How to write a brief, what gets delivered, how to iterate.
- **§4** — Examples — good brief vs. bad brief.

Read linearly on first pass; return to §2 (the YAML brief template) every time you open a new WP.

---

## 1 · Who Team 35 is and where they sit

**Team 35 is the Design Studio running in the claude-design sandbox.**

Team 35 turns a design brief from Team 100 into visual, navigable, reviewable design artifacts — wireframes, mockups, clickable prototypes, decks, design canvases — so that interface decisions can be made and signed off **before** LOD400 (executable spec) is written.

### Where Team 35 fits in Track B

```
LOD100 research
     │
LOD200 concept ─────► Team 100 writes concept + design-studio config
     │
     ├─► L-GATE_CONCEPT (Team 190)
     │
     ▼
┌───────────────────────────────────────────────┐
│ DESIGN_STUDIO_LOOP                            │
│                                               │
│   Team 100 ──brief──► Team 35                 │
│                        │                      │
│                        ▼                      │
│                     wireframes (3–5)          │
│                        │                      │
│                        ▼                      │
│                     prototype (1)             │
│                        │                      │
│   Team 35 ──handoff──► Team 100               │
│                                               │
└───────────────────────────────────────────────┘
     │
LOD300 design ──────► Team 100 writes mockup spec using Team 35 output
     │
     ├─► L-GATE_DESIGN (Team 00 / Team 190)
     │
     ▼
LOD400 executable spec ◄── Team 35 is OUT of scope from here on
```

### Team 35's environment

- **HTML-first.** Everything Team 35 builds is HTML. React/JSX inline when interactivity is needed. No separate build step.
- **Live preview + file-based.** Team 35 sees their own output in a live preview; reads and writes to a flat project filesystem; cannot run `git`, `npm`, or shell.
- **No backend.** Prototypes can call `window.claude.complete` (Anthropic Haiku, 1024-token cap) for in-demo AI. Anything else must be mocked.
- **Starter kits available.** iOS / Android / macOS / browser device frames, deck stage, design canvas, animation stage — built in.
- **Tweaks protocol.** Any prototype delivered can expose a live-tweak panel (colors, copy, variants) that Team 100 / Team 00 can manipulate during review.
- **Handoff = file export.** Standalone-HTML bundle / PPTX / PDF / folder zip. Team 35 does not push to git, run CI, or deploy.

### What Team 35 produces (by LOD stage)

| Stage          | Output                                                                           |
| -------------- | -------------------------------------------------------------------------------- |
| LOD200 entry   | Design-studio config review (markdown advisory)                                  |
| LOD200 main    | Wireframe exploration — **3–5 distinct directions per screen**, low-fi, sketchy  |
| LOD200 exit    | One converged clickable prototype, tweak-enabled                                 |
| LOD300 main    | Hi-fi mockup grounded in the declared design system                              |
| LOD300 exit    | Screen-by-screen narrative + state diagram                                       |
| Any (on ask)   | Gate-review deck, design canvas for A/B sign-off, animated prototypes            |

### What Team 35 does NOT do

- ✗ Write LOD400 executable specs — that is Team 100.
- ✗ Write production code — that is Team 200 / Team 110 / Team 60.
- ✗ Cast gate verdicts — that is Team 190.
- ✗ Edit `_aos/` governance — that is Team 00 / Team 100 / Team 191.
- ✗ Self-initiate work — Team 35 waits for a mandate.
- ✗ Invent design tokens when a design system is declared.

---

## 2 · How to brief Team 35

### 2.1 The Golden Rule

> **A brief is a contract. A vague brief returns vague output.**

A well-specified brief takes Team 100 roughly **30–60 minutes to write**. That time is paid back 5× in reduced revision rounds.

### 2.2 Information required before Team 35 starts

Every brief MUST answer all of these. If any answer is "I don't know", either decide first or flag it as an explicit open question in the brief (not a hidden assumption).

**WHAT**
- [ ] WP ID (from `_aos/roadmap.yaml`)
- [ ] LOD stage — LOD200 (wireframes) or LOD300 (hi-fi mockup)?
- [ ] Screens / flows to design (count + names)
- [ ] Variant count requested (default: 3–5 at LOD200; 1 at LOD300)

**WHO / WHERE**
- [ ] Target user (one sentence)
- [ ] Device / viewport (mobile? desktop? both? which breakpoint?)
- [ ] Input mode (pointer, touch, keyboard, voice, CLI-like?)
- [ ] Accessibility priorities (if any specific)

**DESIGN LANGUAGE**
- [ ] Design system in play — path or "none, explore freely"
- [ ] Tone (formal / neutral / playful)
- [ ] Language (EN / HE / bilingual)
- [ ] RTL required?
- [ ] Dark mode required?

**CONTENT**
- [ ] Real content samples or structured placeholders — actual strings, not lorem ipsum
- [ ] Data shape — if a screen shows a list, describe the list item fields
- [ ] Edge cases — empty state, error state, loading state (which ones matter?)

**INTERACTION**
- [ ] Core actions per screen (verbs — "archive", "draft", "approve-VIP")
- [ ] Navigation model (tabs? stack? single-page?)
- [ ] States / flows (if non-trivial — attach a sequence or describe)

**CONSTRAINTS**
- [ ] Out-of-scope items (what Team 35 should NOT design in this pass)
- [ ] Hard constraints from Iron Rules / ADRs / prior gate verdicts
- [ ] Tweak inventory (what should be live-adjustable)

**DELIVERY**
- [ ] Expected artifacts (wireframes / prototype / deck / canvas / handoff package)
- [ ] Deadline
- [ ] Sign-off owner (Team 00? Team 190? both?)

### 2.3 Brief template

See [`templates/BRIEF.template.md`](templates/BRIEF.template.md) — copy and fill before every mandate.

File the completed brief at: `_COMMUNICATION/team_100/[WP-ID]/BRIEF_{WP_ID}_{SCOPE}_{DATE}_v{VERSION}.md`

---

## 3 · What comes back and how to iterate

### 3.1 The Handoff Package

Team 35 replies with a **Handoff Package** in `_COMMUNICATION/team_35/[WP-ID]/`:

```
_COMMUNICATION/team_35/[WP-ID]/
├── HANDOFF_{WP_ID}_{SCOPE}_{DATE}_v{VERSION}.md     ← package index (authoritative)
├── wireframes/
│   ├── {flow}_variant-A.html
│   ├── {flow}_variant-B.html
│   └── {flow}_variant-C.html
├── prototype/
│   └── {flow}_prototype.html
├── mockup/                                          ← LOD300 only
│   └── {flow}_mockup.html
├── narrative/
│   └── {flow}_screen-by-screen.md
├── state-diagram/
│   └── {flow}_states.html
└── assets/
```

See [`templates/HANDOFF.template.md`](templates/HANDOFF.template.md) for the index format.

### 3.2 Iteration protocol

| Team 100 response         | Action                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------- |
| **APPROVED**              | Fold handoff into LOD200/LOD300. Team 35 role closed for this WP.                                 |
| **APPROVED_WITH_REVISIONS** | File `REVISION_REQUEST_*.md` (atomic delta list). Team 35 ships `HANDOFF_*_v{N+1}.md`.          |
| **REJECTED**              | Rewrite the brief. Team 35 starts fresh.                                                          |

**Revision limit:** 3 rounds per WP. Beyond round 3, Team 100 must re-author the brief or escalate to Team 00.

See [`templates/REVISION_REQUEST.template.md`](templates/REVISION_REQUEST.template.md) for the revision request format.

---

## 4 · Examples — good brief vs. bad brief

### ❌ Bad brief (will return CLARIFICATION_REQUEST)

```markdown
# Brief for Team 35

Hey — we need to design the daily digest for Agros Insite.
Please make 3 options, something clean, similar to Superhuman.
Needs to look modern and work on mobile too. Thanks!
```

**Why this fails:**
- No WP ID, no LOD stage, no artifact ID
- "Clean" / "Modern" are undefined criteria
- "Similar to Superhuman" = reference-by-analogy without extracted principle
- "3 options" with no variation axis
- "Mobile too" without priority or breakpoint
- No content samples, no design system path, no state coverage, no tweak inventory, no sign-off owner

### ✅ Good brief (produces convergent output)

```markdown
# BRIEF — S001-P001-WP001 — team_100 → team_35 — v1.0.0

**Date:** 2026-05-02
**Author:** team_100
**WP:** S001-P001-WP001
**Type:** DESIGN_BRIEF
**Target LOD stage:** LOD200
**Target delivery:** 2026-05-09

## 1. Context
Phase A delivers a daily digest. Nimrod opens it once per day, skims in under 60 seconds,
takes 0–5 actions, closes it. The digest is the SOLE surface in Phase A.

## 2. Scope
what_to_design:
  - screen_id: daily_digest
    purpose: "60-second skim of what needs attention today"
    variant_count: 4
out_of_scope:
  - "Settings / VIP list editor (separate WP)"

## 3. Audience & environment
target_user: "One-person software-house operator, highly technical, opens inbox 1×/day"
device: "desktop-first 1440×900; mobile deferred"
rtl: false
dark_mode: "required from day 1"

## 4. Design language
design_system: "none yet — explore freely with hand-drawn sketch vibe (LOD200)"
tone: "formal-technical, minimal, no emoji"
brand_tokens_to_respect: []

## 5. Content samples
samples:
  counts: { processed: 127, archived: 98, drafts: 6, vip_suggestions: 2 }
  vip_suggestions:
    - sender: "yossi@client.co"
      justification: "3 replies in 30 days, domain on active client list"

## 6. States
states_required: ["normal", "empty (first run)", "high-volume (300+ emails)"]
not_required_this_pass: ["error", "offline", "loading"]

## 7. Interactions
primary_actions:
  - "approve VIP suggestion (1 click, no confirm)"
  - "open draft in edit panel"
navigation_model: "single-page; draft edit opens as side panel"

## 8. Tweak inventory
tweaks:
  - "digest_density (compact / comfortable / spacious)"
  - "vip_placement (inline / sidebar / top-banner)"
  - "header_copy (3 variants)"

## 9. Open questions
open_questions:
  - id: Q-A
    question: "Archive count — link to separate screen or inline reveal?"
    default_if_unanswered: "inline reveal with max 20 items"

## 10. Delivery expectation
expected_artifacts:
  - wireframes (design_canvas, 4 variants × 1 screen)
  - prototype (1 HTML, chosen direction, tweaks enabled)
  - handoff package index
sign_off: "Team 00 at L-GATE_CONCEPT"
revision_rounds_budgeted: 3
```

---

*End — Handoff Guide for Team 35 (Design Studio / claude-design) v1.0.0 — canonical lean-kit version 2026-04-22.*
