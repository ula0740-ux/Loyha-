# Boʻlim nizomlari va Lavozim yoʻriqnomalari holati — 2 sahifa (HRM 2026 shabloni uslubida).
#   python3 build.py   (kirish/status.xlsx, kirish/HRM_2026_Sentabr.pptx) -> Nizom_va_Yoriqnoma_holati.pptx
import os, re, shutil, subprocess, zipfile, glob, openpyxl
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

SKILL = glob.glob('/root/.claude/skills/synced/*/pptx/scripts')[0]
TPL, XLSX, OUT = 'kirish/HRM_2026_Sentabr.pptx', 'kirish/status.xlsx', 'Nizom_va_Yoriqnoma_holati.pptx'
CARD, TRACK, TEAL, LTEAL, CORAL, AMBER = '2F343B', '363C44', '3CC6B8', '7FD9CF', 'E8826E', 'E8B86E'
TXT, MUTED, DIM, DARK = 'EDEBEB', '9AA2AC', '6B737D', '1F2328'
UZ = {'Отдел координации производства': 'Ishlab chiqarishni muvofiqlashtirish boʻlimi', 'Отдел контроля производства': 'Ishlab chiqarish nazorati boʻlimi',
      'SKD цех': 'SKD sexi', 'Сварочный цех': 'Payvandlash sexi', 'Окрасочный цех': 'Boʻyoqlash sexi', 'Сборочный цех': 'Yigʻuv sexi'}

# ---------- maʼlumot ----------
wb = openpyxl.load_workbook(XLSX, data_only=True)
r1 = list(wb["Bo'lim nizomlari"].iter_rows(values_only=True))
NIZ = [(r[1], r[2]) for r in r1 if isinstance(r[0], int)]                      # (boʻlinma, Bor/Jarayonda/Yoʻq)
r2 = list(wb["Lavozim yo'riqnomalari"].iter_rows(values_only=True))
i2 = next(k for k, r in enumerate(r2) if r[0] and str(r[0]).startswith('2.'))
YOR = []
for r in r2[i2 + 2:]:
    if r[1] == 'JAMI': JAMI = r[2:5]; break
    YOR.append((r[1], r[2], r[3], r[4]))                                          # (boʻlinma, jami, bor, yoʻq)
i3 = next(k for k, r in enumerate(r2) if r[0] and str(r[0]).startswith('3.'))
DET = [r for r in r2[i3 + 2:] if isinstance(r[0], int)]
MISS = [r for r in DET if r[4] != 'Bor']
assert sum(y[1] for y in YOR) == JAMI[0] == len(DET) and sum(y[2] for y in YOR) == JAMI[1] and len(MISS) == JAMI[2]
for u, tot, bor, yoq in YOR: assert sum(1 for r in DET if r[1] == u) == tot and sum(1 for r in DET if r[1] == u and r[4] == 'Bor') == bor
nb = sum(1 for _, v in NIZ if v == 'Bor'); nj = sum(1 for _, v in NIZ if v == 'Jarayonda'); ny = len(NIZ) - nb - nj
def pct(a, b): return (f'{a / b * 100:.1f}'.replace('.', ',').removesuffix(',0')) + '%'

# ---------- shablondan 2 ta boʻsh sahifa ----------
shutil.rmtree('un', ignore_errors=True); zipfile.ZipFile(TPL).extractall('un')
for _ in range(2): subprocess.run(['python3', f'{SKILL}/add_slide.py', 'un/', 'slide18.xml', '--after', 'slide35.xml'], check=True, capture_output=True)
pxml = open('un/ppt/presentation.xml').read(); rels = open('un/ppt/_rels/presentation.xml.rels').read()
rid2s = {}
for m in re.finditer(r'<Relationship [^>]*/>', rels):
    a = re.search(r'Id="(rId\d+)"', m.group(0)); t = re.search(r'Target="slides/(slide\d+)\.xml"', m.group(0))
    if a and t: rid2s[a.group(1)] = t.group(1)
lst = re.search(r'<p:sldIdLst>(.*?)</p:sldIdLst>', pxml, re.S).group(1)
by = {rid2s[re.search(r'r:id="(rId\d+)"', e).group(1)]: e for e in re.findall(r'<p:sldId [^>]*/>', lst)}
new = sorted([k for k in by if int(k[5:]) > 35], key=lambda k: int(k[5:]))
open('un/ppt/presentation.xml', 'w').write(pxml.replace(lst, ''.join(by[k] for k in new)))
subprocess.run(['python3', f'{SKILL}/clean.py', 'un/'], check=True, capture_output=True)
if os.path.exists('base.pptx'): os.remove('base.pptx')
subprocess.run('cd un && zip -qXrD ../base.pptx .', shell=True, check=True)
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
def box(sl, x, y, w, h, color, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.08, line=None):
    s = sl.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h)); s.fill.solid(); s.fill.fore_color.rgb = rgb(color); s.shadow.inherit = False
    if line: s.line.color.rgb = rgb(line); s.line.width = Pt(1.25)
    else: s.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: s.adjustments[0] = adj
    return s
def pill(sl, x, y, w, t, color):
    b = box(sl, x, y, w, 0.28, color, adj=0.5); tf = b.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.text = t; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.runs[0]; r.font.size = Pt(9); r.font.bold = True; r.font.name = 'Segoe UI'; r.font.color.rgb = rgb(DARK)
def line(sl, x1, y1, x2, y2, color='4A515B', w=1.5):
    c = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)); c.line.color.rgb = rgb(color); c.line.width = Pt(w)
def settext(sh, t):
    p = sh.text_frame.paragraphs[0]; p.runs[0].text = t
    for r in p.runs[1:]: r._r.getparent().remove(r._r)
    for e in sh.text_frame.paragraphs[1:]: e._p.getparent().remove(e._p)
def header(sl, num, title, sub, pg):
    for sh in list(sl.shapes):
        if not sh.name.startswith('!!') or sh.name in ('!!c1', '!!c2', '!!c3', '!!c4'):
            if sh.shape_type == 3:
                rid = sh._element.xpath('.//c:chart/@r:id')
                if rid: sl.part.drop_rel(rid[0])
            sh._element.getparent().remove(sh._element)
        elif sh.name == '!!num': settext(sh, num)
        elif sh.name == '!!title': settext(sh, title)
        elif sh.name == '!!sub': settext(sh, sub)
        elif sh.name == '!!foot': settext(sh, 'Boʻlim nizomlari va lavozim yoʻriqnomalari | ADM Jizzax')
        elif sh.name == '!!pg': settext(sh, f'{pg:02d}')
def donut(sl, x, y, d, vals, colors):
    cd = CategoryChartData(); cd.categories = [str(i) for i in range(len(vals))]; cd.add_series('s', vals)
    gf = sl.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(x), Inches(y), Inches(d), Inches(d), cd); ch = gf.chart
    ch.has_legend = False; ch.has_title = False
    for i, pt in enumerate(ch.plots[0].series[0].points):
        pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(colors[i]); pt.format.line.color.rgb = rgb(CARD); pt.format.line.width = Pt(2)
    hs = ch.plots[0]._element.find('{http://schemas.openxmlformats.org/drawingml/2006/chart}holeSize')
    if hs is not None: hs.set('val', '74')
    return gf
SUB = 'Ishlab chiqarish boshqarmasi (Управление производства) · 4 ta sex va 2 ta boʻlim'

# ================= 1-SAHIFA: BOʻLIM NIZOMLARI =================
sl = slides[0]; header(sl, '01', 'Boʻlim nizomlari holati', SUB, 1)
box(sl, 0.55, 1.30, 3.55, 5.45, CARD)
text(sl, 0.85, 1.50, 3.0, 0.3, 'NIZOM TASDIQLANGAN', 9, TEAL, 'Segoe UI Semibold')
donut(sl, 0.92, 1.85, 2.8, [nb, nj, ny] if ny else [nb, nj], [TEAL, AMBER, CORAL])
text(sl, 0.92, 2.72, 2.8, 0.6, pct(nb, len(NIZ)), 30, TXT, 'Segoe UI Light', align=PP_ALIGN.CENTER)
text(sl, 0.92, 3.28, 2.8, 0.3, f'{nb} / {len(NIZ)} boʻlinma', 10, MUTED, align=PP_ALIGN.CENTER)
for i, (lab, n, c) in enumerate([('Nizom bor', nb, TEAL), ('Jarayonda', nj, AMBER), ('Nizom yoʻq', ny, CORAL)]):
    y = 4.85 + i * 0.5
    box(sl, 0.85, y + 0.08, 0.22, 0.22, c, adj=0.3)
    text(sl, 1.2, y, 2.0, 0.4, lab, 12, TXT, anchor=MSO_ANCHOR.MIDDLE)
    text(sl, 3.0, y, 0.8, 0.4, str(n), 18, c, 'Segoe UI Semibold', align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
# daraxt
box(sl, 4.30, 1.30, 8.50, 5.45, CARD)
top = box(sl, 6.55, 1.52, 4.0, 0.62, '363C44', adj=0.2)
text(sl, 6.55, 1.52, 4.0, 0.62, [('Ishlab chiqarish boshqarmasi', {'font': 'Segoe UI Semibold', 'size': 12}), ('\n', {}), ('Управление производства', {'size': 9, 'color': MUTED})], 12, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
units = [u for u, _ in NIZ if 'Пластиков' not in u]; st = dict(NIZ)
plast = next((u for u, _ in NIZ if 'Пластиков' in u), None)
cw, chh, gx = 2.55, 1.30, 0.22
xs = [4.55 + j * (cw + gx) for j in range(3)]; ys = [2.62, 4.25]
line(sl, 8.55, 2.14, 8.55, 2.38); line(sl, xs[0] + cw / 2, 2.38, xs[2] + cw / 2, 2.38)
for j in range(3): line(sl, xs[j] + cw / 2, 2.38, xs[j] + cw / 2, 2.62)
for i, u in enumerate(units):
    x, y = xs[i % 3], ys[i // 3]
    c = TEAL if st[u] == 'Bor' else (AMBER if st[u] == 'Jarayonda' else CORAL)
    box(sl, x, y, cw, chh, '363C44', adj=0.1); box(sl, x, y, 0.07, chh, c, MSO_SHAPE.RECTANGLE)
    kind = 'BOʻLIM' if 'Отдел' in u else 'SEX'
    text(sl, x + 0.2, y + 0.1, cw - 0.3, 0.2, kind, 7.5, DIM, 'Segoe UI Semibold')
    text(sl, x + 0.2, y + 0.28, cw - 0.3, 0.55, [(UZ.get(u, u), {'font': 'Segoe UI Semibold', 'size': 10.5}), ('\n', {}), (u, {'size': 8, 'color': MUTED})], 10.5)
    pill(sl, x + 0.2, y + chh - 0.40, 1.25, '✓ Nizom bor' if st[u] == 'Bor' else ('◔ Jarayonda' if st[u] == 'Jarayonda' else '✗ Yoʻq'), c)
# 2-qatorga ulash: chap tomondan tushadigan shina
by2 = ys[1] - 0.16
line(sl, xs[0] + cw / 2, 2.38, 4.42, 2.38); line(sl, 4.42, 2.38, 4.42, by2); line(sl, 4.42, by2, xs[2] + cw / 2, by2)
for j in range(3): line(sl, xs[j] + cw / 2, by2, xs[j] + cw / 2, ys[1])
# plastik bo'yoqlash — Bo'yoqlash sexi tarkibida
if plast:
    oi = units.index('Окрасочный цех'); ox, oy = xs[oi % 3], ys[oi // 3]
    px, py = ox + 0.25, oy + chh + 0.22
    line(sl, ox + 0.12, oy + chh, ox + 0.12, py + 0.33, AMBER, 1.25); line(sl, ox + 0.12, py + 0.33, px, py + 0.33, AMBER, 1.25)
    box(sl, px, py, cw - 0.25, 0.66, '3A3428', adj=0.15, line=AMBER)
    text(sl, px + 0.12, py + 0.06, cw - 0.45, 0.55, [('Plastik boʻyoqlash sexi', {'font': 'Segoe UI Semibold', 'size': 9.5}), ('\n', {}), ('Boʻyoqlash sexi tarkibida · ', {'size': 8, 'color': MUTED}), ('JARAYONDA', {'size': 8, 'color': AMBER, 'font': 'Segoe UI Semibold'})], 9.5)
text(sl, 0.55, 6.85, 12.25, 0.3, [('Xulosa: ', {'font': 'Segoe UI Semibold', 'color': TEAL}),
     (f'{len(NIZ)} ta boʻlinmadan {nb} tasida boʻlim nizomi bor ({pct(nb, len(NIZ))}). Plastik boʻyoqlash sexi (Boʻyoqlash sexi tarkibida) nizomi — jarayonda. Nizomi yoʻq boʻlinma yoʻq.', {})], 10, MUTED)

# ================= 2-SAHIFA: LAVOZIM YOʻRIQNOMALARI =================
sl = slides[1]; header(sl, '02', 'Lavozim yoʻriqnomalari holati', SUB, 2)
tot, bor, yoq = JAMI
box(sl, 0.55, 1.30, 5.55, 5.45, CARD)
text(sl, 0.85, 1.50, 5.0, 0.3, 'YOʻRIQNOMASI BOR LAVOZIMLAR', 9, TEAL, 'Segoe UI Semibold')
text(sl, 0.85, 1.78, 3.2, 1.0, pct(bor, tot), 54, TEAL, 'Segoe UI Light')
text(sl, 3.75, 1.98, 2.2, 0.8, [(f'{bor}', {'size': 26, 'font': 'Segoe UI Semibold'}), (f' / {tot}', {'size': 18, 'color': MUTED}), ('\n', {}), ('lavozim', {'size': 10, 'color': MUTED})], 26, align=PP_ALIGN.RIGHT)
# vafli: har kvadrat = 1 lavozim
cols = 17; sq, g = 0.245, 0.045; wx, wy = 0.85, 2.95
k = 0; order = [(u, r[4]) for r in DET for u in [r[1]]]
for idx, r in enumerate(DET):
    cx, cy = wx + (idx % cols) * (sq + g), wy + (idx // cols) * (sq + g)
    box(sl, cx, cy, sq, sq, TEAL if r[4] == 'Bor' else CORAL, adj=0.18)
text(sl, 0.85, wy + 7 * (sq + g) + 0.12, 5.0, 0.3, [('■ ', {'color': TEAL}), ('yoʻriqnoma bor   ', {}), ('■ ', {'color': CORAL}), ('yoʻriqnoma yoʻq   ·   1 kvadrat = 1 lavozim', {})], 9, MUTED)
m = MISS[0] if MISS else None
if m:
    box(sl, 0.85, 5.62, 4.95, 0.92, '3A2E2C', adj=0.12, line=CORAL)
    text(sl, 1.05, 5.70, 4.6, 0.8, [('YOʻRIQNOMASI YOʻQ', {'font': 'Segoe UI Semibold', 'size': 8.5, 'color': CORAL}), ('\n', {}),
         (f'{m[3]}', {'font': 'Segoe UI Semibold', 'size': 13}), (f'  —  {UZ.get(m[1], m[1])}', {'size': 10, 'color': MUTED}), ('\n', {}), (f'{m[1]} · manba: {m[5]}', {'size': 8, 'color': DIM})], 13)
# bo'linmalar bo'yicha
box(sl, 6.30, 1.30, 6.50, 5.45, CARD)
text(sl, 6.60, 1.50, 6.0, 0.3, 'BOʻLINMALAR BOʻYICHA', 9, TEAL, 'Segoe UI Semibold')
for i, (u, t_, b_, y_) in enumerate(YOR):
    y = 1.95 + i * 0.74
    c = TEAL if b_ == t_ else (AMBER if b_ / t_ >= 0.5 else CORAL)
    text(sl, 6.60, y, 3.45, 0.45, [(UZ.get(u, u), {'font': 'Segoe UI Semibold', 'size': 10.5}), ('\n', {}), (u, {'size': 8, 'color': MUTED})], 11)
    box(sl, 10.15, y + 0.14, 1.25, 0.14, TRACK, adj=0.5); box(sl, 10.15, y + 0.14, 1.25 * b_ / t_, 0.14, c, adj=0.5)
    text(sl, 11.5, y - 0.02, 1.15, 0.45, [(pct(b_, t_), {'font': 'Segoe UI Semibold', 'size': 13, 'color': c}), ('\n', {}), (f'{b_} / {t_}', {'size': 8.5, 'color': MUTED})], 13, align=PP_ALIGN.RIGHT)
    if i: box(sl, 6.60, y - 0.13, 6.0, 0.008, '3D434C', MSO_SHAPE.RECTANGLE)
text(sl, 6.60, 6.40, 6.0, 0.3, 'Yigʻuv sexidagi «Практикант» (Лист1!C498) ro‘yxat hisobiga kiritilmagan — aniqlashtirish tavsiya etiladi.', 8, DIM)
text(sl, 0.55, 6.85, 12.25, 0.3, [('Xulosa: ', {'font': 'Segoe UI Semibold', 'color': TEAL}),
     (f'{tot} ta lavozimdan {bor} tasida yoʻriqnoma bor ({pct(bor, tot)}). 5 ta boʻlinmada — 100%. Faqat 1 ta lavozim qoldi: {m[3]} ({UZ.get(m[1], m[1])}).', {})], 10, MUTED)
pres.save(OUT)
print('ok', OUT, '| nizom', nb, nj, ny, '| yoriqnoma', tot, bor, yoq)
