"""v7 prep: rank "Jizzakh" takes by closeness to the approved "Jizzakh!" of video/pptx-film (ADM_HR_2026_v5, intro 0.96-1.80 s,
outro 4.04-4.88 s). MFCC (cepstral mean/var normalised) + DTW on the cut word, lower = closer. Also writes the cut words
(<id>_<k>_jz.mp3) for the ru STT check.
usage: python3 -I build/jz_pick.py TAKES_DIR B I T   (group "title": the whole "A-de-em, Jizzakh!" phrase vs the reference phrase 0.0-1.80 s)"""
import sys, json, glob, os, subprocess
import numpy as np, librosa
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PF = os.path.join(HERE, '..', 'pptx-film', 'audio')
def load(f, a, b):
    y, _ = librosa.load(f, sr=16000, offset=max(0, a - .03), duration=b - a + .13); y, _ = librosa.effects.trim(y, top_db=35); return y
def feat(y):
    m = librosa.feature.mfcc(y=y, sr=16000, n_mfcc=20, n_fft=512, hop_length=160)[1:]
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
def d(a, b):
    D, wp = librosa.sequence.dtw(X=feat(a), Y=feat(b)); return float(D[-1, -1] / len(wp))
R = [load(f'{PF}/intro.mp3', .96, 1.80), load(f'{PF}/outro.mp3', 4.04, 4.88)]
RP = [load(f'{PF}/intro.mp3', 0.0, 1.80)]
print('approved ref vs ref:', round(d(R[0], R[1]), 3))
out = {}
for g in sys.argv[2:]:
    rows = []
    for f in sorted(glob.glob(f'{sys.argv[1]}/{g}_[0-9].mp3')):
        ws = json.load(open(f[:-4] + '.json'))['words']; w = next(x for x in ws if x['text'].lower().startswith('jizz'))
        if g == 'title': y = load(f, ws[0]['start'], w['end']); sc = float(np.mean([d(y, r) for r in RP]))
        else: y = load(f, w['start'], w['end']); sc = float(np.mean([d(y, r) for r in R]))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(max(0, w['start'] - .04)), '-to', str(w['end'] + .15), '-i', f, f[:-4] + '_jz.mp3'], check=True)
        rows.append([round(sc, 3), os.path.basename(f), round(w['end'] - w['start'], 2)])
    rows.sort(); out[g] = rows; print(g, rows)
json.dump(out, open(f'{sys.argv[1]}/jz_pick.json', 'w'))
