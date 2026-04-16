---
standard: 11.4
id: domain-platform-separation
title: Domain/Platform Separation
version: 1.0.0
date: 2026-04-16
authority: Team 00 + Team 100
status: ACTIVE
profiles: [L0, L2, L2.5]
---

# Standard 11.4 — Domain/Platform Separation

## Principle

AOS is a **platform** — a multi-domain environment with its own governance authority. Each domain (TikTrack, SmallFarmsAgents, HobbitHome, etc.) sits as a **layer above** the platform, not inside it.

**Rule:** No domain team may audit, modify, document, or produce artifacts that govern the AOS platform layer (`agents-os/`) without explicit dual authorization.

This standard codifies the platform/domain boundary as a binding rule for all AOS-managed projects.

---

## Binding Rules (universal — applies to every domain)

### DOM-PLAT-1 — AOS Environment is Out of Scope for Domain Teams

Domain work covers the domain's own:
- Application code standards (the project codebase)
- Documentation standards (the project documentation)
- UI/UX standards (the project interface)
- Project work environment conventions (tooling and workflows)

Violations: Any artifact produced by a domain team that purports to govern, override, or document AOS-layer behavior (`agents-os/`) without Team 00 + Team 100 authorization is **invalid** and must be retracted.

### DOM-PLAT-2 — AOS Layer Extensions Require Dual Authorization

A domain **MAY extend** the AOS layer (add capabilities on top of AOS defaults for the domain's benefit). However, any extension that **overrides an AOS default** — rather than purely adding to it — requires BOTH:

1. **Team 00 written approval** — explicit authorization in a communication artifact
2. **AOS authorization** — confirmation that the AOS layer permits the override action

An extension lacking both approvals is invalid. The implementing team is responsible for obtaining both approvals **before** implementation. Post-hoc authorization is not acceptable.

**Extension vs. override distinction:**
- Extension (permitted): Adding a new domain-specific configuration key to an AOS config
- Override (requires authorization): Changing the behavior of an existing AOS mechanism

### DOM-PLAT-3 — Domain Standards Live in the Domain Repo

All product-level standards (code style, testing conventions, UI patterns, etc.) MUST be owned and stored in the domain repository (`_aos/context/` or `_COMMUNICATION/`). They must NOT be placed in `agents-os/` as domain-specific files.

---

## For Domain Teams: How to Adopt These Rules

### Step 1 — Declare domain rules in team contracts

When your domain onboards, Team 100 will propagate a `## [DOMAIN] Domain Rules` section to all `core/governance/team_*.md` files via the GCR process. Use the template at:
```
lean-kit/modules/standards-conventions/templates/DOMAIN_RULES_TEMPLATE.md
```

### Step 2 — Request AOS changes via GCR

Any change to AOS platform behavior you need → file a `GOVERNANCE_CHANGE_REQUEST` artifact in your `_COMMUNICATION/` and route to Team 00 → Team 100. Reference:
```
lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template
```

### Step 3 — Keep domain SSOT in the domain repo

Standards documents, code conventions, architecture records → stored in the domain's `_aos/context/` or `documentation/` — never in `agents-os/`.

---

## For AOS Hub: Enforcement Mechanism

The `## [DOMAIN] Domain Rules` section in all `core/governance/team_*.md` contracts (propagated to spoke `_aos/governance/`) is the primary enforcement mechanism. When Team 100 creates domain rules, they follow this process:

1. Domain team files GCR artifact in `_COMMUNICATION/team_[ID]/`
2. Team 00 approves (verbal or written communication artifact)
3. Team 100 executes: adds `## [DOMAIN] Domain Rules` section to all 16+ team contracts in `core/governance/`
4. `propagate_governance.sh --all` propagates to all registered spokes
5. Team 100 notifies domain team of completion

**Reference implementation:** TikTrack Phoenix — `lean-kit/modules/project-governance/TT_DOMAIN_RULES_CANON_v1.0.0.md`
