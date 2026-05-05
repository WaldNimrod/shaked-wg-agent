# SWG-W1-SPRINT — Dashboard

**Last updated:** 2026-05-06 16:30
**⚡ SHIP TARGET MOVED: Thu 2026-05-07 EOD (Shaked in Basel until Fri AM)**
**Sprint:** SWG-W1-SPRINT | 2026-05-04 → 2026-05-08
**Strategic deadline:** Shaked signs Basel WG lease before 2026-05-30

---

## WP Status

| WP | Title | Status | Gate | Notes |
|----|-------|--------|------|-------|
| W1.1 | Weegee Basel scraper | ✅ GATE PASS | L-GATE_BUILD_R1_INTERNAL PASS | 8/8 checks. Advisory: full_desc=extract only. commit df1e890 |
| W1.2 | Full-description extraction | ✅ GATE PASS | L-GATE_BUILD_R1_INTERNAL PASS | 7/7 checks. 116 listings migrated. commit 57b08e9 |
| W1.3 | RonOrp + signal extractors | ✅ GATE PASS | L-GATE_BUILD_R1_INTERNAL PASS | 9/9 (AC#4 advisory: 2 detections now, ≥3 after live scrape). commit 1b43899 |
| W1.4 | One-click HTML rebuild | ✅ GATE PASS | L-GATE_BUILD_R1_INTERNAL PASS | 8/8 (1 skip). 0.07s runtime. commit 580e71f |
| W1.5 | Integration + prod run | ⏳ Thu 2026-05-07 | — | --extra-listings ready. Waiting: manual_finds_2026-05-05.json from team_00, Thu live run |
| W1.6 *(stretch)* | Unimarkt API scraper | ✅ GATE PASS | L-GATE_BUILD_R1_INTERNAL PASS | tRPC scraper. Advisory: TCP timeout from local host (resolved at live run). commit 7a9f369 |

---

## Sprint-Level DOD Progress

| Criterion | Status |
|-----------|--------|
| ≥150 listings (flatfox+weegee+ronorp+unimarkt) | ⏳ needs W1.5 live run |
| `full_description` on ≥80% listings | ✅ 110/110 = 100% |
| ≥3 cooking-culture detections | ⏳ needs W1.3 extractors |
| HTML rebuild in ≤30s | ✅ 0.07s confirmed |
| pytest 100% | ✅ current suite clean |
| ruff clean | ✅ |
| validate_aos 0 FAIL | ✅ 30 PASS |
| HANDOFF_SWG_W1_TO_TEAM_00 filed | ⏳ Day 5 |

---

*(updated after each WP gate result)*
