"""Soundtrack: ElevenLabs narration on the timeline + ElevenLabs Music bed (time-fitted, ducked ~10 dB under the voice)
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

# music: fitted to the film length with atempo (pitch kept), fade in/out
md = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(HERE / "audio/music.mp3")], capture_output=True, text=True).stdout)
tempo = md / (T + .5)
music = np.zeros(N); put(music, 0, load(HERE / "audio/music.mp3", f"atempo={tempo:.5f}"))
t = np.arange(N) / SR
music *= np.clip(t / 2.0, 0, 1) * np.clip((T - t) / 3.0, 0, 1)
env = np.convolve(np.abs(voice), np.ones(int(.2 * SR)) / int(.2 * SR), "same")
duck = 1 - .68 * np.clip(env / (np.percentile(env[env > 1e-4], 60) + 1e-9), 0, 1)       # ~ -10 dB while speaking
duck = np.convolve(duck, np.ones(int(.25 * SR)) / int(.25 * SR), "same")
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
hit("pop", W("c_skd", 17), .22)                                                      # "250 nafar xodim" badge
for i in range(4): hit("tick", S["struct"]["start"] + .8 + i * .45, .18)            # structure nodes
for i in range(7): hit("tick", S["goals"]["start"] + .6 + i * .45, .14)             # goal rows
put(sfx, S["dost"]["start"] + .2, X["car"], .22); put(sfx, S["dost"]["start"] + 1.4, X["car"], .16)   # vans drive in
hit("chime", L["outro"]["end"] + .55, .35)                                           # white logo card

mix = voice * 1.0 + music * .32 + sfx * .9
mix = mix[: int(T * SR)]
mix *= .9 / np.abs(mix).max()
st = np.stack([mix, mix], 1).astype(np.float32)
raw = HERE / "out/raw.wav"; raw.parent.mkdir(exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(raw)], input=st.tobytes(), check=True)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", af, "-ar", str(SR), str(HERE / "out/audio.wav")], check=True)
print("audio ->", HERE / "out/audio.wav", f"{T:.2f}s, music tempo x{tempo:.4f}")
