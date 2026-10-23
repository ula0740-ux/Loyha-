/* cinefx.js — kino effektlari kutubxonasi seek(t) dvigateli uchun.
 * Hamma narsa faqat vaqtdan (t, soniya) hisoblanadi: taymer, CSS transition, holat yo'q.
 * Bir xil t → bir xil kadr (render deterministik). Ishlatish:
 *   <script src="cinefx.js"></script>
 *   const fx = CineFX.mount(document.getElementById('stage'), {w:1080, h:1920, seed:7});
 *   window.seek = async t => { ...sahna...; fx.frame(t, {grain:.08, leak:.5, ...}); };
 */
(function (G) {
  'use strict';
  /* ---------- matematika ---------- */
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const prog = (t, t0, d) => clamp((t - t0) / d);
  const E = {
    lin: k => k,
    out: k => 1 - Math.pow(1 - k, 3),
    in: k => k * k * k,
    io: k => (k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
    expo: k => (k === 1 ? 1 : 1 - Math.pow(2, -10 * k)),
    expoIn: k => (k === 0 ? 0 : Math.pow(2, 10 * k - 10)),
    o5: k => 1 - Math.pow(1 - k, 5),
    back: k => { const c = 1.70158; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); },
  };
  /* yopiq ko'rinishdagi prujina: 0→1, tau = boshlanish, f = chastota (Hz), z = so'nish (0.2 sakraydi, 1 silliq) */
  function spring(t, t0, f = 2.2, z = .45) {
    const x = t - t0; if (x <= 0) return 0;
    const w = 2 * Math.PI * f;
    if (z >= 1) return 1 - Math.exp(-w * x) * (1 + w * x);
    const wd = w * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w * x) * (Math.cos(wd * x) + (z * w / wd) * Math.sin(wd * x));
  }
  /* deterministik shovqin */
  function hash(n) { n = (n << 13) ^ n; return 1 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824; }
  function noise1(x, seed = 0) { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hash(i + seed * 1013), hash(i + 1 + seed * 1013), u); }
  /* kalitlar bo'yicha interpolyatsiya: keys = [[t, v], ...], ease bilan */
  function keys(t, ks, ease = E.io) {
    if (t <= ks[0][0]) return ks[0][1];
    for (let i = 1; i < ks.length; i++) if (t <= ks[i][0]) {
      const k = ease((t - ks[i - 1][0]) / (ks[i][0] - ks[i - 1][0]));
      const a = ks[i - 1][1], b = ks[i][1];
      return Array.isArray(a) ? a.map((v, j) => lerp(v, b[j], k)) : lerp(a, b, k);
    }
    return ks[ks.length - 1][1];
  }
  /* kamera zoomini log fazoda (ko'z uchun tekis) */
  const zoomKeys = (t, ks, ease = E.io) => Math.exp(keys(t, ks.map(([a, z]) => [a, Math.log(z)]), ease));

  /* ---------- kamera ---------- */
  /* qo'lda ushlangan kamera tebranishi: amp px, freq Hz; rot gradusda */
  function shake(t, amp = 6, freq = .9, seed = 1) {
    return { x: amp * noise1(t * freq, seed), y: amp * noise1(t * freq, seed + 7), r: amp * .06 * noise1(t * freq * .7, seed + 13) };
  }
  /* zarba (impact) tebranishi: t0 da kuchli, tez so'nadi */
  function punch(t, t0, amp = 22, decay = 9, freq = 18) {
    const x = t - t0; if (x < 0 || x > 1.2) return { x: 0, y: 0, s: 1 };
    const e = Math.exp(-decay * x);
    return { x: amp * e * Math.sin(2 * Math.PI * freq * x), y: amp * .6 * e * Math.cos(2 * Math.PI * freq * .8 * x), s: 1 + .035 * e };
  }

  /* ---------- o'tishlar ---------- */
  /* whip-pan: t0 markazli, d davomiylik. {k: 0→1 (yangi sahna ulushi), x: siljish (ekran eniga nisbatan), blur px} */
  function whip(t, t0, d = .36, dir = 1) {
    const k = prog(t, t0 - d / 2, d), e = E.io(k);
    const v = Math.sin(Math.PI * k);               /* tezlik profili */
    return { k: e, cut: k >= .5, x: dir * (k < .5 ? -e : 1 - e), blur: 60 * v, active: k > 0 && k < 1 };
  }
  /* oq/rangli chaqnash: t0 da 1, keyin exp so'nish */
  const flash = (t, t0, d = .25) => (t < t0 || t > t0 + d * 4 ? 0 : Math.exp(-(t - t0) / d * 2.2) * (t >= t0 ? 1 : 0));
  /* iris / doira ochilishi: radius 0→1 (ekranning eng uzoq burchagigacha) */
  const iris = (t, t0, d = .5) => E.o5(prog(t, t0, d));

  /* ---------- kinetik matn ---------- */
  /* el ichidagi matnni so'zlarga bo'ladi (bir marta), keyin rise(t) bilan har kadrda joylaydi */
  function splitWords(el) {
    if (el._words) return el._words;
    const words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map(w => '<span class="cfx-m"><span class="cfx-w">' + w + '</span></span>').join(' ');
    el._words = Array.from(el.querySelectorAll('.cfx-w'));
    return el._words;
  }
  function splitChars(el) {
    if (el._chars) return el._chars;
    const s = el.textContent; el.innerHTML = '';
    el._chars = Array.from(s).map(c => { const sp = document.createElement('span'); sp.className = 'cfx-c'; sp.textContent = c === ' ' ? ' ' : c; el.appendChild(sp); return sp; });
    return el._chars;
  }
  /* maskadan ko'tarilish: har so'z stagger bilan; out berilsa chiqib ketadi */
  function rise(el, t, t0, { stagger = .055, d = .55, rot = 6, outAt = null, outD = .35 } = {}) {
    const ws = splitWords(el);
    ws.forEach((w, i) => {
      let k = E.o5(prog(t, t0 + i * stagger, d));
      let y = (1 - k) * 110, r = (1 - k) * rot;
      if (outAt !== null) { const o = E.in(prog(t, outAt + i * stagger * .5, outD)); y -= o * 110; r -= o * rot; }
      w.style.transform = 'translateY(' + y.toFixed(2) + '%) rotate(' + r.toFixed(2) + 'deg)';
    });
  }
  /* harfma-harf "scramble" / dekoder effekti */
  function decode(el, t, t0, text, { cps = 28, glyphs = '01#%&*+=<>/' } = {}) {
    const n = Math.floor((t - t0) * cps); let s = '';
    for (let i = 0; i < text.length; i++) {
      if (text[i] === ' ') { s += ' '; continue; }
      s += i < n - 3 ? text[i] : i < n ? glyphs[Math.abs(hash(i * 31 + Math.floor(t * 30))) * glyphs.length | 0] : '';
    }
    el.textContent = t < t0 ? '' : s;
  }
  /* raqam sanagich: 0 → v, format bilan (bo'shliq bilan minglik) */
  function counter(t, t0, d, v, dec = 0) {
    const x = v * E.expo(prog(t, t0, d));
    const s = x.toFixed(dec).split('.');
    s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    return s.join(',');
  }

  /* ---------- post-effektlar qatlami ---------- */
  const CSS = `
  .cfx-m{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .02em .08em}
  .cfx-w,.cfx-c{display:inline-block;will-change:transform}
  .cfx-layer{position:absolute;inset:0;pointer-events:none}
  .cfx-grade{mix-blend-mode:soft-light}
  .cfx-leak{mix-blend-mode:screen}
  .cfx-flare{mix-blend-mode:screen}
  .cfx-vig{background:radial-gradient(120% 85% at 50% 50%,transparent 55%,rgba(0,0,0,.55) 100%)}
  .cfx-bar{position:absolute;left:0;right:0;background:#000}
  .cfx-flash{background:#fff}
  .cfx-grain{mix-blend-mode:overlay;opacity:.5;image-rendering:pixelated}
  `;
  function mount(stage, { w = 1080, h = 1920, seed = 7, z = 900 } = {}) {
    if (!document.getElementById('cfx-css')) { const st = document.createElement('style'); st.id = 'cfx-css'; st.textContent = CSS; document.head.appendChild(st); }
    const mk = (cls, zz) => { const d = document.createElement('div'); d.className = 'cfx-layer ' + cls; d.style.zIndex = zz; stage.appendChild(d); return d; };
    const grade = mk('cfx-grade', z), leak = mk('cfx-leak', z + 1), flare = mk('cfx-flare', z + 2), vig = mk('cfx-vig', z + 3);
    const flashL = mk('cfx-flash', z + 6);
    const barT = document.createElement('div'), barB = document.createElement('div');
    [barT, barB].forEach(b => { b.className = 'cfx-bar'; b.style.zIndex = z + 5; stage.appendChild(b); });
    barT.style.top = 0; barB.style.bottom = 0;
    /* donadorlik: kichik kanvas, har kadrda deterministik shovqin, kattalashtirilib cho'ziladi */
    const gc = document.createElement('canvas'); gc.width = Math.round(w / 3); gc.height = Math.round(h / 3);
    gc.className = 'cfx-layer cfx-grain'; gc.style.zIndex = z + 4; gc.style.width = '100%'; gc.style.height = '100%'; stage.appendChild(gc);
    const gx = gc.getContext('2d'), img = gx.createImageData(gc.width, gc.height);
    function grain(t, amt) {
      gc.style.opacity = amt > 0 ? 1 : 0; if (amt <= 0) return;
      const f = Math.floor(t * 24), d = img.data; let s = (f * 9301 + seed * 49297) | 0;
      for (let i = 0; i < d.length; i += 4) { s = (s * 1103515245 + 12345) | 0; const v = 128 + ((s >>> 16) & 255) * amt - 128 * amt; d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255; }
      gx.putImageData(img, 0, 0);
    }
    /* frame(t, o): har kadr chaqiriladi. o — effekt kuchlari (0 = o'chiq):
       grain, vignette (0..1), letterbox (0..1 → 2.39:1 gacha), leak (0..1), leakHue, flare {x,y,a},
       flash (0..1), grade ('teal'|'warm'|'cold'|'mono'|null), gradeAmt */
    function frame(t, o = {}) {
      grain(t, o.grain ?? .06);
      vig.style.opacity = o.vignette ?? .8;
      const lb = clamp(o.letterbox ?? 0), bar = lb * (h - w / 2.39) / 2;
      barT.style.height = barB.style.height = bar.toFixed(1) + 'px';
      /* light leak: ikki yumshoq dog' sekin suzadi */
      const la = o.leak ?? 0;
      if (la > 0) {
        const hue = o.leakHue ?? 28, x1 = 20 + 30 * noise1(t * .25, seed), y1 = 15 + 25 * noise1(t * .2, seed + 3), x2 = 80 + 15 * noise1(t * .3, seed + 5);
        leak.style.background = 'radial-gradient(45% 35% at ' + x1 + '% ' + y1 + '%,hsla(' + hue + ',100%,62%,' + (.55 * la) + '),transparent 70%),' +
          'radial-gradient(40% 30% at ' + x2 + '% 85%,hsla(' + (hue + 320) % 360 + ',100%,60%,' + (.35 * la) + '),transparent 70%)';
        leak.style.opacity = 1;
      } else leak.style.opacity = 0;
      /* anamorf flare: gorizontal ko'k chiziq + yadro */
      const fl = o.flare;
      if (fl && fl.a > 0) {
        flare.style.background = 'radial-gradient(6% 3.2% at ' + fl.x + '% ' + fl.y + '%,rgba(255,255,255,' + fl.a + '),transparent 70%),' +
          'radial-gradient(70% 1.1% at ' + fl.x + '% ' + fl.y + '%,rgba(120,190,255,' + (.85 * fl.a) + '),transparent 70%),' +
          'radial-gradient(30% 14% at ' + fl.x + '% ' + fl.y + '%,rgba(90,150,255,' + (.25 * fl.a) + '),transparent 70%)';
        flare.style.opacity = 1;
      } else flare.style.opacity = 0;
      flashL.style.opacity = clamp(o.flash ?? 0);
      const g = o.grade, ga = o.gradeAmt ?? .6;
      grade.style.background = !g ? 'none' : g === 'teal' ? 'linear-gradient(180deg,rgba(0,160,170,' + ga * .55 + '),rgba(255,140,40,' + ga * .45 + '))'
        : g === 'warm' ? 'linear-gradient(180deg,rgba(255,170,90,' + ga * .5 + '),rgba(255,90,40,' + ga * .35 + '))'
        : g === 'cold' ? 'linear-gradient(180deg,rgba(60,120,255,' + ga * .5 + '),rgba(0,200,220,' + ga * .3 + '))'
        : g === 'mono' ? 'rgba(128,128,128,' + ga + ')' : 'none';
    }
    return { frame, layers: { grade, leak, flare, vig, flash: flashL, barT, barB, grain: gc } };
  }

  /* xromatik aberratsiya / glitch: el uchun CSS filter (drop-shadow siljishlari) */
  function chroma(el, px) {
    el.style.filter = px > .05 ? 'drop-shadow(' + px.toFixed(1) + 'px 0 0 rgba(255,0,80,.75)) drop-shadow(' + (-px).toFixed(1) + 'px 0 0 rgba(0,220,255,.75))' : 'none';
  }
  /* glitch kesiklari: el klonlari o'rniga clip-path bilan gorizontal tilimlar siljiydi */
  function glitch(el, t, t0, d = .22, amt = 30) {
    const on = t >= t0 && t < t0 + d;
    if (!on) { el.style.clipPath = 'none'; el.style.transform = el._baseT || ''; return; }
    const f = Math.floor((t - t0) * 60), y = Math.abs(hash(f * 7)) * 80, hgt = 4 + Math.abs(hash(f * 11)) * 14;
    el.style.clipPath = 'inset(' + y + '% 0 ' + Math.max(0, 100 - y - hgt) + '% 0)';
    el.style.transform = (el._baseT || '') + ' translateX(' + (hash(f * 13) * amt).toFixed(1) + 'px)';
  }
  /* fokus (DOF): chuqurlik bo'yicha blur — fokus tekisligidan uzoqlashgan sari xiralashadi */
  const dof = (depth, focus, strength = 10) => 'blur(' + (Math.abs(depth - focus) * strength).toFixed(2) + 'px)';

  /* ---------- foydalanuvchi videosi (kadrlar ketma-ketligi) ---------- */
  /* prep_footage.py kadrlarni dir/f_000001.jpg qilib chiqaradi. Footage(img, dir, fps, n).show(localT) */
  function Footage(img, dir, fps, n, ext = 'jpg') {
    let cur = -1;
    return {
      fps, n, dur: n / fps,
      async show(lt) {
        const i = clamp(Math.floor(lt * fps), 0, n - 1);
        if (i === cur) return; cur = i;
        img.src = dir + '/f_' + String(i + 1).padStart(6, '0') + '.' + ext;
        try { await img.decode(); } catch (e) { /* oxirgi kadr qoladi */ }
      },
    };
  }
  /* speed ramp: kalitlar [[filmT, clipSpeed], ...] → klip vaqti (integral, deterministik) */
  function ramp(t, ks, steps = 240) {
    let acc = 0; const dt = t / steps;
    for (let i = 0; i < steps; i++) acc += keys((i + .5) * dt, ks, E.io) * dt;
    return acc;
  }

  G.CineFX = { clamp, lerp, prog, E, spring, noise1, hash, keys, zoomKeys, shake, punch, whip, flash, iris,
    splitWords, splitChars, rise, decode, counter, mount, chroma, glitch, dof, Footage, ramp };
})(window);
