# SPQRC маълумотлари (Ноябрь 2026) → HRM 2026 shabloni uslubida taqdimot:
# muqova, har sex uchun umumiy slayd + 5 ta yo'nalish slaydi (Safety, People, Quality, Responsiveness, Cost), yakun.
#   python3 build.py
import datetime, os, re, shutil, subprocess, zipfile, openpyxl
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SKILL = '/root/.claude/skills/synced/bb7b0922-36d0-4b1f-8fcb-0025844e920b_160cec7e-c774-4a51-9040-7a1d5a36cb8e/pptx/scripts'
TPL, XLSX, OUT = 'kirish/HRM_2026_Sentabr.pptx', 'kirish/SPQRC_dashboard_November_2026.xlsx', 'SPQRC_Noyabr_2026_sexlar.pptx'
CARD, TRACK, CHIP, TEAL, LTEAL, CORAL, AMBER = '2F343B', '363C44', '3A3F47', '3CC6B8', '7FD9CF', 'E8826E', 'E8B86E'
TXT, MUTED, DIM, GREY = 'EDEBEB', '9AA2AC', '6B737D', '5A626C'
DIRS = [('SAFETY', 'Хавфсизлик', 'Душанба'), ('PEOPLE', 'Ходимлар', 'Сешанба'), ('QUALITY', 'Сифат', 'Чоршанба'),
        ('RESPONSIVENESS', 'Тезкорлик', 'Пайшанба'), ('COST', 'Харажат', 'Жума')]
DAYN = {d[0]: i for i, d in enumerate(DIRS)}
SHOPS = [('Body Shop', 'Пайвандлаш цехи', 'Body'), ('Paint Shop', 'Бўёқлаш цехи', 'Paint'), ('GA Shop', 'Йиғув цехи', 'GA'), ('SKD', 'SKD цехи', 'SKD')]
REP = datetime.date(2026, 11, 9)
SUB = 'SPQRC маълумотлари · Ноябрь 2026 · ҳисобот санаси 09.11.2026'

# ---------- маълумот ----------
wb = openpyxl.load_workbook(XLSX, data_only=True)
DASH = [r for r in wb['Dashboard'].iter_rows(values_only=True)]
NA = {}  # dashboard: "н/а" ko'rsatkichlar (cex jadvalida yo'q)
hdr = next(i for i, r in enumerate(DASH) if r[1] == 'Йўналиш' and r[2] == 'Кўрсаткич')
for r in DASH[hdr + 1:]:
    if not r[1] or r[1] not in DAYN: break
    for k, v in enumerate(r[6:10]):
        if v == 'н/а': NA.setdefault(SHOPS[k][2], []).append((r[1], r[2]))
def shop(sheet):
    rows = list(wb[sheet].iter_rows(values_only=True))
    dates = [d.date() if isinstance(d, datetime.datetime) else None for d in next(r for r in rows if isinstance(r[4], datetime.datetime))[4:34]]
    items, cur = [], None
    for r in rows:
        if r[2] and str(r[2]).split('\n')[0] in DAYN: cur = str(r[2]).split('\n')[0]
        if cur and r[3] and isinstance(r[37], (int, float)) and r[3] != 'Кунлик бажарилган (+) сони':
            plan_d = [d for d in dates if d and d <= REP and d.weekday() == DAYN[cur]]
            done_d = [dates[i] for i, v in enumerate(r[4:34]) if v == '+']
            assert len(plan_d) == r[37] and len(done_d) == r[36], (sheet, r[3])
            items.append(dict(dir=cur, name=r[3], done=int(r[36]), plan=int(r[37]), marks=[(d, d in done_d) for d in plan_d]))
        if r[1] == 'Кунлик бажарилган (+) сони': daily = [r[4:34][i] or 0 for i in (1, 2, 3, 4, 5, 8)]; tot = (int(r[36]), int(r[37]))
    assert sum(i['done'] for i in items) == tot[0] and sum(i['plan'] for i in items) == tot[1]
    return items, daily, tot
DATA = {s[2]: shop(s[0]) for s in SHOPS}
def dirv(short, code):
    it = [i for i in DATA[short][0] if i['dir'] == code]; d, p = sum(i['done'] for i in it), sum(i['plan'] for i in it)
    return d, p, (d / p if p else 0), it
# dashboard bilan solishtirish (xatosiz bo'lsin)
drow = {r[1]: r for r in DASH if r[1] in [s[1].split(' ')[0] for s in SHOPS] or (r[1] and str(r[1]).startswith(('Пайвандлаш', 'Бўёқлаш', 'Йиғув', 'SKD')))}
for (sheet, name, short), key in zip(SHOPS, ['Пайвандлаш (Body)', 'Бўёқлаш (Paint)', 'Йиғув (GA)', 'SKD']):
    r = next(x for x in DASH if x[1] == key and isinstance(x[3], float))
    for k, (code, *_ ) in enumerate(DIRS): assert abs(dirv(short, code)[2] - r[3 + k]) < 1e-9, (key, code)
    assert DATA[short][2] == (r[10], r[11]), key

# ---------- shablondan asos: muqova + 24 ta slayd18 nusxasi + yakun ----------
N = len(SHOPS) * (1 + len(DIRS))
shutil.rmtree('un', ignore_errors=True); zipfile.ZipFile(TPL).extractall('un')
for _ in range(N): subprocess.run(['python3', f'{SKILL}/add_slide.py', 'un/', 'slide18.xml', '--after', 'slide35.xml'], check=True, capture_output=True)
pxml = open('un/ppt/presentation.xml').read(); rels = open('un/ppt/_rels/presentation.xml.rels').read()
rid2s = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship [^>]*?Id="(rId\d+)"[^>]*?Target="slides/(slide\d+)\.xml"', rels)}
rid2s.update({m.group(2): m.group(1) for m in re.finditer(r'<Relationship [^>]*?Target="slides/(slide\d+)\.xml"[^>]*?Id="(rId\d+)"', rels)})
lst = re.search(r'<p:sldIdLst>(.*?)</p:sldIdLst>', pxml, re.S).group(1)
by = {rid2s[re.search(r'r:id="(rId\d+)"', e).group(1)]: e for e in re.findall(r'<p:sldId [^>]*/>', lst)}
new = sorted([k for k in by if int(k[5:]) > 35], key=lambda k: int(k[5:]))
open('un/ppt/presentation.xml', 'w').write(pxml.replace(lst, ''.join(by[k] for k in ['slide3'] + new + ['slide35'])))
subprocess.run(['python3', f'{SKILL}/clean.py', 'un/'], check=True, capture_output=True)
if os.path.exists('base.pptx'): os.remove('base.pptx')
subprocess.run('cd un && zip -qXrD ../base.pptx .', shell=True, check=True)

# ---------- yordamchilar ----------
pres = Presentation('base.pptx'); slides = list(pres.slides)
def rgb(h): return RGBColor.from_string(h)
def text(sl, x, y, w, h, t, size, color=TXT, font='Segoe UI', bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align
    for s, o in (t if isinstance(t, list) else [(t, {})]):
        if s == '\n': p = tf.add_paragraph(); p.alignment = align; continue
        r = p.add_run(); r.text = s; f = r.font; f.size = Pt(o.get('size', size)); f.name = o.get('font', font); f.bold = o.get('bold', bold); f.color.rgb = rgb(o.get('color', color))
    return tb
def box(sl, x, y, w, h, color, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.06):
    s = sl.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h)); s.fill.solid(); s.fill.fore_color.rgb = rgb(color); s.line.fill.background(); s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: s.adjustments[0] = adj
    return s
def settext(sh, t):
    p = sh.text_frame.paragraphs[0]; p.runs[0].text = t
    for r in p.runs[1:]: r._r.getparent().remove(r._r)
    for e in sh.text_frame.paragraphs[1:]: e._p.getparent().remove(e._p)
def pct(v): return (f'{v * 100:.1f}'.replace('.', ',').removesuffix(',0')) + '%'
def col(v): return TEAL if v >= .999 else (LTEAL if v >= .75 else (AMBER if v >= .5 else CORAL))
def status(i): return ('Бажарилди', TEAL) if i['done'] == i['plan'] else (('Қисман', AMBER) if i['done'] else ('Бажарилмади', CORAL))
def header(sl, num, title, pg):
    for sh in list(sl.shapes):
        if not (sh.name.startswith('!!') and sh.name not in ('!!c1', '!!c2', '!!c3', '!!c4')):
            if sh.shape_type == 3:
                rid = sh._element.xpath('.//c:chart/@r:id')
                if rid: sl.part.drop_rel(rid[0])
            sh._element.getparent().remove(sh._element)
        elif sh.name == '!!num': settext(sh, num)
        elif sh.name == '!!title': settext(sh, title)
        elif sh.name == '!!sub': settext(sh, SUB)
        elif sh.name == '!!foot': settext(sh, 'SPQRC маълумотлари | Ноябрь 2026')
        elif sh.name == '!!pg': settext(sh, f'{pg:02d}')
def kpis(sl, cards):
    for i, (lab, val, note, ac) in enumerate(cards):
        x = 0.55 + i * 3.1
        box(sl, x, 1.30, 2.95, 1.40, CARD); box(sl, x, 1.48, 0.06, 1.04, ac, MSO_SHAPE.RECTANGLE)
        text(sl, x + 0.25, 1.44, 2.6, 0.3, lab, 8.5, MUTED, 'Segoe UI Semibold')
        text(sl, x + 0.25, 1.66, 2.6, 0.7, val, 28, TXT, 'Segoe UI Light')
        text(sl, x + 0.25, 2.34, 2.65, 0.3, note, 8.5, DIM)
def summary(sl, body, y=5.75, h=1.15, w=8.15):
    box(sl, 0.55, y, w, h, CARD); box(sl, 0.55, y, 0.06, h, TEAL, MSO_SHAPE.RECTANGLE)
    text(sl, 0.80, y + 0.12, w - 0.4, h - 0.2, [('Хулоса: ', {'font': 'Segoe UI Semibold', 'color': TEAL}), (body, {})], 9.5)
def ranks(code=None):
    v = {s: (dirv(s, code)[2] if code else DATA[s][2][0] / DATA[s][2][1]) for s in DATA}
    return v
def place(v, s): return 1 + sum(1 for k in v if v[k] > v[s] + 1e-9)
def ties(v, s): return [k for k in v if k != s and abs(v[k] - v[s]) < 1e-9]

# ---------- muqova ----------
for sh in slides[0].shapes:
    if sh.name == '!!title':
        ps = sh.text_frame.paragraphs; ps[0].runs[0].text = 'SPQRC'; [r._r.getparent().remove(r._r) for r in ps[0].runs[1:]]
        ps[1].runs[0].text = 'маълумотлари'; [r._r.getparent().remove(r._r) for r in ps[1].runs[1:]]
    if sh.name == '!!foot': settext(sh, 'Safety · People · Quality · Responsiveness · Cost · 4 та цех')
    if sh.name == '!!pilltx': settext(sh, 'Ноябрь 2026')

pg = 2; k = 1
for si, (sheet, name, short) in enumerate(SHOPS):
    items, daily, (done, plan) = DATA[short]; tot = done / plan; allv = ranks()
    # ===== sex umumiy slaydi =====
    sl = slides[k]; k += 1; header(sl, f'0{si + 1}', f'{name} ({short}) — SPQRC умумий натижа', pg); pg += 1
    t = ties(allv, short)
    kpis(sl, [('ЖАМИ БАЖАРИЛИШ', pct(tot), f'{place(allv, short)}-ўрин · 4 та цех орасида' + (f' ({", ".join(t)} билан тенг)' if t else ''), col(tot)),
              ('БАЖАРИЛДИ (+)', str(done), 'ҳисобот санасигача', TEAL), ('РЕЖА', str(plan), 'кўрсаткич × йўналиш кунлари', TEAL),
              ('ЎТКАЗИБ ЮБОРИЛДИ', str(plan - done), f'режанинг {pct((plan - done) / plan)} қисми', CORAL)])
    box(sl, 0.55, 2.85, 4.55, 2.75, CARD)
    text(sl, 0.80, 2.97, 4.1, 0.25, 'SPQRC ЙЎНАЛИШЛАРИ БЎЙИЧА БАЖАРИЛИШ, %', 9, TEAL, 'Segoe UI Semibold')
    for j, (code, uz, _) in enumerate(DIRS):
        d, p, v, _ = dirv(short, code); y = 3.38 + j * 0.43
        text(sl, 0.80, y - 0.05, 1.75, 0.35, [(code, {'font': 'Segoe UI Semibold', 'size': 8.5}), ('\n', {}), (uz, {'size': 7.5, 'color': MUTED})], 8.5)
        box(sl, 2.55, y + 0.08, 1.75, 0.11, TRACK, adj=0.5)
        if v > 0: box(sl, 2.55, y + 0.08, max(0.08, 1.75 * v), 0.11, col(v), adj=0.5)
        text(sl, 4.38, y - 0.02, 0.7, 0.3, [(pct(v), {'font': 'Segoe UI Semibold'}), (f'  {d}/{p}', {'size': 7.5, 'color': DIM})], 9)
    box(sl, 5.25, 2.85, 3.45, 2.75, CARD)
    text(sl, 5.50, 2.97, 3.0, 0.25, 'КУНЛИК БАЖАРИЛГАН (+) СОНИ', 9, TEAL, 'Segoe UI Semibold')
    mx = max(6, max(daily)); base, hmax = 5.05, 1.45
    for j, (lab, v) in enumerate(zip(['Ду 2', 'Се 3', 'Чо 4', 'Па 5', 'Жу 6', 'Ду 9'], daily)):
        x = 5.55 + j * 0.52; h = hmax * v / mx
        if v: box(sl, x, base - h, 0.34, h, TEAL, adj=0.12)
        else: box(sl, x, base - 0.04, 0.34, 0.04, CORAL, MSO_SHAPE.RECTANGLE)
        text(sl, x - 0.1, base - h - 0.26, 0.54, 0.22, str(v), 9, TXT, 'Segoe UI Semibold', align=PP_ALIGN.CENTER)
        text(sl, x - 0.12, base + 0.06, 0.58, 0.22, lab, 7.5, MUTED, align=PP_ALIGN.CENTER)
    text(sl, 5.50, 5.33, 3.1, 0.22, 'Ду–S · Се–P · Чо–Q · Па–R · Жу–C (йўналиш кунлари)', 7, DIM)
    miss = [i for i in items if i['done'] < i['plan']]
    box(sl, 8.85, 2.85, 3.95, 4.05, CARD)
    text(sl, 9.10, 2.97, 3.6, 0.25, f'БАЖАРИЛМАГАН КЎРСАТКИЧЛАР · {len(miss)} та', 9, CORAL, 'Segoe UI Semibold')
    for j, i in enumerate(miss[:9]):
        y = 3.32 + j * 0.39
        box(sl, 9.10, y + 0.04, 0.95, 0.24, CHIP, adj=0.3)
        text(sl, 9.10, y + 0.04, 0.95, 0.24, i['dir'] if i['dir'] != 'RESPONSIVENESS' else 'RESPONS.', 7, MUTED, 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 10.15, y, 1.9, 0.34, i['name'], 8.5, TXT, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 12.05, y, 0.65, 0.34, f"{i['done']}/{i['plan']}", 9, CORAL if not i['done'] else AMBER, 'Segoe UI Semibold', align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    dv = {c: dirv(short, c)[2] for c, *_ in DIRS}; weak = min(dv, key=dv.get); full = [c for c in dv if dv[c] >= .999]
    zero = [i['name'] for i in miss if not i['done']]
    summary(sl, f'{name} режанинг {pct(tot)} қисмини бажарди ({done}/{plan}). ' + (f'{", ".join(full)} йўналишлари 100%. ' if full else '')
            + f'Энг заиф — {weak} ({pct(dv[weak])}). ' + (f'Умуман бажарилмаган: {", ".join(zero)}. ' if zero else '')
            + ('9-ноябр (душанба) SAFETY белгилари ҳали киритилмаган.' if daily[5] == 0 else ''))

    # ===== 5 ta yo'nalish slaydi =====
    for code, uz, wd in DIRS:
        sl = slides[k]; k += 1; header(sl, f'0{si + 1}', f'{name} · {code} — {uz}', pg); pg += 1
        d, p, v, it = dirv(short, code); rv = ranks(code); t = ties(rv, short)
        fullc = sum(1 for i in it if i['done'] == i['plan'])
        kpis(sl, [(f'{code} БАЖАРИЛИШИ', pct(v), f'{place(rv, short)}-ўрин · 4 та цех орасида' + (f' ({", ".join(t)} билан тенг)' if t else ''), col(v)),
                  ('БАЖАРИЛДИ (+)', str(d), f'{len(it)} та кўрсаткич бўйича', TEAL),
                  ('РЕЖА', str(p), f'{wd} кунлари × кўрсаткичлар', TEAL),
                  ('ЎТКАЗИБ ЮБОРИЛДИ', str(p - d), 'ҳамма белгилар қўйилган' if p == d else f'{len(it) - fullc} та кўрсаткичда', CORAL if p > d else TEAL)])
        # ko'rsatkichlar jadvali
        box(sl, 0.55, 2.85, 8.15, 2.75, CARD)
        text(sl, 0.80, 2.97, 7.6, 0.25, f'{code} КЎРСАТКИЧЛАРИ · ҲАР БИР КЎРСАТКИЧ БЎЙИЧА', 9, TEAL, 'Segoe UI Semibold')
        for x, w, lab, al in [(0.80, 2.55, 'Кўрсаткич', PP_ALIGN.LEFT), (3.45, 1.30, 'Саналар (✓ / ✗)', PP_ALIGN.LEFT), (4.80, 0.75, 'Бажарилди', PP_ALIGN.CENTER),
                              (5.62, 1.55, 'Бажарилиш', PP_ALIGN.LEFT), (7.40, 1.10, 'Ҳолат', PP_ALIGN.CENTER)]:
            text(sl, x, 3.25, w, 0.2, lab, 7.5, DIM, 'Segoe UI Semibold', align=al)
        rows = it + [dict(name=n2, na=True) for c2, n2 in NA.get(short, []) if c2 == code]
        rh = min(0.36, 2.0 / max(1, len(rows)))
        for j, i in enumerate(rows):
            y = 3.50 + j * rh
            if j: box(sl, 0.80, y - 0.02, 7.7, 0.006, '3D434C', MSO_SHAPE.RECTANGLE)
            if i.get('na'):
                text(sl, 0.80, y, 2.6, rh, i['name'], 9, DIM, anchor=MSO_ANCHOR.MIDDLE)
                text(sl, 3.45, y, 4.0, rh, 'н/а — ушбу цех жадвалида бу кўрсаткич йўқ', 8, DIM, anchor=MSO_ANCHOR.MIDDLE); continue
            text(sl, 0.80, y, 2.6, rh, i['name'], 9, TXT, anchor=MSO_ANCHOR.MIDDLE)
            for m, (dt, ok) in enumerate(i['marks']):
                cx = 3.45 + m * 0.64
                box(sl, cx, y + rh / 2 - 0.11, 0.58, 0.22, CHIP, adj=0.3)
                text(sl, cx, y + rh / 2 - 0.11, 0.58, 0.22, [(dt.strftime('%d.%m') + ' ', {'color': MUTED, 'size': 7}), ('✓' if ok else '✗', {'color': TEAL if ok else CORAL, 'font': 'Segoe UI Semibold', 'size': 8})], 7, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, 4.80, y, 0.75, rh, f"{i['done']}/{i['plan']}", 9, TXT, 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            iv = i['done'] / i['plan']
            box(sl, 5.62, y + rh / 2 - 0.05, 1.05, 0.10, TRACK, adj=0.5)
            if iv: box(sl, 5.62, y + rh / 2 - 0.05, max(0.08, 1.05 * iv), 0.10, col(iv), adj=0.5)
            text(sl, 6.75, y, 0.6, rh, pct(iv), 8.5, TXT, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE)
            st, sc = status(i)
            box(sl, 7.45, y + rh / 2 - 0.12, 1.0, 0.24, CHIP, adj=0.4)
            text(sl, 7.45, y + rh / 2 - 0.12, 1.0, 0.24, st, 7.5, sc, 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # sexlar taqqoslamasi
        box(sl, 8.85, 2.85, 3.95, 4.05, CARD)
        text(sl, 9.10, 2.97, 3.6, 0.25, f'{code} · ЦЕХЛАР ТАҚҚОСЛАМАСИ', 9, TEAL, 'Segoe UI Semibold')
        for j, (_, nm, sh2) in enumerate(SHOPS):
            dd, pp, vv, _ = dirv(sh2, code); y = 3.40 + j * 0.62; me = sh2 == short
            text(sl, 9.10, y, 2.4, 0.25, [(nm, {'font': 'Segoe UI Semibold' if me else 'Segoe UI', 'color': TXT if me else MUTED})], 8.5)
            text(sl, 11.6, y, 1.0, 0.25, [(pct(vv), {'font': 'Segoe UI Semibold', 'color': TXT if me else MUTED}), (f'  {dd}/{pp}', {'size': 7, 'color': DIM})], 8.5, align=PP_ALIGN.RIGHT)
            box(sl, 9.10, y + 0.30, 3.50, 0.12, TRACK, adj=0.5)
            if vv: box(sl, 9.10, y + 0.30, max(0.08, 3.50 * vv), 0.12, col(vv) if me else GREY, adj=0.5)
        avg = sum(dirv(s, code)[0] for s in DATA) / sum(dirv(s, code)[1] for s in DATA)
        text(sl, 9.10, 5.95, 3.6, 0.8, [('Барча цехлар бўйича: ', {'color': MUTED}), (pct(avg), {'font': 'Segoe UI Semibold', 'color': TXT}), ('\n', {}),
                                         (f'Режа: {wd} кунлари, ҳисобот санасигача ({", ".join(m[0].strftime("%d.%m") for m in it[0]["marks"])}).', {'color': DIM, 'size': 7.5})], 8.5)
        # xulosa
        bad = [i for i in it if i['done'] < i['plan']]
        s = f'{name}да {code} йўналиши бўйича {len(it)} та кўрсаткичдан {fullc} таси тўлиқ бажарилди, умумий бажарилиш {pct(v)} ({d}/{p}). '
        if bad: s += 'Бажарилмаган белгилар: ' + '; '.join(f"{i['name']} — {', '.join(m[0].strftime('%d.%m') for m in i['marks'] if not m[1])}" for i in bad) + '. '
        else: s += 'Барча кўрсаткичлар режа бўйича бажарилган. '
        if code == 'SAFETY' and any(not m[1] and m[0] == REP for i in it for m in i['marks']): s += '09.11 — ҳисобот санаси (душанба): шу кунги белгилар ҳали киритилмаган бўлиши мумкин.'
        summary(sl, s)
pres.save(OUT); print('ok', len(pres.slides), 'slayd')
