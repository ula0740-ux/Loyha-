# SPQRC dashboard (Ноябрь 2026) → har bir sex uchun bitta slayd, HRM 2026 shablon uslubida.
#   python3 build.py   (base.pptx: shablondan muqova + 4 ta slayd18 nusxasi + yakun)
import openpyxl
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

CARD, TRACK, TEAL, LTEAL, CORAL, AMBER = '2F343B', '363C44', '3CC6B8', '7FD9CF', 'E8826E', 'E8B86E'
TXT, MUTED, DIM = 'EDEBEB', '9AA2AC', '6B737D'
DIRS = [('SAFETY', 'Хавфсизлик'), ('PEOPLE', 'Ходимлар'), ('QUALITY', 'Сифат'), ('RESPONSIVENESS', 'Тезкорлик'), ('COST', 'Харажат')]
SHEETS = [('Body Shop', 'Пайвандлаш цехи', 'Body'), ('Paint Shop', 'Бўёқлаш цехи', 'Paint'), ('GA Shop', 'Йиғув цехи', 'GA'), ('SKD', 'SKD цехи', 'SKD')]
DAYS = ['Ду 2', 'Се 3', 'Чо 4', 'Па 5', 'Жу 6', 'Ду 9']

wb = openpyxl.load_workbook('kirish/SPQRC_dashboard_November_2026.xlsx', data_only=True)
def shop_data(sheet):
    ws = wb[sheet]; rows = list(ws.iter_rows(values_only=True)); items = []; cur = None
    for r in rows:
        if r[2] and str(r[2]).split('\n')[0] in dict(DIRS): cur = str(r[2]).split('\n')[0]
        if cur and r[3] and isinstance(r[36], (int, float)) and r[3] != 'Кунлик бажарилган (+) сони' and isinstance(r[37], (int, float)):
            items.append((cur, r[3], int(r[36]), int(r[37])))
        if r[1] == 'Кунлик бажарилган (+) сони':
            daily = r[4:34]; done, plan = int(r[36]), int(r[37])
    # 2-6 va 9-noyabr (ish kunlari, hisobot sanasigacha)
    d = [daily[i] or 0 for i in (1, 2, 3, 4, 5, 8)]
    return items, d, done, plan

pres = Presentation('base.pptx'); slides = list(pres.slides)
def rgb(h): return RGBColor.from_string(h)
def text(sl, x, y, w, h, t, size, color=TXT, font='Segoe UI', bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
    runs = t if isinstance(t, list) else [(t, {})]
    p = tf.paragraphs[0]; p.alignment = align
    for s, o in runs:
        if s == '\n': p = tf.add_paragraph(); p.alignment = align; continue
        r = p.add_run(); r.text = s; f = r.font; f.size = Pt(o.get('size', size)); f.name = o.get('font', font); f.bold = o.get('bold', bold); f.color.rgb = rgb(o.get('color', color))
    return tb
def box(sl, x, y, w, h, color, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.06):
    s = sl.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h)); s.fill.solid(); s.fill.fore_color.rgb = rgb(color); s.line.fill.background(); s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: s.adjustments[0] = adj
    return s
def settext(sh, t):
    p = sh.text_frame.paragraphs[0]; runs = p.runs
    runs[0].text = t
    for r in runs[1:]: r._r.getparent().remove(r._r)
    for extra in sh.text_frame.paragraphs[1:]: extra._p.getparent().remove(extra._p)
def pct(v): return f'{v * 100:.1f}%'.replace('.', ',').replace(',0%', '%')
def col(v): return TEAL if v >= .9 else (LTEAL if v >= .75 else (AMBER if v >= .5 else CORAL))

# --- muqova ---
cov = slides[0]
for sh in cov.shapes:
    if sh.name == '!!title':
        ps = sh.text_frame.paragraphs; ps[0].runs[0].text = 'SPQRC'
        for r in ps[0].runs[1:]: r._r.getparent().remove(r._r)
        if len(ps) > 1: ps[1].runs[0].text = 'Дашборд · 4 цех'; [r._r.getparent().remove(r._r) for r in ps[1].runs[1:]]
    if sh.name == '!!foot': settext(sh, 'Safety · People · Quality · Responsiveness · Cost')
    if sh.name == '!!pilltx': settext(sh, 'Ноябрь 2026')

all_tot = {}
for (sheet, _, short) in SHEETS:
    it, d, done, plan = shop_data(sheet); all_tot[short] = done / plan
rank = sorted(all_tot, key=lambda k: -all_tot[k])

for n, (sheet, name, short) in enumerate(SHEETS):
    sl = slides[1 + n]; items, daily, done, plan = shop_data(sheet); tot = done / plan
    # shablon bezaklari qoladi, eski kontent olib tashlanadi
    for sh in list(sl.shapes):
        keep = sh.name.startswith('!!') and sh.name not in ('!!c1', '!!c2', '!!c3', '!!c4')
        if not keep:
            if sh.shape_type == 3:  # diagramma: bog'lanishini ham olib tashlash
                rid = sh._element.xpath('.//c:chart/@r:id')
                if rid: sl.part.drop_rel(rid[0])
            sh._element.getparent().remove(sh._element)
        elif sh.name == '!!num': settext(sh, f'0{n + 1}')
        elif sh.name == '!!title': settext(sh, f'{name} ({short}) — SPQRC назорати')
        elif sh.name == '!!sub': settext(sh, 'Ноябрь 2026 · ҳисобот санаси 09.11.2026 · режа = ҳисобот санасигача йўналиш кунлари × кўрсаткичлар')
        elif sh.name == '!!foot': settext(sh, 'SPQRC | Ноябрь 2026')
        elif sh.name == '!!pg': settext(sh, f'0{n + 2}')
    missed = plan - done; place = rank.index(short) + 1
    ties = [k for k in all_tot if abs(all_tot[k] - tot) < 1e-9 and k != short]
    # 1) yuqori 4 kartochka
    cards = [('ЖАМИ БАЖАРИЛИШ', pct(tot), f'{place}-ўрин · 4 та цех орасида' + (f' ({", ".join(ties)} билан тенг)' if ties else ''), col(tot)),
             ('БАЖАРИЛДИ (+)', str(done), 'ҳисобот санасигача', TEAL),
             ('РЕЖА', str(plan), 'кўрсаткич × йўналиш кунлари', TEAL),
             ('ЎТКАЗИБ ЮБОРИЛДИ', str(missed), f'режанинг {pct(missed / plan)} қисми', CORAL)]
    for i, (lab, val, note, ac) in enumerate(cards):
        x = 0.55 + i * 3.1
        box(sl, x, 1.30, 2.95, 1.40, CARD); box(sl, x, 1.48, 0.06, 1.04, ac, MSO_SHAPE.RECTANGLE)
        text(sl, x + 0.25, 1.44, 2.6, 0.3, lab, 8.5, MUTED, 'Segoe UI Semibold')
        text(sl, x + 0.25, 1.66, 2.6, 0.7, val, 28, TXT, 'Segoe UI Light')
        text(sl, x + 0.25, 2.34, 2.65, 0.3, note, 8.5, DIM)
    # 2) yo'nalishlar bo'yicha
    box(sl, 0.55, 2.85, 4.55, 2.75, CARD)
    text(sl, 0.80, 2.97, 4.1, 0.25, 'SPQRC ЙЎНАЛИШЛАРИ БЎЙИЧА БАЖАРИЛИШ, %', 9, TEAL, 'Segoe UI Semibold')
    for j, (code, uz) in enumerate(DIRS):
        di = [x for x in items if x[0] == code]; dd = sum(x[2] for x in di); dp = sum(x[3] for x in di); v = dd / dp if dp else 0
        y = 3.38 + j * 0.43
        text(sl, 0.80, y - 0.05, 1.75, 0.35, [(code, {'font': 'Segoe UI Semibold', 'size': 8.5}), ('\n', {}), (uz, {'size': 7.5, 'color': MUTED})], 8.5)
        box(sl, 2.55, y + 0.08, 1.75, 0.11, TRACK, adj=0.5)
        if v > 0: box(sl, 2.55, y + 0.08, max(0.08, 1.75 * v), 0.11, col(v), adj=0.5)
        text(sl, 4.38, y - 0.02, 0.65, 0.3, [(pct(v), {'font': 'Segoe UI Semibold'}), (f'  {dd}/{dp}', {'size': 7.5, 'color': DIM})], 9)
    # 3) kunlik bajarilish (ish kunlari)
    box(sl, 5.25, 2.85, 3.45, 2.75, CARD)
    text(sl, 5.50, 2.97, 3.0, 0.25, 'КУНЛИК БАЖАРИЛГАН (+) СОНИ', 9, TEAL, 'Segoe UI Semibold')
    mx = max(6, max(daily)); base = 5.05; hmax = 1.45
    for k, (lab, v) in enumerate(zip(DAYS, daily)):
        x = 5.55 + k * 0.52
        h = hmax * v / mx
        if v: box(sl, x, base - h, 0.34, h, TEAL if k < 5 else CORAL, adj=0.12)
        else: box(sl, x, base - 0.04, 0.34, 0.04, CORAL, MSO_SHAPE.RECTANGLE)
        text(sl, x - 0.1, base - h - 0.26, 0.54, 0.22, str(v), 9, TXT, 'Segoe UI Semibold', align=PP_ALIGN.CENTER)
        text(sl, x - 0.12, base + 0.06, 0.58, 0.22, lab, 7.5, MUTED, align=PP_ALIGN.CENTER)
    text(sl, 5.50, 5.33, 3.1, 0.22, 'Ду–S · Се–P · Чо–Q · Па–R · Жу–C (йўналиш кунлари)', 7, DIM)
    # 4) bajarilmagan ko'rsatkichlar
    box(sl, 8.85, 2.85, 3.95, 4.05, CARD)
    miss = [x for x in items if x[2] < x[3]]
    text(sl, 9.10, 2.97, 3.6, 0.25, f'БАЖАРИЛМАГАН КЎРСАТКИЧЛАР · {len(miss)} та', 9, CORAL, 'Segoe UI Semibold')
    for j, (code, ind, dd, dp) in enumerate(miss[:9]):
        y = 3.32 + j * 0.39
        box(sl, 9.10, y + 0.04, 0.95, 0.24, '3A3F47', adj=0.3)
        text(sl, 9.10, y + 0.04, 0.95, 0.24, code if code != 'RESPONSIVENESS' else 'RESPONS.', 7, MUTED, 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 10.15, y, 1.9, 0.34, ind, 8.5, TXT, anchor=MSO_ANCHOR.MIDDLE)
        text(sl, 12.05, y, 0.65, 0.34, f'{dd}/{dp}', 9, CORAL if dd == 0 else AMBER, 'Segoe UI Semibold', align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    na = [x for x in items]  # н/а ko'rsatkichlar jadvalda yo'q
    # 5) xulosa
    box(sl, 0.55, 5.75, 8.15, 1.15, CARD); box(sl, 0.55, 5.75, 0.06, 1.15, TEAL, MSO_SHAPE.RECTANGLE)
    dv = {c: (sum(x[2] for x in items if x[0] == c) / max(1, sum(x[3] for x in items if x[0] == c))) for c, _ in DIRS}
    weak = min(dv, key=dv.get); full = [c for c in dv if dv[c] >= 1]
    zero = [x[1] for x in miss if x[2] == 0]
    s1 = f'{name} режанинг {pct(tot)} қисмини бажарди ({done}/{plan}). '
    s2 = f'{", ".join(full)} йўналишлари 100%. ' if full else ''
    s3 = f'Энг заиф — {weak} ({pct(dv[weak])}). '
    s4 = f'Умуман бажарилмаган: {", ".join(zero)}. ' if zero else ''
    s5 = '9-ноябр (душанба) SAFETY маълумотлари ҳали киритилмаган — эртага тўлдирилса, SAFETY кўрсаткичи ошади.' if daily[5] == 0 else ''
    text(sl, 0.80, 5.85, 7.75, 0.95, [('Хулоса: ', {'font': 'Segoe UI Semibold', 'color': TEAL}), (s1 + s2 + s3 + s4 + s5, {'color': TXT})], 9.5)
pres.save('SPQRC_Noyabr_2026_sexlar.pptx'); print('ok', rank, {k: round(v, 3) for k, v in all_tot.items()})
