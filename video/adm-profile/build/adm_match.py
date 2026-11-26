"""v4: which TTS candidate says "ADM Jizzakh" most like the user's reference video?
Cuts the reference's spoken "ADM Jizzakh" (STT word times: 10.64-11.34, 105.00-105.76, 152.42-153.60 s), trims
silence, and compares each candidate span (audio/variants6/*_span.wav) by DTW over cepstral-mean-normalised MFCCs
(speaker/channel differences mostly cancel; lower = closer). Also compares the first 45 % of the span ("ADM" alone).
usage: python3 -I build/adm_match.py ref16.wav (audio of src/user_ref_adm.mp4) audio/variants6"""
import sys, glob, os, json
import numpy as np, librosa

ref, vdir = sys.argv[1], sys.argv[2]
SPANS = [(10.60, 11.38), (104.96, 105.80), (152.38, 153.64)]
def feat(y, sr=16000):
    y, _ = librosa.effects.trim(y, top_db=30)
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20, n_fft=512, hop_length=160)[1:]
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6), len(y) / sr
def dtw(a, b):
    D, wp = librosa.sequence.dtw(X=a, Y=b, metric='euclidean')
    return float(D[-1, -1] / len(wp))
R = []
for a, b in SPANS:
    y, _ = librosa.load(ref, sr=16000, offset=a, duration=b - a)
    R.append(feat(y))
print('reference spans (s):', [round(d, 2) for _, d in R])
rows = []
for f in sorted(glob.glob(os.path.join(vdir, '*_span.wav'))):
    y, _ = librosa.load(f, sr=16000)
    F, d = feat(y)
    full = np.mean([dtw(F, r) for r, _ in R])
    head = np.mean([dtw(F[:, :int(F.shape[1] * .45)], r[:, :int(r.shape[1] * .45)]) for r, _ in R])
    rows.append((os.path.basename(f).replace('_span.wav', ''), round(d, 2), round(full, 3), round(head, 3)))
for r in sorted(rows, key=lambda r: r[2] + r[3]):
    print(f'{r[0]:10s} dur {r[1]:5.2f}s  DTW full {r[2]:.3f}  ADM-part {r[3]:.3f}')
json.dump(rows, open(os.path.join(vdir, 'match.json'), 'w'), indent=1)
