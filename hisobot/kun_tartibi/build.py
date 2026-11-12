# Rahbar kunlik ish tartibi — Excel shablon (namuna: Boʻyoqlash sexi boshligʻi).
# Rahbar har qadamga vaqt va TOIFANI oʻzi yozadi (alohida varaq yoʻq). Oʻngdagi diagrammalar yozilgan toifalardan oʻzi shakllanadi:
# har xil toifa — alohida rang, eng koʻp vaqt ketgan ish — tepada. «Tushlik» deb yozilgan qadam ish vaqti ulushiga kirmaydi.
#   python3 build.py  -> Rahbar_kun_tartibi_shablon.xlsx
import datetime as dt, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule, DataBarRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.chart import DoughnutChart, BarChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.title import Title
from openpyxl.chart.text import Text, RichText
from openpyxl.chart.data_source import StrRef, StrData, StrVal
from openpyxl.drawing.text import Paragraph, ParagraphProperties, CharacterProperties, Font as DFont
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.utils.units import cm_to_EMU
from openpyxl.workbook.properties import CalcProperties

OUT, SRC = 'Rahbar_kun_tartibi_shablon.xlsx', 'kirish/namuna.xlsx'
PAL = ['3CC6B8', '5B8DEF', 'E8826E', 'A78BFA', 'E8B86E', '94A3B8', 'F472B6', '84CC16', '22D3EE', 'FB923C']   # toifa ranglari (paydo boʻlish tartibida)
NC = len(PAL)                       # koʻpi bilan 10 xil toifa
NAMUNA = ['Йиғилишлар', 'Ҳисобот ва тайёргарлик', 'Йиғилишлар', 'Почта ва ЭДО', 'Линияда назорат (GO&SEE)', 'Тушлик',
          'Сифат ва муаммолар таҳлили', 'Жамоа билан ишлаш ва ўқитиш', 'Линияда назорат (GO&SEE)', 'Ҳисобот ва тайёргарлик']
NROWS = 14
INK, SUBT, LINE_C, HEAD = '1F2937', '6B7280', 'E5E7EB', '1F2937'
F = lambda c: PatternFill('solid', fgColor=c)
def font(c=INK, b=False, s=10, i=False): return Font(name='Segoe UI', color=c, bold=b, size=s, italic=i)
CEN = Alignment(horizontal='center', vertical='center', wrap_text=True)
LFT = Alignment(horizontal='left', vertical='center', wrap_text=True, indent=1)
TOP = Alignment(horizontal='left', vertical='top', wrap_text=True, indent=1)
BOT = Border(bottom=Side(style='thin', color=LINE_C))
def is_lunch(s): return any(w in s.lower() for w in ('тушлик', 'tushlik', 'обед'))

src = list(openpyxl.load_workbook(SRC, data_only=True).active.iter_rows(values_only=True))
STEPS = []
for r in src:
    if isinstance(r[0], int) and r[1]:
        a, b = [x.strip() for x in str(r[1]).split('-')]
        t = lambda s: dt.time(*map(int, s.split(':')))
        STEPS.append((t(a), t(b), NAMUNA[len(STEPS)], ' '.join(str(r[2]).split()), r[3]))
assert len(STEPS) == len(NAMUNA)

CHARTS = []
wb = openpyxl.Workbook(); wb.calculation = CalcProperties(fullCalcOnLoad=True); wb.remove(wb.active)

def build(ws, steps, title, who):
    ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
    for k, v in {'A': 2, 'B': 5, 'C': 9, 'D': 9, 'E': 9, 'F': 28, 'G': 70, 'H': 22, 'I': 3, 'J': 34, 'K': 11, 'L': 11, 'M': 11}.items(): ws.column_dimensions[k].width = v
    for c in 'PQRSTU': ws.column_dimensions[c].hidden = True
    for c in range(1, 14):
        for r in (1, 2, 3): ws.cell(r, c).fill = F(HEAD)
    ws['B1'] = 'РАҲБАР КУНЛИК ИШ ТАРТИБИ'; ws['B1'].font = font('3CC6B8', True, 10)
    ws['B2'] = title; ws['B2'].font = font('FFFFFF', True, 20)
    ws['B3'] = who; ws['B3'].font = font('C7CBD1', False, 10)
    ws.row_dimensions[1].height = 20; ws.row_dimensions[2].height = 34; ws.row_dimensions[3].height = 22
    ws['J2'] = 'ADM JIZZAKH'; ws['J2'].font = font('FFFFFF', True, 12); ws['J2'].alignment = Alignment(horizontal='right'); ws.merge_cells('J2:M2')
    H = 5; R0 = H + 1; R1 = H + NROWS
    for c, t in zip('BCDEFGH', ['№', 'Бошлаш', 'Тугаш', 'Дақиқа', 'Тоифа (ўзингиз ёзинг)', 'Қадамлар таснифи (нима иш қилинади)', 'Изоҳ / натижа']):
        x = ws[f'{c}{H}']; x.value = t; x.font = font(SUBT, True, 9); x.alignment = CEN if c != 'G' else LFT; x.border = Border(bottom=Side(style='medium', color=INK))
    ws.row_dimensions[H].height = 26
    # --- yashirin hisob: P = toifa birinchi marta uchragan tartib raqami; Q = toifalar ro'yxati; R = daqiqa; S = ulush; T = saralash kaliti; U = tur (1 ish, -1 tushlik, 0 bo'sh)
    for i in range(NROWS):
        r = R0 + i
        lf = f'OR(ISNUMBER(SEARCH("тушлик",F{r})),ISNUMBER(SEARCH("tushlik",F{r})),ISNUMBER(SEARCH("обед",F{r})))'
        ws[f'P{r}'] = f'=IF(AND(TRIM(F{r})<>"",NOT({lf}),COUNTIF($F${R0}:F{r},F{r})=1),MAX($P${H}:P{r - 1})+1,"")'
    QA, QB = R0, R0 + NC - 1
    for k in range(NC):
        q = QA + k
        ws[f'Q{q}'] = f'=IFERROR(INDEX($F${R0}:$F${R1},MATCH({k + 1},$P${R0}:$P${R1},0)),"")'
        lun = f'OR(ISNUMBER(SEARCH("тушлик",Q{q})),ISNUMBER(SEARCH("tushlik",Q{q})),ISNUMBER(SEARCH("обед",Q{q})))'
        ws[f'R{q}'] = f'=IF(Q{q}="",0,IF({lun},0,SUMIF($F${R0}:$F${R1},Q{q},$E${R0}:$E${R1})))'
        ws[f'U{q}'] = f'=IF(Q{q}="",0,IF({lun},-1,1))'
        ws[f'T{q}'] = f'=IF(U{q}=1,R{q}+ROW()/10000,-1)'
    tw = f'SUM($R${QA}:$R${QB})'
    from openpyxl.workbook.defined_name import DefinedName
    sq = "'" + ws.title.replace("'", "''") + "'"
    cnt = f'MAX(1,COUNTIF({sq}!$U${QA}:$U${QB},1))'
    ws.defined_names.add(DefinedName('ToifaNom', attr_text=f'OFFSET({sq}!$Q${QA},0,0,{cnt},1)'))
    ws.defined_names.add(DefinedName('ToifaDaq', attr_text=f'OFFSET({sq}!$R${QA},0,0,{cnt},1)'))
    for k in range(NC): ws[f'S{QA + k}'] = f'=IF({tw}=0,0,R{QA + k}/{tw})'
    # --- jadval
    dv = DataValidation(type='list', formula1=f'=$Q${QA}:$Q${QB}', allow_blank=True, showErrorMessage=False); ws.add_data_validation(dv)
    dvt = DataValidation(type='time', operator='between', formula1='0', formula2='0.999988', allow_blank=True, showErrorMessage=True, errorTitle='Вақт', error='Вақтни 08:50 кўринишида ёзинг')
    ws.add_data_validation(dvt)
    for i in range(NROWS):
        r = R0 + i; st = steps[i] if i < len(steps) else None
        ws.cell(r, 2, f'=IF(C{r}="","",ROW()-{H})').font = font(SUBT, True, 10); ws.cell(r, 2).alignment = CEN
        for c, v in ((3, st[0] if st else None), (4, st[1] if st else None)):
            x = ws.cell(r, c, v); x.number_format = 'hh:mm'; x.font = font(INK, True, 11); x.alignment = CEN
        ws.cell(r, 5, f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(D{r})),ROUND((D{r}-C{r})*1440,0),"")').font = font(INK, True, 11); ws.cell(r, 5).alignment = CEN
        ws.cell(r, 6, st[2] if st else None).font = font(INK, True, 10); ws.cell(r, 6).alignment = LFT
        ws.cell(r, 7, st[3] if st else None).font = font(INK, False, 10); ws.cell(r, 7).alignment = TOP
        ws.cell(r, 8, st[4] if st else None).font = font(SUBT, False, 9); ws.cell(r, 8).alignment = TOP
        for c in range(2, 9): ws.cell(r, c).border = BOT
        ws.cell(r, 6).border = Border(bottom=Side(style='thin', color=LINE_C), left=Side(style='thin', color=LINE_C), right=Side(style='thin', color=LINE_C))
        ws.row_dimensions[r].height = max(32, -(-len(st[3]) // 78) * 14 + 10) if st else 30
    dv.add(f'F{R0}:F{R1}'); dvt.add(f'C{R0}:D{R1}')
    # rang: toifa ro'yxatdagi o'rniga qarab (tushlik — kulrang)
    lr0 = f'OR(ISNUMBER(SEARCH("тушлик",$F{R0})),ISNUMBER(SEARCH("tushlik",$F{R0})),ISNUMBER(SEARCH("обед",$F{R0})))'
    for rg in (f'F{R0}:F{R1}', f'B{R0}:B{R1}'): ws.conditional_formatting.add(rg, FormulaRule(formula=[lr0], fill=F('D5D9DE'), stopIfTrue=True))
    for k in range(NC):
        cond = f'AND($F{R0}<>"",$F{R0}=$Q${QA + k})'
        ws.conditional_formatting.add(f'F{R0}:F{R1}', FormulaRule(formula=[cond], fill=F(PAL[k]), stopIfTrue=True))
        ws.conditional_formatting.add(f'B{R0}:B{R1}', FormulaRule(formula=[cond], fill=F(PAL[k]), font=Font(color='FFFFFF', bold=True), stopIfTrue=True))
    ws.conditional_formatting.add(f'E{R0}:E{R1}', DataBarRule(start_type='num', start_value=0, end_type='max', color='9CA3AF', showValue=True))
    # --- panel sarlavhalari (formulali)
    top = f'INDEX(Q{QA}:Q{QB},MATCH(MAX(T{QA}:T{QB}),T{QA}:T{QB},0))'
    topm = f'INDEX(R{QA}:R{QB},MATCH(MAX(T{QA}:T{QB}),T{QA}:T{QB},0))'
    ws['Q2'] = f'=IF({tw}<=0,"ЭНГ КЎП ВАҚТ: —","ЭНГ КЎП ВАҚТ:  "&{top}&CHAR(10)&INT({topm}/60)&" соат "&MOD({topm},60)&" дақиқа  ·  иш вақтининг "&TEXT({topm}/{tw},"0%"))'
    ws['Q3'] = f'="Жами иш вақти: "&INT({tw}/60)&" соат "&MOD({tw},60)&" дақ. (тушликсиз)"&CHAR(10)&COUNTIF(U{QA}:U{QB},1)&" хил иш тоифаси"'
    # kesh (Python hisobi)
    cats, mins = [], {}
    for st in steps:
        if st[2] not in cats: cats.append(st[2])
        m = (st[1].hour * 60 + st[1].minute) - (st[0].hour * 60 + st[0].minute)
        if not is_lunch(st[2]): mins[st[2]] = mins.get(st[2], 0) + m
    twv = sum(mins.values())
    if twv:
        tc = max(mins, key=lambda c: (mins[c], -cats.index(c))); tm = mins[tc]
        c2 = f'ЭНГ КЎП ВАҚТ:  {tc}\n{tm // 60} соат {tm % 60} дақиқа  ·  иш вақтининг {round(tm / twv * 100)}%'
    else: c2 = 'ЭНГ КЎП ВАҚТ: —'
    c3 = f'Жами иш вақти: {twv // 60} соат {twv % 60} дақ. (тушликсиз)\n{len(mins)} хил иш тоифаси'
    order = [c for c in cats if c in mins]
    CHARTS.append(dict(sheet=ws.title, kind='bar', title=('Q2', c2, 1300, '1F2937'), cats=order, vals=[mins[c] for c in order]))
    CHARTS.append(dict(sheet=ws.title, kind='donut', title=('Q3', c3, 1050, '374151'), cats=order, vals=[mins[c] for c in order]))
    sname = ws.title.replace("'", "''")
    def ttl(cell, cache, size=1300, color='1F2937'):
        sr = StrRef(f=f"'{sname}'!${cell[0]}${cell[1:]}", strCache=StrData(ptCount=1, pt=[StrVal(idx=0, v=cache)]))
        cp = CharacterProperties(sz=size, b=True, solidFill=color, latin=DFont(typeface='Segoe UI'))
        return Title(tx=Text(strRef=sr), overlay=False, txPr=RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)]))
    def anchor(chart, row, off_pt, w_cm, h_cm):
        chart.anchor = OneCellAnchor(_from=AnchorMarker(col=9, colOff=0, row=row - 1, rowOff=int(off_pt * 12700)), ext=XDRPositiveSize2D(cm_to_EMU(w_cm), cm_to_EMU(h_cm)))
        ws.add_chart(chart)
    def row_at(pt):
        acc = 0
        for r in range(6, 300):
            hh = ws.row_dimensions[r].height or 15
            if acc + hh > pt: return r, pt - acc
            acc += hh
    ws['J5'] = 'ВАҚТ ҚАЕРГА КЕТМОҚДА?'; ws['J5'].font = font(INK, True, 13); ws['J5'].alignment = Alignment(vertical='center')
    lab = RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=900, solidFill='374151', latin=DFont(typeface='Segoe UI'))), endParaRPr=CharacterProperties(sz=900))])
    # 1) ustunlar — har toifa necha daqiqa
    bc = BarChart(); bc.type = 'bar'; bc.grouping = 'clustered'; bc.legend = None; bc.gapWidth = 40; bc.visible_cells_only = False
    bc.add_data(Reference(ws, min_col=18, min_row=QA, max_row=QB), titles_from_data=False)
    bc.set_categories(Reference(ws, min_col=17, min_row=QA, max_row=QB))
    bc.title = ttl('Q2', c2)
    bc.x_axis.scaling.orientation = 'maxMin'; bc.y_axis.delete = True; bc.y_axis.majorGridlines = None; bc.x_axis.majorTickMark = 'none'; bc.x_axis.txPr = lab
    sr = bc.series[0]
    for k in range(NC):
        pt = DataPoint(idx=k); pt.graphicalProperties.solidFill = PAL[k]; pt.graphicalProperties.line.noFill = True; sr.dPt.append(pt)
    sr.dLbls = DataLabelList(); sr.dLbls.showVal = True; sr.dLbls.showCatName = False; sr.dLbls.showSerName = False; sr.dLbls.showPercent = False; sr.dLbls.showLegendKey = False
    sr.dLbls.numFmt = '0" дақ.";;;'; sr.dLbls.position = 'outEnd'
    anchor(bc, 6, 4, 12.8, 10.2)
    # 2) halqa — ulush
    dc = DoughnutChart(); dc.holeSize = 55; dc.legend = None; dc.visible_cells_only = False
    dc.add_data(Reference(ws, min_col=18, min_row=QA, max_row=QB), titles_from_data=False)
    dc.set_categories(Reference(ws, min_col=17, min_row=QA, max_row=QB))
    dc.title = ttl('Q3', c3, 1050, '374151')
    ds = dc.series[0]
    for k in range(NC):
        pt = DataPoint(idx=k); pt.graphicalProperties.solidFill = PAL[k]; pt.graphicalProperties.line.solidFill = 'FFFFFF'; ds.dPt.append(pt)
    ds.dLbls = DataLabelList(); ds.dLbls.showPercent = True; ds.dLbls.showVal = False; ds.dLbls.showCatName = False; ds.dLbls.showSerName = False; ds.dLbls.showLegendKey = False; ds.dLbls.showLeaderLines = False
    ds.dLbls.numFmt = '0%;;;'
    r_, o_ = row_at(10.2 / 2.54 * 72 + 14); anchor(dc, r_, o_, 12.8, 8.0)
    r_, o_ = row_at((10.2 + 8.0) / 2.54 * 72 + 26)
    ws[f'J{r_ + 1}'] = 'Тоифани ўзингиз ёзинг (олдин ёзилганини рўйхатдан танлаш ҳам мумкин). Бир хил иш — бир хил ном. «Тушлик» иш вақтига кирмайди.'
    ws[f'J{r_ + 1}'].font = font(SUBT, False, 8, True)
    ws.freeze_panes = f'A{R0}'
    ws.print_area = f'A1:M{max(R1, r_ + 1)}'
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True
    for m in ('left', 'right'): setattr(ws.page_margins, m, 0.3)

build(wb.create_sheet('Намуна — Бўёқлаш'), STEPS, 'Бўёқлаш цехи бошлиғи', 'Ф.И.Ш.: ______________________     ·     Сана: ____.____.2026     ·     Иш вақти: 08:50 – 18:00')
build(wb.create_sheet('Бўш шаблон'), [], 'Лавозим: ______________________', 'Ф.И.Ш.: ______________________     ·     Сана: ____.____.2026     ·     Иш вақти: ____ – ____')
wb.save(OUT)

import zipfile
from xml.sax.saxutils import escape as X
def rpr(sz, color, b=1): return f'<a:defRPr sz="{sz}" b="{b}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="Segoe UI"/><a:cs typeface="Segoe UI"/></a:defRPr>'
def txpr(sz, color, b=0): return f'<c:txPr><a:bodyPr/><a:lstStyle/><a:p><a:pPr>{rpr(sz, color, b)}</a:pPr><a:endParaRPr lang="ru-RU"/></a:p></c:txPr>'
def chart_xml(ch):
    sq = "'" + ch['sheet'].replace("'", "''") + "'"
    cell, cache, sz, col = ch['title']; n = max(1, len(ch['cats']))
    cats = ch['cats'] or ['']; vals = ch['vals'] or [0]
    strc = f'<c:ptCount val="{n}"/>' + ''.join(f'<c:pt idx="{i}"><c:v>{X(c)}</c:v></c:pt>' for i, c in enumerate(cats))
    numc = f'<c:formatCode>General</c:formatCode><c:ptCount val="{n}"/>' + ''.join(f'<c:pt idx="{i}"><c:v>{v}</c:v></c:pt>' for i, v in enumerate(vals))
    title = (f'<c:title><c:tx><c:strRef><c:f>{sq}!${cell[0]}${cell[1:]}</c:f><c:strCache><c:ptCount val="1"/><c:pt idx="0"><c:v>{X(cache)}</c:v></c:pt></c:strCache></c:strRef></c:tx>'
             f'<c:overlay val="0"/>{txpr(sz, col, 1)}</c:title><c:autoTitleDeleted val="0"/>')
    if ch['kind'] == 'bar':
        dpt = ''.join(f'<c:dPt><c:idx val="{k}"/><c:invertIfNegative val="0"/><c:bubble3D val="0"/><c:spPr><a:solidFill><a:srgbClr val="{PAL[k]}"/></a:solidFill></c:spPr></c:dPt>' for k in range(NC))
        lbl = f'<c:dLbls><c:numFmt formatCode="0&quot; дақ.&quot;;;;" sourceLinked="0"/><c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr>{txpr(900, "374151", 1)}<c:dLblPos val="outEnd"/><c:showLegendKey val="0"/><c:showVal val="1"/><c:showCatName val="0"/><c:showSerName val="0"/><c:showPercent val="0"/><c:showBubbleSize val="0"/></c:dLbls>'
        plot = (f'<c:barChart><c:barDir val="bar"/><c:grouping val="clustered"/><c:varyColors val="0"/><c:ser><c:idx val="0"/><c:order val="0"/>'
                f'<c:spPr><a:solidFill><a:srgbClr val="{PAL[0]}"/></a:solidFill></c:spPr><c:invertIfNegative val="0"/>{dpt}{lbl}'
                f'<c:cat><c:strRef><c:f>{sq}!ToifaNom</c:f><c:strCache>{strc}</c:strCache></c:strRef></c:cat>'
                f'<c:val><c:numRef><c:f>{sq}!ToifaDaq</c:f><c:numCache>{numc}</c:numCache></c:numRef></c:val></c:ser>'
                f'<c:gapWidth val="45"/><c:axId val="111"/><c:axId val="222"/></c:barChart>'
                f'<c:catAx><c:axId val="111"/><c:scaling><c:orientation val="maxMin"/></c:scaling><c:delete val="0"/><c:axPos val="l"/><c:numFmt formatCode="General" sourceLinked="0"/>'
                f'<c:majorTickMark val="none"/><c:minorTickMark val="none"/><c:tickLblPos val="nextTo"/><c:spPr><a:ln w="9525"><a:solidFill><a:srgbClr val="D1D5DB"/></a:solidFill></a:ln></c:spPr>{txpr(900, "374151", 0)}'
                f'<c:crossAx val="222"/><c:crosses val="autoZero"/><c:auto val="1"/><c:lblAlgn val="ctr"/><c:lblOffset val="100"/><c:noMultiLvlLbl val="0"/></c:catAx>'
                f'<c:valAx><c:axId val="222"/><c:scaling><c:orientation val="minMax"/><c:min val="0"/></c:scaling><c:delete val="1"/><c:axPos val="b"/><c:numFmt formatCode="General" sourceLinked="1"/>'
                f'<c:majorTickMark val="none"/><c:minorTickMark val="none"/><c:tickLblPos val="nextTo"/><c:crossAx val="111"/><c:crosses val="max"/><c:crossBetween val="between"/></c:valAx>')
    else:
        dpt = ''.join(f'<c:dPt><c:idx val="{k}"/><c:bubble3D val="0"/><c:spPr><a:solidFill><a:srgbClr val="{PAL[k]}"/></a:solidFill><a:ln w="19050"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln></c:spPr></c:dPt>' for k in range(NC))
        lbl = f'<c:dLbls><c:numFmt formatCode="0%;;;" sourceLinked="0"/><c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr>{txpr(900, "1F2937", 1)}<c:showLegendKey val="0"/><c:showVal val="0"/><c:showCatName val="0"/><c:showSerName val="0"/><c:showPercent val="1"/><c:showBubbleSize val="0"/><c:showLeaderLines val="0"/></c:dLbls>'
        plot = (f'<c:doughnutChart><c:varyColors val="1"/><c:ser><c:idx val="0"/><c:order val="0"/>{dpt}{lbl}'
                f'<c:cat><c:strRef><c:f>{sq}!ToifaNom</c:f><c:strCache>{strc}</c:strCache></c:strRef></c:cat>'
                f'<c:val><c:numRef><c:f>{sq}!ToifaDaq</c:f><c:numCache>{numc}</c:numCache></c:numRef></c:val></c:ser>'
                f'<c:firstSliceAng val="0"/><c:holeSize val="55"/></c:doughnutChart>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><c:roundedCorners val="0"/>'
            f'<c:chart>{title}<c:plotArea><c:layout/>{plot}<c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr></c:plotArea>'
            '<c:plotVisOnly val="0"/><c:dispBlanksAs val="gap"/></c:chart>'
            '<c:spPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:ln w="9525"><a:solidFill><a:srgbClr val="E5E7EB"/></a:solidFill></a:ln></c:spPr>'
            '<c:txPr><a:bodyPr/><a:lstStyle/><a:p><a:pPr><a:defRPr><a:latin typeface="Segoe UI"/></a:defRPr></a:pPr><a:endParaRPr lang="ru-RU"/></a:p></c:txPr></c:chartSpace>')
zin = zipfile.ZipFile(OUT); files = {n: zin.read(n) for n in zin.namelist()}; zin.close()
for i, ch in enumerate(CHARTS, 1):
    assert f'xl/charts/chart{i}.xml' in files
    files[f'xl/charts/chart{i}.xml'] = chart_xml(ch).encode('utf-8')
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items(): z.writestr(n, b)
print('ok', OUT, len(STEPS), 'qadam')
