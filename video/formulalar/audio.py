"""Soundtrack: ElevenLabs narration placed on the timeline, a synthesized 100 BPM corporate bed
(Bm-G-D-A) ducked under the voice, SFX on the transitions and key numbers, two-pass loudnorm -14 LUFS."""
import json, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
TL = json.loads((HERE / "audio/timeline.json").read_text())
S, T = TL["scenes"], TL["total"]
SR = 48000
N = int(T * SR) + SR
rng = np.random.default_rng(11)
t = np.arange(N) / SR


def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def env(n, a=.003, d=.2):
    x = np.arange(n) / SR
    return np.minimum(1, x / a) * np.exp(-x / d)


def put(buf, t0, s, g=1.0):
    i = int(round(t0 * SR)); j = min(len(buf), i + len(s))
    if 0 <= i < len(buf): buf[i:j] += g * s[:j - i]


W = lambda sid, i: S[sid]["words"][i]["t"]

# ---------- voice
voice = np.zeros(N)
for sid in TL["order"]:
    put(voice, S[sid]["vo"], load(HERE / f"audio/{sid}.mp3"))

# ---------- music bed (100 BPM, bar = 2.4 s)
BEAT = 0.6
chords = [[57, 60, 64], [53, 57, 60], [60, 64, 67], [55, 59, 62]]  # Am F C G (midi), techno-ish
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
pad = np.zeros(N); bass = np.zeros(N)
for b in range(int(T / 2.4) + 1):
    ch = chords[b % 4]; t0 = b * 2.4; n = int(2.6 * SR)
    x = np.arange(n) / SR
    e = np.minimum(1, x / .5) * np.minimum(1, np.maximum(0, (2.6 - x) / .4))
    p = sum(np.sin(2 * np.pi * hz(m) * x) + .3 * np.sin(2 * np.pi * 2 * hz(m) * x + .5) for m in ch) / 3
    put(pad, t0, p * e, .18)
    put(bass, t0, np.sin(2 * np.pi * hz(ch[0] - 24) * x) * e, .22)
kick = np.zeros(N); hat = np.zeros(N)
def kick_s(n=int(.3 * SR)):
    x = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-x * 28)) / SR) * env(n, .001, .1)
groove_on, groove_off = S["tt1"]["start"], S["outro"]["start"]
for k in np.arange(0, T, BEAT):
    if groove_on <= k < groove_off: put(kick, k, kick_s(), .5)
    if groove_on <= k < groove_off: put(hat, k + BEAT / 2, np.diff(rng.standard_normal(int(.05 * SR) + 1)) * env(int(.05 * SR), .0005, .012), .07)
music = pad + bass + kick + hat
fade_in = np.clip(t / 1.5, 0, 1); fade_out = np.clip((T - t) / 2.5, 0, 1)
music *= fade_in * fade_out

# duck the music under the voice (smoothed voice envelope)
venv = np.abs(voice)
win = int(.15 * SR); venv = np.convolve(venv, np.ones(win) / win, "same")
duck = 1 - .62 * np.clip(venv / (venv.max() * .25 + 1e-9), 0, 1)
music *= duck

# ---------- SFX
sfx = np.zeros(N)
def whoosh(d=.5):
    n = int(d * SR); x = rng.standard_normal(n); k = np.linspace(0, 1, n)
    return np.convolve(x, np.ones(10) / 10, "same") * np.sin(np.pi * k ** .8) ** 2
def pop(f0=420, f1=980, d=.1):
    n = int(d * SR); x = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f0 + (f1 - f0) * x / d) / SR) * env(n, .001, .03)
def tone(f, d, dec=.3):
    n = int(d * SR); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * x) + .25 * np.sin(4 * np.pi * f * x)) * env(n, .002, dec)
def tick(): return tone(2200, .03, .008)

put(sfx, .15, pop(300, 700, .12), .35)                    # dot
for k in np.arange(.9, 4.2, .25): put(sfx, k, tick(), .1)    # stopwatch
put(sfx, W("hook", 2), kick_s(), .6); put(sfx, W("hook", 3), kick_s(int(.6 * SR)), .8)
put(sfx, S["intro"]["start"] - .35, whoosh(.5), .3)           # zoom through the dot
put(sfx, W("intro", 3), kick_s(int(.8 * SR)), .9)             # 7
for i in range(7): put(sfx, W("intro", 5) + i * .12, pop(500 + 40 * i, 1100 + 60 * i, .06), .2)
for sid in ["tt1", "jph1", "ct"]:                              # green flash + enter key
    put(sfx, S[sid]["start"] - .15, whoosh(.3), .3); put(sfx, S[sid]["start"], kick_s(int(.7 * SR)), .9); put(sfx, S[sid]["start"] + .05, tone(1760, .2, .05), .2)
for sid in ["att1", "over", "outro"]: put(sfx, S[sid]["start"] - .3, whoosh(.6), .32)   # scanline
for sid, i in [("tt1", 7), ("tt2", 0), ("tt2", 4), ("tt2", 8), ("att2", 0), ("att2", 9), ("jph2", 1), ("jph3", 1), ("over", 10), ("outro", 6)]:
    for k in range(6): put(sfx, W(sid, i) + k * .07, tick(), .12)  # decoding text
def counter(t0, d): 
    for k in np.arange(0, d, .06): put(sfx, t0 + k, tick(), .1)
counter(W("tt2", 16), W("tt2", 21) - W("tt2", 16)); put(sfx, W("tt2", 21), tone(880, .6, .25), .2); put(sfx, W("tt2", 21), tone(1318.5, .6, .25), .12)
k0 = S["tt3"]["start"] + .3
for n in range(int((S["att1"]["start"] - k0) / 1.45)): put(sfx, k0 + n * 1.45, pop(200, 400, .1), .25)   # conveyor steps
put(sfx, W("att1", 4), kick_s(), .6)
put(sfx, W("att1", 6), whoosh(.25), .3); put(sfx, W("att1", 6) + .18, whoosh(.25), .3)                # X
for i in range(17): put(sfx, W("att1", 6) + .1 + i * 1.0 / 17, pop(400 + 20 * i, 900 + 30 * i, .05), .12)
counter(W("att2", 13), W("att2", 18) - W("att2", 13)); put(sfx, W("att2", 18), tone(659.3, .6, .25), .2)
counter(W("jph1", 10), 1.2); put(sfx, W("jph1", 10), kick_s(), .6)
for sid in ["jph2", "jph3"]:
    counter(W(sid, 12), .9); put(sfx, W(sid, 12) + .9, tone(987.8, .5, .2), .2); put(sfx, S[sid]["start"], whoosh(.4), .2)
put(sfx, W("over", 3), whoosh(.6), .2)
counter(W("over", 27), 1.2); put(sfx, W("over", 27), kick_s(int(.8 * SR)), .8); put(sfx, W("over", 27) + 1.2, tone(1318.5, .7, .3), .18)
put(sfx, W("rwt", 10), whoosh(.5), .3); put(sfx, W("rwt", 12) + .5, kick_s(), .7)
for k in np.arange(W("outro", 0), W("outro", 10) - .3, 1.1): put(sfx, k, kick_s(int(.4 * SR)), .45); put(sfx, k + .18, kick_s(int(.3 * SR)), .3)  # heartbeat
lt = W("outro", 10) - .3
for i, f in enumerate([523.3, 784, 1046.5]): put(sfx, lt + i * .08, tone(f, 2.0, .9), .12)

# ---------- mix + loudness
mix = voice * 1.0 + music * .55 + sfx * .8
mix = mix[: int(T * SR)]
mix /= np.abs(mix).max() * 1.05
st = np.stack([mix, mix], 1).astype(np.float32)
raw = HERE / "out/raw.wav"; raw.parent.mkdir(exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(raw)], input=st.tobytes(), check=True)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", af, "-ar", str(SR), str(HERE / "out/audio.wav")], check=True)
print("audio ->", HERE / "out/audio.wav", f"{T:.2f}s")
