# SPQRC ma'lumotlari: umumiy o'zgarmaslar va ikki manba.
#   load_dashboard(xlsx) - zavodning SPQRC_dashboard_*.xlsx fayli (kunlik '+' belgilari)
#   load_input(xlsx)     - bizning SPQRC_belgilash.xlsx (haftalik ✓/✗ belgilash fayli)
# Ikkalasi ham bir xil natija qaytaradi: dict(year, month, items, na)
#   items[(s, d)] = [(ko'rsatkich nomi, [w1..w5 belgilari])], belgilar: '✓' | '✗' | '' | '—' (oyda yo'q hafta)
#   na[s] = [(yo'nalish kodi, ko'rsatkich nomi)]  - shu sex jadvalida yo'q ko'rsatkichlar
import calendar, datetime, openpyxl

OK, NO, OFF = '✓', '✗', '—'
DIRS = [('SAFETY', 'Хавфсизлик', 'Душанба', 'Ду'), ('PEOPLE', 'Ходимлар', 'Сешанба', 'Се'), ('QUALITY', 'Сифат', 'Чоршанба', 'Чо'),
        ('RESPONSIVENESS', 'Тезкорлик', 'Пайшанба', 'Па'), ('COST', 'Харажат', 'Жума', 'Жу')]
DAYN = {d[0]: i for i, d in enumerate(DIRS)}
SHOPS = [('Body Shop', 'Пайвандлаш цехи', 'Body'), ('Paint Shop', 'Бўёқлаш цехи', 'Paint'), ('GA Shop', 'Йиғув цехи', 'GA'), ('SKD', 'SKD цехи', 'SKD')]
MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']


def weeks(year, month, d):  # d: 0=Du..4=Ju -> oyning shu kunlari
    return [datetime.date(year, month, x) for x in range(1, calendar.monthrange(year, month)[1] + 1) if calendar.weekday(year, month, x) == d]


def norm(v):
    t = str(v or '').strip()
    if t in ('+', '✓', '✔', 'v', 'V'): return OK
    if t in ('-', '−', '–', 'x', 'X', 'х', 'Х', '✗', '✘'): return NO
    return ''


def load_dashboard(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    dash = list(wb['Dashboard'].iter_rows(values_only=True))
    rep = next(next(v for v in r if isinstance(v, datetime.datetime)) for r in dash if r[1] and 'Ҳисобот санаси' in str(r[1])).date()
    na = {}
    h0 = next(i for i, r in enumerate(dash) if r[1] == 'Йўналиш' and r[2] == 'Кўрсаткич')
    for r in dash[h0 + 1:]:
        if r[1] not in DAYN: break
        for k, v in enumerate(r[6:10]):
            if v == 'н/а': na.setdefault(k + 1, []).append((r[1], r[2]))
    items, year, month = {}, None, None
    for si, (sheet, *_) in enumerate(SHOPS, 1):
        rows = list(wb[sheet].iter_rows(values_only=True))
        dates = [x.date() if isinstance(x, datetime.datetime) else None for x in next(r for r in rows if isinstance(r[4], datetime.datetime))[4:34]]
        year, month = dates[0].year, dates[0].month
        cur = None
        for r in rows:
            if r[2] and str(r[2]).split('\n')[0] in DAYN: cur = str(r[2]).split('\n')[0]
            if cur and r[3] and isinstance(r[37], (int, float)) and r[3] != 'Кунлик бажарилган (+) сони':
                plus = {dates[i] for i, v in enumerate(r[4:34]) if v == '+'}
                wk = weeks(year, month, DAYN[cur])
                marks = [(OK if dt in plus else (NO if dt <= rep else '')) for dt in wk] + [OFF] * (5 - len(wk))
                assert marks.count(OK) == r[36] and sum(1 for v in marks if v in (OK, NO)) == r[37], (sheet, r[3])
                items.setdefault((si, DAYN[cur] + 1), []).append((r[3], marks))
    return dict(year=year, month=month, items=items, na=na, rep=rep)


def load_input(path):
    """SPQRC_belgilash.xlsx: A ustunidagi yashirin kalitlar bo'yicha o'qiydi (R|d / NA|d)."""
    wb = openpyxl.load_workbook(path)
    top = wb['Барча цехлар']
    year, month = int(top['C4'].value), int(top['E4'].value)
    items, na = {}, {}
    for si, (_, nm, short) in enumerate(SHOPS, 1):
        ws = wb[short]
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
            key = str(row[0].value or '')
            if key.startswith('R|'):
                d = int(key.split('|')[1]); wk = weeks(year, month, d - 1)
                marks = [norm(row[2 + w].value) if w < len(wk) else OFF for w in range(5)]
                items.setdefault((si, d), []).append((str(row[1].value), marks))
            elif key.startswith('NA|'):
                d = int(key.split('|')[1]); na.setdefault(si, []).append((DIRS[d - 1][0], str(row[1].value)))
    return dict(year=year, month=month, items=items, na=na, rep=None)
