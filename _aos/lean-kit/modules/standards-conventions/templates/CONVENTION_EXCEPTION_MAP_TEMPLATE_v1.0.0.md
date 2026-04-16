# Convention exception map (template) v1.0.0

**Module:** standards-conventions (optional)  
**Use:** When a codebase-wide convention has **documented** one-off deviations (e.g. multi-file UI patterns).

| Area | Default convention (SSOT ref) | Exception location | Rationale | Approved by |
|------|-------------------------------|--------------------|-----------|-------------|
| Example | `docs/STYLE.md` §3 | `src/foo/bar.js:10-40` | Legacy hotfix | Team 00 YYYY-MM-DD |

**Rules:**
- Exceptions are **domain** records. They do not override AOS hub behavior.
- Overrides of **AOS defaults** follow Team 00 + Team 100 authorization (see `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` and domain iron rules in `core/governance/team_*.md`).
