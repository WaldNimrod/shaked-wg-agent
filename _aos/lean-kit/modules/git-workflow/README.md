# Module 13 — Git Workflow Standard

Defines branch strategy, commit conventions, and pre-session health checks for AOS projects.

## Usage

### Run health check
```bash
bash scripts/git_health_check.sh [project_root]
```
Exit 0 = healthy, Exit 1 = warnings found (non-blocking), Exit 2 = not a git repo.

## Contents

- **GIT_WORKFLOW_STANDARD.md** — Full branch/commit/session standard
- **QA_GIT_CHECKLIST.md** — Pre-QA git verification checklist
- **scripts/git_health_check.sh** — Automated checks
