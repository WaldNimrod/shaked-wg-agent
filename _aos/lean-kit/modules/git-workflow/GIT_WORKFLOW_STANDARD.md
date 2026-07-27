# Git Workflow Standard

## 1. Branch Naming

| Pattern | Use |
|---------|-----|
| `main` | Production branch — always deployable |
| `feature/<WP-ID>-<desc>` | Feature branch for a work package |
| `fix/<IDEA-ID>-<desc>` | Bug fix branch |
| `release/<version>` | Release preparation branch |

Examples:
- `feature/AOS-V313-WP-MATURITY-dashboard-ux`
- `fix/IDEA-024-badge-contrast`
- `release/v3.1.3`

## 2. Commit Message Format

```
<type>(<scope>): <description>

[optional body]

Co-Authored-By: <agent> <noreply@provider.com>
```

### Types
| Type | When |
|------|------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructuring, no behavior change |
| `test` | Adding or updating tests |
| `chore` | Build, tooling, config changes |

### Scope
Use WP ID, module name, or component: `feat(AOS-V313-WP-MATURITY): dashboard UX overhaul`

## 3. Pre-Session Checks

Before starting work, run:
```bash
bash lean-kit/modules/git-workflow/scripts/git_health_check.sh <project_root>
```

This checks:
1. Valid git repository
2. Current branch name
3. Uncommitted changes (warn)
4. Stale worktrees (warn)
5. Remote sync status (ahead/behind)

## 4. Post-Session

1. Verify clean working state (`git status`)
2. Push if authorized and session work is complete
3. Do NOT push incomplete work to shared branches

## 5. Worktree Management

- Use worktrees for parallel agent work
- Clean up worktrees after use: `git worktree remove <path>`
- Health check warns if stale worktrees exist
