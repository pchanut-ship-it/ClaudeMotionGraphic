# Thai text: blanks, marks, readings and copy

Thai stacks vowels and tone marks above and below consonants and has no
spaces between words. Most visual bugs in these games come from that. Follow
these rules wherever text is split, boxed or fitted.

## 1. Splitting a word around a blank

Render a missing-letter word as three pieces: `before` + `<span class="slot">` + `after`.

- The text **after** a blank must begin with a consonant or a leading vowel
  (เ แ โ ใ ไ). It must never begin with a combining mark:
  ั ิ ี ึ ื ุ ู ็ ่ ้ ๊ ๋ ์ ํ ำ ฺ. A span that starts with a combining mark
  renders a dotted circle (◌).
- The missing letter should be a base consonant that carries no marks of its
  own. That holds for all leading-consonant words (ห in หมู, กะ_ล่ำปลี,
  เ_ลือง). If a future task needs to blank a consonant that *carries* a vowel
  or tone, blank the whole cluster (consonant + marks) as one piece instead.
- Store the pattern in the data (`blank: 'กะ_ล่ำปลี'`) and derive the answer:
  `answer = word.charAt(blank.indexOf('_'))`, then check that
  `before + answer + after === word`. Skip rows that fail instead of showing
  a broken sign. Thai characters are single UTF-16 units, so `charAt` is
  safe.
- Leading vowels on their own (เ in เ_ลือง) render fine in a separate span.

## 2. The slot box

```css
.slot{display:inline-block;vertical-align:baseline;min-width:.8em;padding:0 .07em;line-height:1.12;
      border:.05em dashed var(--wood);border-radius:.14em;background:#fff;}
.slot .ch{visibility:hidden;}          /* placeholder "ก" sets width and baseline */
.slot.filled{border-style:solid;border-color:var(--hi);background:var(--hi-bg);}
.slot.filled .ch{visibility:visible;color:var(--hi);}
```
An invisible "ก" keeps the empty box one consonant wide and on the text
baseline. It was checked with Mali and with a fallback Thai font. Inside a
word, the box sits slightly high, because its height includes the space for
upper marks. That is acceptable.

## 3. Blanks for whole words (cloze)

- Use an inline-block with a **uniform** `min-width` (3.1em) when empty, so
  the blank length doesn't hint at the answer. It grows when filled.
- `line-height: 1.45` inside the blank and `1.95` on the sentence, so boxes
  on consecutive lines don't touch the upper marks of the line below.
- Mark the hint clue in the data with `[ ]`, because Thai has no spaces to
  find "the word before the blank" automatically:
  `'เช้า[วัน]{หนึ่ง} ฉัน[ล้าง]{หน้า} แล้วใส่[เสื้อตัว]{ใหม่}'`.
  A clue belongs to the next blank. A blank with no clue of its own uses the
  nearest earlier clue.
- Keep the original spaces between phrases. They are part of Thai
  punctuation.

## 4. Line height and clipping

- **Never put `overflow:hidden` on a line of Thai** unless it has padding.
  It cuts off ู ุ below the line and stacked marks such as ้ above ื
  (เสื้อ, ซื้อ). Text measured for width can stay `overflow: visible`,
  because `scrollWidth` still reports the overflow.
- Single line: line-height ≥ 1.42. Multi-line reading text: ≥ 1.6, or the
  stacked marks of one line collide with the line above. The story page
  needed 1.62.
- Add bottom padding to signs and boxes so lower vowels stay inside the
  frame.
- Check stacked marks by zooming into a screenshot (crop and scale it). At
  full-screen size they look fine even when clipped.

## 5. Fitting text

`fitText(el, maxU, minU, axis)` lowers the font size in 0.2u steps until
the element stops overflowing (`'h'`, `'w'` or `'hw'`). Requirements:
- The element needs a fixed size, or a max-height or width, so overflow can
  be measured.
- Transitions are disabled and animations paused while measuring (done
  inside `fitText`).
- Run it again after `document.fonts.ready` and on resize (`currentFit`).
- Choose `minU` to respect the size floors (sentences 6u, words 10u). If
  teacher-added content would need less, let it go lower rather than
  overflow, and mention it.

## 6. Reading guides (คำอ่าน)

The notation follows Thai school books:
- Phinthu (ฺ) under a silent leading letter: หมู → **หฺมู**, ใหม่ → **ไหฺม่**,
  อยาก → **หฺยาก**.
- A hyphen between syllables: กะหล่ำปลี → **กะ-หฺล่ำ-ปฺลี**, ขนม → **ขะ-หฺนม**,
  ตลาด → **ตะ-หฺลาด**, สนิทสนม → **สะ-หฺนิด-สะ-หฺนม**.
- Show the reading **after** a correct answer ("อ่านว่า …"), never before,
  so it doesn't give the answer away.
- Readings come from the data (`read` field). Don't generate them, because
  they are easy to get wrong.

## 7. Groups and hints for leading consonants (อักษรนำ)

| Group | Example | Hint 1 that is true for the whole group |
|---|---|---|
| ห นำ (silent ห) | หมู หญิง ใหม่ | ตัวอักษรนี้นำหน้า แต่ไม่ออกเสียง |
| อ นำ ย (silent อ) | อย่าง อยาก | ตัวอักษรนี้นำหน้า ย แต่ไม่ออกเสียง |
| high-class consonant leading a single low-class one | ขนม เสมอ | ตัวอักษรนี้ออกเสียงสั้น ๆ มีเสียง อะ |
| mid-class consonant leading a single low-class one | ตลาด อร่อย | ตัวอักษรนี้ออกเสียงสั้น ๆ มีเสียง อะ |

Write hints per group, with an optional per-word `tip` override. Check every
hint against every word it appears with.

## 8. Line breaking and fonts

- Modern browsers break Thai lines with a dictionary. Old ones may only break
  at spaces, so add `overflow-wrap: break-word` as a safety net. Splitting
  sentences into spans at blanks also creates safe break points.
- Mali (Google Fonts, `display=swap`) with fallbacks: Itim, Leelawadee UI,
  Thonburi, Noto Sans Thai, Sarabun, Tahoma. Test once with the font blocked.
- Check that the font has the phinthu (ฺ). Mali and the listed fallbacks do.

## 9. Copy for Grade 1–3

- Short sentences of 8 words or fewer, everyday words, a friendly นะ, and
  no grammar jargon in children's text (use "ตัวอักษรนี้นำหน้า", not
  "อักษรนำ"). Teacher text (summary, notes) may use the terms.
- Name the action the child does ("ลาก… หรือแตะ…ก็ได้").
- The shopkeeper and story characters speak in first person to make it a
  story ("ป้ายหลุดไป 1 ตัว ช่วยเติมหน่อยนะ").
