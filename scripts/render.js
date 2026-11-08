// Render the animation to MP4 (1920×1080, 30 fps) by stepping time frame-by-frame.
// Usage: node scripts/render.js out.mp4 [--clean]   (--clean = no captions / overlay text)
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path = require('path');
(async () => {
  const out = process.argv[2] || 'output/watermark-explainer.mp4', clean = process.argv.includes('--clean');
  const FPS = 30;
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto('file://' + path.resolve(__dirname, '../index.html') + '?render=1' + (clean ? '&captions=0' : ''));
  await pg.waitForFunction(() => window.__ready);
  const DUR = await pg.evaluate(() => window.__DUR);
  // sound effects (generate with: python3 scripts/sfx.py /tmp/raw.wav, then loudnorm → output/sfx.wav — see README)
  const sfx = path.resolve(__dirname, '../output/sfx.wav');
  const audio = require('fs').existsSync(sfx) ? ['-i', sfx, '-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k', '-shortest'] : [];
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', ...audio,
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < FPS * DUR; f++) {
    await pg.evaluate(t => window.__setTime(t), f / FPS);
    const buf = await pg.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${FPS * DUR}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('done', out);
})();
