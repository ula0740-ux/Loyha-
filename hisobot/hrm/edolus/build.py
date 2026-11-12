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


REC_CSS = """
.slide,.slide *{transition:none!important;animation:none!important}
#ui,#bar,#picker{display:none!important}
"""
REC_JS = r"""
var recMode = false;
/* vaqt chizig'i: muqova/mundarija 6 s, bo'lim sarlavhasi 4.5 s, ma'lumot slaydi 8 s, o'tish 1.5 s, yakun 4.6 s */
var TR = 1.5, OUTRO = 4.6, HOLD = slides.map(function(s, i){ return i < 2 ? 6 : s.classList.contains("hero") ? 4.5 : 8; });
var HS = [], acc = 0; HOLD.forEach(function(h, i){ HS.push(acc); acc += h + (i < N - 1 ? TR : 0); });
var TOTAL = acc + OUTRO;
function revealEls(s){
  var out = [];
  Array.prototype.forEach.call(s.children, function(c){
    if (c.matches(".fill,.row,.col,.cover,.sec2,.toc2,.grid,[class*=g]") && c.children.length > 1 && c.children.length < 9)
      Array.prototype.forEach.call(c.children, function(d){ out.push(d); });
    else out.push(c);
  });
  return out;
}
var REV = slides.map(revealEls);
function place(i, vis, age, fade, kb){
  var s = slides[i];
  if (!vis){ s.style.visibility = "hidden"; return; }
  s.style.visibility = "visible"; s.style.opacity = fade.toFixed(3);
  s.style.transform = "translateY(" + ((1 - fade) * 10).toFixed(1) + "px) scale(" + (1 + .012 * kb).toFixed(4) + ")";
  REV[i].forEach(function(el, k){
    var e = ease(Math.max(0, Math.min(1, (age - .1 - .09 * k) / .65)));
    el.style.opacity = e.toFixed(3);
    el.style.transform = e < 1 ? "translateY(" + (26 * (1 - e)).toFixed(1) + "px)" : "";
    el.style.filter = e < 1 ? "blur(" + (6 * (1 - e)).toFixed(2) + "px)" : "";
  });
}
function seekAt(t){
  recMode = true;
  slides.forEach(function(s){ s.classList.remove("on", "fade-in", "fade-out"); s.removeAttribute("inert"); s.style.visibility = "hidden"; });
  var i = 0; while (i < N - 1 && t >= HS[i + 1]) i++;
  var hEnd = HS[i] + HOLD[i], vel = 0;
  if (t < hEnd || i === N - 1){
    J = i;
    place(i, true, t - HS[i] + (i ? TR * .18 : .3), 1, Math.min(1, (t - HS[i]) / HOLD[i]));
  } else {
    var p = (t - hEnd) / TR, e = ease(p);
    J = i + e;
    vel = Math.abs(6 * Math.min(p, 1 - p));
    if (p < .2) place(i, true, 99, 1 - p / .2, 1);
    if (p >= .82) place(i + 1, true, (p - .82) * TR, Math.min(1, (p - .82) / .18), 0);
  }
  canvas.style.filter = vel > .05 ? "blur(" + Math.min(1.8, vel * 1.2).toFixed(2) + "px)" : "none";
  stageEl.style.clipPath = ""; $("outro").hidden = true;
  stageEl.style.opacity = Math.min(1, t / .8).toFixed(3);              /* qora fondan ochilish */
  var ot = t - (HS[N - 1] + HOLD[N - 1]);
  if (ot > 0){
    var k = function(a, d){ return Math.max(0, Math.min(1, (ot - a) / d)); }, bl = ease(k(.2, .7));
    slides[N - 1].style.opacity = (1 - k(0, .3)).toFixed(3);
    canvas.style.filter = "blur(" + (14 * bl).toFixed(2) + "px) brightness(" + (1 - .12 * bl).toFixed(3) + ")";
    $("outro").hidden = false;
    $("omsg").style.opacity = ease(k(.8, .5)) * (1 - ease(k(3.1, .3)));
    var band = ease(k(2.4, .6)), close = ease(k(3.3, .45)), half = (540 - 380 * band) * (1 - close);
    stageEl.style.clipPath = "inset(" + (540 - half).toFixed(1) + "px 0 " + (540 - half).toFixed(1) + "px 0)";
  }
  if (scene){ scene.setJ(J); scene.frameT(t); }
}
window.seek = async function(t){ seekAt(t); };
window.TOTAL = TOTAL;
setTimeout(function(){ seekAt(0); window.ready = true; }, 400);
"""

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

# 6) video uchun yozish rejimi: window.seek(t) — butun taqdimot deterministik vaqt chizig'ida
REC = t
REC = one(REC, 'function step(now){', 'function step(now){ if (recMode) return;')
REC = one(REC, 'window.__deck = {', REC_JS + 'window.__deck = {')
REC = one(REC, '</style>\n</head>', REC_CSS + '</style>\n</head>')

open(OUT, 'w', encoding='utf-8').write(t)
open(OUT.replace('.html', '_rec.html'), 'w', encoding='utf-8').write(REC)
print('OK', OUT, len(re.findall(r'<section class="slide', t)), 'slides', os.path.getsize(OUT) // 1024, 'KB')
