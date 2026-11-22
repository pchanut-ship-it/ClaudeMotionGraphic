#!/usr/bin/env node
/*
 * Layout and robustness audit for a Thai classroom touch game built from the template.
 *
 * Usage:
 *   node check_layout.js path/to/index.html [--out dir] [--fonts dir]
 *
 * Assumes the template's structure: stage #app, screen container #screen, teacher
 * buttons in #teacher, optional cover button #btnCover. It audits the cover and the
 * first screen after it (the map); level screens need a game-specific play-through
 * (see playthrough_example.js).
 *
 * Checks, per viewport (16:9, wide TV browser, 16:10, 4:3, portrait):
 *   - every child control (buttons, tiles, cards, shops, blanks) starts at >= 40% of
 *     the stage height
 *   - buttons, tiles, cards and shops are at least 12% of the stage height tall
 *   - no console errors or page errors (failed font requests are reported separately)
 * Then reloads at 1920x1080 with: localStorage blocked, Pointer Events removed (touch),
 * prefers-reduced-motion, Web Audio missing — each must load and reach the map without errors.
 *
 * --fonts dir: folder holding mali.css plus woff2 files named like the fonts.gstatic.com path
 * with "/" replaced by "_" (lets you test with the real font offline). Without it the real
 * network is used, or the fallback font if offline.
 * Exit code 1 when something fails.
 */
'use strict';
const fs = require('fs');
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) {
  console.error('Playwright is not installed. Try `npm i -D playwright && npx playwright install chromium`.');
  process.exit(2);
}

const args = process.argv.slice(2);
if (!args[0]) { console.error('usage: node check_layout.js path/to/index.html [--out dir] [--fonts dir]'); process.exit(2); }
const file = path.resolve(args[0]);
const opt = (name) => { const i = args.indexOf(name); return i > 0 ? args[i + 1] : null; };
const OUT = path.resolve(opt('--out') || 'layout-check');
const FONTS = opt('--fonts');
fs.mkdirSync(OUT, { recursive: true });
const URL = 'file://' + file;

const VIEWPORTS = [[1920, 1080, '16x9'], [1920, 950, 'tv-browser'], [1440, 900, '16x10'], [1024, 768, '4x3'], [820, 1000, 'portrait']];
const MODES = {
  nostorage: { init: () => { Object.defineProperty(window, 'localStorage', { get() { throw new Error('SecurityError'); } }); } },
  nopointer: { touch: true, init: () => { try { window.PointerEvent = undefined; } catch (e) {} } },
  reduced: { reduced: true },
  noaudio: { init: () => { window.AudioContext = undefined; window.webkitAudioContext = undefined; } }
};

let failures = 0;
const fail = (msg) => { failures++; console.log('FAIL ' + msg); };
const pass = (msg) => console.log('PASS ' + msg);

async function openPage(browser, vp, mode) {
  mode = mode || {};
  const context = await browser.newContext({ viewport: { width: vp[0], height: vp[1] }, deviceScaleFactor: 1,
    hasTouch: !!mode.touch, reducedMotion: mode.reduced ? 'reduce' : 'no-preference' });
  const page = await context.newPage();
  const errors = [], fontFails = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('requestfailed', (r) => { if (/fonts\.(googleapis|gstatic)\.com/.test(r.url())) fontFails.push(r.url()); });
  if (FONTS) {
    await page.route('https://fonts.googleapis.com/**', (r) => r.fulfill({ status: 200, contentType: 'text/css', body: fs.readFileSync(path.join(FONTS, 'mali.css'), 'utf8') }));
    await page.route('https://fonts.gstatic.com/**', (r) => {
      const f = path.join(FONTS, r.request().url().replace('https://fonts.gstatic.com/', '').replace(/\//g, '_'));
      if (fs.existsSync(f)) r.fulfill({ status: 200, contentType: 'font/woff2', body: fs.readFileSync(f), headers: { 'access-control-allow-origin': '*' } });
      else r.fulfill({ status: 404, body: '' });
    });
  }
  if (mode.init) await page.addInitScript(mode.init);
  await page.goto(URL);
  try { await page.evaluate(() => document.fonts && document.fonts.ready); } catch (e) {}
  await page.waitForTimeout(1500);
  return { context, page, errors, fontFails };
}

async function audit(page) {
  return page.evaluate(() => {
    const app = document.getElementById('app');
    if (!app) return { error: 'no #app element' };
    const a = app.getBoundingClientRect();
    const high = [], small = [];
    document.querySelectorAll('#screen button, #screen [role=button], #screen .tile, #screen .card, #screen .shop, #screen .blank').forEach((el) => {
      const cs = getComputedStyle(el);
      if (el.offsetParent === null || cs.visibility === 'hidden' || cs.pointerEvents === 'none') return;
      const r = el.getBoundingClientRect();
      if (!r.width) return;
      const name = el.id || (el.className + '').split(' ')[0] || el.tagName;
      const top = (r.top - a.top) / a.height * 100;
      if (top < 39.5) high.push(name + ' top=' + top.toFixed(1) + '%');
      if (!el.classList.contains('blank') && r.height / a.height * 100 < 11.9) small.push(name + ' h=' + (r.height / a.height * 100).toFixed(1) + '%');
    });
    return { high, small, screenHtml: document.getElementById('screen') ? document.getElementById('screen').innerHTML.length : 0 };
  });
}

async function pressCover(page, touch) {
  const b = await page.$('#btnCover');
  if (!b) return false;
  const box = await b.boundingBox();
  if (touch) await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
  else await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  await page.waitForTimeout(1500);
  return true;
}

function judge(label, res, errors, fontFails) {
  if (res.error) return fail(label + ': ' + res.error);
  if (res.high.length) fail(label + ': controls above 40%: ' + res.high.join(', ')); else pass(label + ': controls in the lower 60%');
  if (res.small.length) fail(label + ': controls under 12% tall: ' + res.small.join(', ')); else pass(label + ': control sizes');
  if (errors.length) fail(label + ': console errors: ' + errors.slice(0, 3).join(' | '));
  if (fontFails.length) console.log('NOTE ' + label + ': font requests failed (fallback font used)');
}

(async () => {
  const browser = await chromium.launch();
  for (const vp of VIEWPORTS) {
    const { context, page, errors, fontFails } = await openPage(browser, vp);
    const tag = vp[2];
    await page.screenshot({ path: path.join(OUT, tag + '-1-start.png') });
    judge(tag + ' start screen', await audit(page), errors, fontFails);
    if (await pressCover(page, false)) {
      await page.screenshot({ path: path.join(OUT, tag + '-2-after-cover.png') });
      judge(tag + ' after cover', await audit(page), errors, []);
    }
    await context.close();
  }
  for (const name of Object.keys(MODES)) {
    const mode = MODES[name];
    const { context, page, errors } = await openPage(browser, [1920, 1080], mode);
    await pressCover(page, !!mode.touch);
    const res = await audit(page);
    await page.screenshot({ path: path.join(OUT, 'mode-' + name + '.png') });
    if (res.error || !res.screenHtml) fail('mode ' + name + ': screen did not render');
    else if (errors.length) fail('mode ' + name + ': console errors: ' + errors.slice(0, 3).join(' | '));
    else pass('mode ' + name + ': loads and reaches the next screen without errors');
    await context.close();
  }
  await browser.close();
  console.log('\nScreenshots: ' + OUT + '\n' + (failures ? failures + ' failure(s)' : 'all checks passed'));
  process.exit(failures ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
