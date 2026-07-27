# AOS Governance Operating SOP — v1.0.0

**Date:** 2026-06-07 · **Author:** team_100 · **Status:** ACTIVE
**Audience:** team_00 (Principal) — day-to-day operating reference for governance updates + distribution.
**Companion (in-app):** `core/ui/guides/AOS_GOVERNANCE_OPERATING_v1.0.0.html` (dashboard view).
**Supersedes nothing; consolidates:** `AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.0.0.md`, ADR040, ADR054, Iron Rules #2/#10/#11/#12/#13.

> **One line:** A governance change flows **request → triage → implement (in `core/` only) → distribute via `/AOS_gov-sync`**. Under **Model B (ADR054)** distribution refreshes a *git-ignored cache* in each domain — governance never touches a domain's git/branch/push/CI.

---

## 1. Intake — how a request reaches team_100 (two paths only)

| Source | Mechanism | Lands at |
|--------|-----------|----------|
| **team_00 (you)** | direct in-session, or `APPROVAL_*.md` in `_COMMUNICATION/team_00/` | team_100 executes |
| **A domain team (spoke)** | **`GOVERNANCE_CHANGE_REQUEST`** (template: `lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template`) → `_COMMUNICATION/team_XX/`, to team_100, cc team_00 | team_100 triages |

**Hard rule (IR#12 / ADR040):** a spoke may **request** but never run `/AOS_gov-sync`. Only `team_00` and `team_100` implement + distribute.

## 2. Triage — team_100's fixed decision protocol

Every inbound request → classify → one of four outcomes → always write `TRIAGE_{id}_{date}_v1.0.0.md`:

| Decision | When | Action |
|----------|------|--------|
| **IMPLEMENT-NOW** | small, well-scoped, team_00 approves in-session | edit `core/governance/` → `/AOS_gov-sync` |
| **OPEN-WP** | significant scope / CANON / constitutional | LOD100 brief → team_00 approves → WP in roadmap |
| **DEFER** | valid, not urgent | triage artifact + log in `_aos/ideas.json` |
| **REJECT** | out of scope / contradicts a locked Iron Rule | rationale artifact + notify requester |

**The dividing line:** *constitutional / fleet-wide / high-risk* (e.g. amending an Iron Rule) → **MANAGED WP** with the full gate ladder (ELIGIBILITY → SPEC → BUILD → VALIDATE + HG-1/HG-2, each gate cross-engine per ADR053). *Small fix* → IMPLEMENT-NOW.

## 3. Implement — edit the SSoT only

- Edit **`core/governance/`**, `governance/directives/ADR*`, `methodology/`, `lean-kit/` — the **source of truth**.
- **Never** edit `_aos/...` — it is a read-only snapshot/cache (IR#10/#11, one-directional).
- A constitutional text change must appear in **all** canonical sites (avoid drift — CS-6). Example: the IR#2 amendment touched 8 sites.
- If it's a WP, implementation passes the build + validation gates before distribution.

## 4. Distribute — one command, Model B mechanics

**Command:** **`/AOS_gov-sync`** (the deprecated `/AOS_gov-update` redirects here). Authority: **team_00 / team_100 only**. Thin orchestrator over `scripts/aos_sync_all.sh`.

```
/AOS_gov-sync [--scope=full|teams] [--dry-run] [--push] [--no-push] [--spoke=<id>]
```
**Always `--dry-run` first** → review the per-spoke delta → then run for real.

**What happens under Model B (ADR054):**
1. Refresh the **git-ignored cache** in each domain — `_aos/{governance,methodology,lean-kit}` (Tier A). *No commit to domain history.*
2. Render `CLAUDE.md` + `.cursorrules` from canonical templates; write the tracked stamp `_aos/AOS_GOVERNANCE_VERSION.yaml`.
3. Commit **only the tracked set** (engine-context + scripts + stamp) — governance content itself never enters the domain's git/branch/push/CI.

**Cold clone / session start:** `scripts/aos_governance_bootstrap.sh` hydrates the cache (wired into `/AOS_session` register). **Adopt Model B on a new domain:** `scripts/aos_modelb_apply.sh <repo>`.

## 5. Commands · scripts · rules — quick map

**Commands (skills):** `/AOS_gov-sync` (distribute — the one command) · `/AOS_gov-update` (deprecated → redirects) · `/AOS_validate` (0 FAIL) · `/AOS_session` · `/AOS_gate-mandate` · `/AOS_mail`.

**Scripts:**
| Script | Role |
|--------|------|
| `scripts/aos_sync_all.sh` | engine — refresh cache + render + tracked-set commit (all spokes) |
| `lean-kit/modules/project-governance/scripts/propagate_governance.sh` | copy contracts → cache (Model-B guard: no commit/push of cache) |
| `scripts/aos_governance_bootstrap.sh` | hydrate Tier-A cache (cold clone / session start) |
| `scripts/aos_modelb_apply.sh` | adopt Model B on one domain (gitignore + untrack + stamp) |
| `scripts/lib/aos_gov_stamp.sh` | write the version stamp |
| `validate_aos.sh` | Check 50 = cache-staleness (advisory, never blocks) |

**Rules:** IR#2 (ADR054 — physical copy *or* git-ignored cache; never symlink) · IR#10/#11 (source→snapshot, one-directional) · IR#12/ADR040 (`/AOS_gov-sync` = team_00/team_100 only; others → GCR) · IR#13/ADR041 (commands = thin orchestrators) · ADR034 (DB-as-SSoT when online; `AOS-V*` WPs are file-canonical) · ADR053 (cross-engine by gate×track).

## 6. The flow in one line

> **request** (you direct / spoke GCR) → **triage** (4 outcomes + artifact) → if constitutional/large: **MANAGED WP** with cross-engine gates; else **IMPLEMENT-NOW** → **edit `core/` only** → **`/AOS_gov-sync --dry-run` then real** → Model B refreshes cache + stamp, untouching the domain's git.

---

*team_100, Chief System Architect. Canonical operating reference for AOS governance updates + distribution under Model B.*
