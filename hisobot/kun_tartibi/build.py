# Rahbar kunlik ish tartibi — Excel shablon (namuna: Boʻyoqlash sexi boshligʻi).
# Har qatorga vaqt (boshlanish/tugash) va toifa kiritiladi; oʻngdagi panel vaqt taqsimotini, eng koʻp vaqt ketgan ishni va diagrammani oʻzi hisoblaydi.
#   python3 build.py  -> Rahbar_kun_tartibi_shablon.xlsx
import datetime as dt, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule, DataBarRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.chart import DoughnutChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.chart.label import DataLabelList
from openpyxl.workbook.properties import CalcProperties

OUT = 'Rahbar_kun_tartibi_shablon.xlsx'
SRC = 'kirish/namuna.xlsx'
CATS = [('Йиғилишлар (SPQRC, Operation, GCA)', '5B8DEF'), ('Линияда назорат (GO&SEE)', '3CC6B8'), ('Сифат ва муаммолар таҳлили', 'E8826E'),
        ('Жамоа билан ишлаш ва ўқитиш', 'A78BFA'), ('Ҳисобот ва тайёргарлик', 'E8B86E'), ('Почта ва ЭДО', '94A3B8'), ('Тушлик', 'D5D9DE')]
LUNCH = len(CATS)  # oxirgisi — tushlik (ish vaqti ulushiga kirmaydi)
NAMUNA_CAT = [1, 5, 1, 6, 2, 7, 3, 4, 2, 5]  # Boʻyoqlash namunasidagi har qadamning toifasi
NROWS = 14
INK, SUBT, LINE_C, HEAD, PANEL = '1F2937', '6B7280', 'E5E7EB', '1F2937', 'F3F4F6'
F = lambda c: PatternFill('solid', fgColor=c)
def font(c=INK, b=False, s=10, i=False): return Font(name='Segoe UI', color=c, bold=b, size=s, italic=i)
CEN = Alignment(horizontal='center', vertical='center', wrap_text=True)
LFT = Alignment(horizontal='left', vertical='center', wrap_text=True, indent=1)
TOP = Alignment(horizontal='left', vertical='top', wrap_text=True, indent=1)
thin = Side(style='thin', color=LINE_C); BOT = Border(bottom=thin)

# ---------- namuna maʼlumoti ----------
src = list(openpyxl.load_workbook(SRC, data_only=True).active.iter_rows(values_only=True))
TITLE = str(src[0][0]).strip()
STEPS = []
for r in src:
    if isinstance(r[0], int) and r[1]:
        a, b = [x.strip() for x in str(r[1]).split('-')]
        t = lambda s: dt.time(*map(int, s.split(':')))
        STEPS.append((t(a), t(b), ' '.join(str(r[2]).split()), r[3]))
assert len(STEPS) == len(NAMUNA_CAT)

wb = openpyxl.Workbook(); wb.calculation = CalcProperties(fullCalcOnLoad=True)
# ---------- Тоифалар ----------
wc = wb.active; wc.title = 'Тоифалар'
wc['B1'] = 'Иш тоифалари (номини ўзгартириш мумкин — шаблон ўзи янгиланади)'; wc['B1'].font = font(INK, True, 12)
for i, (n, c) in enumerate(CATS, 2):
    wc.cell(i, 2, n).font = font(INK, True, 11); wc.cell(i, 2).fill = F(c); wc.cell(i, 2).alignment = LFT
    wc.cell(i, 3, 'тушлик — иш вақти улушига кирмайди' if i - 1 == LUNCH else '').font = font(SUBT, False, 9, True)
wc.column_dimensions['B'].width = 40; wc.column_dimensions['C'].width = 36
for i in range(2, 2 + len(CATS)): wc.row_dimensions[i].height = 24
CATREF = f"Тоифалар!$B$2:$B${1 + len(CATS)}"

def build(ws, steps, title, who):
    ws.sheet_view.showGridLines = False; ws.sheet_view.zoomScale = 90
    widths = {'A': 2, 'B': 5, 'C': 9, 'D': 9, 'E': 9, 'F': 30, 'G': 70, 'H': 22, 'I': 3, 'J': 34, 'K': 11, 'L': 11, 'M': 11, 'N': 3, 'O': 8}
    for k, v in widths.items(): ws.column_dimensions[k].width = v
    ws.column_dimensions['O'].hidden = True
    # sarlavha bandi
    for c in range(1, 15):
        for r in (1, 2, 3): ws.cell(r, c).fill = F(HEAD)
    ws['B1'] = 'РАҲБАР КУНЛИК ИШ ТАРТИБИ'; ws['B1'].font = font('3CC6B8', True, 10)
    ws['B2'] = title; ws['B2'].font = font('FFFFFF', True, 20)
    ws['B3'] = who; ws['B3'].font = font('C7CBD1', False, 10)
    ws.row_dimensions[1].height = 20; ws.row_dimensions[2].height = 34; ws.row_dimensions[3].height = 22
    ws['J2'] = 'ADM JIZZAKH'; ws['J2'].font = font('FFFFFF', True, 12); ws['J2'].alignment = Alignment(horizontal='right')
    ws.merge_cells('J2:M2')
    # jadval sarlavhasi
    H = 5
    for c, t in zip('BCDEFGH', ['№', 'Бошлаш', 'Тугаш', 'Дақиқа', 'Тоифа', 'Қадамлар таснифи (нима иш қилинади)', 'Изоҳ / натижа']):
        x = ws[f'{c}{H}']; x.value = t; x.font = font(SUBT, True, 9); x.alignment = CEN if c != 'G' else LFT; x.border = Border(bottom=Side(style='medium', color=INK))
    ws.row_dimensions[H].height = 26
    dv = DataValidation(type='list', formula1=f'={CATREF}', allow_blank=True); ws.add_data_validation(dv)
    dvt = DataValidation(type='time', operator='between', formula1='0', formula2='0.999988', allow_blank=True, showErrorMessage=True,
                         errorTitle='Вақт', error='Вақтни 08:50 кўринишида ёзинг'); ws.add_data_validation(dvt)
    R0 = H + 1; R1 = H + NROWS
    for i in range(NROWS):
        r = R0 + i; st = steps[i] if i < len(steps) else None
        ws.cell(r, 2, f'=IF(C{r}="","",ROW()-{H})').font = font(SUBT, True, 10); ws.cell(r, 2).alignment = CEN
        for c, v in ((3, st[0] if st else None), (4, st[1] if st else None)):
            x = ws.cell(r, c, v); x.number_format = 'hh:mm'; x.font = font(INK, True, 11); x.alignment = CEN
        ws.cell(r, 5, f'=IF(AND(ISNUMBER(C{r}),ISNUMBER(D{r})),ROUND((D{r}-C{r})*1440,0),"")').font = font(INK, True, 11); ws.cell(r, 5).alignment = CEN
        ws.cell(r, 6, CATS[NAMUNA_CAT[i] - 1][0] if st else None).font = font(INK, True, 9); ws.cell(r, 6).alignment = LFT
        ws.cell(r, 7, st[2] if st else None).font = font(INK, False, 10); ws.cell(r, 7).alignment = TOP
        ws.cell(r, 8, st[3] if st else None).font = font(SUBT, False, 9); ws.cell(r, 8).alignment = TOP
        for c in range(2, 9): ws.cell(r, c).border = BOT
        ws.row_dimensions[r].height = max(32, -(-len(st[2]) // 78) * 14 + 10) if st else 30
    dv.add(f'F{R0}:F{R1}'); dvt.add(f'C{R0}:D{R1}')
    for k, (n, c) in enumerate(CATS, 2):
        ws.conditional_formatting.add(f'F{R0}:F{R1}', FormulaRule(formula=[f'$F{R0}=Тоифалар!$B${k}'], fill=F(c), stopIfTrue=True))
        ws.conditional_formatting.add(f'B{R0}:B{R1}', FormulaRule(formula=[f'$F{R0}=Тоифалар!$B${k}'], fill=F(c), font=Font(color='FFFFFF', bold=True), stopIfTrue=True))
    ws.conditional_formatting.add(f'E{R0}:E{R1}', DataBarRule(start_type='num', start_value=0, end_type='max', color='9CA3AF', showValue=True))
    # ---------- o'ng panel: yashirin hisob (Q..T) + suzuvchi diagrammalar ----------
    ws['J5'] = 'ВАҚТ ҚАЕРГА КЕТМОҚДА?'; ws['J5'].font = font(INK, True, 13); ws['J5'].alignment = Alignment(vertical='center')
    for c in 'QRST': ws.column_dimensions[c].hidden = True
    S0 = 6; NW = LUNCH - 1                      # ish toifalari (tushliksiz)
    for k in range(1, len(CATS) + 1):
        r = S0 + k - 1
        ws[f'Q{r}'] = f'=Тоифалар!B{k + 1}'
        ws[f'R{r}'] = f'=SUMIF($F${R0}:$F${R1},Q{r},$E${R0}:$E${R1})'
        ws[f'T{r}'] = -1 if k == LUNCH else f'=R{r}+ROW()/10000'
    QL = S0 + LUNCH - 1; QA, QB = S0, S0 + NW - 1
    tw = f'(SUM($E${R0}:$E${R1})-R{QL})'
    for k in range(NW): ws[f'S{S0 + k}'] = f'=IF({tw}=0,0,R{S0 + k}/{tw})'
    top = f'INDEX(Q{QA}:Q{QB},MATCH(MAX(T{QA}:T{QB}),T{QA}:T{QB},0))'
    topm = f'INDEX(R{QA}:R{QB},MATCH(MAX(T{QA}:T{QB}),T{QA}:T{QB},0))'
    ws['Q2'] = f'=IF(MAX(R{QA}:R{QB})<=0,"ЭНГ КЎП ВАҚТ: —","ЭНГ КЎП ВАҚТ:  "&{top}&CHAR(10)&INT({topm}/60)&" соат "&MOD({topm},60)&" дақиқа  ·  иш вақтининг "&TEXT({topm}/{tw},"0%"))'
    ws['Q3'] = f'="Жами иш вақти: "&INT({tw}/60)&" соат "&MOD({tw},60)&" дақ. (тушликсиз)"&CHAR(10)&"Йиғилишлар "&TEXT(S{S0},"0%")&"  ·  Линияда (GO&SEE) "&TEXT(S{S0 + 1},"0%")'
    # kesh (oldindan ko'rinish uchun) — Python hisobi
    mins = [0] * len(CATS)
    for i, st in enumerate(steps):
        a_ = st[0].hour * 60 + st[0].minute; b_ = st[1].hour * 60 + st[1].minute; mins[NAMUNA_CAT[i] - 1] += b_ - a_
    twv = sum(mins) - mins[LUNCH - 1]
    if twv:
        ti = max(range(NW), key=lambda k: (mins[k], -k)); tm = mins[ti]
        c2 = f'ЭНГ КЎП ВАҚТ:  {CATS[ti][0]}\n{tm // 60} соат {tm % 60} дақиқа  ·  иш вақтининг {round(tm / twv * 100)}%'
        c3 = f'Жами иш вақти: {twv // 60} соат {twv % 60} дақ. (тушликсиз)\nЙиғилишлар {round(mins[0] / twv * 100)}%  ·  Линияда (GO&SEE) {round(mins[1] / twv * 100)}%'
    else:
        c2, c3 = 'ЭНГ КЎП ВАҚТ: —', 'Жами иш вақти: 0 соат 0 дақ. (тушликсиз)\nЙиғилишлар 0%  ·  Линияда (GO&SEE) 0%'
    from openpyxl.chart import BarChart
    from openpyxl.chart.title import Title
    from openpyxl.chart.text import Text, RichText
    from openpyxl.chart.data_source import StrRef, StrData, StrVal
    from openpyxl.drawing.text import Paragraph, ParagraphProperties, CharacterProperties, Font as DFont
    from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
    from openpyxl.drawing.xdr import XDRPositiveSize2D
    from openpyxl.utils.units import cm_to_EMU, pixels_to_EMU
    sname = ws.title.replace("'", "''")
    def ttl(cell, cache, size=1300, color='1F2937'):
        sr = StrRef(f=f"'{sname}'!${cell[0]}${cell[1:]}", strCache=StrData(ptCount=1, pt=[StrVal(idx=0, v=cache)]))
        cp = CharacterProperties(sz=size, b=True, solidFill=color, latin=DFont(typeface='Segoe UI'))
        return Title(tx=Text(strRef=sr), overlay=False, txPr=RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)]))
    def anchor(chart, row, off_pt, w_cm, h_cm):
        m = AnchorMarker(col=9, colOff=0, row=row - 1, rowOff=int(off_pt * 12700))
        chart.anchor = OneCellAnchor(_from=m, ext=XDRPositiveSize2D(cm_to_EMU(w_cm), cm_to_EMU(h_cm)))
        ws.add_chart(chart)
    def row_at(pt_from_row6):  # 6-qatordan pt masofadagi qator va ofset
        acc = 0
        for r in range(6, 200):
            hh = ws.row_dimensions[r].height or 15
            if acc + hh > pt_from_row6: return r, pt_from_row6 - acc
            acc += hh
    # 1) gorizontal ustunlar — daqiqa
    bc = BarChart(); bc.type = 'bar'; bc.grouping = 'clustered'; bc.legend = None; bc.gapWidth = 45
    bc.add_data(Reference(ws, min_col=18, min_row=QA, max_row=QB), titles_from_data=False)
    bc.set_categories(Reference(ws, min_col=17, min_row=QA, max_row=QB))
    bc.title = ttl('Q2', c2); bc.visible_cells_only = False
    bc.x_axis.scaling.orientation = 'maxMin'; bc.y_axis.delete = True; bc.y_axis.majorGridlines = None
    bc.x_axis.majorTickMark = 'none'; bc.x_axis.txPr = RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=CharacterProperties(sz=900, solidFill='374151', latin=DFont(typeface='Segoe UI'))), endParaRPr=CharacterProperties(sz=900))])
    sr = bc.series[0]
    for k in range(NW):
        pt = DataPoint(idx=k); pt.graphicalProperties.solidFill = CATS[k][1]; pt.graphicalProperties.line.noFill = True; sr.dPt.append(pt)
    sr.dLbls = DataLabelList(); sr.dLbls.showVal = True; sr.dLbls.showCatName = False; sr.dLbls.showSerName = False; sr.dLbls.showPercent = False; sr.dLbls.showLegendKey = False
    sr.dLbls.numFmt = '0" дақ."'; sr.dLbls.position = 'outEnd'
    anchor(bc, 6, 4, 12.8, 9.6)
    # 2) halqa — ulush
    dc = DoughnutChart(); dc.holeSize = 55; dc.legend = None; dc.visible_cells_only = False
    dc.add_data(Reference(ws, min_col=18, min_row=QA, max_row=QB), titles_from_data=False)
    dc.set_categories(Reference(ws, min_col=17, min_row=QA, max_row=QB))
    dc.title = ttl('Q3', c3, 1050, '374151')
    ds = dc.series[0]
    for k in range(NW):
        pt = DataPoint(idx=k); pt.graphicalProperties.solidFill = CATS[k][1]; pt.graphicalProperties.line.solidFill = 'FFFFFF'; ds.dPt.append(pt)
    ds.dLbls = DataLabelList(); ds.dLbls.showPercent = True; ds.dLbls.showVal = False; ds.dLbls.showCatName = False; ds.dLbls.showSerName = False; ds.dLbls.showLegendKey = False; ds.dLbls.showLeaderLines = False
    r_, o_ = row_at(9.6 / 2.54 * 72 + 14)
    anchor(dc, r_, o_, 12.8, 8.4)
    r_, o_ = row_at((9.6 + 8.4) / 2.54 * 72 + 26)
    ws[f'J{r_ + 1}'] = 'Тоифани рўйхатдан танланг, вақтни 08:50 кўринишида ёзинг — диаграммалар ўзи янгиланади.'; ws[f'J{r_ + 1}'].font = font(SUBT, False, 8, True)
    ws.freeze_panes = f'A{H + 1}'
    ws.print_area = f'A1:M{max(R1, r_ + 1)}'
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 1; ws.sheet_properties.pageSetUpPr.fitToPage = True
    for m in ('left', 'right'): setattr(ws.page_margins, m, 0.3)

ws1 = wb.create_sheet('Намуна — Бўёқлаш', 0)
build(ws1, STEPS, TITLE.replace('Бўёқлаш цехи бошлиғи кунлик иш режим графиги', 'Бўёқлаш цехи бошлиғи'), 'Ф.И.Ш.: ______________________     ·     Сана: ____.____.2026     ·     Иш вақти: 08:50 – 18:00')
ws2 = wb.create_sheet('Бўш шаблон', 1)
build(ws2, [], 'Лавозим: ______________________', 'Ф.И.Ш.: ______________________     ·     Сана: ____.____.2026     ·     Иш вақти: ____ – ____')
wb.active = 0
wb.save(OUT)
print('ok', OUT, len(STEPS), 'qadam')
