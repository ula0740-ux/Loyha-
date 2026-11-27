"""v6: rank ADM takes by how close their "ADM" sounds to the two takes the user approved by ear
(audio/variants7/ADM_JIZZAKH_2.mp3 0.10-0.60 s, ADM_ICHIDA_2.mp3 1.80-2.36 s; scribe word times).
MFCC (cepstral-mean/var normalised) + DTW, lower = closer. Between the two approved takes themselves: ~3.6.
usage: python3 -I build/adm_pick.py TAKES_DIR id1 id2 ...   (takes from build/adm_takes.mts; also scores the current audio/<id>.mp3)"""
import sys, json, glob, os
import numpy as np, librosa
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def cut(f, a, b):
    y, _ = librosa.load(f, sr=16000, offset=max(0, a - .03), duration=b - a + .06); return y
def feat(y):
    m = librosa.feature.mfcc(y=y, sr=16000, n_mfcc=20, n_fft=512, hop_length=160)[1:]
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
def d(a, b):
    D, wp = librosa.sequence.dtw(X=feat(a), Y=feat(b)); return float(D[-1, -1] / len(wp))
R = [cut(f'{HERE}/audio/variants7/ADM_JIZZAKH_2.mp3', .10, .60), cut(f'{HERE}/audio/variants7/ADM_ICHIDA_2.mp3', 1.80, 2.36)]
timing = json.load(open(f'{HERE}/audio/timing.json'))
res = {}
for lid in sys.argv[2:]:
    rows = []
    cands = [(f, json.load(open(f[:-4] + '.json'))) for f in sorted(glob.glob(f'{sys.argv[1]}/{lid}_*.mp3'))]
    cands.append((f'{HERE}/audio/{lid}.mp3', timing[lid]['words']))
    for f, ws in cands:
        w = next(x for x in ws if x['text'] in ('A-De-Em', 'ADM'))
        y = cut(f, w['start'], w['end'])
        sc = np.mean([d(y, r) for r in R]); rows.append((round(sc, 3), round(w['end'] - w['start'], 2), os.path.basename(f) if 'takes' in f else 'CURRENT'))
    rows.sort(); res[lid] = rows
    print(lid, rows)
json.dump(res, open(f'{sys.argv[1]}/pick.json', 'w'))
