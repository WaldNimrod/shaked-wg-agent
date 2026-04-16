---
template: domain-rules
version: 1.0.0
scope: lean-kit
usage: "Copy into lean-kit/modules/project-governance/[DOMAIN]_DOMAIN_RULES_CANON_v1.0.0.md for each new domain"
---

# [DOMAIN NAME] Domain Rules — Canonical Reference

**Read this file only when operating on [DOMAIN NAME] product work** (standards, specs, or code in the [DOMAIN NAME] repo). Hub-only or non-[DOMAIN] spokes: skip.

**Hub path:** `lean-kit/modules/project-governance/[DOMAIN]_DOMAIN_RULES_CANON_v1.0.0.md`
**Spoke path (physical copy):** `_aos/lean-kit/modules/project-governance/[DOMAIN]_DOMAIN_RULES_CANON_v1.0.0.md`

---

## [DOMAIN]-DOM-1 — AOS Environment is Out of Scope

Do NOT audit, modify, document, or produce artifacts that govern the AOS environment (`agents-os/`). The AOS platform is a general multi-project environment with its own governance authority separate from [DOMAIN NAME].

[DOMAIN NAME] domain work covers:
- Application code standards ([DOMAIN NAME] codebase)
- Documentation standards ([DOMAIN NAME] project documentation)
- UI/UX standards ([DOMAIN NAME] interface)
- Project work environment conventions (tooling and workflows specific to [DOMAIN])

Violations: Any artifact that purports to govern, override, or document AOS-layer behavior without Team 00 + Team 100 authorization is invalid and must be retracted.

## [DOMAIN]-DOM-2 — AOS Layer Extensions Require Dual Authorization

[DOMAIN NAME] MAY extend the AOS layer (add capabilities on top of AOS defaults for [DOMAIN]'s benefit). However:

**Any extension that overrides an AOS default** — rather than purely adding to it — requires BOTH:
1. **Team 00 written approval** — explicit authorization in a communication artifact
2. **AOS authorization** — confirmation that the AOS layer permits the override action

An extension lacking both approvals is invalid. The implementing team is responsible for obtaining both approvals BEFORE implementation. Post-hoc authorization is not acceptable.

**Extension vs. override distinction:**
- Extension (permitted): Adding a new [DOMAIN]-specific configuration key to an AOS config
- Override (requires authorization): Changing the behavior of an existing AOS mechanism
