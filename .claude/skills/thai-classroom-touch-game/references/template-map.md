# Template map: `assets/game-template.html`

The template is the finished วันหนึ่งที่ตลาด game. It is one HTML file: a
`<style>` block, then one `<script>` IIFE in numbered sections with Thai
headers ("ส่วนที่ n"). Search for those headers to jump to a section.

## Contents
1. What to keep, adapt or replace
2. Data you edit (section 1)
3. Helper API (sections 2–5)
4. Adding a new shop (step by step)
5. Making a brand-new game from the template
6. Checklist after editing

---

## 1. Keep / adapt / replace

| Part | Search for | Action |
|---|---|---|
| CSS: stage, awning, floor, buttons, textures, tiles, cards, effects, entrance and idle motion, feedback, keyframes, reduced motion | `/* ---------- เวที 16:9`, `ปุ่มกดแบบนูน`, `พื้นผิว`, `เอฟเฟกต์ดาว`, `เข้าฉาก`, `ภาพเคลื่อนไหว` | **keep** |
| CSS: screen-specific blocks (sign, scene and sentence, map, demo, finish, story, summary, cover) | `ป้าย + ช่องว่าง`, `ฉาก + ประโยค`, `หน้าแรก: แผนที่ตลาด`, `หน้าสาธิต`, `จบด่าน 1`, `นิทานของเรา`, `สรุปผลสำหรับครู`, `หน้าปก` | adapt and reuse; add new blocks with prefixed class names |
| ส่วนที่ 1: data (`WORDS`, `LETTER_CHOICES`, `GROUP_TIPS`, `LEVEL1_QUESTIONS`, `STORY`, `SHOPS`) | `ส่วนที่ 1` | **replace** with the new content |
| ส่วนที่ 2: utilities (`$`, `esc`, `shuffle`, class helpers, timers, `D()`, `fitText`, `awningTile`, `IC` icons) | `ส่วนที่ 2` | keep |
| ส่วนที่ 3: stats storage | `ส่วนที่ 3 :` | keep the mechanism; change the shape of `stats.l1/l2` if the levels change, and bump `STORE_KEY` for a new game |
| ส่วนที่ 3.5: `Sound` | `ส่วนที่ 3.5` | keep (remove it if the brief says no sound) |
| ส่วนที่ 4: touch (`bindPress`, `onTap`, `makeDraggable`, clones, flights, `pickTarget`) | `ส่วนที่ 4 :` | keep |
| ส่วนที่ 4.5: effects (`burst`, `confetti`, `flyStar`, `delayStyle`) | `ส่วนที่ 4.5` | keep |
| ส่วนที่ 5: shell, `setScreen`, `feedback`, fullscreen, sound toggle | `ส่วนที่ 5 :` | keep |
| ส่วนที่ 5.5: cover | `ส่วนที่ 5.5` | adapt the title, highlighted letters, stalls and labels |
| ส่วนที่ 6: map, reward animation | `ส่วนที่ 6` | keep; title text from the new game |
| ส่วนที่ 7: demo | `ส่วนที่ 7` | keep; supports `kind: 'letter'` and `'word'`, add a kind for a new mechanic |
| ส่วนที่ 8: Level 1 letter fill | `ส่วนที่ 8` | reuse as is for missing-letter tasks, or as the model for a new level |
| ส่วนที่ 9: Level 2 cloze story, read-aloud page | `ส่วนที่ 9` | reuse for any fill-the-sentence task |
| ส่วนที่ 10: teacher summary | `ส่วนที่ 10` | keep; add one panel per new skill |
| Start-up (`buildShell(); showCover();`) | end of the script | keep |

## 2. Data you edit (ส่วนที่ 1)

```js
var WORDS = [   // one array for every word in the game
  { word:'หมู', read:'หฺมู', group:'A', pic:'🐷', blank:'_มู' },          // in the Level 1 pool because it has `blank`
  { word:'หยวก', read:'หฺยวก', group:'A', pic:'🍌', blank:'_ยวก', caption:'หยวกกล้วย' },
  { word:'หน้า', read:'หฺน้า', group:'A' },                                // story only
  // tip:'…' overrides the group hint for one word
];
var LETTER_CHOICES = ['ห','อ','ส','ข','ต'];   // tiles = the answer + 2 random others from here
var GROUP_TIPS = { A:'…', B:'…', C:'…', D:'…' };
var LEVEL1_QUESTIONS = 5;
var STORY = [
  { scene:['☀️','🏠','👧'], bg:'sky', text:'เช้า[วัน]{หนึ่ง} ฉัน[ล้าง]{หน้า} แล้วใส่[เสื้อตัว]{ใหม่}', extra:'หมู' },
  { scene:['🥬','🎋','🍌'], bg:'veg', anyOrder:true, text:'[ร้านผักมี]{กะหล่ำปลี} {หน่อไม้} และ{หยวก}', extra:'ใหญ่' },
  { scene:['🐈','💨','🐕'], bg:'park', anim:'run', text:'[แมวตัว]{ใหญ่}[วิ่ง]{หนี}สุนัข', extra:'หวาน' }
];
var SHOPS = [
  { id:'signs', icon:'🪧', name:'ร้านซ่อมป้าย', level:'ด่าน 1', skill:'เติมตัวอักษรนำ', theme:'s1',
    reward:{ icon:'🥬', name:'กะหล่ำปลี' },
    demo:{ kind:'letter', story:'…', how:'ลากตัวอักษรไปวางในช่องว่าง หรือแตะตัวอักษรก็ได้',
           pic:'🐭', blank:'_นู', tiles:['ส','ห','ต'], answer:'ห' },
    start:function(){ startLevel1(); } },
  { id:'story', /* … */ demo:{ kind:'word', /* … */ before:'ฉันเห็น', after:'ตัวเล็ก', cards:['ไก่','หนู'], answer:'หนู' },
    start:function(){ startLevel2(); } }
];
```
Every field has a Thai comment in the template. Keep them, because teachers
edit these arrays.

## 3. Helper API

**Screens and timing**
- `setScreen(html, name, statusHtml)`: replaces `#screen`; clears timers,
  gestures, clones and effects; fades in; tap lock of 350 ms; hides หน้าแรก on
  `'cover'` and `'home'`. Then set `currentFit = function(){…}` and call it.
- `later(fn, ms)`: a `setTimeout` that `setScreen` cancels. Use it for
  everything that belongs to the screen.
- `D(ms)`: returns 1 under reduced motion. Wrap motion durations in it, but
  not sound timings.
- `lockTaps(ms)`: ignore taps for a while (used when ไปต่อ appears).
- `busy`: set it while an answer animation runs.

**Touch**
- `onTap(el, fn, snd)`: button behaviour. `snd` is a sound name, defaults to
  `'tap'`; `false` means silent.
- `makeDraggable(el, { canUse(el), tap(el), drop(el, clone, target), targets() })`:
  tap-or-drag piece. `targets()` returns
  `[{ el, zone?, margin(u), ...data }]`. The `drop` callback receives the
  chosen target object.
- `makeClone(el)`, `flyTo(clone, x, y, ms, cb)`, `deltaTo(clone, targetEl)`,
  `flyHome(el, clone)`: the flight animations used by every attempt.
- `removeChoice(el)`: hint step 2; pops the piece out and keeps its space.

**Feedback and effects**
- `feedback('ok' | 're' | 'tip', html)`: the pill in zone C with its icon,
  fitted to one line.
- `restartAnim(el, cls)`: replays a CSS animation class (`'shake'`,
  `'hinted'`, `'wave'`).
- `burst(el, n, spread)`, `confetti(n)`, `flyStar(fromEl, toEl, done)`,
  `delayStyle(sec)` (returns ` style="animation-delay:…"`).
- `Sound.play(name)`: `tap pick drop correct wrong hint star next start
  fanfare tada whoosh coin stamp`.
- `fitText(el, maxU, minU, 'h' | 'w' | 'hw')`.
- `IC.check / retry / next / cross / home / full / sound / mute`,
  `starSVG(fill)`, `esc(text)`, `shuffle(array)`.

**Stats**
- `stats` (the object described in ux-patterns §9), `saveStats()`,
  `addWrong(word, levelKey, n)`, `freshStats()`.
- `pendingReward = shopId` before returning to the map triggers the basket
  and stamp animation.

## 4. Adding a new shop (step by step)

1. **Data**: add the content array near the others, with Thai field comments.
2. **Shop entry**: push `{ id, icon, name, level, skill, theme, reward, demo, start }`
   to `SHOPS`. Give it a new `theme` class for its card awning colours. The
   map fits 2 cards at the current size (62u wide plus 7u margins each).
   For 3 cards set `.shop` to about 50u wide with 3u margins and scale the
   emoji and name down a little. For 4 or more, use two rows or a scrolling
   street. Keep cards at least 12u tall and in the lower 60%.
3. **Demo**: reuse `kind:'letter'` or `'word'`, or add a branch in
   `showDemo` that builds a sample plus a `mover` piece and a `dSlot`
   target. The hand loop only needs those two ids.
4. **Level code**, modelled on ส่วนที่ 8:
```js
var L3 = null;
function startLevel3() {
  L3 = { qs: shuffle(POOL).slice(0, 5), i: 0 };
  stats.rounds.l3 = (stats.rounds.l3 || 0) + 1;
  stats.l3 = { finished: false, total: L3.qs.length, items: [] };
  saveStats(); renderL3();
}
function renderL3() {
  var q = L3.qs[L3.i];
  L3.rec = { word: q.word, wrong: 0, hint: 0, firstTry: false, done: false };
  stats.l3.items[L3.i] = L3.rec; saveStats();
  var html = '<div class="zone zA center">…picture…</div>' +
    '<div class="zone zB center">…targets…</div>' +
    '<div class="zone zC center"><div class="fb" id="fb" role="status" aria-live="polite"></div></div>' +
    '<div class="zone zD">' +
      '<button class="btn btn-hint in-drop"' + delayStyle(0.3) + ' id="btnHint">💡 คำใบ้<span class="cnt" id="hintCnt">2</span></button>' +
      '<div class="tiles" id="pieces">…pieces with class in-drop…</div>' +
      '<div class="nextwrap" id="nextWrap"><button class="btn btn-next btn-go" id="btnNext">ไปต่อ ' + IC.next + '</button></div>' +
    '</div>';
  setScreen(html, 'l3', '🚂 ชื่อร้าน<span class="sep">·</span>ข้อ ' + (L3.i + 1) + ' / ' + L3.qs.length);
  // makeDraggable(...) for each piece; onTap($('btnHint'), l3Hint, false); onTap($('btnNext'), l3Next, 'next');
}
// l3Attempt(piece, clone, target): busy = true; fly to the target; correct → l3Solved(); wrong → wrong++, addWrong, feedback('re', …), Sound.play('wrong'), fly back, shake
// l3Solved(): rec.done = true, rec.firstTry = rec.wrong === 0, saveStats(); feedback('ok', word + reading); Sound.play('correct'); burst(...);
//            hide the pieces and hint; later(function(){ lockTaps(300); addCls($('nextWrap'), 'show'); }, D(450));
// l3Next(): next question, or stats.l3.finished = true; first completion → stats.done[id] = true, pendingReward = id; the finish screen
```
5. **Finish screen**: copy `showL1Done` (recap, reward line, confetti,
   `tada`).
6. **Summary**: add `panelL3()` modelled on `panelL1()`, and give `.sum` a
   third column (or a second row) when there are 3 skills. Keep one panel
   per skill.
7. **Stats loading**: `loadStats()` copies only the known keys, so add
   `l3` there and in `freshStats()`.
8. **Copy**: the demo story line, instruction, hint tips and feedback lines
   in the style of ux-patterns §4.

## 5. Making a brand-new game from the template

- Change the `<title>`, the cover title (highlight the target letters), the
  map title board and subtitle, `STORE_KEY` (so old results are not mixed
  in), the shops, the rewards and the stall labels.
- Replace `WORDS`, `GROUP_TIPS` and the story with the new skill's content,
  or delete the levels you don't need: remove their shop entries, functions
  and summary panels. Then search for leftover references such as `L1`,
  `L2` and `panelL2`.
- Keep the engine sections untouched unless you are fixing a real bug, and
  if you fix one, consider copying the fix back into this skill's template.

## 6. Checklist after editing

- `python3 scripts/check_static.py <file>` passes.
- `node scripts/check_layout.js <file>` reports no FAIL lines and no errors.
- Your play-through (modelled on `scripts/playthrough_example.js`) completes
  every level with taps, again with drags, and in touch mode.
- Screenshots reviewed: cover, each level's question, correct and wrong
  states, the finish page and the summary. Zoom in on any Thai text with
  stacked marks.
- Every new data field has a Thai comment, and the report to the user lists
  the decisions you made.
