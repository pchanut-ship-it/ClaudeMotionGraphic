#!/usr/bin/env node
/*
 * Example end-to-end play-through for the template game (วันหนึ่งที่ตลาด).
 * Copy it and adapt the ANSWERS and per-level steps when you build a new game.
 *
 * Usage:
 *   node playthrough_example.js path/to/index.html [--mode mouse|touch] [--out dir] [--fonts dir] [--size 1920x1080]
 *
 * What it demonstrates:
 *   - tapping with the mouse and with touch (page.touchscreen.tap)
 *   - dragging with the mouse and with touch (CDP Input.dispatchTouchEvent)
 *   - a wrong answer, both hint steps, choosing another blank, any-order pages
 *   - waiting for #nextWrap.show before pressing ไปต่อ (never a fixed sleep: the button
 *     appears ~0.45–0.9 s after the answer and ignores taps for another 0.3 s)
 *   - screenshots of each important state, and a console-error report at the end
 */
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf(n); return i > 0 ? args[i + 1] : d; };
const FILE = path.resolve(args[0] || 'index.html');
const MODE = opt('--mode', 'mouse');
const OUT = path.resolve(opt('--out', 'playthrough'));
const FONTS = opt('--fonts', null);
const [W, H] = opt('--size', '1920x1080').split('x').map(Number);

// Level 2 answers in page order (from STORY). Level 1 answers are read from the sign.
const ANSWERS = [['หนึ่ง', 'หน้า', 'ใหม่'], ['ตลาด'], ['กะหล่ำปลี', 'หน่อไม้', 'หยวก'],
  ['หญิง', 'หมู', 'สนิทสนม', 'เสมอ'], ['อยาก', 'ขนม', 'เหลือง', 'หวาน'], ['ใหญ่', 'หนี'], ['หนังสือ', 'อร่อย', 'อย่าง']];
const EXTRA_PAGE1 = 'หมู';

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1, hasTouch: MODE === 'touch' });
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  if (FONTS) {
    await page.route('https://fonts.googleapis.com/**', (r) => r.fulfill({ status: 200, contentType: 'text/css', body: fs.readFileSync(path.join(FONTS, 'mali.css'), 'utf8') }));
    await page.route('https://fonts.gstatic.com/**', (r) => {
      const f = path.join(FONTS, r.request().url().replace('https://fonts.gstatic.com/', '').replace(/\//g, '_'));
      if (fs.existsSync(f)) r.fulfill({ status: 200, contentType: 'font/woff2', body: fs.readFileSync(f), headers: { 'access-control-allow-origin': '*' } });
      else r.fulfill({ status: 404, body: '' });
    });
  }

  let n = 0;
  const shot = (name) => page.screenshot({ path: path.join(OUT, String(++n).padStart(2, '0') + '-' + name + '.png') });
  const wait = (ms) => page.waitForTimeout(ms);
  const center = async (sel) => {
    const b = await page.locator(sel).first().boundingBox();
    if (!b) throw new Error('not visible: ' + sel);
    return { x: b.x + b.width / 2, y: b.y + b.height / 2 };
  };
  const tap = async (sel) => {
    const c = await center(sel);
    if (MODE === 'touch') await page.touchscreen.tap(c.x, c.y);
    else { await page.mouse.move(c.x, c.y); await page.mouse.down(); await page.mouse.up(); }
  };
  const drag = async (fromSel, toSel) => {
    const a = await center(fromSel), b = await center(toSel), steps = 12;
    if (MODE === 'touch') {
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: a.x, y: a.y, id: 1 }] });
      for (let i = 1; i <= steps; i++) {
        await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: a.x + (b.x - a.x) * i / steps, y: a.y + (b.y - a.y) * i / steps, id: 1 }] });
        await wait(16);
      }
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    } else {
      await page.mouse.move(a.x, a.y); await page.mouse.down();
      for (let i = 1; i <= steps; i++) { await page.mouse.move(a.x + (b.x - a.x) * i / steps, a.y + (b.y - a.y) * i / steps); await wait(16); }
      await page.mouse.up();
    }
  };
  const next = async () => { await page.waitForSelector('#nextWrap.show', { timeout: 5000 }); await wait(350); await tap('#btnNext'); await wait(1000); };

  await page.goto('file://' + FILE);
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await wait(1500); await shot('cover');
  await tap('#btnCover'); await wait(1500); await shot('map');

  // ---------- Level 1: fill the missing letter ----------
  await tap('#shop-signs'); await wait(2000); await shot('demo1');
  await tap('#btnStart'); await wait(1200);
  for (let q = 0; q < 5; q++) {
    const ans = await page.evaluate(() => {      // read the answer from the sign text after the slot
      const sw = document.getElementById('signWord');
      const after = sw.lastChild.nodeType === 3 ? sw.lastChild.textContent : '';
      return after === 'นม' ? 'ข' : after === 'ลาด' ? 'ต' : 'ห';
    });
    if (q === 0) {
      await shot('l1-question');
      await tap(`#tiles .tile:not([data-l="${ans}"])`); await wait(800); await shot('l1-wrong');
      await tap('#btnHint'); await wait(400); await shot('l1-hint1');
      await tap('#btnHint'); await wait(500); await shot('l1-hint2');
    }
    if (q % 2) await drag(`#tiles .tile[data-l="${ans}"]`, '#slot'); else await tap(`#tiles .tile[data-l="${ans}"]`);
    await wait(500);
    if (q === 0) await shot('l1-correct');
    await next();
  }
  await shot('l1-finish');
  await tap('#btnMap'); await wait(2600); await shot('map-reward');

  // ---------- Level 2: cloze story ----------
  await tap('#shop-story'); await wait(2000); await shot('demo2');
  await tap('#btnStart'); await wait(1200);
  for (let p = 0; p < ANSWERS.length; p++) {
    const words = ANSWERS[p];
    if (p === 0) {
      await shot('l2-page1');
      await tap(`#bank .card[data-w="${EXTRA_PAGE1}"]`); await wait(800); await shot('l2-wrong');
      await tap('#btnHint'); await wait(400); await shot('l2-hint1');
      await tap('#b2'); await wait(300);                       // choose the third blank
      await tap(`#bank .card[data-w="${words[2]}"]`); await wait(800);
      await tap('#btnHint'); await wait(500); await shot('l2-hint2');
      await tap(`#bank .card[data-w="${words[0]}"]`); await wait(800);
      await tap(`#bank .card[data-w="${words[1]}"]`); await wait(1200); await shot('l2-page1-done');
    } else if (p === 2) {                                       // any-order page, filled in reverse by dragging
      for (let i = 0; i < words.length; i++) { await drag(`#bank .card[data-w="${words[words.length - 1 - i]}"]`, '#b' + i); await wait(700); }
    } else {
      for (let i = 0; i < words.length; i++) {
        if ((p + i) % 2) await drag(`#bank .card[data-w="${words[i]}"]`, '#b' + i); else await tap(`#bank .card[data-w="${words[i]}"]`);
        await wait(700);
      }
      if (p === 3) { await wait(600); await shot('l2-page4-done'); }
    }
    await next();
  }
  await wait(600); await shot('story');
  await tap('#btnMap'); await wait(2600); await shot('map-both');
  await tap('#btnSummary'); await wait(800); await shot('summary');

  console.log(errors.length ? 'console errors:\n  ' + errors.join('\n  ') : 'no console errors');
  console.log('screenshots in ' + OUT);
  await browser.close();
  process.exit(errors.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
