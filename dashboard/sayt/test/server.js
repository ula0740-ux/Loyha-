// Mahalliy sinov: Google Apps Script muhitining soddalashtirilgan nusxasi.
// Code.gs shu yerda ishga tushadi, index.html esa google.script.run o'rniga /rpc ga murojaat qiladi.
const http = require('http'), fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..');

function makeSheet(name) {
  let cells = [], maxRows = 1000;
  const sh = {
    name,
    getLastRow() { for (let i = cells.length - 1; i >= 0; i--) if (cells[i] && cells[i].some(v => v !== '' && v != null)) return i + 1; return 0; },
    getMaxRows() { return maxRows; },
    insertRowsAfter(_, n) { maxRows += n; },
    setFrozenRows() {},
    getRange(r, c, nr, nc) {
      nr = nr || 1; nc = nc || 1;
      return {
        setValues(v) { for (let i = 0; i < nr; i++) { cells[r - 1 + i] = cells[r - 1 + i] || []; for (let j = 0; j < nc; j++) cells[r - 1 + i][c - 1 + j] = v[i][j]; } return this; },
        getValues() { const o = []; for (let i = 0; i < nr; i++) { const row = []; for (let j = 0; j < nc; j++) { const x = (cells[r - 1 + i] || [])[c - 1 + j]; row.push(x == null ? '' : x); } o.push(row); } return o; },
        clearContent() { for (let i = 0; i < nr; i++) if (cells[r - 1 + i]) for (let j = 0; j < nc; j++) cells[r - 1 + i][c - 1 + j] = ''; return this; },
        setNumberFormat() { return this; }, setFontWeight() { return this; }
      };
    }
  };
  return sh;
}
const sheets = {};
const props = {};
const pad = n => String(n).padStart(2, '0');
const ctx = {
  SpreadsheetApp: { getActive: () => ({ getSheetByName: n => sheets[n] || null, insertSheet: n => (sheets[n] = makeSheet(n)) }) },
  PropertiesService: { getScriptProperties: () => ({ getProperty: k => props[k] || null, setProperty: (k, v) => { props[k] = v; } }) },
  LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
  Utilities: { formatDate(d, tz, fmt) { const t = new Date(d.getTime() + 5 * 3600e3);
    const s = { yyyy: t.getUTCFullYear(), MM: pad(t.getUTCMonth() + 1), dd: pad(t.getUTCDate()), HH: pad(t.getUTCHours()), mm: pad(t.getUTCMinutes()) };
    return fmt.replace('yyyy', s.yyyy).replace('MM', s.MM).replace('dd', s.dd).replace('HH', s.HH).replace('mm', s.mm); } },
  CacheService: { getScriptCache: () => ({ get: () => null, put() {}, remove() {} }) },
  HtmlService: {}, console
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'Code.gs'), 'utf8'), ctx);

const shim = `<script>
(function(){ function mk(h){ return new Proxy({}, {get:function(_,k){
  if(k==='withSuccessHandler') return function(f){ return mk(Object.assign({},h,{s:f})); };
  if(k==='withFailureHandler') return function(f){ return mk(Object.assign({},h,{e:f})); };
  return function(){ var args=[].slice.call(arguments);
    fetch('/rpc',{method:'POST',body:JSON.stringify({fn:k,args:args})}).then(function(r){return r.json();}).then(function(j){
      if(j.error){ h.e && h.e({message:j.error}); } else { h.s && h.s(j.result); } }); };
}}); }
window.google={script:{run:mk({})}}; })();
</script>`;

http.createServer((req, res) => {
  if (req.url.startsWith('/rpc')) {
    let body = ''; req.on('data', c => body += c); req.on('end', () => {
      const { fn, args } = JSON.parse(body); let out;
      try { out = { result: JSON.parse(JSON.stringify(ctx[fn](...args)) ?? 'null') }; }
      catch (e) { out = { error: e.message }; }
      res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(out));
    });
    return;
  }
  if (req.url.startsWith('/xlsx.js')) { res.setHeader('content-type', 'text/javascript'); return res.end(fs.readFileSync(path.join(__dirname, 'node_modules/xlsx/dist/xlsx.full.min.js'))); }
  if (req.url.startsWith('/jszip.js')) { res.setHeader('content-type', 'text/javascript'); return res.end(fs.readFileSync(path.join(__dirname, 'node_modules/jszip/dist/jszip.min.js'))); }
  if (req.url.startsWith('/dump')) { const o = {}; for (const k in sheets) o[k] = sheets[k].getRange(1, 1, sheets[k].getLastRow() || 1, 10).getValues(); res.setHeader('content-type', 'application/json'); return res.end(JSON.stringify(o)); }
  let html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8')
    .replace('<?= showAdmin ?>', 'true')
    .replace('https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js', '/xlsx.js')
    .replace('https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js', '/jszip.js')
    .replace('<script>window.SHOW_ADMIN', shim + '<script>window.SHOW_ADMIN');
  res.setHeader('content-type', 'text/html; charset=utf-8'); res.end(html);
}).listen(process.env.PORT || 8790, () => console.log('ok ' + (process.env.PORT || 8790)));
