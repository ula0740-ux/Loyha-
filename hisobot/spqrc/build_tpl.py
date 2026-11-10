# SPQRC haftalik belgilash SHABLONI (HRM 2026 uslubida). Har yo'nalish slaydida ko'rsatkich × hafta katakchalari:
# bo'sh / ✓ / ✗ / — (shu oyda yo'q hafta). Katakchalar SPQRC.bas makrosidagi ToggleMark ga ulangan; foizlar Yangilash makrosi bilan
# qayta hisoblanadi. Shakl nomlari makros uchun kalit:  CELL|s|d|r|w   HDR|s|d|w   TXT|metric|s|d|r|w   BAR|...  TRK|...  MAT|s|d
#   s: sex 1..4, d: yo'nalish 1..5, r: ko'rsatkich 1..6, w: hafta 1..5; 0 = hammasi (yig'indi).
#   metric: pct = ✓/oylik reja, exe = ✓/(✓+✗), done, miss, plan.
#   python3 build_tpl.py   (Noyabr 2026 ma'lumotlari Excel'dan oldindan to'ldiriladi)
import calendar, datetime, os, re, shutil, subprocess, zipfile, openpyxl
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SKILL = '/root/.claude/skills/synced/bb7b0922-36d0-4b1f-8fcb-0025844e920b_160cec7e-c774-4a51-9040-7a1d5a36cb8e/pptx/scripts'
TPL, XLSX, OUT = 'kirish/HRM_2026_Sentabr.pptx', 'kirish/SPQRC_dashboard_November_2026.xlsx', 'SPQRC_haftalik_shablon.pptx'
YEAR, MONTH, MONTH_UZ = 2026, 11, 'Ноябрь'
CARD, TRACK, CHIP, CELLC, TEAL, LTEAL, CORAL, AMBER = '2F343B', '363C44', '3A3F47', '343A42', '3CC6B8', '7FD9CF', 'E8826E', 'E8B86E'
TXT, MUTED, DIM, GREY = 'EDEBEB', '9AA2AC', '6B737D', '5A626C'
OK, NO, OFF = '✓', '✗', '—'
DIRS = [('SAFETY', 'Хавфсизлик', 'Душанба', 'Ду'), ('PEOPLE', 'Ходимлар', 'Сешанба', 'Се'), ('QUALITY', 'Сифат', 'Чоршанба', 'Чо'),
        ('RESPONSIVENESS', 'Тезкорлик', 'Пайшанба', 'Па'), ('COST', 'Харажат', 'Жума', 'Жу')]
DAYN = {d[0]: i for i, d in enumerate(DIRS)}
SHOPS = [('Body Shop', 'Пайвандлаш цехи', 'Body'), ('Paint Shop', 'Бўёқлаш цехи', 'Paint'), ('GA Shop', 'Йиғув цехи', 'GA'), ('SKD', 'SKD цехи', 'SKD')]

# ---------- ma'lumot (Excel) ----------
wb = openpyxl.load_workbook(XLSX, data_only=True)
DASH = list(wb['Dashboard'].iter_rows(values_only=True))
REP = next(next(v for v in r if isinstance(v, datetime.datetime)) for r in DASH if r[1] and 'Ҳисобот санаси' in str(r[1])).date()
NA = {}
h0 = next(i for i, r in enumerate(DASH) if r[1] == 'Йўналиш' and r[2] == 'Кўрсаткич')
for r in DASH[h0 + 1:]:
    if r[1] not in DAYN: break
    for k, v in enumerate(r[6:10]):
        if v == 'н/а': NA.setdefault(k + 1, []).append((r[1], r[2]))
def weeks(dcode):  # oyning shu hafta kuniga to'g'ri keladigan sanalari (4 yoki 5 ta)
    return [datetime.date(YEAR, MONTH, d) for d in range(1, calendar.monthrange(YEAR, MONTH)[1] + 1) if calendar.weekday(YEAR, MONTH, d) == DAYN[dcode]]
ITEMS = {}  # (s, d) -> [(nomi, {sana: '✓'|'✗'|''})]
for si, (sheet, *_ ) in enumerate(SHOPS, 1):
    rows = list(wb[sheet].iter_rows(values_only=True))
    dates = [x.date() if isinstance(x, datetime.datetime) else None for x in next(r for r in rows if isinstance(r[4], datetime.datetime))[4:34]]
    cur = None
    for r in rows:
        if r[2] and str(r[2]).split('\n')[0] in DAYN: cur = str(r[2]).split('\n')[0]
        if cur and r[3] and isinstance(r[37], (int, float)) and r[3] != 'Кунлик бажарилган (+) сони':
            plus = {dates[i] for i, v in enumerate(r[4:34]) if v == '+'}
            marks = {dt: (OK if dt in plus else (NO if dt <= REP else '')) for dt in weeks(cur)}
            assert sum(1 for v in marks.values() if v == OK) == r[36] and sum(1 for v in marks.values() if v) == r[37], (sheet, r[3])
            ITEMS.setdefault((si, DAYN[cur] + 1), []).append((r[3], marks))
CELLS = []  # (s, d, r, w, qiymat)
for (s, d), its in ITEMS.items():
    wk = weeks(DIRS[d - 1][0])
    for r, (_, marks) in enumerate(its, 1):
        for w in range(1, 6): CELLS.append((s, d, r, w, marks[wk[w - 1]] if w <= len(wk) else OFF))
def agg(s=0, d=0, r=0, w=0):
    c = [v for (a, b, e, f, v) in CELLS if (not s or a == s) and (not d or b == d) and (not r or e == r) and (not w or f == w)]
    done = c.count(OK); miss = c.count(NO); plan = sum(1 for v in c if v != OFF)
    return done, miss, plan
def pct(v): return (f'{v * 100:.1f}'.replace('.', ',').removesuffix(',0')) + '%'
def metric(m, s=0, d=0, r=0, w=0):
    done, miss, plan = agg(s, d, r, w)
    return {'pct': pct(done / plan) if plan else '—', 'exe': pct(done / (done + miss)) if done + miss else '—', 'done': str(done), 'miss': str(miss), 'plan': str(plan)}[m]
def exe_col(s=0, d=0, r=0, w=0):
    done, miss, _ = agg(s, d, r, w)
    if not done + miss: return GREY
    v = done / (done + miss); return TEAL if v >= .999 else (LTEAL if v >= .75 else (AMBER if v >= .5 else CORAL))
def ratio(s=0, d=0, r=0, w=0):
    done, _, plan = agg(s, d, r, w); return done / plan if plan else 0

# ---------- shablondan asos ----------
N = 2 + len(SHOPS) * 6
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
if os.path.exists('base_tpl.pptx'): os.remove('base_tpl.pptx')
subprocess.run('cd un && zip -qXrD ../base_tpl.pptx .', shell=True, check=True)

pres = Presentation('base_tpl.pptx'); slides = list(pres.slides)
def rgb(h): return RGBColor.from_string(h)
def text(sl, x, y, w, h, t, size, color=TXT, font='Segoe UI', bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name=None):
    tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
    p = tf.paragraphs[0]; p.alignment = align
    for s, o in (t if isinstance(t, list) else [(t, {})]):
        if s == '\n': p = tf.add_paragraph(); p.alignment = align; continue
        r = p.add_run(); r.text = s; f = r.font; f.size = Pt(o.get('size', size)); f.name = o.get('font', font); f.bold = o.get('bold', bold); f.color.rgb = rgb(o.get('color', color))
    if name: tb.name = name
    return tb
def box(sl, x, y, w, h, color, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.06, name=None):
    s = sl.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h)); s.fill.solid(); s.fill.fore_color.rgb = rgb(color); s.line.fill.background(); s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: s.adjustments[0] = adj
    if name: s.name = name
    return s
def bar(sl, x, y, w, h, key, color, ratio_v):  # TRK (fon) + BAR (to'ldirish); makros BAR enini TRK eniga nisbatan o'zgartiradi
    box(sl, x, y, w, h, TRACK, adj=0.5, name='TRK|' + key)
    b = box(sl, x, y, max(0.02, w * ratio_v), h, color, adj=0.5, name='BAR|' + key)
    if ratio_v <= 0: b._element.nvSpPr.cNvPr.set('hidden', '1')
def settext(sh, t):
    p = sh.text_frame.paragraphs[0]; p.runs[0].text = t
    for r in p.runs[1:]: r._r.getparent().remove(r._r)
    for e in sh.text_frame.paragraphs[1:]: e._p.getparent().remove(e._p)
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
def macro_click(shape, name='ToggleMark'):  # bosilganda makros: <a:hlinkClick r:id="" action="ppaction://macro?name=..."/>
    cNvPr = shape._element.nvSpPr.cNvPr
    h = etree.SubElement(cNvPr, f'{{{A}}}hlinkClick'); h.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', ''); h.set('action', f'ppaction://macro?name={name}')
def header(sl, num, title, sub, pg):
    for sh in list(sl.shapes):
        if not (sh.name.startswith('!!') and sh.name not in ('!!c1', '!!c2', '!!c3', '!!c4')):
            if sh.shape_type == 3:
                rid = sh._element.xpath('.//c:chart/@r:id')
                if rid: sl.part.drop_rel(rid[0])
            sh._element.getparent().remove(sh._element)
        elif sh.name == '!!num': settext(sh, num)
        elif sh.name == '!!title': settext(sh, title)
        elif sh.name == '!!sub': settext(sh, sub)
        elif sh.name == '!!foot': settext(sh, 'SPQRC маълумотлари | ҳафталик белгилаш')
        elif sh.name == '!!pg': settext(sh, f'{pg:02d}')
def kpi(sl, i, lab, key_val, note, ac, val_text):
    x = 0.55 + i * 3.1
    box(sl, x, 1.30, 2.95, 1.40, CARD); box(sl, x, 1.48, 0.06, 1.04, ac, MSO_SHAPE.RECTANGLE)
    text(sl, x + 0.25, 1.44, 2.6, 0.3, lab, 8.5, MUTED, 'Segoe UI Semibold')
    text(sl, x + 0.25, 1.66, 2.6, 0.7, val_text if isinstance(val_text, list) else [(val_text, {})], 28, TXT, 'Segoe UI Light', name=key_val)
    text(sl, x + 0.25, 2.34, 2.65, 0.3, note, 8.5, DIM)
SUB = f'SPQRC маълумотлари · {MONTH_UZ} {YEAR} · ҳафталик белгилаш'
HOWTO = [('Белгилаш: ', {'font': 'Segoe UI Semibold', 'color': TEAL}), ('слайд-шоуда (F5) катакни босинг: бўш → ✓ → ✗ → бўш. Фоизлар ўзи янгиланади.', {}), ('\n', {}),
         ('Таҳрирлаш режимида: ', {'font': 'Segoe UI Semibold', 'color': TEAL}), ('катакка + ёки − ёзинг, сўнг Alt+F8 → Yangilash.', {}), ('\n', {}),
         ('— ', {'font': 'Segoe UI Semibold', 'color': TEAL}), ('шу ойда йўқ ҳафта (режага кирмайди).', {})]

# ---------- 1) muqova ----------
for sh in slides[0].shapes:
    if sh.name == '!!title':
        ps = sh.text_frame.paragraphs; ps[0].runs[0].text = 'SPQRC'; [r._r.getparent().remove(r._r) for r in ps[0].runs[1:]]
        ps[1].runs[0].text = 'маълумотлари'; [r._r.getparent().remove(r._r) for r in ps[1].runs[1:]]
    if sh.name == '!!foot': settext(sh, 'Ҳафталик белгилаш шаблони · 4 та цех · 5 йўналиш')
    if sh.name == '!!pilltx': settext(sh, f'{MONTH_UZ} {YEAR}')

# ---------- 2) qo'llanma ----------
sl = slides[1]; header(sl, '00', 'Шаблондан фойдаланиш тартиби', SUB, 2)
steps = [('1', 'Макросни бир марта улаш', 'Alt+F11 → File → Import File → SPQRC.bas. Сўнг файлни «PowerPoint Macro-Enabled Presentation (*.pptm)» сифатида сақланг. Очилганда «Enable Content / Включить содержимое» ни босинг.'),
         ('2', 'Ҳафтани белгилаш', 'F5 (слайд-шоу) да катакни босинг: бўш → ✓ (бажарилди) → ✗ (бажарилмади) → бўш. Ҳар бир йўналиш ўз куни бўйича: Ду–SAFETY, Се–PEOPLE, Чо–QUALITY, Па–RESPONSIVENESS, Жу–COST.'),
         ('3', 'Фоизлар ўзи ошади', 'Ойлик бажарилиш = ✓ / ойлик режа. Белгиланган ҳафталар бўйича = ✓ / (✓ + ✗). Цехнинг умумий слайди ва «Барча цехлар» жадвали ҳам янгиланади.'),
         ('4', 'Таҳрирлаш режимида', 'Катакка + (бажарилди) ёки − (бажарилмади) ёзинг ва Alt+F8 → Yangilash ни ишга туширинг.'),
         ('5', 'Янги ой', 'Alt+F8 → OyniOrnatish → йил-ойни киритинг (масалан 2026-12). Саналар янгиланади, белгилар тозаланади, шу ойда йўқ ҳафта «—» бўлади. Сарлавҳадаги ой номини қўлда алмаштиринг.')]
for i, (n, t, d) in enumerate(steps):
    y = 1.35 + i * 1.08
    box(sl, 0.55, y, 12.25, 0.95, CARD)
    box(sl, 0.75, y + 0.2, 0.55, 0.55, TEAL, MSO_SHAPE.OVAL); text(sl, 0.75, y + 0.2, 0.55, 0.55, n, 18, '1F2328', 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 1.55, y + 0.12, 3.2, 0.7, t, 13, TXT, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 4.8, y + 0.1, 7.8, 0.75, d, 10, MUTED, anchor=MSO_ANCHOR.MIDDLE)

# ---------- 3) barcha sexlar matritsasi ----------
sl = slides[2]; header(sl, '00', 'Барча цехлар · SPQRC йўналишлари бўйича ойлик бажарилиш', SUB, 3)
box(sl, 0.55, 1.35, 12.25, 4.6, CARD)
cw = 1.55; x0 = 3.25
text(sl, 0.85, 1.55, 2.2, 0.3, 'Цех', 9, MUTED, 'Segoe UI Semibold')
for j, (code, uz, *_ ) in enumerate(DIRS + [('ЖАМИ', 'ойлик', '', '')]):
    text(sl, x0 + j * cw, 1.50, cw - 0.1, 0.45, [(code, {'font': 'Segoe UI Semibold', 'size': 9}), ('\n', {}), (uz, {'size': 7.5, 'color': MUTED})], 9, align=PP_ALIGN.CENTER)
for i, (_, nm, short) in enumerate(SHOPS, 1):
    y = 2.05 + (i - 1) * 0.92
    text(sl, 0.85, y, 2.3, 0.75, [(nm, {'font': 'Segoe UI Semibold'}), ('\n', {}), (short, {'size': 8, 'color': MUTED})], 11, anchor=MSO_ANCHOR.MIDDLE)
    for j in range(6):
        d = j + 1 if j < 5 else 0
        c = box(sl, x0 + j * cw, y + 0.06, cw - 0.12, 0.62, exe_col(i, d), adj=0.12, name=f'MAT|{i}|{d}')
        tf = c.text_frame; tf.text = metric('pct', i, d); r = tf.paragraphs[0].runs[0]; r.font.size = Pt(15); r.font.name = 'Segoe UI Semibold'; r.font.color.rgb = rgb('1F2328'); tf.paragraphs[0].alignment = PP_ALIGN.CENTER
text(sl, 0.55, 6.1, 12.25, 0.8, [('Ранг — белгиланган ҳафталар бўйича (✓ / (✓+✗)): ', {'color': MUTED}), ('100%', {'color': TEAL, 'font': 'Segoe UI Semibold'}), (' · ', {}), ('75–99%', {'color': LTEAL, 'font': 'Segoe UI Semibold'}), (' · ', {}),
                                  ('50–74%', {'color': AMBER, 'font': 'Segoe UI Semibold'}), (' · ', {}), ('50% дан паст', {'color': CORAL, 'font': 'Segoe UI Semibold'}), (' · ', {}), ('ҳали белгиланмаган', {'color': GREY, 'font': 'Segoe UI Semibold'}),
                                  ('\n', {}), ('Ячейкадаги фоиз — ойлик бажарилиш (✓ / ойлик режа): ой давомида белгилар қўйилган сари ошади.', {'color': DIM})], 9)

k = 3; pg = 4
for s, (sheet, name, short) in enumerate(SHOPS, 1):
    # ===== sex umumiy =====
    sl = slides[k]; k += 1; header(sl, f'0{s}', f'{name} ({short}) — SPQRC умумий натижа', SUB, pg); pg += 1
    kpi(sl, 0, 'ОЙЛИК БАЖАРИЛИШ', f'TXT|pct|{s}|0|0|0', '✓ / ойлик режа', TEAL, metric('pct', s))
    kpi(sl, 1, 'БЕЛГИЛАНГАН ҲАФТАЛАР БЎЙИЧА', f'TXT|exe|{s}|0|0|0', '✓ / (✓ + ✗)', TEAL, metric('exe', s))
    kpi(sl, 2, 'БАЖАРИЛДИ ✓  /  РЕЖА', f'TXT|done|{s}|0|0|0', 'ойлик режа: кўрсаткич × ҳафталар', TEAL, [(metric('done', s), {}), (' / ' + metric('plan', s), {'color': MUTED})])
    kpi(sl, 3, 'БАЖАРИЛМАДИ ✗', f'TXT|miss|{s}|0|0|0', 'белгиланган ҳафталарда', CORAL, metric('miss', s))
    box(sl, 0.55, 2.85, 8.15, 4.05, CARD)
    text(sl, 0.80, 2.97, 7.6, 0.25, 'ЙЎНАЛИШЛАР БЎЙИЧА · ОЙЛИК БАЖАРИЛИШ', 9, TEAL, 'Segoe UI Semibold')
    for x, w, lab, al in [(0.80, 2.2, 'Йўналиш', PP_ALIGN.LEFT), (3.05, 2.6, 'Ойлик бажарилиш', PP_ALIGN.LEFT), (5.75, 0.75, '✓', PP_ALIGN.CENTER), (6.5, 0.75, '✗', PP_ALIGN.CENTER),
                          (7.25, 0.65, 'Режа', PP_ALIGN.CENTER), (7.85, 0.75, '✓/(✓+✗)', PP_ALIGN.CENTER)]:
        text(sl, x, 3.27, w, 0.2, lab, 7.5, DIM, 'Segoe UI Semibold', align=al)
    for d, (code, uz, wd, _) in enumerate(DIRS, 1):
        y = 3.55 + (d - 1) * 0.64
        if d > 1: box(sl, 0.80, y - 0.05, 7.7, 0.006, '3D434C', MSO_SHAPE.RECTANGLE)
        text(sl, 0.80, y, 2.2, 0.5, [(code, {'font': 'Segoe UI Semibold'}), ('\n', {}), (f'{uz} · {wd}', {'size': 7.5, 'color': MUTED})], 9, anchor=MSO_ANCHOR.MIDDLE)
        bar(sl, 3.05, y + 0.20, 1.85, 0.11, f'pct|{s}|{d}|0|0', exe_col(s, d), ratio(s, d))
        text(sl, 4.98, y, 0.75, 0.5, metric('pct', s, d), 9, TXT, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE, name=f'TXT|pct|{s}|{d}|0|0')
        for x, m, c in [(5.75, 'done', TEAL), (6.5, 'miss', CORAL), (7.25, 'plan', MUTED)]:
            text(sl, x, y, 0.75 if m != 'plan' else 0.65, 0.5, metric(m, s, d), 10, c, 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, name=f'TXT|{m}|{s}|{d}|0|0')
        text(sl, 7.85, y, 0.75, 0.5, metric('exe', s, d), 9, TXT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, name=f'TXT|exe|{s}|{d}|0|0')
    box(sl, 8.85, 2.85, 3.95, 4.05, CARD)
    text(sl, 9.10, 2.97, 3.6, 0.25, 'ИЗОҲ ВА ЧОРА-ТАДБИРЛАР', 9, TEAL, 'Segoe UI Semibold')
    text(sl, 9.10, 3.30, 3.5, 2.2, 'Шу ерга изоҳ ёзинг…', 9.5, DIM)
    text(sl, 9.10, 5.55, 3.5, 1.25, HOWTO, 7.5, MUTED)
    # ===== yo'nalishlar =====
    for d, (code, uz, wd, wds) in enumerate(DIRS, 1):
        sl = slides[k]; k += 1; header(sl, f'0{s}', f'{name} · {code} — {uz}', SUB, pg); pg += 1
        its = ITEMS[(s, d)]; wk = weeks(code)
        kpi(sl, 0, f'{code} · ОЙЛИК БАЖАРИЛИШ', f'TXT|pct|{s}|{d}|0|0', '✓ / ойлик режа — ҳафта сайин ошади', TEAL, metric('pct', s, d))
        kpi(sl, 1, 'БЕЛГИЛАНГАН ҲАФТАЛАР БЎЙИЧА', f'TXT|exe|{s}|{d}|0|0', '✓ / (✓ + ✗)', TEAL, metric('exe', s, d))
        kpi(sl, 2, 'БАЖАРИЛДИ ✓  /  РЕЖА', f'TXT|done|{s}|{d}|0|0', f'{len(its)} кўрсаткич × {len(wk)} ҳафта ({wd})', TEAL, [(metric('done', s, d), {}), (' / ' + metric('plan', s, d), {'color': MUTED})])
        kpi(sl, 3, 'БАЖАРИЛМАДИ ✗', f'TXT|miss|{s}|{d}|0|0', 'белгиланган ҳафталарда', CORAL, metric('miss', s, d))
        # katakchalar jadvali
        box(sl, 0.55, 2.85, 8.15, 4.05, CARD)
        text(sl, 0.80, 2.97, 7.6, 0.25, f'ҲАФТАЛИК БЕЛГИЛАШ · {wd.upper()} КУНЛАРИ', 9, TEAL, 'Segoe UI Semibold')
        cx0, cwid = 3.30, 0.72
        text(sl, 0.80, 3.28, 2.4, 0.3, 'Кўрсаткич', 7.5, DIM, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE)
        for w in range(1, 6):
            lab = (wk[w - 1].strftime('%d.%m') if w <= len(wk) else OFF)
            text(sl, cx0 + (w - 1) * cwid, 3.22, cwid - 0.08, 0.4, [(f'{w}-ҳафта', {'size': 7, 'color': DIM}), ('\n', {}), (lab, {'size': 8, 'color': MUTED, 'font': 'Segoe UI Semibold'})], 8, align=PP_ALIGN.CENTER, name=f'HDR|{s}|{d}|{w}')
        text(sl, 7.00, 3.28, 1.6, 0.3, 'Ойлик бажарилиш', 7.5, DIM, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE)
        rh = min(0.5, 3.1 / max(1, len(its) + len([1 for c2, _ in NA.get(s, []) if c2 == code])))
        for r, (nm, marks) in enumerate(its, 1):
            y = 3.70 + (r - 1) * rh
            text(sl, 0.80, y, 2.45, rh, nm, 9, TXT, anchor=MSO_ANCHOR.MIDDLE)
            for w in range(1, 6):
                v = marks[wk[w - 1]] if w <= len(wk) else OFF
                c = box(sl, cx0 + (w - 1) * cwid, y + rh / 2 - 0.17, cwid - 0.12, 0.34, CELLC, adj=0.25, name=f'CELL|{s}|{d}|{r}|{w}')
                tf = c.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf.text = v; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
                run = p.runs[0] if p.runs else p.add_run()
                run.font.size = Pt(13); run.font.name = 'Segoe UI Semibold'; run.font.color.rgb = rgb(TEAL if v == OK else (CORAL if v == NO else GREY))
                if v != OFF: macro_click(c)
            bar(sl, 7.00, y + rh / 2 - 0.05, 0.95, 0.10, f'pct|{s}|{d}|{r}|0', exe_col(s, d, r), ratio(s, d, r))
            text(sl, 8.02, y, 0.6, rh, metric('pct', s, d, r), 8.5, TXT, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE, name=f'TXT|pct|{s}|{d}|{r}|0')
        for j, (c2, nm) in enumerate([x for x in NA.get(s, []) if x[0] == code]):
            y = 3.70 + (len(its) + j) * rh
            text(sl, 0.80, y, 2.45, rh, nm, 9, DIM, anchor=MSO_ANCHOR.MIDDLE)
            text(sl, cx0, y, 4.6, rh, 'н/а — ушбу цех жадвалида бу кўрсаткич йўқ', 8, DIM, anchor=MSO_ANCHOR.MIDDLE)
        # haftalar bo'yicha
        box(sl, 8.85, 2.85, 3.95, 4.05, CARD)
        text(sl, 9.10, 2.97, 3.6, 0.25, 'ҲАФТАЛАР БЎЙИЧА БАЖАРИЛИШ', 9, TEAL, 'Segoe UI Semibold')
        for w in range(1, 6):
            y = 3.30 + (w - 1) * 0.46
            text(sl, 9.10, y, 1.2, 0.25, f'{w}-ҳафта', 8.5, MUTED)
            bar(sl, 10.15, y + 0.08, 1.85, 0.11, f'pct|{s}|{d}|0|{w}', exe_col(s, d, 0, w), ratio(s, d, 0, w))
            text(sl, 12.08, y, 0.62, 0.25, metric('pct', s, d, 0, w), 8.5, TXT, 'Segoe UI Semibold', align=PP_ALIGN.RIGHT, name=f'TXT|pct|{s}|{d}|0|{w}')
        text(sl, 9.10, 5.62, 3.5, 1.2, HOWTO, 7.5, MUTED)
pres.save(OUT)
print('ok', len(pres.slides), 'slayd · hisobot sanasi', REP, '· sexlar oylik %:', {SHOPS[s - 1][2]: metric('pct', s) for s in range(1, 5)})
