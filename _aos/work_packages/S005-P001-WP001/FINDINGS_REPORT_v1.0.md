# [L-GATE_B] — Team 10 | Israel sourcing findings | v1.0.0

## Context bundle

- Work Package: S005-P001-WP001 (Yad2 POC) — **consolidated findings release**
- Operating mode: Mode B (Solo Builder)
- Write to: `_aos/work_packages/S005-P001-WP001/` (canonical)
- Date: 2026-04-12
- Supersedes: informal summaries only; technical detail remains in [`YAD2_FEASIBILITY_REPORT.md`](YAD2_FEASIBILITY_REPORT.md)

---

## 1. Purpose of this document

This is the **version 1.0** consolidated findings report for **Israel expansion sourcing**, combining:

1. **Prior market mapping** (baseline, do not duplicate) — [`S002-RND-WP001` LOD200](../S002-RND-WP001/LOD200_S002-RND-WP001.md) and [`DECISIONS_ISRAEL_STRATEGY_v1.0.0.md`](../../../_COMMUNICATION/team_00/DECISIONS_ISRAEL_STRATEGY_v1.0.0.md).
2. **Yad2 technical POC** — [`YAD2_FEASIBILITY_REPORT.md`](YAD2_FEASIBILITY_REPORT.md) (verdict `PARTIALLY_FEASIBLE`).
3. **Product / risk stance (Team 00 direction, 2026-04-12):** we **do not** intend to operate against **explicit platform policy** of a large incumbent when the legal/reputational risk is disproportionate to a small personal tool (see Decision 1 — low business potential; proportionality).

This v1.0 report **does not replace** the POC dossier; it **routes** engineering and research to the next phase documented in [`ISRAEL_SOURCES_RESEARCH_PLAN_v1.0.md`](ISRAEL_SOURCES_RESEARCH_PLAN_v1.0.md).

---

## 2. Baseline source landscape (by reference)

**Single source of truth for the first-pass Israeli platform list (11 platforms) and competitor set (7+):**  
[`../S002-RND-WP001/LOD200_S002-RND-WP001.md`](../S002-RND-WP001/LOD200_S002-RND-WP001.md) §10 and [`../../../_COMMUNICATION/team_00/DECISIONS_ISRAEL_STRATEGY_v1.0.0.md`](../../../_COMMUNICATION/team_00/DECISIONS_ISRAEL_STRATEGY_v1.0.0.md).

**Included names (for continuity only — full parameters in RND spec):**  
Yad2, Homeless, Facebook Groups, Madlan, Janglo, OnMap, WinWin, Komo, Airbnb, Telegram, university boards; competitors e.g. Jeremy, TheFinder, Shushu, IL Rents Bot, Nester, Realta, Seenker.

**Gap vs. next phase:** RND focused on **platforms and competitors**. It did **not** deliver an exhaustive **third-party data vendor / aggregator** catalog, nor a **legal referral-only** product pattern for Yad2-class sources. That is **Phase 2** (see research plan).

---

## 3. Yad2 technical findings (summary)

**Full evidence:** [`YAD2_FEASIBILITY_REPORT.md`](YAD2_FEASIBILITY_REPORT.md), [`poc/`](poc/), [`samples/`](samples/).

**Headline:** Automated ingestion hits **ShieldSquare** / **hCaptcha**; plain HTTP is insufficient; browser automation is **volatile** (session/fingerprint-dependent). **Maintenance** non-trivial (order of **4–8 h/month** estimated in POC).

**Verdict:** `PARTIALLY_FEASIBLE` for “can we ever get HTML/JSON” — **not** equivalent to “should we run unsanctioned scraping in production.”

---

## 4. Strategic routing (post-v1.0)

| Theme | Conclusion |
|--------|------------|
| Direct unsanctioned scraping of Yad2 for core product data | **Declined** on risk posture (Team 00) — not proportional to project scope |
| Third-party / licensed / contractual data channels | **In scope** for evaluation — risk shifted to vendor diligence |
| Alternative Israeli listing sources (Homeless, social, niche) | **In scope** — already in RND; implementation follows other S005 WPs |
| **Referral / minimal-metadata UX** for Yad2 (titles + link-out + user education) | **In scope for research & legal review** — see research plan §4 |

**Impact on downstream WPs:**  
`S005-P001-WP003` (production Yad2 scraper) assumed POC-driven scraping — **revisit** with Team 00 / architect: either **cancel**, **replace** with licensed feed, or **narrow** to referral-only integration (no bulk scrape). No code change in this document.

---

## 5. Deliverables satisfied by v1.0

| Deliverable | Location |
|-------------|----------|
| Technical POC dossier | [`YAD2_FEASIBILITY_REPORT.md`](YAD2_FEASIBILITY_REPORT.md) |
| Samples & provenance | [`samples/`](samples/) |
| **Consolidated findings v1.0 (this file)** | `FINDINGS_REPORT_v1.0.md` |
| **Next research plan** | [`ISRAEL_SOURCES_RESEARCH_PLAN_v1.0.md`](ISRAEL_SOURCES_RESEARCH_PLAN_v1.0.md) |

---

## 6. Approval

| Role | Name / Team | Status |
|------|-------------|--------|
| Author | Team 10 (Builder) | Draft complete 2026-04-12 |
| Strategic alignment | Team 00 | Pending explicit sign-off if required for gate |

---

*End — FINDINGS_REPORT_v1.0.0*
