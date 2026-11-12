# Foydalanuvchi bergan qo'shiqdan fon musiqasi (2026-10-30): audio uzunligicha kesiladi, balandligi eski fon darajasiga
# (RMS) tushiriladi va sekin "gain-riding" bilan bir xil ushlab turiladi (pasayib-ko'tarilmasin), boshida 0.5 s ochilish, oxirida 3 s so'nish.
#   python3 bed_from_track.py TRACK.mp3 OUT.wav [DUR=297.04] [TARGET_DB=-17.5]
import sys, subprocess, numpy as np
SR = 44100; src, out = sys.argv[1], sys.argv[2]; dur = float(sys.argv[3]) if len(sys.argv) > 3 else 297.04; tgt = float(sys.argv[4]) if len(sys.argv) > 4 else -17.5
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-t', str(dur), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
m = x.mean(1); h = int(.1 * SR); n = len(m) // h
rms = np.array([np.sqrt(np.mean(m[i * h:(i + 1) * h] ** 2)) for i in range(n)]) + 1e-6
k = 30; env = np.sqrt(np.convolve(rms ** 2, np.ones(k) / k, 'same'))            # ~3 s oyna
g = np.clip(10 ** (tgt / 20) / env, 10 ** (-20 / 20), 10 ** (6 / 20))
g = np.convolve(np.pad(g, (15, 15), mode='edge'), np.ones(31) / 31, 'valid')[:n]     # yumshoq o'zgarish
gs = np.interp(np.arange(len(m)), np.arange(n) * h + h / 2, g)
y = x * gs[:, None]
fi, fo = int(.5 * SR), int(3 * SR); y[:fi] *= np.linspace(0, 1, fi)[:, None]; y[-fo:] *= np.linspace(1, 0, fo)[:, None]
np.clip(y, -1, 1).astype(np.float32).tofile(out + '.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', out + '.f32', out], check=True)
subprocess.run(['rm', '-f', out + '.f32'])
r = [20 * np.log10(np.sqrt(np.mean(y[i:i + 10 * SR].mean(1) ** 2)) + 1e-9) for i in range(0, len(y) - 10 * SR, 10 * SR)]
print('fon RMS (10 s):', ' '.join('%.0f' % v for v in r))
