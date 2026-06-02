# Browser-QA Harness — AOS canon (curl vs CDP vs Lighthouse)

Status: canon · Owner: validation-quality module (team_100/team_90) · Version v1.0.0

This is the canonical, domain-neutral entry point for browser QA across all AOS domains.
Agents kept falling back to `curl` (blind to layout) because the browser harness wasn't
documented or runnable — this doc + the CDP runner (`qa_probe.mjs`) fix that. Nothing here
is site-specific: base/pages/forbidden-terms/viewports all come from config or flags.

## TL;DR — run browser QA with ZERO pip/npm installs
```bash
# N pages × M viewports: overflow + forbidden-term scan + screenshots.
# Canonical (propagated) path — works in any spoke that has the snapshot:
node _aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs --config <config.json>

# ad-hoc:
node _aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs \
     --base https://<dev-host> \
     --paths "/,/about/,/contact/" --absent "TBD,LOREM" --shots
```
A spoke MAY copy the script to its own `scripts/qa/cdp/qa_probe.mjs` for convenience —
the runner is byte-for-byte the same; only the invocation path changes.

Exit 0 = all pass; exit 1 = overflow / forbidden substring / blank title on any page.
Output: JSON summary to stdout + `<out>/qa_probe_result.json` + `<out>/screenshots/*.png`.

## Why a CDP runner (not the legacy Python harness)
- Any **legacy Python `playwright` harness** (e.g. responsive_probe / lighthouse_batch /
  axe_runner / crawl_links scripts a spoke may carry under its own `scripts/qa/`) requires
  the **Python `playwright` module**, which is frequently NOT pip-installed in agent
  shells → `ImportError` → silent fallback to curl. The Chromium
  *browser* is usually cached, but the Python *binding* isn't. Net effect: layout bugs
  (e.g. horizontal overflow) ship undetected because curl only sees HTML, never the
  rendered box model.
- `qa_probe.mjs` talks to a cached **`chrome-headless-shell`** over the DevTools Protocol
  via Node's built-in `WebSocket` — **no npm/pip dependency**, Node 18+ only. This is the
  technique that catches and confirms horizontal-overflow regressions a curl probe is
  structurally blind to.

## What each tool is for
| Need | Tool | Notes |
|------|------|-------|
| HTTP status, locks, exact HTML/alt/meta, mailto presence | `curl -k ?nc=` | deterministic, cheap, reliable — most checks |
| Layout / horizontal overflow / RTL / screenshots | `qa_probe.mjs` (this module) | renders the page; curl cannot |
| Performance / a11y / best-practices / SEO | `lighthouse` (v13) | needs **full Chrome**, not headless-shell (see below) |
| Accessibility rules / link health (legacy) | spoke-local Python `playwright` scripts | only if Python `playwright` is pip-installed |

## Lighthouse
```bash
export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # NOT chrome-headless-shell
npx --no-install lighthouse "<url>" --quiet \
  --chrome-flags="--headless=new --ignore-certificate-errors --no-sandbox" \
  --only-categories=performance,accessibility,best-practices,seo \
  --output=json --output-path=out.json
```
- **Use full `Google Chrome.app`** (or a full Chrome/Chromium binary), not
  `chrome-headless-shell` — Lighthouse needs features the shell lacks.
- **`python3` may be off-PATH** inside compound shell commands in some agent envs — read
  the result JSON with `node -e` instead, or run lighthouse and the JSON read as
  **separate** commands.

## ⚠ TLS — dev/staging may have NO valid certificate (by design)
- A **dev/staging host** (e.g. `https://<dev-host>`) often serves an invalid/expired TLS
  cert by design — many hosting setups issue a valid cert **only on the primary/prod
  domain**, never on the dev/staging URL. This is EXPECTED and is NOT a defect to fix; it
  resolves automatically when the site moves to the primary domain.
- **Production** (the primary domain) has a valid cert and must verify cleanly.
- **Consequence for all dev tooling:** pass the cert-bypass flag —
  `curl -k` · chrome `--ignore-certificate-errors` · requests `verify=False`.
  These flags are **DEV-ONLY**; production QA must run WITHOUT them. **A cert error on
  prod = a real defect.**
- Dev/staging often also sets `X-Robots-Tag: noindex` at the edge → Lighthouse **SEO**
  scores are artificially low on dev; re-measure on the primary domain. Likewise
  **Performance** (cache miss on `?nc=` + no edge CDN) reads lower on dev than prod.
  **Treat dev SEO/Perf scores as artifacts, not findings.**

## Config shape (`qa_probe.mjs --config`)
```json
{ "base": "https://<dev-host>", "out": "docs/qa/cdp/<run>",
  "viewports": [{"name":"mobile","w":375,"h":812},{"name":"desktop","w":1440,"h":900}],
  "pages": [{"name":"home","path":"/"}, ...],
  "absent": ["TBD","LOREM", ...],
  "shots": true }
```

## Portability (serves all AOS domains)
`qa_probe.mjs` hardcodes nothing site-specific — base/pages/absent/viewports come from the
config or flags, and chrome discovery walks `~/.cache/puppeteer` then falls back to system
Chrome/Chromium. The script + this doc can run unchanged in any spoke from the propagated
`_aos/` snapshot, or be copied into a spoke's own `scripts/qa/cdp/` for convenience.

---
**Provenance:** canonized from a nimrod-bio FOR_HUB methodology report (2026-06-01),
triaged by team_100 2026-06-02.
