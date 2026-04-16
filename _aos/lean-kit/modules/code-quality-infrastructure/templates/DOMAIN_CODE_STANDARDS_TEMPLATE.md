---
template: 14.3
id: domain-code-standards
version: 1.0.0
reference_impl: TikTrack-Phoenix_AOSProject/_aos/context/CODE_STANDARDS.md
---

# [DOMAIN NAME] — Code Standards

> **Canonical document.** Anchored by Team 00.
> All WPs must comply with these standards. Team 100 adds new standards after Team 00 approval.
> Stored at `_aos/context/CODE_STANDARDS.md` — referenced from LOD documents.

---

## CS-1 — [Standard Name]

**Principle:** [One-sentence principle]

### Definition

[Describe what this standard governs and why]

### Rules

| Scenario | Policy |
|----------|--------|
| [Case 1] | [Action required] |
| [Case 2] | [Action required] |

### Scope

[What files, directories, or conditions this standard applies to]

---

## CS-2 — [Standard Name]

**Principle:** [One-sentence principle]

### [Sub-section as needed]

[Describe the standard in sufficient detail for an implementing agent to apply it without ambiguity]

### What is in scope / out of scope

| In Scope | Out of Scope |
|----------|-------------|
| [Included] | [Excluded] |

---

## CS-N — [Add further standards using the CS-1 format]

---

## How to Use This Document

1. **During WP spec (LOD400):** Reference applicable CS-N standards in each acceptance criterion. Format: `[CS-N]` inline with the AC.
2. **During implementation:** Check each CS-N for prohibited patterns before committing.
3. **During QA (Team 50):** Verify AC compliance against referenced CS-N standards.
4. **Adding a new standard:** Team 100 proposes to Team 00 → Team 00 approves → Team 100 adds CS-N+1 → version bump this file.

---

*Team 100 | [DOMAIN NAME] | [date] | v1.0.0*
*Approved: Team 00 | [date]*
