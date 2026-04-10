---
module: 8
id: validation-quality
title: Validation & Quality
version: 3.1.1
status: ACTIVE
category: TOOLING
required_by_profiles: [L2, L3]
depends_on: [project-governance]
---

# Module 08 — Validation & Quality

## Purpose
validate_aos.sh (10 checks; respects `active_modules` in `_aos/metadata.yaml`), L-GATE_B exit criterion, Definition of Done.

## Contents
| File | Description |
|------|-------------|
| scripts/validate_aos.sh | Universal validation script (10 checks; module-scoped when `active_modules` set) |
