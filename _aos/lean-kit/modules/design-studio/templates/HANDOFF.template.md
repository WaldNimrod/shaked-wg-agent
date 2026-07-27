# HANDOFF — {WP_ID} — team_35 → team_100 — v{VERSION}

**Date:** {YYYY-MM-DD}
**Author:** team_35 (Design Studio / claude-design)
**WP:** {WP_ID}
**Brief ref:** _COMMUNICATION/team_100/{WP_ID}/BRIEF_*.md
**Mandate ref:** _COMMUNICATION/team_100/{WP_ID}/MANDATE_*.md
**LOD stage:** LOD200 | LOD300
**Revision round:** N of 3

---

## 1. What was delivered

```yaml
files:
  - path: wireframes/{flow}_variant-A.html
    kind: wireframe
    screen: "{screen_id}"
    variant: "{short description of this direction}"
  - path: wireframes/{flow}_variant-B.html
    kind: wireframe
    screen: "{screen_id}"
    variant: "{short description of this direction}"
  - path: prototype/{flow}_prototype.html
    kind: prototype
    screen: "{screen_id}"
    notes: "Tweaks panel enabled top-right"
  # add more files as needed
```

## 2. Design decisions made (with rationale)

- {Decision 1 — what was chosen and why, grounded in brief content}
- {Decision 2}

## 3. Assumptions filled from brief defaults

- {Open question ID}: resolved to "{value}" (per brief default)

## 4. Open questions for Team 100

- {Q-N (new)}: {question text — arose during design, not covered by brief}

## 5. Tweak inventory exposed

```yaml
tweaks:
  - {tweak_key}: "{option A} | {option B} | {option C}"
```

## 6. What Team 100 must decide next

1. {Decision required — e.g. pick direction A/B/C/D at review}
2. {Resolve open question Q-N before LOD300}
3. {Sign off on design system extensions in §2}

## 7. Not done / deferred

- {Item deferred per brief §2 out-of-scope or §3 device defer}

## 8. How to review

Open `wireframes/*.html` directly in a browser.
Prototype: `prototype/{flow}_prototype.html` — toggle Tweaks panel (top-right) to try variants live.
