---
template: 14.2
id: ci-quality-gates-pattern
version: 1.0.0
reference_impl: TikTrack-Phoenix_AOSProject/.github/workflows/ci.yml
---

# CI Quality Gates Pattern

## Philosophy

CI is the **authoritative quality record** — it runs the full suite, not just the fast subset that pre-commit can afford. The guiding principle:

> **Block on regressions that violate correctness or safety invariants. Track everything else as informational.**

---

## Two-Tier Gate Structure

### Tier 1 — Blocking Gates (PR/branch merge blocked on failure)

These failures mean the code is provably broken or unsafe. No merge until resolved.

| Gate | What it checks | Language/Layer |
|------|---------------|---------------|
| Unit tests | Core logic correctness | Any |
| Infrastructure contract tests | API contract / DB schema correctness | Backend |
| Security scan (HIGH severity) | Known dangerous code patterns | Any |
| Build validation | UI/frontend compiles and tree-shakes cleanly | Frontend |

**Rule:** A blocking gate must have a clear pass/fail criterion and produce actionable output. "It's slow" is not a reason to make a gate informational.

### Tier 2 — Informational Gates (recorded, visible, never block merge)

These signals provide quality awareness without stopping the pipeline. Teams track them and address systematically.

| Gate | What it checks | Why informational |
|------|---------------|------------------|
| Static type checking (mypy, tsc) | Type correctness | Type debt is fixed incrementally; rarely emergency |
| Dependency audit (pip-audit, npm audit) | Known CVEs in dependencies | Many false positives; needs triage |
| Code coverage | Test coverage percentage | Coverage targets are team policy, not gate invariants |
| Extended linting (ESLint --max-warnings) | Code style warnings | Style is iterative; not a merge blocker |

---

## YAML Pattern (GitHub Actions)

```yaml
# .github/workflows/ci.yml pattern
jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      # === TIER 1: BLOCKING ===
      - name: "Unit Tests [BLOCKING]"
        run: |
          <activate_env>
          pytest tests/unit/ -q --tb=short
        # no `continue-on-error` — fail fast

      - name: "Security Scan [BLOCKING]"
        run: |
          <activate_env>
          bandit -r <src_dir>/ --exclude <venv_dir> -lll
        # no `continue-on-error`

      - name: "Frontend Build [BLOCKING]"
        working-directory: ui/
        run: npm run build
        # no `continue-on-error`

      # === TIER 2: INFORMATIONAL ===
      - name: "Type Check [INFORMATIONAL]"
        run: |
          <activate_env>
          mypy <src_dir>/ || true
        continue-on-error: true

      - name: "Dependency Audit [INFORMATIONAL]"
        run: |
          <activate_env>
          pip-audit || true
        continue-on-error: true

      - name: "ESLint [INFORMATIONAL]"
        working-directory: ui/
        run: npm run lint || true
        continue-on-error: true
```

---

## Lint Enforcement Workflow (Governance Layer)

Governance documents (`_COMMUNICATION/`, `docs-governance/`) benefit from a **separate lightweight workflow** focused on date/metadata linting. This keeps quality checks on structured markdown artifacts out of the main CI flow.

```yaml
# .github/workflows/lint-enforcement.yml pattern
jobs:
  governance-lint:
    runs-on: ubuntu-latest
    steps:
      - name: "Governance Date Lint"
        run: bash scripts/lint_governance_dates.sh
```

---

## Anti-patterns

| Anti-pattern | Why to avoid |
|-------------|-------------|
| `continue-on-error: true` on blocking gates | Defeats the purpose; errors go unnoticed |
| No `continue-on-error` on informational gates | Blocks merge on non-critical signals |
| Mixing governance lint with application tests | Different failure modes; separate workflows |
| Blocking on test coverage thresholds | Coverage is a team metric, not a gate invariant |
