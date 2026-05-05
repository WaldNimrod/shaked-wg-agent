# Session Handoff — team_100 → team_100 (NEW) — SWG-W1-SPRINT

**Generated:** 2026-05-03
**HANDOFF_DEPTH:** full
**ACTIVATION_SCOPE:** SWG-W1 5-day development sprint
**Filed by:** team_100 (current session, this conversation)
**Filed for:** team_100 (NEW session — opens fresh on Mon 2026-05-04)
**Authority:** team_00 (Owner) directive 2026-05-03
**Storage:** Spoke-native artifact (ADR034 R9 — hub API DB offline; per ADR034 R9 + 410-stub guidance, spoke-native sprint artifacts written directly without API call)

---

## 1. Identity & Recent Accomplishments

### 1.1 Who you are
You are team_100 (Chief Architect / orchestrator) of the **shaked-wg-agent** AOS spoke. Profile L0. Working directory: `/Users/nimrod/Documents/shaked-wg-agent`.

### 1.2 What just shipped (this session, 2026-05-01 → 2026-05-03)
- **v1.9 published** — `https://www.nimrod.bio/wp-content/uploads/2026/05/shaked_curated_2026-05-01.html` — 10 listings + 13 transparent score parameters + 42-row parameter matrix + mobile-first + cooking-culture badge
- **Profile v1.8** — Layer-2 client requirements integrated (hard 1000 CHF cap, no-family WG, vegetarian bonus, English preferred, noise-sensitive)
- **Source research delivered** — 3 independent agents (Perplexity / Gemini / OpenAI) converged on **Weegee + RonOrp + Unimarkt** as top expansion targets. Gemini specifically called out RonOrp as the vegan-signal source.
- **M1–M5 mandate** — earlier delivered to team_110 (profile schema + full description + wgzimmer recovery + outreach lifecycle + negative filter); status mostly unaddressed in this conversation cycle, but baseline exists.

### 1.3 Current state of the page (live)
- 10 listings curated, scored 40–74
- **Top 3 right now**: Gotthelf bioscience-WG (74), Markgräflerstr 76 (71), Gundeldingerstr 191 (65)
- Cooking-culture detected on 2 listings (Gotthelf + Gundeldingerstr) — manual flagging
- 0 explicit vegetarian/vegan signals in budget-fit listings (RonOrp integration is the documented fix)

---

## 2. Governance Contract — Iron Rules in Force

You operate under standard AOS Iron Rules:
1. Cross-engine validation: builder ≠ validator (sonnet builders, haiku validators)
2. Physical lean-kit only — no symlinks
3. Repo-internal `spec_ref` paths
4. Single logical writer on `roadmap.yaml` (skip — spoke-native)
5. L-GATE_VALIDATE_EXTERNAL waived for this sprint by Owner (5-day window)
6. Inter-team via canonical artifacts in `_COMMUNICATION/`
7. **API-only structured mutations when DB online** — currently DB at hub is offline; ADR034 R9 spoke-native fallback applies
8. Port canon (n/a here)
9. Universal team numbering ✓
10. Governance source → snapshot only ✓
11. Iron Rule #11 — `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml` are READ-ONLY snapshots
12. Iron Rule #13 — but you're allowed `_aos/work_packages/` per AOS_DIRECTORY_CANON Part 5 (RULING MSG-HUB-20260429-003-RESPONSE 2026-04-30)

**Special this sprint:** Owner waived external L-GATE_VALIDATE due to 5-day window. Sonnet ≠ haiku still satisfies cross-engine within Anthropic. Document the gap in completion bundle.

---

## 3. Sprint Context — SWG-W1-SPRINT

### 3.1 Strategic anchor
**Shaked must vacate current housing 2026-05-30.** This 5-day dev sprint (Mon 2026-05-04 → Fri 2026-05-08) builds the funnel + tools needed for the 3-week outreach phase that follows.

### 3.2 Five WPs to deliver (full spec in mandate §4)

| WP | Deliverable | Effort | Dependency |
|---|---|---:|---|
| W1.1 | Weegee.ch scraper — adds ~89 Basel WG listings | 6h | independent |
| W1.2 | Full-description extraction — unblocks signal extractors | 5h | independent |
| W1.3 | RonOrp scraper + diet/quiet/social signal extractors | 7h | depends on W1.2 |
| W1.4 | One-click HTML rebuild tool — replaces 90-min manual cycle | 5h | depends on W1.1+W1.2+W1.3 schemas |
| W1.5 | Integration test + first production re-run | 6h | final |

### 3.3 Wave dispatch plan
- **Day 1 (Mon)**: W1.1 + W1.2 in parallel sonnet sub-agents
- **Day 2-3 (Tue-Wed)**: W1.3 (after W1.2 PASS)
- **Day 4 (Thu)**: W1.4
- **Day 5 (Fri)**: W1.5 integration + production run + bundle to team_00

### 3.4 Engine matrix
- **You** (orchestrator): opus or sonnet — dispatches, tracks, commits
- **Builders**: claude-sonnet-4-6 — one per WP, parallelizable
- **Internal validators**: claude-haiku-4-5 — per gate, deterministic VC checklist
- **External validator**: WAIVED for this sprint (note in completion bundle for future backfill)

### 3.5 Token budget
Owner approved **$30-50** total for sub-agent dispatches across the 5-day sprint. Track in completion bundle.

---

## 4. Open Blockers

| Blocker | Status | Severity | Workaround |
|---|---|---|---|
| **wgzimmer.ch returns 0 listings** since 2026-04-30 | Active | High | Not in this sprint — flatfox+weegee+ronorp will compensate. M3 (wgzimmer recovery) deferred. |
| **FTP port 21 blocked outbound** | Permanent | Medium | WP REST API upload working (`upload_html_via_rest`) — see `data/shaked_curated_2026-05-01.html` upload pattern in conversation history |
| **Hub DB offline (Postgres down)** | Active 2026-05-03 | Low for this sprint | ADR034 R9 spoke-native — `_aos/roadmap.yaml` direct-edit allowed; this handoff written to spoke without API call |
| **No vegan signals in budget-fit listings** | Open | Critical for Shaked | W1.3 (RonOrp + extractors) directly addresses |
| **5-day dev window** | Hard constraint | — | If by Day 4 EOD ≥1 WP BLOCKED, file BLOCKED-FINAL to team_00 same day |
| **Manual-trigger only** | By design (Owner directive) | — | No cron jobs, no auto-scheduling. Tools are commands, not daemons. |

---

## 5. Path Forward

### 5.1 Sequence
```
Day 0 (today, 2026-05-03) — current session ends, this handoff filed
Day 1 (Mon 04.05) — pre-flight, dispatch W1.1 + W1.2
Day 2 (Tue 05.05) — dispatch W1.3 (after W1.2 PASS)
Day 3 (Wed 06.05) — W1.3 completion + W1.4 prep
Day 4 (Thu 07.05) — W1.4 + smoke test
Day 5 (Fri 08.05) — W1.5 integration + prod run + handoff to team_00
```

### 5.2 What NOT to do
- DO NOT extend dev window past Friday — Owner's hard line
- DO NOT add Unimarkt, Tutti, MeinWGZimmer to this sprint — explicitly waived
- DO NOT design dynamic UI / SPA — explicitly waived (M9 deferred indefinitely)
- DO NOT skip haiku validation — even with time pressure
- DO NOT make policy decisions — escalate to team_00 (Owner via mail/handoff)

### 5.3 What success looks like (Friday 2026-05-08 EOD)
- 5 WPs PASS internal haiku gates ✓
- New `python -m shaked_wg_agent run --profile default` returns ≥150 listings (vs ~50 today) ✓
- `python -m shaked_wg_agent rebuild-html --profile default --top 10 --out new.html` works in ≤30s ✓
- ≥3 cooking-culture detections across new corpus (vs 2 hand-found today) ✓
- HANDOFF_SWG_W1_TO_TEAM_00 filed ✓
- Owner accepts on Day 5 → outreach phase begins Monday 2026-05-11

---

## 6. ACTIVATION PROMPT

**(Copy the fenced block below into the new team_100 Cursor session — first message)**

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: SWG-W1-SPRINT — 5-day development sprint

You are team_100 (Chief Architect, orchestrator-of-record) for the
shaked-wg-agent AOS spoke. Profile L0. Working dir:
/Users/nimrod/Documents/shaked-wg-agent.

Sprint: SWG-W1-SPRINT
Window: Mon 2026-05-04 → Fri 2026-05-08 (5 working days, hard cap)
Strategic anchor: Shaked must sign Basel WG lease before 2026-05-30 (vacates current housing). This sprint builds the funnel + tooling for the 3-week outreach phase that begins 2026-05-11.

═══════════════════════════════════════════════════════════════════
PHASE 0 — READ THESE FILES IN ORDER (MANDATORY, IN THIS SEQUENCE)
═══════════════════════════════════════════════════════════════════

1. THE SPRINT MANDATE (your full assignment, 5 WP specs, dispatch plan):
   _COMMUNICATION/team_100/MANDATE_SWG_W1_SPRINT_2026-05-03_v1.0.0.md

2. THIS HANDOFF (state-of-play, blockers):
   _COMMUNICATION/team_100/HANDOFF_SELF_100_SWG-W1-SPRINT_2026-05-03_v1.0.0.md

3. PROFILE SSOT (Shaked's requirements, Layer 1 + Layer 2):
   data/profiles/default_PROFILE_POLICY.md
   data/profiles/default.json

4. CURRENT PRODUCTION ARTIFACT (the page that's live):
   data/shaked_curated_2026-05-01.html
   Live at: https://www.nimrod.bio/wp-content/uploads/2026/05/shaked_curated_2026-05-01.html

5. CANONICAL SUB-AGENT PIPELINE PATTERN (engine matrix, validation flow):
   /Users/nimrod/Documents/TikTrack-Phoenix_AOSProject/_COMMUNICATION/team_100/REPORT_TO_AOS_TEAM_100_SUB_AGENT_PIPELINE_PATTERN_2026-04-29_v1.0.0.md

6. AOS GOVERNANCE (your iron rules):
   _aos/governance/team_100.md
   CLAUDE.md  (NOTE: §"Directory Authority" has known defect — RULING MSG-HUB-20260429-003-RESPONSE supersedes for _aos/work_packages/ writes)

═══════════════════════════════════════════════════════════════════
PHASE 1 — KEY DECISIONS ALREADY RESOLVED (do NOT re-litigate)
═══════════════════════════════════════════════════════════════════

- Sprint scope: exactly 5 WPs (W1.1 Weegee, W1.2 full-desc, W1.3 RonOrp+extractors, W1.4 HTML rebuild, W1.5 integration)
- Out of scope (Owner waived): Unimarkt, Tutti, MeinWGZimmer, dynamic UI, M9, cron automation, external L-GATE_VALIDATE
- Engine matrix: opus orchestrator (you) → sonnet builders → haiku validators
- Token budget: $30-50 total for sub-agents (Owner pre-approved)
- Manual-trigger only — no daemons or schedules
- LOD path canon: _aos/work_packages/<WP>/LOD{200,400}_spec.md (Option A per RULING MSG-HUB-20260429-003-RESPONSE)
- For tactical sprint WPs (this one): WP specs ARE §4 of the mandate — no separate LOD200/300/400 docs needed
- WP IDs: SWG-W1-1 through SWG-W1-5 (use this convention in worktree paths, commit messages, verdicts)

═══════════════════════════════════════════════════════════════════
PHASE 2 — HARD CONSTRAINTS (NEVER VIOLATE)
═══════════════════════════════════════════════════════════════════

- Iron Rule #1: builder engine ≠ validator engine. sonnet ≠ haiku satisfies same-vendor tier.
- Iron Rule #7 (ADR034): if hub DB online, structured mutations via API. Currently OFFLINE — ADR034 R9 spoke-native applies.
- Iron Rule #11/#12: do NOT edit _aos/governance/, _aos/lean-kit/, _aos/project_identity.yaml. _aos/work_packages/ IS allowed for you per Part 5 ruling.
- Pre-flight checklist (mandate §6) MANDATORY before EVERY sub-agent dispatch. STOP and file BLOCKED if any check fails.
- Sub-agents author files but NEVER commit — orchestrator commits per mandate §8.
- Policy decisions (e.g., scraper can't comply with robots.txt, source moved location, schema migration risks data loss) — file CLARIFICATION_<topic>.md to team_00 mail and STOP. Do NOT decide unilaterally.
- 5-day window HARD. If Day 4 EOD ≥1 WP still BLOCKED: file BLOCKED-FINAL to team_00 same day.

═══════════════════════════════════════════════════════════════════
PHASE 3 — IMMEDIATE EXECUTION SEQUENCE
═══════════════════════════════════════════════════════════════════

Step 1 (Day 1, Mon morning): Acknowledge mandate. Run pre-flight checklist (§6).
   File: _COMMUNICATION/team_100/ACK_SWG_W1_SPRINT_v1.0.0.md
   Contents: pre-flight results + Wave-1 dispatch plan + ETA matrix.

Step 2 (Day 1, Mon morning): Dispatch Wave 1.
   - Sonnet sub-agent A → W1.1 Weegee scraper (worktree: ../shaked-wg-w1-1)
   - Sonnet sub-agent B → W1.2 full-description extraction (worktree: ../shaked-wg-w1-2)
   Use the dispatch template in mandate §7.

Step 3 (Day 1, Mon EOD): Receive both sub-agent returns.
   - Haiku validator on each (verdict file at _COMMUNICATION/team_190/)
   - Orchestrator commits each WP per mandate §8 commit-msg conventions
   - Update _COMMUNICATION/team_100/SWG-W1-PIPELINE_LOG.md
   - Update _COMMUNICATION/team_100/SWG-W1-DASHBOARD.md

Step 4 (Day 2, Tue): If W1.2 PASS → dispatch W1.3 (RonOrp + extractors).
   - Single sonnet sub-agent (more focused scope)
   - Haiku gate must be especially careful with regex patterns (false positives ruin the diet signal)

Step 5 (Day 3, Wed): W1.3 returns. After PASS → dispatch W1.4 (HTML rebuild).

Step 6 (Day 4, Thu): W1.4 returns. After PASS → orchestrator runs end-to-end smoke test:
   python -m shaked_wg_agent run --profile default
   python -m shaked_wg_agent rebuild-html --profile default --top 10 --out /tmp/test.html
   Validate output, fix any integration glitches.

Step 7 (Day 5, Fri): Live production run.
   - Real scrape against flatfox + Weegee + RonOrp
   - Rebuild HTML, upload to nimrod.bio (use existing WP REST pattern)
   - File completion bundle:
     * _COMMUNICATION/team_100/SPRINT_RUN_2026-05-08_v1.0.0.md (run report)
     * _COMMUNICATION/team_100/HANDOFF_SWG_W1_TO_TEAM_00_2026-05-08_v1.0.0.md (delivery)
     * Final SWG-W1-DASHBOARD.md state captured

═══════════════════════════════════════════════════════════════════
EXPECTED FIRST RESPONSE FROM YOU (Day 1, Mon morning, ≤10 lines)
═══════════════════════════════════════════════════════════════════

A brief readback confirming:
- You read all 6 files in Phase 0
- You understand: 5-WP sprint, sonnet builders, haiku validators, no LOD400 separate docs needed (mandate §4 IS the spec)
- The pre-flight checklist (§6) result for Day 1
- DB probe outcome (online/offline → which protocol)
- Your proposed first action: file ACK, dispatch Wave 1 (W1.1 + W1.2 parallel)

DO NOT dispatch in your first turn — first do readback + pre-flight + ACK file.

═══════════════════════════════════════════════════════════════════
SUCCESS CRITERIA (Friday 2026-05-08 EOD)
═══════════════════════════════════════════════════════════════════

DOD (full list in mandate §9):
- 5 WPs PASS internal haiku gates
- pytest 100% pass · ruff clean · validate_aos.sh 0 FAIL
- Live run returns ≥150 listings (vs ~50 today)
- Rebuild HTML in ≤30s
- ≥3 cooking-culture signals detected (vs 2 today)
- HANDOFF_SWG_W1_TO_TEAM_00 filed
- Token usage report in bundle

═══════════════════════════════════════════════════════════════════
FIRST ACTION (when you start the new session Mon morning)
═══════════════════════════════════════════════════════════════════

FIRST ACTION: Read the 6 mandatory files in Phase 0 (in order). Run the pre-flight checklist (mandate §6). File _COMMUNICATION/team_100/ACK_SWG_W1_SPRINT_v1.0.0.md with pre-flight results + Wave-1 dispatch plan. Wait for Owner confirmation OR auto-proceed if pre-flight all-green. Then dispatch W1.1 (Weegee scraper) + W1.2 (full-description) as parallel sonnet sub-agents using the §7 dispatch template.
```

---

## 7. Cross-References & Provenance

### 7.1 Sprint mandate (full WP specs)
`_COMMUNICATION/team_100/MANDATE_SWG_W1_SPRINT_2026-05-03_v1.0.0.md`

### 7.2 Profile SSOT
- `data/profiles/default.json` (live data file)
- `data/profiles/default_PROFILE_POLICY.md` (evolution log + Layer 2 client refinements)

### 7.3 Live page artifact
- File: `data/shaked_curated_2026-05-01.html` (v1.9)
- URL: `https://www.nimrod.bio/wp-content/uploads/2026/05/shaked_curated_2026-05-01.html`
- WP media id: 91345 (last upload via REST API)

### 7.4 Source research (3 independent agents, 2026-05-03)
- Perplexity report: in conversation transcript (top: WoVe, Unimarkt, Weegee)
- Gemini report: in conversation transcript (RonOrp called out as vegan-signal source)
- OpenAI report: in conversation transcript (Weegee verified 89 Basel listings live; Tutti, MeinWGZimmer, Comparis, Homegate medium-priority)

### 7.5 Earlier mandates (background, not active for this sprint)
- `_COMMUNICATION/team_110/MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0.md` (M1-M5 baseline)
- `_COMMUNICATION/team_100/GOVERNANCE_CHANGE_REQUEST_CLAUDE_MD_DIRECTORY_AUTHORITY_2026-04-30_v1.0.0.md` (CLAUDE.md fix tracking)

### 7.6 Canonical pattern reference
`/Users/nimrod/Documents/TikTrack-Phoenix_AOSProject/_COMMUNICATION/team_100/REPORT_TO_AOS_TEAM_100_SUB_AGENT_PIPELINE_PATTERN_2026-04-29_v1.0.0.md`

### 7.7 Owner contact
team_00 (Nimrod) — direct conversation. Time-sensitive escalations via mail to `_COMMUNICATION/team_00/`.

---

*END OF HANDOFF v1.0.0 — 2026-05-03 — Filed by team_100 (current session) for team_100 (NEW session, dispatched Mon 2026-05-04 morning)*
