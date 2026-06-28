---
summary: "Generate a structured Decision Brief — canonical multi-option analysis with recommendation, trade-offs."
category: decision
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8090`); (3) `http://127.0.0.1:8090` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team). **Front door (shell execution):** when running these calls from a shell, the canonical boilerplate front door is `scripts/aos_api_server_call.sh <team_id> <METHOD> <path> [curl_args]` (W5 W-S1) — it applies this same three-tier base resolution + actor headers in one place, so callers no longer hand-roll the curl/auth block.

Generate a structured Decision Brief — canonical multi-option analysis with recommendation, trade-offs, and a parseable response format for AOS decision-making.

API endpoint: `GET {HUB_API_BASE}/api/contexts/decision?topic={topic}&wp_id={wp_id}`  
(`HUB_API_BASE` defaults to `http://127.0.0.1:8090`; override via `AOS_API_BASE` env)

**Invocation:** `/AOS_decide [topic] [wp_id]`

## Phase 0 — Parse arguments

Parse `$ARGUMENTS`:
- Scan for WP ID pattern (`[A-Z]+-V\d+-WP-\S+`) → extract as `wp_id`, remainder as `topic`
- If no WP pattern → entire string is `topic`, `wp_id` is empty
- If `$ARGUMENTS` empty → **Interactive Mode**: read `_aos/roadmap.yaml` for IN_PROGRESS WPs and recent `_COMMUNICATION/team_00/` artifacts; display numbered menu; wait for user selection

## Phase 1 — Load decision context via API

```
GET {HUB_API_BASE}/api/contexts/decision?topic={topic}&wp_id={wp_id}
```

**If API unreachable:** STOP. Instruct user: `bash scripts/start_aos_api_local.sh`

Use returned `{wp_context, iron_rules, profile, decision_options_hints}` to inform the brief.

## Phase 2 — Generate Decision Brief

Using context from Phase 1, generate 2–5 options.

### Display rule (MANDATORY — human-readable, NOT code blocks)

Decision briefs carry mixed Hebrew + English content and complex trade-offs.
Rendering the option fields inside a fenced code block destroys readability —
Hebrew RTL columns collapse, indentation breaks, and the human cannot parse the
trade-offs at a glance. Therefore:

- Present each option as a **markdown `###` sub-heading** followed by a two-column
  **markdown table** (attribute → value), OR as a properly-formatted bullet list
  with bold labels. Whichever keeps the Hebrew legible in the reader's terminal/UI.
- **Never** wrap the option attributes in fenced code blocks.
- Use plain running text for descriptions; bullets for advantages/disadvantages.
- Include a **comparison matrix** (markdown table) summarizing all options on one
  screen: row=option, columns=(work cost, flexibility, alignment, risk, recommendation flag).

### Per-option attributes (required fields)

Each option presents: **What** (one sentence); **Advantages** (2–4 bullets);
**Disadvantages** (2–4 bullets); **Work cost** (LOW/MEDIUM/HIGH + who + effort);
**Dependencies** (prerequisites or "none"); **Flexibility** (HIGH/MEDIUM/LOW +
reversibility note); **Novelty** (INCREMENTAL/SIGNIFICANT/PARADIGM_SHIFT);
**Short-term impact** (next 1–2 WPs); **Long-term impact** (3–6 month strategic);
**AOS alignment** (ALIGNED/TENSION/CONFLICT + which Iron Rule); **Risk**
(LOW/MEDIUM/HIGH + primary risk).

Close the brief with: (1) one-line recommendation per question, (2) open-parameters
block listing any remaining uncertainties, (3) the response snippet below.

### Response snippet — the ONE allowed code block

Only the response collection snippet at the end of the brief is rendered as a
fenced code block (it is copy-paste input for the user). Nothing else.

```
─── תגובה / RESPONSE ────────────────────────────────────────────
decision:     [  ]        ← A / B / C / combo:A+B / defer
Q1:           [  ]        ← accept / skip / override
Q2:           [  ]        ← …
modify:                   ← (optional)
defer:                    ← (optional)
─────────────────────────────────────────────────────────────────
```

## Phase 3 — Process response

When user pastes filled response: parse `decision`, `[N]`, `modify`, `defer` fields → output DECISION RECORDED summary → offer to write `DECISION_{SLUG}_{DATE}_v1.md` to `_COMMUNICATION/team_00/`.

## Error Handling

- API 4xx/5xx → fall back to file-based context (read `_aos/roadmap.yaml` + `core/definition.yaml` directly)
- WP ID not found → warn "generating brief without WP context", continue
- No topic and no detectable decision points → show menu with free-text option only
