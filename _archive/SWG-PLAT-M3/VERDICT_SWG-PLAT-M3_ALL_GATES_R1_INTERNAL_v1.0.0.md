# VERDICT — SWG-PLAT-M3 ALL GATES R1_INTERNAL
**Date:** 2026-04-30  
**Validator:** haiku internal validator sub-agent (team_110 dispatch)  
**Revision:** v1.0.0  

---

## Deterministic Verification Checklist Results

### SPEC CHECKS (L-GATE_SPEC_R1_INTERNAL)

- **[PASS] VC-S1:** File exists: `_aos/work_packages/SWG-PLAT-M3/LOD200_spec.md` (5.3K)
- **[PASS] VC-S2:** File exists: `_aos/work_packages/SWG-PLAT-M3/LOD400_spec.md` (4.8K)
- **[PASS] VC-S3:** LOD200 header has all required fields:
  - Date: `2026-04-30`
  - Author: `sonnet_sub_agent (dispatched by team_110)`
  - WP: `SWG-PLAT-M3`
  - Type: `LOD200_SPEC`
- **[PASS] VC-S4:** LOD200 documents root cause with substantive evidence (not "unknown")
  - Root cause: **Anti-bot / reCAPTCHA v3 + incorrect Playwright strategy (combined)**
  - Evidence sections: HTTP 200/401 status codes, reCAPTCHA v3 token requirements, HTML analysis, API endpoint inspection
  - File length: 5.3K (substantial content)

**Verdict: L-GATE_SPEC_R1_INTERNAL = PASS** ✓

---

### BUILD CHECKS (L-GATE_BUILD_R1_INTERNAL)

- **[PASS] VC-B1:** Old broken API interception removed from `wgzimmer_pw.py`
  - Grep: no active code intercepting `img.wgzimmer.ch` (only mentioned in comments explaining why it was removed)
- **[PASS] VC-B2:** New Playwright form-submission approach present
  - `page.evaluate("submitForm()")` found on line 138
  - Selectors `li.search-mate-entry` found in `_LISTING_SELECTORS` list (lines 82–85)
- **[PASS] VC-B3:** 0-result WARNING logging present
  - logger.warning found on lines 112, 140, 157, 170, 198
  - Specific 0-result warning on line 170: "0 listings parsed from search results page"
- **[PASS] VC-B4:** Deprecation notice in `wgzimmer.py` (module-level docstring)
  - Marked DEPRECATED with clear rationale: reCAPTCHA v3 requirement, runtime bug (price_chf field), selector drift
- **[PASS] VC-B5:** Test file exists: `tests/test_scrapers/test_wgzimmer.py` (11K)
- **[PASS] VC-B6:** Tests are mocked (no live network required)
  - Import: `from unittest.mock import MagicMock, patch` (line 9)
  - Fixture fixtures: HTML fixture at `_FIXTURE_DIR / "wgzimmer_search_page.html"`
  - Mocked Playwright page/browser/context objects in test functions
- **[PASS] VC-B7:** pytest passes with 0 failures
  - Command: `python3 -m pytest tests/ -q --tb=short`
  - Result: **144 passed in 0.37s** (0 failures)

**Verdict: L-GATE_BUILD_R1_INTERNAL = PASS** ✓

---

### VALIDATE CHECKS (L-GATE_VALIDATE_R1_INTERNAL)

- **[PASS] VC-V1:** Root cause documented with anti-bot evidence
  - HTTP status codes: 200, 401
  - HTML evidence: reCAPTCHA v3 block message and `grecaptcha.execute()` script injection detected
  - Evidence section spans ~20 lines with concrete HTTP probe results
  
- **[PASS] VC-V2:** Non-evasive workarounds documented (mandate §3 AC3)
  - Documented alternatives in LOD200_spec.md lines 66–68:
    1. Contact form → API access request
    2. Reduce scraping cadence (2-hour intervals vs. continuous)
    3. Switch to alternative aggregator (Homegate.ch with public API)

- **[PASS] VC-V3:** PARTIAL disposition acknowledged (mandate §3 AC4)
  - LOD200_spec.md line 65: "**Fallback disposition (if v3 consistently fails): PARTIAL BLOCK.**"
  - LOD400_spec.md lines 57–60: reCAPTCHA score discussion, headless browser behavioral expectations, fallback strategy on block detection

- **[PASS] VC-V4:** validate_aos.sh returns 0 FAIL
  - Command: `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
  - Result: **30 PASS / 9 SKIP / 0 FAIL**
  - L-GATE_BUILD exit criterion: SATISFIED

**Verdict: L-GATE_VALIDATE_R1_INTERNAL = PASS** ✓

---

## Overall Gate Verdicts

| Gate | Status | Notes |
|------|--------|-------|
| **L-GATE_SPEC_R1_INTERNAL** | **PASS** | All 4 spec checks passing; documentation complete and substantive. |
| **L-GATE_BUILD_R1_INTERNAL** | **PASS** | All 7 build checks passing; new implementation present, legacy deprecated, tests mocked and passing (144/144). |
| **L-GATE_VALIDATE_R1_INTERNAL** | **PASS** | All 4 validate checks passing; PARTIAL disposition properly acknowledged per mandate §3 AC4; no AOS validation failures. |

---

## Key Findings

### ✓ Strengths

1. **Complete root cause analysis:** LOD200_spec.md provides HTTP-level evidence (status codes, response body inspection, reCAPTCHA token mechanics) and CSS/DOM analysis. Not speculative.

2. **Non-invasive mitigation:** The Playwright approach executes `grecaptcha.execute()` as originally designed by the site — no evasion, no spoofing of user headers, no proxy chains. The browser context is real Chromium, and the reCAPTCHA challenge is handled transparently.

3. **Defensible PARTIAL outcome:** The spec explicitly acknowledges that reCAPTCHA v3 scoring in headless contexts is uncertain and documents legitimate fallbacks (API request, cadence reduction, aggregator switch). This is not avoidance; it is transparency.

4. **Tested implementation:** All tests mocked; no external dependencies; 144 tests passing with 0 failures. The build is deterministic and reproducible.

5. **Clean deprecation:** The legacy `wgzimmer.py` is marked DEPRECATED with clear rationale, preventing runtime crashes and confusion.

### ⚠ Advisories

1. **reCAPTCHA v3 success not guaranteed:** Headless Playwright browsers typically score ~0.1 vs. ~0.9 for real users. The site may reject even well-formed tokens. If live runs fail with block detection, the non-evasive escalation path is well documented.

2. **Selector drift risk (medium):** The spec mentions that site redesigns could break `li.search-mate-entry` again. Mitigation in code: multiple fallback selectors and WARNING logs on 0-result pages (line 170) aid rapid detection.

3. **No facility for increasing score:** The implementation does not attempt to warm sessions, vary timings, or inject synthetic user signals. This is intentional and maintains transparency. If wgzimmer requires higher scores, API access (recommended in LOD200) is the path forward.

---

## Mandate Compliance

- **WP SWG-PLAT-M3 mandate §3 AC3 (non-evasive workarounds):** ✓ Documented (API contact, cadence reduction, aggregator switch)
- **WP SWG-PLAT-M3 mandate §3 AC4 (PARTIAL disposition acceptable):** ✓ Acknowledged in both LOD200 and LOD400; risk table and fallback strategy present
- **Iron Rule #5 (team_190 final validation):** This verdict is a record of deterministic checks and advisories. Team_190 may accept or escalate based on organizational risk appetite.

---

## Recommendation

**All three gates PASS.** The implementation is complete, tested, and transparent. Recommend proceeding to deployment pending team_190 review and any site-policy escalation required by team_100 (re: reCAPTCHA usage disclosure).

---

**Validation completed:** 2026-04-30 03:45 UTC  
**Validator:** haiku (4.5)
