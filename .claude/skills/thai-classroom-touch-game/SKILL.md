---
name: thai-classroom-touch-game
description: Design and build touch-screen learning games for Thai primary classrooms that run on a big smart TV or interactive board at the front of the room, in the house style of the game วันหนึ่งที่ตลาด - a bright Thai fresh-market world (striped awning, wooden signs, woven frames, mango yellow), Mali font, big pressable tiles, answers by tap or drag, icon-plus-text feedback, two-step hints, an animated demo hand, a cover page, synthesized sound effects and a teacher summary, shipped as one self-contained ES5 HTML file. Use this whenever someone wants an educational or classroom game, เกมการศึกษา, เกมสอนภาษาไทย, เกมฝึกอ่านหรือสะกดคำ, a game for อักษรนำ, สระ, วรรณยุกต์, มาตราตัวสะกด, คำควบกล้ำ or vocabulary, a touch game for a smart TV or smart board for young learners, or a new shop, level or mechanic for วันหนึ่งที่ตลาด, even if they never name this style or skill.
---

# Thai classroom touch game (วันหนึ่งที่ตลาด house style)

This skill packages a game that was built, tested and refined for a real Thai
classroom: Grade 1–3 students take turns at a large touch TV while the whole
class watches. It records the theme, the visual system, the UX rules and the
mistakes that cost time, so the next game of this kind starts where the last
one finished.

The working implementation is `assets/game-template.html` (about 1,900 lines,
Thai comments). **Start every new game from a copy of it** rather than from a
blank file. Its touch system, text fitting, sound, effects, stats and teacher
summary already handle the hard cases: imprecise touch panels, resting palms,
old Smart-TV browsers, Thai combining marks and screens that are not 16:9.

## Who the game is for (the reason behind every rule)

- **One child at a time, standing at a tall screen.** Young children cannot
  reach the top of a 75" TV, so everything they press lives in the lower 60%.
- **The whole class watches from up to ~6 m.** Text is huge, feedback is
  readable from the back row, and an answer stays on screen until someone
  presses ไปต่อ, because the class reads it together.
- **Large touch panels are imprecise.** Fingers slip, palms rest on the glass,
  and two children touch at once. Taps must forgive movement, drop zones must
  be generous, and a new touch replaces a stuck one.
- **Early readers.** Short, simple Thai, pictures for every word, and icons
  next to every message. Colour is never the only signal.
- **The teacher runs it.** One file, no install, works offline apart from the
  font. The teacher needs fullscreen, home, a sound switch and a results page,
  all small in the top-right corner, out of children's reach.
- **Old TV browsers.** ES5 JavaScript and conservative CSS. Every browser
  feature that might be missing is guarded.

## Workflow

1. **Pin down the brief.** You need the target skill (e.g. อักษรนำ, สระเอือ),
   the word list with reading guides, the grade, the mechanics per level,
   and whether sound is wanted. Ask only for what is missing. Defaults: Grade
   1–3, 2 shops (levels), 5 questions in a letter or word level, synthesized
   sound with a teacher on/off switch, market theme.
2. **Copy the template** into the project (e.g. `<game>/index.html`). Read
   `references/template-map.md` before editing: it says which sections are
   engine (keep as is), which are content (replace) and which are screens
   (adapt), and lists the helper functions to reuse.
3. **Content first.** Put every word, sentence and story page in the editable
   arrays at the top of the script (`WORDS`, `STORY`, or new arrays shaped the
   same way), with Thai comments on each field so a teacher can edit them
   later. Validate the data in code (for example, a blank pattern plus its
   answer must rebuild the word) and skip bad rows instead of crashing.
4. **One shop per mechanic.** Each level is an entry in `SHOPS` with an icon,
   a name, a skill label, a reward item, a demo and a `start()` function. The
   map renders whatever is in `SHOPS`, so new mechanics slot in as new shops.
   Recipes for the screens are in `references/ux-patterns.md`.
5. **Keep the visual system.** Use the tokens, textures, components and
   motion in `references/visual-design.md`. A new topic can have its own stall
   colours, goods and scene emoji, but keep the awning, wood, woven frames,
   pressable cards and type scale so all games feel like one series.
6. **Get the Thai right** wherever a blank touches a word, and wherever
   multi-line Thai text has stacked marks. Read `references/thai-text.md`.
7. **Respect the device.** Read `references/tv-compat.md` before adding any
   new JS or CSS feature.
8. **Verify** (next section), look at the screenshots yourself, fix, re-run.
9. **Deliver** the file, screenshots and a short report (last section).

## Non-negotiables

| Rule | Why |
|---|---|
| Child controls start at or below 40% of the stage height. Above that: pictures, sentences, status only. Teacher buttons sit small in the top-right corner. | Children are short. The top area belongs to what the class reads. |
| Every answer works by **tap** and by **drag**. A tap fills the active blank, a drag drops on any blank. Movement under 10 px counts as a tap. | Some children drag, some tap, and panels jitter. Neither path may fail. |
| Sizes use stage units (1u = 1% of stage height): target words ≥ 10u, sentences ≥ 6u, tiles and buttons ≥ 12u tall. | Readable at ~6 m on a 1080p TV, and pressable with a child's finger. |
| Feedback is always an icon + short text + colour (✔ correct, ↺ try again, 💡 hint), with the icons drawn as inline SVG. | Colour-blind children and the back row both need it. SVG icons render on every TV, while symbol glyphs may not. |
| A correct answer stays on screen, with its reading guide, until the child presses **ไปต่อ ▶**. No auto-advance and no timers. | The teacher pauses here for the class to read aloud. |
| Wrong answers are gentle: the piece slides back, shakes, and (when only one answer is possible) dims with a ✖ badge, plus ↺ and a short hint. | Mistakes are part of learning in front of peers, so nothing loud or shaming. |
| Two-step hints: step 1 points at the right place or rule, step 2 removes a wrong choice. Hint use is recorded. | Children should still do the last step themselves, and the teacher learns who needed help. |
| One self-contained HTML file. The only external resource is the Google Font **Mali**. Pictures are emoji or CSS/SVG. | Classroom wifi is unreliable and teachers copy the file around. |
| ES5 script, conservative CSS, guarded `localStorage`; the game must run fully without storage, audio or Pointer Events. | Smart-TV browsers are old and locked down. |
| The play area is exactly 16:9 and fills any screen: background and awning extend sideways, a wooden counter fills extra height, and portrait screens show a rotate hint. | A browser that isn't fullscreen should still look finished, without brown letterbox bars. |
| `prefers-reduced-motion` turns effects off (`transition: none`, 1 ms animations). | Some children get motion sickness or are distracted easily. |
| Teacher summary by skill: first-try results, which items used which hint step, and words to review (with reading guide). Never a single total score. Reset needs two taps. | The teacher plans the next lesson from it. |

## The look in brief

A Thai fresh market at mid-morning: an orange and cream scalloped awning
across the top, a warm mango-yellow woven background, dark-brown ink on cream
paper, wooden sign frames with nail heads, woven bamboo picture frames, and
big rounded "pressable" cards with a solid bottom shadow that sinks when
touched. The font is **Mali** (looped Thai letters, friendly for early
readers). The answer colour is burnt orange (`#b23c06` on `#fff0c2`). Word
cards all share one light blue, so children read the word instead of matching
colours. Full tokens, CSS snippets and the motion catalogue are in
`references/visual-design.md`.

## Screen flow

cover (เริ่มเล่น) → market map (shops, basket, stamps, teacher summary button)
→ demo (cartoon hand drags a piece, then เริ่มเลย) → level questions → finish
screen (recap, reward, confetti) → back to the map, where the reward flies
into the basket and the shop gets a "ผ่านแล้ว ✔" stamp. Story-type games end
on a read-aloud page with the note "ครูให้นักเรียนอ่านออกเสียงพร้อมกัน",
because the game cannot check pronunciation.

## Verify before delivering

If your environment can run code (Python 3, Node.js and Playwright), run the bundled
checks (paths are relative to this skill's folder). If it can't, review the code against
the non-negotiables and `references/tv-compat.md` by reading it, and say so in the report.

```bash
python3 scripts/check_static.py <game>/index.html   # forbidden syntax, external hosts, ES5 parse
node scripts/check_layout.js <game>/index.html --out <scratch>/layout   # positions, sizes, errors, 5 screen shapes, 4 degraded modes
```

`check_layout.js` needs Playwright. It audits the cover and the map only,
because it can't know your game's answers. For the levels, write a
play-through modelled on `scripts/playthrough_example.js`. That example plays
the whole template game with mouse taps, drags and touch, waits for
`#nextWrap.show` instead of fixed sleeps, and saves screenshots. Then **look at
the screenshots**. Clipped Thai marks, overlaps and fit problems show up there,
not in the numbers.

Measure positions and sizes only after entrance animations settle (about
1 s). Mid-animation transforms report false failures. When several browsers
run in parallel the machine slows down, so rerun a single failed scenario on
its own before calling it a bug.

## Lessons from the first build

Each of these cost a debugging round. Avoid them up front:

- **Class names collide in one big file.** `.story` was both the demo text
  and the story container, and the demo text vanished. Prefix screen-specific
  classes (`.demo-story`, `.cover-title`).
- **`overflow:hidden` on a text line clips Thai marks**, both the lower vowels
  (ู in หมู) and stacked tone marks (เสื้อ). Use line-height ≥ 1.42 for a
  single line and ≥ 1.6 for multi-line Thai, and add padding instead of
  clipping.
- **Write reduced-motion CSS as `transition: none !important`.** Never write
  `transition-duration: 1ms`: the default property is `all`, so font sizes
  would transition too and every synchronous measurement goes wrong.
- **Text-fit loops must freeze motion while measuring.** The template's
  `fitText` disables transitions and adds `.fitting` (`animation: none` on
  descendants), because entrance transforms with `backwards` fill count as
  overflow.
- **Animations override transforms.** The animation listed later in the CSS
  wins. Define entrance and idle classes *before* `.shake` and `.removed`. Use
  fill-mode `backwards`, never `both` or `forwards`, on anything pressable.
  Use two-class selectors for state animations (`.blank.shake` after
  `.blank.active`).
- **Guard the answer moment.** ไปต่อ appears about 0.45 s after a correct
  answer with a 0.3 s tap lock, so a child hammering the screen cannot skip
  the reading. Tests must wait for `#nextWrap.show`.
- **Keep remaining pieces still.** Hide used cards with `visibility:hidden`
  so the rest do not slide under a child's finger.
- **A new touch cancels the old gesture**, so a palm resting on the glass
  never blocks the next tap.
- **Audio starts only after a gesture.** Create or resume the AudioContext in
  the first `pointerdown`. The cover's เริ่มเล่น button provides that tap.
- **Letterbox bars read as "not full screen".** Paint the background on
  `body`, repeat the awning tile across the full width, pin the stage to the
  top, and put a wooden counter underneath.
- **Hint text must be true for every word it is shown with.**
  "ตัวอักษรนี้นำหน้า แต่ไม่ออกเสียง" is wrong for ขนม and ตลาด, where the
  first letter is pronounced (ขะ, ตะ). Write tips per group, with optional
  per-word overrides.
- **Captions and pictures can give the answer away** (the caption หยวกกล้วย
  under the question _ยวก). Point such cases out to the user instead of
  silently changing the brief.
- **Fitting a whole story on one screen** can push text slightly below the
  6u target. Report the number rather than hiding it.

## Deliver

- Save the game in the project, commit it, and send the HTML file plus a
  handful of screenshots (cover, a correct answer, a finished page, the
  teacher summary).
- Report against the non-negotiables: what passed, any number that fell short
  and why, and every decision you made that the brief did not specify.
- If the user wants a shareable preview and your platform hosts HTML pages
  (for example Claude Artifacts), follow `references/tv-compat.md` §7. Some
  hosts add their own page skeleton, so the game's `<!DOCTYPE>`, `<html>`,
  `<head>` and `<body>` tags must be stripped first.
- Answer in the user's language, which is often Thai. In-game copy is short,
  simple Thai for the grade level. Teacher-facing text may be more formal.
