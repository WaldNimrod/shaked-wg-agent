---
id: AOS_OPERATING_ENVIRONMENT
version: v1.0.0
from: Team 100 (Chief System Architect)
authority: Team 00 (Principal)
date: 2026-06-01
status: ACTIVE
type: DOCTRINE
adr_ref: governance/directives/ADR052_AOS_OPERATING_ENVIRONMENT_AND_SESSION_MODEL_v1.0.0.md
program_ref: AOS-SESSION-MODEL
---

# AOS Operating Environment & Session Model

Doctrine for *how AOS is actually operated*. Mechanisms implementing it: program AOS-SESSION-MODEL
(W2 worktree isolation, W3 DB session register, W4 smart-mail/handoff, W5 DB-friction reduction).

## 1. The reality
AOS is operated by **one human (team_00)** who orchestrates **ephemeral AI sessions** across multiple
engines, **on one Mac** — plus a few **environment-isolated teams**. It is *not* a multi-developer team.
Therefore:
- **Git = backup + deploy + session isolation**, NOT synchronization between people.
- **Branches/worktrees = the mutex between concurrent sessions**, NOT collaboration boundaries between humans.
- **Coordination machinery is repointed people → sessions** (ADR052): it exists to coordinate ephemeral
  sessions and assure quality, not to coordinate humans.

What this calibrates vs. retains:
| Mechanism | Status under this doctrine |
|---|---|
| CI as contributor-gate | calibrated → local-first (ADR051) |
| Inter-team MSG ceremony (#4) | retained as **session-context + audit**; trimmed for light tracks |
| Gates | quality checkpoints (engine/human review), sized by track |
| Branch discipline (#8-adjacent, branch-guard) | **repointed** → session mutex (not people-collab) |
| Cross-engine validation (#1) | **retained/strengthened** (model-diversity, quality) |
| Artifacts/memory | **strengthened** (the nervous system across ephemeral sessions) |

## 2. Operating modes
### SOLO (default)
Single developer, **multiple concurrent sessions**, **worktree-isolated**, local-first. All routine work.

### COLLAB (canonical, dormant — requires explicit declaration)
External developer(s) participate. Activating COLLAB **re-activates multi-developer machinery**:
branch protection, PR review, CI-as-contributor-gate. COLLAB is **off by default** and must be
**explicitly declared** to activate (declaration mechanism specified by a later WP; this doctrine names
the switch, not its implementation). Until declared, AOS runs SOLO.

## 3. Special-teams environment taxonomy
Every session carries an `environment`. The **worktree-isolation rule applies ONLY to sessions sharing
the local Mac tree**; environment-isolated teams are **exempt from worktrees but still register** (W3).

| `environment` | Team(s) | Shares local Mac tree? | Worktree-isolation |
|---|---|---|---|
| `local-mac` | most sessions (team_100, 90, 191, …) | **yes** | **required** (W2/W3) |
| `cowork` | team_200 (Cowork bundle) | no (isolated env) | exempt; registers |
| `claude-design` | team_35 | no (Claude Design) | exempt; registers |
| `web-research` | team_80 | no (web env) | exempt; registers |
| `home-server` | team_99 | no (waldhomeserver) | exempt; registers |
| `cursor-cloud` | team_60 (per-domain DevOps operator; session-overridable `engine: cursor-cloud-agent`) | no (async sandboxed cloud VM) | exempt; registers |

## 4. Phasing
Session-coordination mechanisms ship **Phase-1: non-silent** — team_00 is notified of session events,
handoffs, and reaps; nothing material happens silently until proven. Promotion to **Phase-2: automatic**
is a separate, explicit team_00 decision **per mechanism**.

## 5. DB-as-SSoT (reaffirmed)
All structured session/coordination state (the active-session register, handoff records) lives in the
**DB via API** (ADR034). **Files drift** — demonstrated repeatedly — so files are for **documents only**,
never for structured state. (Per team_00 directive: the cure for drift is the DB, not file-canonical.)

## 6. Relationship to Iron Rules
- **#1 (cross-engine)** — unchanged/strengthened: builder engine ≠ validator engine (quality via model diversity).
- **#4 (inter-team = artifact)** — reframed: artifacts are **session-context carriers + audit trail** for
  ephemeral sessions, not human async-comms; volume calibrated by track.
- **#8-adjacent (branch-guard / allowlist)** — **repointed**: the purpose is concurrent-session isolation
  on one machine, not multi-dev collaboration.
- **#11/#12 (governance source→snapshot, authority)** — unchanged.
- **ADR034 (DB-SSoT)** — reaffirmed (§5).

## 7. Scope note
This is **doctrine**. The enforcement pre-flight (W2), DB register schema + API (W3), smart-mail/handoff
with auto-capture (W4), and DB-friction reduction (W5) are the implementing WPs of program AOS-SESSION-MODEL.

## 8. W2 enforcement addendum (AOS-V5-WP-CONCURRENCY-DECONFLICTION)

ADR052 W2 mandates worktree-isolation; this section makes it **enforceable** (not advisory-only).

### 8.1 Clobber guard (C1)
- Destructive git ops (`reset --hard`, dirty `checkout`, `clean -fd`, `worktree remove`) on a checkout
  with **live peer sessions** (W3 `active_sessions`) must go through **`scripts/aos_git.sh`** (or set
  `alias git='bash scripts/aos_git.sh'` in the session shell).
- Override: `AOS_CLOBBER_GUARD_FORCE=1` — logged to `_COMMUNICATION/_log/clobber_guard_force.log`.

### 8.2 Automation isolation (C2)
- Auto-commit on the **hub shared tree** is **refused** when live human sessions own that checkout
  (`hub_write_guard.sh` in `aos_sync_all` Step 4c). Automation registers on `../agents-os-automation`
  (`aos/automation` branch). Bootstrap: `bash scripts/ensure_automation_worktree.sh`.
- Spoke Step 3b commits run in each spoke repo (not the hub main tree).

### 8.3 Checkout ownership (C3)
- W3 register is SSoT for "who owns this worktree now": `bash scripts/aos_session_ctl.sh owner [path]`.
- `session_preflight.sh` **refuses** CONCURRENT shared-tree starts (exit 1) unless `--force` (logged).

### 8.4 Operator commands
- **Isolate:** `bash scripts/worktree_isolate.sh <branch> [wp_id]` (or `/AOS_session --worktree <wp>`).
- **Validate:** `validate_aos.sh` Check 52 FAILs when DB online and two live sessions share one checkout.

### 8.5 Spoke builders (interim)
Until enforcement propagates to spokes: **worktree-isolate per W2** before building; commit/push promptly.
Evidence: tiktrack S008-P015 (`MSG-20260628-082` item 3).
