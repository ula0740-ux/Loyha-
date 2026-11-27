# SPQRC_belgilash.xlsx - haftalik belgilash fayli (telefonda ham ishlaydi, makrossiz).
#   python3 make_xlsx.py [manba.xlsx]   -> zavod dashboard faylidan oldindan to'ldiradi (standart: kirish/SPQRC_dashboard_November_2026.xlsx)
#   python3 make_xlsx.py --bosh 2026 12 -> bo'sh shablon
# Foizlar Excel formulalari bilan hisoblanadi; A ustunida yashirin kalitlar (R|d, NA|d, H|d, T|d) - build_tpl.py shu bo'yicha o'qiydi.
import sys, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule, DataBarRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as L
from spqrc_data import DIRS, SHOPS, OK, NO, OFF, load_dashboard

if len(sys.argv) > 1 and sys.argv[1] == '--bosh':
    data = dict(year=int(sys.argv[2]), month=int(sys.argv[3]), items=None, na=None)
    src = load_dashboard('kirish/SPQRC_dashboard_November_2026.xlsx')  # ko'rsatkichlar ro'yxati uchun
    data['items'] = {k: [(n, [''] * 5) for n, _ in v] for k, v in src['items'].items()}; data['na'] = src['na']
else:
    data = load_dashboard(sys.argv[1] if len(sys.argv) > 1 else 'kirish/SPQRC_dashboard_November_2026.xlsx')
OUT = 'SPQRC_belgilash.xlsx'

BG, CARD, HEAD, CELL, OFFC = '23272D', '2F343B', '363C44', '3A4048', '2A2E34'
TEAL, LTEAL, CORAL, AMBER, TXT, MUTED, DIM = '3CC6B8', '7FD9CF', 'E8826E', 'E8B86E', 'EDEBEB', '9AA2AC', '6B737D'
F = lambda c: PatternFill('solid', fgColor=c)
def font(c=TXT, b=False, s=10): return Font(name='Segoe UI', color=c, bold=b, size=s)
CEN = Alignment(horizontal='center', vertical='center'); LEFT = Alignment(horizontal='left', vertical='center', indent=1)
thin = Side(style='thin', color=BG); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
MARK_OK = '((C{r}:G{r}="✓")+(C{r}:G{r}="+"))'
MARK_NO = '((C{r}:G{r}="✗")+(C{r}:G{r}="-")+(C{r}:G{r}="x")+(C{r}:G{r}="х"))'

wb = openpyxl.Workbook()
top = wb.active; top.title = 'Барча цехлар'

def paint(ws, rows, cols):
    ws.sheet_view.showGridLines = False
    for r in range(1, rows + 1):
        for c in range(1, cols + 1): ws.cell(r, c).fill = F(BG)

# ---------- har sex varag'i ----------
TOT = {}  # (s, d) -> jami qatori ; (s, 0) -> sex jami
for s, (_, name, short) in enumerate(SHOPS, 1):
    ws = wb.create_sheet(short)
    nrows = 8 + sum(len(data['items'][(s, d)]) + len([1 for c, _ in data['na'].get(s, []) if c == DIRS[d - 1][0]]) + 4 for d in range(1, 6))
    paint(ws, nrows + 5, 13)
    for col, w in zip('ABCDEFGHIJKLM', [2, 38, 9, 9, 9, 9, 9, 7, 7, 7, 12, 12, 2]): ws.column_dimensions[col].width = w
    ws.column_dimensions['A'].hidden = True
    ws['B1'] = f'{name} ({short}) — SPQRC ҳафталик белгилаш'; ws['B1'].font = font(TXT, True, 15)
    ws['B2'] = 'Катакка ✓ (бажарилди) ёки ✗ (бажарилмади) танланг — фоизлар ўзи ҳисобланади. «—» = шу ойда йўқ ҳафта.'; ws['B2'].font = font(MUTED, s=9)
    # KPI qatori (4-5)
    kp = [('B', 'Ойлик бажарилиш (✓ / режа)'), ('C', '✓ бажарилди'), ('E', '✗ бажарилмади'), ('G', 'Режа'), ('I', '✓ / (✓+✗)')]
    r = 8; blocks = []
    dv = DataValidation(type='list', formula1=f'"{OK},{NO}"', allow_blank=True, showErrorMessage=False); ws.add_data_validation(dv)
    for d, (code, uz, wd, _) in enumerate(DIRS, 1):
        its = data['items'][(s, d)]
        # sarlavha: yo'nalish + hafta raqamlari
        ws.cell(r, 2, f'{code} — {uz} · {wd}').font = font(TEAL, True, 11)
        for w in range(5): ws.cell(r, 3 + w, f'{w + 1}-ҳафта').font = font(DIM, s=8)
        for c, t in zip(range(8, 13), ['✓', '✗', 'Режа', 'Ойлик %', '✓/(✓+✗)']): ws.cell(r, c, t).font = font(DIM, True, 8)
        for c in range(2, 13): ws.cell(r, c).fill = F(CARD); ws.cell(r, c).alignment = CEN if c > 2 else LEFT
        # sanalar qatori
        h = r + 1; ws.cell(h, 1, f'H|{d}'); ws.cell(h, 2, 'Кўрсаткич  /  сана').font = font(DIM, s=8)
        for w in range(5):
            x = f'(OY+MOD({d}-WEEKDAY(OY,2),7)+{7 * w})'
            c = ws.cell(h, 3 + w, f'=IF(MONTH({x})=MONTH(OY),{x},"{OFF}")'); c.number_format = 'dd.mm'; c.font = font(MUTED, True, 9); c.alignment = CEN
        for c in range(2, 13): ws.cell(h, c).fill = F(CARD)
        ws.cell(h, 2).alignment = LEFT
        r = h + 1; first = r
        for nm, marks in its:
            ws.cell(r, 1, f'R|{d}'); ws.cell(r, 2, nm).font = font(TXT, s=10); ws.cell(r, 2).alignment = LEFT; ws.cell(r, 2).fill = F(CARD)
            for w in range(5):
                c = ws.cell(r, 3 + w, marks[w] if marks[w] in (OK, NO) else None); c.fill = F(CELL); c.font = font(MUTED, True, 12); c.alignment = CEN; c.border = BOX
            dv.add(f'C{r}:G{r}')
            hr = f'$C${h}:$G${h}'
            ws.cell(r, 8, f'=SUMPRODUCT({MARK_OK.format(r=r)}*ISNUMBER({hr}))')
            ws.cell(r, 9, f'=SUMPRODUCT({MARK_NO.format(r=r)}*ISNUMBER({hr}))')
            ws.cell(r, 10, f'=SUMPRODUCT(--ISNUMBER({hr}))')
            ws.cell(r, 11, f'=IF(J{r}=0,"",H{r}/J{r})'); ws.cell(r, 12, f'=IF(H{r}+I{r}=0,"{OFF}",H{r}/(H{r}+I{r}))')
            for c, col in zip(range(8, 13), [TEAL, CORAL, MUTED, TXT, TXT]):
                x = ws.cell(r, c); x.font = font(col, c in (8, 9, 11), 10); x.alignment = CEN; x.fill = F(CARD)
                if c >= 11: x.number_format = '0.0%'
            r += 1
        last = r - 1
        for c2, nm in [x for x in data['na'].get(s, []) if x[0] == code]:
            ws.cell(r, 1, f'NA|{d}'); ws.cell(r, 2, nm).font = font(DIM, s=10); ws.cell(r, 2).alignment = LEFT
            ws.cell(r, 3, 'н/а — ушбу цех жадвалида йўқ').font = font(DIM, s=8)
            for c in range(2, 13): ws.cell(r, c).fill = F(CARD)
            r += 1
        # jami
        ws.cell(r, 1, f'T|{d}'); ws.cell(r, 2, f'Жами {code}').font = font(TEAL, True, 10); ws.cell(r, 2).alignment = LEFT
        for c, col in zip(range(8, 11), 'HIJ'): ws.cell(r, c, f'=SUM({col}{first}:{col}{last})')
        ws.cell(r, 11, f'=IF(J{r}=0,"",H{r}/J{r})'); ws.cell(r, 12, f'=IF(H{r}+I{r}=0,"{OFF}",H{r}/(H{r}+I{r}))')
        for c in range(2, 13):
            x = ws.cell(r, c); x.fill = F(HEAD)
            if c >= 8: x.font = font([TEAL, CORAL, MUTED, TXT, TXT][c - 8], True, 10); x.alignment = CEN
            if c >= 11: x.number_format = '0.0%'
        TOT[(s, d)] = r; blocks.append((first, last, h))
        r += 2
    # shartli formatlash: belgilar va yo'q haftalar
    for first, last, h in blocks:
        rng = f'C{first}:G{last}'
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'NOT(ISNUMBER(C${h}))'], fill=F(OFFC), font=Font(color=DIM), stopIfTrue=True))
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR(C{first}="✓",C{first}="+")'], fill=F('24524D'), font=Font(color=TEAL, bold=True)))
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'OR(C{first}="✗",C{first}="-",C{first}="x")'], fill=F('5A3530'), font=Font(color=CORAL, bold=True)))
        ws.conditional_formatting.add(f'K{first}:K{last}', DataBarRule(start_type='num', start_value=0, end_type='num', end_value=1, color=TEAL, showValue=True))
    # sex KPI (4-5 qator)
    rows = [TOT[(s, d)] for d in range(1, 6)]
    sm = lambda col: '+'.join(f'{col}{x}' for x in rows)
    vals = [f'=IF(({sm("J")})=0,"",({sm("H")})/({sm("J")}))', f'={sm("H")}', f'={sm("I")}', f'={sm("J")}', f'=IF(({sm("H")})+({sm("I")})=0,"{OFF}",({sm("H")})/(({sm("H")})+({sm("I")})))']
    for (col, lab), v, ac in zip(kp, vals, [TEAL, TEAL, CORAL, MUTED, TEAL]):
        a = ws[f'{col}4']; a.value = lab; a.font = font(MUTED, s=8)
        b = ws[f'{col}5']; b.value = v; b.font = font(ac, True, 18)
        if col in 'BI': b.number_format = '0.0%'
    for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
        for rr in (4, 5): ws[f'{col}{rr}'].fill = F(CARD)
    ws.merge_cells('C4:D4'); ws.merge_cells('C5:D5'); ws.merge_cells('E4:F4'); ws.merge_cells('E5:F5'); ws.merge_cells('G4:H4'); ws.merge_cells('G5:H5'); ws.merge_cells('I4:L4'); ws.merge_cells('I5:L5')
    for rr in (4, 5):
        for col in 'BCEGI': ws[f'{col}{rr}'].alignment = LEFT
    ws.row_dimensions[5].height = 30
    ws.freeze_panes = 'C8'
    TOT[(s, 0)] = rows

# ---------- umumiy varaq ----------
paint(top, 32, 10)
for col, w in zip('ABCDEFGHIJ', [2, 24, 14, 14, 14, 16, 14, 14, 2, 2]): top.column_dimensions[col].width = w
top['B1'] = 'SPQRC маълумотлари — ҳафталик белгилаш'; top['B1'].font = font(TXT, True, 16)
top['B2'] = 'Белгилаш ҳар бир цех варағида (Body, Paint, GA, SKD). Бу ердаги фоизлар ўзи ҳисобланади.'; top['B2'].font = font(MUTED, s=9)
top['B4'] = 'Йил:'; top['C4'] = data['year']; top['D4'] = 'Ой (1–12):'; top['E4'] = data['month']; top['F4'] = 'Ой боши:'; top['G4'] = '=DATE(C4,E4,1)'
top['G4'].number_format = 'mm.yyyy'
for c in ('B4', 'D4', 'F4'): top[c].font = font(MUTED, s=9); top[c].alignment = Alignment(horizontal='right', vertical='center')
for c in ('C4', 'E4'): top[c].font = font(AMBER, True, 13); top[c].fill = F(CELL); top[c].alignment = CEN; top[c].border = BOX
top['G4'].font = font(TXT, True, 11); top['G4'].alignment = CEN
wb.defined_names['OY'] = DefinedName('OY', attr_text="'Барча цехлар'!$G$4")
def matrix(r0, title, num, den, colored):
    top.cell(r0, 2, title).font = font(TEAL, True, 10)
    for j, t in enumerate(['Цех'] + [d[0] for d in DIRS] + ['ЖАМИ']):
        c = top.cell(r0 + 1, 2 + j, t); c.font = font(DIM, True, 8); c.fill = F(CARD); c.alignment = CEN if j else LEFT
    for s, (_, name, short) in enumerate(SHOPS, 1):
        r = r0 + 1 + s; q = lambda col, t: f"'{short}'!{col}{t}"
        c = top.cell(r, 2, name); c.font = font(TXT, True, 10); c.fill = F(CARD); c.alignment = LEFT
        for d in range(1, 7):
            ts = [TOT[(s, d)]] if d < 6 else TOT[(s, 0)]
            n = '+'.join(num(q, t) for t in ts); m = '+'.join(den(q, t) for t in ts)
            x = top.cell(r, 2 + d, f'=IF(({m})=0,"{OFF}",({n})/({m}))')
            x.number_format = '0.0%'; x.alignment = CEN; x.border = BOX
            x.font = font('1F2328' if colored else TXT, True, 11); x.fill = F(HEAD)
    rng = f'C{r0 + 2}:H{r0 + 5}'; a = f'C{r0 + 2}'
    if colored:
        for f_, col in [(f'{a}>=0.999', TEAL), (f'{a}>=0.75', LTEAL), (f'{a}>=0.5', AMBER), (f'{a}<0.5', CORAL)]:
            top.conditional_formatting.add(rng, FormulaRule(formula=[f'AND(ISNUMBER({a}),{f_})'], fill=F(col), stopIfTrue=True))
        top.conditional_formatting.add(rng, FormulaRule(formula=[f'NOT(ISNUMBER({a}))'], font=Font(color=DIM)))
    else:
        top.conditional_formatting.add(rng, DataBarRule(start_type='num', start_value=0, end_type='num', end_value=1, color=TEAL, showValue=True))
matrix(6, 'Ойлик бажарилиш (✓ / ойлик режа) — ой давомида ошиб боради', lambda q, t: q('H', t), lambda q, t: q('J', t), False)
matrix(13, 'Белгиланган ҳафталар бўйича (✓ / (✓+✗)) — ранг: 100% · 75–99% · 50–74% · 50% дан паст', lambda q, t: q('H', t), lambda q, t: f"{q('H', t)}+{q('I', t)}", True)
notes = ['Қандай ишлатилади:', '1) Цех варағида (пастдаги ёрлиқлар) ҳафта катагига ✓ ёки ✗ танланг (ёки + / − ёзинг).',
         '2) Ҳар бир йўналиш ўз куни бўйича: Ду–SAFETY, Се–PEOPLE, Чо–QUALITY, Па–RESPONSIVENESS, Жу–COST.',
         '3) «—» — шу ойда йўқ ҳафта, режага кирмайди.',
         '4) Янги ой: юқоридаги Йил ва Ой катакларини ўзгартиринг — саналар ўзи янгиланади; эски белгиларни ўчиринг.',
         '5) PowerPoint слайдлар шу файлдан олинади (SPQRC_haftalik_shablon.pptx).']
for i, t in enumerate(notes):
    c = top.cell(21 + i, 2, t); c.font = font(TEAL if i == 0 else MUTED, i == 0, 10 if i == 0 else 9)
wb.save(OUT)
print('ok', OUT, data['year'], data['month'])
