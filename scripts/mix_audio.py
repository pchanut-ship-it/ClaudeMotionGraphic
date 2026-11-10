#!/usr/bin/env python3
"""Build the final soundtrack (56 s): voice-over + background music + sound effects.

    python3 scripts/mix_audio.py assets/audio/vo.wav assets/audio/bg_music.mp3 output/sfx.wav output/mix.wav

1. VO — the narration arrives as one continuous take. It is cut at the pauses
   between sentences (found with ffmpeg silencedetect, -40 dB / 0.25 s) and each
   sentence is placed so its first syllable lands on its scene's slot (the start
   times of CAPS in index.html).
2. Music — starts at 0 (the track has its own 2 s fade-in), fades out under the
   credit card, and ducks ~7 dB whenever the VO speaks (sidechain compression).
3. SFX — output/sfx.wav, kept under the voice.
4. Two-pass EBU R128 loudness normalisation to −16 LUFS, true peak −1.5 dBTP.
"""
import json, subprocess, sys

DUR = 56.0
PAD_IN, PAD_OUT = 0.06, 0.10   # keep a little air before/after each sentence

# (speech start, speech end) in the source VO take  →  slot where the speech must start
SEGMENTS = [
    # src_start src_end  slot   sentence
    (0.00,  2.49,  0.30),   # 1  เมื่อเราขอให้ AI ช่วยเขียน…
    (3.08,  7.59,  4.25),   # 2  AI จะเขียนทีละคำ …
    (8.13, 13.39,  9.25),   # 3  ระบบลายน้ำใช้กุญแจลับ … (two phrases, short pause kept)
    (13.93, 19.09, 15.25),  # 4  แล้วเพิ่มคะแนนให้ “กลุ่มพิเศษ” … (two phrases)
    (19.90, 23.44, 21.25),  # 5  ทำซ้ำทุกคำ …
    (24.25, 27.05, 26.25),  # 6  ข้อความจึงมีคำจากกลุ่มพิเศษ …
    (27.93, 31.07, 30.25),  # 7  แต่คนอ่านเห็นเป็นข้อความธรรมดา …
    (31.98, 35.12, 34.25),  # 8  เครื่องมือที่มีกุญแจเดียวกัน …
    (35.79, 38.92, 37.60),  # 9  ถ้ามีมากเกินกว่าความบังเอิญ …
    (39.58, 43.59, 41.25),  # 10 แต่ถ้าข้อความสั้น …
    (44.22, 47.55, 46.25),  # 11 ลายน้ำจึงเป็นหลักฐานเพียงส่วนหนึ่ง …
]

VO_GAIN_DB = 5.0       # VO take is ≈ −21 LUFS → ≈ −16
MUSIC_GAIN_DB = -10.0  # track is ≈ −12.5 LUFS → ≈ −22.5 in the gaps, ≈ −29 under the voice
SFX_GAIN_DB = -5.0     # sfx.wav is −19 LUFS → ≈ −24
MUSIC_FADE = (52.6, 3.4)


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def build_filter():
    parts, labels = [], []
    for i, (a, b, slot) in enumerate(SEGMENTS):
        s0, s1 = max(0.0, a - PAD_IN), b + PAD_OUT
        d = s1 - s0
        delay_ms = int(round((slot - (a - s0)) * 1000))
        parts.append(
            f"[0:a]atrim=start={s0:.3f}:end={s1:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.015,afade=t=out:st={d - 0.05:.3f}:d=0.05,adelay={delay_ms}[v{i}]")
        labels.append(f"[v{i}]")
    parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,aresample=48000,"
                 f"aformat=sample_fmts=fltp:channel_layouts=stereo,apad=whole_dur={DUR},volume={VO_GAIN_DB}dB,asplit=2[vo][vosc]")
    parts.append(f"[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=0:{DUR},asetpts=PTS-STARTPTS,"
                 f"volume={MUSIC_GAIN_DB}dB,afade=t=out:st={MUSIC_FADE[0]}:d={MUSIC_FADE[1]}[mus]")
    parts.append("[mus][vosc]sidechaincompress=threshold=0.03:ratio=4:attack=60:release=700:makeup=1[musd]")
    parts.append(f"[2:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad=whole_dur={DUR},"
                 f"atrim=0:{DUR},volume={SFX_GAIN_DB}dB[sfx]")
    parts.append("[vo][musd][sfx]amix=inputs=3:normalize=0,atrim=0:" + str(DUR) + "[mix]")
    return ";".join(parts)


def main(vo, music, sfx, out):
    raw = out.replace(".wav", "_raw.wav")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", vo, "-i", music, "-i", sfx,
         "-filter_complex", build_filter(), "-map", "[mix]", "-c:a", "pcm_s24le", raw])
    # two-pass loudnorm
    target = "I=-16:TP=-1.5:LRA=11"
    r = run(["ffmpeg", "-hide_banner", "-i", raw, "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"])
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
         f"loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
         f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
         "-ar", "48000", "-c:a", "pcm_s16le", out])
    subprocess.run(["rm", "-f", raw])
    print("wrote", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(*(a + ["assets/audio/vo.wav", "assets/audio/bg_music.mp3", "output/sfx.wav", "output/mix.wav"][len(a):]))
