"""Fast chunked renderer for film.html (seek(t) contract, same as cinematic-shorts/render_short.py) using JPEG
screenshots (~2.5x faster than PNG here) and --disable-gpu. Sub-frames on a 180-degree shutter are averaged for motion blur.
  python3 build/render.py OUT_PREFIX --fps 30 --sub 2 --chunks 4 [--scale 1]     -> OUT_PREFIX_k.mp4 per chunk, then OUT_PREFIX.mp4
"""
import asyncio, functools, http.server, io, json, socketserver, subprocess, sys, threading
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parents[1]; ROOT = HERE.parents[1]
def arg(k, d): return type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
OUT = Path(sys.argv[1]); FPS = arg('--fps', 30); SUB = arg('--sub', 2); CH = arg('--chunks', 4); SHUT = .5
K = arg('--k', -1); PORT = arg('--port', 8830)
T = json.loads((HERE / 'audio/timeline.json').read_text())['total']; N = int(round(T * FPS))
F0 = arg('--f0', 0); F1 = arg('--f1', N)   # optional frame range (re-render only part of the film)

async def worker(k):
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', PORT + k), functools.partial(Q, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from playwright.async_api import async_playwright
    per = -(-(F1 - F0) // CH); frames = range(F0 + k * per, min(F1, F0 + (k + 1) * per))
    out = OUT.with_name(f'{OUT.stem}_{k}.mp4')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-crf', '14', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(out)], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--disable-gpu', '--force-color-profile=srgb'])
        pg = await b.new_page(viewport={'width': 1920, 'height': 1080})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(f'http://127.0.0.1:{PORT + k}/video/adm-profile/film.html')
        await pg.wait_for_function('window.ready === true', timeout=180000)
        for i in frames:
            acc = None
            for j in range(SUB):
                t = i / FPS + ((j + .5) / SUB - .5) * SHUT / FPS if SUB > 1 else i / FPS
                await pg.evaluate(f'window.seek({max(0, min(T - 1e-3, t)):.5f})')
                await pg.evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
                f = np.asarray(Image.open(io.BytesIO(await pg.screenshot(type='jpeg', quality=95))).convert('RGB'), np.float32)
                acc = f if acc is None else acc + f
            enc.stdin.write((acc / SUB + .5).clip(0, 255).astype(np.uint8).tobytes())
            if i % (FPS * 5) == 0: print(f'chunk {k}: {i / FPS:.0f}s', flush=True)
        await b.close()
    enc.stdin.close(); enc.wait(); srv.shutdown(); print('done', out, errs[:3], flush=True)

if K >= 0: asyncio.run(worker(K))
else:
    ps = [subprocess.Popen([sys.executable, __file__, str(OUT), '--fps', str(FPS), '--sub', str(SUB), '--chunks', str(CH), '--k', str(k), '--port', str(PORT), '--f0', str(F0), '--f1', str(F1)]) for k in range(CH)]
    for p in ps: p.wait()
    lst = OUT.with_name(OUT.stem + '_list.txt'); lst.write_text(''.join(f"file '{OUT.stem}_{k}.mp4'\n" for k in range(CH)))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', str(OUT)], check=True)
    print('video ->', OUT, f'{F1 - F0} frames')
