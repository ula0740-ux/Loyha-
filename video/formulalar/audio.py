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
groove_on, groove_off = S["intro"]["start"], S["outro"]["start"]
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

def crackle(d):                                   # welding sizzle: sparse sharp noise crackles
    n = int(d * SR); x = np.zeros(n)
    for k in range(int(d * 90)):
        p = int(rng.random() * (n - 400)); x[p:p + 400] += rng.standard_normal(400) * np.exp(-np.arange(400) / 60) * rng.random()
    return np.diff(np.concatenate([[0], x])) * np.minimum(1, np.arange(n) / (.02 * SR))
def typing(t0, chars, cps):
    for k in range(min(chars, 60)): put(sfx, t0 + k / cps, tone(1800 + 300 * rng.random(), .02, .006), .06)
order = TL["order"]; prev = None
VIEW = {"hook": 0, "intro": 1, "tt1": 2, "tt2": 3, "tt3": 3, "up": 4, "att1": 5, "att2": 6, "jph1": 7, "jph2": 8, "jph3": 8, "over1": 9, "over2": 10, "ct": 11, "rwt": 12, "outro": 13}
for sid in order:                                 # camera pan along the laser
    if prev is not None and VIEW[sid] != VIEW[prev]: put(sfx, S[sid]["start"] - .45, whoosh(.9), .3); put(sfx, S[sid]["start"] - .4, tone(2400, .5, .3), .03)
    prev = sid
for sid in ["jph1", "ct"]:                        # green Enter flash
    tb = S[sid]["start"] + .15; put(sfx, tb - .1, kick_s(int(.6 * SR)), .8); put(sfx, tb, tone(1760, .2, .05), .2)
for sid in ["att1", "over2"]:                     # glitch tear
    tb = S[sid]["start"] + .15; put(sfx, tb - .25, rng.standard_normal(int(.5 * SR)) * np.sin(np.linspace(0, np.pi, int(.5 * SR))) * (rng.random(int(.5 * SR)) > .7), .12)
welds = [("hook", 0, .85), ("tt1", 5, .6), ("up", 3, .9), ("att1", 9, .8), ("jph1", 10, .7), ("over1", 4, .7), ("ct", 5, .55), ("rwt", 6, .6)]
for sid, i, d in welds: put(sfx, W(sid, i), crackle(d + .1), .5)
kins = [("hook", [2, 3]), ("tt1", [2, 3]), ("up", [1]), ("att1", [5, 6, 7]), ("jph1", [5, 6, 7]), ("over1", [2]), ("ct", [2, 3]), ("rwt", [2, 3, 4]), ("intro", [3, 4, 5])]
for sid, ix in kins:
    for i in ix: put(sfx, W(sid, i) - .05, kick_s(int(.35 * SR)), .45); put(sfx, W(sid, i) - .05, pop(500, 1200, .06), .15)
nums = [("tt3", 21), ("up", 24), ("att2", 23), ("jph1", 25), ("jph2", 21), ("jph3", 27), ("over2", 36), ("ct", 18)]
for sid, i in nums:
    for k in np.arange(0, 1.0, .06): put(sfx, W(sid, i) + k, tick(), .1)
    put(sfx, W(sid, i) + 1.0, tone(1318.5, .6, .25), .14); put(sfx, W(sid, i) - .05, kick_s(), .5)
types = [("intro", 6, 120, 3.5), ("tt1", 13, 110, 30), ("tt2", 1, 40, 40), ("tt3", 0, 25, 30), ("tt3", 15, 25, 30), ("up", 5, 70, 34), ("att1", 13, 120, 30), ("att2", 1, 25, 26), ("att2", 10, 14, 22), ("jph1", 16, 55, 30), ("jph2", 6, 14, 26), ("jph3", 11, 14, 26), ("over1", 7, 100, 30), ("over2", 1, 30, 26), ("over2", 11, 18, 24), ("over2", 26, 18, 24), ("ct", 8, 75, 30), ("rwt", 10, 75, 30)]
for sid, i, n, cps in types: typing(W(sid, i), n, cps if cps > 5 else 60)
put(sfx, W("rwt", 27), whoosh(.5), .3); put(sfx, W("rwt", 29) + .5, kick_s(), .6)
po = S["outro"]["start"] + .55
put(sfx, po, rng.standard_normal(int(.3 * SR)) * env(int(.3 * SR), .001, .08), .25)        # white flash
for wi in [0, 2, 5, 7, 9, 12]: put(sfx, max(po + .2, W("outro", wi)), pop(300, 900, .08), .3)  # ticks on the form
lt = W("outro", 22) - .2
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
