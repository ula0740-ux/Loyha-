// Uchidan-uchiga sinov: PIN, reja, 630/700/MQS yuklash, qayta yuklash, tuzatish, panel ko'rinishi.
const { chromium } = require('playwright');
const path = require('path');
const X = process.argv[2];          // Excel namunalar papkasi
const OUT = process.argv[3];        // skrinshotlar papkasi
const URL = 'http://127.0.0.1:' + (process.env.PORT || 8790) + '/#boshqaruv';

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1.25 });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  const toast = async () => (await p.locator('#toast').textContent()) || '';
  await p.goto(URL); await p.waitForSelector('#lgPin');
  await p.fill('#lgKim', 'Sinov'); await p.fill('#lgPin', '1234'); await p.click('#lgGo');
  await p.waitForSelector('#amain');
  // reja
  await p.fill('#plCKD', '4700'); await p.fill('#plSKD', '3100');
  await p.click('#gSave'); await p.waitForTimeout(600); console.log('reja:', await toast());
  // 630 + 700
  await p.click('.side button[data-a="natija"]'); await p.waitForSelector('#dzEv');
  await p.setInputFiles('#dzEv input', [path.join(X, '630__04.11.2026.xlsx'), path.join(X, '700__04.11.2026.xlsx')]);
  await p.waitForFunction(() => document.querySelectorAll('#dzEvPv .pv').length === 2, null, { timeout: 15000 });
  await p.screenshot({ path: OUT + '/t_preview.png' });
  for (let i = 0; i < 2; i++) { await p.locator('#dzEvPv .pv button.btn.p').first().click(); await p.waitForTimeout(800); }
  console.log('upload:', await p.locator('#dzEvPv').innerText());
  // qayta yuklash (takror)
  await p.setInputFiles('#dzEv input', [path.join(X, '700__04.11.2026.xlsx')]);
  await p.waitForSelector('#dzEvPv .pv button.btn.p'); await p.locator('#dzEvPv .pv button.btn.p').first().click(); await p.waitForTimeout(800);
  console.log('reupload:', (await p.locator('#dzEvPv .ok-t').first().innerText()));
  // tuzatish
  await p.fill('#tzS', '2026-11-04'); await p.click('#tzLoad'); await p.waitForSelector('#tzT');
  await p.locator('#tzT tr[data-m="TIGGO 7"] input[data-t="630"]').fill('16');
  await p.click('#tzSave'); await p.waitForTimeout(800); console.log('tuzatish:', await toast());
  // MQS
  await p.click('.side button[data-a="mqs"]'); await p.waitForSelector('#dzMq');
  await p.setInputFiles('#dzMq input', [path.join(X, 'MQS__04.11.2026.xlsx')]);
  await p.waitForSelector('#dzMqPv .pv button.btn.p'); await p.locator('#dzMqPv .pv button.btn.p').click(); await p.waitForTimeout(900);
  console.log('mqs:', await p.locator('#dzMqPv').innerText());
  await p.screenshot({ path: OUT + '/t_admin_mqs.png', fullPage: true });
  // reja sahifasi skrinshoti
  await p.click('.side button[data-a="reja"]'); await p.waitForTimeout(300);
  await p.screenshot({ path: OUT + '/t_admin_reja.png', fullPage: true });
  // panel
  await p.click('#tabPanel'); await p.waitForTimeout(700);
  await p.click('[data-pv="kalendar"]'); await p.waitForTimeout(700);
  await p.click('button[data-day="2026-11-04"]'); await p.waitForTimeout(500);
  await p.click('[data-pv="umumiy"]'); await p.waitForTimeout(1200);
  await p.screenshot({ path: OUT + '/t_panel.png', fullPage: true });
  console.log('kun karta:', (await p.locator('.score .sc').first().innerText()).replace(/\n/g, ' | '));
  // telefon kengligi
  await p.setViewportSize({ width: 420, height: 900 }); await p.waitForTimeout(300);
  const w = await p.evaluate(() => document.documentElement.scrollWidth); console.log('phone scrollWidth:', w);
  console.log('errors:', errs);
  await b.close();
})();
