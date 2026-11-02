const pptxgen = require('pptxgenjs');
const React = require('react');
const RDS = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const { applyTheme } = require('/root/.claude/skills/synced/bb7b0922-36d0-4b1f-8fcb-0025844e920b_160cec7e-c774-4a51-9040-7a1d5a36cb8e/pptx/scripts/apply_theme.js');

const THEME = {
  name: 'ADM Academy',
  headFontFace: 'Calibri', bodyFontFace: 'Calibri',
  colors: { dk1: '1A1F36', lt1: 'FFFFFF', dk2: '14213D', lt2: 'EEF1F6',
    accent1: '14213D', accent2: 'C8102E', accent3: '5B6B8C', accent4: '9AA7BF', accent5: '2E7D32', accent6: 'F2A900',
    hlink: '14213D', folHlink: '5B6B8C' },
};
const HEX = { navy: '14213D', red: 'C8102E', slate: '5B6B8C', mute: '9AA7BF', tint: 'EEF1F6', grid: 'DDE2EA' };
const PERIOD = '2026-yil 1-aprel – 30-sentabr';

async function icon(Comp, color = 'FFFFFF') {
  const svg = RDS.renderToStaticMarkup(React.createElement(Comp, { color: '#' + color, size: 256 }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return 'image/png;base64,' + png.toString('base64');
}

function setup(pres, footer) {
  pres.layout = 'LAYOUT_WIDE';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = 'ADM Academy';
  pres.company = 'ADM Jizzax';
  const C = pres.SchemeColor;
  pres.defineSlideMaster({
    title: 'CONTENT',
    background: { color: C.background1 },
    margin: [0.5, 0.5, 0.6, 0.5],
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 10.6, h: 0.75, fontSize: 30, bold: true, color: C.text2, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
      { placeholder: { options: { name: 'sub', type: 'body', x: 0.5, y: 1.02, w: 10.6, h: 0.42, fontSize: 15, color: C.accent3, align: 'left', valign: 'top', margin: 0 }, text: '' } },
      { text: { text: 'ADM ACADEMY', options: { x: 10.9, y: 0.38, w: 1.95, h: 0.5, fontSize: 13, bold: true, color: C.accent2, align: 'right', charSpacing: 2, margin: 0 } } },
      { text: { text: footer, options: { x: 0.5, y: 7.02, w: 11.0, h: 0.3, fontSize: 10, color: C.accent3, margin: 0 } } },
    ],
    slideNumber: { x: 12.35, y: 7.02, w: 0.5, h: 0.3, fontSize: 10, color: C.accent3, align: 'right' },
  });
  return C;
}

function stat(slide, C, { x, y, w, h, value, label, note, alert, name }) {
  slide.addShape('roundRect', { x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: 'none' }, objectName: name + ' card' });
  slide.addText(value, { x: x + 0.25, y: y + 0.12, w: w - 0.5, h: h * 0.45, fontSize: h > 1.6 ? 44 : 34, bold: true, color: alert ? C.accent2 : C.text2, margin: 0, valign: 'bottom', isTextBox: true, objectName: name + ' value' });
  slide.addText([
    { text: label, options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
    { text: note, options: { fontSize: 12, color: C.accent3 } },
  ], { x: x + 0.25, y: y + 0.12 + h * 0.47, w: w - 0.5, h: h * 0.47 - 0.15, margin: 0, valign: 'top', isTextBox: true, objectName: name + ' label' });
}

const chartBase = (C, extra) => ({
  showTitle: true, titleFontSize: 14, titleColor: HEX.navy, titleFontFace: '+mj-lt', titleBold: true,
  catAxisLabelColor: HEX.slate, valAxisLabelColor: HEX.slate, catAxisLabelFontSize: 12, valAxisLabelFontSize: 11,
  catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt',
  valGridLine: { color: HEX.grid, size: 0.75 }, catGridLine: { style: 'none' }, showLegend: false,
  showValue: true, dataLabelFontSize: 12, dataLabelColor: HEX.navy, ...extra,
});

async function deck3() {
  const pres = new pptxgen();
  const C = setup(pres, PERIOD + ' • Manba: ADM Academy oylik davomat jurnallari va baholash varaqlari');
  pres.title = '6 oylik o‘qitish va kompetensiya natijalari';
  const months = ['Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentabr'];

  // 1
  pres.addSection({ title: 'Qamrov va davomat' });
  let s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Qamrov va davomat' });
  s.addText('Qamrov yuqori, lekin sentabrda davomat pasaydi', { placeholder: 'title' });
  s.addText('6 oylik o‘qitish va kompetensiya natijalari · ' + PERIOD, { placeholder: 'sub' });
  const cw = 2.9, gx = 0.233;
  [
    { value: '94,5%', label: 'Brigadirlar qamrovi', note: '165 nafardan 156 nafari kamida bir marta qatnashgan' },
    { value: '2 865', label: 'Brigadir qatnashuvi', note: 'Barcha darslardagi qatnashuvlar yig‘indisi' },
    { value: '45,7%', label: 'Rahbarlar qatnashuvi', note: '35 rahbar, 13 mavzu: 455 imkoniyatdan 208 qayd', alert: true },
    { value: '23 nafar', label: 'Sentabrda darsga kelmagan', note: 'Aprelda 5 nafar edi', alert: true },
  ].forEach((d, i) => stat(s, C, { ...d, x: 0.5 + i * (cw + gx), y: 1.65, w: cw, h: 1.55, name: 'kpi' + (i + 1) }));
  s.addChart(pres.charts.LINE, [{ name: 'Qamrov, %', labels: months, values: [96.6, 94.7, 96.7, 95.3, 91.2, 85.0] }],
    chartBase(C, { x: 0.5, y: 3.45, w: 6.05, h: 3.4, title: 'Oyda kamida 1 darsga qatnashganlar, %', chartColors: [HEX.navy],
      lineSize: 3, lineDataSymbol: 'circle', lineDataSymbolSize: 8, valAxisMinVal: 80, valAxisMaxVal: 100, valAxisMajorUnit: 5,
      dataLabelPosition: 't', dataLabelFormatCode: '0.0', objectName: 'coverage chart' }));
  s.addChart(pres.charts.BAR, [{ name: 'Kelmaganlar', labels: months, values: [5, 8, 5, 7, 13, 23] }],
    chartBase(C, { x: 6.8, y: 3.45, w: 6.05, h: 3.4, barDir: 'col', barGapWidthPct: 60, title: 'Oyda birorta darsga kelmagan brigadirlar, nafar',
      chartColors: [HEX.mute, HEX.mute, HEX.mute, HEX.mute, HEX.red, HEX.red], dataLabelPosition: 'outEnd', valAxisHidden: true, valGridLine: { style: 'none' }, objectName: 'absent chart' }));
  s.addNotes('Iyundan sentabrgacha qamrov 11,7 foiz punktga kamaydi (96,7% → 85,0%). Kelmaganlar iyuldagi 7 nafardan sentabrda 23 nafarga oshdi. 94,5% — olti oyda kamida bir marta qatnashish, kurs tugatish emas. Rahbarlar uchun 45,7% — qayd ulushi, o‘quv rejasini bajarish foizi emas.');

  // 2
  pres.addSection({ title: 'Bo‘limlar va kompetensiya' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Bo‘limlar va kompetensiya' });
  s.addText('Sifat yo‘nalishida kompetensiya eng past', { placeholder: 'title' });
  s.addText('Bo‘limlar kesimida davomat va 341 xodimning kompetensiya bahosi', { placeholder: 'sub' });
  const depts = ['Bo‘yoqlash', 'Sifat nazorati', 'Yig‘uv', 'Ta’minot', 'Ma’muriy xizmat', 'Payvandlash', 'SKD', 'Uskunalar'];
  const att = [97.7, 95.5, 94.3, 94.3, 91.7, 91.0, 89.4, 66.7];
  s.addChart(pres.charts.BAR, [{ name: 'Qatnashuv', labels: depts.slice().reverse(), values: att.slice().reverse() }],
    chartBase(C, { x: 0.5, y: 1.65, w: 5.7, h: 5.2, barDir: 'bar', barGapWidthPct: 45, title: 'O‘rtacha oylik qatnashuv, % (6 oy)',
      chartColors: [HEX.red, HEX.mute, HEX.mute, HEX.mute, HEX.mute, HEX.mute, HEX.mute, HEX.navy],
      dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', valAxisHidden: true, valGridLine: { style: 'none' }, valAxisMinVal: 0, valAxisMaxVal: 110, objectName: 'dept chart' }));
  stat(s, C, { x: 6.55, y: 1.65, w: 3.0, h: 1.45, value: '76,8%', label: 'O‘rtacha ball', note: '585 maksimal ballga nisbatan', name: 'avg' });
  stat(s, C, { x: 9.85, y: 1.65, w: 3.0, h: 1.45, value: '108 nafar', label: '70%dan past natija', note: 'Ularning 72,2%i Sifatda', alert: true, name: 'low' });
  const hdr = (t, al = 'left') => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 }, align: al } });
  const rows = [['Sifat', 130, '66,8%', 78], ['Yig‘uv', 118, '81,4%', 28], ['Bo‘yoqlash', 43, '86,5%', 1], ['SKD', 18, '83,2%', 0], ['Ta’mirlash', 17, '79,9%', 0], ['Uskunalar', 15, '88,4%', 1]];
  s.addTable([[hdr('Yo‘nalish'), hdr('Xodim', 'right'), hdr('O‘rtacha', 'right'), hdr('70%dan past', 'right')],
    ...rows.map((r) => {
      const bad = r[3] >= 20;
      const o = { color: bad ? C.accent2 : C.text1, bold: bad };
      return [{ text: r[0], options: o }, { text: String(r[1]), options: { ...o, align: 'right' } }, { text: r[2], options: { ...o, align: 'right' } }, { text: String(r[3]), options: { ...o, align: 'right' } }];
    })],
  { x: 6.55, y: 3.35, w: 6.3, colW: [2.1, 1.2, 1.4, 1.6], rowH: 0.42, fontSize: 14, fontFace: 'Calibri', border: { type: 'solid', pt: 0.75, color: HEX.grid }, valign: 'middle', margin: [0, 0.12, 0, 0.12], objectName: 'competency table' });
  s.addText('Sifat 78 va Yig‘uv 28 xodim — maqsadli o‘qitishga. 70% — tahliliy chegara, rasmiy attestatsiya mezoni emas.',
    { x: 6.55, y: 6.4, w: 6.3, h: 0.5, fontSize: 12, italic: true, color: C.accent3, margin: 0, valign: 'top', isTextBox: true, objectName: 'competency note' });
  s.addNotes('Uskunalar guruhida 3 brigadir: Sh. Ikramovning iyul va avgustdagi qatnashuvi yo‘q. Sentabrda kelmagan 23 nafar: Payvandlash 7, Ta’minot 5, Sifat 3, Ma’muriy xizmat 3, SKD 2, qolganlari 1 tadan. Kompetensiya baholashi avgust–sentabrda o‘tkazilgan, oldingi baho yo‘qligi sabab o‘sish hisoblanmadi. Sifatdagi eng past komponentlar: ADM MS 34,2%, yo‘qotishlar 34,2%, WPO 39,4%.');

  // 3
  pres.addSection({ title: 'KPI va choralar' });
  s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'KPI va choralar' });
  s.addText('KPI tafovutlari va keyingi 30 kun choralari', { placeholder: 'title' });
  s.addText('Sentabr rejalari, ijro dalili va boshqaruv takliflari', { placeholder: 'sub' });
  const kpi = [['Brigadir davomati', '>90%', '73,9% (−16,1 f.p.)', true], ['Dars bahosi va samaradorligi', '100% / ≥85%', '6 oylik yakun aniqlanmadi'], ['ADM MS prinsiplari darsi', '2 ta/oy', 'Ijro reyestri kerak'], ['PowerPoint mashg‘uloti', '8 ta/oy', 'Yakun tasdig‘i kerak'], ['AI orqali tahlil tizimi', '50%', 'Ishga tushirish dalili yo‘q'], ['3 darajali BPD tizimi', '40%', 'Ijro foizi tasdiqlanmagan']];
  s.addTable([[hdr('Ko‘rsatkich'), hdr('Reja', 'center'), hdr('Holat')],
    ...kpi.map(([a, b, c, bad]) => [{ text: a, options: { color: C.text1 } }, { text: b, options: { align: 'center', color: C.text1 } }, { text: c, options: { color: bad ? C.accent2 : C.accent3, bold: !!bad } }])],
  { x: 0.5, y: 1.65, w: 7.3, colW: [3.0, 1.5, 2.8], rowH: 0.42, fontSize: 14, fontFace: 'Calibri', border: { type: 'solid', pt: 0.75, color: HEX.grid }, valign: 'middle', margin: [0, 0.12, 0, 0.12], objectName: 'kpi table' });
  s.addText('Sentabr: 120 ta qoldirilgan qatnashuv sababi', { x: 0.5, y: 4.85, w: 7.3, h: 0.35, fontSize: 15, bold: true, color: C.text2, margin: 0, isTextBox: true, objectName: 'reasons head' });
  [['67', 'Ta’til'], ['29', 'Qatnashmagan'], ['24', 'Sababi yozilmagan']].forEach(([v, l], i) => {
    const x = 0.5 + i * 2.5;
    s.addShape('roundRect', { x, y: 5.3, w: 2.3, h: 1.5, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: 'none' }, objectName: 'reason card ' + (i + 1) });
    s.addText(v, { x: x + 0.2, y: 5.38, w: 1.9, h: 0.8, fontSize: 36, bold: true, color: i ? C.accent2 : C.text2, margin: 0, valign: 'bottom', isTextBox: true, objectName: 'reason value ' + (i + 1) });
    s.addText(l, { x: x + 0.2, y: 6.2, w: 1.9, h: 0.45, fontSize: 14, color: C.text1, margin: 0, valign: 'top', isTextBox: true, objectName: 'reason label ' + (i + 1) });
  });
  const acts = [
    [fa.FaUserCheck, '1. Davomatni tiklash', 'Ta’til va smenaga mos qo‘shimcha darslar. Payvandlash (7) va Ta’minot (5) birinchi navbatda; Sh. Ikramov va I. Rustamov bo‘yicha sabab aniqlansin.'],
    [fa.FaBullseye, '2. Maqsadli o‘qitish: 106 xodim', 'Sifat 78 + Yig‘uv 28: ADM MS, yo‘qotishlar va WPO amaliyoti. 30 kundan keyin shu mezon bilan qayta baho.'],
    [fa.FaDatabase, '3. Yagona natijalar reyestri', 'Davomat, baho, OJT, sertifikat va xarajatni xodim tabeli va kursga bog‘lash (Akademiya, HR, Moliya).'],
  ];
  for (const [i, [Ic, head, body]] of acts.entries()) {
    const y = 1.65 + i * 1.75;
    s.addShape('roundRect', { x: 8.1, y, w: 4.75, h: 1.55, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: 'none' }, objectName: 'action card ' + (i + 1) });
    s.addShape('ellipse', { x: 8.3, y: y + 0.2, w: 0.55, h: 0.55, fill: { color: i === 1 ? C.accent2 : C.text2 }, line: { type: 'none' }, objectName: 'action icon bg ' + (i + 1) });
    s.addImage({ data: await icon(Ic), x: 8.43, y: y + 0.33, w: 0.29, h: 0.29, altText: head, objectName: 'action icon ' + (i + 1) });
    s.addText(head, { x: 9.05, y: y + 0.15, w: 3.65, h: 0.4, fontSize: 15, bold: true, color: C.text2, margin: 0, valign: 'middle', isTextBox: true, objectName: 'action head ' + (i + 1) });
    s.addText(body, { x: 9.05, y: y + 0.55, w: 3.65, h: 0.92, fontSize: 12, color: C.text1, margin: 0, valign: 'top', isTextBox: true, objectName: 'action body ' + (i + 1) });
  }
  s.addNotes('73,9% — sentabrdagi brigadir dars qaydi ulushi (339/459), 90% mezondan 16,1 f.p. past. Bu butun Akademiya KPI yakuni emas. 76,8% kompetensiya bali ≥85% samaradorlik KPI bilan bir xil o‘lchov emas. 120 qoldirilgan qatnashuv 120 nafar xodim degani emas. Choralar — tahliliy taklif, tasdiqlangan topshiriq emas.');

  await pres.writeFile({ fileName: '6_oylik_oqitish_va_kompetensiya_natijalari.pptx' });
  await applyTheme('6_oylik_oqitish_va_kompetensiya_natijalari.pptx', THEME);
}

async function deck1() {
  const pres = new pptxgen();
  const C = setup(pres, PERIOD + ' • Manba: ADM Academy hisobotlari');
  pres.title = '6 oylik o‘qitish: eng muhim xulosalar';
  pres.addSection({ title: 'Xulosa' });
  const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: 'Xulosa' });
  s.addText('6 oylik o‘qitish: eng muhim xulosalar', { placeholder: 'title' });
  s.addText('Qamrov yuqori, ammo sentabrda davomat pasaydi va Sifat yo‘nalishida kompetensiya past', { placeholder: 'sub' });
  const sw = 3.6, sh = 2.45;
  [
    { value: '94,5%', label: 'Brigadirlar o‘qitildi', note: '165 nafardan 156 nafari kamida bir marta' },
    { value: '23 nafar', label: 'Sentabrda darsga kelmagan', note: 'Aprelda 5 nafar edi; qamrov 85,0%gacha tushdi', alert: true },
    { value: '76,8%', label: 'O‘rtacha kompetensiya bali', note: '341 xodim baholandi (585 ball maksimum)' },
    { value: '108 nafar', label: '70%dan past natija', note: 'Sifat 78, Yig‘uv 28 nafar', alert: true },
  ].forEach((d, i) => stat(s, C, { ...d, x: 0.5 + (i % 2) * (sw + 0.3), y: 1.75 + Math.floor(i / 2) * (sh + 0.3), w: sw, h: sh, name: 'key' + (i + 1) }));
  s.addShape('roundRect', { x: 8.35, y: 1.75, w: 4.5, h: 5.2, rectRadius: 0.08, fill: { color: C.text2 }, line: { type: 'none' }, objectName: 'decisions panel' });
  s.addText('Rahbariyat qarori uchun', { x: 8.65, y: 1.95, w: 3.9, h: 0.45, fontSize: 18, bold: true, color: C.background1, margin: 0, isTextBox: true, objectName: 'decisions head' });
  const dec = [
    ['Davomatni tiklash', '23 brigadir uchun qo‘shimcha darslar; sex rahbarlari sababni aniqlasin.'],
    ['106 xodimni qayta o‘qitish', 'Sifat va Yig‘uv: ADM MS, yo‘qotishlar, WPO. 30 kunda qayta baho.'],
    ['Yagona reyestr', 'Davomat, baho, sertifikat va xarajat bitta tizimda.'],
  ];
  for (const [i, [h, b]] of dec.entries()) {
    const y = 2.6 + i * 1.4;
    s.addShape('ellipse', { x: 8.65, y, w: 0.5, h: 0.5, fill: { color: C.accent2 }, line: { type: 'none' }, objectName: 'decision num bg ' + (i + 1) });
    s.addText(String(i + 1), { x: 8.65, y, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: C.background1, align: 'center', valign: 'middle', margin: 0, isTextBox: true, objectName: 'decision num ' + (i + 1) });
    s.addText([{ text: h, options: { bold: true, fontSize: 15, color: C.background1, breakLine: true } }, { text: b, options: { fontSize: 12, color: C.background2 } }],
      { x: 9.35, y: y - 0.05, w: 3.3, h: 1.2, margin: 0, valign: 'top', isTextBox: true, objectName: 'decision text ' + (i + 1) });
  }
  s.addNotes('94,5% — olti oyda kamida bir marta qatnashish, kurs tugatish emas. Sentabrdagi brigadir davomat indikatori 73,9% (reja >90%). Past natijalarning 72,2%i Sifat yo‘nalishida. 70% — tahliliy chegara.');
  await pres.writeFile({ fileName: 'Eng_muhim_xulosalar_1_slayd.pptx' });
  await applyTheme('Eng_muhim_xulosalar_1_slayd.pptx', THEME);
}

(async () => { await deck3(); await deck1(); console.log('ok'); })().catch((e) => { console.error(e); process.exit(1); });
