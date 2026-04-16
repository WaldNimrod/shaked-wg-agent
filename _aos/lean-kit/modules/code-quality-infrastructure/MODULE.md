---
module: 14
id: code-quality-infrastructure
title: Code Quality Infrastructure
version: 1.0.0
date: 2026-04-16
status: ACTIVE
category: TOOLING
required_by_profiles: []
depends_on: []
---

# Module 14 — Code Quality Infrastructure

## Purpose

Patterns and templates for domain-level code quality infrastructure: pre-commit gates, CI blocking/informational splits, and domain code standards documents. Each pattern is independently optional per project.

**Scope:** Patterns and principles only. Tool versions and specific configurations are domain responsibility.

**Reference implementation:** TikTrack Phoenix (`TikTrack-Phoenix_AOSProject/_COMMUNICATION/team_170/`, `_aos/context/CODE_STANDARDS.md`)

---

## Contents

| Template | ID | Purpose |
|----------|----|---------|
| Pre-Commit Gate Pattern | 14.1 | Philosophy and structure for pre-commit quality hooks |
| CI Quality Gates Pattern | 14.2 | Blocking vs. informational split in CI workflows |
| Domain Code Standards Template | 14.3 | Structure for `_aos/context/CODE_STANDARDS.md` |

---

## Templates

- `templates/PRE_COMMIT_PATTERN.md` — Pre-commit gate philosophy, blocking vs. non-blocking hooks, scope rules
- `templates/CI_QUALITY_GATES_PATTERN.md` — CI workflow pattern: blocking gates (must pass) vs. informational gates (tracked, not blocking)
- `templates/DOMAIN_CODE_STANDARDS_TEMPLATE.md` — Template for a domain's `CODE_STANDARDS.md` (CS-1..CS-N format)

---

## Adoption

Copy individual templates into the domain repo as needed. Do not modify hub copies.

A domain wishing to share patterns back to this module files a standard `GOVERNANCE_CHANGE_REQUEST` via Team 100.
