// Bitta 3 slaydli taqdimot, o'zbek kirill yozuvida. Matn lotinda yoziladi va T() orqali kirillga o'giriladi.
import { createRequire } from 'node:module';
import { latToCyr } from '../../studio/src/lib/uzbek.ts';
const require = createRequire(process.env.NODE_PATH + '/');
const pptxgen = require('pptxgenjs');
const React = require('react');
const RDS = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const { applyTheme } = require('/root/.claude/skills/synced/bb7b0922-36d0-4b1f-8fcb-0025844e920b_160cec7e-c774-4a51-9040-7a1d5a36cb8e/pptx/scripts/apply_theme.js');

// Latin brand/abbreviation tokens stay as written
const KEEP = /^(ADM|MS|KPI|WPO|AI|BPD|OJT|HR|PowerPoint|ACADEMY|Academy)$/;
// loanwords whose Cyrillic spelling differs from a letter-by-letter conversion
const FIX: [RegExp, string][] = [
  [/компетенси/g, 'компетенци'], [/Компетенси/g, 'Компетенци'], [/принсип/g, 'принцип'], [/рейестр/g, 'реестр'],
  [/аттестатси/g, 'аттестаци'], [/\bсех/g, 'цех'], [/ентабр/g, 'ентябр'], [/Ийун/g, 'Июн'], [/ийун/g, 'июн'],
  [/Ийул/g, 'Июл'], [/ийул/g, 'июл'],   // a month name standing alone takes the soft sign: апрель, июнь, июль, сентябрь (апрелда, сентябрда without it)
  [/([Аа]прел|[Ии]юн|[Ии]юл|[Сс]ентябр)(?![\p{L}])/gu, '$1ь'],
];
function T(s: string): string {
  let out = s.split(/(\s+)/).map((w) => {
    const core = w.replace(/[^\p{L}]/gu, '');
    return core && KEEP.test(core) ? w : latToCyr(w);
  }).join('');
  for (const [re, to] of FIX) out = out.replace(re, to);
  return out;
}

const THEME = {
  name: 'ADM Academy',
  headFontFace: 'Calibri', bodyFontFace: 'Calibri',
  colors: { dk1: '1A1F36', lt1: 'FFFFFF', dk2: '14213D', lt2: 'EEF1F6',
    accent1: '14213D', accent2: 'C8102E', accent3: '5B6B8C', accent4: '9AA7BF', accent5: '2E7D32', accent6: 'F2A900',
    hlink: '14213D', folHlink: '5B6B8C' },
};
const HEX = { navy: '14213D', red: 'C8102E', slate: '5B6B8C', mute: '9AA7BF', grid: 'DDE2EA' };
const PERIOD = T('2026-yil 1-aprel – 30-sentabr');

async function icon(Comp: any) {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: '#FFFFFF', size: 256 }));
  return 'image/png;base64,' + (await sharp(Buffer.from(svg)).png().toBuffer()).toString('base64');
}

function stat(slide: any, C: any, o: any) {
  const { x, y, w, h, value, label, note, alert, name } = o;
  slide.addShape('roundRect', { x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: 'none' }, objectName: name + ' card' });
  slide.addText(T(value), { x: x + 0.25, y: y + 0.12, w: w - 0.5, h: h * 0.45, fontSize: h > 1.6 ? 40 : 32, bold: true, color: alert ? C.accent2 : C.text2, margin: 0, valign: 'bottom', isTextBox: true, objectName: name + ' value' });
  slide.addText([
    { text: T(label), options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
    { text: T(note), options: { fontSize: 12, color: C.accent3 } },
  ], { x: x + 0.25, y: y + 0.12 + h * 0.47, w: w - 0.5, h: h * 0.47 - 0.15, margin: 0, valign: 'top', isTextBox: true, objectName: name + ' label' });
}

const chartBase = (extra: any) => ({
  showTitle: true, titleFontSize: 14, titleColor: HEX.navy, titleFontFace: '+mj-lt', titleBold: true,
  catAxisLabelColor: HEX.slate, valAxisLabelColor: HEX.slate, catAxisLabelFontSize: 12, valAxisLabelFontSize: 11,
  catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt',
  valGridLine: { color: HEX.grid, size: 0.75 }, catGridLine: { style: 'none' }, showLegend: false,
  showValue: true, dataLabelFontSize: 12, dataLabelColor: HEX.navy, ...extra,
});

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = 'ADM Academy';
  pres.company = 'ADM Jizzax';
  pres.title = T('6 oylik o‘qitish va kompetensiya natijalari');
  const C = pres.SchemeColor;
  pres.defineSlideMaster({
    title: 'CONTENT', background: { color: C.background1 }, margin: [0.5, 0.5, 0.6, 0.5],
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 10.6, h: 0.75, fontSize: 30, bold: true, color: C.text2, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
      { placeholder: { options: { name: 'sub', type: 'body', x: 0.5, y: 1.02, w: 10.6, h: 0.42, fontSize: 15, color: C.accent3, align: 'left', valign: 'top', margin: 0 }, text: '' } },
      { text: { text: 'ADM ACADEMY', options: { x: 10.9, y: 0.38, w: 1.95, h: 0.5, fontSize: 13, bold: true, color: C.accent2, align: 'right', charSpacing: 2, margin: 0 } } },
      { text: { text: PERIOD + T(' • Manba: ADM Academy oylik davomat jurnallari va baholash varaqlari'), options: { x: 0.5, y: 7.02, w: 11.0, h: 0.3, fontSize: 10, color: C.accent3, margin: 0 } } },
    ],
    slideNumber: { x: 12.35, y: 7.02, w: 0.5, h: 0.3, fontSize: 10, color: C.accent3, align: 'right' },
  });
  const months = ['Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentabr'].map(T);
  const hdr = (t: string, al = 'left') => ({ text: T(t), options: { bold: true, color: C.background1, fill: { color: C.text2 }, align: al } });
  const tbl = { fontSize: 14, fontFace: 'Calibri', border: { type: 'solid', pt: 0.75, color: HEX.grid }, valign: 'middle', margin: [0, 0.12, 0, 0.12] };

  // 1 — asosiy xulosalar
  pres.addSection({ title: T('Xulosa') });
  let s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: T('Xulosa') });
  s.addText(T('6 oylik o‘qitish va kompetensiya natijalari'), { placeholder: 'title' });
  s.addText(T('Qamrov yuqori, ammo sentabrda davomat pasaydi va Sifat yo‘nalishida kompetensiya past'), { placeholder: 'sub' });
  const sw = 3.6, sh = 2.45;
  [
    { value: '94,5%', label: 'Brigadirlar o‘qitildi', note: '165 nafardan 156 nafari kamida bir marta' },
    { value: '23 nafar', label: 'Sentabrda darsga kelmagan', note: 'Aprelda 5 nafar edi; qamrov 85,0%gacha tushdi', alert: true },
    { value: '76,8%', label: 'O‘rtacha kompetensiya bali', note: '341 xodim baholandi (585 ball maksimum)' },
    { value: '108 nafar', label: '70%dan past natija', note: 'Sifat 78, Yig‘uv 28 nafar', alert: true },
  ].forEach((d, i) => stat(s, C, { ...d, x: 0.5 + (i % 2) * (sw + 0.3), y: 1.75 + Math.floor(i / 2) * (sh + 0.3), w: sw, h: sh, name: 'key' + (i + 1) }));
  s.addShape('roundRect', { x: 8.35, y: 1.75, w: 4.5, h: 5.2, rectRadius: 0.08, fill: { color: C.text2 }, line: { type: 'none' }, objectName: 'decisions panel' });
  s.addText(T('Rahbariyat qarori uchun'), { x: 8.65, y: 1.95, w: 3.9, h: 0.45, fontSize: 18, bold: true, color: C.background1, margin: 0, isTextBox: true, objectName: 'decisions head' });
  const dec = [
    [fa.FaUserCheck, 'Davomatni tiklash', 'Ta’til va smenaga mos qo‘shimcha darslar. Payvandlash (7) va Ta’minot (5) birinchi navbatda.'],
    [fa.FaBullseye, '106 xodimni qayta o‘qitish', 'Sifat 78 + Yig‘uv 28: ADM MS, yo‘qotishlar, WPO. 30 kunda qayta baho.'],
    [fa.FaDatabase, 'Yagona natijalar reyestri', 'Davomat, baho, OJT, sertifikat va xarajat bitta tizimda (Akademiya, HR, Moliya).'],
  ];
  for (const [i, [Ic, h, b]] of dec.entries()) {
    const y = 2.6 + i * 1.4;
    s.addShape('ellipse', { x: 8.65, y, w: 0.5, h: 0.5, fill: { color: C.accent2 }, line: { type: 'none' }, objectName: 'decision icon bg ' + (i + 1) });
    s.addImage({ data: await icon(Ic), x: 8.77, y: y + 0.12, w: 0.26, h: 0.26, altText: T(h as string), objectName: 'decision icon ' + (i + 1) });
    s.addText([{ text: T(h as string), options: { bold: true, fontSize: 15, color: C.background1, breakLine: true } }, { text: T(b as string), options: { fontSize: 12, color: C.background2 } }],
      { x: 9.35, y: y - 0.05, w: 3.3, h: 1.25, margin: 0, valign: 'top', isTextBox: true, objectName: 'decision text ' + (i + 1) });
  }
  s.addNotes(T('94,5% — olti oyda kamida bir marta qatnashish, kurs tugatish emas. Sentabrdagi brigadir davomat indikatori 73,9% (reja 90%dan yuqori). Past natijalarning 72,2%i Sifat yo‘nalishida. 70% — tahliliy chegara, rasmiy attestatsiya mezoni emas. Choralar — tahliliy taklif, tasdiqlangan topshiriq emas.'));

  // 2 — davomat
  pres.addSection({ title: T('Davomat') });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: T('Davomat') });
  s.addText(T('Davomat sentabrda pasaydi, eng pasti Uskunalarda'), { placeholder: 'title' });
  s.addText(T('Brigadirlar: 2 865 qatnashuv · rahbarlar: 455 imkoniyatdan 208 qayd (45,7%)'), { placeholder: 'sub' });
  s.addChart(pres.charts.LINE, [{ name: T('Qamrov'), labels: months, values: [96.6, 94.7, 96.7, 95.3, 91.2, 85.0] }],
    chartBase({ x: 0.5, y: 1.6, w: 6.05, h: 2.6, title: T('Oyda kamida 1 darsga qatnashganlar, %'), chartColors: [HEX.navy],
      lineSize: 3, lineDataSymbol: 'circle', lineDataSymbolSize: 8, valAxisMinVal: 80, valAxisMaxVal: 100, valAxisMajorUnit: 5,
      dataLabelPosition: 't', dataLabelFormatCode: '0.0', objectName: 'coverage chart' }));
  s.addChart(pres.charts.BAR, [{ name: T('Kelmaganlar'), labels: months, values: [5, 8, 5, 7, 13, 23] }],
    chartBase({ x: 0.5, y: 4.3, w: 6.05, h: 2.6, barDir: 'col', barGapWidthPct: 60, title: T('Oyda birorta darsga kelmagan brigadirlar, nafar'),
      chartColors: [HEX.mute, HEX.mute, HEX.mute, HEX.mute, HEX.red, HEX.red], dataLabelPosition: 'outEnd', valAxisHidden: true, valGridLine: { style: 'none' }, valAxisMaxVal: 28, objectName: 'absent chart' }));
  const depts = ['Bo‘yoqlash', 'Sifat nazorati', 'Yig‘uv', 'Ta’minot', 'Ma’muriy xizmat', 'Payvandlash', 'SKD', 'Uskunalar'].map(T);
  const att = [97.7, 95.5, 94.3, 94.3, 91.7, 91.0, 89.4, 66.7];
  s.addChart(pres.charts.BAR, [{ name: T('Qatnashuv'), labels: depts.slice().reverse(), values: att.slice().reverse() }],
    chartBase({ x: 6.8, y: 1.6, w: 6.05, h: 4.6, barDir: 'bar', barGapWidthPct: 45, title: T('Bo‘limlar: o‘rtacha oylik qatnashuv, % (6 oy)'),
      chartColors: [HEX.red, HEX.mute, HEX.mute, HEX.mute, HEX.mute, HEX.mute, HEX.mute, HEX.navy],
      dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', valAxisHidden: true, valGridLine: { style: 'none' }, valAxisMinVal: 0, valAxisMaxVal: 110, objectName: 'dept chart' }));
  s.addText(T('Sentabrda kelmagan 23 nafar: Payvandlash 7, Ta’minot 5, Sifat 3, Ma’muriy xizmat 3.'),
    { x: 6.8, y: 6.35, w: 6.05, h: 0.5, fontSize: 12, italic: true, color: C.accent3, margin: 0, valign: 'top', isTextBox: true, objectName: 'dept note' });
  s.addNotes(T('Iyundan sentabrgacha qamrov 11,7 foiz punktga kamaydi (96,7% → 85,0%). Uskunalar guruhida 3 brigadir: Sh. Ikramovning iyul va avgustdagi qatnashuvi yo‘q. Rahbarlar uchun 45,7% — qayd ulushi, o‘quv rejasini bajarish foizi emas.'));

  // 3 — kompetensiya va KPI
  pres.addSection({ title: T('Kompetensiya va KPI') });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: T('Kompetensiya va KPI') });
  s.addText(T('Kompetensiya va KPI: Sifat yo‘nalishi ustuvor'), { placeholder: 'title' });
  s.addText(T('341 xodimning baholash natijalari va sentabr KPI tafovutlari'), { placeholder: 'sub' });
  const rows: [string, number, string, number][] = [['Sifat', 130, '66,8%', 78], ['Yig‘uv', 118, '81,4%', 28], ['Bo‘yoqlash', 43, '86,5%', 1], ['SKD', 18, '83,2%', 0], ['Ta’mirlash', 17, '79,9%', 0], ['Uskunalar', 15, '88,4%', 1]];
  s.addTable([[hdr('Yo‘nalish'), hdr('Xodim', 'right'), hdr('O‘rtacha', 'right'), hdr('70%dan past', 'right')],
    ...rows.map((r) => {
      const o = { color: r[3] >= 20 ? C.accent2 : C.text1, bold: r[3] >= 20 };
      return [{ text: T(r[0]), options: o }, { text: String(r[1]), options: { ...o, align: 'right' } }, { text: r[2], options: { ...o, align: 'right' } }, { text: String(r[3]), options: { ...o, align: 'right' } }];
    })],
  { ...tbl, x: 0.5, y: 1.65, w: 6.05, colW: [1.95, 1.2, 1.3, 1.6], rowH: 0.42, objectName: 'competency table' });
  stat(s, C, { x: 0.5, y: 4.85, w: 2.9, h: 1.55, value: '76,8%', label: 'O‘rtacha ball', note: '585 maksimal ballga nisbatan', name: 'avg' });
  stat(s, C, { x: 3.65, y: 4.85, w: 2.9, h: 1.55, value: '108 nafar', label: '70%dan past', note: 'Ularning 72,2%i Sifatda', alert: true, name: 'low' });
  s.addText(T('70% — tahliliy chegara, rasmiy attestatsiya mezoni emas.'),
    { x: 0.5, y: 6.5, w: 6.05, h: 0.35, fontSize: 12, italic: true, color: C.accent3, margin: 0, valign: 'top', isTextBox: true, objectName: 'competency note' });
  const kpi: [string, string, string, boolean?][] = [['Brigadir davomati', '>90%', '73,9% (−16,1 f.p.)', true], ['Dars bahosi / samaradorlik', '100% / ≥85%', 'Yakun aniqlanmadi'], ['ADM MS darsi', '2 ta/oy', 'Ijro reyestri kerak'], ['PowerPoint mashg‘uloti', '8 ta/oy', 'Yakun tasdig‘i kerak'], ['AI tahlil tizimi', '50%', 'Ishga tushirilmagan'], ['3 darajali BPD', '40%', 'Ijro tasdiqlanmagan']];
  s.addTable([[hdr('Ko‘rsatkich'), hdr('Reja', 'center'), hdr('Holat')],
    ...kpi.map(([a, b, c, bad]) => [{ text: T(a), options: { color: C.text1 } }, { text: T(b), options: { align: 'center', color: C.text1 } }, { text: T(c), options: { color: bad ? C.accent2 : C.accent3, bold: !!bad } }])],
  { ...tbl, x: 6.8, y: 1.65, w: 6.05, colW: [2.55, 1.25, 2.25], rowH: 0.42, fontSize: 13, objectName: 'kpi table' });
  s.addText(T('Sentabr: 120 ta qoldirilgan qatnashuv sababi'), { x: 6.8, y: 4.85, w: 6.05, h: 0.35, fontSize: 15, bold: true, color: C.text2, margin: 0, isTextBox: true, objectName: 'reasons head' });
  [['67', 'Ta’til'], ['29', 'Qatnashmagan'], ['24', 'Sababi yozilmagan']].forEach(([v, l], i) => {
    const x = 6.8 + i * 2.07;
    s.addShape('roundRect', { x, y: 5.3, w: 1.91, h: 1.55, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: 'none' }, objectName: 'reason card ' + (i + 1) });
    s.addText(v, { x: x + 0.2, y: 5.38, w: 1.5, h: 0.8, fontSize: 34, bold: true, color: i ? C.accent2 : C.text2, margin: 0, valign: 'bottom', isTextBox: true, objectName: 'reason value ' + (i + 1) });
    s.addText(T(l), { x: x + 0.2, y: 6.22, w: 1.55, h: 0.5, fontSize: 13, color: C.text1, margin: 0, valign: 'top', isTextBox: true, objectName: 'reason label ' + (i + 1) });
  });
  s.addNotes(T('73,9% — sentabrdagi brigadir dars qaydi ulushi (339/459), 90% mezondan 16,1 f.p. past. 76,8% kompetensiya bali ≥85% samaradorlik KPI bilan bir xil o‘lchov emas. Sifatdagi eng past komponentlar: ADM MS 34,2%, yo‘qotishlar 34,2%, WPO 39,4%. 120 qoldirilgan qatnashuv 120 nafar xodim degani emas.'));

  const out = 'ADM_Akademiya_6_oylik_natijalar_kirill.pptx';
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log('ok');
})().catch((e) => { console.error(e); process.exit(1); });
