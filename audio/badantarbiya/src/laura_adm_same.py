# Foydalanuvchi (2026-10-23): "Audio boshida ADM qanday aytilgan bo'lsa, aynan o'sha talaffuzni namuna qilib ol."
# f0 dagi "ADM Jizzax xodimlari" bo'lagi (Laura, aynan o'sha yozuv) f3 va f5 oxiriga qo'yiladi; kesish nuqtalari
# so'zlar orasidagi eng jim joyga (energiya minimumiga) suriladi. Natija: laura/lines/f3_full.wav, f5_full.wav
import json, subprocess, sys, numpy as np
SR = 44100; L = '/home/user/Loyha-/audio/badantarbiya/laura/lines/'; W = json.load(open(sys.argv[1]))
def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, np.float32).copy()
def quiet(x, a, b):
    """a..b oralig'idagi eng jim 10 ms nuqta"""
    h = int(.01 * SR); i0, i1 = int(a * SR), int(b * SR)
    e = [np.sqrt(np.mean(x[i:i + h] ** 2)) for i in range(i0, max(i0 + 1, i1 - h), h)]
    return (i0 + int(np.argmin(e)) * h + h // 2) / SR
def w(f, key): return next(v for v in W[f] if key in v[0])
def fade(x, fi=.008, fo=.03):
    a, b = int(fi * SR), int(fo * SR); x = x.copy(); x[:a] *= np.linspace(0, 1, a); x[-b:] *= np.linspace(1, 0, b); return x
def save(x, p): x.astype(np.float32).tofile('/tmp/x.f32'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '/tmp/x.f32', p], check=True)
f0 = load(L + 'f0.mp3'); al, adm, xo = w('f0', 'alaykum'), w('f0', 'ADM'), w('f0', 'xodimlari')
s0 = quiet(f0, al[2] - .05, adm[1] + .02); e0 = quiet(f0, xo[2], xo[2] + .35)
seg = fade(f0[int(s0 * SR):int(e0 * SR)]); print(f'f0 bo\'lagi: {s0:.2f}-{e0:.2f} ({e0 - s0:.2f} s)')
f3b = load(L + 'f3b.mp3'); b = w('f3b', 'shash'); a = w('f3b', 'ADM'); c3 = quiet(f3b, b[2] - .05, a[1] + .02)
f3a = load(L + 'f3a.mp3')
save(np.concatenate([f3a, np.zeros(int(.35 * SR), np.float32), fade(f3b[:int(c3 * SR)]), np.zeros(int(.06 * SR), np.float32), seg]), L + 'f3_full.wav')
f5 = load(L + 'f5.mp3'); o = w('f5', 'Olg'); a = w('f5', 'ADM'); c5 = quiet(f5, o[2] - .03, a[1] + .02)
save(np.concatenate([fade(f5[:int(c5 * SR)]), np.zeros(int(.06 * SR), np.float32), seg]), L + 'f5_full.wav')
print(f'f3: "Bo\'shashmaymiz," {c3:.2f} s gacha + bo\'lak; f5: "...Olg\'a," {c5:.2f} s gacha + bo\'lak')
