#!/usr/bin/env python3
"""scene.html → MP4 (kanvasdan to'g'ridan-to'g'ri JPEG; skrinshotdan ~30x tez).
    python3 render2.py OUT.mp4 --dur 297.04 [--fps 30 --sub 2 --chunk k/n --port 8820 --cuts a,b --w 1920 --h 1080]"""
import asyncio, base64, functools, http.server, socketserver, subprocess, sys, threading
from pathlib import Path
from playwright.async_api import async_playwright
def arg(k, d, c=None):
    return (c or type(d))(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
OUT = Path(sys.argv[1]).resolve(); DUR = arg('--dur', 10.0); FPS = arg('--fps', 30); SUB = arg('--sub', 2); SHUT = .5
PORT = arg('--port', 8820); VW = arg('--w', 1080); VH = arg('--h', 1920); CH = arg('--chunk', '', str); CUTS = [float(x) for x in arg('--cuts', '', str).split(',') if x]
ROOT = Path(__file__).resolve().parents[2]
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), functools.partial(Q, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
def subt(t):
    if SUB <= 1: return [t]
    sp = SHUT / FPS; ts = [t - sp / 2 + sp * (i + .5) / SUB for i in range(SUB)]
    for c in CUTS:
        if min(ts) < c <= max(ts): ts = [x if (x >= c) == (t >= c) else t for x in ts]
    return [max(0, x) for x in ts]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg = await b.new_page(viewport={'width': VW, 'height': VH})
        await pg.goto(f'http://127.0.0.1:{PORT}/video/badantarbiya-2d/scene.html?w={VW}&h={VH}'); await pg.wait_for_function('window.ready === true')
        n = int(round(DUR * FPS)); fr = range(n)
        if CH: k, m = map(int, CH.split('/')); per = -(-n // m); fr = range(k * per, min(n, (k + 1) * per))
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17',
                                '-preset', 'medium', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-movflags', '+faststart', str(OUT)], stdin=subprocess.PIPE)
        for i in fr:
            url = await pg.evaluate(f'window.frameJPEG({subt(i / FPS)})')
            enc.stdin.write(base64.b64decode(url.split(',', 1)[1]))
            if i % (FPS * 5) == 0: print(f'{i / FPS:6.1f}s', flush=True)
        enc.stdin.close(); enc.wait(); await b.close(); print('done', OUT)
asyncio.run(main())
