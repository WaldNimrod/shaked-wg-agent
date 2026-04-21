# Anti-Patterns — Briefs That Will Return a CLARIFICATION_REQUEST

Team 35 will file `CLARIFICATION_REQUEST_*` and stop for any of these. Fix before sending the mandate.

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| *"Make it look good"* | No criterion for "good" — 10 outputs, 0 converge | Declare target tone, device, design system |
| *"Like Superhuman but simpler"* | Reference-by-analogy without a declared principle — leads to shallow copy | List the exact principles you want inherited |
| *"3 variations"* with no axis | Variations of what? Color? Layout? IA? | Name the axis — "3 IA variations: flat list, grouped, timeline" |
| *Lorem ipsum everywhere* | Design decisions depend on real content; lorem produces generic output | Provide ≥3 real content samples per screen |
| *"Include all states"* | Unbounded — Team 35 will miss some, or pad | List the exact states required this pass |
| *"Match our existing app"* + no codebase link | Team 35 cannot reverse-engineer an app they cannot see | Attach codebase / screenshots / UI kit path |
| *LOD400-level detail in a LOD200 brief* | Over-specification kills exploration | At LOD200: state the problem, not the solution |
| *Brief that is one sentence in a chat message* | No artifact, no traceability, no contract | Write `BRIEF_*.md` artifact per template |
| *Multiple briefs mashed together* | Team 35 loses track of which question belongs to which WP | One brief per WP; one handoff per brief |
| *Hidden design-system override* | Creates a drift that cannot be detected later | If tokens must be extended, declare exactly which + why in §4 |
| *No sign-off owner named* | Team 35 doesn't know who approves — delivery limbo | Name the sign-off owner in §10 |
| *Deadline missing* | Team 35 cannot prioritize | Add a concrete date in §10 |
| *Variant count missing* | Default (3–5) may not match the WP scope | Always state variant count per screen |

---

*If you're unsure whether your brief covers everything, run through `checklists/before-you-brief.md` first.*
