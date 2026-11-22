# Visual design system: the Thai fresh market

Everything below is already implemented in `assets/game-template.html`. Use
this file to understand the system, and to stay consistent when you add new
screens or a new shop.

## Contents
1. Stage and units
2. Layout zones
3. Colour tokens
4. Typography
5. Textures (awning, bunting, wood, woven, basket, floor, background)
6. Components
7. Icons and emoji
8. Motion catalogue
9. Cover page composition
10. Giving a new game its own flavour

---

## 1. Stage and units

The play area is a 16:9 stage. Every size is written in stage units:
`--u` = 1% of the stage height, so `calc(var(--u)*12)` is 12% of the height.
This replaces vh and makes the layout identical on every screen.

```css
:root{ --u:1vh; }
@media (max-aspect-ratio:16/9){ :root{ --u:0.5625vw; } }   /* narrower than 16:9 → width decides */
#app{ position:absolute; left:50%; top:0;                    /* pinned to the top */
      width:calc(var(--u)*177.78); height:calc(var(--u)*100);
      margin-left:calc(var(--u)*-88.89); overflow:hidden; }
```

- Do not centre the stage with `transform: translate(-50%,-50%)`. A transform
  turns `#app` into the containing block for `position:fixed` drag clones.
  Use negative margins instead.
- The market background is painted on `body`, so the whole screen is
  textured. The awning is a body-level strip that repeats a 14.8u tile
  across the full width, aligned with
  `background-position: calc(50vw - var(--u)*88.89) 0`. A `.floor` element
  (wood planks) fills from `top: calc(var(--u)*100)` to the bottom, so it is
  zero-height on 16:9 or wider screens. In portrait it shows "หมุนจอเป็น
  แนวนอน".
- The effects layer `#fx` is `position:fixed` over the whole viewport, so
  confetti also falls beside the stage.

## 2. Layout zones (stage units, top to bottom)

| Zone | Top–height | Holds | Touchable? |
|---|---|---|---|
| Awning | 0–9.6 | stripes, status pill (top-left), teacher buttons (top-right) | teacher only |
| zA | 10.5–38.5 | picture, scene frame, shopkeeper bubble, progress | no |
| zB | 40–67 | the sign with the slot, or the sentence box with blanks | blanks only (≥ 40) |
| zC | 68–77.5 | feedback pill | no |
| zD | 79–98.5 | hint button (left), tiles or word cards (centre), ไปต่อ (centre, replaces the pieces) | yes |

The map, cover, finish and summary screens use their own positions but keep
the same principle: everything a child presses starts at ≥ 40u.

## 3. Colour tokens

| Token | Hex | Use |
|---|---|---|
| mango | `#ffc83d` (glow `#ffe48f`) | page background with diagonal woven stripes |
| ink | `#2b1a0c` | all text, borders, button shadows |
| paper | `#fffaf0` | sign faces, pills, tiles, cards behind text |
| sentence paper | `#fffdf6` | sentence box, book page, summary panels |
| answer (hi) | `#b23c06` on `#fff0c2` | filled letters and words, highlighted words in the story |
| wood | `#8a5426`, dark `#5c3714`, frame gradient `#d39556 → #a9672f` | frames, borders, shadows |
| awning orange / cream | `#ef661c` / `#fff4dc` | top awning, shop 1, stall A |
| awning green | `#2f8f4e` / `#eafbe9` | shop 2, stall B |
| awning blue | `#2b62a8` / `#e6f0ff` | stall C, cover badge |
| word card | `#dcebff`, border and shadow `#1d4478` | **every** word card in one colour |
| active blank | border `#1d4478`, fill `#e6f0ff`, a "?" mark | the blank a tap will fill |
| correct | text `#14532a` on `#d4f4da` | ✔ feedback, ok chips |
| try again | text `#7a2e05` on `#ffe4cf` | ↺ feedback, review chips |
| hint | text `#574100` on `#fff4b0`; clue highlight `#fff07a` + underline `#9a6b00` | 💡 feedback, clue word |
| go button | `#8fe39a` | เริ่มเล่น, เริ่มเลย, ไปต่อ, กลับแผนที่ |
| hint button | `#ffe36e` | 💡 คำใบ้ |
| stamp | `#a3201a` | "ผ่านแล้ว ✔" ink stamp |
| confetti | `#ef661c #ffc21a #2f9e44 #3b82d6 #e8456b #9b59d0` | bursts, confetti, bunting |

Text is always dark on light. White text appears only on the blue cover
badge and the green ✔ circle.

## 4. Typography

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mali:wght@400;600;700&display=swap">
```
`font-family: 'Mali','Itim','Leelawadee UI','Leelawadee','Thonburi','Noto Sans Thai','Sarabun','Tahoma',sans-serif;`

Mali has looped Thai letters, which early readers recognise from school
books. Fallbacks keep the layout working offline (the template was checked
with a fallback font).

Type scale in stage units (bold 700 unless noted):

| Element | Size |
|---|---|
| cover title | 12.6 |
| sign word (missing-letter task) | 12.5 (fit down to 7 for long words) |
| letter tile glyph | 11 |
| title on the map board | 8.6 |
| ไปต่อ / เริ่มเลย | 7–7.5 |
| sentence (cloze) | 6.8, fit down to 5 only for teacher-added long text |
| word card | 6.4 (fit down to 4.4 so the row stays on one line) |
| shop name | 6.4 |
| story page (whole story) | fit from 6.4 (lands near 5.6) |
| feedback pill | 4.7 (fit down to 3.4) |
| hint button | 4.8 |
| subtitles, bubbles | 3.6–4.8 (600) |
| status pill | 3.4 |
| teacher buttons | 2.7 |
| summary panels | 3.4, fit down to 2.2 |

Line-heights: single-line Thai ≥ 1.42, sentences 1.95 (room for blank
boxes), multi-line reading text 1.62, cards and tiles use fixed `line-height`
in u.

## 5. Textures

**Awning tile** (one orange and one cream stripe, scalloped; repeat-x, 14.8u × 9.6u):
```js
function awningTile() {
  var d1 = 'M0 8H74V48A37 37 0 0 1 0 48Z', d2 = 'M74 8H148V48A37 37 0 0 1 74 48Z';
  var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 148 96" preserveAspectRatio="none">' +
    '<g fill="rgba(70,30,0,.18)" transform="translate(0 5)"><path d="' + d1 + '"/><path d="' + d2 + '"/></g>' +
    '<path d="' + d1 + '" fill="#ef661c"/><path d="' + d2 + '" fill="#fff4dc"/>' +
    '<rect x="0" y="0" width="148" height="10" fill="#7a4a1f"/></svg>';
  return 'url("data:image/svg+xml,' + encodeURIComponent(svg) + '")';
}
```

**Background**: mango base, two 45° repeating stripes (white 16% and brown
10%, 1.1u on 4.4u), plus a radial glow at 50% 40%.

**Wood frame**: `.wood-frame` has 1.2u padding, a vertical gradient
`#d39556 → #a9672f`, faint horizontal grain, a 1u bottom shadow in
`#5c3714`, and two nail heads drawn by `:before/:after`. Inside it sits a
`.sign-face` (paper, inset border `#e3c393`), where the text goes.

**Woven frame** (pictures and scenes): `.woven` crosses two 45° repeating
gradients over `#d6a253`, with a 0.9u bottom shadow.

**Basket**: woven body with a large bottom radius, an arc handle (border
without bottom), and reward items placed *between* handle and body so they
peek out. A label pill on the front shows the count, or the reward message.

**Bunting** (cover): a string line plus inline-block CSS triangles in the
confetti colours.

**Floor**: horizontal plank lines over `#c98a4b → #9a5c2a` with a dark
`#6b3e19` top edge.

## 6. Components

**Pressable button `.btn`**: 0.5u ink border, 3u radius, white or a colour
fill, `box-shadow: 0 1.2u 0 ink`. In the `.pressed` state (added on
pointerdown, which is more reliable than `:active` on TVs) it gets
`translateY(1u)` and the shadow shrinks to 0.2u. `.off` means disabled: 40%
opacity, already pressed down. Variants: `.btn-go` (green),
`.btn-next` (15.5u tall, 7u text), `.btn-hint` (25u × 15u, yellow, with a count
badge circle in the top-right corner), `.btn-start` (16u), `.btn-teach`
(paper colour, 12u).

**Letter tile `.tile`**: 16.5u square, paper fill, ink border, brown bottom
shadow, glyph 11u. States: `.ghost` (left behind while dragging), `.dim`
(wrong: 35% opacity plus a ✖ badge), `.removed` (taken away by a hint: pops
out), `.gone` (used: `visibility:hidden`, so the space stays).

**Word card `.card`**: 14u tall, padding 0.5em, one colour for all
(`#dcebff` and `#1d4478`), font size inherited from the `.bank` row so the
row can be fitted as a whole.

**Slot `.slot`** (missing letter inside a word): an inline-block with a
dashed wood border, white fill and an invisible placeholder "ก" that sets
width and baseline. `.filled` switches to a solid answer-colour border, the
`#fff0c2` fill and the visible letter. `.hinted` adds a yellow ring that
pulses 3 times. `.drop-hover` turns it light blue while something is dragged
over it.

**Blank `.blank`** (whole word inside a sentence): an inline-block with a
uniform min-width of 3.1em, so its length gives no clue. Empty means a
dashed border. `.active` means a solid blue border, a "?" mark and a soft
glow pulse. `.filled` shows the word in the answer colour. The clue word for
a hint is a `.clue` span; `.clue.on` gives it a yellow highlight and an
underline.

**Feedback pill `.fb`** in zone C: one line, 4.7u, icon first.
`.fb-ok` / `.fb-re` / `.fb-tip`. It pops in on every new message.

**Big check**: a 13u green circle with a white SVG check, overlapping the
top-right corner of the sign. It spins and pops in on a correct answer.

**Status pill** (top-left, on the awning): shop icon, name, "ป้ายที่ 2 / 5".
Max width 112u, so it never meets the teacher buttons.

**Teacher buttons** (top-right, 5.4u tall): 🔊 เสียง: เปิด/ปิด, หน้าแรก
(hidden on the cover and the map), เต็มจอ (hidden when the Fullscreen API is
missing).

**Shop card** (map): 62u × 41.5u paper card with a striped mini awning in the
shop's colour, a 13u bobbing emoji, the name, "ด่าน n · skill", a round stop
number at the top-left, and a rotated red ink stamp "ผ่านแล้ว ✔" once
finished.

**Progress boards** (Level 1): small numbered boards. The current one has a
thick ring, finished ones turn green with a check. A star flies into each one.

**Summary chips**: ✔ word (green), ↺ word with an error count (orange),
dashed for "ยังไม่ตอบ", yellow 💡 for hint steps.

## 7. Icons and emoji

Draw UI icons as inline SVG with `stroke="currentColor"`. Glyphs like ✔ ↺ ▶
are missing from some TV fonts. The template's `IC` object has: `check`,
`retry` (↺), `next` (▶), `cross`, `home`, `full`, `sound`, `mute`. The star is
`starSVG(fill)`.

Emoji are the pictures: word pictures, scenes, shops, rewards and the
cartoon ✋ hand. Rules:
- Store a scene as an array of emoji, one per item. ZWJ sequences such as
  👩‍👧 count as one item, so never split strings by character.
- Add a caption when the emoji alone is ambiguous (🍌 for หยวกกล้วย). Check
  whether the caption reveals the answer.
- Never let an emoji be the *only* carrier of meaning in feedback. That job
  belongs to SVG icons plus text.

## 8. Motion catalogue

One clear animation per event; idle motion stays subtle. All of it is
switched off under `prefers-reduced-motion`.

| Class or function | What it does | Used on |
|---|---|---|
| `in-drop` | bounces up from below (0.55 s, `backwards`) | tiles, cards, shops, stalls, recap cards |
| `in-pop` | scales from 0.6 to 1 | picture frames, basket, start button, bubble |
| `in-rise` | slides up 25% with a fade | sentence box, story lines, demo text |
| `in-swing` | a hanging sign swings in | map title board, Level 1 sign, cover sign |
| `delayStyle(sec)` | inline `animation-delay` to stagger | rows of pieces |
| `bob` (idle) | 6% float | scene emoji, picture emoji, shop emoji, stall goods |
| `sway` (idle) | ±1° on hanging signs | title boards |
| `glow` (idle) | soft ring pulse | the active blank |
| `shake` | wrong-answer wiggle | tile, card, slot, blank |
| `checkin`, `pop` | correct-answer badge and filled slot | big check, slot, progress board |
| `hopword` (`.wave`) | filled words hop one after another | finished sentence |
| `hop` / `runby` | the scene celebrates (page `anim: 'run'` for chases) | scene emoji |
| `stampin` | stamp drops onto the shop card | map |
| `burst(el, n, spread)` | stars and confetti burst from an element | correct answer, page done, basket |
| `confetti(n)` | confetti rains over the whole screen | finish screens |
| `flyStar(from, to, done)` | a star flies to the progress board | Level 1 correct answer |

Order matters in the CSS: entrance and idle classes first, then `.shake`,
then `.removed`. Pressable elements use only `backwards` fill.

## 9. Cover page composition

- Bunting under the awning.
- A big hanging wood sign: the title at 12.6u, with the target letters
  highlighted in the answer colour (in "วัน**ห**นึ่งที่**ต**ลาด" both leading
  consonants are coloured), a subtitle, and a rotated blue badge "ภาษาไทย
  ป.1–3".
- Three stalls with striped awnings, poles, a wooden counter with a label
  (ผักสด / ขนมหวาน / หนังสือ) and bobbing goods. The labels can reuse target
  words.
- A child with a basket (👧🧺) walking along the bottom, behind the button.
- The เริ่มเล่น button at 80.5u with a breathing ring, and a small teacher
  note at the bottom-left: "ครู: แตะ “เต็มจอ” ที่มุมขวาบน ก่อนเริ่มเล่น".

## 10. Giving a new game its own flavour

Keep the system and vary the content:
- **Stalls and goods**: fruit stall for สระ, fish stall for มาตราตัวสะกด, toy
  stall for คำควบกล้ำ.
- **Stall and shop awning colours**: use the existing three pairs, or derive
  a new pair at the same lightness, a strong stripe plus a pale one.
- **Shopkeeper** (👵 in Level 1): any market character with a short speech
  bubble.
- **Rewards**: a market item that matches the shop (🥬, 📚, 🐟, 🍉).
- **Scene backgrounds**: the `bg-*` gradients (sky, market, veg, pink, sun,
  park, book). Add new ones in the same pale style.

Avoid changing the font, the ink and paper contrast, the pressable-card
shape or the zone layout. Those carry the usability.
