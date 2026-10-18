#!/usr/bin/env python3
"""Namuna (reference) videoni tahlil qilish: uslubni o'rganish uchun.
    python3 analyze_ref.py VIDEO OUT_DIR [--thresh 0.32]
Chiqadi: OUT_DIR/ref.json (o'lcham, fps, davomiylik, kesishlar, o'rtacha shot uzunligi, palitra, ovoz balandligi)
         OUT_DIR/shots.png  (har bir shotning o'rtasidan 1 kadr)
         OUT_DIR/grid.png   (bir tekis 16 kadr)
Ko'rib chiqing (Read) va uslubni yozing: kompozitsiya, kamera harakati, o'tishlar, shrift, ranglar, ritm.
Faqat texnikani olamiz — boshqa birovning kadrlari, qahramonlari, logolari ko'chirilmaydi."""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image

def run(a): return subprocess.run(a, capture_output=True, text=True)

def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    th = float(sys.argv[sys.argv.index('--thresh') + 1]) if '--thresh' in sys.argv else 0.32
    pr = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(src)]).stdout)
    v = next(s for s in pr['streams'] if s['codec_type'] == 'video')
    num, den = map(int, v['r_frame_rate'].split('/')); fps = num / den
    dur = float(pr['format']['duration']); W, H = int(v['width']), int(v['height'])
    # sahna kesishlari
    r = run(['ffmpeg', '-hide_banner', '-i', str(src), '-vf', f"select='gt(scene,{th})',showinfo", '-an', '-f', 'null', '-'])
    cuts = [round(float(m), 3) for m in re.findall(r'pts_time:([0-9.]+)', r.stderr)]
    edges = [0.0] + cuts + [dur]
    shots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1) if edges[i + 1] - edges[i] > 0.05]
    lens = [b - a for a, b in shots]
    # kadrlar
    tmp = out / '_f'; tmp.mkdir(exist_ok=True)
    def grab(t, p): run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', str(src), '-frames:v', '1', '-vf', 'scale=360:-2', str(p)])
    mids = [(a + b) / 2 for a, b in shots][:40]
    for i, t in enumerate(mids): grab(t, tmp / f's_{i:03d}.png')
    for i in range(16): grab(dur * (i + .5) / 16, tmp / f'g_{i:03d}.png')
    def tile(prefix, n, name, cols):
        ims = [Image.open(tmp / f'{prefix}_{i:03d}.png').convert('RGB') for i in range(n) if (tmp / f'{prefix}_{i:03d}.png').exists()]
        if not ims: return
        w, h = ims[0].size; rows = -(-len(ims) // cols)
        sheet = Image.new('RGB', (cols * (w + 6), rows * (h + 6)), 'white')
        for k, im in enumerate(ims): sheet.paste(im.resize((w, h)), ((k % cols) * (w + 6), (k // cols) * (h + 6)))
        sheet.save(out / name)
    tile('s', len(mids), 'shots.png', 6 if H < W else 8)
    tile('g', 16, 'grid.png', 4 if H < W else 8)
    # palitra (grid kadrlaridan)
    allpx = Image.new('RGB', (360 * 4, 360 * 4))
    for i in range(16):
        p = tmp / f'g_{i:03d}.png'
        if p.exists(): allpx.paste(Image.open(p).convert('RGB').resize((360, 360)), ((i % 4) * 360, (i // 4) * 360))
    q = allpx.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:24]; counts = sorted(q.getcolors(), reverse=True)
    palette = ['#%02x%02x%02x' % tuple(pal[c * 3:c * 3 + 3]) for _, c in counts]
    # ovoz
    loud = None
    if any(s['codec_type'] == 'audio' for s in pr['streams']):
        lr = run(['ffmpeg', '-hide_banner', '-i', str(src), '-af', 'ebur128', '-f', 'null', '-'])
        m = re.findall(r'I:\s+(-?[0-9.]+) LUFS', lr.stderr); loud = float(m[-1]) if m else None
    rep = dict(file=str(src), width=W, height=H, aspect=f'{W}:{H}', vertical=H > W, fps=round(fps, 3), duration=round(dur, 3),
               shots=len(shots), cuts=cuts, avg_shot=round(sum(lens) / len(lens), 3), min_shot=round(min(lens), 3),
               cuts_per_sec=round(len(cuts) / dur, 3), palette=palette, loudness_lufs=loud)
    (out / 'ref.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    for p in tmp.iterdir(): p.unlink()
    tmp.rmdir()
    print(json.dumps({k: rep[k] for k in rep if k != 'cuts'}, ensure_ascii=False))

if __name__ == '__main__': main()
