# BRIEF — {WP_ID} — team_100 → team_35 — v{VERSION}

**Date:** {YYYY-MM-DD}
**Author:** team_100 (Chief Architect)
**WP:** {WP_ID}
**Type:** DESIGN_BRIEF
**Target LOD stage:** LOD200 | LOD300
**Target delivery:** {YYYY-MM-DD}

---

## 1. Context (1 paragraph)

{Why does this screen/flow exist in the WP? What problem does it solve? What is the user's state immediately before they reach this screen?}

## 2. Scope

```yaml
what_to_design:
  - screen_id: "{screen_id}"
    purpose: "{one-line purpose}"
    variant_count: 4          # LOD200 default 3–5; LOD300 default 1
  # add more screens as needed

out_of_scope:
  - "{item out of scope for this pass}"
```

## 3. Audience & environment

```yaml
target_user: "{one sentence — e.g. a one-person software-house operator who...}"
device: "desktop-first {WxH}; mobile {required/deferred/not-applicable}"
input_mode: "pointer + keyboard | touch | voice | CLI-like"
language: "EN | HE | bilingual"
rtl: false
dark_mode: "required from day 1 | defer | not required"
accessibility: "{specific priorities or 'standard only'}"
```

## 4. Design language

```yaml
design_system: "{path/to/design-system} | none, explore freely"
tone: "formal-technical | neutral | playful"
brand_tokens_to_respect:
  - "{token name or description}"
```

## 5. Content samples

```yaml
# Team 35 will render these verbatim — do not write "TODO" or lorem ipsum.
samples:
  # describe the real data that screens will display
  # example:
  # senders:
  #   - name: "Yossi Levi"
  #     email: "yossi@client.co"
  #     vip: true
```

## 6. States to cover

```yaml
states_required:
  - "normal — content present"
  - "empty — first run, no data"
  # add other states required this pass

not_required_this_pass:
  - "offline"
  - "partial degradation"
```

## 7. Interactions

```yaml
primary_actions:
  - "{verb (e.g. approve, archive, open, send)}"

navigation_model: "{single-page | tabs | stack | other}"
flow_description: "{optional: describe the sequence if non-trivial}"
```

## 8. Tweak inventory (what should be live-adjustable in the prototype)

```yaml
tweaks:
  - "{tweak label} ({option A | option B | option C})"
```

## 9. Open questions / known gaps

```yaml
open_questions:
  - id: Q-A
    question: "{question text}"
    default_if_unanswered: "{what Team 35 should assume if no answer arrives}"
```

## 10. Delivery expectation

```yaml
expected_artifacts:
  - "wireframes (HTML design canvas, {N} variants × {M} screens)"
  - "prototype (1 HTML file, chosen direction, tweaks enabled)"
  - "narrative (markdown, 1 file per screen)"
  - "handoff package index"

sign_off: "{Team 00 | Team 190 | both} at {L-GATE_CONCEPT | L-GATE_DESIGN}"
revision_rounds_budgeted: 3
```
