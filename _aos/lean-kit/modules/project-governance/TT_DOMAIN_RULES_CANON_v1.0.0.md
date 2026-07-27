---
id: TT_DOMAIN_RULES_CANON
type: DOMAIN_RULES_REFERENCE
domain: tiktrack
authority: Team 00 + Team 100 (hub)
date: 2026-04-15
version: 1.0.0
status: ACTIVE
---

# TikTrack domain rules (TT-DOM) — canonical reference

**Read this file only when operating on TikTrack product work** (standards, specs, or code in the TikTrack Phoenix repo). Hub-only or non-TT spokes: skip.

**Hub path:** `lean-kit/modules/project-governance/TT_DOMAIN_RULES_CANON_v1.0.0.md`  
**Spoke path (physical copy):** `_aos/lean-kit/modules/project-governance/TT_DOMAIN_RULES_CANON_v1.0.0.md`

---

## TT-DOM-1 — AOS Environment is Out of Scope

Do NOT audit, modify, document, or produce artifacts that govern the AOS environment (`agents-os/`). The AOS platform is a general multi-project environment with its own governance authority separate from TikTrack.

TT-domain work covers:
- Application code standards (TikTrack Phoenix codebase)
- Documentation standards (TikTrack project documentation)
- UI/UX standards (TikTrack Phoenix interface)
- Project work environment conventions (tooling and workflows specific to TT)

Violations: Any artifact that purports to govern, override, or document AOS-layer behavior without Team 00 + Team 100 authorization is invalid and must be retracted.

## TT-DOM-2 — AOS Layer Extensions Require Dual Authorization

TikTrack MAY extend the AOS layer (add capabilities on top of AOS defaults for TT's benefit). However:

**Any extension that overrides an AOS default** — rather than purely adding to it — requires BOTH:
1. **Team 00 written approval** — explicit authorization in a communication artifact
2. **AOS authorization** — confirmation that the AOS layer permits the override action

An extension lacking both approvals is invalid. The implementing team is responsible for obtaining both approvals BEFORE implementation. Post-hoc authorization is not acceptable.

**Extension vs. override distinction:**
- Extension (permitted): Adding a new TT-specific configuration key to an AOS config
- Override (requires authorization): Changing the behavior of an existing AOS mechanism
