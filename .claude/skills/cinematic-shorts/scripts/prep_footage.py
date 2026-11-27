#!/usr/bin/env python3
"""Foydalanuvchi videosini seek(t) dvigatelida ishlatish uchun tayyorlash.
    python3 prep_footage.py VIDEO OUT_DIR [--ss 0] [--to END] [--fps 30] [--w 1080 --h 1920]
                            [--mode fill|crop|fit] [--x 0.5] [--q 3]
mode: crop = 9:16 ga markazdan kesish (--x 0..1 gorizontal fokus, odam/predmet qayerda bo'lsa);
      fill = kadr butun ko'rinadi, orqasi o'sha videoning xiralashgan kattalashtirilgani (Reels uslubi);
      fit  = qora maydon bilan.
Chiqadi: OUT_DIR/f_000001.jpg ... + OUT_DIR/audio.wav + OUT_DIR/meta.json {fps, n, dur, w, h}"""
import json, subprocess, sys
from pathlib import Path

def arg(k, d):
    return type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d

def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    ss, to, fps = arg('--ss', 0.0), arg('--to', -1.0), arg('--fps', 30)
    W, H, mode, fx, q = arg('--w', 1080), arg('--h', 1920), arg('--mode', 'fill'), arg('--x', 0.5), arg('--q', 3)
    if mode == 'crop':
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}:(in_w-{W})*{fx}:(in_h-{H})/2"
    elif mode == 'fit':
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black"
    else:
        vf = (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:2,eq=brightness=-0.12:saturation=1.15[bg];"
              f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
    vf = f"fps={fps}," + vf
    tt = ['-to', str(to)] if to > 0 else []
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), *tt, '-i', str(src), '-filter_complex', vf, '-q:v', str(q),
                    str(out / 'f_%06d.jpg')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), *tt, '-i', str(src), '-vn', '-ac', '2', '-ar', '48000',
                    str(out / 'audio.wav')], check=False)
    n = len(list(out.glob('f_*.jpg')))
    meta = dict(fps=fps, n=n, dur=round(n / fps, 3), w=W, h=H, mode=mode, src=str(src), ss=ss)
    (out / 'meta.json').write_text(json.dumps(meta, indent=1)); print(meta)

if __name__ == '__main__': main()
