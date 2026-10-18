# -*- coding: utf-8 -*-
"""HRM 2026 · Сентабр — EDOLUS reel uslubidagi HTML taqdimot.

Kontent (32 slayd, tartibi o'zgarmaydi) va diagrammalar zavod variantidan olinadi
(../factory: slides.html, charts.js, extra.css, img/). Navigatsiya shablonniki.
WebGL zavod sahnasi o'rniga scene.js: reel'dagi sayt sahnalari — orbita, sun'iy
yo'ldosh, oltin tuman, hisoblash koridori, energiya portlashi, nur lentasi va
oxirida yo'ldagi mashina (Kia Sonet). Oxirgi slayddan keyin "keyingi" — yakun:
xiralashuv, xabar, tasma, qora ekran.

    python3 hisobot/hrm/edolus/build.py
"""
import base64, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FAC = os.path.join(HERE, '..', 'factory')
ROOT = os.path.join(HERE, '..', '..', '..')
OUT = os.path.join(HERE, 'HRM_2026_Sentabr_EDOLUS.html')


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def one(s, a, b):
    assert s.count(a) == 1, a[:70]
    return s.replace(a, b)


def b64(p, mime):
    return 'data:%s;base64,%s' % (mime, base64.b64encode(open(p, 'rb').read()).decode())


t = read(os.path.join(FAC, 'template.html'))

# 1) CSS
t = one(t, '</style>\n</head>', read(os.path.join(FAC, 'extra.css')) + read(os.path.join(HERE, 'edolus.css')) + '</style>\n</head>')
t = one(t, '<title>ADM Jizzax — HRM Ҳисоботи 2026</title>', '<title>ADM Jizzax — HRM Ҳисоботи 2026 · Сентабр</title>')

# 2) slaydlar (zavod variantidagi bilan bir xil)
slides = read(os.path.join(FAC, 'slides.html'))
for name in re.findall(r'\{\{(\w+)\}\}', slides):
    slides = slides.replace('{{%s}}' % name, b64(os.path.join(FAC, 'img', name + '.webp'), 'image/webp'))
i = t.index('<div id="vignette" aria-hidden="true"></div>') + len('<div id="vignette" aria-hidden="true"></div>')
j = t.index('<nav id="ui"')
t = t[:i] + '\n\n' + slides + '\n<div id="outro" hidden><div id="omsg">Эътиборингиз учун <b>раҳмат</b></div></div>\n' + t[j:]

# 3) diagrammalar
i = t.index('(function(){ /* contents ring */')
j = t.index('/* ================= WebGL factory scene')
t = t[:i] + read(os.path.join(FAC, 'charts.js')) + '\n' + t[j:]

# 4) sahna: WebGL zavod o'rniga EDOLUS sahnalari
car = b64(os.path.join(ROOT, 'video', 'kia-sonet', 'assets', 'sonet_cut.webp'), 'image/webp')
i = t.index('/* ================= WebGL factory scene')
j = t.index('/* ================= stage scaling')
t = t[:i] + read(os.path.join(HERE, 'scene.js')) + '''
var canvas = $("gl"), scene = null;
try { scene = makeEdolus(canvas, Array.prototype.slice.call(document.querySelectorAll(".slide")), "%s"); } catch(e){ console.error(e); scene = null; }
if (!scene){ $("fallback").style.display = "block"; canvas.style.display = "none"; }

''' % car + t[j:]

# 5) yakun (outro): oxirgi slayddan keyin "keyingi"
t = one(t, 'function go(dir){ goTo(cur + dir); }',
        'function go(dir){ if (dir > 0 && cur === N - 1 && !anim){ outro(); return; } goTo(cur + dir); }')
t = one(t, '$("next").disabled = i === N - 1;', '$("next").disabled = false;')
t = one(t, 'fit();\nif (scene){ scene.snap(0); scene.setTarget(0); }', '''var outroOn = false, oT0 = 0;
function outro(){
  if (outroOn || anim) return; outroOn = true; oT0 = performance.now();
  slides[cur].classList.remove("on"); slides[cur].classList.add("fade-out");
  $("outro").hidden = false; requestAnimationFrame(otick);
}
function otick(now){
  if (!outroOn) return;
  var t = (now - oT0) / 1000, k = function(a, d){ return Math.max(0, Math.min(1, (t - a) / d)); };
  var bl = ease(k(.2, .7));
  canvas.style.filter = "blur(" + (14 * bl).toFixed(2) + "px) brightness(" + (1 - .12 * bl).toFixed(3) + ")";
  $("omsg").style.opacity = ease(k(.8, .5)) * (1 - ease(k(3.1, .3)));
  var band = ease(k(2.4, .6)), close = ease(k(3.3, .45)), half = (540 - 380 * band) * (1 - close);
  stageEl.style.clipPath = "inset(" + (540 - half).toFixed(1) + "px 0 " + (540 - half).toFixed(1) + "px 0)";
  if (t < 4) requestAnimationFrame(otick);
}
function outroOff(){
  if (!outroOn) return; outroOn = false;
  canvas.style.filter = "none"; stageEl.style.clipPath = ""; $("outro").hidden = true; $("omsg").style.opacity = 0;
  slides[cur].classList.remove("fade-out"); show(cur);
}
document.addEventListener("keydown", function(e){ if (outroOn && e.key !== "f" && e.key !== "F"){ outroOff(); e.stopImmediatePropagation(); e.preventDefault(); } }, true);
document.addEventListener("click", function(e){ if (outroOn){ outroOff(); e.stopPropagation(); } }, true);
window.__deck = {goTo: function(k){ goTo(k); }, snap: function(k){ cur = Math.floor(k); J = k; if (scene) scene.snap(k); show(k % 1 ? -1 : k); }, outro: function(){ outro(); }};

fit();
if (scene){ scene.snap(0); scene.setTarget(0); }''')

open(OUT, 'w', encoding='utf-8').write(t)
print('OK', OUT, len(re.findall(r'<section class="slide', t)), 'slides', os.path.getsize(OUT) // 1024, 'KB')
