# ร่องรอยลับในข้อความ AI — AI ซ่อนลายน้ำในข้อความอย่างไร?

แอนิเมชันอธิบายแนวคิด 2D flat vector ความยาว 56 วินาที (16:9, 1920×1080, 30 fps) มีเสียงบรรยาย เพลงประกอบ และเสียงเอฟเฟกต์
storyboard ฉบับเต็มพร้อมพรอมป์ต์อยู่ใน [`STORYBOARD.md`](STORYBOARD.md) · สคริปต์เสียงบรรยายอยู่ใน [`VO_SCRIPT.md`](VO_SCRIPT.md)

**ไฟล์หลัก: `output/watermark-explainer-final.mp4`** (ไม่มีซับไตเติล มีชื่อคลิป ป้ายกำกับ ข้อความปิด และเครดิตเพลง)

| ฉาก | เวลา | เนื้อหา |
|---|---|---|
| 1 | 0–4 s | นักศึกษายื่นกระดาษให้หุ่นยนต์ AI |
| 2 | 4–26 s | กลไกลายน้ำ: AI ให้คะแนนคำถัดไป → กุญแจลับ + คำก่อนหน้า แบ่งคำเป็น 2 กลุ่ม → เพิ่มคะแนน “กลุ่มพิเศษ” เล็กน้อย → ทำซ้ำทุกคำ |
| 3 | 26–30 s | บัตรคำรวมเป็นข้อความ จุดม่วงกะพริบแล้วจางหาย |
| 4 | 30–34 s | คนอ่านเห็นข้อความธรรมดา |
| 5 | 34–41 s | เครื่องมือตรวจที่มีกุญแจเดียวกันนับคำกลุ่มพิเศษ เทียบกับระดับความบังเอิญ |
| 6 | 41–46 s | ข้อความสั้น / ถูกแก้ไข → สัญญาณอ่อนลงจนต่ำกว่าเกณฑ์ |
| 7 | 46–52 s | ลายน้ำเป็นจิ๊กซอว์หนึ่งชิ้นของหลักฐาน · “ไม่พบลายน้ำ ≠ ไม่ได้ใช้ AI” |
| เครดิต | 52–56 s | เครดิตเพลง |

## เครดิต

Music track: A Better Future by Bluewave
Source: https://freetouse.com/music
Free To Use Music for Video

ฟอนต์: Prompt (SIL Open Font License) ใน `assets/fonts/`

## ไฟล์
- `index.html` — ตัวแอนิเมชัน (SVG + JS) เปิดในเบราว์เซอร์ได้เลย มีปุ่มเล่น/หยุด แถบเลื่อนเวลา และสวิตช์ข้อความบนจอ/ซับไตเติล (ไม่มีเสียงในเบราว์เซอร์)
  - `?render=1` โหมดเรนเดอร์ 1920×1080 · `?subs=0` ซ่อนเฉพาะซับไตเติล · `?captions=0` ไม่มีข้อความเลย (clean plate)
- `output/watermark-explainer-final.mp4` — **ฉบับสุดท้าย** ไม่มีซับไตเติล + เสียงบรรยาย + เพลง + เอฟเฟกต์ + เครดิต
- `output/watermark-explainer.mp4`, `output/watermark-explainer-clean.mp4` — ฉบับก่อนหน้า (52 วินาที มีแค่เสียงเอฟเฟกต์ ไม่มีเสียงบรรยาย/เพลง)
- `output/sfx.wav` — แทร็กเสียงเอฟเฟกต์แยก (stem) 56 วินาที, −19 LUFS
- `assets/audio/vo.wav` — เสียงบรรยายต้นฉบับ (สร้างจาก Google AI Studio, อ่านต่อเนื่อง 47.9 วินาที)
- `assets/audio/bg_music.mp3` — เพลงประกอบ **ไม่ได้เก็บใน git** (เป็นเพลงที่มีเงื่อนไขการใช้งาน) ดาวน์โหลด “A Better Future” by Bluewave จาก freetouse.com แล้ววางไว้ที่ path นี้ก่อนมิกซ์ใหม่

## สคริปต์
- `scripts/sfx.py` — สังเคราะห์เสียงเอฟเฟกต์จากคลื่นไซน์และ noise ตาม cue list ที่ตรงกับไทม์ไลน์ภาพ
  `python3 scripts/sfx.py /tmp/raw.wav && ffmpeg -i /tmp/raw.wav -af loudnorm=I=-19:TP=-2:LRA=11 -ar 48000 output/sfx.wav`
- `scripts/mix_audio.py` — ตัดเสียงบรรยายเป็นประโยคตามช่วงเงียบ วางแต่ละประโยคให้ตรงฉาก ลดเสียงเพลงอัตโนมัติขณะมีเสียงพูด (ducking) เฟดเพลงออกช่วงเครดิต แล้วปรับความดังรวมเป็น −16 LUFS → `output/mix.wav`
  `python3 scripts/mix_audio.py` (ค่าเริ่มต้น: `assets/audio/vo.wav`, `assets/audio/bg_music.mp3`, `output/sfx.wav`)
  ถ้าอัดเสียงบรรยายใหม่ ต้องแก้ตาราง `SEGMENTS` (ช่วงเวลาของแต่ละประโยคในไฟล์ VO) — หาได้ด้วย `ffmpeg -i vo.wav -af silencedetect=noise=-40dB:d=0.25 -f null -`
- `scripts/render.js` — เรนเดอร์ MP4: `node scripts/render.js output/watermark-explainer-final.mp4 --nosubs`
  (ใส่เสียงจาก `output/mix.wav` อัตโนมัติ, `--clean` = ไม่มีข้อความ, `--audio=path` = เลือกไฟล์เสียงเอง; ต้องมี Playwright + ffmpeg)
- `scripts/snap.js` — ถ่ายภาพนิ่ง ณ เวลาที่กำหนด: `node scripts/snap.js <dir> 2.0 12.8 27`
