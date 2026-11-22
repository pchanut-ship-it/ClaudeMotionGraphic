# UX patterns: interaction, feedback, flow, teacher tools

## Contents
1. Screen map
2. Touch input model
3. Answering: active slot, tap, drag
4. Feedback copy and timing
5. Hints
6. Demo screen recipe
7. Level recipes (letter fill, cloze story, future mechanics)
8. Rewards and finish screens
9. Teacher summary
10. Sound design
11. Accessibility and keyboard

---

## 1. Screen map

```
cover ──เริ่มเล่น──► map ──shop──► demo ──เริ่มเลย──► level (n questions or pages)
                      ▲  │                                   │ ไปต่อ after the last one
                      │  └─สรุปผลสำหรับครู─► summary          ▼
                      └──────────กลับแผนที่────────── finish screen / read-aloud page
```
- `หน้าแรก` (teacher corner) always returns to the map. It is hidden on the
  cover and the map. Partial progress is kept.
- Every screen change goes through `setScreen(html, name, status)`. It clears
  timers, cancels any gesture, removes clones and effects, fades in, and
  locks taps for 350 ms so the tap that changed the screen can't also press
  something on the new one.
- A level remembers nothing between visits. Replaying starts a new round in
  the stats.

## 2. Touch input model

All input goes through one gesture adapter (`bindPress`). It uses Pointer
Events and falls back to touch plus mouse events on old browsers.

- **Tap vs drag**: movement under 10 px from the start point is a tap. Big
  panels jitter, so a strict threshold would turn taps into failed drags.
- **Buttons** (`onTap`) fire on release *if the finger is still within
  16 px of the button*, even after moving. The pressed state follows the
  finger. Keyboard `click` events (`e.detail === 0`) also fire, for teachers
  using a remote.
- **One gesture at a time; the newest wins.** A new touch cancels the
  previous gesture (its clone flies home). A palm resting on the glass would
  otherwise block every tap.
- **`busy` flag** while an answer animation runs: pieces ignore presses, but
  teacher buttons still work.
- **Tap locks**: 350 ms after a screen change, and 300 ms when ไปต่อ appears.
- **No hover effects, double-tap or long-press.** The context menu,
  selection, native drag and pinch zoom are all prevented.

## 3. Answering: active slot, tap, drag

- **Active slot**: in multi-blank tasks the first empty blank is active
  (solid blue border, "?" and a glow). Tapping a piece fills the active
  blank. Tapping another empty blank makes it active. After a correct fill,
  the next empty blank (searching forward, then wrapping around) becomes
  active automatically.
- **Drag**: the piece's clone follows the finger at 1.08× scale with a
  shadow, and the original stays behind as a faint ghost. The drop target is
  the nearest empty slot whose rectangle, widened by a margin, contains
  either the clone's centre or the finger point. Margins are 6u around the
  whole sign for a single slot, and 2.5u around each blank in a sentence.
  The target under the finger is highlighted while dragging.
- **Dropping on nothing**: the clone flies home with no penalty and a soft
  "drop" sound.
- **Tap animation**: a tapped piece also flies to the slot (≈ 240 ms), so tap
  and drag look the same: correct pieces land, wrong ones bounce back.
- **Correct**: the slot fills in the answer colour, the piece's place stays
  empty (`visibility:hidden`), a burst plays, and the feedback pill shows the
  word plus its reading guide.
- **Wrong**: the piece flies back (300 ms) and shakes, and the slot shakes.
  In single-answer tasks the piece dims with a ✖ badge and can't be chosen
  again. In multi-answer tasks it stays usable, because it may belong in
  another blank. Errors are recorded against the target word.
- **Any-order groups**: blanks that accept their answers in any order (three
  vegetables in a list) check against the remaining answers of the group.
- **After the last answer**: hide the pieces and the hint button, celebrate,
  then show ไปต่อ ▶ in the pieces' place after about 0.45–0.9 s.

## 4. Feedback copy and timing

Short, kind, concrete Thai. Icon first, one line.

| Moment | Copy (Thai) |
|---|---|
| correct letter | ✔ **หมู** — เติม **ห** สำเร็จ, with "อ่านว่า หฺมู" under the word on the sign |
| correct word | ✔ **หนึ่ง** อ่านว่า **หฺนึ่ง** |
| page complete | ✔ **ใหม่** อ่านว่า **ไหฺม่** · ครบแล้ว! อ่านประโยคพร้อมกันนะ |
| wrong letter | ↺ ดูภาพ แล้วลองอีกครั้ง |
| wrong word | ↺ อ่านประโยคอีกครั้งนะ |
| hint 1, silent ห | 💡 ตัวอักษรนี้นำหน้า แต่ไม่ออกเสียง |
| hint 1, sounded leading letter | 💡 ตัวอักษรนี้ออกเสียงสั้น ๆ มีเสียง อะ |
| hint 1, cloze | 💡 อ่านคำที่ขีดเส้นใต้ แล้วเลือกคำที่เข้ากัน |
| hint 2 | 💡 เอาตัวที่ไม่ใช่ออกไปแล้ว 1 ตัว / เอาบัตรคำที่ไม่ใช่ออกไปแล้ว 1 ใบ |
| level done | ✔ ซ่อมป้ายครบแล้ว! เก่งมาก · 👵 ขอบใจนะ ป้าให้ 🥬 กะหล่ำปลี ใส่ตะกร้า |
| demo line | ลากตัวอักษรไปวางในช่องว่าง หรือแตะตัวอักษรก็ได้ |
| map tip | 👆 แตะร้านเพื่อเริ่มเล่น |

Never say "ผิด" (wrong) to the child. Refer to colours in copy only together
with a shape ("ขีดเส้นใต้", not "สีเหลือง" alone).

## 5. Hints

- One 💡 คำใบ้ button at the bottom-left of zone D, with a badge showing the
  hints left (2, 1, 0). It disables itself when there is nothing more it can
  do.
- **Step 1 teaches.** Level 1: the slot pulses and the group tip appears.
  Cloze: the clue word before the active blank is highlighted and
  underlined. Mark clue words in the data with `[ ]`. If none is marked, the
  nearest earlier clue is used, and failing that the text right before the
  blank. The highlight follows the active blank.
- **Step 2 narrows.** It removes one wrong choice (a random wrong tile, or
  the distractor card). The space stays empty so nothing shifts.
- Record the highest step used per item for the summary.

## 6. Demo screen recipe

Shown once before each level (every time the shop is entered):
- Top: one story line (why we are here) and one instruction in a pill.
- Middle: a sample item made of words outside the lesson list, so no
  answers are revealed (หนู with 🐭 for a letter task, "ฉันเห็น{หนู}ตัวเล็ก" for
  a cloze task).
- Pieces row: a demo copy of the real pieces with `pointer-events:none`.
- A cartoon ✋ hand, positioned below and to the right of the piece so the
  letter stays visible, loops through: fade in (0.3 s) → move onto the piece
  (0.45 s) → grab (scale 0.86) → carry the piece to the slot (1.1 s) → the
  slot fills → fade out → restart after 4 s. The loop runs on `later()`
  timers, so `setScreen` stops it.
- Reduced motion: a still picture with the hand on the piece and the slot
  already filled.
- Big เริ่มเลย ▶ at the bottom.

## 7. Level recipes

**Letter fill ("fix the sign")**: a picture in zA, a wooden sign with the word
in zB with one dashed slot (the 12.5u word fits by width), 3 tiles in zD
(the answer plus 2 distractors from a fixed letter set, shuffled), and a
progress boards strip at the top-right. On a correct answer: big check,
reading guide shown on the sign, star to the progress board. 5 random
questions from the pool.

**Cloze story ("complete the story")**: pages in order. A scene frame in zA,
the sentence box in zB with uniform-width blanks, and the word bank in zD:
the page's answers plus one distractor, all cards in one colour. Sentence
markup: `{word}` is a blank, `[clue]` is the hint word for the next blank,
and `anyOrder: true` makes a list of blanks interchangeable. On page
complete: scene celebration (`hop`, or `run` for chases), word wave, burst,
fanfare, then ไปต่อ. The final page shows the **whole story** with the
filled words highlighted, for choral reading.

**Future mechanics** (each becomes a new shop):
- *Word train (รถไฟส่งคำ)*: sort word cards into 2–3 wagons by rule (silent ห
  vs sounded leading letter). The wagons are drop targets in zB, the active
  wagon is the tap target, and a tap on a wagon selects it.
- *Reading bridge (สะพานคำอ่าน)*: match a word to its reading guide. The
  planks are reading cards, and a tap or drag puts the matching plank on the
  bridge.
- *Picture hunt*: a market scene with tappable items. Keep the targets in
  the lower 60%, or give a picture list in zD whose items map onto the scene.

Reuse `makeDraggable`, the active-slot model, `feedback`, hints, stats and
the finish flow for all of them.

## 8. Rewards and finish screens

- **No points or stars for children to compare.** The rewards are story
  progress and market items.
- The first completion of a shop puts its reward item in the basket on the
  map. On return, the item flies from the shop card into the basket
  (whoosh), lands (coin sound plus a burst), the basket label changes to
  "✔ ได้ 🥬 กะหล่ำปลี แล้ว!", and then the stamp drops onto the shop card
  (stamp sound). Replays just say they finished again.
- **Finish screen** (letter levels): a title with ✔, the shopkeeper's thanks
  and reward line, recap cards for every item (picture, word with the
  answer highlighted, reading guide), confetti and a fanfare, then
  กลับแผนที่.
- **Read-aloud page** (story levels): the whole text with highlighted
  answers, zebra-striped lines, the teacher note "ครูให้นักเรียนอ่านออกเสียง
  พร้อมกัน", confetti, and กลับแผนที่.

## 9. Teacher summary

Data model (kept in memory, saved to `localStorage` when possible):
```js
{ v:1,
  done:   { signs:true, story:false },            // stamps and basket
  rounds: { l1:2, l2:1 },                         // times each level was started
  l1: { finished:true, total:5, items:[ {word, wrong, hint, firstTry, done} ] },   // latest round
  l2: { finished:false, total:20, pages:[ {page, hint, done, blanks:[ {word, wrong, firstTry, done} ]} ] },
  wrong:  { 'ขนม': { l1:2, l2:1 } } }             // cumulative, for "คำที่ควรทบทวน"
```
- Record a wrong attempt the moment it happens. For blanks, add the attempts
  to `wrong[word]` when the blank is finally filled, so any-order groups
  credit the word actually placed.
- **One panel per skill** ("ทักษะ: เติมตัวอักษรนำ", "ทักษะ: ใช้คำในประโยค").
  Each has: first-try score with a bar ("4 / 5 ข้อ ตอบถูกตั้งแต่ครั้งแรก"),
  latest round and total rounds ("(ยังเล่นไม่จบ)" if unfinished), per-item
  chips (✔ / ↺ ×n / ยังไม่ตอบ), hint chips with their step, and words to
  review with readings, sorted by count. Never only one total.
- A note on whether results are saved on this device or will be lost when
  the page closes.
- เล่นใหม่ทั้งหมด uses a two-tap confirm: the first tap changes the label to
  "แตะอีกครั้งเพื่อลบผลทั้งหมด" for 4 s. Browser `confirm()` dialogs are
  avoided because they look broken on TVs and are blocked in some frames.
- The panels fit their text to the panel (min 2.2u) and both rows and
  height are measured.

## 10. Sound design

Synthesized with Web Audio, with no audio files and **no speech** (the game
must not pretend to model pronunciation; the teacher does that).

| Event | Sound |
|---|---|
| any button | `tap`: short soft pop |
| piece lifted (drag starts) | `pick` |
| dropped on nothing | `drop` |
| correct | `correct`: C–E–G–C arpeggio with a sparkle |
| wrong | `wrong`: two soft falling notes, never a buzzer |
| hint step | `hint`: twinkle |
| star reaches progress | `star` |
| ไปต่อ | `next`: page-turn whoosh plus pop |
| เริ่มเล่น / เริ่มเลย | `start`: rising arpeggio |
| page complete | `fanfare` |
| finish or read-aloud page | `tada` |
| reward flies / lands / stamp | `whoosh` / `coin` / `stamp` |

- Master volume around 0.6, individual sounds 0.07–0.3, triangle or sine
  waves for warmth, square waves only very quietly.
- 🔊 เสียง: เปิด/ปิด in the teacher corner, remembered in storage. Audio
  unlocks on the first pointerdown, keydown or touchstart. With no Web Audio,
  `Sound.play` silently does nothing.
- **If the brief says no sound**, remove the `Sound` module, the toggle and
  every `Sound.play` call (use `onTap(..., false)`), and state in the report
  that the code contains no audio.

## 11. Accessibility and keyboard

- The feedback pill has `role="status" aria-live="polite"`. Shops, tiles and
  cards are `<button>` elements with Thai `aria-label`s, and blanks have
  `role="button"`.
- Keyboard and remote: Enter or Space on a focused button or piece acts as a
  tap.
- Reduced motion: no bursts, confetti, flying star or hand loop. Animations
  last 1 ms and transitions are off.
