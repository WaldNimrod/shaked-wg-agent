---
template: 14.1
id: pre-commit-pattern
version: 1.0.0
reference_impl: TikTrack-Phoenix_AOSProject/.pre-commit-config.yaml
---

# Pre-Commit Gate Pattern

## Philosophy

Pre-commit hooks serve as the **last local quality gate** before code enters version control. The guiding principle:

> **Block on defects that are cheap to fix locally; never block on aspirational checks.**

---

## Hook Categories

### Category A — Blocking (must pass for commit to proceed)

These hooks protect the invariants that, if violated, break other team members' environments or corrupt governance records.

| Hook type | When to apply | Example |
|-----------|---------------|---------|
| Unit tests (fast) | On changes to relevant source files | `pytest tests/unit/ -q` scoped to staged py files |
| Governance date lint | On `_COMMUNICATION/` / `docs-governance/` markdown | `lint_governance_dates_staged.sh` |
| Security scan (HIGH severity only) | On all Python files | `bandit -r api/ -lll` |
| Secret detection | Always | `detect-secrets-hook --baseline .secrets.baseline` |
| Build validation | On UI changes | `vite build` (verifies no broken imports) |
| Process separation guard | On team communication files | Checks cross-team boundary violations |

**Design rule:** Blocking hooks must complete in < 60 seconds for the staged changeset. If a check is slow, make it non-blocking or scope it tightly with `files:` patterns.

### Category B — Non-Blocking (run but do not block commit)

These hooks update derived artifacts or provide quality signals without blocking commit flow.

| Hook type | When to apply | Example |
|-----------|---------------|---------|
| File index auto-update | On new files in indexed dirs | `update_file_index.py` |
| Informational linting | On staged files | Code style suggestions |

---

## Configuration Pattern

```yaml
# .pre-commit-config.yaml pattern
repos:
  - repo: local
    hooks:
      # === BLOCKING GATES ===
      - id: [project]-unit-tests
        name: "Unit Tests [BLOCKING on source changes]"
        entry: bash -c 'git diff --cached --name-only | grep -Eq "^(api/.*\.py)$" || exit 0; <test_command>'
        language: system
        pass_filenames: false
        stages: [pre-commit]

      - id: [project]-governance-date-lint
        name: "Governance Date Lint [BLOCKING on _COMMUNICATION/ changes]"
        entry: scripts/lint_governance_dates_staged.sh
        language: system
        pass_filenames: false
        files: '^(_COMMUNICATION/|docs-governance/).+\.md$'
        stages: [pre-commit]

      - id: [project]-security-scan
        name: "Security Scan HIGH [BLOCKING]"
        entry: bash -c "bandit -r <src_dir>/ -lll"
        language: system
        pass_filenames: false
        types: [python]
        stages: [pre-commit]

      # === NON-BLOCKING (advisory) ===
      - id: [project]-file-index-update
        name: "File Index Auto-Update [NON-BLOCKING]"
        entry: python3 scripts/update_file_index.py
        language: system
        pass_filenames: false
        always_run: false
        files: '^<indexed_dir>/'
        stages: [pre-commit]
```

---

## Scope Rules

- Use `files:` patterns to limit hooks to relevant file types — avoids slow hooks on every commit
- Use `types: [python]` / `types: [markdown]` for language-specific hooks
- Gate on `git diff --cached --name-only` inside the hook script for fine-grained conditional execution
- Never block on `mypy`, `eslint`, or `prettier` in pre-commit — these belong in CI (Category A) or as advisory (Category B)

---

## Anti-patterns

| Anti-pattern | Why to avoid |
|-------------|-------------|
| Running full test suite on every commit | Slows commit flow; run unit tests only |
| Blocking on mypy/TypeScript errors | Type checking is iterative; better as CI informational |
| No `files:` scope on expensive hooks | Every commit runs a 30-second check unnecessarily |
| Blocking on formatting (Black, Prettier) | Use `--fix` mode or CI; don't block humans on style |
