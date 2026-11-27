// 17:50 da ish tugagach har bir sex xodimlari KPP gacha necha daqiqada yetib boradi — bitta sodda slayd.
//   node build.js  →  KPP_vaqti_17-50.pptx
const pptxgen = require('pptxgenjs');
const React = require('react'), RDS = require('react-dom/server'), sharp = require('sharp');
const { FaTshirt, FaWalking, FaFlagCheckered } = require('react-icons/fa');
const { applyTheme } = require(process.env.PPTX_SKILL + '/scripts/apply_theme.js');

const THEME = { name: 'KPP vaqti', headFontFace: 'Calibri', bodyFontFace: 'Calibri',
  colors: { dk1: '1F2A44', lt1: 'FFFFFF', dk2: '5B6478', lt2: 'EEF2F7', accent1: '1C9A8C', accent2: 'F28C28', accent3: '1F2A44', accent4: 'D64545', accent5: '8FA3BF', accent6: '2E7D32', hlink: '1C9A8C', folHlink: '5B6478' } };
// sexlar: kiyim almashtirish (min..max), yo'l (min..max), daqiqada — foydalanuvchi bergan o'rtacha vaqtlar
const SEX = [
  { n: 1, name: 'Svarka sexi', ch: [5, 6], rd: [2.5, 3], chTxt: '5–6 daq', rdTxt: '2,5–3 daq' },
  { n: 2, name: 'Boʻyoqlash sexi', ch: [5, 6], rd: [1.5, 2], chTxt: '5–6 daq', rdTxt: '1,5–2 daq', note: 'kiyim + yuz yuvish' },
  { n: 3, name: 'Zborka sexi', ch: [4, 4], rd: [6, 6], chTxt: '4 daq', rdTxt: '6 daq' },
  { n: 4, name: 'SKD sexi', ch: [5, 6], rd: [1, 1], chTxt: '5–6 daq', rdTxt: '1 daq', note: 'kiyim almashtirsa' },
];
const clock = (m) => { const s = Math.round((50 + m) * 60), h = 17 + Math.floor(s / 3600), mm = Math.floor((s % 3600) / 60), ss = s % 60; return `${h}:${String(mm).padStart(2, '0')}${ss ? ':' + String(ss).padStart(2, '0') : ''}`; };
const fmt = (v) => String(v).replace('.', ',');
async function icon(Comp, color) {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: '#' + color, size: 256 }));
  return 'image/png;base64,' + (await sharp(Buffer.from(svg)).png().toBuffer()).toString('base64');
}
(async () => {
  const pres = new pptxgen(); pres.layout = 'LAYOUT_WIDE'; pres.title = 'KPP gacha yetib borish vaqti';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  pres.defineSlideMaster({ title: 'TITLE_ONLY', background: { color: 'FFFFFF' },
    objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.35, w: 12.1, h: 0.8, fontSize: 34, bold: true, color: C.text1, align: 'left', valign: 'middle', margin: 0 }, text: '' } }] });
  pres.addSection({ title: 'KPP vaqti' });
  const s = pres.addSlide({ masterName: 'TITLE_ONLY', sectionTitle: 'KPP vaqti' });
  s.addText('17:50 da ish tugagach — KPP gacha necha daqiqa?', { placeholder: 'title' });
  s.addText('Har bir sex uchun oʻrtacha vaqt: kiyim almashtirish + KPP gacha yoʻl', { x: 0.6, y: 1.1, w: 8, h: 0.4, fontSize: 16, color: C.text2, margin: 0, isTextBox: true });
  // izoh (legend)
  const icShirt = await icon(FaTshirt, THEME.colors.accent1), icWalk = await icon(FaWalking, THEME.colors.accent2), icFlag = await icon(FaFlagCheckered, THEME.colors.dk1);
  s.addImage({ data: icShirt, x: 8.75, y: 1.13, w: 0.3, h: 0.3, objectName: 'izoh kiyim' });
  s.addText('Kiyim almashtirish', { x: 9.12, y: 1.1, w: 1.9, h: 0.36, fontSize: 14, color: C.text1, margin: 0, isTextBox: true });
  s.addImage({ data: icWalk, x: 11.0, y: 1.13, w: 0.3, h: 0.3, objectName: 'izoh yol' });
  s.addText('KPP gacha yoʻl', { x: 11.37, y: 1.1, w: 1.5, h: 0.36, fontSize: 14, color: C.text1, margin: 0, isTextBox: true });

  // soat chizig'i: 17:50 → 18:00 (10 daqiqa)
  const X0 = 3.75, X1 = 9.75, PX = (X1 - X0) / 10, Y0 = 1.85, ROW = 1.12;
  for (let m = 0; m <= 10; m += 2) {
    const x = X0 + m * PX;
    s.addShape(pres.shapes.LINE, { x, y: Y0 + 0.35, w: 0, h: ROW * 4 - 0.1, line: { color: 'D5DCE6', width: 0.75, dashType: m % 10 ? 'dash' : 'solid' }, objectName: `chiziq ${m}` });
    s.addText(clock(m), { x: x - 0.5, y: Y0, w: 1, h: 0.3, fontSize: 12, bold: m === 0 || m === 10, color: C.text2, align: 'center', margin: 0, isTextBox: true });
  }
  s.addText('Yetib kelish', { x: 10.15, y: Y0, w: 2.6, h: 0.3, fontSize: 12, bold: true, color: C.text2, margin: 0, isTextBox: true });

  for (const [i, x] of SEX.entries()) {
    const y = Y0 + 0.45 + i * ROW, chM = (x.ch[0] + x.ch[1]) / 2, rdM = (x.rd[0] + x.rd[1]) / 2;
    const tMin = x.ch[0] + x.rd[0], tMax = x.ch[1] + x.rd[1];
    // raqamli doira + sex nomi
    s.addShape(pres.shapes.OVAL, { x: 0.6, y: y + 0.12, w: 0.56, h: 0.56, fill: { color: C.text1 }, line: { type: 'none' }, objectName: `raqam ${x.n}` });
    s.addText(String(x.n), { x: 0.6, y: y + 0.12, w: 0.56, h: 0.56, fontSize: 20, bold: true, color: C.background1, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
    s.addText([{ text: x.name, options: { fontSize: 20, bold: true, color: C.text1, breakLine: !!x.note } }].concat(x.note ? [{ text: x.note, options: { fontSize: 12, color: C.text2 } }] : []),
      { x: 1.3, y: y + 0.05, w: 2.35, h: 0.7, valign: 'middle', margin: 0, isTextBox: true });
    // ikki rangli tasma: kiyim (firuza) + yo'l (to'q sariq), o'rtacha uzunlikda
    const wCh = chM * PX, wRd = rdM * PX;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: X0, y: y + 0.15, w: wCh, h: 0.5, fill: { color: C.accent1 }, line: { type: 'none' }, rectRadius: 0.08, objectName: `${x.name} kiyim` });
    s.addText(x.chTxt, { x: X0, y: y + 0.15, w: wCh, h: 0.5, fontSize: 14, bold: true, color: C.background1, align: 'center', valign: 'middle', margin: 0, isTextBox: true });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: X0 + wCh + 0.04, y: y + 0.15, w: wRd - 0.04, h: 0.5, fill: { color: C.accent2 }, line: { type: 'none' }, rectRadius: 0.08, objectName: `${x.name} yol` });
    const narrow = wRd < 0.9;   // tor tasmada yozuv tasmadan o'ngga chiqadi
    s.addText(x.rdTxt, { x: narrow ? X0 + wCh + wRd + 0.1 : X0 + wCh, y: y + 0.15, w: narrow ? 1.0 : wRd, h: 0.5, fontSize: 14, bold: true, color: narrow ? C.accent2 : C.background1, align: narrow ? 'left' : 'center', valign: 'middle', margin: 0, isTextBox: true });
    // yetib kelish vaqti va jami
    const arr = tMin === tMax ? clock(tMax) : `${clock(tMin)} – ${clock(tMax)}`, tot = tMin === tMax ? `${fmt(tMax)} daqiqa` : `${fmt(tMin)}–${fmt(tMax)} daqiqa`;
    s.addImage({ data: icFlag, x: 10.15, y: y + 0.2, w: 0.32, h: 0.32, objectName: `${x.name} bayroq` });
    s.addText([{ text: arr, options: { fontSize: 20, bold: true, color: C.text1, breakLine: true } }, { text: tot, options: { fontSize: 13, color: C.text2 } }],
      { x: 10.6, y: y + 0.02, w: 2.2, h: 0.76, valign: 'middle', margin: 0, isTextBox: true });
  }
  s.addText('* Barcha vaqtlar oʻrtacha. Tasma uzunligi oʻrtacha qiymat boʻyicha. SKD sexi kiyim almashtirmasa — KPP gacha 1 daqiqa (17:51).',
    { x: 0.6, y: 6.85, w: 12.1, h: 0.35, fontSize: 11, italic: true, color: C.text2, margin: 0, isTextBox: true });
  s.addNotes('17:50 da ish tugaydi. Svarka: kiyim 5–6 daq, yo‘l 2,5–3 daq — KPP ga 17:57:30–17:59. Bo‘yoqlash: kiyim va yuz yuvish 5–6 daq, yo‘l 1,5–2 daq — 17:56:30–17:58. Zborka: kiyim 4 daq, yo‘l 6 daq — 18:00 (eng uzoq yo‘l). SKD: kiyim almashtirsa 5–6 daq, yo‘l 1 daq — 17:56–17:57.');
  await pres.writeFile({ fileName: 'KPP_vaqti_17-50.pptx' });
  await applyTheme('KPP_vaqti_17-50.pptx', THEME);
  console.log('ok');
})();
