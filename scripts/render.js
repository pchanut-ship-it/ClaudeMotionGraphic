// Render the animation to MP4 (1920×1080, 30 fps) by stepping time frame-by-frame.
// Usage: node scripts/render.js out.mp4 [--clean] [--nosubs] [--audio=path]
//   --clean   no on-screen text at all      --nosubs  hide only the bottom subtitles
//   --audio   soundtrack to mux (default: output/mix.wav, else output/sfx.wav, else silent)
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path = require('path');
(async () => {
  const args = process.argv.slice(2), out = args.find(a => !a.startsWith('--')) || 'output/watermark-explainer-final.mp4';
  const clean = args.includes('--clean'), nosubs = args.includes('--nosubs');
  const audioArg = (args.find(a => a.startsWith('--audio=')) || '').slice(8);
  const FPS = 30;
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto('file://' + path.resolve(__dirname, '../index.html') + '?render=1' + (clean ? '&captions=0' : '') + (nosubs ? '&subs=0' : ''));
  await pg.waitForFunction(() => window.__ready);
  const DUR = await pg.evaluate(() => window.__DUR);
  // soundtrack: final mix (scripts/mix_audio.py) or SFX only (scripts/sfx.py) — see README
  const fs = require('fs');
  const sfx = audioArg ? path.resolve(audioArg) : ['../output/mix.wav', '../output/sfx.wav'].map(p => path.resolve(__dirname, p)).find(p => fs.existsSync(p));
  console.log('audio:', sfx || '(none)');
  const audio = sfx && fs.existsSync(sfx) ? ['-i', sfx, '-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k', '-shortest'] : [];
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
