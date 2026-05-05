# SWG-W1-SPRINT — Dashboard

**Last updated:** 2026-05-05 09:20
**Sprint:** SWG-W1-SPRINT | 2026-05-04 → 2026-05-08
**Strategic deadline:** Shaked signs Basel WG lease before 2026-05-30

---

## WP Status

| WP | Title | Status | Gate | Notes |
|----|-------|--------|------|-------|
| W1.1 | Weegee Basel scraper | 🔄 IN BUILD | L-GATE_BUILD_R1_INTERNAL pending | Sonnet sub-agent dispatched 2026-05-05 |
| W1.2 | Full-description extraction | ✅ BUILD DONE | Haiku gate in progress | Pre-done in prior session; 36/36 tests pass; 110/110 listings migrated |
| W1.3 | RonOrp + signal extractors | ⏳ PENDING W1.2 PASS | — | Will dispatch Tue EOD if W1.1/W1.2 both PASS |
| W1.4 | One-click HTML rebuild | ⏳ PENDING W1.3 PASS | — | Wave 3 — Thu |
| W1.5 | Integration + prod run | ⏳ PENDING W1.4 PASS | — | Wave 4 — Fri |

---

## Sprint-Level DOD Progress

| Criterion | Status |
|-----------|--------|
| ≥150 listings (flatfox+weegee+ronorp) | ⏳ needs W1.1+W1.3 |
| `full_description` on ≥80% listings | ✅ 110/110 = 100% |
| ≥3 cooking-culture detections | ⏳ needs W1.3 extractors |
| HTML rebuild in ≤30s | ⏳ needs W1.4 |
| pytest 100% | ✅ current suite clean |
| ruff clean | ✅ |
| validate_aos 0 FAIL | ✅ 30 PASS |
| HANDOFF_SWG_W1_TO_TEAM_00 filed | ⏳ Day 5 |

---

*(updated after each WP gate result)*
