# Laura versiyasi (2026-10-23): foydalanuvchi tanlagan 3-shablon ovozi, sanoq faqat 2 mashqda (yugurish, bel).
# To'xtashlarni tuzatish: gaplar ichidagi 0.35 s dan uzun jimliklar 0.28 s gacha qisqartiriladi; sanoq so'zlari kesilmaydi —
# har so'z keyingisigacha bo'lgan bo'lagi bilan olinadi va atempo bilan aniq 0.6 s ga moslanadi (foydalanuvchi namunasi ritmi).
#   python3 mix_laura.py shablon|toliq MUSIQA.wav OUT.wav
import json, os, sys, subprocess, numpy as np
SR = 44100; M = '/home/user/Loyha-/audio/badantarbiya/laura/'; MAN = json.load(open(M + 'manifest.json'))
TONE = 'highpass=f=90,highshelf=f=4000:g=-2.5,acompressor=threshold=-24dB:ratio=2.5:attack=6:release=120'
TRIM = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,'
SPACE = .6
def load(p, ch=1, af='anull', ss=None, t=None):
    a = ['ffmpeg', '-v', 'error'] + (['-ss', str(ss)] if ss is not None else []) + (['-t', str(t)] if t else []) + ['-i', p, '-af', af, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-']
    x = np.frombuffer(subprocess.run(a, capture_output=True).stdout, np.float32).reshape(-1, ch).copy(); return x[:, 0] if ch == 1 else x
def lufs(x):
    x.astype(np.float32).tofile('t.f32')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 't.f32', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])
def tighten(x, maxgap=.35, keep=.28):
    """gap ichidagi uzun jimliklarni qisqartiradi (bir yozuv ichida, so'zlar o'rni o'zgarmaydi)"""
    h = int(.01 * SR); e = np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) for i in range(0, len(x) - h, h)]); q = e < 10 ** (-42 / 20) * max(e.max(), 1e-6) * 30
    out, i, n = [], 0, len(e)
    while i < n:
        j = i
        while j < n and q[j]: j += 1
        if j > i and (j - i) * .01 > maxgap and i > 0 and j < n:
            a, b = i * h, j * h; k = int(keep * SR); f = int(.02 * SR)
            seg = np.concatenate([x[a:a + k // 2], x[b - k // 2:b]]); seg[k // 2 - f:k // 2] *= np.linspace(1, 0, f); seg[k // 2:k // 2 + f] *= np.linspace(0, 1, f)
            out.append(seg); i = j; continue
        out.append(x[i * h:(max(j, i + 1)) * h]); i = max(j, i + 1)
    return np.concatenate(out + [x[n * h:]])
def stretch(x, dur):
    """bo'lakni atempo bilan aniq dur soniyaga keltiradi (0.5..2 oralig'ida)"""
    r = len(x) / SR / dur; x.astype(np.float32).tofile('s.f32')
    y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 's.f32', '-af', f'atempo={max(.5, min(2, r)):.4f}', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
    n = int(dur * SR); return np.pad(y, (0, max(0, n - len(y))))[:n]
def count_block(c):
    a = load(M + c['file'], 1, TONE); w = c['words']; parts = []
    for i in range(8):
        s, e = w[i]['start'] - .03, w[i + 1]['start'] - .03
        parts.append(stretch(a[int(s * SR):int(e * SR)].copy(), SPACE))
    tail = tighten(a[int((w[8]['start'] - .03) * SR):]); f = int(.01 * SR)
    for p in parts: p[:f] *= np.linspace(0, 1, f); p[-f:] *= np.linspace(1, 0, f)
    return np.concatenate(parts + [tail])
def line(fid): x = tighten(load(M + 'lines/' + fid + '.mp3', 1, TRIM + TONE)); return x * 10 ** ((-16.5 - lufs(x)) / 20)
mode, mus, outp = sys.argv[1:4]
cb = count_block(MAN['counts'][0]); cb = cb * 10 ** ((-16.5 - lufs(cb)) / 20)
if mode == 'shablon':
    g = load('/tmp/claude-0/-home-user-Loyha-/c834dc26-1eb9-51ce-89e6-3a681ac8c16d/scratchpad/tpl3/laura_salom.mp3', 1, TRIM + TONE); g = tighten(g); g = g * 10 ** ((-16.5 - lufs(g)) / 20)
    v = np.concatenate([np.zeros(int(.5 * SR), np.float32), g, np.zeros(int(.35 * SR), np.float32), cb]); T = len(v) + int(1.2 * SR)
    music = load(mus, 2, ss=35.75, t=T / SR) * 10 ** (-4 / 20); vo = np.pad(v, (0, T - len(v)))[:len(music)]; T = len(vo)
else:
    music = load(mus, 2) * 10 ** (-4 / 20); T = len(music); vo = np.zeros(T, np.float32); prev = 0; ends = {}
    LINES = [(1.0, 'f0'), (22.82, 'm0'), (24.94, 'm1'), (51.62, 'f1'), (76.20, 'm2'), (81.88, 'm3'), (111.16, 'f2'),
             (141.66, 'm4'), (148.61, 'm5'), (166.62, 'f3'), (198.10, 'm6'), (225.70, 'm7'), (253.46, 'f4'), (279.78, 'f5')]
    for at, fid in LINES:
        a = line(fid); st = max(at, prev + .6); i = int(st * SR); vo[i:i + len(a)] += a[:T - i]; prev = st + len(a) / SR; ends[fid] = prev
        print(f'{fid} {st:.2f}-{prev:.2f}')
    # sanoq faqat 2 mashqda: joyida yugurish (m1 dan keyin) va bel aylantirish (m5 dan keyin) — keyingi zarbdan
    for after, nxt in (('m1', 51.62), ('m5', 166.62)):
        st = B0 = .25 + .5 * np.ceil((ends[after] + .35 - .25) / .5); i = int(st * SR); vo[i:i + len(cb)] += cb
        print(f'sanoq {st:.2f}-{st + len(cb) / SR:.2f} (keyingi gap {nxt})')
vo.astype(np.float32).tofile('v.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'v.f32', '-af', 'aecho=0.9:0.6:35|60:0.08|0.05', 'v_l.wav'], check=True)
vo = load('v_l.wav')[:T]; vo = np.pad(vo, (0, T - len(vo)))
act = (np.convolve(np.abs(vo), np.ones(2205) / 2205, 'same') > 0.003).astype(np.float32)
env = np.clip(np.convolve(act, np.ones(int(.35 * SR)) / int(.35 * SR), 'same') * 1.5, 0, 1)
fade = np.ones(T, np.float32); fe = int((T / SR - 1.0) * SR); fade[fe:] = np.linspace(1, 0, T - fe)
out = music[:T] * ((1 - env * (1 - 10 ** (-9 / 20))) * fade)[:, None] + vo[:, None]
if mode != 'shablon':
    ap = load('applause.mp3', 2); i = int((ends['f5'] + .3) * SR); e = min(T, i + len(ap)); out[i:e] += ap[:e - i] * .45
np.clip(out, -1, 1).astype(np.float32).tofile('mix.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'mix.f32', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-b:a', '192k', outp], check=True)
for f in ('mix.f32', 'v.f32', 't.f32', 's.f32'):
    if os.path.exists(f): os.remove(f)
