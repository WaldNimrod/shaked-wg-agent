# LOD500 Addendum — v0.2.2 (post L-GATE_B baseline)

**WP:** S001-P001-WP001  
**Parent LOD500:** `LOD500_asbuilt.md` (2026-04-10, L-GATE_B, v0.1.0 scope)  
**Addendum date:** 2026-04-11  
**Author:** Team 100 / Team 00 (domain validation close-out)

---

## Purpose

The original LOD500 captured the repository at **v0.1.0** (46 tests). The product has since advanced to **v0.2.2** with additional surface area. This addendum records **delta** only; it does not replace the historical L-GATE_B record.

---

## Version and packaging

| Item | v0.1.0 (LOD500) | v0.2.2 (current) |
|------|-----------------|------------------|
| `pyproject.toml` / `__init__.py` | 0.1.0 | **0.2.2** |
| pytest count | 46 passed | **53 passed** |

---

## New / materially changed components

| Area | Change |
|------|--------|
| Scraping | Playwright-based `wgzimmer_pw.py` path; Flatfox verification via API in `runner._verify_flatfox_via_api` |
| Publisher | `publisher/html_report.py` — dual-table UI, verified/unverified split, live validation affordances |
| Publisher | `publisher/ftps_upload.py` — FTPS upload to hosting (TLS session reuse pattern) |
| Data | `data/listings.json` — live dataset (59 listings at last audit) |
| CLI / UX | Rich tables; `status` shows scan summary and deadline |
| Quality | Ruff clean; SIM105/I001/E741 hygiene applied for gate |

---

## Spec / test alignment

- LOD400 acceptance criteria remain satisfied at v0.2.2 (53 tests, ruff 0, CLI commands, scoring cap behavior).

---

## Outstanding documentation hygiene

- Full merge of this addendum into a single LOD500 revision is **optional**; canonical gate record remains `LOD500_asbuilt.md` + this addendum until a future editorial WP.

---

*End of addendum.*
