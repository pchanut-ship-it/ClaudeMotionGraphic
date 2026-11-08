#!/usr/bin/env python3
"""Synthesize the sound-effects track for index.html (52 s) — no samples, no licences.

Every sound is generated from sine waves and filtered noise, then placed on a cue
list whose times come from the animation timeline in index.html.

    python3 scripts/sfx.py output/sfx.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 52.0
rng = np.random.default_rng(7)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def env_ad(n, a, d_tau):
    """attack (s) then exponential decay with time constant d_tau (s)."""
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), np.exp(-(t - a) / d_tau))
    return e


def env_hann(n):
    return np.sin(np.linspace(0, np.pi, n)) ** 2


def svf(x, fc, q=0.7, mode="bp"):
    """State-variable filter; fc may be a scalar or an array (sweeps)."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    f = 2 * np.sin(np.pi * np.clip(fc, 20, SR / 6) / SR)
    damp = 1 / q
    low = band = 0.0
    out = np.empty_like(x)
    for i in range(len(x)):
        high = x[i] - low - damp * band
        band += f[i] * high
        low += f[i] * band
        out[i] = band if mode == "bp" else (low if mode == "lp" else high)
    return out


def noise(d):
    return rng.standard_normal(int(d * SR))


# ---------------------------------------------------------------- sound designs
def pop(freq=520, d=0.12, drop=0.45, vol=0.5):
    t = t_axis(d)
    f = freq * (1 + drop * np.exp(-t / 0.015))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return vol * np.sin(ph) * env_ad(len(t), 0.002, 0.035)


def tick(freq=2600, vol=0.25):
    d = 0.05
    t = t_axis(d)
    s = np.sin(2 * np.pi * freq * t) * env_ad(len(t), 0.0005, 0.008)
    n = svf(noise(d), 4500, 1.5, "bp") * env_ad(len(t), 0.0005, 0.004)
    return vol * (s + 0.6 * n)


def whoosh(d=0.6, f0=500, f1=2200, vol=0.35, q=1.2):
    n = len(t_axis(d))
    fc = np.geomspace(f0, f1, n)
    return vol * svf(noise(d), fc, q, "bp") * env_hann(n) * 0.6


def chime(freqs=(1568, 2093, 2637), stagger=0.045, d=0.9, vol=0.22):
    out = np.zeros(int((d + stagger * len(freqs)) * SR))
    for k, f in enumerate(freqs):
        t = t_axis(d)
        s = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2.01 * t)) * env_ad(len(t), 0.003, 0.22)
        i0 = int(k * stagger * SR)
        out[i0:i0 + len(s)] += s
    return vol * out / len(freqs) * 1.6


def sparkle(base=1760, vol=0.18):
    return chime((base, base * 1.26, base * 1.5, base * 2), 0.03, 0.6, vol)


def whirr(d=1.2, f0=260, f1=620, vol=0.22):
    t = t_axis(d)
    f = np.geomspace(f0, f1, len(t)) * (1 + 0.03 * np.sin(2 * np.pi * 9 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 14 * t)
    air = svf(noise(d), np.geomspace(800, 2400, len(t)), 2, "bp") * 0.4
    return vol * (s * trem + air) * env_hann(len(t)) * 0.7


def power_up(d=0.9, f0=420, f1=980, vol=0.22):
    t = t_axis(d)
    f = np.geomspace(f0, f1, len(t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.5 * np.sin(1.5 * ph) + 0.25 * np.sin(2 * ph)
    e = np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - d * 0.7) / 0.08)
    return vol * s * e * 0.6


def key_click(vol=0.35):
    d = 0.18
    t = t_axis(d)
    s = (np.sin(2 * np.pi * 2480 * t) + 0.7 * np.sin(2 * np.pi * 4130 * t) + 0.4 * np.sin(2 * np.pi * 6020 * t)) * env_ad(len(t), 0.0005, 0.03)
    s2 = np.zeros_like(s)
    i0 = int(0.045 * SR)
    s2[i0:] = s[: len(s) - i0] * 0.6
    thump = np.sin(2 * np.pi * 140 * t) * env_ad(len(t), 0.001, 0.025)
    return vol * (0.5 * (s + s2) + 0.6 * thump)


def scan(d=2.4, vol=0.12):
    t = t_axis(d)
    f = 880 + 220 * t / d
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * (0.6 + 0.4 * np.sin(2 * np.pi * 22 * t))
    hiss = svf(noise(d), 3200, 1.0, "bp") * 0.35
    e = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.3)
    return vol * (s + hiss) * e


def blip(freq=1320, vol=0.2):
    d = 0.09
    t = t_axis(d)
    return vol * (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)) * env_ad(len(t), 0.002, 0.025)


def bell(f=880, d=1.6, vol=0.25):
    t = t_axis(d)
    parts = [(1, 1), (2.0, 0.5), (2.76, 0.35), (5.4, 0.15)]
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (0.5 / r ** 0.5)) for r, a in parts)
    return vol * s * np.minimum(1, t / 0.003) * 0.6


def scribble(d=0.7, vol=0.22):
    t = t_axis(d)
    n = svf(noise(d), 3000 + 1200 * np.sin(2 * np.pi * 7 * t), 1.4, "bp")
    strokes = np.clip(np.sin(2 * np.pi * 11 * t + 2 * np.sin(2 * np.pi * 3 * t)), 0, 1) ** 0.7
    return vol * n * strokes * env_hann(len(t)) * 1.2


def snap(vol=0.4):
    d = 0.2
    t = t_axis(d)
    click = svf(noise(d), 2200, 1.2, "bp") * env_ad(len(t), 0.0005, 0.006)
    thump = np.sin(2 * np.pi * 95 * t * (1 + 0.6 * np.exp(-t / 0.01))) * env_ad(len(t), 0.001, 0.05)
    return vol * (1.4 * click + 0.9 * thump)


def soft_swell(d=1.8, vol=0.12):
    n = len(t_axis(d))
    return vol * svf(noise(d), np.geomspace(200, 900, n), 0.8, "lp") * env_hann(n)


def chord(freqs=(523.25, 659.25, 783.99, 987.77), d=3.0, vol=0.16):
    t = t_axis(d)
    s = sum(np.sin(2 * np.pi * f * t + k) + 0.2 * np.sin(2 * np.pi * 2 * f * t) for k, f in enumerate(freqs))
    e = np.minimum(1, t / 0.25) * np.exp(-np.maximum(0, t - 0.25) / 1.1)
    return vol * s / len(freqs) * e * (1 + 0.04 * np.sin(2 * np.pi * 5 * t))


def descend(freq=700, vol=0.18):
    return pop(freq, 0.14, -0.25, vol)


# ---------------------------------------------------------------- cue list
# (time in seconds, sound) — times mirror the timeline constants in index.html
def cues():
    c = []
    add = lambda t, s: c.append((t, s))
    # Scene 1 — asking the AI (0–4)
    add(0.15, chime((1046.5, 1318.5, 1568), 0.06, 1.0, 0.16))      # title
    add(0.35, whoosh(1.2, 300, 1400, 0.22))                        # paper slides across
    add(1.42, tick(1800, 0.18))                                    # robot grabs paper
    add(1.6, blip(660, 0.16)); add(1.95, blip(780, 0.14))          # nod nod
    add(2.2, pop(700, 0.12, 0.6, 0.24))                             # pencil up
    # scene transitions
    for tt in (3.85, 25.9, 29.85, 33.85, 40.85, 45.85):
        add(tt, whoosh(0.45, 400, 2600, 0.2))
    # Scene 2A — writing word by word
    add(4.2, pop(480, vol=0.32)); add(4.3, pop(540, vol=0.32))
    for i in range(5):
        add(5.0 + i * 0.15, pop(520 + 70 * i, vol=0.3))
    add(6.0, power_up(1.3, 300, 640, 0.12))                         # bars grow
    # Scene 2B — key + previous word → split
    add(9.3, pop(380, 0.16, 0.7, 0.38))                              # mixer appears
    add(9.4, whoosh(0.9, 600, 2400, 0.22))                           # key flies in
    add(10.35, key_click(0.2))                                       # key docks
    add(10.0, whoosh(0.8, 1600, 500, 0.16))                          # previous word drops in
    add(10.8, whirr(1.25, 240, 640, 0.24))                           # shuffle
    add(11.9, whoosh(0.5, 2500, 5000, 0.16, 3))                      # beams
    add(12.25, sparkle(1760, 0.2))                                   # special group marked
    # Scene 2C — boost + pick
    add(15.4, power_up(1.1, 440, 1040, 0.2))                         # small boost
    add(17.65, tick(2200, 0.2))                                      # winner highlighted
    add(18.4, whoosh(1.0, 700, 2000, 0.2))                           # flies to the row
    add(19.55, tick(1500, 0.28)); add(19.6, sparkle(2093, 0.16))     # placed + hidden dot
    add(20.1, whoosh(0.6, 500, 1100, 0.12))                          # row shifts
    # Scene 2D — fast repeats (s = cycle start), dot only when a special word won
    for s, has_dot in ((21.0, True), (22.55, False), (24.1, True)):
        add(s, tick(2000, 0.16))
        add(s + 0.3, whirr(0.32, 320, 620, 0.16))
        add(s + 0.5, sparkle(1980, 0.12))
        add(s + 0.68, power_up(0.25, 520, 980, 0.13))
        add(s + 0.9, whoosh(0.4, 800, 2000, 0.15))
        add(s + 1.28, tick(1500, 0.24))
        if has_dot:
            add(s + 1.3, sparkle(2093, 0.13))
    add(25.35, whoosh(0.65, 500, 1500, 0.18))                        # words regroup
    # Scene 3 — words become text, pattern blinks once
    add(26.05, soft_swell(0.8, 0.14))
    for i in range(6):
        add(27.25 + i * 0.14, tick(1200 + 60 * i, 0.16))             # each card lands as a line
    add(28.15, chime((2093, 2637, 3136, 4186), 0.02, 1.2, 0.22))     # shimmer
    # Scene 4 — reader
    add(30.3, whoosh(0.5, 300, 900, 0.1))                            # paper rustle
    add(31.95, blip(560, 0.1))                                       # nod
    add(32.05, soft_swell(1.9, 0.12))                                # zoom in
    # Scene 5 — detector with the same key
    add(34.2, whoosh(0.9, 600, 2400, 0.22))
    add(35.05, key_click(0.2))
    add(35.2, scan(2.4, 0.12))
    for tt in (35.76, 36.10, 36.26, 36.60):                          # dots light up as the scan passes
        add(tt, blip(1480, 0.16))
    add(37.8, pop(420, 0.16, 0.6, 0.36))                             # result panel
    add(38.5, power_up(0.8, 330, 520, 0.12))                         # chance bar
    add(38.8, power_up(1.1, 440, 1100, 0.16))                        # this-text bar
    add(39.9, bell(988, 1.8, 0.26))                                  # watermark found
    # Scene 6 — short / edited text
    for k, i in enumerate(range(7, 2, -1)):
        add(41.4 + (7 - i) * 0.18, descend(820 - 70 * k, 0.15))
    add(41.6, power_up(1.0, 700, 420, 0.1))                          # meter drops
    for i in range(3):
        add(43.0 + i * 0.7, scribble(0.7, 0.2))
    add(43.15, pop(1200, 0.1, -0.3, 0.2)); add(44.86, pop(1100, 0.1, -0.3, 0.2))   # dots pop
    add(43.2, power_up(1.8, 600, 300, 0.09))                         # meter falls below threshold
    # Scene 7 — puzzle
    add(46.0, whoosh(0.8, 1800, 600, 0.18))
    add(46.5, pop(400, 0.16, 0.7, 0.34))
    add(47.0, whoosh(0.9, 400, 1400, 0.2))
    add(47.3, whoosh(0.9, 500, 1600, 0.2))
    add(49.15, snap(0.22)); add(49.32, snap(0.19))
    add(49.4, chord(d=3.2, vol=0.18))                                # closing text
    return c


def main(out):
    buf = np.zeros(int(DUR * SR) + SR)
    for t0, s in cues():
        i0 = int(t0 * SR)
        buf[i0:i0 + len(s)] += s[: len(buf) - i0]
    buf = buf[: int(DUR * SR)]
    # tiny stereo width: delay right channel 0.4 ms, gentle soft-clip, normalize to −3 dBFS
    left = buf
    right = np.concatenate([np.zeros(20), buf[:-20]])
    st = np.stack([left, right], 1)
    st = np.tanh(st * 1.2) / np.tanh(1.2)
    st *= 10 ** (-3 / 20) / max(1e-9, np.abs(st).max())
    fade = int(0.4 * SR)
    st[-fade:] *= np.linspace(1, 0, fade)[:, None]
    pcm = (st * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", out, f"{len(pcm) / SR:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "output/sfx.wav")
