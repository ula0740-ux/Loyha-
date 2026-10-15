"""HRM 2026 · Sentabr: builds HRM_2026_sentabr.html from HRM_2026_zavod_shablon.html (the approved template)
with the content of HRM_2026_Sentabrgacha_shablon_2.pptx (13 slides).

Template slides reused as they are (same content in the new pptx): cover, contents, 05 Electronic application
(intro + 3), 06 Corporate culture (intro + 1), 07 Discipline (intro + 2). Sections are renumbered 01..03.
New: two ITR KPI dashboard slides (pptx slides 9-10) built with the template's own blocks.
Run: python3 build_sentabr.py
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
src = (HERE / 'HRM_2026_zavod_shablon.html').read_text(encoding='utf-8')

ORDER = [0, 1, 20, 21, 22, 'K', 24, 25, 26, 27, 28]   # user's order: e-application summary, process & benefit, then the KPI dashboard (salary table removed)
N = len(ORDER)
RENUM = {'05': '01', '06': '02', '07': '03'}
KPI_TITLE = '01 · ИТР ходимлари KPI'

# ---------------- slide sections (markup) ----------------
starts = [m.start() for m in re.finditer(r'  <section class="slide', src)]
main_end = src.index('</main>')
secs = [src[a:(starts[k + 1] if k + 1 < len(starts) else main_end)] for k, a in enumerate(starts)]
assert len(secs) == 29


def renum(t):
    for a, b in RENUM.items():
        t = t.replace(f'data-title="{a} · ', f'data-title="{b} · ')
        t = t.replace(f'<div class="ghost" aria-hidden="true">{a}</div>', f'<div class="ghost" aria-hidden="true">{b}</div>')
        t = t.replace(f'<b>{a}</b> ', f'<b>{b}</b> ')
    return t


out_secs = []
for j, k in enumerate(ORDER):
    if isinstance(k, str):   # new KPI dashboard slide: same shell as the corporate-culture data slide
        t = secs[21].replace('data-title="05 · Электрон ариза тизими"', f'data-title="{KPI_TITLE}"')
        t = t.replace('<div class="ghost" aria-hidden="true">05</div>', '<div class="ghost" aria-hidden="true">KPI</div>')
        old = 21
    else:
        t, old = renum(secs[k]), k
    t = t.replace(f'data-i="{old}"', f'data-i="{j}"')
    t = re.sub(r'aria-label="\d+ / 29:', f'aria-label="{j + 1} / {N}:', t)
    t = t.replace('Август 2026', 'Сентабр 2026').replace('Сентябрь 2026', 'Сентабр 2026')
    out_secs.append(t)
html = src[:starts[0]] + ''.join(out_secs) + src[main_end:]

# ---------------- SLIDES data ----------------
a = html.index('const SLIDES = [') + len('const SLIDES = [')
b = html.index('\n  ];', a)
ents = re.split(r'\n\n(?=    \{ t: )', html[a:b].strip('\n'))
assert len(ents) == 29

ents[0] = ents[0].replace('Август 2026', 'Сентабр 2026')
ents[1] = re.sub(r"grid\('repeat\(4,minmax\(0,1fr\)\)'.*?'align-content:center'\)",
    lambda m: """grid('repeat(3,minmax(0,1fr))', [['01', 'Электрон ариза тизими', '8 та ариза тури электрон шаклда · 2 та стандарт · ИТР KPI дашборди'], ['02', 'Корпоратив маданият', 'Коммуникациялар · Сентябрь тадбирлари · Табель сўровномаси'], ['03', 'Интизом бўйича', '2025 ва 2026-йил солиштирмаси · ички меҳнат тартиби қоидалари янги таҳрири']]
        .map(([n, t, d]) => card('', `<div style="font-size:calc(var(--u)*4.2);font-weight:900;color:var(--accent);line-height:1">${n}</div><div class="rule" style="margin:calc(var(--u)*.8) 0"></div><div class="txt" style="font-size:calc(var(--u)*1.5);line-height:1.25"><b>${t}</b></div><p class="note" style="margin-top:auto;font-size:calc(var(--u)*.95)">${d}</p>`, 'grow')).join(''), 'align-items:stretch')""",
    ents[1], flags=re.S)
assert "'03', 'Интизом бўйича'" in ents[1], 'contents not replaced'

ents[27] = ents[27].replace("c: ['Ходим 2025', 'Ходим 2026', 'Ҳолат 2025', 'Ҳолат 2026']", "c: ['Ходим<br>2025', 'Ходим<br>2026', 'Ҳолат<br>2025', 'Ҳолат<br>2026']")
assert 'Ходим<br>2025' in ents[27]
for k, (o, n) in zip((20, 24, 26), RENUM.items()):
    ents[k] = ents[k].replace(f"hero('{o}'", f"hero('{n}'")

# ITR KPI dashboard (pptx slides 9-10), split into two readable slides
POS = [('Мастер', 57, 16, 3, 6, 25, '97,8%'), ('Бўлинма бошлиғи', 60, 2, 1, 6, 9, '98,9%'), ('Бўлим бошлиғи', 35, 4, 0, 3, 7, '98,2%'),
       ('Мастер (GL)', 20, 2, 1, 1, 4, '98,7%'), ('Муҳандис', 50, 0, 1, 0, 1, '99,3%'), ('Харид бўйича муҳандис', 24, 0, 0, 1, 1, '99,8%')]
UNITS = [  # name, sub-row, Jul, Aug, Sep, 3 months, delta
    ('1. Маҳаллийлаштириш ва етказиб берувчиларни ривожл. бошқ.', 0, '100%', '100%', '99,4%', 99.8, '▼ −0,6'),
    ('2. Молия ва бухгалтерия дирекцияси', 0, '100%', '97,9%', '97,7%', 98.6, '▼ −0,2'),
    ('3. Харид қилиш ва таъминот тизими бошқармаси', 0, '98,7%', '96,5%', '96,0%', 97.1, '▼ −0,5'),
    ('4. Стратегик режалаштириш ва ривожлантириш бошқармаси', 0, '100%', '96,2%', '92,8%', 96.3, '▼ −3,4'),
    ('5. Тажриба-конструкторлик ишлари, лойиҳалаш … бошқармаси', 0, '97,3%', '97,9%', '93,5%', 96.2, '▼ −4,4'),
    ('6. Дирекция', 0, '92,6%', '95,0%', '98,2%', 95.2, '▲ +3,2'),
    ('7. Ходимларни бошқариш ва ривожлантириш дирекцияси', 0, '92,0%', '95,8%', '95,7%', 94.4, '▼ −0,1'),
    ('8. Канцелярия бўлинмаси', 0, '80,0%', '100%', '100%', 93.3, '■ 0'),
    ('9. Ишлаб чиқариш бошқармаси', 0, '91,6%', '87,9%', '85,8%', 87.9, '▼ −2,1'),
    ('Ишлаб чиқаришни назорат қилиш бўлими', 1, '100%', '100%', '100%', 100, '■ 0'),
    ('Йиғув цехи', 1, '83,3%', '82,2%', '100%', 89.6, '▲ +17,8'),
    ('Пайвандлаш цехи', 1, '88,7%', '87,2%', '83,8%', 86.6, '▼ −3,4'),
    ('СКД цехи', 1, '100%', '93,0%', '75,9%', 85.3, '▼ −17,1'),
    ('Бўёқлаш цехи', 1, '—', '82,7%', '82,6%', 82.7, '▼ −0,1'),
    ('Ишлаб чиқаришни мувофиқлаштириш', 1, '95,0%', '75,0%', '75,0%', 81.7, '■ 0'),
    ('10. Сифат назорати ва кафолоти бошқармаси', 0, '81,1%', '96,6%', '85,2%', 87.5, '▼ −11,4'),
    ('11. Хавфсизлик хизмати', 0, '100%', '84,6%', '76,9%', 86.8, '▼ −7,7'),
    ('12. Ташқи алоқалар ва давлат ҳокимияти орг. … бошқармаси', 0, '88,9%', '88,9%', '80,0%', 85.7, '▼ −8,9'),
]
js_pos = ',\n        '.join(f"['{p}', '{n}', '{a}', '{b}', '{c}', '<b>{t}</b>', '<b>{k}</b>']" for p, n, a, b, c, t, k in POS)
js_units = ',\n        '.join(f"[{repr(u)}, {s}, '{a}', '{b}', '{c}', {v}, '{d}']" for u, s, a, b, c, v, d in UNITS)
# ITR KPI dashboard: one slide exactly as in the pptx (two panels, no extra charts)
def jsq(t): return "'" + t.replace("\\", "\\\\").replace("'", "\\'") + "'"
pos_rows = ''.join(
    "<tr class=\"%s\"><td>%s</td><td class=\"r\">%s</td>%s<td class=\"r tot\">%s</td><td class=\"r\">%s</td></tr>" % (
        'hot' if p == 'Мастер' else '', ('<b>%s</b>' % p) if p == 'Мастер' else p, n,
        ''.join('<td class="r %s">%s</td>' % ('z' if v == 0 else 'b', v) for v in (a, b, c)), t, k)
    for p, n, a, b, c, t, k in POS)
pos_table = ('<table class="tb kp"><thead><tr><th></th><th></th><th class="grp" colspan="4">Тўлиқ KPI олмаганлар, нафар</th><th></th></tr>'
             '<tr><th>Лавозим</th><th class="r">Ходим*</th><th class="r">Июль</th><th class="r">Авг</th><th class="r">Сен</th><th class="r">Жами</th><th class="r">3 ой KPI</th></tr></thead><tbody>'
             + pos_rows + '<tr class="tot"><td><b>Жами ИТР</b></td><td class="r">523</td><td class="r b">44</td><td class="r b">21</td><td class="r b">27</td><td class="r tot">92</td><td class="r">98,8%</td></tr></tbody></table>')
def pct(v): return float(v.replace('%', '').replace(',', '.')) if v not in ('—',) else 100.0
def cell(v): return '<td class="r%s">%s</td>' % (' b' if v != '—' and pct(v) < 85 else '', v)
def bar(v):
    c = 'linear-gradient(90deg,var(--green),var(--cyan))' if v >= 95 else 'linear-gradient(90deg,var(--blue),var(--cyan))' if v >= 85 else 'linear-gradient(90deg,var(--orange),var(--amber))'
    return '<span class="kb"><i style="--w:%.1f%%;background:%s"></i></span><b>%s%%</b>' % ((v - 70) / 30 * 100, c, ('%.1f' % v).replace('.', ',').replace(',0', '') if v == 100 else ('%.1f' % v).replace('.', ','))
def dl(d): return '<span class="dl %s">%s</span>' % ('up' if d[0] == '▲' else 'dn' if d[0] == '▼' else '', d)
unit_rows = ''.join(
    '<tr class="%s"><td class="%s">%s</td>%s%s%s<td class="kbc">%s</td><td class="r">%s</td></tr>' % (
        'grp' if u.startswith('9.') else '', 'sub' if sub else '', ('↳ ' if sub else '') + (('<b>%s</b>' % u) if u.startswith('9.') else u),
        cell(a), cell(b), cell(c), bar(v), dl(d))
    for u, sub, a, b, c, v, d in UNITS)
unit_table = ('<table class="tb kr"><thead><tr><th>Бўлинма / цех</th><th class="r">Июль</th><th class="r">Авг</th><th class="r">Сен</th><th>3 ой (шкала 70–100%)</th><th class="r">Δ Сен/Авг</th></tr></thead><tbody>'
              + unit_rows + '<tr class="tot"><td><b>Жами корхона (kpi.adm.uz)</b></td><td class="r">95,6%</td><td class="r">95,5%</td><td class="r">93,2%</td><td class="kbc">' + bar(94.7) + '</td><td class="r">' + dl('▼ −2,3') + '</td></tr></tbody></table>')
left = ('<span class="cap">Лавозимлар кесимида — тўлиқ KPI олмаганлар сони</span>'
        '<p class="note" style="margin:0 0 calc(var(--u)*.5)">Энг кўп ходимли лавозимлар (асл номлари) · KPI натижаси мақсаддан паст бўлган ходимлар, нафар</p>'
        + pos_table + '<p class="note" style="margin-top:auto"><i>* Ходим — Сентябрь ҳолатига. 3 ой KPI — ходимлар бўйича ўртача бажарилиш (натижа ÷ мақсад). 3 ой давомида 100% бажарган 4 та лавозим (Мутахассис, Омбор мудири, Бухгалтер, Муҳандис технолог) кўрсатилмаган.</i></p>')
right = ('<div style="display:flex;justify-content:space-between;align-items:baseline;gap:1em"><span class="cap">Бўлинмалар рейтинги — KPI (Факт ÷ Режа), %</span><span class="note" style="white-space:nowrap">Манба: kpi.adm.uz · Report department</span></div>'
         + unit_table + '<p class="note" style="margin-top:auto"><i>Изоҳ: СКД, Бўёқлаш, Пайвандлаш цехлари ҳамда Сифат назорати ва кафолоти бошқармасида KPI натижалари бўлим ва цех бошлиқлари томонидан текширилганлиги сабабли бажарилиш 100% дан паст. 3 ой давомида 100% бажарган 4 та бўлинма рейтингга киритилмаган.</i></p>')
K = ("    { t: 'ИТР ходимлари KPI бажарилиши: <em>3 ойлик дашборд</em>', s: '«ADM JIZZAKH» АЖ · Июль — Сентябрь 2026 · 576 ИТР ходими, улардан 465 нафари 3 ойда ҳам ишлаган', "
     "layout: 'grid-template-columns:minmax(0,1fr) minmax(0,1.62fr)', body: () =>\n      card('', " + jsq(left) + ", 'grow') + card('', " + jsq(right) + ", 'grow') },")

new_ents = [K if k == 'K' else ents[k] for k in ORDER]
for i, e in enumerate(new_ents):   # every entry ends with a comma
    if not e.rstrip().endswith(','): new_ents[i] = e.rstrip() + ','
html = html[:a] + '\n' + '\n\n'.join(new_ents) + html[b:]
html = html.replace('var SECS = [["01", "Ишга қабул ва адаптация"], ["02", "Самарадорлик ва KPI"], ["03", "Ўқитишлар"], ["04", "Grading тизими"], ["05", "Электрон ариза тизими"], ["06", "Корпоратив маданият ва коммуникациялар"], ["07", "Интизом бўйича"]];',
                    'var SECS = [["01", "Электрон ариза тизими"], ["02", "Корпоратив маданият ва коммуникациялар"], ["03", "Интизом бўйича"]];')

# ---------------- chrome ----------------
html = html.replace('<b id="curNum">01</b> / 29</span>', f'<b id="curNum">01</b> / {N}</span>')
html = html.replace('<title>HRM Ҳисоботи 2026</title>', '<title>HRM Ҳисоботи 2026 · Сентабр</title>')
# drop photos only the removed adaptation slide used
for key in ('ad1', 'ad2', 'ad3', 'ad4'):
    html = re.sub(r'"%s": "data:image/[a-z]+;base64,[^"]*",?\s*' % key, '', html)
# KPI dashboard styles (template tokens only)
css = """
/* ---- ITR KPI dashboard (Sentabr) ---- */
.kb{display:inline-block;width:calc(var(--u)*9);height:calc(var(--u)*.62);border-radius:99px;background:rgba(255,255,255,.08);vertical-align:middle;margin-right:calc(var(--u)*.6);overflow:hidden}
.kb i{display:block;height:100%;width:var(--w);border-radius:inherit;transform-origin:left;animation:kbIn 1.3s var(--out) .35s both;box-shadow:0 0 12px rgba(95,225,255,.35)}
@keyframes kbIn{from{transform:scaleX(0)}}
.tb td.kbc{white-space:nowrap}
.vb .x{line-height:1.15}
.tb.kp th.grp{text-align:center;color:var(--cyan);border-bottom:1px solid var(--line);font-weight:700}
.tb.kp td{padding-top:calc(var(--u)*.55);padding-bottom:calc(var(--u)*.55)}
.tb.kp td.z{color:rgba(170,185,203,.45)}.tb .b{font-weight:800}
.tb.kp td.tot{color:var(--orange);font-weight:900}
.tb.kr tr.grp td{background:rgba(46,168,255,.10)}
.tb.kr tr.tot .kb i{background:linear-gradient(90deg,var(--orange),var(--amber))!important}
.tb td.sub{padding-left:calc(var(--u)*1.6);color:var(--muted);font-size:.94em}
.dl{font-family:var(--mono);font-weight:700;white-space:nowrap}
.dl.up{color:var(--green)}.dl.dn{color:var(--orange)}
@media (prefers-reduced-motion:reduce){.kb i{animation:none}}
"""
html = html.replace('</style>', css + '</style>', 1)

assert 'Август 2026' not in html, 'old report month left'
(HERE / 'HRM_2026_sentabr.html').write_text(html, encoding='utf-8')
print('HRM_2026_sentabr.html', len(html) // 1024, 'KB,', N, 'slides')
