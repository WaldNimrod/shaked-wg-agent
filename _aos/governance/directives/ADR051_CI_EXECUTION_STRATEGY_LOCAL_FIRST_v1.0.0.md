# ADR051 — CI Execution Strategy for AOS Domains: Local-First, Minimal-Cloud, Zero-Pay

**Status:** ACCEPTED
**Date:** 2026-06-01
**Decided by:** Team 00 (Principal)
**Authors:** Team 100 (Chief System Architect)
**Track:** STANDARD (governance canon) · implementation: AOS-V4.5-WP-CI-LOCAL-MINIMAL
**Relates to:** Iron Rule #1 (cross-engine validation), Iron Rule #8 (port-registry canon),
Iron Rule #15 / ADR048 (IPv6-only WAN), ADR044 (track model), Module 12 (home-server infra),
Module 13 (monitoring — future).
**Supersedes:** the PROPOSED ADR draft embedded in
`_COMMUNICATION/team_100/TRIAGE_REPORT_AOS100_GCR_SELF_HOSTED_CI_ALL_DOMAINS_2026-06-01_v1.0.0.md`.

## Context

GCR `SELF_HOSTED_CI_ALL_DOMAINS` (TikTrack, 2026-05-31) asked whether AOS should migrate CI to
self-hosted runners on `waldhomeserver` as the standard for all domains, after TikTrack exhausted its
GitHub Actions free minutes and was blocked by the default `$0` spending limit.

Decisive operating context established by Team 00 during triage:
- **Single developer** across all domains; all team/session work runs on **one Mac** (except team_99
  on the home server).
- **Git is used for backup + deployment**, not for multi-developer collaboration.
- **No branch protection** on any `main` — CI green gates nothing today (red checks are cosmetic).
- `validate_aos.sh` already runs **locally** pre-merge and is the only cross-repo-consistent gate.

This collapses CI's primary value (multi-contributor pre-merge protection) to ~zero. The only residual
value of cloud CI is **Mac→Linux environment parity** for repos that deploy to the Linux home server.

Survey facts: only TikTrack has heavy CI (Postgres service + Selenium + nightly cron + dual runtime
matrix); the other 12 spokes run a lightweight `validate_aos.sh` check. `waldhomeserver` is a loaded
4-core/8GB SPOF already running the AOS API + hub DB on an IPv6-only WAN. Self-hosted runners carry a
standing secret-exfiltration/persistence liability and a recurring ops tax. Self-hosted runners
currently carry no per-minute GitHub charge (proposed fee postponed indefinitely).

## Decision

1. **Self-hosted CI as an all-domain standard is REJECTED.** It couples 13 domains to the most fragile
   single point in the estate and imports recurring security/availability/ops liability to solve a
   one-domain problem.
2. **Paying for a GitHub Actions tier is REJECTED as the permanent answer.** The trimmed footprint fits
   the Free tier (2,000 min/mo) at **$0**.
3. **ADOPTED: "Local-First, Minimal-Cloud, Zero-Pay."**
   - **Authoritative gate → local `pre-push` hook** on the Mac running `validate_aos.sh` (+ repo tests
     when an entrypoint exists). This is where validation effectively already happens.
   - **Cloud CI → a single minimal free-tier Linux parity job (`aos-ci-minimal.yml`), PR-to-main only,**
     kept ONLY for repos that deploy to Linux; **removed entirely** from doc/content/non-deploy repos.
   - **Mac→Linux gap → covered at deploy time by team_99**, reusing the existing health check +
     pre-deploy guard + `wan_dual_stack_probe.sh`. No generic test-harness is built (deferred).
4. **Distribution/sync:** the `pre-push` hook + installer and the `aos-ci-minimal.yml` template are
   propagated through the existing `aos_sync_all.sh` mechanism, closing the gap that
   `.github/workflows/` was never previously propagated. Future CI changes become one edit + one sync.
5. **A generic cross-repo Linux test-harness is DEFERRED** — it is the complex infrastructure this
   decision explicitly avoids; revisit only if a concrete need arises.

## Consequences

- **Positive:** $0 recurring spend; no self-hosted runner; near-zero new infra; governance CI no longer
  depends on the box it validates; clean managed runners retained only where parity matters.
- **Negative / accepted residual:** a `pre-push` hook runs in the Mac environment and will not catch
  Linux-only defects (e.g. the 2026-05-01 IPv6 class) — mitigated by the minimal cloud parity check and
  team_99 deploy verification. Hooks are bypassable (`--no-verify`) and per-clone — acceptable for a
  single disciplined operator and consistent with existing local-verification closure precedent.
- **Canon impact:** `AOS_DIRECTORY_CANON` and `AOS_GOVERNANCE_UPDATE_PROCEDURE` currently assert cloud
  CI as required; they are relaxed to local-first under the implementing WP.

## Alternatives Considered

- **(a) Full self-hosted, all domains** — REJECTED (SPOF coupling, capacity, IPv6 fragility, all-domain
  security blast radius).
- **(b) Stay GitHub-hosted + pay overage** — REJECTED as permanent (recurring spend); raising the limit
  off `$0` retained only as an optional anti-billing-bug safety, not a spend path.
- **(c) Reduce usage to fit free tier (keep cloud CI)** — partially adopted, but superseded by the
  local-first framing once the single-dev/one-Mac context was established.
- **(d) Local-first + minimal cloud parity + team_99 deploy-parity** — **ADOPTED.**

## Implementation

Tracked by **AOS-V4.5-WP-CI-LOCAL-MINIMAL** (STANDARD, 3 sprints): S1 local gate · S2 CI right-sizing +
fan-out + team_99 amendment · S3 governance close. Rollback is per-workstream and fully reversible; CI
remains non-blocking throughout. Propagated to spokes via `propagate_governance.sh` after closure.
