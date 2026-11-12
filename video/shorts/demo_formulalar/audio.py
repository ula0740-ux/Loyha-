"""Demo short uchun sintez saundtrek (litsenziyasiz, to'liq kod): drone, riser, boom, whoosh, kick, tick.
    python3 audio.py  ->  audio.wav (-14 LUFS)"""
import subprocess, numpy as np, wave
SR, T = 48000, 13.0
n = int(SR * T); t = np.arange(n) / SR; L = np.zeros(n); R = np.zeros(n)
rng = np.random.default_rng(7)
def env(t0, a, d):
    x = t - t0; e = np.where(x < 0, 0, np.where(x < a, x / max(a, 1e-4), np.exp(-(x - a) / d))); return e
def add(sig, pan=0.0, g=1.0):
    global L, R
    L += sig * g * (1 - max(0, pan)); R += sig * g * (1 + min(0, pan))
def lp(x, k):  # oddiy bir qutbli past chastota filtri
    y = np.zeros_like(x); a = 0.0
    for i in range(0, len(x)):
        a += k * (x[i] - a); y[i] = a
    return y
# drone: 55 Hz + kvinta, sekin ko'tarilish va oxirida so'nish
sw = np.clip(t / 2.0, 0, 1) * np.clip((T - t) / 1.5, 0, 1)
dr = (np.sin(2 * np.pi * 55 * t) + .6 * np.sin(2 * np.pi * 82.4 * t + .3) + .3 * np.sin(2 * np.pi * 110 * t * (1 + .002 * np.sin(t)))) * sw
add(dr, g=.18)
# riser 0.1 -> 1.6: shovqin, chastota ko'tariladi
noise = rng.standard_normal(n)
rise = np.clip((t - .1) / 1.5, 0, 1) ** 2 * (t < 1.62)
hp = noise - lp(noise, .02)
add(hp * rise * .35, g=1)
add(np.sin(2 * np.pi * (200 + 900 * np.clip((t - .1) / 1.5, 0, 1) ** 2) * t) * rise * .08)
# boom (zarba): pastga sirpanuvchi sinus + klik
def boom(t0, g=1.0):
    x = np.maximum(t - t0, 0); f = 35 + 70 * np.exp(-x * 9)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env(t0, .004, .45) + .5 * hp * env(t0, .001, .03)
    add(s * g)
for h in [1.6, 4.2, 6.8, 9.4]: boom(h, .9)
boom(11.2, 1.0)
# whoosh: tarmoqli shovqin, o'rtada cho'qqi
def whoosh(tc, d=.42, g=.5, pan=0):
    x = (t - (tc - d / 2)) / d; e = np.where((x > 0) & (x < 1), np.sin(np.pi * np.clip(x, 0, 1)) ** 2, 0)
    band = lp(noise * e, .25) - lp(noise * e, .03)
    add(band * g, pan=pan)
for w in [4.2, 6.8]: whoosh(w, .45, 1.6, .3)
whoosh(9.35, .3, 1.2, -.3)
# kick 120 BPM (1.6 -> 11.0), C slow-mo (7.8-8.6) da sukut
for k in np.arange(1.6, 11.0, .5):
    if 7.75 < k < 8.65: continue
    x = np.maximum(t - k, 0); f = 45 + 90 * np.exp(-x * 30)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(k, .002, .12), g=.45)
# hi-hat oraliqda
for k in np.arange(1.85, 11.0, .5):
    if 7.75 < k < 8.65: continue
    add(hp * env(k, .001, .025), g=.08, pan=.2)
# dekoder tiklari (intro va final)
for k in np.arange(.2, 1.3, 1 / 14): add(np.sin(2 * np.pi * 2400 * t) * env(k, .0005, .012), g=.05)
for k in np.arange(11.45, 12.2, 1 / 18): add(np.sin(2 * np.pi * 2800 * t) * env(k, .0005, .01), g=.04)
# final: teskari reverb hissi (ko'tariluvchi shovqin) va chuqur sub
add(hp * np.clip((t - 10.6) / .6, 0, 1) ** 3 * (t < 11.2) * .25)
add(np.sin(2 * np.pi * 41 * t) * env(11.2, .01, 1.4), g=.5)
st = np.stack([L, R], 1); st /= np.max(np.abs(st)) + 1e-9; st *= .9
fade = np.clip((T - t) / .4, 0, 1)[:, None]; st *= fade
with wave.open('raw.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', 'audio.wav'], check=True)
print('audio.wav ok')
