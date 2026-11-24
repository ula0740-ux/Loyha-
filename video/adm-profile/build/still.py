"""Full-resolution stills of film.html at given times (QA): python3 build/still.py OUTDIR t1 t2 ..."""
import asyncio, functools, http.server, socketserver, sys, threading
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parents[3]; OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
TS = [float(x) for x in sys.argv[2:]]
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 8797), functools.partial(Q, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 1920, 'height': 1080})
        await pg.goto('http://127.0.0.1:8797/video/adm-profile/film.html')
        await pg.wait_for_function('window.ready === true', timeout=180000)
        for t in TS:
            await pg.evaluate(f'window.seek({t})')
            await pg.evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))')
            await pg.screenshot(path=str(OUT / f's_{t:07.2f}.jpg'), type='jpeg', quality=85)
        await b.close()
asyncio.run(main()); srv.shutdown(); print('stills ->', OUT)
