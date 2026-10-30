#!/usr/bin/env python3
"""seek(t) HTML → MP4 (vertikal yoki istalgan o'lcham), kino motion blur bilan.
    python3 render_short.py HTML OUT.mp4 --dur 12 [--w 1080 --h 1920] [--fps 30] [--sub 4] [--shutter 0.5]
                            [--audio a.wav] [--root DIR] [--probe 0.5,2,4] [--chunk k/n] [--port 8790] [--cuts 1.2,3.4]
- HTML katalogi http orqali beriladi (img/footage nisbiy yo'llari ishlaydi).
- Sahifada window.seek(t) (async) va window.ready = true bo'lishi shart.
- --sub N: har kadrga N ta subkadr, shutter ulushiga yoyilib o'rtachalanadi (180° = 0.5) → tabiiy motion blur.
  --cuts: qattiq kesish vaqtlari, subkadrlar kesishdan o'tmaydi (ikki sahna ustma-ust tushmaydi).
- --probe: faqat shu vaqtlardagi kadrlarni OUT.mp4 o'rniga OUT_probe.png varaqqa chiqaradi (tekshiruv uchun).
- --chunk k/n: kadrlarning k-qismini (0..n-1) render qiladi → keyin concat (uzun filmlar uchun parallel)."""
import asyncio, functools, http.server, io, socketserver, subprocess, sys, threading
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright

def arg(k, d, cast=None):
    if k not in sys.argv: return d
    v = sys.argv[sys.argv.index(k) + 1]; return (cast or type(d))(v)

HTML = Path(sys.argv[1]).resolve(); OUT = Path(sys.argv[2]).resolve()
DUR = arg('--dur', 10.0); W = arg('--w', 1080); H = arg('--h', 1920); FPS = arg('--fps', 30)
SUB = arg('--sub', 4); SHUT = arg('--shutter', 0.5); AUD = arg('--audio', '', str); PORT = arg('--port', 8790)
PROBE = [float(x) for x in arg('--probe', '', str).split(',') if x]
CUTS = [float(x) for x in arg('--cuts', '', str).split(',') if x]
CH = arg('--chunk', '', str)
ROOT = Path(arg('--root', str(HTML.parent), str)).resolve()  # served directory (e.g. repo root, so ../../assets/fonts works)
CHROME = '/opt/pw-browsers/chromium'
ARGS = ['--autoplay-policy=no-user-gesture-required', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']

def serve():
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Q, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), h)
    threading.Thread(target=s.serve_forever, daemon=True).start(); return s

async def page(p):
    b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
    pg = await b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    await pg.goto(f'http://127.0.0.1:{PORT}/{HTML.relative_to(ROOT).as_posix()}')
    await pg.wait_for_function('window.ready === true', timeout=180000)
    await pg.evaluate('document.fonts.ready')
    await pg.add_style_tag(content='*,*::before,*::after{transition:none!important;animation:none!important}')
    return b, pg, errs

async def grab(pg, t):
    await pg.evaluate(f'window.seek({t:.6f})')
    await pg.evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
    png = await pg.screenshot(type='png', clip={'x': 0, 'y': 0, 'width': W, 'height': H})
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGB'), dtype=np.float32)

def subtimes(t):
    if SUB <= 1: return [t]
    span = SHUT / FPS; ts = [t - span / 2 + span * (i + .5) / SUB for i in range(SUB)]
    for c in CUTS:  # kesishdan o'tmasin: hammasi kadr markazi tomonida qolsin
        if min(ts) < c <= max(ts): ts = [x if (x >= c) == (t >= c) else t for x in ts]
    return [max(0, x) for x in ts]

async def main():
    srv = serve()
    async with async_playwright() as p:
        b, pg, errs = await page(p)
        if PROBE:
            ims = [Image.fromarray((await grab(pg, t)).astype(np.uint8)) for t in PROBE]
            sw = 360; sh = int(H * sw / W); cols = min(6, len(ims)); rows = -(-len(ims) // cols)
            sheet = Image.new('RGB', (cols * (sw + 8), rows * (sh + 8)), 'white')
            for i, im in enumerate(ims): sheet.paste(im.resize((sw, sh)), ((i % cols) * (sw + 8), (i // cols) * (sh + 8)))
            out = OUT.with_name(OUT.stem + '_probe.png'); sheet.save(out); print('probe', out, 'errors:', errs[:5])
            await b.close(); srv.shutdown(); return
        n = int(round(DUR * FPS)); frames = range(n)
        if CH:
            k, m = map(int, CH.split('/')); per = -(-n // m); frames = range(k * per, min(n, (k + 1) * per))
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                *(['-i', AUD, '-shortest', '-c:a', 'aac', '-b:a', '256k'] if AUD and not CH else []),
                                '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                                '-colorspace', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', str(OUT)], stdin=subprocess.PIPE)
        for i in frames:
            t = i / FPS
            acc = None
            for st in subtimes(t):
                f = await grab(pg, st); acc = f if acc is None else acc + f
            enc.stdin.write((acc / len(subtimes(t))).clip(0, 255).astype(np.uint8).tobytes())
            if i % FPS == 0: print(f'{t:5.1f}s', flush=True)
        enc.stdin.close(); enc.wait(); await b.close()
        print('done', OUT, 'errors:', errs[:5])
    srv.shutdown()

asyncio.run(main())
