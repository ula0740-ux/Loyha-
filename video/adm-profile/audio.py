"""Soundtrack: ElevenLabs narration on the timeline + the user's music (bar-line arrangement, ducked ~11 dB under the voice)
+ a few ElevenLabs SFX placed on picture cues (whips, reveals, panels, van drive-ins, logo). No synthesized audio.
Two-pass loudnorm to -16 LUFS integrated, true peak -1.5 dBTP. Writes out/audio.wav."""
import json, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
TL = json.loads((HERE / "audio/timeline.json").read_text())
SR, T = 48000, TL["total"]
N = int(T * SR) + SR
S = {s["id"]: s for s in TL["scenes"]}; L = TL["lines"]
W = lambda lid, i: L[lid]["words"][i]["t"]

def load(p, filt=None):
    a = ["ffmpeg", "-v", "quiet", "-i", str(p)] + (["-af", filt] if filt else []) + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(a, capture_output=True, check=True).stdout, np.float32).astype(np.float64)
def put(buf, t0, x, g=1.0):
    i = int(round(t0 * SR)); j = min(len(buf), i + len(x))
    if i < 0: x, i = x[-i:], 0
    if i < len(buf): buf[i:j] += g * x[: j - i]
def peak_at(x):  # SFX are placed by their measured peak, so the hit lands on the cue frame
    return int(np.argmax(np.abs(x))) / SR

voice = np.zeros(N)
for lid, l in L.items(): put(voice, l["vo"], load(HERE / f"audio/t/{lid}.wav"))

# music (v3): the user's own track (src/music_user.m4a, decoded to out/music_user.wav), arranged on bar lines following the
# plan in timeline.json (no time-stretch): bars straight through to the climax under the cluster, section A repeated after
# it, the final accent on the outro flash. 0.3 s equal-power crossfades at the joins, fades at the very start/end.
track = load(HERE / "out/music_user.wav")
music = np.zeros(N); XF = int(.3 * SR)
for k, sg in enumerate(TL["music"]["segments"]):
    t0, d = sg["track"], sg["dur"]
    pad = max(0, -t0); a = int(max(0, t0) * SR); n = int((d - pad) * SR) + XF
    seg = np.concatenate([np.zeros(int(pad * SR)), track[a:a + n]])
    env = np.ones(len(seg))
    if k: env[:XF] = np.sin(np.linspace(0, np.pi / 2, XF))                 # fade in over the join
    if k < len(TL["music"]["segments"]) - 1: env[-XF:] = np.cos(np.linspace(0, np.pi / 2, XF))
    put(music, sg["film"] - (XF / SR if k else 0), seg * env)
t = np.arange(N) / SR
music *= np.clip(t / .8, 0, 1) * np.clip((T - t) / 2.5, 0, 1)
# ducking: voice activity at 100 Hz -> target -11 dB while speaking, attack 0.15 s / release 0.3 s (one-pole smoothing)
CR = 100; hop = SR // CR
va = np.abs(voice[: len(voice) // hop * hop]).reshape(-1, hop).max(1)
active = np.convolve(va > .02, np.ones(8), "same") > 0                       # bridge tiny gaps between words
# v4: look-ahead so the music is already down when a line starts (v3 ducked only after the first syllable, so the music
# and the panel SFX masked the opening words: "ADM Jizzakh", "Shtamplash sexi")
PRE = int(.3 * CR); active = np.concatenate([active[PRE:], np.zeros(PRE, bool)]) | active
g_target = np.where(active, 10 ** (-11 / 20), 1.0); g = np.ones_like(g_target)
for i in range(1, len(g)):
    tau = .15 if g_target[i] < g[i - 1] else .30
    g[i] = g[i - 1] + (g_target[i] - g[i - 1]) * (1 - np.exp(-1 / (CR * tau)))
duck = np.interp(np.arange(N), np.arange(len(g)) * hop, g)
music *= duck
sfx = np.zeros(N)
X = {k: load(HERE / f"audio/sfx/{k}.mp3") for k in ["whoosh", "impact", "tick", "pop", "rise", "chime", "car"]}
def hit(name, t0, g): put(sfx, t0 - peak_at(X[name]), X[name], g)
for sid in ["kpi", "seg", "goals"]: hit("whoosh", S[sid]["start"], .35)          # whip transitions
for sid in ["hist", "struct", "geo", "logi", "dost", "eco", "outro"]: hit("whoosh", S[sid]["start"], .16)
put(sfx, S["cluster"]["start"] - 1.9, X["rise"], .22); hit("impact", S["cluster"]["start"], .45)   # cluster reveal (flash)
hit("impact", S["rnd"]["start"], .25)
for lid in ["c_kia", "c_skd", "c_lok", "c_sht", "c_nev", "c_rd", "c_dost"]:
    b0 = L[lid]["vo"] - .45; hit("whoosh", b0 + .2, .14); hit("pop", b0 + .8, .25)           # fly-to + panel pop
hit("pop", W("c_skd", [w["text"] for w in L["c_skd"]["words"]].index(next(w["text"] for w in L["c_skd"]["words"] if w["text"].lower().startswith("zavod")))), .22)                                                      # "250 nafar xodim" badge
for i in range(4): hit("tick", S["struct"]["start"] + .8 + i * .45, .18)            # structure nodes
for i in range(7): hit("tick", S["goals"]["start"] + 1.25 + i * .4, .14)             # goal rows
put(sfx, S["dost"]["start"] + .2, X["car"], .22); put(sfx, S["dost"]["start"] + 1.4, X["car"], .16)   # vans drive in
hit("chime", TL["flash"], .2)                                           # white logo card

sfx *= 1 - (1 - duck) * (1 - 10 ** (-7 / 20)) / (1 - 10 ** (-11 / 20))   # v4: SFX dip ~7 dB under the voice too (same smooth envelope)
mix = voice * 1.0 + music * .42 + sfx * .7   # the user's track is mastered loud: -7.5 dB under the voice at full level
mix = mix[: int(T * SR)]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(HERE / "out/music_stem.wav")], input=(music[: int(T * SR)] * .42).astype(np.float32).tobytes(), check=True)   # QA stem
mix *= .9 / np.abs(mix).max()
st = np.stack([mix, mix], 1).astype(np.float32)
raw = HERE / "out/raw.wav"; raw.parent.mkdir(exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(raw)], input=st.tobytes(), check=True)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-2:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
af = (f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", af, "-ar", str(SR), str(HERE / "out/audio.wav")], check=True)
print("audio ->", HERE / "out/audio.wav", f"{T:.2f}s, music: user track, bar-line arrangement")
