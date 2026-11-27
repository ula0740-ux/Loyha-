# SPQRC haftalik belgilash SHABLONI - bitta PowerPoint fayl, makrossiz (HRM 2026 uslubida).
# Har yo'nalish slaydida diagramma; uning ichki (embedded) Excel jadvalida ko'rsatkich x hafta belgilari va formulalar.
# Foydalanuvchi: diagramma -> o'ng tugma -> «Изменить данные / Edit Data» -> B–F ustunlariga ✓/✗ (+/−) -> ranglar va foizlar o'zi yangilanadi.
#   python3 build_native.py [manba.xlsx]   (standart: zavod dashboard fayli; SPQRC_belgilash.xlsx ham bo'ladi)
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
N = 1 + len(SHOPS) * 6
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

def finish_chart(gf, wb, n_rows, cat_col, ser_cols, title_val, plot_layout, vmax, colors, gap=55):
    """Diagramma XML: havolalarni bizning varaqqa yo'naltirish, sarlavha (katakdan), ranglar, o'qlar, ichki Excel."""
    ch = gf.chart; cs = ch._chartSpace; c = cs.find(f'{{{C}}}chart')
    ch.has_legend = False
    plot = ch.plots[0]; plot.gap_width = gap
    if len(ser_cols) > 1: plot.overlap = 100
    for i, ser in enumerate(plot.series):
        col = colors[i]
        if col: ser.format.fill.solid(); ser.format.fill.fore_color.rgb = RGBColor.from_string(col)
        else: ser.format.fill.background()
        ser.format.line.fill.background()
        x = ser._element
        x.find(f'{{{C}}}tx').find(f'.//{{{C}}}f').text = f'{Q}${ser_cols[i]}$3'
        x.find(f'{{{C}}}cat').find(f'.//{{{C}}}f').text = f'{Q}${cat_col}$4:${cat_col}${3 + n_rows}'
        x.find(f'{{{C}}}val').find(f'.//{{{C}}}f').text = f'{Q}${ser_cols[i]}$4:${ser_cols[i]}${3 + n_rows}'
    ca, va = ch.category_axis, ch.value_axis
    ca.reverse_order = True; ca.format.line.fill.background(); ca.has_major_gridlines = False
    from pptx.enum.chart import XL_TICK_MARK, XL_TICK_LABEL_POSITION
    ca.major_tick_mark = XL_TICK_MARK.NONE
    va.minimum_scale = 0; va.maximum_scale = vmax; va.has_major_gridlines = False; va.visible = False
    cae = ca._element; old = cae.find(f'{{{C}}}txPr')
    if old is not None: cae.remove(old)
    cae.insert(list(cae).index(cae.find(f'{{{C}}}crossAx')), txpr(10.5, TXT))
    # sarlavha - katakdagi formuladan
    t = E('c:title'); tx = E('c:tx'); tx.append(strref(f'{Q}$N$1', title_val)); t.append(tx)
    lay = E('c:layout'); ml = E('c:manualLayout')
    for k, v in [('xMode', 'edge'), ('yMode', 'edge'), ('x', 0.01), ('y', 0.0)]: e = E('c:' + k, val=v); ml.append(e)
    lay.append(ml); t.append(lay); t.append(E('c:overlay', val=0)); t.append(txpr(14, TXT, True))
    old = c.find(f'{{{C}}}title')
    if old is not None: c.remove(old)
    c.insert(0, t); atd = c.find(f'{{{C}}}autoTitleDeleted')
    if atd is not None: atd.set('val', '0')
    # chizma maydoni joylashuvi
    pa = c.find(f'{{{C}}}plotArea'); old = pa.find(f'{{{C}}}layout')
    if old is not None: pa.remove(old)
    lay = E('c:layout'); ml = E('c:manualLayout'); ml.append(E('c:layoutTarget', val='inner'))
    for k, v in [('xMode', 'edge'), ('yMode', 'edge'), ('x', plot_layout[0]), ('y', plot_layout[1]), ('w', plot_layout[2]), ('h', plot_layout[3])]: ml.append(E('c:' + k, val=v))
    lay.append(ml); pa.insert(0, lay)
    pv = c.find(f'{{{C}}}plotVisOnly')
    if pv is not None: pv.set('val', '0')
    # fonlar shaffof
    for parent in (cs, pa):
        sp = parent.find(f'{{{C}}}spPr')
        if sp is None:
            sp = E('c:spPr')
            if parent is cs: parent.insert(list(parent).index(c) + 1, sp)
            else: parent.append(sp)
        for ch_ in list(sp): sp.remove(ch_)
        sp.append(E('a:noFill')); ln = E('a:ln'); ln.append(E('a:noFill')); sp.append(ln)
    # ichki Excel
    bio = io.BytesIO(); wb.save(bio); ch.part.chart_workbook.update_from_xlsx_blob(bio.getvalue())

def sheet_base():
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = SHEET
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    return wb, ws
HDRF = Font(bold=True, color='3CC6B8'); INF = PatternFill('solid', fgColor='FFF4D6'); MK = PatternFill('solid', fgColor='EAF7F5')

def direction_chart(sl, s, d, its, x, y, w, h):
    code, uz, wd, _ = DIRS[d - 1]; wk = weeks(code); n = len(its)
    wb, ws = sheet_base()
    ws['A1'] = 'Йил:'; ws['B1'] = YEAR; ws['C1'] = 'Ой (1–12):'; ws['D1'] = MONTH
    for k in ('B1', 'D1'): ws[k].fill = INF; ws[k].font = Font(bold=True)
    ws['A2'] = f'{code} — {uz} · {wd} кунлари'; ws['A2'].font = HDRF
    ws['A3'] = 'Кўрсаткич  \\  сана'
    for i, lab in enumerate(['✓', '✗', 'Режа', 'Ойлик %']): ws.cell(2, 7 + i, lab).font = Font(bold=True)
    for wi in range(5):
        L = CL(2 + wi); ws.cell(2, 2 + wi, f'{wi + 1}-ҳафта').font = Font(bold=True)
        xx = f'(DATE($B$1,$D$1,1)+MOD({d}-WEEKDAY(DATE($B$1,$D$1,1),2),7)+{7 * wi})'
        c_ = ws.cell(3, 2 + wi, f'=IF(MONTH({xx})=$D$1,{xx},"{OFF}")'); c_.number_format = 'dd.mm'; c_.alignment = Alignment(horizontal='center')
    SER = []  # (ustun harfi, rang)
    col = 15
    for wi in range(5):
        for kind, color in [('ok', TEAL), ('no', CORAL), ('em', '4A515B'), ('off', '2A2E34'), ('gap', None)]:
            SER.append((CL(col), color, kind, wi)); col += 1
    cache_vals = {k: [] for k in range(len(SER))}; labels = []
    for ri, (nm, marks) in enumerate(its):
        r = 4 + ri; ws.cell(r, 1, nm)
        for wi in range(5):
            c_ = ws.cell(r, 2 + wi, marks[wi] if marks[wi] in (OK, NO) else None); c_.alignment = Alignment(horizontal='center'); c_.fill = MK
        cols = {}
        for k, (L, color, kind, wi) in enumerate(SER):
            B = CL(2 + wi); m = f'{B}{r}'
            if kind == 'ok': f = f'=IF(AND(ISNUMBER({B}$3),OR({m}="✓",{m}="+",{m}="v",{m}="✔")),1,0)'; v = int(marks[wi] == OK)
            elif kind == 'no': f = f'=IF(AND(ISNUMBER({B}$3),OR({m}="✗",{m}="-",{m}="x",{m}="х",{m}="−",{m}="✘")),1,0)'; v = int(marks[wi] == NO)
            elif kind == 'em': f = f'=IF(ISNUMBER({B}$3),1-{cols[(wi, "ok")]}{r}-{cols[(wi, "no")]}{r},0)'; v = int(marks[wi] == '')
            elif kind == 'off': f = f'=IF(ISNUMBER({B}$3),0,1)'; v = int(marks[wi] == OFF)
            else: f = 0.12; v = 0.12
            cols[(wi, kind)] = L; ws[f'{L}{r}'] = f; cache_vals[k].append(v)
        ws.cell(r, 7, '=' + '+'.join(f'{cols[(wi, "ok")]}{r}' for wi in range(5)))
        ws.cell(r, 8, '=' + '+'.join(f'{cols[(wi, "no")]}{r}' for wi in range(5)))
        ws.cell(r, 9, '=COUNT($B$3:$F$3)')
        ws.cell(r, 10, f'=IF(I{r}=0,0,G{r}/I{r})').number_format = '0.0%'
        ws.cell(r, 14, f'=A{r}&"   "&ROUND(J{r}*100,1)&"%"')
        dn, pl = marks.count(OK), len(wk); labels.append(f'{nm}   {num(dn / pl) if pl else "0"}%')
    t = 4 + n; ws.cell(t, 1, 'ЖАМИ').font = Font(bold=True)
    for cc, L in [(7, 'G'), (8, 'H'), (9, 'I')]: ws.cell(t, cc, f'=SUM({L}4:{L}{t - 1})').font = Font(bold=True)
    ws.cell(t, 10, f'=IF(I{t}=0,0,G{t}/I{t})').number_format = '0.0%'
    ds = '&" · "&'.join(f'IF(ISNUMBER({CL(2 + wi)}3),RIGHT("0"&DAY({CL(2 + wi)}3),2)&"."&RIGHT("0"&MONTH({CL(2 + wi)}3),2),"{OFF}")' for wi in range(5))
    ws['N2'] = f'={ds}'
    ws['N1'] = f'="Ойлик бажарилиш "&ROUND(J{t}*100,1)&"%     ✓ "&G{t}&" / "&I{t}&"     ✗ "&H{t}&"          {wd}: "&N2'
    done, miss, plan = agg(s, d)
    title_val = f'Ойлик бажарилиш {num(done / plan) if plan else "0"}%     ✓ {done} / {plan}     ✗ {miss}          {wd}: ' + ' · '.join(dstr(wk[wi]) if wi < len(wk) else OFF for wi in range(5))
    tips = ['Қандай белгиланади:', '1) B–F устунларига (1–5-ҳафта) ✓ ёки ✗ ёзинг (+ ёки − ҳам бўлади). Бўш = ҳали белгиланмаган.',
            '2) Ойнани ёпинг — слайддаги ранглар ва фоизлар ўзи янгиланади.', '3) «—» = шу ойда йўқ ҳафта (режага кирмайди). Янги ой: B1 (йил) ва D1 (ой).']
    for i, tp in enumerate(tips): ws.cell(t + 2 + i, 1, tp).font = Font(bold=(i == 0), color='3CC6B8' if i == 0 else '555555')
    ws.column_dimensions['A'].width = 40
    for L in 'BCDEF': ws.column_dimensions[L].width = 9
    for L in 'GHIJ': ws.column_dimensions[L].width = 8
    for k in range(14, col): ws.column_dimensions[CL(k)].hidden = True
    ws.freeze_panes = 'B4'
    cd = CategoryChartData(); cd.categories = labels
    for k, (L, color, kind, wi) in enumerate(SER): cd.add_series(f'{wi + 1}-{kind}', cache_vals[k])
    gf = sl.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    gf.name = f'SPQRC|{s}|{d}'
    PL = (0.34, 0.16, 0.64, 0.82)
    finish_chart(gf, wb, n, 'N', [L for L, *_ in SER], title_val, PL, 5.6, [c for _, c, *_ in SER], gap=45 if n > 3 else 120)
    return PL

def shop_chart(sl, s, x, y, w, h):
    wb, ws = sheet_base(); name = SHOPS[s - 1][1]
    ws['A2'] = f'{name} — йўналишлар бўйича (йўналиш слайдлари сарлавҳасидаги сонлар)'; ws['A2'].font = HDRF
    for i, lab in enumerate(['Йўналиш', '✓ бажарилди', 'Режа', 'Ойлик %']): ws.cell(3, 1 + i, lab).font = Font(bold=True)
    ws['O3'] = 'Ойлик %'; labels, vals = [], []
    for d in range(1, 6):
        r = 3 + d; code, uz = DIRS[d - 1][:2]; done, miss, plan = agg(s, d)
        ws.cell(r, 1, f'{code} — {uz}'); ws.cell(r, 2, done).fill = INF; ws.cell(r, 3, plan).fill = INF
        ws.cell(r, 4, f'=IF(C{r}=0,0,B{r}/C{r})').number_format = '0.0%'
        ws[f'N{r}'] = f'=A{r}&"   "&ROUND(D{r}*100,1)&"%   (✓ "&B{r}&" / "&C{r}&")"'; ws[f'O{r}'] = f'=D{r}'
        labels.append(f'{code} — {uz}   {num(done / plan) if plan else "0"}%   (✓ {done} / {plan})'); vals.append(done / plan if plan else 0)
    ws['A9'] = 'ЖАМИ'; ws['B9'] = '=SUM(B4:B8)'; ws['C9'] = '=SUM(C4:C8)'; ws['D9'] = '=IF(C9=0,0,B9/C9)'; ws['D9'].number_format = '0.0%'
    ws['N1'] = '="Цех бўйича ойлик бажарилиш "&ROUND(D9*100,1)&"%     ✓ "&B9&" / "&C9'
    ws['A11'] = 'Сариқ катакларга йўналиш слайдлари сарлавҳасидаги ✓ ва Режа сонларини ёзинг, сўнг ойнани ёпинг.'
    ws.column_dimensions['A'].width = 34; ws.column_dimensions['N'].hidden = True; ws.column_dimensions['O'].hidden = True
    done, miss, plan = agg(s)
    cd = CategoryChartData(); cd.categories = labels; cd.add_series('Ойлик %', vals)
    gf = sl.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd); gf.name = f'SPQRC|{s}|0'
    finish_chart(gf, wb, 5, 'N', ['O'], f'Цех бўйича ойлик бажарилиш {num(done / plan)}%     ✓ {done} / {plan}', (0.40, 0.18, 0.57, 0.78), 1, [TEAL], gap=70)
    # trek (fon) seriyasi o'rniga: o'q 0..1, chiziq 100% gacha bo'sh joy - kartochka foni yetarli

# ---------- 1) muqova ----------
for sh in slides[0].shapes:
    if sh.name == '!!title':
        ps = sh.text_frame.paragraphs; ps[0].runs[0].text = 'SPQRC'; [r._r.getparent().remove(r._r) for r in ps[0].runs[1:]]
        ps[1].runs[0].text = 'маълумотлари'; [r._r.getparent().remove(r._r) for r in ps[1].runs[1:]]
    if sh.name == '!!foot': settext(sh, 'Ҳафталик белгилаш шаблони · 4 та цех · 5 йўналиш')
    if sh.name == '!!pilltx': settext(sh, f'{MONTH_UZ} {YEAR}')

# ---------- 2) qo'llanma ----------
sl = slides[1]; header(sl, '00', 'Шаблондан фойдаланиш тартиби', SUB, 2)
steps = [('1', 'Диаграммани очинг', 'Йўналиш слайдидаги диаграммани сичқончанинг ўнг тугмаси билан босинг → «Изменить данные» (Edit Data). Ичидаги Excel жадвали очилади. Макрос керак эмас.'),
         ('2', 'Ҳафтага белги қўйинг', 'B–F устунлари = 1–5-ҳафта. Катакка ✓ (бажарилди) ёки ✗ (бажарилмади) ёзинг; + ёки − ҳам бўлади. Ҳар йўналиш ўз куни бўйича: Ду–SAFETY, Се–PEOPLE, Чо–QUALITY, Па–RESPONSIVENESS, Жу–COST.'),
         ('3', 'Фоизлар ўзи ошади', 'Excel ойнасини ёпинг: ҳафта катаклари яшил / қизил бўлади, кўрсаткич ва йўналиш фоизи ўзи янгиланади. Ойлик бажарилиш = ✓ / ойлик режа — ой давомида ошиб боради.'),
         ('4', 'Цехнинг умумий слайди', 'Йўналиш слайдлари сарлавҳасидаги ✓ ва режа сонларини цех слайдидаги диаграммага («Изменить данные», сариқ катаклар) ёзинг — цех фоизи ўзи ҳисобланади.'),
         ('5', 'Янги ой ва бошқаларга бериш', 'Ҳар диаграммада B1 (йил) ва D1 (ой) ни ўзгартиринг — саналар ва «—» ўзи қўйилади; эски белгиларни ўчиринг. Файл оддий PowerPoint (Windows / Mac) да ишлайди, ҳар ким ўз нусхасида белгилайди.')]
for i, (n_, t_, d_) in enumerate(steps):
    y = 1.35 + i * 1.08
    box(sl, 0.55, y, 12.25, 0.95, CARD)
    box(sl, 0.75, y + 0.2, 0.55, 0.55, TEAL, MSO_SHAPE.OVAL); text(sl, 0.75, y + 0.2, 0.55, 0.55, n_, 18, '1F2328', 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 1.55, y + 0.12, 3.2, 0.7, t_, 13, TXT, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 4.8, y + 0.1, 7.8, 0.75, d_, 10, MUTED, anchor=MSO_ANCHOR.MIDDLE)

HINT = [('Белгилаш: ', {'font': 'Segoe UI Semibold', 'color': TEAL}), ('диаграмма → ўнг тугма → «Изменить данные» → B–F устунларига ✓ ёки ✗ → ойнани ёпинг. ', {}),
        ('■ ', {'color': TEAL}), ('бажарилди  ', {}), ('■ ', {'color': CORAL}), ('бажарилмади  ', {}), ('■ ', {'color': '4A515B'}), ('белгиланмаган  ', {}), ('■ ', {'color': '2A2E34'}), ('шу ойда йўқ ҳафта', {})]
k = 2; pg = 3
for s, (sheet, name, short) in enumerate(SHOPS, 1):
    sl = slides[k]; k += 1; header(sl, f'0{s}', f'{name} ({short}) — SPQRC умумий натижа', SUB, pg); pg += 1
    box(sl, 0.55, 1.30, 12.25, 5.25, CARD)
    shop_chart(sl, s, 0.70, 1.40, 11.95, 5.05)
    text(sl, 0.55, 6.68, 12.25, 0.3, [('Янгилаш: ', {'font': 'Segoe UI Semibold', 'color': TEAL}), ('диаграмма → ўнг тугма → «Изменить данные» → сариқ катакларга йўналиш слайдлари сарлавҳасидаги ✓ ва режа сонларини ёзинг.', {})], 9, MUTED)
    for d, (code, uz, wd, _) in enumerate(DIRS, 1):
        sl = slides[k]; k += 1; header(sl, f'0{s}', f'{name} · {code} — {uz}', SUB, pg); pg += 1
        box(sl, 0.55, 1.30, 12.25, 5.25, CARD)
        cx, cy, cw_, chh = 0.70, 1.40, 11.95, 5.05
        PL = direction_chart(sl, s, d, ITEMS[(s, d)], cx, cy, cw_, chh)
        px, pw = cx + PL[0] * cw_, PL[2] * cw_
        for wi in range(5):
            mid = (wi * 1.12 + 0.5) / 5.6
            text(sl, px + pw * mid - 0.5, cy + 0.42, 1.0, 0.25, f'{wi + 1}-ҳафта', 8.5, DIM, 'Segoe UI Semibold', align=PP_ALIGN.CENTER)
        for c2, nm in [x_ for x_ in NA.get(s, []) if x_[0] == code]:
            text(sl, 0.85, 6.20, 11.5, 0.25, f'н/а: {nm} — ушбу цех жадвалида бу кўрсаткич йўқ', 8, DIM)
        text(sl, 0.55, 6.68, 12.25, 0.3, HINT, 9, MUTED)
pres.save(OUT)
print('ok', OUT, len(pres.slides), 'slayd', MONTH_UZ, YEAR)
