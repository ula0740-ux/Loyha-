# SPQRC haftalik slaydlari (HRM 2026 uslubida) SPQRC_belgilash.xlsx dan (makrossiz).
#   Belgilash Excel'da: har sex varag'ida ko'rsatkich x hafta katagiga ✓ / ✗ (make_xlsx.py yasaydi).
#   python3 build_tpl.py [SPQRC_belgilash.xlsx]   -> SPQRC_haftalik_shablon.pptx (oy va yil Excel'dagi Йил/Ой kataklaridan)
#   Zavod dashboard faylini ham to'g'ridan-to'g'ri berish mumkin (Dashboard varag'i bo'lsa avtomatik aniqlanadi).
import calendar, datetime, os, re, shutil, subprocess, sys, zipfile, openpyxl
from spqrc_data import DIRS, DAYN, SHOPS, MONTHS, OK, NO, OFF, load_dashboard, load_input, weeks as _weeks
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SKILL = '/root/.claude/skills/synced/bb7b0922-36d0-4b1f-8fcb-0025844e920b_160cec7e-c774-4a51-9040-7a1d5a36cb8e/pptx/scripts'
TPL, OUT = 'kirish/HRM_2026_Sentabr.pptx', 'SPQRC_haftalik_shablon.pptx'
CARD, TRACK, CHIP, CELLC, TEAL, LTEAL, CORAL, AMBER = '2F343B', '363C44', '3A3F47', '343A42', '3CC6B8', '7FD9CF', 'E8826E', 'E8B86E'
TXT, MUTED, DIM, GREY = 'EDEBEB', '9AA2AC', '6B737D', '5A626C'

# ---------- ma'lumot: SPQRC_belgilash.xlsx (yoki zavod dashboard fayli) ----------
SRC = sys.argv[1] if len(sys.argv) > 1 else 'SPQRC_belgilash.xlsx'
DATA = load_dashboard(SRC) if 'Dashboard' in openpyxl.load_workbook(SRC, read_only=True).sheetnames else load_input(SRC)
YEAR, MONTH = DATA['year'], DATA['month']; MONTH_UZ = MONTHS[MONTH - 1]
ITEMS, NA = DATA['items'], DATA['na']
def weeks(dcode): return _weeks(YEAR, MONTH, DAYN[dcode])
CELLS = [(s_, d_, r_ + 1, w + 1, marks[w]) for (s_, d_), its in ITEMS.items() for r_, (_, marks) in enumerate(its) for w in range(5)]
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
HOWTO = [('Ўзгартириш: ', {'font': 'Segoe UI Semibold', 'color': TEAL}), ('SPQRC_belgilash.xlsx да ҳафта катагига ✓ ёки ✗ қўйинг — слайдлар шу Excel асосида янгиланади.', {}), ('\n', {}),
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
steps = [('1', 'Excel файлни очинг', 'SPQRC_belgilash.xlsx — телефонда (Excel иловаси), браузерда ёки компьютерда очилади. Макрос керак эмас.'),
         ('2', 'Ҳафтани белгиланг', 'Цех варағида (Body, Paint, GA, SKD) ҳафта катагига ✓ (бажарилди) ёки ✗ (бажарилмади) танланг ёки + / − ёзинг. Ҳар йўналиш ўз куни бўйича: Ду–SAFETY, Се–PEOPLE, Чо–QUALITY, Па–RESPONSIVENESS, Жу–COST.'),
         ('3', 'Фоизлар ўзи ошади', 'Ойлик бажарилиш = ✓ / ойлик режа (ой давомида ошиб боради). Белгиланган ҳафталар бўйича = ✓ / (✓ + ✗). Excel да дарҳол, слайдларда — янгилангач.'),
         ('4', 'Слайдларни янгилаш', 'Белгиланган Excel файлни юборинг — шу шаблондаги барча слайдлар (цехлар, йўналишлар, «Барча цехлар» жадвали) Excel бўйича янгиланади.'),
         ('5', 'Янги ой', 'Excel даги «Барча цехлар» варағида Йил ва Ой катакларини ўзгартиринг: ҳафта саналари ўзи янгиланади, «—» ўзи қўйилади. Эски белгиларни ўчиринг.')]
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
        for r, (nm, marks) in enumerate(its, 1):  # marks: [w1..w5]
            y = 3.70 + (r - 1) * rh
            text(sl, 0.80, y, 2.45, rh, nm, 9, TXT, anchor=MSO_ANCHOR.MIDDLE)
            for w in range(1, 6):
                v = marks[w - 1]
                c = box(sl, cx0 + (w - 1) * cwid, y + rh / 2 - 0.17, cwid - 0.12, 0.34, CELLC, adj=0.25, name=f'CELL|{s}|{d}|{r}|{w}')
                tf = c.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
                tf.text = v; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
                run = p.runs[0] if p.runs else p.add_run()
                run.font.size = Pt(13); run.font.name = 'Segoe UI Semibold'; run.font.color.rgb = rgb(TEAL if v == OK else (CORAL if v == NO else GREY))
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
print('ok', len(pres.slides), 'slayd ·', MONTH_UZ, YEAR, '· sexlar oylik %:', {SHOPS[s - 1][2]: metric('pct', s) for s in range(1, 5)})
