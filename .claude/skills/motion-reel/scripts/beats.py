"""python beats.py song.wav > beats.json   (the animation reads this file)
beats -> state changes, downbeats -> big moments, hits -> SFX.
Uses librosa when installed; otherwise a numpy onset/autocorrelation fallback with ffmpeg decoding.
Never trust an auto grid blindly: check the real drop by band energy (motion-design/scripts/analyze_song.py)."""
import json, subprocess, sys
import numpy as np

path = sys.argv[1]
try:
    import librosa
    y, sr = librosa.load(path, sr=None, mono=True)
    tempo, frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
    beats = librosa.frames_to_time(frames, sr=sr).round(3).tolist()
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    peaks = librosa.util.peak_pick(onset, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
    hits = librosa.frames_to_time(peaks, sr=sr).round(3).tolist()
    bpm = float(np.atleast_1d(tempo)[0])
except ImportError:
    sr, hop = 22050, 256
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    y = np.frombuffer(raw, np.float32)
    n = len(y) // hop
    spec = np.abs(np.fft.rfft(y[:n * hop].reshape(n, hop) * np.hanning(hop), axis=1))
    onset = np.maximum(0, np.diff(np.log1p(spec), axis=0)).sum(1)
    onset = (onset - onset.mean()) / (onset.std() + 1e-9)
    fps = sr / hop
    g = np.exp(-0.5 * (np.arange(-8, 9) / 3) ** 2)
    env = np.convolve(onset, g / g.sum(), "same")  # smoothed envelope: fractional-lag AC stays stable
    # tempo = autocorrelation of the onset envelope, fractional lags, weighted by a log-normal prior around 120 BPM (as librosa does)
    bpms = np.arange(60, 200.01, 0.25)
    t_idx = np.arange(len(onset))
    def ac_at(lag):
        return np.dot(env, np.interp(t_idx + lag, t_idx, env, right=0)) / len(env)
    score = np.array([ac_at(fps * 60 / b) for b in bpms]) * np.exp(-0.5 * (np.log2(bpms / 120)) ** 2)
    period = 60 / bpms[score.argmax()]
    bpm = 60 / period
    grid = lambda ph: np.interp((ph + np.arange(int((n / fps - ph) / period)) * period) * fps, t_idx, env).sum()
    phase = max(np.arange(0, period, 0.005), key=grid)
    beats = [round(phase + i * period, 3) for i in range(int((n / fps - phase) / period))]
    pk = [i for i in range(6, len(onset) - 6) if onset[i] == onset[i - 6:i + 7].max() and onset[i] > 1.5]
    hits, last = [], -1e9
    for i in pk:
        if i - last >= 20: hits.append(round(i / fps, 3)); last = i
json.dump({"bpm": round(bpm, 2), "beats": beats, "downbeats": beats[::4], "hits": hits}, sys.stdout, indent=1)
