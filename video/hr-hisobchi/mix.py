# Diktor qatorlarini sahna vaqtlariga qo'yadi, asl musiqani ovoz ostida -9 dB pasaytiradi -> mix.wav
#   python3 mix.py VIDEO.mp4   (trim/*.wav — jimjitligi kesilgan ovozlar)
import sys, subprocess, numpy as np
V = sys.argv[1]; SR = 48000; N = int(41.0 * SR)
def load(path, ch, af='anull'):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-af', af, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch)
orig = load(V, 2)[:N]; orig = np.pad(orig, ((0, N - len(orig)), (0, 0)))
# id: (boshlanish s, tempo) — tempo > 1 faqat sahnaga sig'masa
PLAN = {'s1': (0.25, 1.08), 's2': (4.25, 1), 's3': (8.4, 1), 's4': (11.3, 1), 's5': (15.2, 1.06),
        's6': (21.4, 1), 's7': (26.1, 1), 's8': (30.2, 1), 's9': (34.2, 1), 's10': (37.35, 1.15)}
voice = np.zeros(N, np.float32)
for k, (at, tempo) in PLAN.items():
    a = load(f'trim/{k}.wav', 1, f'atempo={tempo}' if tempo != 1 else 'anull')[:, 0]
    i = int(at * SR); e = min(N, i + len(a))
    voice[i:e] += a[:e - i]; print(k, '%.2f-%.2f' % (at, at + len(a) / SR), 'OVER' if i + len(a) > N else '')
act = (np.convolve(np.abs(voice), np.ones(2400) / 2400, 'same') > 0.004).astype(np.float32)
env = np.clip(np.convolve(act, np.ones(int(.25 * SR)) / int(.25 * SR), 'same') * 1.6, 0, 1)
mix = np.clip(orig * (1 - env * (1 - 10 ** (-9 / 20)))[:, None] + voice[:, None], -1, 1).astype(np.float32)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', 'mix.wav'], input=mix.tobytes(), check=True)
