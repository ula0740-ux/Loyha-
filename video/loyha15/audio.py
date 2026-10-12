"""Loyha 15s soundtrack, 100 % synthesized: 120 BPM groove (quiet build, full on the 8.0 s drop),
riser into the drop, SFX on the exact animation times, two-pass loudnorm to -14 LUFS."""
import json, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
FF, SR, T, BEAT = "ffmpeg", 48000, 15.0, 0.5
N = int(T * SR)
mix = np.zeros(N)
rng = np.random.default_rng(7)


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def put(t0, s, g):
    i = int(round(t0 * SR)); j = min(N, i + len(s))
    if i < N: mix[i:j] += g * s[:j - i]


def kick(n=int(.35 * SR)):
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .12)


def hat(n=int(.06 * SR)):
    x = np.diff(rng.standard_normal(n + 1))
    return x * env(n, .0005, .015)


def clap(n=int(.2 * SR)):
    x = rng.standard_normal(n)
    e = sum(env(n, .001, .01) * (np.arange(n) >= int(k * SR)) for k in (0, .01, .02)) + env(n, .001, .06)
    return x * e * .5


def tone(f, dur, a=.003, d=.3, harm=(1, .3)):
    n = int(dur * SR); t = np.arange(n) / SR
    return sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm)) * env(n, a, d)


def pop(f0=500, f1=1100, dur=.09):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 + (f1 - f0) * t / dur
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .03)


def whoosh(dur=.45, up=True):
    n = int(dur * SR); x = rng.standard_normal(n)
    k = np.linspace(0, 1, n); w = np.sin(np.pi * (k if up else 1 - k) ** .7) ** 2
    y = np.convolve(x, np.ones(12) / 12, "same")
    return y * w


# pad: Am9 voicing, quiet before the drop, warm under the end card
pad_notes = [110, 164.81, 220, 261.63, 329.63, 493.88]
t = np.arange(N) / SR
pad = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate(pad_notes)) / len(pad_notes)
lvl = np.interp(t, [0, 1.5, 7.5, 8.0, 11.0, 11.4, 14.0, 15.0], [0, .10, .16, .05, .05, .14, .14, 0])
mix += pad * lvl

# groove
for b in np.arange(0, T, BEAT):
    if 4.0 <= b < 7.6: put(b, kick(), .35)
    if 8.0 <= b < 11.0: put(b, kick(), .9)
    if 8.0 <= b < 11.0 and int(round(b / BEAT)) % 2 == 1: put(b, clap(), .45)
for h in np.arange(2.0, 11.0, BEAT / 2):
    if h < 7.6 or h >= 8.0: put(h + (BEAT / 4 if h < 8 else 0), hat(), .10 if h < 8 else .16)
bass = {8.0: 55, 9.0: 55, 10.0: 65.41, 10.5: 49}
for b, f in bass.items(): put(b, tone(f, .5, .005, .25, (1, .5, .2)), .5)

# riser into the drop + impact
n = int(1.5 * SR); k = np.linspace(0, 1, n)
riser = np.convolve(rng.standard_normal(n), np.ones(6) / 6, "same") * k ** 2 * .5
riser += np.sin(2 * np.pi * np.cumsum(200 + 900 * k ** 2) / SR) * k ** 2 * .25
put(6.5, riser, .6)
put(8.0, kick(int(.9 * SR)) * 1.0, 1.0)
put(8.0, rng.standard_normal(int(.5 * SR)) * env(int(.5 * SR), .001, .12), .35)

# SFX on the animation
put(0.15, pop(380, 900, .12), .5)
for i in range(3): put(0.4 + i * .055, tone(1800, .05, .001, .015, (1,)), .12)
put(1.85, whoosh(.3), .12)
put(1.95, whoosh(.45), .22)
for i, tt in enumerate((2.3, 2.355, 2.8)): put(tt, tone(1700, .05, .001, .015, (1,)), .12)
put(3.85, whoosh(.4), .2)
put(4.35, tone(1500, .05, .001, .015, (1,)), .1)
for i in range(3): put(4.6 + i * .4, pop(420 + 60 * i, 900 + 80 * i), .3)
for i in range(3):
    put(5.75 + i * .5, tone(2200, .04, .0005, .01, (1,)), .3)       # click
    put(5.8 + i * .5, tone([659.25, 783.99, 987.77][i], .4, .003, .18), .18)  # rising check notes
for i in range(14): put(10.3 + i * .05, tone(2400, .03, .0005, .008, (1,)), .07)
put(10.95, tone(1318.5, .5, .002, .2), .15)
put(10.95, whoosh(.5), .25)
put(11.5, pop(300, 700, .14), .5)
put(11.8, kick(), .4)
for i, f in enumerate((880, 1318.5, 1760)): put(11.8 + i * .07, tone(f, 1.6, .003, .7), .10)
put(12.3, tone(1600, .05, .001, .015, (1,)), .08)

f0 = int(14.0 * SR); mix[f0:] *= np.linspace(1, 0, N - f0) ** 1.5
st = np.stack([mix, mix], 1).astype(np.float32)
st /= np.abs(st).max() * 1.1
rawp = HERE / "out/raw.wav"; rawp.parent.mkdir(exist_ok=True)
subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(rawp)], input=st.tobytes(), check=True)
m = subprocess.run([FF, "-hide_banner", "-i", str(rawp), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run([FF, "-v", "error", "-y", "-i", str(rawp), "-af", af, "-ar", str(SR), str(HERE / "out/audio.wav")], check=True)
print("audio ->", HERE / "out/audio.wav", "| input LUFS", j["input_i"])
