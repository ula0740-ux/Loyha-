"""v6: is the final consonant of "Jizzax" a throat fricative (x/kh) or a stop (q/k)?
Russian STT is biased here ("Джизак" is the city's Russian name), so measure it: after the last voiced frame of the word
(the vowel "a"), count the milliseconds of continuous aperiodic noise in 1-6 kHz (fricative x: long, ~80-200 ms) and
the milliseconds of silence right after the vowel (a stop k/q: closure gap, then a short burst).
usage: python3 -I build/x_meter.py file.mp3:start:end ...   (start/end = word times from the TTS alignment, seconds)"""
import sys
import numpy as np, librosa
def meter(f, a, b):
    y, sr = librosa.load(f, sr=16000, offset=max(0, a), duration=b - a + .30)
    hop = 80                                             # 5 ms
    f0, vf, vp = librosa.pyin(y, fmin=120, fmax=450, sr=sr, frame_length=640, hop_length=hop)
    S = np.abs(librosa.stft(y, n_fft=512, hop_length=hop)) ** 2
    fr = librosa.fft_frequencies(sr=sr, n_fft=512)
    hb = 10 * np.log10(S[(fr > 1500) & (fr < 6000)].sum(0) + 1e-10)
    n = min(len(vf), len(hb)); vf, hb = vf[:n], hb[:n]
    end_word = int((b - a) / .005)
    voiced = np.where(vf[: end_word + 20])[0]
    if not len(voiced): return None
    lv = voiced[-1]                                      # end of the vowel
    thr = hb.max() - 28
    gap = 0
    i = lv + 1
    while i < n and hb[i] < thr and gap < 60: gap += 1; i += 1
    fric = 0
    while i < n and hb[i] >= thr and not vf[i]: fric += 1; i += 1
    return gap * 5, fric * 5
for arg in sys.argv[1:]:
    f, a, b = arg.rsplit(':', 2); r = meter(f, float(a), float(b))
    print(f"{f.split('/')[-1]:28s} gap {r[0]:4d} ms  fricative {r[1]:4d} ms  -> {'x (fricative)' if r and r[1] >= 60 and r[0] < 30 else 'k/q-like'}" if r else f"{f}: no voicing")
