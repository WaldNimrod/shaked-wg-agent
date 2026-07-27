# DESIGN_SYSTEM_EXTENSION_REQUEST — {WP_ID} — team_35 → team_100 — v{VERSION}

**Date:** {YYYY-MM-DD}
**Author:** team_35 (Design Studio / claude-design)
**WP:** {WP_ID}
**Brief ref:** _COMMUNICATION/team_100/{WP_ID}/BRIEF_*.md
**Design system declared:** {path/to/design-system | "none declared"}
**Status:** PENDING_APPROVAL — team_35 is blocked on this token until approved

---

## Token request

| Field | Value |
|-------|-------|
| **token_id** | `{token-name}` (e.g. `color.surface.elevated`, `spacing.xl-2`, `radius.card`) |
| **proposed_value** | `{value}` (e.g. `#1A1A2E`, `32px`, `12px`) |
| **token_category** | color \| type-scale \| spacing \| radii \| motion \| component |

## Rationale tied to brief

{Which brief section or user requirement drives this token? Quote the brief passage.}

Specifically: the token is needed because {reason the declared system does not cover this case}.

## Blast radius

{Which existing components use adjacent tokens that could be affected if this extension is applied inconsistently?}

- Component/surface: `{name}` — uses `{adjacent-token}` — impact: low \| medium \| high

## Fallback if rejected

If team_100 rejects this extension, team_35 will use `{fallback_token_or_value}` instead.
Impact of fallback: {describe visual difference from proposed token}.

## Team 35 recommendation

{Optional: why the proposed value is better than the fallback, if team_35 has a strong view.}

---

*Awaiting team_100 approval. team_35 has NOT introduced this token unilaterally (Iron Rule #12).*
