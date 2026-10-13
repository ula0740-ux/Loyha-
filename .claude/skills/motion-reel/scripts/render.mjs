// node render.mjs --fps 60 --dur 15 --sub 4 [--w 1080 --h 1920] [--page index.html | --url http://localhost:8000/index.html] [--sel #c]
// Pages that use <script type="module"> must be served over HTTP (--url): browsers block ES modules on file://.
// Walks time, seeks the page, pipes screenshots into ffmpeg; tmix blends SUB subframes for motion blur.
import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import { mkdirSync, existsSync } from 'node:fs';
// resolve playwright from the film project (npm i -D playwright there), not from the skill folder
const { chromium } = createRequire(process.cwd() + '/')('playwright');

const argv = process.argv;
const arg = (k, d) => { const i = argv.indexOf('--' + k); return i > 0 ? argv[i + 1] : d; };
const FPS = Number(arg('fps', 60)), DUR = Number(arg('dur', 15)), SUB = Number(arg('sub', 4));
const W = Number(arg('w', 1080)), H = Number(arg('h', 1920));
const PAGE = arg('page', 'index.html'), SEL = arg('sel', '#c');
const URL = arg('url', 'file://' + process.cwd() + '/' + PAGE);
mkdirSync('out', { recursive: true });

const exe = existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined;
const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
await page.goto(URL);
await page.waitForFunction(() => typeof window.seek === 'function');
await page.evaluate(() => document.fonts.ready); // canvas text needs loaded fonts

// tmix averages SUB consecutive subframes; select keeps the last of each group
const vf = `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/${FPS}/TB`;
const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS * SUB), '-i', '-', '-vf', vf,
  '-r', String(FPS), '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', 'out/silent.mp4'],
  { stdio: ['pipe', 'inherit', 'inherit'] });

const total = Math.round(DUR * FPS * SUB);
for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.seek(t), i / (FPS * SUB));
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  const png = await page.locator(SEL).screenshot({ type: 'png' });
  if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % (FPS * SUB) === 0) console.log(`rendered ${i / (FPS * SUB)}s / ${DUR}s`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
