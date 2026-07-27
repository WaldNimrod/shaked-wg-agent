---
id: TEAM_50_E2E_STANDARD
version: v2.0.0
status: ACTIVE
date: 2026-06-17
authors: [team_100]
authority: Team 50 (QA) + Team 100 (Spec reviewer)
scope: AOS hub — all spokes (L2/L3 with web UI)
supersedes: v1.0.0
promoted_from: AOS-V5-M5 / QA_DEEPENING_SPEC_v1.0.0.md §1–§5 (CA13 §6)
---

# Team 50 E2E + QA Evidence Standard v2.0.0

This standard promotes the **four QA-deepening axes** (QA_DEEPENING_SPEC §1–§4) into a binding
team_50 QA procedure. It supersedes v1.0.0 (the E2E-evidence rule, preserved verbatim in §6). No new
decisions are introduced here (P12) — this is the binding restatement of decided spec content.

The mechanical enforcement of these rules ships in AOS v5 M5: `scripts/qa_enforcement.py` + validate_aos
**Check 55/56** (advisory in-hub) — made **HARD in CI** by the `cold-integration.yml` + `qa-antifalsepass`
workflow (M5-WP2). This document is the *normative* standard; those artifacts are its *implementation*.

---

## §0 — Overriding principles (apply to all four axes)

1. **A verdict is a run, not an opinion.** At every gate (L2/L3) PASS/FAIL is decided by the exit-code +
   report of a deterministic test run. An LLM agent is **never** the source of a verdict.
2. **Evidence-or-it-didn't-happen.** Every test claim is backed by an artifact: pasted run output / CI link /
   trace. A claim with no evidence = "NOT-TESTED".
3. **Hard-gate, not advisory.** The four axes are PASS conditions at the gates where they apply (§5). An axis
   failure = a gate FAIL, with a defined failure protocol (not a "note").
4. **Derived from the spec, not invented in QA.** What is tested is fixed in the WP's LOD400 (ACs + state
   matrix). QA verifies what the spec defined — a drift-free spec → build → QA chain.
5. **Toolkit is fixed (Config B′):** Playwright + pytest spine · free visual diff (`toHaveScreenshot()` /
   Lost-Pixel) · Playwright-MCP (author only) · Claude sub-agent (internal) + Cursor-Cloud-Agent (external
   explore) · GitHub-Actions fresh-clone · Merge-Queue · post-deploy smoke · Trace-Viewer. Zero new subscriptions.

---

## §1 — Q-D1 · Anti-false-pass (false confidence → mandatory evidence)

### Criterion (what a valid PASS is)
- **Every test asserts real behavior** (`expect`/`assert` on output / DOM / DB-state). A test that runs but
  checks nothing is not a test.
- **Silent-skip = FAIL.** A `skipped`/`xfail` test without an explicit reason-and-expiry is counted as a gate
  failure, not a pass.
- **"The agent saw no failure" ≠ PASS.** A PASS claim is valid only with run evidence (full output: counts + exit-code).
- **Every AC maps to a test.** An AC with no pointer to a `test-id`/`file:line` = "NOT-TESTED" (and blocks L2).

### Process
**A · In-build internal-QA contract (L1, fixed in the build-mandate template / CA7):**
1. After each increment the builder runs a **fresh Tier-1 sub-agent** with an adversarial frame:
   *"Assume the increment is broken — try to break it."*
2. The sub-agent **actually runs** (build + tests + preview) and **pastes raw output** (not "looks fine").
3. It returns an **AC↔evidence table**: per AC — `test-id`/`file:line` + output; otherwise the row is `NOT-TESTED`.
4. A `NOT-TESTED` row on an AC of the increment ⇒ the increment is not done (the builder completes it first).

**B · Deterministic CI enforcement (L2 — discipline-independent):**
1. **skip-detector:** `pytest -rs --strict-markers`; parse the summary — `skipped > 0` without an allowlist
   entry ⇒ exit≠0. In Playwright: a `test.skip`/`test.fixme` without a `reason+expiry` annotation ⇒ FAIL.
2. **allowlist-skips:** `tests/SKIP_ALLOWLIST.yaml` — every sanctioned skip carries `reason`, `owner`, `expiry`
   (date). An expired skip ⇒ FAIL. (Schema below; validator = `qa_enforcement.py allowlist`.)
3. **assertion-density check:** a lint gate — a test (`def test_*` / `test()`) with no `assert`/`expect` ⇒ FAIL.
   Implementation: AST scan in `qa_enforcement.py assertions` (validate_aos Check 55).
4. **AC-coverage table as a gate artifact:** the BUILD-gate QA report MUST include the AC↔test-id↔result table;
   an AC with no row ⇒ the verdict cannot be PASS.

### SKIP_ALLOWLIST.yaml schema
```yaml
# tests/SKIP_ALLOWLIST.yaml
skips:
  - test_id: "path/to/test.py::test_name"   # relpath-from-test-dir :: function
    reason: "why this static skip is sanctioned"
    owner: "team_NN"                          # who owns clearing it
    expiry: "YYYY-MM-DD"                       # an expired entry FAILs the gate
```
> **Implementation scope (M5-WP1 skip-detector, validated — not a relaxation of the rule).** The normative rule is
> §1's: a skip without a sanctioned reason+expiry is a FAIL. The `qa_enforcement.py` skip-detector implements this
> over **static** skip markers (`@pytest.mark.skip`/`xfail`/unconditional `skipif`) lacking an allowlist entry.
> Runtime conditional skips (`pytest.skip()` in a body; env-contracts like `requires_aos_db`) are gated-execution
> contracts governed by their declared condition — they are not the silent failure-hiding the rule targets (§1.1),
> so they are not subject to the allowlist. (Detector behavior fixed in WP1; documented here, not decided here.)

### AC↔evidence table format
| Column | Meaning |
|--------|---------|
| `AC-id` | the acceptance criterion id from the WP LOD400 |
| `test-id` | canonical test id, or `NOT-TESTED` |
| `file:line` | where the assertion lives |
| `result` | PASS / FAIL (from the run) |
| `evidence` | pasted output / CI link / trace path |

### Gate
| Level | Applies | Nature |
|-------|---------|--------|
| **L1** (internal) | Contract A — required every increment | mandate contract (discipline + framing) |
| **L2** (BUILD gate) | Enforcement B — required, deterministic | **hard-gate** (CI blocks) |
| **L3** | inherits L2 + allowlist-skip review | hard-gate |

---

## §2 — Q-D2 · Cold-integration as a hard gate

### Criterion
- **The product works integrated, not only in isolation:** fresh-clone on an ephemeral runner → hermetic env
  (lockfiles) → migrations (up + idempotent down) → start → **full regression suite green** — on the **actually-
  merged commit** (post-rebase / merge-queue), not on the PR head.
- **post-deploy smoke green** (<2 min) after every deploy — CI-green ≠ live-healthy.
- **Zero spreading damage (fleet):** at L3, affected spokes pass smoke (fleet-check).

### Process
**A · The cold-integration run** — trigger: every PR heading for merge (merge-queue) + every RC before
release/deploy. Ephemeral GitHub-Actions runner: fresh `git clone` (not a cached checkout) → install from
**lockfiles only** (`pip install -r requirements.lock` / `npm ci`; free install forbidden) → migrations up →
down-idempotence check on a throwaway DB → service start → health-wait → full regression (pytest + Playwright).
Any failing step ⇒ FAIL with trace/log as an artifact.
*Implementation (M5-WP2):* `.github/workflows/cold-integration.yml` job `cold-integration` wraps
`scripts/integration_gate.sh` (fresh local clone → drop+rebuild the isolated test DB → migrations+seed via
pg_bootstrap → full pytest → clone-portable validate_aos), plus a `down-idempotence` job (fresh rebuild + seed,
then auto-detected down→re-up of the latest migration).

**B · Merge-gate (semantic-merge-break):** enable **GitHub Merge Queue** (or post-rebase test in CI) — tests run
on the merge result, not the branch. A PR enters `main` **only** through the queue; manual queue-bypass merges are
forbidden (branch-protection). *Activation is a repo-admin action (team_00).*

**C · Post-deploy smoke (OPS, team_99):** a <2-min script — health-endpoint · one login/key-path · one DB read ·
static-assets. Runs automatically after deploy; FAIL ⇒ rollback/investigation protocol.
*Implementation (M5-WP2):* `scripts/smoke.sh` (read-only; `AOS_API_BASE`-parameterized).

**D · Fleet-check (L3 only):** a fleet-runner checks out affected spokes (from `_aos/projects.yaml`) → runs
validate_aos + a minimal smoke per spoke. A spoke failure ⇒ the release is blocked until fixed or team_00
grants a reasoned exception. *(Implementation: M5-WP6 fleet-runner.)*

**E · Failure protocol (mandatory):**
- cold-integration FAIL at the BUILD gate ⇒ the WP returns to `ACTIVE` (maker-loop); the gate is not signed.
- FAIL at L3 ⇒ the RC is `BLOCKED`; "ship-and-fix-later" is forbidden.
- On any failure: the artifact (run-link + trace) is attached to the verdict; the failure is recorded in events.

### Gate
| Level | Applies | Nature |
|-------|---------|--------|
| **L-GATE_BUILD** | A + B (fresh-clone + merge-queue) | **hard-gate** — signing condition |
| **L3** (pre-release) | A + B + C + D (full + fleet) | **hard-gate** — release condition |
| OPS/deploy | C (post-deploy smoke) | hard (rollback trigger) |

---

## §3 — Q-D3 · N×4 state-matrix coverage (the spec → build → QA chain)

The general rule: every UI surface of a WP × 4 states (**empty / loading / error / offline-DEGRADED**). CA1's
"6×4" is the special case (6 surfaces); the rule is **N×4**.

### Criterion
- **For every WP with UI:** its LOD400 contains an N×4 state matrix (CA1 §6.2 format; cell = abbreviated G/W/T +
  P9/enforcement aspect). A missing matrix = the LOD400 is not lockable (feasibility-gate).
- **Every cell = a test:** at least one deterministic test per cell, by a derivable naming convention.
- **A missing cell = FAIL** (not a warning). An N/A cell is allowed **only** if the spec declared a reasoned N/A.
- **Cell behavior is tested as written:** the assertion verifies the cell's Then (incl. copy-key when defined)
  + the row's P9 aspect.

### Process
- **Test-id convention (locked):** each cell ⇒ `states.{surface}.{state}` (e.g. `states.map.offline`,
  `states.modals_c3.error`).
- **Test body:** Given = set up the state (below) · When = load/action · Then = assert the cell's declared
  behavior (+ copy-key if defined). A P9 column ⇒ one additional per-row assertion.
- **Per-state setup (deterministic):**
  | State | Setup mechanism |
  |-------|-----------------|
  | **empty** | empty seed-fixture (clean DB / project with no WPs) |
  | **loading** | Playwright route-interception with an artificial delay → capture the skeleton before resolve |
  | **error** | route-interception returns 500/timeout; for P9-fail — real calls with an invalid payload (`422`/`400`/`403` from the server) |
  | **offline (DEGRADED)** | an SM-D fixture: simulated DB-down (stopped container / blocked connection) → degrade-banner + git-mode; **not** a global network cut alone |
- **Coverage tally (deterministic):** `qa_enforcement.py tally` reads the LOD400 markdown matrix ⇄ the actual
  `states.*` test-ids; a diff ⇒ missing cells. Runs in the BUILD-gate CI: a missing cell ⇒ exit≠0 (validate_aos
  Check 56). "QA verifies N×4" is not session-memory-dependent.

### Gate
| Level | Applies | Nature |
|-------|---------|--------|
| **LOD400-lock** | matrix exists in the spec | feasibility-gate |
| **L2** (acceptance@BUILD) | full N×4 suite + tally green | **hard-gate** |
| **L3** | the suite is part of the (accumulated) regression | hard-gate |

---

## §4 — Q-D4 · Determinism (the verdict is deterministic; the agent is author/explore)

### Criterion
- **The verdict source at L2/L3 = a Playwright/pytest run** (exit-code + report). A single LLM-judge is not a
  verdict; "an agent looked at the screens and all looked fine" is not a PASS; and a flaky agent run **alone** ≠
  BLOCK (investigate → a decisive deterministic test).
- **Visual = a deterministic diff:** `toHaveScreenshot()`/Lost-Pixel against a baseline in the repo; not an
  LLM judgment over screenshots.
- **Flaky is managed, not denied:** a flaky test goes into documented quarantine; quarantined ≠ passing.

### Process
**A · Verdict-source rule (ties to the L54 verdict ingestion):**
1. A gate's verdict artifact MUST carry a `run_evidence` field: CI link / report path + exit-code + counts. A
   verdict without `run_evidence` is **formally invalid** (ingestion rejects it). *(Bus enforcement: M3-WP6.)*
2. **Agent role split:**
   - **author** — Playwright-MCP writes/fixes tests.
   - **execute** — runs the suites and collects artifacts.
   - **explore** — Cursor-Cloud-Agent runs an exploratory pass; an explore finding is **recorded as a finding
     that converts into a new deterministic test**, it does not change a verdict directly.

   These three roles are wired into the team_50 mandate templates by **M5-WP4**.

**B · Flaky protocol:**
1. A test that fails-then-passes in the same commit (retry-pass) ⇒ marked flaky: enters quarantine
   (`@quarantine` + an entry in `SKIP_ALLOWLIST.yaml` with owner+expiry) + the trace is kept.
2. Quarantined is not counted as a pass; at L3 the quarantine list is reviewed — an expired or route-critical
   item ⇒ blocks release until fixed.
3. Flaky ceiling: global retry ≤1 (Playwright `retries: 1` in CI, `0` locally) — hiding more is forbidden.

**C · Visual protocol:**
1. Baselines live in the repo (under `tests/__screenshots__/`), per defined viewport (desktop · RTL; mobile if
   in spec).
2. Diff threshold — **single source of truth (SSoT · P11):** `policies.qa.visual_max_diff_ratio` in `policies`
   is canonical; the Playwright-config/CI is **derived from it** (loaded/injected at build, not an independent
   value). Default `0.1%`; a change = one policy update (not ad-hoc per-test, not a hand-edited config).
3. **Baseline update = human approval** (team_00/mandate): a diff marked "intentional" requires an explicit
   baseline commit referencing the WP; an agent must not update a baseline autonomously.

### Gate
| Level | Applies | Nature |
|-------|---------|--------|
| **L1** (internal) | the agent may run-and-observe, but its claims are subject to Q-D1 (evidence) | contract |
| **L2/L3** | verdict-source rule (A) + flaky (B) + visual (C) | **hard-gate** |

### Canonical Playwright config
`retries: { ci: 1, local: 0 }` · `maxDiffPixelRatio` derived from `policies.qa.visual_max_diff_ratio` · baselines
under `tests/__screenshots__/`.

---

## §5 — Where each axis applies (unified map: axis × level × gate)

| | **L1 — smoke (internal, in-build)** | **L2 — acceptance (BUILD gate, external)** | **L3 — deep (pre-release/deploy)** |
|---|---|---|---|
| **Q-D1** anti-false-pass | mandate contract (§1.A) | CI: skip-detector + assertion-lint + AC-table (§1.B) **hard** | inherits + allowlist review |
| **Q-D2** cold-integration | — | fresh-clone + merge-queue (§2.A-B) **hard** | full + post-deploy-smoke + fleet (§2.C-D) **hard** |
| **Q-D3** N×4-coverage | builder spot-checks | full N×4 suite + tally (§3) **hard** | part of the regression |
| **Q-D4** determinism | claims subject to Q-D1 | verdict=run + flaky + visual (§4) **hard** | same + quarantine review |

### Per-track applicability (from QA_DEEPENING §5)
- **STANDARD / MANAGED** — all 4 axes.
- **EXPRESS** — Q-D1 only (contract + evidence). **Explicit exception: EXPRESS-with-UI** → additionally **Q-D3
  minimum on `error` + `offline` only** (not a full N×4 matrix), on the surfaces touched. Crossing the
  complexity threshold → **bump to STANDARD** (full matrix).
- **CONTENT** — Q-D1 + Q-D4-visual on the artifact.
- **OPS** — Q-D1 + Q-D2.C (smoke).

---

## §6 — E2E evidence rule (preserved from v1.0.0)

When a QA_REQUEST covers any flow that **cannot be fully verified** by screenshot, snapshot, or MCP browser
tooling alone, the builder team MUST supply E2E evidence before the mandate may be marked PASS.

### When E2E evidence is required
| Trigger | Explanation |
|---------|-------------|
| File upload | MCP tools cannot drive `<input type="file">` — a real browser via Playwright is required |
| Multi-step interaction with state mutation | Flows where each step depends on the previous step's server-side state |
| Session-dependent state | Features that change based on prior user actions within the same session |
| Drag-and-drop / canvas interaction | Non-standard UI elements MCP screenshot tools cannot interact with |
| Any flow where MCP tooling returns no actionable signal | If the feature cannot be confirmed from screenshot + network trace alone |

When in doubt: Team 50 declares E2E required in the QA_REQUEST; the builder runs and attaches evidence before resubmission.

### When screenshot + snapshot suffices
E2E is **not** required when ALL are true: static page render · read-only data display · a single API call
visible in the network trace · form fill without file upload.

### Evidence attachment protocol
1. Run with an HTML report: `pytest tests/e2e/ --html=tests/e2e/report.html --self-contained-html`.
2. Optionally capture a trace: `pytest tests/e2e/ --tracing=on` → `test-results/<test>/trace.zip`.
3. Attach to the QA_REQUEST: HTML report → `evidence_e2e_report`; trace zip → `evidence_e2e_trace`.
4. Reference the committed path or paste the pass/fail summary into the QA_REQUEST body.

---

## §7 — Team obligations & enforcement

| Team | Obligation |
|------|-----------|
| Team 50 (QA) | Owns this standard; declares E2E required when triggered; verdicts carry `run_evidence`; flags `blocked_reason_code: e2e_evidence_missing` when evidence is absent |
| Team 20/30/10 (builders) | Run the in-build L1 contract + the required suites; attach evidence before signalling build-complete |
| Team 100 (Validator) | Confirms `run_evidence` + the AC↔test-id↔result table are present before routing the gate |
| Team 99 (OPS) | Runs the post-deploy smoke; owns the rollback/investigation protocol |
| Team 00 | Approves visual-baseline updates; grants reasoned fleet exceptions; owns merge-queue/branch-protection activation |

If a required axis fails (or required E2E evidence is missing): the QA round returns `BLOCKED` with a
`blocked_reason_code`; a round blocked for missing evidence does not count toward the resubmission count.

---

## Scaffold & implementation references
- Playwright harness: `lean-kit/modules/testing-e2e/templates/` (conftest + README templates).
- Enforcement tooling: `scripts/qa_enforcement.py` (skips / assertions / allowlist / tally) + validate_aos
  Check 55/56 (advisory in-hub).
- CI hard gates: `.github/workflows/cold-integration.yml` (cold-integration · down-idempotence · qa-antifalsepass ·
  smoke) + `scripts/smoke.sh` + `scripts/integration_gate.sh` (M5-WP2).
- Source spec: `_aos/v5_characterization/characterization/QA_DEEPENING_SPEC_v1.0.0.md` §1–§5.

---

*AOS Lean Kit — Team 50 E2E + QA Evidence Standard v2.0.0 | 2026-06-17*
*Promoted from QA_DEEPENING_SPEC §1–§5 (AOS-V5-M5-WP3) by team_100 | Supersedes v1.0.0 | Authority: Team 50 + Team 100*
