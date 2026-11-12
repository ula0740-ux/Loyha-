# -*- coding: utf-8 -*-
"""HRM 2026 · Сентабр — 3D zavod shablonidagi HTML taqdimot.

Shablon (foydalanuvchi bergan index.html): WebGL zavod sahnasi, har slaydda
mashinaga bitta qism qo'shiladi; slaydlar ustida panel bo'lib turadi.
Bu skript shablonning CSS / WebGL / navigatsiyasini saqlab, slaydlarni
slides.html dan, diagrammalarni charts.js dan oladi. Panellar butun
balandlikni egallaydi (pastki qism bo'sh qolmaydi), sahna esa 41 bosqichini
slaydlar soniga moslab o'tadi.

    python3 hisobot/hrm/factory/build.py <shablon index.html>
"""
import base64, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'template.html')
OUT = os.path.join(HERE, 'HRM_2026_Sentabr_zavod.html')


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def one(s, a, b):
    assert s.count(a) == 1, a[:70]
    return s.replace(a, b)


t = read(TPL)

# 1) CSS
t = one(t, '</style>\n</head>', read(os.path.join(HERE, 'extra.css')) + '</style>\n</head>')
t = one(t, '<title>ADM Jizzax — HRM Ҳисоботи 2026</title>', '<title>ADM Jizzax — HRM Ҳисоботи 2026 · Сентабр</title>')

# 2) slaydlar
slides = read(os.path.join(HERE, 'slides.html'))
for name in re.findall(r'\{\{(\w+)\}\}', slides):
    data = base64.b64encode(open(os.path.join(HERE, 'img', name + '.webp'), 'rb').read()).decode()
    slides = slides.replace('{{%s}}' % name, 'data:image/webp;base64,' + data)
i = t.index('<div id="vignette" aria-hidden="true"></div>') + len('<div id="vignette" aria-hidden="true"></div>')
j = t.index('<nav id="ui"')
t = t[:i] + '\n\n' + slides + '\n' + t[j:]

# 3) diagrammalar: shablonning slaydga bog'liq chizmalari o'rniga bizniki
i = t.index('(function(){ /* contents ring */')
j = t.index('/* ================= WebGL factory scene')
t = t[:i] + read(os.path.join(HERE, 'charts.js')) + '\n' + t[j:]

# 4) sahna: 41 bosqich (0..40) slaydlar soniga cho'ziladi — mashina oxirgi slaydda to'liq yig'iladi
t = one(t, 'var N = slides.length, cur = 0, anim = null, J = 0;',
        'var N = slides.length, cur = 0, anim = null, J = 0, JK = N > 1 ? 40 / (N - 1) : 1;')
t = one(t, 'if (scene) scene.setTarget(j1);', 'if (scene) scene.setTarget(j1 * JK);')
t = one(t, 'if (scene){ scene.setJ(J); try', 'if (scene){ scene.setJ(J * JK); try')

open(OUT, 'w', encoding='utf-8').write(t)
print('OK', OUT, len(re.findall(r'<section class="slide', t)), 'slides', os.path.getsize(OUT) // 1024, 'KB')
