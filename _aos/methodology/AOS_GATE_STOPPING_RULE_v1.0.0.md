# AOS Gate-Stopping Rule — Methodology Canon

**Version:** v1.0.0 | **Status:** ACTIVE (Train-1 / v5.2.1 DOC fold)
**Source harvest:** A9 — TikTrack `GATE_STOPPING_RULE` (2026-07-24)
**Disposition:** `file:///Users/nimrod/Documents/AOS_V5/agents-os/_COMMUNICATION/team_100/HARVEST_DISPOSITION_A1_A10_TRAIN1_2026-07-26_v1.0.0.md`
**Path:** `methodology/AOS_GATE_STOPPING_RULE_v1.0.0.md`

---

## 1. Purpose

Stop adversarial validation at “every finding fixed or classified,” not the unreachable “zero findings in one pass” against an uncontracted core.

## 2. Binding rules

1. **Max 2 adversarial rounds** per spec package (mandate → verdict → remediation → re-verdict).
2. After round 2, every remaining finding MUST be one of:
   - **(a)** a named deferred test (`test_id` + owner + target phase), or
   - **(b)** an explicit signed contract **non-goal**.
3. **“Revisit in build” is banned** as a residual classification.
4. **>5 unclassified CRITICAL** → **HOLD** and escalate to team_00 / team_100 — never grind rounds 3–7.

## 3. Residual register (minimal)

| finding_id | severity | classification | deferred_test_id / non_goal | owner | target_phase |
|------------|----------|----------------|----------------------------|-------|--------------|

## 4. Relationship

Complements IR#1 / dual L-GATE_VALIDATE and `AOS_FIX_CYCLE_DISCIPLINE`. Does not weaken cross-engine independence — it caps *asymptote grinding*.
