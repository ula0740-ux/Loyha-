# SPQRC sodda shablon: har yo'nalishga 1 sahifa (S, P, Q, R, C), 4 sex bitta diagrammada.
# Ma'lumot diagrammaning ichki Excel jadvalida (o'ng tugma -> «Изменить данные»): har sex uchun bajarildi (+) va reja; foiz formulada.
#   python3 build_simple.py [kirish/SPQRC_dashboard_*.xlsx]  -> SPQRC_shablon.pptx
import calendar, datetime, os, re, shutil, subprocess, sys, zipfile, openpyxl
from spqrc_data import DIRS, DAYN, SHOPS, MONTHS, OK, NO, OFF, load_dashboard, load_input, weeks as _weeks
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
import copy, io
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.workbook.properties import CalcProperties
from openpyxl.utils import get_column_letter as CL

SKILL = '/root/.claude/skills/synced/bb7b0922-36d0-4b1f-8fcb-0025844e920b_160cec7e-c774-4a51-9040-7a1d5a36cb8e/pptx/scripts'
TPL, OUT = 'kirish/HRM_2026_Sentabr.pptx', 'SPQRC_shablon.pptx'
CARD, TRACK, CHIP, CELLC, TEAL, LTEAL, CORAL, AMBER = '2F343B', '363C44', '3A3F47', '343A42', '3CC6B8', '7FD9CF', 'E8826E', 'E8B86E'
TXT, MUTED, DIM, GREY = 'EDEBEB', '9AA2AC', '6B737D', '5A626C'

# ---------- ma'lumot: SPQRC_belgilash.xlsx (yoki zavod dashboard fayli) ----------
SRC = sys.argv[1] if len(sys.argv) > 1 else 'kirish/SPQRC_dashboard_November_2026.xlsx'
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
N = 6
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
        elif sh.name == '!!foot': settext(sh, f'SPQRC маълумотлари | {MONTH_UZ} {YEAR}')
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


SUB = f'SPQRC маълумотлари · {MONTH_UZ} {YEAR} · ҳафталик белгилаш'
C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'; A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
def E(tag, **at):
    e = etree.Element(('{%s}' % (C if tag.startswith('c:') else A)) + tag[2:])
    for k, v in at.items(): e.set(k, str(v))
    return e
SHEET = 'Белгилаш'; Q = f"'{SHEET}'!"
def num(v): return (f'{round(v * 100, 1):.1f}'.replace('.', ',').removesuffix(',0'))
def dstr(dt): return dt.strftime('%d.%m') if dt else OFF
def txpr(size, color, bold=False):
    t = etree.fromstring(f'<c:txPr xmlns:c="{C}" xmlns:a="{A}"><a:bodyPr/><a:lstStyle/><a:p><a:pPr><a:defRPr sz="{int(size * 100)}" b="{int(bold)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
                         f'<a:latin typeface="Segoe UI"/><a:cs typeface="Segoe UI"/></a:defRPr></a:pPr><a:endParaRPr lang="ru-RU"/></a:p></c:txPr>')
    return t
def strref(ref, val):
    sr = E('c:strRef'); f = E('c:f'); f.text = ref; sr.append(f); sc = E('c:strCache'); sc.append(E('c:ptCount', val=1))
    pt = E('c:pt', idx=0); v = E('c:v'); v.text = val; pt.append(v); sc.append(pt); sr.append(sc); return sr


# ======================= SODDA SHABLON: har yo'nalishga 1 sahifa, 4 sex birga =======================
SUB = f'SPQRC маълумотлари · {MONTH_UZ} {YEAR} · 4 та цех'
SHEET = 'Маълумот'; Q = f"'{SHEET}'!"
SCOL = ['3CC6B8', 'E8B86E', 'E8826E', '8FA8D6']  # Body, Paint, GA, SKD
LETTER = {'SAFETY': 'S', 'PEOPLE': 'P', 'QUALITY': 'Q', 'RESPONSIVENESS': 'R', 'COST': 'C'}

def dir_data(d):
    """ko'rsatkichlar (4 sex birlashmasi) -> {sex: (bajarildi, reja)}; sexda bo'lmasa None"""
    names = []
    for s in range(1, 5):
        for nm, _ in ITEMS.get((s, d), []):
            if nm not in names: names.append(nm)
    rows = []
    for nm in names:
        vals = []
        for s in range(1, 5):
            m = next((mk for n_, mk in ITEMS.get((s, d), []) if n_ == nm), None)
            vals.append(None if m is None else (m.count(OK), m.count(OK) + m.count(NO)))
        rows.append((nm, vals))
    return rows

def solid(color):
    sp = E('c:spPr'); sf = E('a:solidFill'); sf.append(E('a:srgbClr', val=color)); sp.append(sf); ln = E('a:ln'); ln.append(E('a:noFill')); sp.append(ln); return sp
def nofill():
    sp = E('c:spPr'); sp.append(E('a:noFill')); ln = E('a:ln'); ln.append(E('a:noFill')); sp.append(ln); return sp

def direction_slide(sl, d):
    code, uz, wd, _ = DIRS[d - 1]; rows = dir_data(d); n = len(rows); t = 3 + n
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = SHEET; wb.calculation = CalcProperties(fullCalcOnLoad=True)
    Y = PatternFill('solid', fgColor='FFF4D6'); B = Font(bold=True); HD = Font(bold=True, color='1F8F84')
    ws['A1'] = f'{code} — {uz} · {MONTH_UZ} {YEAR}   (сариқ катакларга сон ёзинг, сўнг ойнани ёпинг)'; ws['A1'].font = HD
    ws['A2'] = 'Кўрсаткич'; ws['A2'].font = B
    for s in range(4):
        c1, c2 = CL(2 + 2 * s), CL(3 + 2 * s)
        ws[f'{c1}2'] = f'{SHOPS[s][2]}: бажарилди (+)'; ws[f'{c2}2'] = f'{SHOPS[s][2]}: режа'
        ws[f'{c1}2'].font = B; ws[f'{c2}2'].font = B
        ws[f'{CL(12 + s)}2'] = SHOPS[s][1]   # seriya nomi (afsona)
    cats, ser = [], [[] for _ in range(4)]
    for i, (nm, vals) in enumerate(rows):
        r = 3 + i; ws.cell(r, 1, nm)
        for s, v in enumerate(vals):
            c1, c2 = CL(2 + 2 * s), CL(3 + 2 * s)
            if v is not None:
                ws[f'{c1}{r}'] = v[0]; ws[f'{c2}{r}'] = v[1]
            ws[f'{c1}{r}'].fill = Y; ws[f'{c2}{r}'].fill = Y
            ws[f'{CL(12 + s)}{r}'] = f'=IF(N({c2}{r})=0,NA(),{c1}{r}/{c2}{r})'
            ser[s].append(None if v is None or v[1] == 0 else v[0] / v[1])
        ws[f'K{r}'] = f'=A{r}'; cats.append(nm)
    ws.cell(t, 1, 'ЖАМИ (йўналиш бўйича)').font = B
    tot = []
    for s in range(4):
        c1, c2 = CL(2 + 2 * s), CL(3 + 2 * s)
        ws[f'{c1}{t}'] = f'=SUM({c1}3:{c1}{t - 1})'; ws[f'{c2}{t}'] = f'=SUM({c2}3:{c2}{t - 1})'
        ws[f'{c1}{t}'].font = B; ws[f'{c2}{t}'].font = B
        ws[f'{CL(12 + s)}{t}'] = f'=IF({c2}{t}=0,NA(),{c1}{t}/{c2}{t})'
        dn = sum(v[0] for _, vals in rows for v in [vals[s]] if v); pl = sum(v[1] for _, vals in rows for v in [vals[s]] if v)
        tot.append((dn, pl)); ser[s].append(dn / pl if pl else None)
    ws[f'K{t}'] = '="ЖАМИ"'; cats.append('ЖАМИ')
    ws[f'A{t + 2}'] = 'Бўш катак = шу цехда бу кўрсаткич йўқ. Фоиз = бажарилди / режа.'
    ws.column_dimensions['A'].width = 34
    for k in range(2, 10): ws.column_dimensions[CL(k)].width = 14
    for k in range(11, 16): ws.column_dimensions[CL(k)].hidden = True
    ws.freeze_panes = 'B3'
    cd = CategoryChartData(); cd.categories = cats
    for s in range(4): cd.add_series(SHOPS[s][1], ser[s])
    gf = sl.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.70), Inches(1.40), Inches(11.95), Inches(5.10), cd); gf.name = f'SPQRC|{code}'
    ch = gf.chart; cs = ch._chartSpace; c = cs.find(f'{{{C}}}chart')
    plot = ch.plots[0]; plot.gap_width = 60; plot.overlap = -5
    plot.has_data_labels = True; dl = plot.data_labels; dl.number_format = '0%'; dl.number_format_is_linked = False
    dl.font.size = Pt(9); dl.font.color.rgb = rgb(TXT); dl.font.name = 'Segoe UI'
    from pptx.enum.chart import XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_MARK
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    for s, srs in enumerate(plot.series):
        srs.format.fill.solid(); srs.format.fill.fore_color.rgb = rgb(SCOL[s]); srs.format.line.fill.background()
        x = srs._element; L = CL(12 + s)
        x.find(f'{{{C}}}tx').find(f'.//{{{C}}}f').text = f'{Q}${L}$2'
        x.find(f'{{{C}}}cat').find(f'.//{{{C}}}f').text = f'{Q}$K$3:$K${t}'
        x.find(f'{{{C}}}val').find(f'.//{{{C}}}f').text = f'{Q}${L}$3:${L}${t}'
    ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.TOP; ch.legend.include_in_layout = False
    ch.legend.font.size = Pt(10); ch.legend.font.color.rgb = rgb(TXT); ch.legend.font.name = 'Segoe UI'
    ca, va = ch.category_axis, ch.value_axis
    ca.reverse_order = True; ca.format.line.fill.background(); ca.major_tick_mark = XL_TICK_MARK.NONE
    ca.tick_labels.font.size = Pt(10); ca.tick_labels.font.color.rgb = rgb(TXT); ca.tick_labels.font.name = 'Segoe UI'
    va.minimum_scale = 0; va.maximum_scale = 1.08; va.has_major_gridlines = False; va.visible = False
    ch.has_title = False
    pv = c.find(f'{{{C}}}plotVisOnly')
    if pv is not None: pv.set('val', '0')
    db = c.find(f'{{{C}}}dispBlanksAs')
    # #N/A (sexda yo'q ko'rsatkich) bo'sh ko'rinsin
    ext = etree.fromstring('<c:extLst xmlns:c="%s"><c:ext uri="{56B9EC1D-385E-4148-901F-78D8002777C0}" xmlns:c16r3="http://schemas.microsoft.com/office/drawing/2017/03/chart">'
                           '<c16r3:dataDisplayOptions16><c16r3:dispNaAsBlank val="1"/></c16r3:dataDisplayOptions16></c:ext></c:extLst>' % C)
    c.append(ext)
    for parent in (cs, c.find(f'{{{C}}}plotArea')):
        sp = parent.find(f'{{{C}}}spPr')
        if sp is not None: parent.remove(sp)
        new = nofill()
        if parent is cs: parent.insert(list(parent).index(c) + 1, new)
        else: parent.append(new)
    bio = io.BytesIO(); wb.save(bio); ch.part.chart_workbook.update_from_xlsx_blob(bio.getvalue())
    return tot

# ---------- 1) muqova ----------
for sh in slides[0].shapes:
    if sh.name == '!!title':
        ps = sh.text_frame.paragraphs; ps[0].runs[0].text = 'SPQRC'; [r._r.getparent().remove(r._r) for r in ps[0].runs[1:]]
        ps[1].runs[0].text = 'маълумотлари'; [r._r.getparent().remove(r._r) for r in ps[1].runs[1:]]
    if sh.name == '!!foot': settext(sh, 'Safety · People · Quality · Responsiveness · Cost · 4 та цех')
    if sh.name == '!!pilltx': settext(sh, f'{MONTH_UZ} {YEAR}')

# ---------- 2) qo'llanma ----------
sl = slides[1]; header(sl, '00', 'Маълумотларни қандай ўзгартириш мумкин', SUB, 2)
steps = [('1', 'Диаграммани танланг', 'Керакли йўналиш саҳифасидаги диаграммани сичқончанинг ўнг тугмаси билан босинг.'),
         ('2', '«Изменить данные»', 'Менюдан «Изменить данные» (Edit Data) ни танланг — диаграмма ичидаги Excel жадвали очилади.'),
         ('3', 'Сонларни ёзинг', 'Сариқ катакларга ҳар бир цех учун «бажарилди (+)» ва «режа» сонини ёзинг. Бўш катак — шу цехда бу кўрсаткич йўқ.'),
         ('4', 'Ойнани ёпинг', 'Excel ойнасини ёпинг — фоизлар ва устунлар ўзи янгиланади. Охирги қатор «ЖАМИ» — цехнинг йўналиш бўйича натижаси.'),
         ('5', 'Янги ой', 'Шу файлнинг нусхасини олинг, ҳар саҳифада сонларни янгиланг, сарлавҳадаги ой номини алмаштиринг (Ctrl+H).')]
for i, (n_, t_, d_) in enumerate(steps):
    y = 1.35 + i * 1.08
    box(sl, 0.55, y, 12.25, 0.95, CARD)
    box(sl, 0.75, y + 0.2, 0.55, 0.55, TEAL, MSO_SHAPE.OVAL); text(sl, 0.75, y + 0.2, 0.55, 0.55, n_, 18, '1F2328', 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 1.55, y + 0.12, 3.2, 0.7, t_, 13, TXT, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 4.8, y + 0.1, 7.8, 0.75, d_, 10.5, MUTED, anchor=MSO_ANCHOR.MIDDLE)

# ---------- 3) yo'nalishlar ----------
for d, (code, uz, wd, _) in enumerate(DIRS, 1):
    sl = slides[1 + d]; header(sl, LETTER[code], f'{code} — {uz} · 4 та цех', SUB + f' · {wd} кунлари', 2 + d)
    box(sl, 0.55, 1.30, 12.25, 5.30, CARD)
    direction_slide(sl, d)
    text(sl, 0.55, 6.72, 12.25, 0.3, [('Ўзгартириш: ', {'font': 'Segoe UI Semibold', 'color': TEAL}),
                                      ('диаграмма → ўнг тугма → «Изменить данные» → сариқ катакларга сон ёзинг → ойнани ёпинг. Фоиз = бажарилди / режа.', {})], 9, MUTED)
pres.save(OUT)
print('ok', OUT, len(pres.slides), 'slayd')
