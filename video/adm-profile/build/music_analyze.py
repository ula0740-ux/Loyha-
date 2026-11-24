"""Beat / bar / energy analysis of the user track (out/music_user.wav, decoded from src/music_user.m4a) -> audio/music_grid.json."""
import json, sys
from pathlib import Path
import numpy as np, librosa
HERE = Path(__file__).resolve().parents[1]
y, sr = librosa.load(str(HERE / 'out/music_user.wav'), sr=22050, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
tempo = float(np.atleast_1d(tempo)[0])
onset = librosa.onset.onset_strength(y=y, sr=sr)
# downbeat phase: the phase (0-3) whose beats carry the most onset energy + low-frequency energy
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512)); low = S[:20].sum(0)
bt = librosa.time_to_frames(beats, sr=sr, hop_length=512); bt = bt[bt < len(low)]
score = [float(np.mean(low[bt[p::4]]) + 50 * np.mean(onset[np.minimum(bt[p::4], len(onset) - 1)])) for p in range(4)]
ph = int(np.argmax(score)); bars = beats[ph::4]
rms = librosa.feature.rms(y=y, hop_length=512)[0]; tt = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
bar_energy = [float(np.mean(rms[(tt >= a) & (tt < b)])) for a, b in zip(bars[:-1], bars[1:])]
out = {'tempo': tempo, 'beats': [round(float(b), 3) for b in beats], 'bars': [round(float(b), 3) for b in bars], 'bar_energy': [round(e, 5) for e in bar_energy], 'duration': len(y) / sr, 'phase_scores': score}
(HERE / 'audio/music_grid.json').write_text(json.dumps(out, indent=1))
print(f'tempo {tempo:.2f}  beats {len(beats)}  bars {len(bars)}  phase {ph} {np.round(score,3)}')
e = np.array(bar_energy); mx = e.max()
for i in range(0, len(bars) - 1):
    print(f'{i:3d} {bars[i]:7.2f} ' + '#' * int(40 * e[i] / mx))
