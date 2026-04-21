# Before You Brief Team 35 — Checklist

Answer **every item** before sending the mandate. If any answer is "I don't know", decide first or flag it as an explicit open question in the brief (§9). Hidden assumptions produce revision rounds.

## WHAT

- [ ] WP ID confirmed (from `_aos/roadmap.yaml`)
- [ ] LOD stage declared — LOD200 (wireframes) or LOD300 (hi-fi mockup)?
- [ ] Every screen / flow named and counted
- [ ] Variant count stated (default: 3–5 at LOD200; 1 at LOD300)

## WHO / WHERE

- [ ] Target user described in one sentence (role + context + frequency of use)
- [ ] Device / viewport specified (desktop-first size? mobile? both? which breakpoint?)
- [ ] Input mode declared (pointer, touch, keyboard, voice, CLI-like?)
- [ ] Accessibility priorities stated (or "standard only")

## DESIGN LANGUAGE

- [ ] Design system named with path — or "none, explore freely"
- [ ] Tone declared (formal-technical / neutral / playful)
- [ ] Language declared (EN / HE / bilingual)
- [ ] RTL requirement stated (true / false)
- [ ] Dark mode requirement stated

## CONTENT

- [ ] Real content samples provided (≥3 per screen — actual strings, not lorem ipsum)
- [ ] Data shape described for any list or table screens
- [ ] Required states listed explicitly (which of: normal, empty, error, loading, high-volume?)

## INTERACTION

- [ ] Primary actions per screen listed as verbs ("archive", "approve", "open draft")
- [ ] Navigation model stated (single-page / tabs / stack / other)
- [ ] Flow sequence described if non-trivial (or attached as diagram)

## CONSTRAINTS

- [ ] Out-of-scope items listed
- [ ] Hard constraints from Iron Rules / ADRs / gate verdicts cited if relevant
- [ ] Tweak inventory declared (what should be live-adjustable)

## DELIVERY

- [ ] Expected artifacts listed (wireframes / prototype / deck / canvas / handoff package)
- [ ] Deadline stated
- [ ] Sign-off owner named (Team 00 / Team 190 / both)
- [ ] Revision rounds budgeted (default: 3)

---

*All boxes checked? File the brief as `BRIEF_{WP_ID}_{SCOPE}_{DATE}_v1.0.0.md` in `_COMMUNICATION/team_100/[WP-ID]/` and issue the mandate to Team 35.*
