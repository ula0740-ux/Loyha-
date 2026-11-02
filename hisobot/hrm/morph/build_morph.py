# -*- coding: utf-8 -*-
"""HRM 2026 · Сентабр — Morph uslubidagi PowerPoint.

Namuna: "Morph PowerPoint Template" videosi (to'q slate fon, firuza aksent,
markazdagi logo atrofida konsentrik halqalar, logo chapga siljiydi, mundarija
chiziqlar bilan chiqadi, bo'lim slaydlarida katta raqam + chevron).

Morph: bir xil "!!nom" li shakllar slaydlar orasida silliq ko'chadi.
PowerPoint 2019 / 2021 / 365 kerak (eskisida oddiy fade bo'ladi).

    python3 hisobot/hrm/morph/build_morph.py
"""
import os
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets')
OUT = os.path.join(HERE, 'HRM_2026_Sentabr_Morph.pptx')

# ---------- palitra (videodan) ----------
BG = '262A30'      # asosiy fon
BG2 = '2F343B'     # kartochka
BG3 = '363C44'     # kartochka ichidagi blok
LINE = '434A53'
TEAL = '3CC6B8'
TEAL2 = '2A8F86'
TEAL3 = '1F5F5A'
WHITE = 'EDEBEB'
MUTED = '9AA2AC'
DIM = '6B737D'
WARN = 'E8826E'    # past natija (logo rangiga yaqin)

F = 'Segoe UI'
FL = 'Segoe UI Light'
FS = 'Segoe UI Semibold'

W, H = 13.333, 7.5
IN = 914400


def E(v):
    return Emu(int(round(v * IN)))


def rgb(h):
    return RGBColor.from_string(h)


# ---------- past darajadagi yordamchilar ----------
def _alpha(el, a):
    """srgbClr ichiga shaffoflik qo'shadi (a: 0..1)."""
    if a is None or a >= 1:
        return
    for c in el.iter(qn('a:srgbClr')):
        al = etree.SubElement(c, qn('a:alpha'))
        al.set('val', str(int(a * 100000)))


def shape(s, kind, x, y, w, h, fill=None, line=None, lw=0.75, name=None,
          alpha=None, lalpha=None, adj=None, rot=0, flip=False):
    sh = s.shapes.add_shape(kind, E(x), E(y), E(w), E(h))
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
        _alpha(sh.fill._xPr.find(qn('a:solidFill')), alpha)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(lw)
        ln = sh.line._get_or_add_ln()
        _alpha(ln, lalpha)
    else:
        sh.line.fill.background()
    if adj:
        for i, v in enumerate(adj):
            sh.adjustments[i] = v
    if rot:
        sh.rotation = rot
    if flip:
        sh._element.spPr.find(qn('a:xfrm')).set('flipH', '1')
    sh.shadow.inherit = False
    if name:
        sh.name = name
    tf = sh.text_frame
    tf.text = ''
    return sh


def rect(s, x, y, w, h, fill=BG2, line=None, r=0.06, name=None, alpha=None, lw=0.75, lalpha=None):
    k = MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE
    sh = shape(s, k, x, y, w, h, fill, line, lw, name, alpha, lalpha)
    if r:
        sh.adjustments[0] = min(0.5, r / min(w, h))
    return sh


def card(s, x, y, w, h, name=None, fill=BG2):
    return rect(s, x, y, w, h, fill=fill, line=LINE, r=0.08, name=name, lw=0.5)


def text(s, x, y, w, h, t, size=12, color=WHITE, font=F, bold=False, align='l',
         anchor='t', name=None, lsp=None, italic=False, wrap=True):
    tb = s.shapes.add_textbox(E(x), E(y), E(w), E(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    lines = t if isinstance(t, list) else [t]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
        if lsp:
            p.line_spacing = lsp
        runs = ln if isinstance(ln, list) else [(ln, {})]
        for rt in runs:
            if isinstance(rt, str):
                rt = (rt, {})
            r = p.add_run()
            r.text = rt[0]
            o = rt[1]
            r.font.size = Pt(o.get('size', size))
            r.font.name = o.get('font', font)
            r.font.bold = o.get('bold', bold)
            r.font.italic = italic
            r.font.color.rgb = rgb(o.get('color', color))
    return tb


def pic(s, path, x, y, w=None, h=None, name=None):
    p = s.shapes.add_picture(os.path.join(A, path), E(x), E(y),
                             E(w) if w else None, E(h) if h else None)
    if name:
        p.name = name
    return p


def pic_fill(s, path, x, y, w, h, name=None):
    """Rasmni ramkaga 'cover' qilib qirqib joylaydi."""
    from PIL import Image
    im = Image.open(os.path.join(A, path))
    iw, ih = im.size
    p = s.shapes.add_picture(os.path.join(A, path), E(x), E(y), E(w), E(h))
    fr, ir = w / h, iw / ih
    if ir > fr:
        c = (1 - fr / ir) / 2
        p.crop_left = p.crop_right = c
    else:
        c = (1 - ir / fr) / 2
        p.crop_top = p.crop_bottom = c
    if name:
        p.name = name
    return p


def morph(s, dur=1250):
    xml = (
        '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
        '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
        '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="%d">'
        '<p159:morph option="byObject"/></p:transition></mc:Choice>'
        '<mc:Fallback><p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="slow">'
        '<p:fade/></p:transition></mc:Fallback></mc:AlternateContent>' % dur)
    el = etree.fromstring(xml)
    sld = s._element
    timing = sld.find(qn('p:timing'))
    if timing is not None:
        timing.addprevious(el)
    else:
        sld.append(el)


# ---------- jadval ----------
NOSTYLE = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'


def table(s, x, y, w, rows, colw, rh=0.3, size=10, head=True, total=False,
          align=None, name=None, colors=None, hsize=None):
    nr, nc = len(rows), len(rows[0])
    gf = s.shapes.add_table(nr, nc, E(x), E(y), E(w), E(rh * nr))
    if name:
        gf.name = name
    tbl = gf.table
    tbl._tbl.tblPr.find(qn('a:tableStyleId')).text = NOSTYLE
    tbl.first_row = False
    tbl.horz_banding = False
    tw = sum(colw)
    for j, cw in enumerate(colw):
        tbl.columns[j].width = E(w * cw / tw)
    for i, row in enumerate(rows):
        tbl.rows[i].height = E(rh)
        is_h = head and i == 0
        is_t = total and i == nr - 1
        for j, v in enumerate(row):
            c = tbl.cell(i, j)
            c.margin_left = c.margin_right = E(0.08)
            c.margin_top = c.margin_bottom = E(0.02)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            if is_h:
                c.fill.fore_color.rgb = rgb(TEAL3)
            elif is_t:
                c.fill.fore_color.rgb = rgb(BG3)
            else:
                c.fill.fore_color.rgb = rgb(BG2 if i % 2 else '2B3036')
            tf = c.text_frame
            tf.word_wrap = True
            tf.text = ''
            p = tf.paragraphs[0]
            a = (align[j] if align else ('l' if j == 0 else 'c'))
            p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[a]
            r = p.add_run()
            r.text = str(v)
            r.font.size = Pt(hsize if (is_h and hsize) else size)
            r.font.name = FS if (is_h or is_t) else F
            col = WHITE
            if is_h:
                col = TEAL
            elif colors and (i, j) in colors:
                col = colors[(i, j)]
            r.font.color.rgb = rgb(col)
            # chiziqlar
            tcPr = c._tc.get_or_add_tcPr()
            for tag in ('a:lnL', 'a:lnR', 'a:lnT', 'a:lnB'):
                ln = etree.SubElement(tcPr, qn(tag))
                if tag == 'a:lnB':
                    ln.set('w', '6350')
                    sf = etree.SubElement(ln, qn('a:solidFill'))
                    etree.SubElement(sf, qn('a:srgbClr')).set('val', LINE)
                else:
                    ln.set('w', '0')
                    etree.SubElement(ln, qn('a:noFill'))
            # lnX lar fill dan oldin turishi kerak
            fill = tcPr.find(qn('a:solidFill'))
            if fill is not None:
                tcPr.remove(fill)
                tcPr.append(fill)
    return gf


# ---------- diagrammalar ----------
def _nofill(chart):
    cs = chart._chartSpace
    sp = cs.find(qn('c:spPr'))
    if sp is None:
        sp = etree.SubElement(cs, qn('c:spPr'))
        # spPr c:chart dan keyin turishi kerak
        cs.remove(sp)
        cs.find(qn('c:chart')).addnext(sp)
    etree.SubElement(sp, qn('a:noFill'))
    ln = etree.SubElement(sp, qn('a:ln'))
    etree.SubElement(ln, qn('a:noFill'))


def _style(ch, legend=False, size=9, vaxis=False, cat_size=None):
    _nofill(ch)
    ch.has_title = False
    ch.font.size = Pt(size)
    ch.font.name = F
    ch.font.color.rgb = rgb(MUTED)
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.TOP
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(size)
        ch.legend.font.color.rgb = rgb(MUTED)
    try:
        ca = ch.category_axis
        ca.format.line.color.rgb = rgb(LINE)
        ca.has_major_gridlines = False
        ca.tick_labels.font.size = Pt(cat_size or size)
        ca.tick_labels.font.color.rgb = rgb(MUTED)
        from pptx.enum.chart import XL_TICK_MARK
        ca.major_tick_mark = XL_TICK_MARK.NONE
        va = ch.value_axis
        va.has_major_gridlines = vaxis
        if vaxis:
            va.major_gridlines.format.line.color.rgb = rgb('363C44')
            va.format.line.fill.background()
            va.tick_labels.font.color.rgb = rgb(DIM)
            va.tick_labels.font.size = Pt(size - 1)
            va.major_tick_mark = XL_TICK_MARK.NONE
        else:
            va.visible = False
    except (ValueError, AttributeError):
        pass


def _labels(plot, fmt='0', size=9, color=WHITE, pos=XL_LABEL_POSITION.OUTSIDE_END):
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format = fmt
    dl.number_format_is_linked = False
    dl.font.size = Pt(size)
    dl.font.color.rgb = rgb(color)
    dl.font.name = FS
    if pos is not None:
        dl.position = pos


def bars(s, x, y, w, h, cats, vals, horiz=True, color=TEAL, name=None, fmt='0',
         gap=55, size=9, hi=None, cat_size=None, labels=True, vmax=None):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series('S', vals)
    t = XL_CHART_TYPE.BAR_CLUSTERED if horiz else XL_CHART_TYPE.COLUMN_CLUSTERED
    gf = s.shapes.add_chart(t, E(x), E(y), E(w), E(h), cd)
    if name:
        gf.name = name
    ch = gf.chart
    _style(ch, size=size, cat_size=cat_size)
    pl = ch.plots[0]
    pl.gap_width = gap
    ser = pl.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(color)
    if hi:
        for i, c in hi.items():
            pt = ser.points[i]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = rgb(c)
    if labels:
        _labels(pl, fmt, size)
    if vmax:
        ch.value_axis.maximum_scale = vmax
    ch.value_axis.minimum_scale = 0
    return gf


def multi(s, x, y, w, h, cats, series, kind='col', name=None, fmt='0', size=9,
          legend=True, gap=60, overlap=-10, labels=True, vaxis=False, lab_size=None):
    cd = CategoryChartData()
    cd.categories = cats
    for nm, vals, _ in series:
        cd.add_series(nm, vals)
    t = {'col': XL_CHART_TYPE.COLUMN_CLUSTERED, 'bar': XL_CHART_TYPE.BAR_CLUSTERED,
         'line': XL_CHART_TYPE.LINE_MARKERS}[kind]
    gf = s.shapes.add_chart(t, E(x), E(y), E(w), E(h), cd)
    if name:
        gf.name = name
    ch = gf.chart
    _style(ch, legend=legend, size=size, vaxis=vaxis)
    pl = ch.plots[0]
    if kind != 'line':
        pl.gap_width = gap
        pl.overlap = overlap
    for ser, (_, _, col) in zip(pl.series, series):
        if kind == 'line':
            ser.format.line.color.rgb = rgb(col)
            ser.format.line.width = Pt(2.5)
            ser.smooth = True
            ser.marker.style = 8  # circle
            ser.marker.size = 7
            ser.marker.format.fill.solid()
            ser.marker.format.fill.fore_color.rgb = rgb(BG)
            ser.marker.format.line.color.rgb = rgb(col)
            ser.marker.format.line.width = Pt(2)
        else:
            ser.format.fill.solid()
            ser.format.fill.fore_color.rgb = rgb(col)
    if labels:
        _labels(pl, fmt, lab_size or size,
                pos=XL_LABEL_POSITION.ABOVE if kind == 'line' else XL_LABEL_POSITION.OUTSIDE_END)
    return gf


def donut(s, x, y, w, h, cats, vals, colors, name=None, hole=68):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series('S', vals)
    gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, E(x), E(y), E(w), E(h), cd)
    if name:
        gf.name = name
    ch = gf.chart
    _nofill(ch)
    ch.has_title = False
    ch.has_legend = False
    ser = ch.plots[0].series[0]
    for i, c in enumerate(colors):
        pt = ser.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(c)
        pt.format.line.color.rgb = rgb(BG2)
        pt.format.line.width = Pt(2)
    hs = ch._chartSpace.find('.//' + qn('c:holeSize'))
    if hs is not None:
        hs.set('val', str(hole))
    return gf


# ---------- kompozit bloklar ----------
def kpi(s, x, y, w, h, val, label, sub=None, name=None, vsize=30, accent=TEAL, vcolor=WHITE):
    card(s, x, y, w, h, name=name)
    rect(s, x, y + 0.18, 0.06, h - 0.36, fill=accent, r=0)
    text(s, x + 0.25, y + 0.14, w - 0.35, 0.3, label.upper(), 8.5, MUTED, FS)
    text(s, x + 0.25, y + 0.38, w - 0.35, h - 0.5, val, vsize, vcolor, FL, anchor='t')
    if sub:
        text(s, x + 0.25, y + h - 0.36, w - 0.35, 0.3, sub, 8.5, DIM)


def label(s, x, y, w, t, color=TEAL, size=9):
    text(s, x, y, w, 0.25, t.upper(), size, color, FS)


def num_badge(s, x, y, n, d=0.36, fill=TEAL, color=BG, size=10):
    o = shape(s, MSO_SHAPE.OVAL, x, y, d, d, fill=fill)
    text(s, x, y, d, d, str(n), size, color, FS, align='c', anchor='m')
    return o


def hbar_rows(s, x, y, w, rows, vmax, rh=0.3, lw=None, color=TEAL, size=9.5, fmt=str, vw=0.6):
    """[(label, value)] — matn + ingichka gorizontal chiziq."""
    lw = lw if lw is not None else w * 0.55
    bw = w - lw - vw
    for i, (lab, v) in enumerate(rows):
        yy = y + i * rh
        text(s, x, yy, lw - 0.1, rh, lab, size, WHITE, anchor='m')
        rect(s, x + lw, yy + rh * 0.38, bw, rh * 0.24, fill=BG3, r=0.05)
        c = color(v) if callable(color) else color
        rect(s, x + lw, yy + rh * 0.38, max(0.04, bw * v / vmax), rh * 0.24, fill=c, r=0.05)
        text(s, x + lw + bw + 0.08, yy, vw, rh, fmt(v), size, WHITE, FS, anchor='m')


# ---------- Morph doimiy elementlari ----------
RINGS = [  # (nom, diametr, fill, line)
    ('!!r4', 9.2, '2B3037', '3A4148'),
    ('!!r3', 7.0, '30353D', '434A53'),
    ('!!r2', 5.0, '2A2F36', '4B535C'),
    ('!!r1', 3.4, '343A42', '58616B'),
]


LIGHT_RINGS = ['E2DDDF', 'D3CECF', 'BFBABC', 'D8D3D5']


def soft(sh, rad_in):
    spPr = sh._element.spPr
    ef = etree.SubElement(spPr, qn('a:effectLst'))
    etree.SubElement(ef, qn('a:softEdge')).set('rad', str(int(rad_in * IN)))


def rings(s, cx, cy, k=1.0, alpha=1.0, arc=True, light=False, rot=None):
    for i, (nm, d, fill, ln) in enumerate(RINGS):
        dd = d * k
        if light:
            sh = shape(s, MSO_SHAPE.OVAL, cx - dd / 2, cy - dd / 2, dd, dd, fill=LIGHT_RINGS[i], name=nm)
            soft(sh, 0.35 * k)
            continue
        shape(s, MSO_SHAPE.OVAL, cx - dd / 2, cy - dd / 2, dd, dd, fill=fill, line=ln, lw=0.75,
              name=nm, alpha=alpha, lalpha=alpha)
    if arc:
        spin(s, cx, cy, k, rot or (0, 0), light)


class _In:
    """Guruh ichiga shakl qo'shish uchun (shape() s.shapes ni kutadi)."""
    def __init__(self, g):
        self.shapes = g.shapes


# (guruh nomi, diametr, yoy boshi, yoy oxiri, rang, qalinlik, asosiy burilish)
# 2-yoy 270° burilgan holda chiziladi: shunda u 1-yoyga teskari aylanadi.
ARCS = [('!!spin1', 4.2, 200, 320, TEAL, 2.25, 0),
        ('!!spin2', 6.0, 110, 185, TEAL2, 1.25, 270)]


def spin(s, cx, cy, k, rot, light=False):
    """Firuza yoy + nuqta bitta guruhda. Morph guruhning burilishini
    animatsiya qiladi: slaydlar orasida yoylar markaz atrofida aylanadi."""
    import math
    dot = 0.14 * max(k, 0.8)
    for (nm, dia, a0, a1, col, lw, base), r in zip(ARCS, rot):
        if light:
            col, lw = 'A9A4A6', lw * 0.8
        d = dia * k
        g = s.shapes.add_group_shape()
        gi = _In(g)
        pad = dot
        # shaffof kvadrat: guruh markazi = halqa markazi bo'lsin
        shape(gi, MSO_SHAPE.RECTANGLE, cx - d / 2 - pad, cy - d / 2 - pad, d + 2 * pad, d + 2 * pad)
        a = shape(gi, MSO_SHAPE.ARC, cx - d / 2, cy - d / 2, d, d, line=col, lw=lw)
        # python-pptx qiymatni 100000 ga ko'paytiradi, OOXML burchak birligi 60000/°
        a.adjustments[0] = (a0 % 360) * 0.6
        a.adjustments[1] = (a1 % 360) * 0.6
        px = cx + d / 2 * math.cos(math.radians(a0))
        py = cy + d / 2 * math.sin(math.radians(a0))
        shape(gi, MSO_SHAPE.OVAL, px - dot / 2, py - dot / 2, dot, dot, fill=col)
        g.name = nm
        g._element.grpSpPr.get_or_add_xfrm().set('rot', str(int(((base + r) % 360) * 60000)))


def disc(s, cx, cy, d, light=False):
    shape(s, MSO_SHAPE.OVAL, cx - d / 2, cy - d / 2, d, d, fill='F1EDEF' if light else WHITE, name='!!disc')
    m = d * 0.56
    pic(s, 'mark_gray.png' if light else 'mark_duo.png', cx - m / 2, cy - m / 2, m, m, name='!!mark')


def brand(s):
    """ADM logosi: yuqori chap burchakda, xira."""
    pic(s, 'word_dim.png', 0.62, 0.2, 0.85, None, name='!!brand')


def fullbg(s, color):
    rect(s, 0, 0, W, H, fill=color, r=0, name='!!bg')


def chevron(s, vx, vy, k):
    """Videodagi "<" belgisi: ikki yumaloq bo'lak + firuza uchburchaklar.
    (vx, vy) — uchi, k — masshtab."""
    import math
    T, dx, dy = 1.2 * k, 1.5 * k, 2.4 * k
    L = math.hypot(dx, dy) + T
    ang = math.degrees(math.atan2(dx, dy))
    t = shape(s, MSO_SHAPE.ISOSCELES_TRIANGLE, vx - 0.45 * k, vy - 0.5 * k, 1.0 * k, 0.9 * k,
              fill=TEAL2, name='!!chT2', alpha=0.9)
    t.rotation = 270
    for nm, sign in (('!!chA', -1), ('!!chB', 1)):
        cx, cy = vx + dx / 2, vy + sign * dy / 2
        sh = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, cx - T / 2, cy - L / 2, T, L, fill='D9D6D8',
                   name=nm, alpha=0.62)
        sh.adjustments[0] = 0.5
        sh.rotation = ang if sign < 0 else 360 - ang
    t = shape(s, MSO_SHAPE.ISOSCELES_TRIANGLE, vx + 1.0 * k, vy - 0.3 * k, 0.55 * k, 0.6 * k,
              fill=TEAL, name='!!chT1', alpha=0.95)
    t.rotation = 270


def spin_anim(s, turns=1.5, dur=1900):
    """Slayd ochilishi bilan '!!spin1/2' guruhlari avtomatik aylanadi
    (Morph 360° dan katta burilishni ko'rsatmaydi, shuning uchun Spin effekti).
    1-yoy soat strelkasi bo'yicha, 2-yoy teskari; boshida tezlashib, oxirida sekinlashadi."""
    ids = {sh.name: sh.shape_id for sh in s.shapes if sh.name in ('!!spin1', '!!spin2')}
    by = int(turns * 360 * 60000)
    P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    effs, n = '', 5
    for nm, sign in (('!!spin1', 1), ('!!spin2', -1)):
        effs += ('<p:par><p:cTn id="%d" presetID="8" presetClass="emph" presetSubtype="0" accel="15000" decel="65000" fill="hold" nodeType="withEffect">'
                 '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:animRot by="%d"><p:cBhvr>'
                 '<p:cTn id="%d" dur="%d" fill="hold"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>'
                 '<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot></p:childTnLst></p:cTn></p:par>'
                 % (n, sign * by, n + 1, dur, ids[nm]))
        n += 2
    xml = ('<p:timing xmlns:p="%s"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
           '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
           '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
           '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>%s</p:childTnLst></p:cTn></p:par>'
           '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
           '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>') % (P, effs)
    s._element.append(etree.fromstring(xml))


class Deck:
    def __init__(self):
        self.p = Presentation()
        self.p.slide_width = E(W)
        self.p.slide_height = E(H)
        self.layout = self.p.slide_layouts[6]
        self.n = 0

    def new(self):
        s = self.p.slides.add_slide(self.layout)
        bg = s.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb(BG)
        self.n += 1
        return s

    def footer(self, s):
        brand(s)
        text(s, 0.55, H - 0.4, 3, 0.25, 'HRM | Ҳисобот 2026', 8, DIM, name='!!foot')
        text(s, W - 1.15, H - 0.42, 0.6, 0.25, '%02d' % self.n, 8, TEAL, FS, align='r', name='!!pg')

    # --- bo'lim slaydi ---
    def section(self, num, title, sub=''):
        s = self.new()
        rings(s, 12.4, 3.75, k=1.05, arc=True, rot=(320, -220))
        # ghost kartochkalar (keyingi slaydda haqiqiy kartochkalarga aylanadi)
        for i, (gx, gy) in enumerate(((6.6, 0.75), (9.75, 0.75), (6.6, 3.9), (9.75, 3.9))):
            rect(s, gx, gy, 3.0, 2.95, fill=BG2, line=LINE, r=0.08, name='!!c%d' % (i + 1),
                 alpha=0.35, lalpha=0.5)
        chevron(s, 0.7, 3.75, 1.05)
        text(s, 3.15, 0.85, 4.0, 1.3, title, 28, WHITE, FL, name='!!title', lsp=0.95, anchor='b')
        text(s, 3.05, 2.55, 3.4, 2.1, num, 130, WHITE, FL, name='!!num', anchor='m')
        rect(s, 3.25, 4.75, 0.9, 0.05, fill=TEAL, r=0, name='!!acc')
        if sub:
            text(s, 3.25, 4.95, 3.3, 1.0, sub, 11.5, MUTED, name='!!sub')
        self.footer(s)
        morph(s)
        return s

    # --- kontent slaydi ---
    def content(self, num, title, sub=None):
        s = self.new()
        rings(s, 14.6, 8.4, k=0.9, alpha=0.55, arc=False)
        chevron(s, 0.02, 0.84, 0.2)
        text(s, 0.62, 0.52, 0.8, 0.6, num, 26, WHITE, FL, name='!!num', anchor='m')
        rect(s, 1.42, 0.6, 0.04, 0.42, fill=TEAL, r=0, name='!!acc')
        text(s, 1.6, 0.43, 10.6, 0.5, title, 22, WHITE, FL, name='!!title')
        if sub:
            text(s, 1.62, 0.93, 11.0, 0.3, sub, 10, MUTED, name='!!sub')
        self.footer(s)
        morph(s)
        return s

    def save(self):
        self.p.save(OUT)


# =====================================================================
def build():
    d = Deck()

    # 0 — oppoq ochilish: oq fon, yumshoq kulrang halqalar, logo markazda
    s = d.new()
    s.background.fill.fore_color.rgb = rgb('ECE8EA')
    fullbg(s, 'ECE8EA')
    rings(s, W / 2, H / 2 - 0.2, k=0.62, light=True, rot=(0, 0))
    disc(s, W / 2, H / 2 - 0.2, 1.25, light=True)
    morph(s, 1600)

    # 1 — rang to'q tusga o'tadi, halqalar kengayadi
    s = d.new()
    fullbg(s, BG)
    rings(s, W / 2, H / 2 - 0.2, k=1.12, rot=(0, 0))
    disc(s, W / 2, H / 2 - 0.2, 2.2)
    pic(s, 'word_white.png', W / 2 - 0.9, H - 0.78, 1.8, None, name='!!brand')
    morph(s, 1100)
    spin_anim(s, 1.5, 1900)

    # 1 — muqova
    s = d.new()
    rings(s, 3.55, 3.75, k=1.0, rot=(120, -60))
    disc(s, 3.55, 3.75, 2.05)
    text(s, 7.1, 2.0, 5.6, 0.4, 'ADM JIZZAKH AJ', 12, TEAL, FS, name='!!sub')
    text(s, 7.1, 2.45, 5.8, 1.9, ['HRM', 'Ҳисоботи 2026'], 44, WHITE, FL, name='!!title', lsp=0.92)
    text(s, 7.15, 4.35, 5.2, 0.4, 'Инсон ресурслари · 9 ой натижалари', 13, MUTED, name='!!foot')
    pill = rect(s, 7.1, 5.15, 3.6, 0.6, fill=WHITE, r=0.3, name='!!pill', alpha=0.12)
    text(s, 7.1, 5.15, 3.6, 0.6, 'Сентабр 2026', 15, WHITE, F, align='c', anchor='m', name='!!pilltx')
    rect(s, 7.1, 5.95, 1.0, 0.04, fill=TEAL, r=0, name='!!acc')
    brand(s)
    morph(s)

    # 2 — mundarija (videodagi "TABLE OF THE CONTENT")
    s = d.new()
    rings(s, W / 2, 3.75, k=0.95, alpha=0.9, rot=(230, -150))
    text(s, W / 2 - 1.6, 3.15, 3.2, 1.2, ['ҲИСОБОТ', 'МУНДАРИЖАСИ'], 22, WHITE, FL,
         align='c', anchor='m', name='!!title', lsp=0.95)
    items = ['Ишга қабул ва адаптация', 'Самарадорлик ва KPI', 'Ўқитишлар', 'Grading тизими',
             'Электрон ариза тизими', 'Корпоратив маданият ва коммуникациялар', 'Интизом бўйича']
    pages = [5, 15, 20, 23, 26, 29, 32]
    left = [(0, 1.15), (1, 2.85), (2, 4.55), (3, 6.05)]
    right = [(4, 1.15), (5, 2.85), (6, 4.55)]
    for i, yy in left:
        text(s, 0.6, yy, 0.9, 0.7, '%02d' % (i + 1), 30, WHITE, FL, anchor='m', name='!!toc%dn' % i)
        rect(s, 1.45, yy + 0.34, 0.9, 0.025, fill=TEAL, r=0, name='!!toc%dl' % i)
        shape(s, MSO_SHAPE.OVAL, 2.33, yy + 0.3, 0.1, 0.1, fill=TEAL, name='!!toc%dd' % i)
        text(s, 2.55, yy + 0.08, 2.6, 0.6, items[i], 13, WHITE, anchor='m', name='!!toc%dt' % i)
        text(s, 2.55, yy + 0.58, 2.6, 0.3, 'слайд %d' % pages[i], 8.5, DIM, name='!!toc%dp' % i)
    for i, yy in right:
        text(s, W - 1.5, yy, 0.9, 0.7, '%02d' % (i + 1), 30, WHITE, FL, align='r', anchor='m',
             name='!!toc%dn' % i)
        rect(s, W - 2.35, yy + 0.34, 0.9, 0.025, fill=TEAL, r=0, name='!!toc%dl' % i)
        shape(s, MSO_SHAPE.OVAL, W - 2.43, yy + 0.3, 0.1, 0.1, fill=TEAL, name='!!toc%dd' % i)
        text(s, W - 6.0, yy + 0.08, 3.45, 0.6, items[i], 13, WHITE, align='r', anchor='m',
             name='!!toc%dt' % i)
        text(s, W - 6.0, yy + 0.62, 3.45, 0.3, 'слайд %d' % pages[i], 8.5, DIM, align='r',
             name='!!toc%dp' % i)
    d.footer(s)
    morph(s)

    # ================= 01 · ИШГА ҚАБУЛ ВА АДАПТАЦИЯ =================
    d.section('01', 'Ишга қабул қилиш ва адаптация',
              'Ёллаш жараёни, баҳолаш тизими ва адаптация дастури')

    # --- Ходимлар статистикаси
    s = d.content('01', 'Ходимлар статистикаси', 'ADM JIZZAKH AJ · Сентабр 2026')
    card(s, 0.55, 1.35, 3.3, 5.55, name='!!c1')
    label(s, 0.8, 1.55, 3, 'Штат жадвали')
    text(s, 0.8, 1.8, 3, 0.9, '3 245', 48, WHITE, FL)
    label(s, 0.8, 2.95, 3, 'Амалда')
    text(s, 0.8, 3.2, 3, 0.9, '2 738', 48, TEAL, FL)
    rect(s, 0.8, 4.3, 2.8, 0.12, fill=BG3, r=0.06)
    rect(s, 0.8, 4.3, 2.8 * 2738 / 3245, 0.12, fill=TEAL, r=0.06)
    text(s, 0.8, 4.5, 2.8, 0.3, 'Тўлиқлик 84,4%  ·  штатдан −496', 9.5, MUTED)
    rect(s, 0.8, 5.0, 2.8, 0.01, fill=LINE, r=0)
    text(s, 0.8, 5.15, 1.4, 0.4, '2 502', 22, WHITE, FL)
    text(s, 0.8, 5.6, 1.4, 0.3, 'Эркаклар', 9, MUTED)
    text(s, 2.25, 5.15, 1.4, 0.4, '236', 22, WHITE, FL)
    text(s, 2.25, 5.6, 1.4, 0.3, 'Аёллар', 9, MUTED)
    rect(s, 0.8, 6.15, 2.8, 0.1, fill=TEAL, r=0.05)
    rect(s, 0.8 + 2.8 * 2502 / 2738, 6.15, 2.8 * 236 / 2738, 0.1, fill=WARN, r=0.05)
    text(s, 0.8, 6.33, 2.8, 0.3, '91,4%  ·  8,6%', 8.5, DIM)

    tiles = [('510', 'Инженер-техник'), ('94', 'Мастер (G/L)'), ('30', 'Ўртача ёш'),
             ('18', 'Имконияти чекланган', 'режа: 50'), ('14', 'Бола парвариши таътилида')]
    pos = [(4.05, 1.35), (5.95, 1.35), (7.85, 1.35), (4.05, 2.95), (5.95, 2.95)]
    for i, (t, (x, y)) in enumerate(zip(tiles, pos)):
        kpi(s, x, y, 1.75, 1.45, t[0], t[1], t[2] if len(t) > 2 else None,
            name='!!c%d' % (i + 2) if i < 3 else None, vsize=28,
            accent=WARN if t[0] == '18' else TEAL)
    # 18/50 progress
    card(s, 7.85, 2.95, 1.75, 1.45)
    label(s, 8.05, 3.1, 1.5, 'Ногиронлик квотаси', MUTED, 8.5)
    text(s, 8.05, 3.38, 1.5, 0.6, '36%', 28, WARN, FL)
    rect(s, 8.05, 4.08, 1.35, 0.08, fill=BG3, r=0.04)
    rect(s, 8.05, 4.08, 1.35 * 0.36, 0.08, fill=WARN, r=0.04)

    card(s, 9.8, 1.35, 3.0, 5.55)
    label(s, 10.05, 1.55, 2.7, 'Ёш бўйича тақсимот')
    donut(s, 10.0, 1.9, 2.6, 2.6, ['18–29', '30–41', '41+'], [1556, 932, 200], [TEAL, '7FD9CF', DIM])
    text(s, 10.0, 2.85, 2.6, 0.5, '2 688', 20, WHITE, FL, align='c', anchor='m')
    text(s, 10.0, 3.3, 2.6, 0.3, 'нафар', 8.5, MUTED, align='c')
    for i, (a, b, c, col) in enumerate((('18–29 ёш', '1 556 нафар', '58,3%', TEAL),
                                         ('30–41 ёш', '932 нафар', '34,3%', '7FD9CF'),
                                         ('41 ёш ва ундан катта', '200 нафар', '7,4%', DIM))):
        yy = 4.75 + i * 0.68
        rect(s, 10.05, yy + 0.08, 0.12, 0.12, fill=col, r=0)
        text(s, 10.3, yy, 1.8, 0.3, a, 10, WHITE)
        text(s, 10.3, yy + 0.26, 1.8, 0.3, b, 8.5, MUTED)
        text(s, 11.6, yy, 1.0, 0.45, c, 15, WHITE, FL, align='r')

    card(s, 4.05, 4.6, 5.55, 2.3)
    label(s, 4.3, 4.8, 5, 'Штат таркиби (нафар)')
    hbar_rows(s, 4.3, 5.1, 5.1, [('Инженер-техник', 510), ('Мастер (G/L)', 94),
                                ('Бола парвариши таътилида', 14), ('Имконияти чекланган', 18)],
              510, rh=0.42, lw=2.2)

    # --- Ишга қабул режаси
    s = d.content('01', '2026-йил ишга қабул қилиш режаси',
                  'Бўлимлар кесимида режалаштирилган ишга қабул қилиш кўрсаткичлари')
    ks = [('855', 'Умумий режа', 'нафар'), ('685', 'Бажарилди', 'нафар'), ('80,1%', 'Бажарилиш', None),
          ('170', 'Қолган режа', 'нафар'), ('28', 'Захира', 'нафар')]
    for i, (v, l, sb) in enumerate(ks):
        kpi(s, 0.55 + i * 2.47, 1.3, 2.3, 1.15, v, l, None, name='!!c%d' % (i + 1), vsize=26,
            vcolor=TEAL if i == 2 else WHITE)
    card(s, 0.55, 2.6, 7.2, 4.3)
    label(s, 0.8, 2.75, 5, 'Ойма-ой ишга қабул қилиш (нафар)')
    mon = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    multi(s, 0.7, 3.0, 6.95, 3.85, mon,
          [('Режа', [109, 130, 119, 120, 87, 11, 84, 80, 34, 73, 4, 4], '58616B'),
           ('Бажарилди', [114, 103, 91, 89, 54, 0, 77, 77, 31, 49, 0, 0], TEAL)],
          gap=45, overlap=-5, size=8.5)
    card(s, 7.95, 2.6, 4.85, 2.75)
    label(s, 8.2, 2.75, 4.4, 'Бўлимлар кесимида йиллик режа (нафар)')
    bars(s, 8.05, 2.95, 4.65, 2.35,
         ['Пайвандлаш цехи', 'Бошқа бўлимлар', 'Таъминот тизими', 'Техник хизмат', 'SKD йиғув цехи',
          'CKD йиғув цехи', 'Сифат назорати', 'Захира'][::-1],
         [320, 189, 87, 87, 50, 47, 47, 28][::-1], gap=40, size=8)
    card(s, 7.95, 5.5, 4.85, 1.4)
    label(s, 8.2, 5.62, 4, 'Захира тақсимоти (нафар)')
    for i, (a, b) in enumerate((('Пайвандлаш', 10), ('Сифат назорати', 4), ('SKD йиғув', 14))):
        x = 8.2 + i * 1.55
        text(s, x, 5.9, 1.5, 0.5, str(b), 22, TEAL if b == 14 else WHITE, FL)
        text(s, x, 6.42, 1.5, 0.3, a, 8.5, MUTED)

    # --- Октябрь: бўлимлар кесимида
    s = d.content('01', 'Октябрь ойи: бўлимлар кесимида ишга қабул',
                  'Режа ва бажарилиш · 19 бўлим')
    for i, (v, l) in enumerate((('73', 'Режа'), ('49', 'Бажарилди'), ('67,1%', 'Бажарилиш'), ('24', 'Қолган'))):
        kpi(s, 0.55, 1.3 + i * 1.4, 2.6, 1.25, v, l, name='!!c%d' % (i + 1), vsize=28,
            vcolor=TEAL if i == 2 else WHITE)
    deps = [('Пайвандлаш цехи', 30, 27), ('Бўёқлаш цехи', 6, 6), ('Пластик бўёқлаш цехи', 0, 0),
            ('SKD йиғув цехи', 8, 3), ('CKD йиғув цехи', 12, 6), ('Сифат назорати ва кафолати', 10, 1),
            ('Техник хизмат кўрсатиш', 0, 1), ('R&D (ME)', 2, 0), ('R&D (PE)', 0, 0),
            ('Бош энергетик бошқармаси', 0, 0), ('Tool Shop', 0, 1), ('R&D (Tooling Center)', 2, 0),
            ('ME департаменти', 0, 0), ('PE департаменти', 2, 2), ('Ахборот технологиялари', 1, 2),
            ('Таъминот тизими', 0, 0), ('Таъмирлаш ва эксплуатация', 0, 0),
            ('Корпоратив овқатланиш ва делегациялар', 0, 0), ('Хавфсизлик', 0, 0)]

    def dep_rows(sl, start):
        rows = [['№', 'Бўлим', 'Режа', 'Бажарилди']]
        cols = {}
        for k, (n_, a, b) in enumerate(sl):
            rows.append([str(start + k + 1), n_, str(a), str(b)])
            if a and b < a:
                cols[(k + 1, 3)] = WARN
            elif b and b >= a:
                cols[(k + 1, 3)] = TEAL
        return rows, cols
    r1, c1 = dep_rows(deps[:10], 0)
    r2, c2 = dep_rows(deps[10:], 10)
    r2.append(['', 'Жами', '73', '49'])
    table(s, 3.4, 1.3, 4.6, r1, [0.4, 2.9, 0.7, 1.0], rh=0.5, size=9.5, colors=c1, name='!!t1', hsize=9, align='clcc')
    table(s, 8.2, 1.3, 4.6, r2, [0.4, 2.9, 0.7, 1.0], rh=0.5, size=9.5, total=True, colors=c2,
          name='!!t2', hsize=9, align='clcc')

    # --- Адаптация
    s = d.content('01', '2026-йил ходимларни мослаштириш (адаптация)',
                  'Янги ходимларнинг корхонага тез ва самарали мослашувини таъминлаш')
    ks = [('132', 'Умумий жалб қилинган', 'нафар'), ('44', 'Бошланғич ҳафтада', '33%'),
          ('51', '1 ойлик кузатувда', '39%'), ('37', '2 ойлик кузатувда', '28%'),
          ('7', 'Адаптацияда бўшаган', 'нафар')]
    for i, (v, l, sb) in enumerate(ks):
        kpi(s, 0.55 + i * 2.47, 1.3, 2.3, 1.15, v, l, None, name='!!c%d' % (i + 1), vsize=24,
            accent=WARN if i == 4 else TEAL)
        text(s, 0.55 + i * 2.47 + 1.2, 1.78, 0.95, 0.4, sb, 11, TEAL if i in (1, 2, 3) else DIM, FS,
             align='r')
    steps = [('Ўқитиш ва таништириш', 'Дастлабки маълумот ва йўриқномалар'),
             ('Иш жойи билан танишув', 'Ишлаб чиқариш ҳудуди ва жараёнлар'),
             ('Ментор билан суҳбат', 'Мослашув ва масалалар муҳокамаси'),
             ('Амалий иш жараёни', 'Иш жараёнидаги кўникмаларни кузатиш')]
    for i, (a, b) in enumerate(steps):
        x = 0.55 + (i % 2) * 3.65
        y = 2.6 + (i // 2) * 2.17
        card(s, x, y, 3.5, 2.05)
        pic_fill(s, 'adapt%d.jpg' % (i + 1), x + 0.1, y + 0.1, 3.3, 1.2)
        num_badge(s, x + 0.15, y + 1.42, '%02d' % (i + 1), d=0.45, size=9)
        text(s, x + 0.7, y + 1.37, 2.75, 0.3, a, 10.5, WHITE, FS)
        text(s, x + 0.7, y + 1.65, 2.75, 0.35, b, 8.5, MUTED)
    card(s, 7.95, 2.6, 4.85, 2.05)
    label(s, 8.2, 2.72, 4.4, 'Адаптация босқичлари (нафар)')
    bars(s, 8.05, 2.9, 4.65, 1.75, ['Бошланғич ҳафта', '1 ойлик кузатув', '2 ойлик кузатув'],
         [44, 51, 37], horiz=False, gap=90, hi={1: TEAL}, color='5E9F98')
    card(s, 7.95, 4.77, 4.85, 2.13)
    label(s, 8.2, 4.9, 4.4, 'Адаптацияда бўшаш сабаблари · 7 нафар', WARN)
    table(s, 8.15, 5.2, 4.45, [['Сабаб', 'Сони', 'Улуши'], ['Оилавий шароит', '4', '57%'],
                               ['Соғлиқ туфайли', '1', '14%'], ['Бошқа сабаблар', '2', '29%'],
                               ['Жами', '7', '100%']], [2.4, 0.9, 0.9], rh=0.32, size=9, total=True)

    # --- Ишдан бўшаш таҳлили
    s = d.content('01', '2026-йил ишдан бўшаш таҳлили',
                  'Ходимлар бўшашининг асосий кўрсаткичлари ва сабаблари · 01.01–01.10.2026')
    card(s, 0.55, 1.3, 2.95, 2.75, name='!!c1')
    label(s, 0.8, 1.5, 2.6, 'Жами бўшаганлар')
    text(s, 0.8, 1.75, 2.6, 1.2, '494', 66, TEAL, FL)
    text(s, 0.8, 3.05, 2.6, 0.6, ['нафар бўшади', '01.01 – 01.10.2026'], 10, MUTED)
    ch = [
        ('Лавозим бўйича', ['Пайвандчи', 'SKD Чилангар', 'Мех. йиғув чилангари', 'Амалиётчи', 'Инспектор',
                            'Бутловчи', 'Сифат инспектори', 'Бўёқчи'],
         [106, 63, 31, 15, 15, 14, 12, 6], True),
        ('Яшаш жойи бўйича', ['Ш. Рашидов т.', 'Жиззах ш.', 'Ғаллаорол т.', 'Пахтакор т.', 'Шаҳрихон т.',
                              'Асака т.'], [140, 62, 33, 26, 9, 7], True),
        ('Ишдан кетиш сабаблари', ['Ойлик етишмаслиги', 'Бошқа иш топган', 'Ишга келмаган', 'Соғлиқ'],
         [96, 2, 1, 1], True),
    ]
    for i, (t, cats, vals, hz) in enumerate(ch):
        x = 3.65 + i * 3.08
        card(s, x, 1.3, 2.95, 2.75, name='!!c%d' % (i + 2))
        label(s, x + 0.2, 1.42, 2.7, t + ' (нафар)')
        bars(s, x + 0.05, 1.62, 2.85, 2.4, cats[::-1], vals[::-1], gap=35, size=7.5,
             hi={len(vals) - 1: TEAL}, color='5E9F98')
    ages = ['18', '19', '20', '21', '22', '23', '25', '26', '27', '29', '30', '31', '32', '34', '44', '54']
    agev = [10, 25, 43, 49, 56, 61, 60, 47, 37, 33, 26, 13, 21, 10, 1, 2]
    bot = [('Ёши бўйича (нафар, ёш)', ages, agev),
           ('Ишлаган муддати бўйича (нафар, ой)', [str(i) for i in range(13)],
            [33, 27, 26, 28, 28, 26, 17, 19, 13, 21, 19, 12, 13]),
           ('Ишдан бўшаш ойлари', ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен'],
            [4, 16, 11, 9, 1, 3, 23, 11, 21])]
    for i, (t, cats, vals) in enumerate(bot):
        x = 0.55 + i * 3.1
        card(s, x, 4.2, 2.95, 2.7)
        label(s, x + 0.2, 4.32, 2.7, t)
        mx = max(vals)
        bars(s, x + 0.05, 4.55, 2.85, 2.3, cats, vals, horiz=False, gap=30, size=6.5, cat_size=6.5,
             color='5E9F98', hi={vals.index(mx): TEAL})
    card(s, 9.85, 4.2, 2.95, 2.7)
    label(s, 10.05, 4.32, 2.7, 'Категория бўйича (нафар)')
    cat = ['E-1', 'E-2', 'E-3', 'E-4', 'I-1', 'I-2', 'I-3', 'I-4', 'I-5', 'I-6', 'IA-1', 'IA-2',
           'IM-2', 'IM-3', 'IM-4', 'S1', 'S-1', 'S-2', 'S-3', 'S-4']
    cv = [2, 4, 2, 6, 3, 185, 126, 35, 43, 6, 15, 10, 1, 2, 2, 3, 12, 13, 7, 17]
    bars(s, 9.9, 4.55, 2.85, 2.3, cat, cv, horiz=False, gap=25, size=6, cat_size=5.5, color='5E9F98',
         hi={5: TEAL, 6: TEAL})

    # --- Чиқиш суҳбатлари (1/2)
    s = d.content('01', 'Ходимлар чиқиш суҳбатлари',
                  'Дашборд: 2026-йил, амалдаги ҳолат · Ҳисобот даври: 01.01.2026 – 01.09.2026')
    for i, (v, l) in enumerate((('104', 'Жами чиқишлар (ёзувлар)'), ('4,45 / 5', 'Ўртача умумий баҳо'),
                                ('409,1', 'Ўртача иш стажи, кун'))):
        kpi(s, 0.55 + i * 4.12, 1.3, 3.95, 1.1, v, l, name='!!c%d' % (i + 1), vsize=26)
    card(s, 0.55, 2.55, 4.0, 4.35, name='!!c4')
    label(s, 0.8, 2.68, 3.6, 'Кетиш сабаблари (жами 104)')
    bars(s, 0.6, 2.9, 3.9, 3.95,
         ['Кореяда ўқиш', 'Олий таълим', 'Соғлиқ', 'Иш юкламаси / стресс', 'Карьера ўсиши чекланган',
          'Бошқа сабаб', 'Шахсий (оилавий)', 'Юқори маошли таклиф', 'Билдирги билан'],
         [1, 1, 1, 6, 6, 11, 19, 23, 27], gap=35, size=8, color='5E9F98', hi={8: TEAL, 7: TEAL, 6: TEAL})
    card(s, 4.7, 2.55, 4.0, 4.35)
    label(s, 4.95, 2.68, 3.6, 'Бўлимлар бўйича (нафар)')
    bars(s, 4.75, 2.9, 3.9, 3.95,
         ['Бошқа бўлимлар', 'Технология', 'Техник хизмат', 'Хавфсизлик', 'Маъмурий хизмат', 'CKD йиғув',
          'Сифат назорати', 'Бўёқлаш', 'Таъминот', 'SKD йиғув', 'Пайвандлаш'],
         [10, 2, 2, 2, 3, 8, 9, 9, 13, 25, 29], gap=35, size=8, color='5E9F98', hi={10: TEAL, 9: TEAL})
    card(s, 8.85, 2.55, 3.95, 2.0)
    label(s, 9.1, 2.68, 3.6, 'Ойлар бўйича (нафар)')
    bars(s, 8.9, 2.85, 3.85, 1.68, mon, [0, 0, 0, 0, 1, 0, 0, 7, 72, 24, 0, 0], horiz=False, gap=40,
         size=7, cat_size=6.5, color='5E9F98', hi={8: TEAL})
    card(s, 8.85, 4.7, 3.95, 2.2)
    label(s, 9.1, 4.82, 3.6, 'Иш жараёнига баҳолар (5 баллдан)')
    rates = [('Маош ва мукофотлар', 3.57), ('Карьера ўсиши', 4.27), ('Иш юкламаси', 4.51),
             ('Ички коммуникация', 4.65), ('Раҳбар услуби', 4.65), ('Жамоа муҳити', 4.73),
             ('Иш шароитлари', 4.75)]
    hbar_rows(s, 9.1, 5.08, 3.55, rates, 5, rh=0.255, lw=1.55, size=8,
              color=lambda v: WARN if v < 4 else TEAL, fmt=lambda v: ('%.2f' % v).replace('.', ','), vw=0.4)

    # --- Чиқиш суҳбатлари (2/2)
    s = d.content('01', 'Чиқиш суҳбатлари: хулосалар', 'Қайта ишлаш истаги ва асосий хулосалар')
    card(s, 0.55, 1.3, 4.3, 5.6, name='!!c1')
    label(s, 0.8, 1.5, 4, 'Қайта ишлаш истаги (n = 57)')
    donut(s, 0.85, 1.85, 2.4, 2.4, ['Ҳа', 'Эҳтимол', 'Йўқ', 'Билмайман'], [36, 15, 4, 2],
          [TEAL, '7FD9CF', WARN, DIM])
    text(s, 0.85, 2.7, 2.4, 0.5, '89,5%', 20, WHITE, FL, align='c', anchor='m')
    text(s, 0.85, 3.15, 2.4, 0.3, 'тайёр', 8.5, MUTED, align='c')
    for i, (a, b, c, col) in enumerate((('Ҳа, истар эдим', '36', '63,2%', TEAL), ('Эҳтимол', '15', '26,3%', '7FD9CF'),
                                         ('Йўқ', '4', '7,0%', WARN), ('Билмайман', '2', '3,5%', DIM))):
        yy = 1.95 + i * 0.55
        rect(s, 3.4, yy + 0.08, 0.12, 0.12, fill=col, r=0)
        text(s, 3.6, yy, 1.2, 0.3, b, 13, WHITE, FL)
        text(s, 3.6, yy + 0.25, 1.2, 0.3, c, 8, MUTED)
    table(s, 0.8, 4.5, 3.8, [['Жавоб', 'Сони', 'Улуши'], ['Ҳа, истар эдим', '36', '63,2%'],
                             ['Эҳтимол', '15', '26,3%'], ['Йўқ', '4', '7,0%'], ['Билмайман', '2', '3,5%'],
                             ['Жами', '57', '100%']], [2.0, 0.8, 1.0], rh=0.36, size=9.5, total=True)
    concl = ['Асосий сабаблар: билдирги билан кетиш (27), юқори маошли иш таклифи (23), оилавий сабаблар (19); жами 69 та (66,3%)',
             'Энг кўп чиқиш: Пайвандлаш (29) ва SKD йиғув (25), жами 54 та (51,9%)',
             'Сентябрда 72 та чиқиш қайд этилган: йилдаги энг юқори кўрсаткич (69,2%)',
             'Энг паст баҳоланган йўналиш: маош ва мукофотлар тизими (3,57/5)',
             'Қайта ишлашга тайёрлар: 51 нафар (57 жавобнинг 89,5%), бу ходимлар захирасини шакллантириш имконини беради']
    for i, t in enumerate(concl):
        y = 1.3 + i * 1.14
        card(s, 5.05, y, 7.75, 1.0, name='!!c%d' % (i + 2))
        num_badge(s, 5.3, y + 0.28, i + 1, d=0.44, size=12)
        text(s, 5.95, y + 0.12, 6.65, 0.8, t, 11.5, WHITE, anchor='m')

    # --- Лавозим ўтишлари
    s = d.content('01', 'Лавозим турлари бўйича бошқа лавозимга ўтиш', 'Жами: 341 нафар, 90 хил лавозим')
    grp = [('Ишлаб чиқариш ходимлари', '261', '76,5% · 45 хил лавозим',
            [('Контактли пайвандлаш машиналари пайвандчиси', 44), ('Сифат назорати инспектори', 32),
             ('Бригадир', 29), ('Бутловчи', 26), ('Омборчи', 17), ('Мастер', 14)], 'Қолган 39 лавозим — 99 нафар'),
           ('Мутахассислар', '43', '12,6% · 27 хил лавозим',
            [('Харид бўйича муҳандис', 4), ('Муҳандис', 4), ('Таъминот омбори мудири', 4), ('Омбор мудири', 3),
             ('Муҳандис технолог', 3), ('Табел юритувчи', 2)], 'Қолган 21 лавозим — 23 нафар'),
           ('Бошқарув ходимлари', '25', '7,3% · 8 хил лавозим',
            [('Бўлинма бошлиғи', 14), ('Бўлим бошлиғи', 3), ('Бўлим бошлиғи ўринбосари', 2),
             ('Хизмат бошлиғи', 2), ('Директор', 1), ('Бош директор', 1)], 'Қолган 2 лавозим — 2 нафар'),
           ('Техник ходимлар', '12', '3,5% · 10 хил лавозим',
            [('Ҳайдовчи', 2), ('Ошхона ишчиси', 2), ('Оператор (видеокузатув)', 1), ('Ёнғин ўчирувчи', 1),
             ('Электрчи', 1), ('Офис тозаловчи', 1)], 'Қолган 4 лавозим — 4 нафар')]
    for i, (t, n_, sb, rows, rest) in enumerate(grp):
        x = 0.55 + i * 3.1
        card(s, x, 1.3, 2.95, 5.6, name='!!c%d' % (i + 1))
        text(s, x + 0.22, 1.45, 2.6, 0.3, t, 10.5, TEAL, FS)
        text(s, x + 0.22, 1.72, 2.6, 0.9, n_, 44, WHITE, FL)
        text(s, x + 0.22, 2.62, 2.6, 0.3, 'нафар · ' + sb, 8.5, MUTED)
        share = float(sb.split('%')[0].replace(',', '.'))
        rect(s, x + 0.22, 2.98, 2.5, 0.07, fill=BG3, r=0.03)
        rect(s, x + 0.22, 2.98, 2.5 * share / 100, 0.07, fill=TEAL, r=0.03)
        mx = rows[0][1]
        for k, (a, b) in enumerate(rows):
            yy = 3.25 + k * 0.5
            text(s, x + 0.22, yy, 2.05, 0.3, a, 8.5, WHITE)
            text(s, x + 2.3, yy, 0.45, 0.3, str(b), 10, WHITE, FS, align='r')
            rect(s, x + 0.22, yy + 0.32, 2.5, 0.05, fill=BG3, r=0)
            rect(s, x + 0.22, yy + 0.32, 2.5 * b / mx, 0.05, fill='5E9F98', r=0)
        text(s, x + 0.22, 6.4, 2.6, 0.3, rest, 8.5, DIM, italic=True)

    # --- Энг кўп ўтилган лавозимлар
    s = d.content('01', 'Бошқа лавозимга ўтган ходимлар', 'Жами: 341 нафар, 90 хил лавозим')
    card(s, 0.55, 1.3, 7.6, 5.0, name='!!c1')
    label(s, 0.8, 1.45, 7, 'Энг кўп ўтилган лавозимлар, нафар')
    bars(s, 0.65, 1.7, 7.4, 4.55,
         ['Механик йиғув чилангари (ТМ)', 'Малакали электр монтёр', 'Бўлинма бошлиғи', 'Мастер', 'Омборчи',
          'Бутловчи', 'Бригадир', 'Сифат назорати инспектори', 'Пресс пайвандчиси'],
         [7, 11, 14, 14, 17, 26, 29, 32, 44], gap=40, size=9, color='5E9F98', hi={8: TEAL})
    card(s, 8.3, 1.3, 4.5, 5.0, name='!!c2')
    label(s, 8.55, 1.45, 4, 'Қолган 81 лавозим')
    text(s, 8.55, 1.7, 4, 0.8, [[('147', {'size': 40, 'font': FL}), ('  нафар · 43%', {'size': 12, 'color': MUTED})]], 40)
    text(s, 8.55, 2.6, 4, 0.3, 'Ҳар бир лавозимдан ўтганлар:', 9.5, MUTED)
    hbar_rows(s, 8.55, 2.95, 4.05, [('1 нафардан', 49), ('2 нафардан', 16), ('3 нафардан', 6),
                                     ('4 нафардан', 5), ('5 нафардан', 2), ('6 нафардан', 3)],
              49, rh=0.5, lw=1.3, vw=1.0, fmt=lambda v: '%d лав.' % v)
    text(s, 0.55, 6.45, 12.2, 0.5,
         'Манба: Ходимлар рўйхати. Бошқа лавозимга ўтган — ҳозирги лавозимга ўтган санаси ишга қабул санасидан '
         'кейин бўлган ходим; 2026 йил октябрь ойи ҳисобга олинмаган.', 8.5, DIM, italic=True)

    # ================= 02 · САМАРАДОРЛИК ВА KPI =================
    d.section('02', 'Самарадорлик ва KPI',
              'Қўшимча иш соатлари, HPV ишлаб чиқариш самарадорлиги ва ишчи-ходимлар KPI таҳлили')

    # --- Қўшимча иш соатлари
    s = d.content('02', 'Қўшимча иш соатлари', '2026 январь – сентябрь')
    card(s, 0.55, 1.3, 5.6, 5.6, name='!!c1')
    label(s, 0.8, 1.45, 5, 'Энг кўп қўшимча соат ишлаган бўлимлар (соат)')
    bars(s, 0.65, 1.7, 5.4, 2.6, ['Йиғув цехи', 'Сифат назорати', 'Бўёқлаш цехи', 'Харид ва таъминот',
                                  'Пайвандлаш цехи'],
         [29443, 29852, 38567, 57069, 66874], gap=40, size=9, fmt='# ##0', color='5E9F98', hi={4: TEAL})
    label(s, 0.8, 4.45, 5, 'Ойлар кесимида (соат)')
    oh = [62463, 39538, 36519, 83670, 24857, 0, 1546, 1546, 10810]
    bars(s, 0.65, 4.65, 5.4, 2.2, ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен'], oh,
         horiz=False, gap=40, size=7.5, fmt='# ##0', color='5E9F98', hi={3: TEAL})
    card(s, 6.3, 1.3, 6.5, 5.6, name='!!c2')
    label(s, 6.55, 1.45, 6, 'Ойлар кесимида: соат ва сумма')
    rows = [['Ой', 'Соат', 'Сумма, сўм'], ['Январь', '62 463', '3 516 876 029'], ['Февраль', '39 538', '2 048 147 543'],
            ['Март', '36 519', '2 104 087 894'], ['Апрель', '83 670', '4 512 395 252'],
            ['Май', '24 857', '2 884 260 424'], ['Июнь', '0', '0'], ['Июль', '1 546', '71 263 167'],
            ['Август', '1 546', '399 693 155'], ['Сентабр', '10 810', '665 395 786'],
            ['Жами', '260 949', '16 202 119 250']]
    table(s, 6.55, 1.8, 6.0, rows, [1.6, 1.4, 2.4], rh=0.44, size=10.5, total=True, align='lrr',
          colors={(4, 1): TEAL, (4, 2): TEAL})

    # --- HPV
    s = d.content('02', 'HPV ишлаб чиқариш самарадорлиги', 'Август ойи · паст кўрсаткич = юқори самарадорлик')
    for i, (t, a, b, c) in enumerate((('CKD цехи · август HPV', '119,6', '100', '19,6%'),
                                       ('SKD цехи · август HPV', '23,8', '21,2', '12,2%'))):
        x = 0.55 + i * 3.15
        card(s, x, 1.3, 3.0, 2.05, name='!!c%d' % (i + 1))
        label(s, x + 0.22, 1.45, 2.7, t)
        text(s, x + 0.22, 1.72, 1.3, 0.3, 'режа', 8.5, MUTED)
        text(s, x + 0.22, 1.92, 1.3, 0.6, a, 24, MUTED, FL)
        text(s, x + 1.55, 1.72, 1.3, 0.3, 'факт', 8.5, MUTED)
        text(s, x + 1.55, 1.92, 1.3, 0.6, b, 24, WHITE, FL)
        rect(s, x + 0.22, 2.75, 2.55, 0.42, fill=TEAL3, r=0.21)
        text(s, x + 0.22, 2.75, 2.55, 0.42, '▼ ' + c + ' га яхши', 10.5, TEAL, FS, align='c', anchor='m')
    for i, (t, p, f) in enumerate((('CKD цехи, июль–сентябрь', [118.8, 112.0, 119.6], [93.7, 98.3, 100.0]),
                                    ('SKD цехи, июль–сентябрь', [25.9, 19.0, 23.8], [18.6, 19.4, 21.2]))):
        x = 0.55 + i * 3.15
        card(s, x, 3.5, 3.0, 3.4, name='!!c%d' % (i + 3))
        label(s, x + 0.22, 3.62, 2.7, t)
        multi(s, x + 0.05, 3.85, 2.9, 3.0, ['Июль', 'Август', 'Сентябрь'],
              [('Режа', p, '58616B'), ('Факт', f, TEAL)], fmt='0.0', size=8, gap=60, overlap=-5)
    card(s, 6.85, 1.3, 5.95, 5.6)
    label(s, 7.1, 1.45, 5.5, 'Август ойи HPV (14 UPH)')
    hp = [['Цех', 'Режа', 'Факт', 'Ҳолат'], ['Welding shop', '26,89', '26,9', 'Режадан яхши'],
          ['Paint shop', '14,57', '14,6', 'Режадан яхши'], ['GA shop', '13,7', '13,7', 'Режадан яхши'],
          ['ME', '1,15', '5,9', 'Режадан юқори'], ['Terminal', '2,26', '2,2', 'Режадан яхши'],
          ['Supply chain', '30,44', '23,8', 'Режадан яхши'], ['Maintenance', '6,46', '5,9', 'Режадан яхши'],
          ['Quality', '18,72', '11,3', 'Режадан яхши']]
    cl = {(r, 3): TEAL for r in range(1, 9)}
    cl[(4, 3)] = WARN
    cl[(4, 2)] = WARN
    table(s, 7.1, 1.8, 5.45, hp, [1.6, 0.9, 0.9, 1.5], rh=0.52, size=10.5, colors=cl)

    # --- Ишчи KPI
    s = d.content('02', 'Ишчи-ходимлар KPI таҳлили',
                  'АДМ Жиззах · 2026 йил январь – сентябрь (9 ой) · ўртача ~1 930 ходим/ой')
    ks = [('19,7%', 'Ўртача KPI (сентябрь)', 'Январь 20,1%, август 20,4%', TEAL),
          ('87,9%', 'Мақсадга эришиш', 'Режага нисбатан, март–сентябрь', TEAL),
          ('2 002', 'Ходимлар сони', 'Январда 1 864 эди (+138)', TEAL),
          ('28 киши', 'Доимий паст натижа', '9 ойлик ўртача KPI 8% дан паст', WARN)]
    for i, (v, l, sb, ac) in enumerate(ks):
        kpi(s, 0.55 + i * 3.1, 1.3, 2.95, 1.4, v, l, sb, name='!!c%d' % (i + 1), vsize=26, accent=ac)
    m9 = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен']
    card(s, 0.55, 2.85, 4.0, 2.75)
    label(s, 0.8, 2.97, 3.6, 'Ойлик ўртача KPI динамикаси, %')
    g = multi(s, 0.6, 3.15, 3.9, 2.4, m9, [('KPI', [20.08, 19.51, 19.42, 19.65, 19.68, 19.32, 19.57, 20.41, 19.67], TEAL)],
              kind='line', fmt='0.0', size=7.5, legend=False)
    g.chart.value_axis.minimum_scale = 18.5
    g.chart.value_axis.maximum_scale = 21
    card(s, 4.7, 2.85, 4.0, 2.75)
    label(s, 4.95, 2.97, 3.6, 'Ходимлар сони, ой охирига')
    g = bars(s, 4.75, 3.15, 3.9, 2.4, m9, [1864, 1908, 1953, 1965, 1963, 1928, 1847, 1999, 2002], horiz=False,
             gap=35, size=7, fmt='# ##0', color='5E9F98', hi={8: TEAL})
    g.chart.value_axis.minimum_scale = 1500
    card(s, 8.85, 2.85, 3.95, 4.05)
    label(s, 9.1, 2.97, 3.6, 'Лавозимлар бўйича ўртача KPI, %')
    pk = [('Автобус ҳайдовчиси', 29.5), ('Оператор', 23.5), ('Чиқинди саралаш ишчиси', 23.2),
          ('Герметизаторчи', 23.2), ('Ҳисобчи', 23.1), ('Сифат назорати инспектори', 19.3),
          ('Йиғув ишлари чилангари', 14.9), ('Ҳайдовчи', 14.6), ('Қўриқчи', 14.2), ('Ошхона ишчиси', 12.8)]
    hbar_rows(s, 9.1, 3.25, 3.55, pk, 30, rh=0.355, lw=1.75, size=8,
              color=lambda v: TEAL if v >= 20 else WARN, fmt=lambda v: ('%.1f' % v).replace('.', ','), vw=0.4)
    card(s, 0.55, 5.75, 8.15, 1.15)
    rect(s, 0.55, 5.75, 0.06, 1.15, fill=TEAL, r=0)
    text(s, 0.8, 5.83, 7.75, 1.0,
         [[('Хулоса: ', {'color': TEAL, 'font': FS}),
           ('KPI 9 ой давомида барқарор (~19–20%), мақсадга эришиш ўртача 87,9%, лекин ҳар ойда ходимларнинг '
            '~11–18% и режанинг ярмига ҳам етмаяпти. Ходимлар сони 9 ойда +138 нафарга кўпайди (285 нафар кетди, '
            '423 нафар қабул қилинди). Энг паст натижа хизмат кўрсатиш ва ҳайдовчилик лавозимларида, энг юқориси '
            'автобус ҳайдовчиси, оператор ва омбор лавозимларида.', {})]], 9, WHITE, anchor='m')

    # --- Хронометраж
    s = d.content('02', 'Хронометраж: 13 штат бирлигидан 9 таси камаювчи',
                  'Бўёқлаш, Пайвандлаш, Йиғув цехлари ва Таъминот тизими · бандлик 460 дақиқалик иш кунига нисбатан')
    ks = [('13', 'Штат бирлиги', 'хронометраж қилинди', TEAL), ('9', 'Камаювчи', 'бандлиги 70% дан паст', WARN),
          ('4', 'Сақланади', 'бандлиги 70% ва юқори', TEAL), ('322 дақ.', 'Чегара', '460 дақиқанинг 70%и', TEAL)]
    for i, (v, l, sb, ac) in enumerate(ks):
        kpi(s, 0.55, 1.3 + i * 1.36, 2.9, 1.22, v, l, sb, name='!!c%d' % (i + 1), vsize=24, accent=ac)
    card(s, 3.6, 1.3, 9.2, 5.6)
    chron = [('Бўёқлаш цехи', 'Материаллар бўйича муҳандис', 30.6, 141), ('', 'Материаллар бўйича муҳандис', 42.1, 194),
             ('', 'Омбор мудири', 30.6, 141), ('', 'Омбор мудири', 42.1, 194),
             ('Пайвандлаш цехи', 'Ҳужжатлар регистратори', 43.5, 200), ('', 'Муҳандис ЖИГ', 30.8, 142),
             ('', 'Комплектация бўйича муҳандис', 47.8, 220), ('', 'Комплектация бўйича муҳандис', 29.5, 136),
             ('Йиғув цехи', 'Жиҳоз устаси', 39.6, 190), ('', 'Комплектация бўйича муҳандис', 71.3, 328),
             ('Таъминот тизими', 'КД деталлари моддий оқимини таҳлил қилиш муҳандиси', 81.4, 374),
             ('', 'Харид бўйича муҳандис', 81.4, 374),
             ('', 'КД деталлари моддий оқимини таҳлил қилиш муҳандиси', 79.1, 364),
             ('', 'Харид бўйича муҳандис', 91.0, 419)]
    text(s, 3.85, 1.42, 1.8, 0.3, 'ЦЕХ', 8.5, TEAL, FS)
    text(s, 5.6, 1.42, 3.4, 0.3, 'ШТАТ БИРЛИГИ', 8.5, TEAL, FS)
    text(s, 9.1, 1.42, 3.4, 0.3, 'БАНДЛИК (460 ДАҚ. = 100%)', 8.5, TEAL, FS)
    bx, bw = 9.1, 2.45
    y0, rh = 1.72, 0.33
    for k, (shop, pos_, pct, mn) in enumerate(chron):
        yy = y0 + k * rh
        if shop:
            if k:
                rect(s, 3.85, yy - 0.02, 8.75, 0.01, fill=LINE, r=0)
            text(s, 3.85, yy, 1.7, rh, shop, 9, WHITE, FS, anchor='m')
        text(s, 5.6, yy, 3.45, rh, pos_, 8.5, WHITE, anchor='m')
        col = TEAL if pct >= 70 else WARN
        rect(s, bx, yy + 0.12, bw, 0.11, fill=BG3, r=0.05)
        rect(s, bx, yy + 0.12, bw * pct / 100, 0.11, fill=col, r=0.05)
        text(s, bx + bw + 0.08, yy, 1.0, rh, ('%.1f%%' % pct).replace('.', ',') + ' · %d' % mn, 8.5, col, FS,
             anchor='m')
    # 70% chegarasi
    rect(s, bx + bw * 0.7, y0 - 0.05, 0.015, rh * 14 + 0.05, fill=WHITE, r=0, alpha=0.5)
    text(s, bx + bw * 0.7 - 0.4, y0 + rh * 14, 0.8, 0.22, '70%', 7.5, MUTED, align='c')
    text(s, 3.85, 6.6, 8.8, 0.25,
         'Камаювчи — бандлиги 70% дан (322 дақиқадан) паст штат бирликлари; қисқартириш ёки вазифаларни '
         'бирлаштириш учун номзод.', 8.5, DIM, italic=True)

    # ================= 03 · ЎҚИТИШЛАР =================
    d.section('03', 'Ўқитишлар', 'АДМ Академия, ички ўқитиш ижроси ва ходимларни баҳолаш тизими')

    s = d.content('03', '6 ойлик ўқитиш ва компетенция натижалари',
                  'Қамров юқори, аммо сентябрда давомат пасайди ва Сифат йўналишида компетенция пастроқ')
    ks = [('94,5%', 'Бригадирлар ўқитилди', '165 нафардан 156 нафари камида бир марта', TEAL),
          ('23 нафар', 'Сентябрда дарсга келмаган', 'Апрелда 5 нафар эди; қамров 85,0%гача', WARN),
          ('76,8%', 'Ўртача компетенция бали', '341 ходим баҳоланди (585 макс. балл)', TEAL),
          ('108 нафар', '70%дан паст натижа', 'Сифат 78, Йиғув 28 · 72,2%и Сифатда', WARN)]
    for i, (v, l, sb, ac) in enumerate(ks):
        kpi(s, 0.55 + i * 3.1, 1.3, 2.95, 1.45, v, l, sb, name='!!c%d' % (i + 1), vsize=26, accent=ac)
    card(s, 0.55, 2.9, 6.1, 4.0)
    label(s, 0.8, 3.03, 4, 'Компетенция: Сифат йўналиши устувор')
    text(s, 4.2, 2.98, 2.3, 0.3, '341 ходим баҳоланди', 8.5, MUTED, align='r')
    comp = [('Сифат', 130, 66.8), ('Йиғув', 118, 81.4), ('Бўёқлаш', 43, 86.5), ('СКД', 18, 83.2),
            ('Таъмирлаш', 17, 79.9), ('Ускуналар', 15, 88.4)]
    text(s, 0.8, 3.35, 1.5, 0.25, 'ЙЎНАЛИШ', 8, DIM, FS)
    text(s, 2.15, 3.35, 0.8, 0.25, 'ХОДИМ', 8, DIM, FS, align='r')
    text(s, 3.15, 3.35, 2.5, 0.25, 'ЎРТАЧА БАЛЛ', 8, DIM, FS)
    for k, (a, n_, v) in enumerate(comp):
        yy = 3.65 + k * 0.42
        text(s, 0.8, yy, 1.4, 0.35, a, 10, WHITE, anchor='m')
        text(s, 2.15, yy, 0.8, 0.35, str(n_), 10, MUTED, align='r', anchor='m')
        col = WARN if v < 70 else TEAL
        rect(s, 3.15, yy + 0.13, 2.6, 0.1, fill=BG3, r=0.05)
        rect(s, 3.15, yy + 0.13, 2.6 * v / 100, 0.1, fill=col, r=0.05)
        text(s, 5.8, yy, 0.75, 0.35, ('%.1f%%' % v).replace('.', ','), 10, col, FS, anchor='m', align='r')
    rect(s, 0.8, 6.25, 5.6, 0.5, fill=TEAL3, r=0.1)
    text(s, 1.0, 6.25, 5.4, 0.5, [[('73,9%', {'font': FS, 'color': WHITE, 'size': 14}),
                                   ('   умумий ўртача   ·   режа: 90%+', {'color': TEAL})]], 10, anchor='m')
    card(s, 6.8, 2.9, 6.0, 4.0)
    label(s, 7.05, 3.03, 3, 'Таклиф')
    tag = rect(s, 9.9, 2.98, 2.7, 0.32, fill=WARN, r=0.16, alpha=0.18)
    text(s, 9.9, 2.98, 2.7, 0.32, 'Таҳлилий таклиф · ҳали тасдиқланмаган', 8, WARN, FS, align='c', anchor='m')
    props = [('Давоматни тиклаш', 'Таътил ва сменага мос қўшимча дарслар. Пайвандлаш (7) ва Таъминот (5) биринчи навбатда.'),
             ('106 ходимни қайта ўқитиш', 'Сифат 78 + Йиғув 28: ADM MS, йўқотишлар, WPO. 30 кунда қайта баҳо.'),
             ('Ягона натижалар реестри', 'Давомат, баҳо, OJT, сертификат ва харажат битта тизимда (Академия, HR, Молия).')]
    for k, (a, b) in enumerate(props):
        yy = 3.45 + k * 1.12
        shape(s, MSO_SHAPE.OVAL, 7.05, yy, 0.7, 0.7, fill=TEAL3)
        pic(s, 'icon%d.png' % (k + 1), 7.2, yy + 0.15, 0.4, 0.4)
        text(s, 7.95, yy - 0.02, 4.7, 0.3, a, 11.5, WHITE, FS)
        text(s, 7.95, yy + 0.3, 4.7, 0.7, b, 9.5, MUTED)

    s = d.content('03', 'Давомат сентябрда пасайди, энг пасти Ускуналарда',
                  'Бригадирлар: 2 865 қатнашув · раҳбарлар: 455 имкониятдан 208 қайд (45,7%)')
    m6 = ['Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен']
    card(s, 0.55, 1.3, 6.1, 2.85, name='!!c1')
    label(s, 0.8, 1.43, 5, 'Қамров, %')
    g = multi(s, 0.6, 1.65, 6.0, 2.45, m6, [('Қамров', [96.6, 94.7, 96.7, 95.3, 91.2, 85.0], TEAL)], kind='line',
              fmt='0.0', size=8.5, legend=False)
    g.chart.value_axis.minimum_scale = 80
    g.chart.value_axis.maximum_scale = 100
    card(s, 0.55, 4.3, 6.1, 2.6, name='!!c2')
    label(s, 0.8, 4.43, 5, 'Келмаганлар, нафар', WARN)
    bars(s, 0.6, 4.65, 6.0, 2.2, m6, [5, 8, 5, 7, 13, 23], horiz=False, gap=60, size=8.5, color='8A5A52',
         hi={5: WARN})
    card(s, 6.8, 1.3, 6.0, 3.6, name='!!c3')
    label(s, 7.05, 1.43, 5, 'Бўлимлар бўйича қатнашув, %')
    att = [('Бўёқлаш', 97.7), ('Сифат назорати', 95.5), ('Йиғув', 94.3), ('Таъминот', 94.3),
           ('Маъмурий хизмат', 91.7), ('Пайвандлаш', 91.0), ('СКД', 89.4), ('Ускуналар', 66.7)]
    hbar_rows(s, 7.05, 1.75, 5.55, att, 100, rh=0.38, lw=1.8, size=9.5,
              color=lambda v: WARN if v < 80 else TEAL, fmt=lambda v: ('%.1f' % v).replace('.', ','), vw=0.5)
    for k, (v, a, b, ac) in enumerate((('−11,7 п.п.', 'Қамров июндан сентябргача', '96,7% → 85,0%', WARN),
                                        ('3 бригадир', 'Ускуналарда', 'Ш. Икрамов: июль–август йўқ', WARN),
                                        ('45,7%', 'Раҳбарлар: қайд улуши', 'режа бажарилиши фоизи эмас', TEAL))):
        x = 6.8 + k * 2.03
        card(s, x, 5.05, 1.94, 1.85, name='!!c%d' % (k + 4))
        rect(s, x, 5.05, 1.94, 0.05, fill=ac, r=0)
        text(s, x + 0.15, 5.2, 1.7, 0.5, v, 18, ac, FL)
        text(s, x + 0.15, 5.72, 1.7, 0.5, a, 9, WHITE, FS)
        text(s, x + 0.15, 6.2, 1.7, 0.6, b, 8, MUTED)

    # ================= 04 · GRADING =================
    d.section('04', 'Grading тизими', 'Рол, баҳолаш, ривожланиш ва тўлов: ягона тизим')

    s = d.content('04', 'Grading тизими: рол, баҳолаш ва тўлов ягона тизимда',
                  'Тўғри одам тўғри ролда, тўғри тўлов ва ўсиш имкониятлари билан')
    card(s, 0.55, 1.3, 3.4, 5.6, name='!!c1')
    label(s, 0.8, 1.45, 3, 'Карьера зинапояси')
    ladder = [('HiPo', 'Young · HiPo · Key'), ('Senior', 'A · B · C'), ('Middle', 'A · B · C'), ('Junior', 'A · B · C')]
    for k, (a, b) in enumerate(ladder):
        w_ = 1.9 + (3 - k) * 0.0 + k * 0.33
        x = 0.8 + k * 0.0
        yy = 1.85 + k * 1.05
        w_ = 2.9 - (3 - k) * 0.3
        x = 0.8 + (3 - k) * 0.3
        rect(s, x, yy, w_, 0.9, fill=TEAL if k == 0 else BG3, r=0.08, alpha=1 if k == 0 else None)
        text(s, x + 0.2, yy + 0.08, w_ - 0.3, 0.4, a, 15, BG if k == 0 else WHITE, FS)
        text(s, x + 0.2, yy + 0.48, w_ - 0.3, 0.3, b, 9.5, BG if k == 0 else MUTED)
    text(s, 0.8, 6.15, 3, 0.6, '↑ Junior → HiPo; ҳар даража ичида A → B → C', 9, TEAL)
    comps = [('РОЛ', 'Аниқ роллар ва кутишлар', ['Рол ва масъулият тавсифи', 'Талаб қилинадиган компетенциялар',
                                                  'Таъсир даражаси ва мураккаблик']),
             ('БАҲОЛАШ', 'Объектив баҳолаш', ['Шаффоф мезонлар', 'Мунтазам тескари алоқа',
                                              'Натижалар ва компетенцияларни баҳолаш']),
             ('РИВОЖЛАНИШ', 'Ўсиш ва ривожланиш', ['Индивидуал ривожланиш режалари', 'Ўқитиш ва ўсиш имкониятлари',
                                                   'Карьера траекториялари']),
             ('ТЎЛОВ', 'Адолатли тўлов', ['Рол қиймати ва натижалар асосида тўлов', 'Рақобатбардош бозор маълумотлари',
                                          'Шаффоф диапазонлар ва қоидалар'])]
    for k, (a, b, bl) in enumerate(comps):
        x = 4.1 + k * 2.2
        card(s, x, 1.3, 2.08, 3.85, name='!!c%d' % (k + 2))
        num_badge(s, x + 0.2, 1.48, k + 1, d=0.45, size=12)
        text(s, x + 0.2, 2.05, 1.8, 0.3, a, 9, TEAL, FS)
        text(s, x + 0.2, 2.32, 1.8, 0.6, b, 12.5, WHITE, FL)
        for j, t in enumerate(bl):
            yy = 3.05 + j * 0.68
            rect(s, x + 0.2, yy + 0.08, 0.05, 0.4, fill=TEAL2, r=0)
            text(s, x + 0.35, yy, 1.62, 0.65, t, 8.5, MUTED, anchor='m')
    princ = [('Шаффофлик', 'Тушунарли қоидалар, мезон ва жараёнлар'),
             ('Автоматлаштириш', 'Баҳолаш ва қарор учун рақамли воситалар'),
             ('Ривожланиш', 'Компетенция ва салоҳиятни ошириш'),
             ('Маълумотли қарор', 'Объектив кадрлар қарори учун таҳлил')]
    card(s, 4.1, 5.3, 8.7, 1.6)
    label(s, 4.35, 5.42, 8, 'Ягона тизимнинг тамойиллари')
    for k, (a, b) in enumerate(princ):
        x = 4.35 + k * 2.12
        text(s, x, 5.75, 2.0, 0.3, a, 11, WHITE, FS)
        text(s, x, 6.07, 1.95, 0.7, b, 8.5, MUTED)

    s = d.content('04', 'Грейдлар ва даражани белгилаш мезонлари',
                  'Лавозимлар G1 дан G14 гача · даража 4 блок бўйича балл билан аниқланади (Мастер G6 мисолида)')
    card(s, 0.55, 1.3, 5.6, 5.6, name='!!c1')
    label(s, 0.8, 1.43, 5, 'Лавозимлар рўйхати (грейдлар)')
    grades = [('G1', 'Асосий ходимлар', 'Тозаловчи, боғбон, оператор, ёрдамчи ишчи, ошхона'),
              ('G2', 'Техник ходимлар', 'Чилангар, ҳайдовчи, омборчи, электрик, курьер, сантехник'),
              ('G3', 'Малакали ишчи', 'Сифат инспектори, электромонтёр, пайвандчи, техника ҳайдовчиси'),
              ('G4', 'Катта ишчилар', 'Бригадир, диспетчер, ассистент, бухгалтерия кўмаги'),
              ('G6', 'Мастер', 'Ишлаб чиқариш участкаси мастери'),
              ('G7', 'Мутахассис', 'Муҳандис, бухгалтер, HR, технолог, IT-админ'),
              ('G8', 'Катта мутахассис', 'Инвестиция мутахассиси, технадзор ва ПТО муҳандиси'),
              ('G9', 'Секция раҳбари', 'Секция бошлиғи, бош бухгалтер ўринбосари, линия бошлиғи'),
              ('G10', 'Секция раҳбари', 'Локализация, бухгалтерия, R&D, режалаштириш'),
              ('G11', 'Олий тоифали', 'Инвестиция, техназорат ва ПТО бош мутахассиси'),
              ('G12', 'Бўлим бошлиғи', 'Бўлим бошлиқлари'),
              ('G13–14', 'Топ-даража', 'Ўринбосар ва бўлим директори')]
    for k, (g_, a, b) in enumerate(grades):
        yy = 1.75 + k * 0.425
        hl = g_ == 'G6'
        rect(s, 0.75, yy, 0.72, 0.36, fill=TEAL if hl else TEAL3, r=0.06)
        text(s, 0.75, yy, 0.72, 0.36, g_, 9, BG if hl else TEAL, FS, align='c', anchor='m')
        text(s, 1.6, yy - 0.02, 4.4, 0.22, a, 9.5, WHITE, FS)
        text(s, 1.6, yy + 0.18, 4.4, 0.22, b, 7.5, MUTED)
    card(s, 6.3, 1.3, 6.5, 3.0, name='!!c2')
    label(s, 6.55, 1.43, 6, 'Даражани белгилаш: 4 блок')
    blocks = [('Awareness', 'Илова №1', 'NT—1, A—2, K—3, D—4, T—5 балл'),
              ('Корпоратив қадриятлар', 'Илова №2', 'Стаж: 1 йил—5, 2—10, 3—25, 4—40 балл; интизомий жазо −20'),
              ('Аттестация ва «360»', 'Илова №3–4', '65 савол × 2 балл; «360»: 1—40, 2—70, 3—100, 4—115, 5—130'),
              ('Лойиҳа тақдимоти', 'KEY учун', 'Фақат KEY (HiPo) даражаси учун талаб қилинади')]
    for k, (a, b, c) in enumerate(blocks):
        x = 6.55 + (k % 2) * 3.1
        yy = 1.75 + (k // 2) * 1.25
        num_badge(s, x, yy + 0.02, k + 1, d=0.38, size=10)
        text(s, x + 0.5, yy, 2.5, 0.3, [[(a, {'font': FS}), ('  · ' + b, {'color': TEAL, 'size': 8})]], 10, WHITE)
        text(s, x + 0.5, yy + 0.3, 2.5, 0.85, c, 8.5, MUTED)
    card(s, 6.3, 4.45, 6.5, 2.45, name='!!c3')
    label(s, 6.55, 4.57, 6, 'Якуний балл бўйича даража')
    lv = [['Даража', 'A', 'B', 'C'], ['Junior', '292', '325', '357'], ['Middle', '422', '455', '487'],
          ['Senior', '552', '585', '620'], ['HiPo', '—', 'KEY: 650 + лойиҳа', '']]
    table(s, 6.55, 4.85, 3.4, lv, [1.0, 0.7, 1.3, 0.7], rh=0.34, size=9, colors={(2, 2): TEAL})
    rect(s, 10.15, 4.85, 2.45, 1.7, fill=TEAL3, r=0.1)
    text(s, 10.3, 4.95, 2.2, 0.3, 'МИСОЛ', 8, TEAL, FS)
    text(s, 10.3, 5.2, 2.2, 0.9, 'балл 85, стаж 2 йил, жазо 0, тўғри жавоб 40, «360» — 3', 8.5, WHITE)
    text(s, 10.3, 5.95, 2.2, 0.5, [[('466,25 → ', {'color': MUTED}), ('MIDDLE B', {'font': FS, 'color': TEAL})]], 11)

    # ================= 05 · ЭЛЕКТРОН АРИЗА =================
    d.section('05', 'Электрон ариза тизими', 'Қоғоз аризадан электрон жараёнга ўтиш ва янги стандартлар')

    s = d.content('05', 'Электрон ариза тизими жорий этилди',
                  'Ходимларни ишга қабул қилиш ва мослаштириш бўйича иккита муҳим стандарт тасдиқланди')
    ks = [('8', 'Электронлаштирилган', 'ариза тури'), ('1', 'Янги модул', 'йиллик таътил'),
          ('100%', 'Электрон кузатиш', ''), ('0 сўм', 'Киоск харидига', 'сарфланган маблағ')]
    for i, (v, l, sb) in enumerate(ks):
        kpi(s, 0.55 + i * 3.1, 1.3, 2.95, 1.35, v, l, sb, name='!!c%d' % (i + 1), vsize=28,
            vcolor=TEAL if i == 3 else WHITE)
    card(s, 0.55, 2.8, 6.6, 4.1)
    label(s, 0.8, 2.93, 6, 'Электрон шаклга ўтказилган аризалар')
    ap = ['Бола туғилиши муносабати билан таътил', 'Никоҳ тўйи муносабати билан таътил',
          'Яқин қариндош вафоти муносабати билан таътил', 'Иш ҳақи сақланмаган ҳолда таътил',
          'Ўқув таътили бериш', 'Отгул бериш', 'Ҳарбий хизматга чақириш бўйича ариза',
          'Иш вақтида ташқарига чиқиш учун рухсатнома']
    for k, t in enumerate(ap):
        x = 0.8 + (k // 4) * 3.15
        yy = 3.3 + (k % 4) * 0.88
        rect(s, x, yy, 3.0, 0.75, fill=BG3, r=0.08)
        text(s, x + 0.12, yy, 0.5, 0.75, '%02d' % (k + 1), 15, TEAL, FL, anchor='m')
        text(s, x + 0.65, yy, 2.25, 0.75, t, 9, WHITE, anchor='m')
    card(s, 7.3, 2.8, 5.5, 4.1)
    label(s, 7.55, 2.93, 5, 'Тасдиқланган стандартлар')
    text(s, 7.55, 3.17, 5, 0.25, 'ходимларни бошқариш жараёнлари бўйича', 8.5, DIM)
    for k, (code, nm, dt) in enumerate((('KSt-205000-006:2026', 'Ишга қабул қилиш тартиби',
                                         'Тасдиқланди 03.09.2026  ·  амал қилади 02.09.2029'),
                                        ('KSt-205000-020:2026', 'Мослаштириш тартиби',
                                         'Тасдиқланди 09.09.2026  ·  амал қилади 08.09.2029'))):
        yy = 3.6 + k * 1.6
        rect(s, 7.55, yy, 5.0, 1.4, fill=BG3, r=0.08)
        rect(s, 7.55, yy, 0.06, 1.4, fill=TEAL, r=0)
        text(s, 7.8, yy + 0.12, 3.5, 0.3, code, 9, TEAL, FS)
        text(s, 7.8, yy + 0.42, 3.5, 0.4, nm, 14, WHITE, FL)
        text(s, 7.8, yy + 0.88, 4.6, 0.3, dt, 8.5, MUTED)
        st = rect(s, 10.95, yy + 0.15, 1.45, 0.38, fill=None, line=TEAL, r=0.19, lw=1.25)
        text(s, 10.95, yy + 0.15, 1.45, 0.38, '✓ ТАСДИҚЛАНДИ', 7.5, TEAL, FS, align='c', anchor='m')

    s = d.content('05', 'Электрон ариза: жараён ва фойда')
    card(s, 0.55, 1.3, 12.25, 2.45, name='!!c1')
    old = ['Ёзиш', 'Чоп этиш', 'Имзо', 'Раҳбарга топшириш', 'Келишиш', "HR'га етказиш", 'Архивлаш']
    new = ['Ариза турини танлаш', 'Маълумот киритиш', 'Электрон юбориш', 'Раҳбар кўриб чиқади',
           'Автоматик йўналтириш', 'Электрон тарихда сақлаш']
    text(s, 0.8, 1.45, 3, 0.3, 'АВВАЛГИ ЖАРАЁН (ҚОҒОЗ)', 8.5, WARN, FS)
    cw = 11.75 / 7
    for k, t in enumerate(old):
        x = 0.8 + k * cw
        rect(s, x, 1.78, cw - 0.3, 0.55, fill=None, line=DIM, r=0.27, lw=0.75)
        text(s, x, 1.78, cw - 0.3, 0.55, t, 8.5, MUTED, align='c', anchor='m')
        if k < 6:
            text(s, x + cw - 0.3, 1.78, 0.3, 0.55, '›', 12, DIM, align='c', anchor='m')
    text(s, 0.8, 2.58, 3, 0.3, 'ЯНГИ ЖАРАЁН (ЭЛЕКТРОН)', 8.5, TEAL, FS)
    cw = 11.75 / 6
    for k, t in enumerate(new):
        x = 0.8 + k * cw
        rect(s, x, 2.9, cw - 0.3, 0.6, fill=TEAL3, line=TEAL, r=0.3, lw=0.75)
        text(s, x, 2.9, cw - 0.3, 0.6, t, 9, WHITE, align='c', anchor='m')
        if k < 5:
            text(s, x + cw - 0.3, 2.9, 0.3, 0.6, '›', 13, TEAL, align='c', anchor='m')
    ben = [('Ходим ва раҳбар вақти', 'Ариза тезкор шакллантирилади, қўлда етказиш ва излаш йўқолади'),
           ('Канцелярия харажати', 'Қоғоз, сиёҳ ва бланкалар сарфи қисқаради'),
           ('Назорат ва шаффофлик', 'Ариза ҳолатини кузатиш, ягона электрон маълумотлар базаси')]
    for k, (a, b) in enumerate(ben):
        x = 0.55 + k * 4.12
        card(s, x, 3.9, 3.97, 1.55, name='!!c%d' % (k + 2))
        num_badge(s, x + 0.22, 4.08, k + 1, d=0.45, size=12)
        text(s, x + 0.82, 4.08, 3.0, 0.45, a, 12, WHITE, FS, anchor='m')
        text(s, x + 0.22, 4.65, 3.6, 0.7, b, 9.5, MUTED)
    card(s, 0.55, 5.6, 7.7, 1.3, name='!!c5')
    rect(s, 0.55, 5.6, 0.06, 1.3, fill=TEAL, r=0)
    text(s, 0.8, 5.65, 7.3, 1.2,
         [[('★ 96 000 000 сўм тежалди. ', {'color': TEAL, 'font': FS}),
           ('Touch Screen киоск қурилмалари сотиб олинмади — мавжуд участка мастерлари компьютерларидан '
            'фойдаланилди. Қўшимча капитал харажат ва техник хизмат заруратининг олди олинди.', {})]],
         9.5, WHITE, anchor='m')
    card(s, 8.4, 5.6, 4.4, 1.3)
    text(s, 8.6, 5.65, 4.05, 1.2,
         [[('Кейинги босқич: ', {'color': TEAL, 'font': FS}),
           ('йиллик меҳнат таътили бўйича аризаларни электронлаштириш — тизим қамрови янада кенгайтирилади.', {})]],
         9.5, WHITE, anchor='m')

    # ================= 06 · КОРПОРАТИВ МАДАНИЯТ =================
    d.section('06', 'Корпоратив маданият ва коммуникациялар',
              'Байрам тадбирлари, спорт, ижтимоий лойиҳалар ва ички канал')

    s = d.content('06', 'Корпоратив маданият: сентябрь тадбирлари',
                  'ADM Jizzakh Communication · 5 та тадбир ва Табель бўйича сўровнома натижасида 6 та чора-тадбир')
    card(s, 0.55, 1.3, 5.2, 5.6, name='!!c1')
    label(s, 0.8, 1.45, 4.5, 'Сентябрь тадбирлари')
    ev = [('ADM MS бўйича викторина', 'ғолиб тақдирланди (25.09.2026)'),
          ('Табель бўйича сўровнома', 'натижалари ва чоралар — кейинги слайдда'),
          ('«Менинг мактабим»', '4 ходим мактабида тақдирланди'),
          ('«Раҳмат Day»', 'ходимларга миннатдорлик тадбири'),
          ('Ички акциялар', '1 ходим Ишонч савдода Sonet автомобилини ютди')]
    for k, (a, b) in enumerate(ev):
        yy = 1.85 + k * 0.98
        if k < 4:
            rect(s, 0.98, yy + 0.45, 0.02, 0.6, fill=TEAL2, r=0)
        num_badge(s, 0.78, yy, k + 1, d=0.42, size=11)
        text(s, 1.4, yy - 0.02, 4.2, 0.3, a, 11.5, WHITE, FS)
        text(s, 1.4, yy + 0.3, 4.2, 0.5, b, 9.5, MUTED)
    phs = [('event1.jpg', '«Менинг мактабим»'), ('event2.jpg', '«Раҳмат Day»'), ('event3.png', 'Sonet автомобили')]
    for k, (f, cap) in enumerate(phs):
        x = 5.9 + k * 2.32
        card(s, x, 1.3, 2.2, 5.6, name='!!c%d' % (k + 2))
        pic_fill(s, f, x + 0.1, 1.4, 2.0, 4.85)
        text(s, x + 0.1, 6.35, 2.0, 0.4, cap, 10, WHITE, FS, align='c', anchor='m')

    s = d.content('06', 'Табель сўровномаси: натижа → чора-тадбир',
                  'МЕТИҲ — Меҳнатни ташкил этиш ва иш ҳақи бўлинмаси · ТТ — техник топшириқ')
    sv = [['№', 'Сўровнома натижаси', 'Чора-тадбир', 'Масъул', 'Муддат'],
          ['01', '14% қониқмаган (25% қисман)', 'Норози ходимларни бўлим ва цех кесимида аниқлаб, сабабини бартараф этиш',
           'Табель юритувчилар', '5 иш куни'],
          ['02', '13% тартибни тушунмаган (28% тушунтириш сўраган)',
           '«Табель ҳисобини юритиш тартиби» бўйича бригадир, сўнг ходимларни каскад ўқитиш', 'Етакчи табелчи',
           '15 иш куни'],
          ['03', '24% жавобни кечикиб олган (13% олмаган)', 'Табелчилар цехларга бориб, мурожаатни жойида ҳал қилади',
           'Табель юритувчилар', 'Доимий'],
          ['04', '26% ёпилган табель билан танишмаган',
           'ADM Ҳақнома бот ва бўлимлардаги [GL…] орқали ёпилган табелни етказиш', 'Табелчилар, раҳбарлар, HR',
           'Ҳар ой, ёпилгач 3 кунда'],
          ['05', '92% Telegram ботни қулай деган', 'IT билан бот: ходим ўз табели ва KPI ни кўради; аввал битта бўлинмада синов',
           'IT бўлими, МЕТИҲ', 'ТТ тайёр; бот 30 кунда'],
          ['06', 'Самарадорликни текшириш', 'Ижро ва мурожаат статистикаси ҳар ҳафта; якунда қайта сўровнома',
           'МЕТИҲ бўлинмаси', 'Ҳар ҳафта; якун 2 ойда']]
    card(s, 0.55, 1.3, 12.25, 5.6, name='!!c1')
    table(s, 0.75, 1.5, 11.85, sv, [0.5, 3.0, 4.7, 2.0, 1.65], rh=0.74, size=10, align='clllc',
          colors={(i, 1): TEAL for i in range(1, 7)})

    # ================= 07 · ИНТИЗОМ =================
    d.section('07', 'Интизом бўйича', '2025 ва 2026-йил солиштирмаси ҳамда янги ички тартиб қоидалари')

    s = d.content('07', 'Интизом бўйича: 2025 ва 2026-йил',
                  '2026 — 9,5 ой (14-октябргача) · интизомий ҳолатлар 2025 йил билан солиштирилди')
    cmp_ = [('ЙТҲ (ходим)', '5 → 10', '2 баравар', '2 та шартнома тугатилди', WARN),
            ('Масъулиятсизлик (ҳолат)', '46 → 24', '−52%', '2025: 17 ходим', TEAL),
            ('Муштлашув (ходим)', '2 → 6', '3 баравар', '1 → 3 ҳолат', WARN),
            ('Талон-торож (ҳолат)', '1 → 2', 'Ошган', '5 ходим, 1 та шартнома бекор қилинди', WARN)]
    for k, (a, v, ch_, sb, ac) in enumerate(cmp_):
        x = 0.55 + k * 3.1
        card(s, x, 1.3, 2.95, 1.95, name='!!c%d' % (k + 1))
        rect(s, x, 1.3, 2.95, 0.05, fill=ac, r=0)
        text(s, x + 0.22, 1.47, 2.6, 0.3, a.upper(), 8.5, MUTED, FS)
        text(s, x + 0.22, 1.72, 2.6, 0.65, v, 28, WHITE, FL)
        rect(s, x + 0.22, 2.42, 1.15, 0.32, fill=ac, r=0.16, alpha=0.2)
        text(s, x + 0.22, 2.42, 1.15, 0.32, ch_, 9, ac, FS, align='c', anchor='m')
        text(s, x + 0.22, 2.82, 2.6, 0.35, sb, 8, DIM)
    card(s, 0.55, 3.4, 7.7, 3.5)
    label(s, 0.8, 3.53, 7, '2025 ва 2026 солиштирмаси')
    multi(s, 0.65, 3.75, 7.5, 3.1, ['Интизомий жазо\nолган ходимлар', 'Масъулиятсизлик\nҳолатлари', 'Сабабсиз\nчиқмаслик',
                                    'ЙТҲ, ходим', 'Муштлашув,\nходим', 'Талон-торож,\nходим'],
          [('2025', [76, 46, 10, 5, 2, 1], '58616B'), ('2026', [50, 24, 1, 10, 6, 5], TEAL)], size=8.5, gap=70,
          overlap=-5)
    card(s, 8.4, 3.4, 4.4, 3.5)
    label(s, 8.65, 3.53, 4, 'Ишга сабабсиз чиқмаслик')
    text(s, 8.65, 3.8, 4, 0.8, [[('10', {'color': MUTED}), (' → ', {'color': DIM}), ('1', {'color': TEAL})]], 36,
         font=FL)
    text(s, 8.65, 4.65, 3.95, 1.0,
         'Ҳақиқий пасайиш эмас: 1 кунлик прогуллар учун жазо тури таъсир чораларига ўзгартирилган.', 9.5, MUTED)
    rect(s, 8.65, 5.6, 3.95, 1.1, fill=WARN, r=0.1, alpha=0.14)
    text(s, 8.85, 5.6, 1.1, 1.1, '69', 32, WARN, FL, anchor='m')
    text(s, 9.85, 5.6, 2.65, 1.1, '2026-йилда ходим ишга сабабсиз келмаганлиги учун ишдан бўшаган', 9, WHITE,
         anchor='m')

    s = d.content('07', 'Интизом: 2026-йилдаги ўзгаришлар',
                  'Интизомий жазолар қайта кўриб чиқилди ва ички меҳнат тартиби қоидалари янгиланди')
    card(s, 0.55, 1.3, 7.2, 2.7, name='!!c1')
    rect(s, 0.55, 1.3, 0.06, 2.7, fill=TEAL, r=0)
    text(s, 0.9, 1.45, 3, 1.6, '29', 96, TEAL, FL)
    text(s, 3.4, 1.85, 4.1, 0.3, 'НАФАР ХОДИМ', 10, TEAL, FS)
    text(s, 3.4, 2.2, 4.1, 1.2, 'Интизомий жазо чорасининг таъсири муддатидан олдин тугатилди', 15, WHITE, FL)
    card(s, 0.55, 4.15, 7.2, 2.75, name='!!c2')
    shape(s, MSO_SHAPE.OVAL, 0.95, 4.6, 1.6, 1.6, fill=TEAL3, line=TEAL, lw=1.5)
    text(s, 0.95, 4.6, 1.6, 1.6, '✓', 48, TEAL, FS, align='c', anchor='m')
    text(s, 3.0, 4.75, 4.5, 0.3, 'ЯНГИ ТАҲРИР', 10, TEAL, FS)
    text(s, 3.0, 5.1, 4.5, 1.2, 'Ички меҳнат тартиби қоидалари тасдиқланди', 15, WHITE, FL)
    text(s, 3.0, 6.1, 4.5, 0.3, 'ҳужжат ўнгда →', 9, MUTED)
    card(s, 7.9, 1.3, 4.9, 5.6, name='!!c3')
    pic(s, 'doc.png', 8.0 + (4.7 - 5.4 * 518 / 734) / 2, 1.4, None, 5.4)

    # ================= ЯКУН =================
    s = d.new()
    rings(s, W / 2, H / 2 - 0.55, k=0.95, rot=(0, 0))
    disc(s, W / 2, H / 2 - 0.55, 1.8)
    text(s, W / 2 - 4, H - 1.45, 8, 0.6, 'Эътиборингиз учун раҳмат!', 26, WHITE, FL, align='c', name='!!title')
    text(s, W / 2 - 4, H - 0.85, 8, 0.4, 'Саволлар бўлса, марҳамат', 12, MUTED, align='c', name='!!sub')
    brand(s)
    morph(s)

    d.save()
    print('OK', OUT, d.n, 'slides')


if __name__ == '__main__':
    build()
