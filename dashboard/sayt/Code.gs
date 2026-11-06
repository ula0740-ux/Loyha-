/**
 * ADM JIZZAX AJ — yig'uv paneli (Google Apps Script veb-ilova).
 *
 * Ma'lumot ombori: shu skript bog'langan Google jadval. Varaqlar o'zi yaratiladi.
 *   Avto       — har bir avtomobil (VIN) bitta qator: 630 va 700 sanasi. VIN bir marta sanaladi.
 *   Kunlik     — kun / sex / model bo'yicha 630 va 700 soni (Avto'dan hisoblanadi).
 *   MQS        — har bir nuqson bitta qator.
 *   Reja       — oylik reja (CKD, SKD).
 *   Grafik     — oyning ish grafigi: 'h:soatlar' va ixtiyoriy ';p:kunlik reja (dona)' (bo'sh = soatdan hisoblanadi).
 *   Tuzatish   — qo'lda tuzatilgan kunlik raqamlar (Kunlik ustidan yoziladi).
 *   OylikQolda — Excel bo'lmagan o'tgan oylar uchun qo'lda kiritilgan oylik jami.
 *   Tarjima    — inglizcha nuqson nomi -> o'zbekcha.
 *   Fayllar    — yuklangan fayllar jurnali.  Tarix — o'zgarishlar tarixi.
 *
 * Excel fayllarning o'zi saqlanmaydi: brauzer ularni o'qiydi va faqat natija yoziladi.
 */

var HEAD = {
  Avto: ['vin', 'sex', 'model', 'modifikatsiya', 'rang', 'sana630', 'sana700', 'rastamojen'],
  Kunlik: ['sana', 'sex', 'model', 'e630', 'e700'],
  MQS: ['sana', 'sex', 'model', 'team', 'nuqson', 'fault', 'detal', 'vin', 'holat'],
  Reja: ['oy', 'sex', 'reja'],
  Grafik: ['oy', 'sex', 'kunlar'],
  Tuzatish: ['sana', 'sex', 'model', 'tur', 'son'],
  OylikQolda: ['oy', 'sex', 'e630', 'e700', 'mqs'],
  Tarjima: ['fault', 'uz'],
  Fayllar: ['vaqt', 'nom', 'tur', 'sex', 'sana', 'qator', 'yangi', 'kim'],
  Tarix: ['vaqt', 'kim', 'amal', 'tafsilot']
};

var TARJIMA0 = [
  ['TOUCH MARK NOT', "Tortish belgisi qo'yilmagan"], ['INCOMPLETE MESH', "To'liq ulanmagan"],
  ['INSTALL DEFECT', "O'rnatishdagi nuqson"], ['NOT FIXING', 'Mahkamlanmagan'], ['DAMAGE', 'Shikastlanish'],
  ['CLIP CLAMP NOT INSTALL', "Qisqich o'rnatilmagan"], ['WRONG INSTALL', "Noto'g'ri o'rnatilgan"],
  ['SCRATCH', 'Chizilgan'], ['PAINT CHIPPING', "Bo'yoqning shikastlanishi"], ['CLEAR DEFECT', 'Laklashdagi nuqsonlar'],
  ['POLISH MARK', 'Polirovka izi'], ['BENT', 'Egilib qolish'], ['CLEAN UP', 'Ifloslanish'], ['OTHER DEFECTS', 'Boshqa nuqsonlar']
];

/* ------------------------------------------------------------------ veb */

function doGet(e) {
  var t = HtmlService.createTemplateFromFile('index');
  t.showAdmin = !!(e && e.parameter && e.parameter.boshqaruv !== undefined);
  return t.evaluate()
    .setTitle('ADM JIZZAX AJ — yig\'uv paneli')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/* ------------------------------------------------------------------ varaqlar */

function sheet_(name) {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.getRange(1, 1, sh.getMaxRows(), HEAD[name].length).setNumberFormat('@');
    sh.getRange(1, 1, 1, HEAD[name].length).setValues([HEAD[name]]).setFontWeight('bold');
    sh.setFrozenRows(1);
    if (name === 'Tarjima') sh.getRange(2, 1, TARJIMA0.length, 2).setValues(TARJIMA0);
  }
  return sh;
}

var MEM_ = {};
function rows_(name) {
  if (MEM_[name]) return MEM_[name].map(function (r) { return r.slice(); });
  var out = rows0_(name); MEM_[name] = out; return out.map(function (r) { return r.slice(); });
}
function rows0_(name) {
  var sh = sheet_(name), n = sh.getLastRow();
  if (n < 2) return [];
  return sh.getRange(2, 1, n - 1, HEAD[name].length).getValues().map(function (r) {
    return r.map(function (v) {
      if (v === null || v === undefined) return '';
      if (Object.prototype.toString.call(v) === '[object Date]') return Utilities.formatDate(v, 'Asia/Tashkent', 'yyyy-MM-dd HH:mm').replace(' 00:00', '');
      return String(v);
    });
  });
}

function write_(name, data) {
  delete MEM_[name]; bust_();
  var sh = sheet_(name), w = HEAD[name].length, n = sh.getLastRow();
  if (n > 1) sh.getRange(2, 1, n - 1, w).clearContent();
  if (!data.length) return;
  if (sh.getMaxRows() < data.length + 1) sh.insertRowsAfter(sh.getMaxRows(), data.length + 1 - sh.getMaxRows());
  sh.getRange(2, 1, data.length, w).setNumberFormat('@').setValues(data.map(function (r) {
    return r.map(function (v) {
      if (v === null || v === undefined) return '';
      if (Object.prototype.toString.call(v) === '[object Date]') return Utilities.formatDate(v, 'Asia/Tashkent', 'yyyy-MM-dd HH:mm').replace(' 00:00', '');
      return String(v);
    });
  }));
}

function append_(name, data) {
  if (!data.length) return;
  delete MEM_[name]; if (name !== 'Tarix') bust_();
  var sh = sheet_(name), w = HEAD[name].length, n = sh.getLastRow();
  if (sh.getMaxRows() < n + data.length) sh.insertRowsAfter(sh.getMaxRows(), n + data.length - sh.getMaxRows());
  sh.getRange(n + 1, 1, data.length, w).setNumberFormat('@').setValues(data.map(function (r) {
    return r.map(function (v) {
      if (v === null || v === undefined) return '';
      if (Object.prototype.toString.call(v) === '[object Date]') return Utilities.formatDate(v, 'Asia/Tashkent', 'yyyy-MM-dd HH:mm').replace(' 00:00', '');
      return String(v);
    });
  }));
}

function now_() { return Utilities.formatDate(new Date(), 'Asia/Tashkent', 'yyyy-MM-dd HH:mm'); }

function log_(kim, amal, tafsilot) {
  append_('Tarix', [[now_(), kim || '—', amal, tafsilot || '']]);
}

/* ------------------------------------------------------------------ PIN */

function hasPin() {
  return !!PropertiesService.getScriptProperties().getProperty('PIN');
}

function setPin(oldPin, newPin, kim) {
  var props = PropertiesService.getScriptProperties();
  var cur = props.getProperty('PIN');
  if (cur && String(oldPin) !== cur) throw new Error('Eski PIN noto\'g\'ri.');
  if (!/^\S{4,32}$/.test(String(newPin || ''))) throw new Error('PIN kamida 4 belgi bo\'lsin, bo\'sh joysiz.');
  props.setProperty('PIN', String(newPin));
  log_(kim, cur ? 'PIN o\'zgartirildi' : 'PIN o\'rnatildi', '');
  return true;
}

function pin_(pin) {
  var cur = PropertiesService.getScriptProperties().getProperty('PIN');
  if (!cur) throw new Error('Avval boshqaruv PIN-kodini o\'rnating.');
  if (String(pin) !== cur) throw new Error('PIN noto\'g\'ri.');
}

function login(pin) { pin_(pin); return true; }

/* ------------------------------------------------------------------ o'qish */

/** Panel uchun hamma narsa (MQS tafsilotlarisiz). */
function bust_() { try { CacheService.getScriptCache().remove('getData'); } catch (e) {} }
function getData() {
  var c = CacheService.getScriptCache(), hit = null;
  try { hit = c.get('getData'); } catch (e) {}
  if (hit) { try { var o = JSON.parse(hit); o.bugun = Utilities.formatDate(new Date(), 'Asia/Tashkent', 'yyyy-MM-dd'); return o; } catch (e) {} }
  var d;
  try { d = getData0_(); } catch (e) { throw new Error('Server: ' + e.message + ' | ' + String(e.stack || '').split('\n').slice(0, 3).join(' | ')); }
  try { var j = JSON.stringify(d); if (j.length < 95000) c.put('getData', j, 600); } catch (e) {}
  return d;
}
function getData0_() {
  var kun = rows_('Kunlik');
  var tuz = rows_('Tuzatish');
  // tuzatishlarni qo'llash: kalit sana|sex|model
  var map = {};
  kun.forEach(function (r) { map[r[0] + '|' + r[1] + '|' + r[2]] = { s: r[0], x: r[1], m: r[2], a: +r[3] || 0, b: +r[4] || 0, t: '' }; });
  tuz.forEach(function (r) {
    var k = r[0] + '|' + r[1] + '|' + r[2];
    var o = map[k] || (map[k] = { s: r[0], x: r[1], m: r[2], a: 0, b: 0, t: '' });
    if (r[3] === '630') o.a = +r[4] || 0; else o.b = +r[4] || 0;
    o.t = 'tuzatildi';
  });
  var days = Object.keys(map).map(function (k) { var o = map[k]; return [o.s, o.x, o.m, o.a, o.b, o.t]; });

  var mqsDay = {};
  rows_('MQS').forEach(function (r) {
    var d = r[0].slice(0, 10), k = d + '|' + r[1];
    var o = mqsDay[k] || (mqsDay[k] = [d, r[1], 0, 0, 0]);
    o[2]++; if (r[3] === 'Production') o[3]++; else o[4]++;
  });

  return {
    days: days,                                   // [sana, sex, model, 630, 700, belgi]
    mqsDays: Object.keys(mqsDay).map(function (k) { return mqsDay[k]; }), // [sana, sex, jami, ishlab ch., ta'minot]
    reja: rows_('Reja'),
    grafik: rows_('Grafik'),
    oylik: rows_('OylikQolda'),
    fayllar: rows_('Fayllar').slice(-60).reverse(),
    hasPin: hasPin(),
    bugun: Utilities.formatDate(new Date(), 'Asia/Tashkent', 'yyyy-MM-dd')
  };
}

/** MQS: tanlangan davr bo'yicha yig'ma (sana 'YYYY-MM-DD', oraliq ikkala chekka bilan). */
function getMqs(from, to, sex) {
  var tr = {};
  rows_('Tarjima').forEach(function (r) { if (r[1]) tr[r[0].trim().toUpperCase()] = r[1]; });
  var name = function (r) { return r[4] || tr[(r[5] || '').trim().toUpperCase()] || r[5] || '—'; };
  var rows = rows_('MQS').filter(function (r) {
    var d = r[0].slice(0, 10);
    return d >= from && d <= to && (!sex || sex === 'ALL' || r[1] === sex);
  });
  var cnt = function (list, f, n, skip) {
    var c = {};
    list.forEach(function (r) { var k = f(r); if (k && k !== skip) c[k] = (c[k] || 0) + 1; });
    return Object.keys(c).map(function (k) { return [k, c[k]]; }).sort(function (a, b) { return b[1] - a[1]; }).slice(0, n);
  };
  var uniq = function (list) { var s = {}; list.forEach(function (r) { if (r[7]) s[r[7]] = 1; }); return Object.keys(s).length; };
  var P = rows.filter(function (r) { return r[3] === 'Production'; });
  var T = rows.filter(function (r) { return r[3] !== 'Production'; });
  var other = 'Boshqa nuqsonlar';
  var byDay = {};
  rows.forEach(function (r) { var d = r[0].slice(0, 10); byDay[d] = (byDay[d] || 0) + 1; });
  return {
    from: from, to: to, total: rows.length, cars: uniq(rows),
    open: rows.filter(function (r) { return r[8] === 'open'; }).length,
    P: P.length, Pc: uniq(P), T: T.length, Tc: uniq(T),
    topP: cnt(P, name, 3, other), topT: cnt(T, name, 3, other), top: cnt(rows, name, 3, other),
    other: rows.filter(function (r) { return name(r) === other; }).length,
    models: cnt(rows, function (r) { return r[2]; }, 8),
    parts: cnt(rows, function (r) { return r[6]; }, 6),
    byDay: byDay,
    list: rows.slice(0, 300).map(function (r) {
      return [r[0].slice(11, 16), r[1], r[2], r[3] === 'Production' ? 'Ishlab chiqarish' : "Ta'minot", name(r), r[6], r[8]];
    })
  };
}

/* ------------------------------------------------------------------ yuklash */

/**
 * 630 yoki 700 fayli. p = {pin, kim, tur:'630'|'700', sex:'CKD'|'SKD', sana:'YYYY-MM-DD',
 *   baza:bool, fayl, rows:[[vin, model, modifikatsiya, rang, rastamojen]]}
 * VIN birinchi marta qaysi sanada ko'rinsa, o'sha kunga yoziladi. Shu sana uchun qayta yuklansa —
 * o'sha sananing avvalgi yozuvlari tozalanib, yangi fayl bilan almashadi.
 * baza = boshlang'ich qoldiq: VIN'lar eslab qolinadi, lekin hech bir kunga sanalmaydi.
 */
function uploadEvent(p) {
  pin_(p.pin);
  var col = p.tur === '700' ? 6 : 5;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(p.sana)) throw new Error('Sana noto\'g\'ri.');
  var stamp = p.baza ? 'baza' : p.sana;
  var lock = LockService.getScriptLock(); lock.waitLock(30000);
  try {
    var data = rows_('Avto'), idx = {};
    var oldi = {};
    data.forEach(function (r, i) {
      if (r[1] === p.sex && r[col] === stamp) { r[col] = ''; oldi[r[0]] = 1; }   // shu sana qayta yuklanmoqda
      idx[r[0]] = i;
    });
    var yangi = 0, takror = 0, qayta = 0;
    p.rows.forEach(function (x) {
      var vin = String(x[0] || '').trim(); if (!vin) return;
      var i = idx[vin];
      if (i === undefined) {
        var r = [vin, p.sex, x[1] || '', x[2] || '', x[3] || '', '', '', x[4] ? '1' : '0'];
        r[col] = stamp; idx[vin] = data.length; data.push(r); yangi++;
      } else {
        var row = data[i];
        row[7] = x[4] ? '1' : row[7];
        if (!row[col]) { row[col] = stamp; if (oldi[vin]) qayta++; else yangi++; }
        else if (row[col] !== 'baza' && stamp !== 'baza' && stamp < row[col]) { row[col] = stamp; yangi++; } // eski fayl keyin yuklandi
        else takror++;
      }
    });
    write_('Avto', data);
    rebuildKunlik_(data);
    append_('Fayllar', [[now_(), p.fayl || '', p.tur, p.sex, p.baza ? 'boshlang\'ich qoldiq' : p.sana, p.rows.length, yangi, p.kim || '']]);
    log_(p.kim, p.tur + ' yuklandi', (p.fayl || '') + ': ' + p.rows.length + ' qator, ' + yangi + ' yangi');
    return { jami: p.rows.length, yangi: yangi, takror: takror, qayta: qayta };
  } finally { lock.releaseLock(); }
}

function rebuildKunlik_(data) {
  var agg = {};
  data.forEach(function (r) {
    [[5, 3], [6, 4]].forEach(function (c) {
      var s = r[c[0]]; if (!s || s === 'baza') return;
      var k = s + '|' + r[1] + '|' + r[2];
      var o = agg[k] || (agg[k] = [s, r[1], r[2], 0, 0]);
      o[c[1]]++;
    });
  });
  write_('Kunlik', Object.keys(agg).sort().map(function (k) { return agg[k]; }));
}

/** MQS fayli. p = {pin, kim, fayl, rows:[[sana, sex, model, team, nuqson, fault, detal, vin, holat]]}
 *  Faylda bor sanalar (sex bilan) to'liq almashtiriladi. */
function uploadMqs(p) {
  pin_(p.pin);
  var lock = LockService.getScriptLock(); lock.waitLock(30000);
  try {
    var keys = {};
    p.rows.forEach(function (r) { keys[String(r[0]).slice(0, 10) + '|' + r[1]] = 1; });
    var old = rows_('MQS').filter(function (r) { return !keys[r[0].slice(0, 10) + '|' + r[1]]; });
    write_('MQS', old.concat(p.rows));
    var sanalar = Object.keys(keys).map(function (k) { return k.split('|')[0]; }).sort();
    append_('Fayllar', [[now_(), p.fayl || '', 'MQS', '', sanalar.join(', '), p.rows.length, p.rows.length, p.kim || '']]);
    log_(p.kim, 'MQS yuklandi', (p.fayl || '') + ': ' + p.rows.length + ' nuqson, ' + sanalar.join(', '));
    return { jami: p.rows.length, sanalar: sanalar };
  } finally { lock.releaseLock(); }
}

/* ------------------------------------------------------------------ boshqaruv */

function saveReja(pin, kim, oy, sex, son) {
  pin_(pin);
  var data = rows_('Reja').filter(function (r) { return !(r[0] === oy && r[1] === sex); });
  if (String(son) !== '') data.push([oy, sex, String(Math.max(0, Math.round(+son || 0)))]);
  write_('Reja', data);
  log_(kim, 'Reja', oy + ' ' + sex + ': ' + son);
  return true;
}

function saveGrafik(pin, kim, oy, sex, kunlar) {
  pin_(pin);
  if (!/^[21QXD](,[21QXD]){27,30}$/.test(kunlar) && !/^h:\d{1,2}(\.5)?(,\d{1,2}(\.5)?){27,30}(;p:(\d{1,5})?(,(\d{1,5})?){27,30})?$/.test(kunlar)) throw new Error('Grafik noto\'g\'ri.');
  var data = rows_('Grafik').filter(function (r) { return !(r[0] === oy && r[1] === sex); });
  data.push([oy, sex, kunlar]);
  write_('Grafik', data);
  log_(kim, 'Ish grafigi', oy + ' ' + sex);
  return true;
}

/** list = [{sana, sex, model, tur:'630'|'700', son}] ; son '' — tuzatishni olib tashlash */
function saveTuzatish(pin, kim, list) {
  pin_(pin);
  var data = rows_('Tuzatish');
  list.forEach(function (t) {
    data = data.filter(function (r) { return !(r[0] === t.sana && r[1] === t.sex && r[2] === t.model && r[3] === t.tur); });
    if (String(t.son) !== '') data.push([t.sana, t.sex, t.model, t.tur, String(Math.max(0, Math.round(+t.son || 0)))]);
  });
  write_('Tuzatish', data);
  log_(kim, 'Natija tuzatildi', list.map(function (t) { return t.sana + ' ' + t.sex + ' ' + t.model + ' ' + t.tur + '=' + t.son; }).join('; '));
  return true;
}

function saveOylik(pin, kim, o) {
  pin_(pin);
  var data = rows_('OylikQolda').filter(function (r) { return !(r[0] === o.oy && r[1] === o.sex); });
  if (o.e630 !== '' || o.e700 !== '' || o.mqs !== '') data.push([o.oy, o.sex, o.e630, o.e700, o.mqs]);
  write_('OylikQolda', data);
  log_(kim, 'Oy qo\'lda kiritildi', o.oy + ' ' + o.sex + ': 630=' + o.e630 + ', 700=' + o.e700 + ', MQS=' + o.mqs);
  return true;
}

function getTarjima() {
  var have = {}, out = [];
  rows_('Tarjima').forEach(function (r) { have[r[0].toUpperCase()] = 1; out.push(r); });
  rows_('MQS').forEach(function (r) {
    var f = (r[5] || '').trim().toUpperCase();
    if (f && !r[4] && !have[f]) { have[f] = 1; out.push([f, '']); }
  });
  return out;
}

function saveTarjima(pin, kim, list) {
  pin_(pin);
  write_('Tarjima', list.filter(function (r) { return r[0]; }));
  log_(kim, 'Tarjima saqlandi', list.length + ' ta nom');
  return true;
}

function getTarix(pin) {
  pin_(pin);
  return rows_('Tarix').slice(-300).reverse();
}

/** Bitta kunning model bo'yicha raqamlari (tuzatish oynasi uchun). */
function getDay(sana, sex) {
  var out = {};
  rows_('Kunlik').forEach(function (r) { if (r[0] === sana && r[1] === sex) out[r[2]] = { a: +r[3] || 0, b: +r[4] || 0, ta: '', tb: '' }; });
  rows_('Tuzatish').forEach(function (r) {
    if (r[0] === sana && r[1] === sex) {
      var o = out[r[2]] || (out[r[2]] = { a: 0, b: 0, ta: '', tb: '' });
      if (r[3] === '630') o.ta = r[4]; else o.tb = r[4];
    }
  });
  return out;
}
