#!/usr/bin/env node
/**
 * qa_probe.mjs — portable, dependency-light browser QA over raw CDP.
 *
 * WHY THIS EXISTS:
 *   The legacy scripts/qa/*.py harness needs the Python `playwright` module,
 *   which is often NOT pip-installed in agent environments — so it silently
 *   fails to run and QA falls back to curl (which cannot see layout/overflow).
 *   This runner uses a chrome-headless-shell binary (already cached by puppeteer
 *   on dev machines) over the DevTools Protocol via Node's built-in WebSocket —
 *   ZERO npm/pip dependencies. Node 18+ only.
 *
 * WHAT IT CHECKS (per page, at each viewport):
 *   - HTTP-rendered scrollWidth vs clientWidth  → horizontal-overflow detection
 *     (the F-003 class of bug that curl is blind to)
 *   - document title + a caller-supplied list of "must be absent" substrings
 *     (lock-term / TBD / forbidden-text scan, IN THE RENDERED DOM incl. alt/aria)
 *   - optional full-page screenshot per (page,viewport)
 *
 * TLS NOTE (dev/staging hosts):
 *   Dev/staging hosts may serve an INVALID TLS cert BY DESIGN (a valid cert
 *   typically exists only on the primary/prod domain). Chrome is launched with
 *   --ignore-certificate-errors, which is a DEV-ONLY flag — never for prod, where
 *   a cert error is a real defect. See
 *   docs/BROWSER_QA_HARNESS_CANON_v1.0.0.md.
 *
 * USAGE:
 *   node qa_probe.mjs --config <config.json> [--out <dir>] [--shots]
 *   node qa_probe.mjs --base https://host --paths /,/about/ --absent "TBD,CDIP" [--shots]
 *
 * CONFIG JSON shape:
 *   { "base": "https://...", "viewports": [{"name":"mobile","w":375,"h":812}, ...],
 *     "pages": [{"name":"home","path":"/"}, ...],
 *     "absent": ["TBD","CDIP","אנטרופיה", ...], "shots": true }
 *
 * EXIT CODE: 0 if all pages pass (no overflow, no forbidden substring, title non-empty);
 *            1 if any failure (CI / gate friendly). Always prints JSON summary to stdout.
 */
import { spawn, execSync } from 'node:child_process';
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';

function findChrome() {
  // Prefer newest cached chrome-headless-shell; fall back to Chrome.app / chromium.
  try {
    const home = process.env.HOME;
    const out = execSync(
      `find "${home}/.cache/puppeteer" -name chrome-headless-shell -type f 2>/dev/null | sort -V | tail -1`,
      { encoding: 'utf8' }
    ).trim();
    if (out) return out;
  } catch {}
  for (const p of [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/chromium', '/usr/bin/google-chrome',
  ]) { try { execSync(`test -x "${p}"`); return p; } catch {} }
  throw new Error('No chrome-headless-shell / Chrome binary found. Install via: npx @puppeteer/browsers install chrome-headless-shell@stable');
}

function parseArgs() {
  const a = process.argv.slice(2); const o = {};
  for (let i = 0; i < a.length; i++) {
    if (a[i] === '--config') o.config = a[++i];
    else if (a[i] === '--base') o.base = a[++i];
    else if (a[i] === '--paths') o.paths = a[++i];
    else if (a[i] === '--absent') o.absent = a[++i];
    else if (a[i] === '--out') o.out = a[++i];
    else if (a[i] === '--shots') o.shots = true;
  }
  return o;
}

async function main() {
  const args = parseArgs();
  let cfg;
  if (args.config) cfg = JSON.parse(readFileSync(args.config, 'utf8'));
  else cfg = {
    base: args.base,
    pages: (args.paths || '/').split(',').map(p => ({ name: p.replace(/\W+/g, '_') || 'root', path: p })),
    absent: args.absent ? args.absent.split(',') : [],
    viewports: [{ name: 'mobile', w: 375, h: 812 }, { name: 'desktop', w: 1440, h: 900 }],
  };
  if (args.shots) cfg.shots = true;
  if (!cfg.base) { console.error('ERROR: no --base / config.base'); process.exit(2); }
  const outDir = args.out || cfg.out || 'docs/qa/cdp';
  if (cfg.shots) mkdirSync(outDir + '/screenshots', { recursive: true });

  const chrome = findChrome();
  const port = 9000 + Math.floor((Date.now() % 1000));
  const proc = spawn(chrome, [
    '--headless', '--disable-gpu', '--no-sandbox',
    `--remote-debugging-port=${port}`,
    '--ignore-certificate-errors', // DEV ONLY — dev/staging host with invalid-by-design cert (never prod)
    '--hide-scrollbars',
  ], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 1800));

  const results = []; let failures = 0;
  try {
    for (const vp of cfg.viewports) {
      for (const pg of cfg.pages) {
        const url = cfg.base.replace(/\/$/, '') + pg.path + (pg.path.includes('?') ? '&' : '?') + 'nc=' + Date.now();
        const t = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json();
        const ws = new WebSocket(t.webSocketDebuggerUrl);
        let id = 0; const pend = {};
        ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend[m.id]) pend[m.id](m); });
        await new Promise(r => ws.addEventListener('open', r));
        const send = (method, params = {}) => new Promise(res => { const i = ++id; pend[i] = res; ws.send(JSON.stringify({ id: i, method, params })); });
        await send('Page.enable'); await send('Runtime.enable');
        await send('Emulation.setDeviceMetricsOverride', { width: vp.w, height: vp.h, deviceScaleFactor: 1, mobile: vp.w < 768 });
        await send('Page.navigate', { url });
        await new Promise(r => setTimeout(r, 3200));
        const probe = `JSON.stringify({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,title:document.title,html:document.documentElement.outerHTML.length,text:(document.body?document.body.innerHTML:'')})`;
        const r = await send('Runtime.evaluate', { expression: probe, returnByValue: true });
        const v = r.result && r.result.result ? JSON.parse(r.result.result.value) : null;
        let shot = null;
        if (cfg.shots && v) {
          const cap = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
          if (cap.result && cap.result.data) {
            shot = `${outDir}/screenshots/${pg.name}_${vp.name}.png`;
            writeFileSync(shot, Buffer.from(cap.result.data, 'base64'));
          }
        }
        const overflow = v ? (v.sw > v.cw + 1) : true;
        const found = [];
        if (v) for (const term of (cfg.absent || [])) if (v.text.includes(term)) found.push(term);
        const pass = v && !overflow && found.length === 0 && (v.title || '').length > 0;
        if (!pass) failures++;
        results.push({ viewport: vp.name, page: pg.name, url: pg.path, http_rendered: !!v,
          scrollWidth: v?.sw, clientWidth: v?.cw, overflow, forbiddenFound: found,
          title: v?.title, screenshot: shot, pass });
        ws.close(); await fetch(`http://127.0.0.1:${port}/json/close/${t.id}`).catch(() => {});
      }
    }
  } finally { proc.kill(); }

  const summary = { base: cfg.base, ts: new Date().toISOString(), total: results.length,
    failures, verdict: failures === 0 ? 'PASS' : 'FAIL', results };
  mkdirSync(outDir, { recursive: true });
  writeFileSync(`${outDir}/qa_probe_result.json`, JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary, null, 2));
  process.exit(failures === 0 ? 0 : 1);
}
main().catch(e => { console.error('FATAL', e); process.exit(2); });
