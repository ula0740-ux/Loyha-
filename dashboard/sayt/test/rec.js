// Effekt namunasi: menyular va sahifalar almashinuvini videoga yozish.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: process.argv[2], size: { width: 1280, height: 720 } } });
  const p = await c.newPage();
  const w = t => p.waitForTimeout(t);
  await p.goto('http://127.0.0.1:8790/'); await p.waitForSelector('.score'); await w(900);
  for (const s of ['CKD', 'SKD', 'ALL']) { await p.click(`#sexSeg button[data-s="${s}"]`); await w(900); }
  await p.click('#tabAdmin'); await w(800);
  await p.fill('#lgKim', 'Sinov'); await p.fill('#lgPin', '1234'); await p.click('#lgGo'); await w(1000);
  for (const a of ['natija', 'mqs', 'tarix', 'reja']) { await p.click(`.side button[data-a="${a}"]`); await w(900); }
  await p.click('#tabPanel'); await w(1000); await p.click('button[data-day="2026-11-04"]'); await w(900); await p.mouse.wheel(0, 1400); await w(1400);
  await c.close(); await b.close();
})();
