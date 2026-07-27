# QA Git Checklist

Pre-QA verification for git state. Run before L-GATE_BUILD validation.

## Checks

- [ ] On correct branch (`main` or `feature/<WP-ID>-*`)
- [ ] No uncommitted changes (`git status` clean)
- [ ] No stale worktrees (`git worktree list` shows only main)
- [ ] Pulled latest from remote (`git pull` or verify no behind)
- [ ] Commit messages follow convention (`<type>(<scope>): <desc>`)
- [ ] No merge conflicts present
- [ ] Co-Authored-By tag present on agent commits

## Automated

Run `git_health_check.sh` for automated verification of checks 1-4:
```bash
bash lean-kit/modules/git-workflow/scripts/git_health_check.sh <project_root>
```
