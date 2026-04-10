---
lod_target: LOD300
lod_status: DRAFT
track: B  # LOD300 is Track B only — do not use this template on TRACK_A
authoring_team: [TEAM_ID]
consuming_team: [TEAM_ID]
date: [YYYY-MM-DD]
version: v1.0.0
supersedes: null
---

> **Track B only.** If the work package is **TRACK_A**, skip LOD300 and proceed from LOD200 to LOD400 per the LOD Standard (Track A sequence).

# [FEATURE NAME] — LOD300 System Design

**work_package_id:** [S00X-P00X-WP00X]
**parent_lod200:** [path/to/LOD200_spec.md]

## 1. System behavior overview
[Describe what the system does at the component level. Not code — behavior.]

## 2. Component interactions
[Sequence or flow diagram (text/ASCII acceptable). Show all components that touch this feature.]

## 3. State model (if applicable)
[States, transitions, triggers. Only if new/modified state machine involved.]

## 4. Interface contracts
| Interface | Producer | Consumer | Contract |
|-----------|---------|---------|----------|
| [name] | [team] | [team] | [what is passed] |

## 5. Open design questions (resolved)
| Question | Decision | Rationale |
|---------|---------|-----------|
| [question] | [decision] | [why] |

## 6. LOD300 exit criteria
- [ ] All component interfaces defined
- [ ] All state transitions defined
- [ ] No open design questions
- [ ] Consuming team (builder) confirms: executable from this design

> **Iron Rule:** L-GATE_V validation MUST use a different engine than the builder. See `gates/L-GATE_V_VALIDATE_AND_LOCK.md`.
