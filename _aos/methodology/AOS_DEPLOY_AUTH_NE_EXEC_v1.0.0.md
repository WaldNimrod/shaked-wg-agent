# AOS Deploy — Authorization ≠ Execution (Shared-Resource Window)

**Version:** v1.0.0 | **Status:** ACTIVE (Train-1 / v5.2.1 DOC fold)
**Source harvest:** A6 — Deploy Authorization ≠ Execution (TikTrack D2)
**Disposition:** `file:///Users/nimrod/Documents/AOS_V5/agents-os/_COMMUNICATION/team_100/HARVEST_DISPOSITION_A1_A10_TRAIN1_2026-07-26_v1.0.0.md`
**Complements:** Iron Rule #16 / Deploy Verification Canon (prod STATE green)
**Path:** `methodology/AOS_DEPLOY_AUTH_NE_EXEC_v1.0.0.md`

---

## 1. Purpose

Owner **authorization** (signature) is not automatic **execution** when a deploy would collide with a **shared resource** another program is soaking on (e.g. pinned staging tag).

## 2. Binding rules

1. **Auth ≠ exec** — a signed deploy decision authorizes the *plan*; it does not by itself run the flip.
2. **Shared-resource window** — if execution would overwrite a shared staging/prod resource another lane depends on, **WAIT** for the owner coordination window; **never** execute that collide autonomously.
3. **Staged runbook** — prepare the exact commands / intended release / health verify (IR#16) so execution is one deliberate, owner-timed step.
4. **Green still means STATE** — when execution proceeds, Deploy Verification Canon still applies (`build_sha` + release symlink); auth≠exec is the *preflight*, not a substitute.

## 3. Minimal checklist before exec

- [ ] Authorization artifact cited
- [ ] Shared resources scanned (tags, staging slots, ports, release names)
- [ ] Collision? → hold for owner window
- [ ] Runbook staged; IR#16 verify plan ready
