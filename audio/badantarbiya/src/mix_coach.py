# Murabbiy versiyasi (2026-10-23): quvnoq, energiyali gaplar + mashq takrorlariga mos "Bir! Ikki! Uch! To'rt!" sanog'i.
# Sanoq so'zlari videodagi takror boshlanishiga (zarbga) qo'yiladi; har to'plam boshqa yozuvdan — ohang bir xil bo'lib qolmaydi.
# Yo'nalish almashadigan mashqlarda 4 martadan keyin ishora ("Endi esa chap tomonga!" va h.k.).
#   python3 mix_coach.py MUSIQA.wav OUT.wav   (ishchi papka: vaqtinchalik fayllar uchun)
import json, os, sys, subprocess, numpy as np
SR = 44100; M = '/home/user/Loyha-/audio/badantarbiya/murabbiy/'
MAN = json.load(open(M + 'manifest.json'))
# gaplar boshlanishi: asl vaqtlar; m2 va f3 sanoq to'plamidan keyinga surildi
LINES = [(1.0, 'f0'), (23.5, 'm0'), (24.94, 'm1'), (51.62, 'f1'), (79.05, 'm2'), (81.88, 'm3'), (111.16, 'f2'),
         (141.66, 'm4'), (148.61, 'm5'), (168.5, 'f3'), (198.10, 'm6'), (226.0, 'm7'), (253.46, 'f4'), (279.78, 'f5')]
# mashq: (videodagi boshlanish, takror davri s, to'plamlar soni, 4 martadan keyingi ishora)
EX = [(16.25, 2.0, 1, None), (34.25, 1.0, 4, None), (62.75, 2.0, 2, 'chapga'), (94.25, 2.0, 2, 'orqaga'),
      (123.75, 2.0, 2, 'tashqariga'), (153.25, 2.0, 2, 'chapga'), (176.25, 2.0, 2, None), (210.75, 2.0, 2, 'tashqariga'),
      (233.25, 2.0, 2, 'chapga'), (265.25, 1.0, 3, None)]
def load(p, ch=1, af='anull'):
    a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-af', af, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True).stdout, np.float32).reshape(-1, ch).copy()
    return a[:, 0] if ch == 1 else a
def lufs(x):
    x.astype(np.float32).tofile('t.f32')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 't.f32', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float([l for l in r.splitlines() if l.strip().startswith('I:')][-1].split()[1])
TRIM = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,'
TONE = 'highpass=f=90,highshelf=f=4000:g=-2.5,acompressor=threshold=-24dB:ratio=2.5:attack=6:release=120'
music = load(sys.argv[1], 2) * 10 ** (-4 / 20); T = len(music); vo = np.zeros(T, np.float32); busy = []
for at, fid in LINES:
    a = load(M + 'lines/' + fid + '.mp3', 1, TRIM + TONE); a = a * 10 ** ((-16.5 - lufs(a)) / 20)
    st = max(at, busy[-1][1] + .6 if busy else 0); i = int(st * SR); e = min(T, i + len(a)); vo[i:e] += a[:e - i]
    busy.append((st, st + len(a) / SR)); print(f'{fid} {st:.2f}-{busy[-1][1]:.2f}')
def free(t0, t1): return all(t1 < s - .15 or t0 > e + .2 for s, e in busy[:len(LINES)])   # sanoq faqat gaplar bilan solishtiriladi
# sanoq so'zlari: har yozuvdan 4 ta so'z, ovoz balandligi gaplarga moslanadi
takes = []
for c in MAN['counts']:
    a = load(M + c['file'], 1, TONE); ws = []
    for w in c['words']:
        s0, s1 = int(max(0, w['start'] - .05) * SR), int(min(len(a) / SR, w['end'] + .16) * SR)
        x = a[s0:s1].copy(); f = int(.03 * SR); x[-f:] *= np.linspace(1, 0, f); x[:int(.005 * SR)] *= np.linspace(0, 1, int(.005 * SR))
        ws.append((x, w['start'] - s0 / SR))
    takes.append(ws)
ref = np.sqrt(np.mean(np.concatenate([w for t in takes for w, _ in t]) ** 2)); g = 10 ** ((-16.5 - lufs(np.concatenate([w for t in takes for w, _ in t]))) / 20) * 1.12
# ishoralar sal tezroq (atempo 1.12) — to'plamlar orasidagi 1.5 s ga sig'sin; 'chapga' allaqachon kesilgan, qayta trim qilinmaydi
cues = {k: load(M + v['file'], 1, ('' if k == 'chapga' else TRIM) + 'atempo=1.12,' + TONE) for k, v in MAN['cues'].items()}
for k in cues: cues[k] = cues[k] * 10 ** ((-16.5 - lufs(cues[k])) / 20)
def put(x, t):
    i = int(t * SR); e = min(T, i + len(x)); vo[i:e] += x[:e - i]
n = 0; log = []; plan = []
# har mashq: birinchi bo'sh takrordan boshlab to'plamlar ketma-ket; gap bilan to'qnashsa bitta takrorga suriladi
for q, (t0, per, sets, cue) in enumerate(EX):
    lim = EX[q + 1][0] if q + 1 < len(EX) else T / SR
    fits = lambda st, tk: all(free(t - .06, t + len(tk[j][0]) / SR) and t < lim for j, t in enumerate([st + j * per for j in range(4)]))
    k = 0
    while k < 12 and not fits(t0 + k * per, takes[n % len(takes)]): k += 1
    st = t0 + k * per; done = 0
    if k: log.append(f'  {t0:.2f}: gap tugashini kutib {k} takrorga surildi')
    while done < sets:
        tk = takes[n % len(takes)]; times = [st + j * per for j in range(4)]
        if not fits(st, tk): log.append(f'  {st:.2f}: to\'plam sig\'madi'); break
        n += 1
        for j, t in enumerate(times):
            w, on = tk[j]; put(w * g * (1.15 if j == 3 else 1), t - on - .02); 
        log.append(f'  sanoq {times[0]:.2f}..{times[3]:.2f}'); plan.append({'start': round(times[0], 2), 'per': per, 'set': done})
        if cue and done == 0 and sets > 1:
            nb = st + 4 * per; cs = nb - .18 - len(cues[cue]) / SR
            if cs > times[3] + .5 and free(cs, cs + len(cues[cue]) / SR): put(cues[cue], cs); log.append(f'  ishora {cue} {cs:.2f}')
            else: log.append(f'  ishora {cue} sig\'madi')
        st += 4 * per; done += 1
json.dump({'lines': [[f, round(a, 2), round(b2, 2)] for (f, _), (a, b2) in zip(LINES, busy[:len(LINES)])], 'counts': plan}, open(M + 'timeline.json', 'w'))
print('\n'.join(log))
vo.astype(np.float32).tofile('v.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'v.f32', '-af', 'aecho=0.9:0.6:35|60:0.08|0.05', 'v_coach.wav'], check=True)
vo = load('v_coach.wav')[:T]; vo = np.pad(vo, (0, T - len(vo)))
act = (np.convolve(np.abs(vo), np.ones(2205) / 2205, 'same') > 0.003).astype(np.float32)
env = np.clip(np.convolve(act, np.ones(int(.35 * SR)) / int(.35 * SR), 'same') * 1.5, 0, 1)
fade = np.ones(T, np.float32); fe = int((T / SR - 1.0) * SR); fade[fe:] = np.linspace(1, 0, T - fe)
out = music * ((1 - env * (1 - 10 ** (-9 / 20))) * fade)[:, None] + vo[:, None]
ap = load('applause.mp3', 2); i = int((busy[13][1] + .3) * SR) if False else int((max(e for s, e in busy) + .3) * SR); e = min(T, i + len(ap)); out[i:e] += ap[:e - i] * .45
np.clip(out, -1, 1).astype(np.float32).tofile('mix.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'mix.f32', sys.argv[2]], check=True)
for f in ('mix.f32', 'v.f32', 't.f32'): os.remove(f)
