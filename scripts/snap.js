// Usage: node scripts/snap.js out_dir t1 t2 ...   (stills for review)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const [out, ...ts] = process.argv.slice(2);
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  pg.on('pageerror', e => console.log('ERR', e.message));
  await pg.goto('file://' + path.resolve(__dirname, '../index.html') + '?render=1');
  await pg.waitForFunction(() => window.__ready);
  for (const t of ts) { await pg.evaluate(t => window.__setTime(+t), t); await pg.screenshot({ path: `${out}/t${String(t).padStart(5,'0')}.png` }); }
  await b.close();
})();
