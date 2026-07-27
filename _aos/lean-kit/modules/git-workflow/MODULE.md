---
id: git-workflow
name: "Git Workflow Standard"
version: "1.0.0"
profile_min: L0
description: "Branch strategy, commit conventions, worktree management, and pre-session health checks."
dependencies: []
scripts:
  health_check: scripts/git_health_check.sh
---

# Module 13 — Git Workflow Standard

## Purpose
Branch strategy, commit conventions, worktree management, and pre-session health checks.

## Contents
| File | Description |
|------|-------------|
| GIT_WORKFLOW_STANDARD.md | Branch naming, commit format, session lifecycle |
| QA_GIT_CHECKLIST.md | Pre-QA git checks |
| scripts/git_health_check.sh | Automated health check (branch, worktrees, sync) |

## Scripts
- `health_check`: `scripts/git_health_check.sh`
