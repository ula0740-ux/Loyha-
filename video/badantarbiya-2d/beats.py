# Musiqa (ovozsiz) dan beat grid: spektral flux → avtokorrelyatsiya (BPM) → faza → beats.js
import numpy as np, subprocess, json, sys
SR = 22050
src = sys.argv[1]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32)
hop, n = 256, 1024
fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
S = np.log1p(np.abs(np.fft.rfft(fr, axis=1)) * 10)
flux = np.maximum(0, np.diff(S, axis=0)).sum(1); flux = np.r_[0, flux]
flux = (flux - np.convolve(flux, np.ones(64) / 64, 'same')).clip(0)
fps = SR / hop
ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
lo, hi = int(fps * 60 / 185), int(fps * 60 / 105)
lag = lo + np.argmax(ac[lo:hi]); bpm = 60 * fps / lag
# aniq BPM: lag atrofida ingichka qidiruv
best = None
for b in np.arange(bpm - 1, bpm + 1, 0.005):
    per = 60 / b * fps
    for ph in np.linspace(0, per, 48, endpoint=False):
        idx = (ph + per * np.arange(int((len(flux) - ph) / per))).astype(int)
        s = flux[idx].sum()
        if not best or s > best[0]: best = (s, b, ph / fps)
_, bpm, off = best
dur = len(x) / SR
beats = list(np.round(np.arange(off, dur, 60 / bpm), 4))
# bar (4 zarb) boshini topish: qaysi fazada kuchliroq
per = 60 / bpm
strength = [sum(flux[int((off + per * (k + 4 * j)) * fps)] for j in range(int(len(beats) / 4) - 1)) for k in range(4)]
down = int(np.argmax(strength))
print(f'BPM {bpm:.2f} offset {off:.3f}s downbeat phase {down} dur {dur:.2f}s beats {len(beats)}')
open('beats.js', 'w').write(f'window.BEAT={{bpm:{bpm:.3f},off:{off:.4f},down:{down},dur:{dur:.3f}}};\n')
