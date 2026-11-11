# SPQRC shabloni: har sex x har yo'nalish = 1 sahifa (20 ta). Sahifadagi jadval - ichki (embedded) Excel varag'i:
# 2 marta bosilganda Excel ochiladi, haftaga ✓/✗ yoziladi, foizlar formula bilan o'zi hisoblanadi. Makros yo'q.
#   python3 build_ole.py [kirish/SPQRC_dashboard_*.xlsx]  -> SPQRC_shablon.pptx
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
N = 21
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

# ======================= OLE (ichki Excel) jadvalli sahifalar =======================
import tempfile
from openpyxl.styles import Font as XF, PatternFill as XP, Alignment as XA, Border as XB, Side as XS
from openpyxl.formatting.rule import FormulaRule, CellIsRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter as CL
from PIL import Image, ImageChops
SUB = f'SPQRC маълумотлари · {MONTH_UZ} {YEAR}'
LETTER = {'SAFETY': 'S', 'PEOPLE': 'P', 'QUALITY': 'Q', 'RESPONSIVENESS': 'R', 'COST': 'C'}
SHOPX = ['Svarka · Body', 'Бўёқлаш · Paint', 'Zborka · GA', 'SKD']
TMP = tempfile.mkdtemp(prefix='spqrc_ole_', dir=os.environ.get('SCRATCH', None))
BGc, CARDc, CELLc = '23272D', '2F343B', '3A4048'
WIDTH = {'A': 42, 'B': 12, 'C': 12, 'D': 12, 'E': 12, 'F': 12, 'G': 20, 'H': 14}

def fnt(c='EDEBEB', b=False, s=12): return XF(name='Segoe UI', color=c, bold=b, size=s)
def fill(c): return XP('solid', fgColor=c)
CEN = XA(horizontal='center', vertical='center', wrap_text=True); LFT = XA(horizontal='left', vertical='center', indent=1, wrap_text=True)
LINE = XB(top=XS(style='thin', color='3D434C'))

def make_sheet(s, d, path):
    code, uz, wd, _ = DIRS[d - 1]; its = ITEMS.get((s, d), []); na = [nm for c2, nm in NA.get(s, []) if c2 == code]
    wk = weeks(code)
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = code
    wb.calculation = CalcProperties(fullCalcOnLoad=True)
    ws.sheet_view.showGridLines = False; ws.sheet_view.showRowColHeaders = False
    for k, w in WIDTH.items(): ws.column_dimensions[k].width = w
    last = 6 + len(its) + len(na)
    for r in range(1, last + 2):
        for c in range(1, 9): ws.cell(r, c).fill = fill(BGc)
    # --- KPI (1-2 qator) ---
    first, lastr = 6, 5 + len(its)
    J = f'SUM(J{first}:J{lastr})' if its else '0'; K = f'SUM(K{first}:K{lastr})' if its else '0'
    kp = [('A', 'A', 'БАЖАРИЛИШ', f'=IF(({J})+({K})=0,"—",({J})/(({J})+({K})))', 'бажарилди / режа'),
          ('B', 'C', 'БАЖАРИЛДИ ✓', f'={J}', 'белги'), ('D', 'E', 'РЕЖА', f'=({J})+({K})', 'ҳисобот санасигача'), ('F', 'H', 'БАЖАРИЛМАДИ ✗', f'={K}', 'белги')]
    for a, b, lab, f, note in kp:
        if a != b:
            for r in (1, 2, 3): ws.merge_cells(f'{a}{r}:{b}{r}')
        ws[f'{a}1'] = lab; ws[f'{a}1'].font = fnt('9AA2AC', True, 11); ws[f'{a}1'].alignment = LFT
        ws[f'{a}2'] = f; ws[f'{a}2'].font = fnt('EDEBEB', False, 34); ws[f'{a}2'].alignment = LFT
        ws[f'{a}3'] = note; ws[f'{a}3'].font = fnt('6B737D', False, 10); ws[f'{a}3'].alignment = LFT
        for col in range(ord(a) - 64, ord(b) - 63):
            for r in (1, 2, 3): ws.cell(r, col).fill = fill(CARDc)
    ws['A2'].number_format = '0.0%'
    ws.row_dimensions[1].height = 24; ws.row_dimensions[2].height = 50; ws.row_dimensions[3].height = 20; ws.row_dimensions[4].height = 16
    # --- jadval sarlavhasi (5-qator) ---
    hdr = ['Кўрсаткич'] + [f'{w + 1}-ҳафта\n' + (wk[w].strftime('%d.%m') if w < len(wk) else '—') for w in range(5)] + ['Бажарилди / режа', 'Фоиз']
    for c, t in enumerate(hdr, 1):
        x = ws.cell(5, c, t); x.font = fnt('9AA2AC', True, 11); x.alignment = LFT if c == 1 else CEN; x.fill = fill(CARDc)
    ws.row_dimensions[5].height = 38
    dv = DataValidation(type='list', formula1='"✓,✗"', allow_blank=True, showErrorMessage=False); ws.add_data_validation(dv)
    for i, (nm, marks) in enumerate(its):
        r = first + i
        ws.cell(r, 1, nm).font = fnt('EDEBEB', False, 14); ws.cell(r, 1).alignment = LFT
        for w in range(5):
            x = ws.cell(r, 2 + w, marks[w] if marks[w] in (OK, NO) else None); x.alignment = CEN; x.font = fnt('9AA2AC', True, 18); x.fill = fill(CELLc)
            x.border = XB(left=XS(style='thick', color=CARDc), right=XS(style='thick', color=CARDc), top=XS(style='thick', color=CARDc), bottom=XS(style='thick', color=CARDc))
        dv.add(f'B{r}:F{r}')
        ws[f'J{r}'] = f'=COUNTIF(B{r}:F{r},"✓")+COUNTIF(B{r}:F{r},"+")'
        ws[f'K{r}'] = f'=COUNTIF(B{r}:F{r},"✗")+COUNTIF(B{r}:F{r},"-")+COUNTIF(B{r}:F{r},"x")+COUNTIF(B{r}:F{r},"х")'
        ws[f'G{r}'] = f'=J{r}&" / "&(J{r}+K{r})'; ws[f'G{r}'].font = fnt('EDEBEB', True, 15); ws[f'G{r}'].alignment = CEN
        ws[f'H{r}'] = f'=IF(J{r}+K{r}=0,"—",J{r}/(J{r}+K{r}))'; ws[f'H{r}'].number_format = '0%'; ws[f'H{r}'].font = fnt('1F2328', True, 15); ws[f'H{r}'].alignment = CEN
        for c in (1, 7): ws.cell(r, c).fill = fill(CARDc)
        ws.cell(r, 8).fill = fill(CELLc)
        ws.row_dimensions[r].height = 40
    for j, nm in enumerate(na):
        r = first + len(its) + j
        ws.cell(r, 1, nm).font = fnt('6B737D', False, 14); ws.cell(r, 1).alignment = LFT
        ws.merge_cells(f'B{r}:H{r}'); ws[f'B{r}'] = 'н/а — ушбу цех жадвалида бу кўрсаткич йўқ'; ws[f'B{r}'].font = fnt('6B737D', False, 11); ws[f'B{r}'].alignment = CEN
        for c in range(1, 9): ws.cell(r, c).fill = fill(CARDc)
        ws.row_dimensions[r].height = 32
    lr = first + len(its) + len(na) - 1
    ws.row_dimensions[lr + 1].height = 10
    for c in range(1, 9): ws.cell(lr + 1, c).fill = fill(CARDc)
    if its:
        rng = f'B{first}:F{lastr}'
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR(B{first}="✓",B{first}="+")'], fill=fill('24524D'), font=XF(color='3CC6B8', bold=True)))
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR(B{first}="✗",B{first}="-",B{first}="x",B{first}="х")'], fill=fill('5A3530'), font=XF(color='E8826E', bold=True)))
        pr = f'H{first}:H{lastr}'
        for f_, c in [(f'AND(ISNUMBER(H{first}),H{first}>=0.999)', '3CC6B8'), (f'AND(ISNUMBER(H{first}),H{first}>=0.5)', 'E8B86E'), (f'ISNUMBER(H{first})', 'E8826E')]:
            ws.conditional_formatting.add(pr, FormulaRule(formula=[f_], fill=fill(c), stopIfTrue=True))
        for f_, c in [('AND(ISNUMBER($A$2),$A$2>=0.999)', '3CC6B8'), ('AND(ISNUMBER($A$2),$A$2>=0.5)', 'E8B86E'), ('ISNUMBER($A$2)', 'E8826E')]:
            ws.conditional_formatting.add('A2', FormulaRule(formula=[f_], font=XF(color=c), stopIfTrue=True))
    rng_all = f'A1:H{lr + 1}'
    ws.print_area = rng_all
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = 'landscape'
    for m in ('left', 'right', 'top', 'bottom', 'header', 'footer'): setattr(ws.page_margins, m, 0)
    ws.cell(lr + 3, 1, 'Ҳафта катагига ✓ (бажарилди) ёки ✗ (бажарилмади) ёзинг ёки рўйхатдан танланг; + / − ҳам бўлади. Саналарни 5-қаторда ўзгартириш мумкин.').font = fnt('9AA2AC', False, 10)
    ws.sheet_view.selection[0].activeCell = 'B6'; ws.sheet_view.selection[0].sqref = 'B6'
    wb.save(path)
    # oleSize: PowerPoint'da ko'rinadigan oraliq
    zin = zipfile.ZipFile(path); items = {n: zin.read(n) for n in zin.namelist()}; zin.close()
    wbx = items['xl/workbook.xml'].decode()
    if '<oleSize' not in wbx:
        if '<calcPr' in wbx: wbx = re.sub(r'(<calcPr[^>]*/>)', r'\1<oleSize ref="%s"/>' % rng_all, wbx, count=1)
        else: wbx = wbx.replace('</workbook>', '<oleSize ref="%s"/></workbook>' % rng_all)
    items['xl/workbook.xml'] = wbx.encode()
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, b in items.items(): z.writestr(n, b)
    # sum (pts) - kenglik/balandlik nisbati uchun
    wpt = sum((WIDTH[k] * 7 + 5) * 0.75 for k in WIDTH)
    hpt = sum((ws.row_dimensions[r].height or 15) for r in range(1, lr + 2))
    return wpt, hpt

def preview(xlsx, png):
    out = os.path.join(TMP, 'pdf'); os.makedirs(out, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', out, xlsx], check=True, capture_output=True, timeout=180)
    pdf = os.path.join(out, os.path.basename(xlsx).replace('.xlsx', '.pdf'))
    subprocess.run(['pdftoppm', '-r', '220', '-png', '-singlefile', '-f', '1', '-l', '1', pdf, png[:-4]], check=True, capture_output=True)
    im = Image.open(png).convert('RGB'); bg = Image.new('RGB', im.size, (255, 255, 255))
    box_ = ImageChops.difference(im, bg).getbbox(); im = im.crop(box_); im.save(png)
    return im.size

# ---------- 1) muqova ----------
for sh in slides[0].shapes:
    if sh.name == '!!title':
        ps = sh.text_frame.paragraphs; ps[0].runs[0].text = 'SPQRC'; [r._r.getparent().remove(r._r) for r in ps[0].runs[1:]]
        ps[1].runs[0].text = 'маълумотлари'; [r._r.getparent().remove(r._r) for r in ps[1].runs[1:]]
    if sh.name == '!!foot': settext(sh, 'Safety · People · Quality · Responsiveness · Cost · 4 та цех')
    if sh.name == '!!pilltx': settext(sh, f'{MONTH_UZ} {YEAR}')
# ---------- 2) qo'llanma ----------
sl = slides[1]; header(sl, '00', 'Маълумотларни қандай ўзгартириш мумкин', SUB, 2)
steps = [('1', 'Жадвални 2 марта босинг', 'Керакли цех ва йўналиш саҳифасидаги жадвални (рақамлар ва катаклар) сичқонча билан 2 марта босинг — ичидаги Excel очилади.'),
         ('2', 'Ҳафтага белги қўйинг', 'Ҳафта катагига ✓ (бажарилди) ёки ✗ (бажарилмади) ёзинг ёки рўйхатдан танланг; + ёки − ҳам бўлади.'),
         ('3', 'Ташқарига босинг', 'Жадвалдан ташқарига босинг — бажарилиш фоизи, бажарилди, режа ва бажарилмади сонлари ўзи янгиланади, ранглар ўзгаради.'),
         ('4', 'Саҳифалар тартиби', 'Ҳар цех учун 5 та саҳифа: S – Safety, P – People, Q – Quality, R – Responsiveness, C – Cost. Цехлар: Пайвандлаш, Бўёқлаш, Йиғув, SKD.'),
         ('5', 'Янги ой', 'Файл нусхасини олинг: жадвалда белгиларни ўчиринг, 5-қатордаги ҳафта саналарини алмаштиринг. Сарлавҳадаги ой номини Ctrl+H билан алмаштиринг.')]
for i, (n_, t_, d_) in enumerate(steps):
    y = 1.35 + i * 1.08
    box(sl, 0.55, y, 12.25, 0.95, CARD)
    box(sl, 0.75, y + 0.2, 0.55, 0.55, TEAL, MSO_SHAPE.OVAL); text(sl, 0.75, y + 0.2, 0.55, 0.55, n_, 18, '1F2328', 'Segoe UI Semibold', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 1.55, y + 0.12, 3.2, 0.7, t_, 13, TXT, 'Segoe UI Semibold', anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 4.8, y + 0.1, 7.8, 0.75, d_, 10.5, MUTED, anchor=MSO_ANCHOR.MIDDLE)
# ---------- 3) sex x yo'nalish ----------
from pptx.enum.shapes import PROG_ID
k = 2; pg = 3
for s, (_, name, short) in enumerate(SHOPS, 1):
    for d, (code, uz, wd, _) in enumerate(DIRS, 1):
        sl = slides[k]; k += 1
        header(sl, LETTER[code], f'{name} — {code} ({uz})', f'{name.upper()} ({SHOPX[s - 1]}) · {SUB} · {wd} кунлари', pg); pg += 1
        x = os.path.join(TMP, f'{short}_{code}.xlsx'); png = x[:-5] + '.png'
        wpt, hpt = make_sheet(s, d, x); iw, ih = preview(x, png)
        maxw, maxh = 12.25, 5.35; ar = iw / ih
        w = maxw; h = w / ar
        if h > maxh: h = maxh; w = h * ar
        gf = sl.shapes.add_ole_object(x, PROG_ID.XLSX, Inches(0.55 + (maxw - w) / 2), Inches(1.30), Inches(w), Inches(h), icon_file=png, icon_width=Inches(w), icon_height=Inches(h))
        gf.name = f'SPQRC|{short}|{code}'
        ole = gf._element.xpath('.//p:oleObj')[0]
        if 'showAsIcon' in ole.attrib: del ole.attrib['showAsIcon']
        text(sl, 0.55, 6.78, 12.25, 0.3, [('Ўзгартириш: ', {'font': 'Segoe UI Semibold', 'color': TEAL}),
                                          ('жадвални 2 марта босинг → ичидаги Excel очилади → ҳафта катагига ✓ ёки ✗ ёзинг → ташқарига босинг, фоизлар ўзи янгиланади.', {})], 9, MUTED)
pres.save(OUT)
print('ok', OUT, len(pres.slides), 'slayd')
