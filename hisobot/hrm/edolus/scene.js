/* ================= EDOLUS uslubidagi sahnalar (2D canvas) =================
   Reel'dagi sayt ketma-ketligi: orbita → sun'iy yo'ldosh → oltin tuman →
   hisoblash koridori → energiya portlashi → nur lentasi → yo'ldagi mashina (Kia Sonet).
   API zavod sahnasi bilan bir xil: resize, frame(now), setJ, setTarget, snap. */
function makeEdolus(canvas, slides, carSrc){
  var W = 1920, H = 1080;
  canvas.width = W; canvas.height = H;
  var ctx = canvas.getContext("2d");
  function cv(w, h){ var c = document.createElement("canvas"); c.width = w; c.height = h; return c; }
  function clamp(v, a, b){ return v < a ? a : v > b ? b : v; }
  function sm(k){ k = clamp(k, 0, 1); return k * k * (3 - 2 * k); }
  function io(k){ k = clamp(k, 0, 1); return k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; }

  /* ---- shovqin ---- */
  function hs(x, y, s){ var h = Math.imul((x * 374761393 + y * 668265263 + s * 982451653) | 0, 1274126177); h = Math.imul(h ^ (h >>> 13), 1103515245); h ^= h >>> 16; return (h >>> 0) / 4294967295; }
  function vn(x, y, s){ var xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    var a = hs(xi, yi, s), b = hs(xi + 1, yi, s), c = hs(xi, yi + 1, s), d = hs(xi + 1, yi + 1, s); return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v; }
  function fbm(x, y, s, o){ var a = 0, am = .5, f = 1, n = 0; for (var i = 0; i < o; i++){ a += am * vn(x * f, y * f, s + i * 7); n += am; am *= .5; f *= 2.02; } return a / n; }
  function tex(w, h, sc, s, o, fn, wrap){
    var c = cv(w, h), g = c.getContext("2d"), im = g.createImageData(w, h), d = im.data;
    for (var y = 0; y < h; y++) for (var x = 0; x < w; x++){
      var n = fbm(x / sc, y / sc, s, o);
      if (wrap){ var m = fbm((x - w) / sc, y / sc, s, o), k = x / w; n = n * (1 - k) + m * k; }   /* gorizontal choklanmaydigan */
      var p = fn(n, x, y), q = (y * w + x) * 4; d[q] = p[0]; d[q + 1] = p[1]; d[q + 2] = p[2]; d[q + 3] = p[3];
    }
    g.putImageData(im, 0, 0); return c;
  }
  var rnd = (function(){ var s = 7; return function(){ s = Math.imul(s ^ (s >>> 15), 2246822519) + 12345 | 0; return ((s >>> 0) % 100000) / 100000; }; })();

  /* ---- yulduzlar ---- */
  var stars = cv(W, H);
  (function(){ var g = stars.getContext("2d");
    for (var i = 0; i < 1400; i++){ var r = rnd() < .04 ? 1.6 : rnd() * .9 + .3; g.fillStyle = "rgba(220,230,255," + (rnd() * .7 + .15).toFixed(2) + ")"; g.beginPath(); g.arc(rnd() * W, rnd() * H, r, 0, 7); g.fill(); }
  })();

  /* ---- Yer teksturasi (okean, quruqlik, bulutlar) ---- */
  var earth = tex(720, 360, 70, 11, 5, function(n, x, y){
    var lat = Math.abs(y / 360 - .5) * 2, land = fbm(x / 95, y / 95, 41, 5), cl = fbm(x / 38, y / 30, 77, 5);
    var r = 10 + 24 * n, g = 38 + 50 * n, b = 92 + 70 * n;
    if (land > .56){ var k = clamp((land - .56) * 6, 0, 1); r = 80 + 70 * k; g = 86 + 40 * k; b = 60 + 10 * k; }
    var c = clamp((cl - .55) * 2.6, 0, 1) * .85; r = r + (245 - r) * c; g = g + (248 - g) * c; b = b + (255 - b) * c;
    return [r, g, b, 255];
  }, true);
  function drawEarth(g, cx, cy, R, rot, t){
    g.save(); g.beginPath(); g.arc(cx, cy, R, 0, 7); g.clip();
    var tw = R * 3.4, th = R * 1.7, off = ((rot % 1) + 1) % 1 * tw;
    for (var k = -1; k < 2; k++) g.drawImage(earth, cx - R - off + k * tw, cy - R - th * .3, tw, th);
    var sh = g.createRadialGradient(cx + R * .35, cy - R * .55, R * .2, cx, cy, R);
    sh.addColorStop(0, "rgba(0,0,0,0)"); sh.addColorStop(.7, "rgba(2,6,20,.35)"); sh.addColorStop(1, "rgba(2,4,14,.92)");
    g.fillStyle = sh; g.fillRect(cx - R, cy - R, R * 2, R * 2);
    g.restore();
    g.save(); g.globalCompositeOperation = "lighter";
    var at = g.createRadialGradient(cx, cy, R * .965, cx, cy, R * 1.07);
    at.addColorStop(0, "rgba(60,140,255,0)"); at.addColorStop(.32, "rgba(90,170,255,.55)"); at.addColorStop(.5, "rgba(70,140,255,.22)"); at.addColorStop(1, "rgba(40,90,255,0)");
    g.fillStyle = at; g.beginPath(); g.arc(cx, cy, R * 1.07, 0, 7); g.fill();
    g.restore();
  }
  function flare(g, x, y, s, warm){
    g.save(); g.globalCompositeOperation = "lighter";
    var r = g.createRadialGradient(x, y, 0, x, y, 420 * s);
    r.addColorStop(0, warm ? "rgba(255,230,190,.95)" : "rgba(220,235,255,.9)"); r.addColorStop(.08, warm ? "rgba(255,170,90,.5)" : "rgba(150,190,255,.45)"); r.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = r; g.fillRect(x - 420 * s, y - 420 * s, 840 * s, 840 * s);
    var l = g.createLinearGradient(x - 900 * s, y, x + 900 * s, y);
    l.addColorStop(0, "rgba(0,0,0,0)"); l.addColorStop(.5, warm ? "rgba(255,190,120,.55)" : "rgba(170,200,255,.5)"); l.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = l; g.fillRect(x - 900 * s, y - 2.5 * s, 1800 * s, 5 * s);
    g.restore();
  }
  function brand(g, dark){
    g.save(); g.font = "600 15px 'Segoe UI',system-ui,sans-serif"; g.textAlign = "center";
    g.fillStyle = dark ? "rgba(60,50,40,.7)" : "rgba(235,240,250,.75)";
    var s = "A D M   J I Z Z A K H"; g.fillText(s, W / 2, 48); g.restore();
  }

  /* ---- 1) ORBITA ---- */
  function sOrbit(g, t, c){
    g.fillStyle = "#02040b"; g.fillRect(0, 0, W, H);
    g.drawImage(stars, -30 * c, -10 * c);
    var R = 1650, cx = 620 + 60 * c, cy = 2260 - 40 * c;
    drawEarth(g, cx, cy, R, t * .004 + c * .03, t);
    flare(g, cx + R * Math.cos(-1.12), cy + R * Math.sin(-1.12), 1, false);
    brand(g);
  }
  /* ---- 2) SUN'IY YO'LDOSH ---- */
  var foil = tex(120, 180, 9, 5, 3, function(n){ var v = 120 + 130 * n; return [v * 1.0, v * .78, v * .38, 255]; });
  function panel(g, x, y, w, h){
    var gr = g.createLinearGradient(x, y, x + w, y + h); gr.addColorStop(0, "#0f1d3d"); gr.addColorStop(.5, "#22407a"); gr.addColorStop(1, "#0a1428");
    g.fillStyle = gr; g.fillRect(x, y, w, h);
    g.strokeStyle = "rgba(160,190,255,.25)"; g.lineWidth = 1;
    for (var i = 1; i < 4; i++){ g.beginPath(); g.moveTo(x + w * i / 4, y); g.lineTo(x + w * i / 4, y + h); g.stroke(); }
    for (var j = 1; j < 7; j++){ g.beginPath(); g.moveTo(x, y + h * j / 7); g.lineTo(x + w, y + h * j / 7); g.stroke(); }
    g.strokeStyle = "#d7a84e"; g.lineWidth = 3; g.strokeRect(x, y, w, h);
  }
  function satellite(g, x, y, s, ang, spin, t){
    g.save(); g.translate(x, y); g.rotate(ang); g.scale(s, s);
    var fs = .45 + .55 * Math.abs(Math.cos(spin));
    for (var side = -1; side <= 1; side += 2){
      g.save(); g.scale(side, 1);
      g.strokeStyle = "#c9a052"; g.lineWidth = 4; g.beginPath(); g.moveTo(60, 0); g.lineTo(100, 0); g.stroke();
      g.save(); g.scale(1, fs);
      for (var k = 0; k < 4; k++) panel(g, 100 + k * 150, -120, 140, 240);
      g.restore(); g.restore();
    }
    g.drawImage(foil, -60, -90, 120, 180);
    var sh = g.createLinearGradient(-60, -90, 60, 90); var p = (t * .15) % 1;
    sh.addColorStop(clamp(p - .15, 0, 1), "rgba(255,255,255,0)"); sh.addColorStop(p, "rgba(255,245,210,.55)"); sh.addColorStop(clamp(p + .15, 0, 1), "rgba(255,255,255,0)");
    g.fillStyle = sh; g.fillRect(-60, -90, 120, 180);
    g.strokeStyle = "rgba(90,60,20,.8)"; g.lineWidth = 2; g.strokeRect(-60, -90, 120, 180);
    g.fillStyle = "#e9e3d6"; g.beginPath(); g.ellipse(0, -112, 46, 16, 0, 0, 7); g.fill();
    g.strokeStyle = "#9c8f78"; g.beginPath(); g.moveTo(0, -112); g.lineTo(0, -90); g.stroke();
    g.restore();
  }
  function sSat(g, t, c){
    var bg = g.createLinearGradient(0, 0, 0, H); bg.addColorStop(0, "#030714"); bg.addColorStop(1, "#0b1f4a");
    g.fillStyle = bg; g.fillRect(0, 0, W, H);
    g.drawImage(stars, -20 * c, 0);
    drawEarth(g, 960 - 40 * c, 3050, 2350, t * .003 + c * .02, t);
    flare(g, 260 + 30 * c, 760, .8, true);
    satellite(g, 1500 - 50 * c, 300 + 16 * Math.sin(t * .4), .52 + .03 * c, -.5 + .05 * Math.sin(t * .2) + .08 * c, t * .25 + c * .6, t);
    brand(g);
  }
  /* ---- 3) OLTIN TUMAN ---- */
  var cloudA = tex(400, 225, 48, 21, 5, function(n){ var a = clamp((n - .38) * 2.6, 0, 1); return [255, 238, 205, a * 255]; });
  var cloudB = tex(400, 225, 30, 33, 5, function(n){ var a = clamp((n - .45) * 3, 0, 1); return [214, 150, 70, a * 200]; });
  var dunes = [0, 1, 2].map(function(L){ var ys = []; for (var x = 0; x <= W; x += 8) ys.push(H - 250 + L * 90 - 120 * fbm(x / (520 - L * 120), L * 3.1, 90 + L, 4)); return ys; });
  function emblem(g, x, y, s, t){
    g.save(); g.translate(x, y); g.rotate(Math.PI / 4 + .04 * Math.sin(t * .5)); g.scale(s, s);
    g.shadowColor = "rgba(255,210,140,.9)"; g.shadowBlur = 40;
    g.strokeStyle = "#2c2111"; g.lineWidth = 10; g.strokeRect(-90, -90, 180, 180);
    g.shadowBlur = 0; g.lineWidth = 5; g.strokeRect(-55, -55, 110, 110);
    g.beginPath(); g.moveTo(-55, 0); g.lineTo(0, 0); g.lineTo(0, 55); g.stroke();
    g.restore();
  }
  function sHaze(g, t, c){
    var bg = g.createLinearGradient(0, 0, 0, H); bg.addColorStop(0, "#f7ecd8"); bg.addColorStop(.6, "#e3b878"); bg.addColorStop(1, "#9a6a34");
    g.fillStyle = bg; g.fillRect(0, 0, W, H);
    var z = 1 + .05 * c + .02 * Math.sin(t * .2);
    for (var i = 0; i < 2; i++){
      var o = (t * (12 + i * 10) + c * 140) % (W * 1.2);
      g.globalAlpha = i ? .7 : .95;
      g.drawImage(i ? cloudB : cloudA, -o, -60 * z, W * 1.2 * z, H * 1.2 * z);
      g.drawImage(i ? cloudB : cloudA, W * 1.2 - o, -60 * z, W * 1.2 * z, H * 1.2 * z);
    }
    g.globalAlpha = 1;
    dunes.forEach(function(ys, L){
      g.beginPath(); g.moveTo(0, H);
      for (var k = 0; k < ys.length; k++) g.lineTo(k * 8, ys[k] + 30 * c * (L + 1) * .3);
      g.lineTo(W, H); g.closePath();
      var d = g.createLinearGradient(0, H - 380, 0, H); d.addColorStop(0, ["#e9c088", "#c98f4b", "#8e5a26"][L]); d.addColorStop(1, ["#c8904c", "#94602c", "#5a3613"][L]);
      g.fillStyle = d; g.fill();
    });
    g.save(); g.globalCompositeOperation = "lighter";
    for (var r = 0; r < 6; r++){ var a = -.9 + r * .12 + .03 * Math.sin(t * .3 + r);
      g.save(); g.translate(1500, -80); g.rotate(a); var l = g.createLinearGradient(0, 0, 0, 1400); l.addColorStop(0, "rgba(255,230,180,.22)"); l.addColorStop(1, "rgba(255,230,180,0)");
      g.fillStyle = l; g.beginPath(); g.moveTo(-10, 0); g.lineTo(10, 0); g.lineTo(90, 1400); g.lineTo(-90, 1400); g.fill(); g.restore(); }
    g.restore();
    emblem(g, 1440 - 40 * c, 470, 1, t);
    brand(g, true);
  }
  /* ---- 4) HISOBLASH KORIDORI ---- */
  var motes = []; for (var i = 0; i < 160; i++) motes.push([rnd() * 6 - 3, rnd() * 4 - 1.6, rnd() * 14 + 1, rnd()]);
  function sCorr(g, t, c){
    var bg = g.createLinearGradient(0, 0, 0, H); bg.addColorStop(0, "#040302"); bg.addColorStop(.55, "#110b04"); bg.addColorStop(1, "#060402");
    g.fillStyle = bg; g.fillRect(0, 0, W, H);
    var VX = 1250, VY = 470, F = 760, mv = t * .35 + c * 1.6;
    function P(X, Y, Z){ return [VX + X * F / Z, VY - Y * F / Z]; }
    /* markazdagi nur piramidasi */
    g.save(); g.globalCompositeOperation = "lighter";
    var a = P(0, 3.4, 9), b1 = P(-1.6, -1.6, 9), b2 = P(1.6, -1.6, 9);
    var pg = g.createLinearGradient(a[0], a[1], a[0], b1[1]); pg.addColorStop(0, "rgba(255,210,120,.05)"); pg.addColorStop(1, "rgba(255,190,90,.55)");
    g.fillStyle = pg; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b2[0], b2[1]); g.lineTo(b1[0], b1[1]); g.fill();
    var m1 = P(-.35, 1.7, 9.2), m2 = P(.35, -1.6, 9.2);
    var mg = g.createLinearGradient(m1[0], 0, m2[0], 0); mg.addColorStop(0, "#ffd37a"); mg.addColorStop(.5, "#fff1c4"); mg.addColorStop(1, "#d9962c");
    g.shadowColor = "rgba(255,190,90,1)"; g.shadowBlur = 60; g.fillStyle = mg; g.fillRect(m1[0], m1[1], m2[0] - m1[0], m2[1] - m1[1]);
    g.restore();
    /* stellajlar: chuqurlik bo'yicha uzoqdan yaqinga */
    for (var k = 16; k >= 0; k--){
      var z0 = k + 1 - (mv % 1), z1 = z0 + .82; if (z0 < .35) continue;
      var fog = Math.exp(-z0 * .13);
      for (var s = -1; s <= 1; s += 2){
        var X = 3 * s, q = [P(X, -1.6, z0), P(X, 2.6, z0), P(X, 2.6, z1), P(X, -1.6, z1)];
        g.fillStyle = "rgba(14,10,6," + (.95) + ")"; g.beginPath(); g.moveTo(q[0][0], q[0][1]); for (var j = 1; j < 4; j++) g.lineTo(q[j][0], q[j][1]); g.fill();
        g.strokeStyle = "rgba(255,190,90," + (.35 * fog) + ")"; g.lineWidth = 1.5; g.stroke();
        for (var r = 0; r < 7; r++) for (var cc = 0; cc < 3; cc++){
          var Y = -1.3 + r * .55, Z = z0 + .12 + cc * .25, p = P(X, Y, Z), sz = 34 / Z, on = hs(k + Math.floor(mv), r * 3 + cc, s + 5) > .25;
          if (!on) continue;
          var fl = .55 + .45 * Math.sin(t * 3 + r + cc * 2 + k);
          g.fillStyle = "rgba(255," + (180 + 40 * fl | 0) + ",90," + (fog * (.5 + .5 * fl)).toFixed(3) + ")";
          g.fillRect(p[0] - sz * .5, p[1], sz, sz * .35);
          var pr = P(X, -3.2 - Y, Z);                            /* pol ustidagi aks */
          g.fillStyle = "rgba(255,190,90," + (fog * .18 * fl).toFixed(3) + ")"; g.fillRect(pr[0] - sz * .5, pr[1], sz, sz * .6);
        }
      }
    }
    g.save(); g.globalCompositeOperation = "lighter";
    motes.forEach(function(m){ var Z = ((m[2] - mv * .6) % 15 + 15) % 15 + .5, p = P(m[0], m[1] + .1 * Math.sin(t + m[3] * 9), Z), r = 2.2 / Z * 4;
      g.fillStyle = "rgba(255,210,140," + (.6 * Math.exp(-Z * .1)).toFixed(3) + ")"; g.beginPath(); g.arc(p[0], p[1], r, 0, 7); g.fill(); });
    g.restore();
    brand(g);
  }
  /* ---- 5) ENERGIYA PORTLASHI ---- */
  var neb = tex(400, 225, 40, 51, 5, function(n){ var a = clamp((n - .4) * 2.4, 0, 1); return [255, 160 + 70 * n, 60, a * 255]; });
  var rays = []; for (var i = 0; i < 140; i++) rays.push([rnd() * 6.283, rnd() * 600 + 200, rnd() * 2 + .5, rnd()]);
  function sNeb(g, t, c){
    g.fillStyle = "#0a0502"; g.fillRect(0, 0, W, H);
    var cx = 1400 + 60 * Math.sin(c * .8), cy = 520;
    g.save(); g.globalCompositeOperation = "lighter";
    g.translate(cx, cy); g.rotate(t * .03 + c * .4);
    g.globalAlpha = .75; g.drawImage(neb, -W * .75, -H * .75, W * 1.5, H * 1.5);
    g.rotate(-t * .07); g.globalAlpha = .45; g.drawImage(neb, -W * .6, -H * .6, W * 1.2, H * 1.2);
    g.globalAlpha = 1; g.rotate(t * .05);
    rays.forEach(function(r){ var a = r[0] + t * .02 * (r[3] - .5), L = r[1] * (1 + .15 * Math.sin(t * 1.3 + r[3] * 9));
      var lg = g.createLinearGradient(0, 0, Math.cos(a) * L, Math.sin(a) * L); lg.addColorStop(0, "rgba(255,220,150,.5)"); lg.addColorStop(1, "rgba(255,150,40,0)");
      g.strokeStyle = lg; g.lineWidth = r[2]; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(a) * L, Math.sin(a) * L); g.stroke(); });
    var core = g.createRadialGradient(0, 0, 0, 0, 0, 380); core.addColorStop(0, "rgba(255,250,230,1)"); core.addColorStop(.15, "rgba(255,200,110,.75)"); core.addColorStop(1, "rgba(255,120,20,0)");
    g.fillStyle = core; g.fillRect(-380, -380, 760, 760);
    g.restore();
    brand(g);
  }
  /* ---- 6) NUR LENTASI ---- */
  var thumb = tex(160, 100, 14, 61, 4, function(n){ return [200 + 55 * n, 130 + 90 * n, 50 + 60 * n, 255]; });
  function rr(g, x, y, w, h, r){ g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
  function sRibbon(g, t, c){
    var bg = g.createRadialGradient(960, 420, 100, 960, 540, 1300); bg.addColorStop(0, "#6a5444"); bg.addColorStop(.6, "#3a2e25"); bg.addColorStop(1, "#1a1410");
    g.fillStyle = bg; g.fillRect(0, 0, W, H);
    [[260, 300, 520, 330, 0], [800, 250, 520, 330, 1], [1340, 300, 520, 330, 2]].forEach(function(cd){
      var x = cd[0] - c * 70 * (cd[4] - 1) + 10 * Math.sin(t * .4 + cd[4]), y = cd[1] + 8 * Math.cos(t * .5 + cd[4]);
      g.save(); rr(g, x, y, cd[2], cd[3], 14); g.fillStyle = "rgba(255,255,255,.06)"; g.fill(); g.strokeStyle = "rgba(255,240,220,.22)"; g.lineWidth = 1.5; g.stroke();
      g.clip(); g.globalAlpha = .55; g.drawImage(thumb, x + 30, y + 60, cd[2] * .45, cd[3] * .6); g.globalAlpha = 1;
      g.fillStyle = "rgba(255,240,220,.35)"; g.fillRect(x + 30, y + 26, 160, 8); g.fillRect(x + cd[2] * .55, y + 70, cd[2] * .35, 6); g.fillRect(x + cd[2] * .55, y + 90, cd[2] * .28, 6);
      g.restore();
    });
    function path(ph, amp){ g.beginPath(); for (var x = -60; x <= W + 60; x += 12){ var y = 700 + amp * Math.sin(x / 380 + t * .6 + ph) + amp * .45 * Math.sin(x / 170 - t * .9 + ph * 2) - 60 * Math.sin(c * .5); x === -60 ? g.moveTo(x, y) : g.lineTo(x, y); } }
    g.save(); g.globalCompositeOperation = "lighter"; g.lineCap = "round";
    [[0, 120], [1.7, 80]].forEach(function(rb, i){
      [[46, .07], [22, .16], [9, .4], [3, .95]].forEach(function(s){ path(rb[0], rb[1]); g.lineWidth = s[0] * (i ? .6 : 1); g.strokeStyle = (s[0] < 5 ? "rgba(255,248,225," : "rgba(255,170,60,") + s[1] + ")"; g.stroke(); });
    });
    g.restore();
    brand(g);
  }
  /* ---- 7) YO'LDAGI MASHINA (Kia Sonet) ---- */
  var LW = 1140, LH = 600, HZ = 300, VXl = 560, base = cv(LW, LH);
  (function paint(){
    var g = base.getContext("2d");
    var gr = g.createLinearGradient(0, 0, 0, HZ); gr.addColorStop(0, "#9fb8cf"); gr.addColorStop(.55, "#cbd8e2"); gr.addColorStop(1, "#eef0ee");
    g.fillStyle = gr; g.fillRect(0, 0, LW, HZ + 2);
    for (var i = 0; i < 14; i++){ var x = hs(i, 1, 3) * LW, y = 30 + hs(i, 2, 3) * 120, r = 60 + hs(i, 3, 3) * 140;
      var c2 = g.createRadialGradient(x, y, 0, x, y, r); c2.addColorStop(0, "rgba(255,255,255,.55)"); c2.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = c2; g.beginPath(); g.ellipse(x, y, r * 1.8, r * .45, 0, 0, 7); g.fill(); }
    var ranges = [{s: 3, top: 70, amp: 150, base: HZ - 8, col: [150, 165, 182], snow: .55, fz: 1 / 210, hz: .35},
                  {s: 9, top: 120, amp: 120, base: HZ - 2, col: [104, 118, 134], snow: .62, fz: 1 / 150, hz: .18},
                  {s: 21, top: 205, amp: 70, base: HZ + 4, col: [74, 82, 92], snow: .8, fz: 1 / 95, hz: .06}];
    ranges.forEach(function(R){
      var ys = [];
      for (var x = 0; x <= LW; x++){ var h = fbm(x * R.fz, R.s, R.s, 5) * 1.6 - .3; if (R.s === 3) h += .35 * Math.exp(-Math.pow((x - 330) / 140, 2)); ys.push(R.top + (1 - clamp(h + .2, 0, 1.2)) * R.amp); }
      var img = g.getImageData(0, 0, LW, LH), d = img.data;
      for (var x = 0; x < LW; x++) for (var y = Math.floor(ys[x]); y < R.base; y++){
        var k = (y - ys[x]) / (R.base - ys[x]), slope = ys[Math.min(LW, x + 2)] - ys[Math.max(0, x - 2)];
        var light = clamp(.75 - slope * .03 + (fbm(x * .021, y * .034, R.s + 5, 3) - .5) * .3, .35, 1.15);
        var snowLine = R.snow * (1 + .25 * (vn(x * .03, 0, R.s + 2) - .5)), isSnow = k + (fbm(x * .018, y * .03, R.s + 7, 3) - .5) * .55 < snowLine * .8;
        var r, gg, b; if (isSnow){ var sv = 225 + 30 * light; r = sv * .97; gg = sv * .99; b = sv; } else { r = R.col[0] * light; gg = R.col[1] * light; b = R.col[2] * light; }
        var q = (y * LW + x) * 4; d[q] = r + (214 - r) * R.hz; d[q + 1] = gg + (224 - gg) * R.hz; d[q + 2] = b + (232 - b) * R.hz; d[q + 3] = 255;
      }
      g.putImageData(img, 0, 0);
    });
    var lt = HZ + 4, lb = HZ + 92;
    g.save(); g.beginPath(); g.moveTo(0, lt); g.lineTo(VXl - 60, lt); g.lineTo(VXl - 230, lb); g.lineTo(0, lb + 40); g.closePath(); g.clip();
    g.save(); g.translate(0, lt * 2); g.scale(1, -1); g.globalAlpha = .55; g.drawImage(base, 0, 0, LW, lt, 0, 0, LW, lt); g.restore();
    gr = g.createLinearGradient(0, lt, 0, lb + 40); gr.addColorStop(0, "rgba(120,160,190,.35)"); gr.addColorStop(1, "rgba(70,110,140,.65)"); g.fillStyle = gr; g.fillRect(0, lt, LW, 140);
    g.restore();
    gr = g.createLinearGradient(0, HZ, 0, LH); gr.addColorStop(0, "#e7ebec"); gr.addColorStop(1, "#f7f8f8"); g.fillStyle = gr;
    g.beginPath(); g.moveTo(VXl + 40, HZ + 2); g.lineTo(LW, HZ + 2); g.lineTo(LW, LH); g.lineTo(VXl + 330, LH); g.closePath(); g.fill();
    g.beginPath(); g.moveTo(0, lb + 40); g.lineTo(VXl - 230, lb); g.lineTo(VXl - 60, HZ + 4); g.lineTo(VXl - 330, LH); g.lineTo(0, LH); g.closePath(); g.fill();
    function pine(x, y, h){ g.fillStyle = "rgb(" + (28 + hs(x | 0, 1, 1) * 6 | 0) + "," + (46 + hs(y | 0, 2, 1) * 6 | 0) + ",40)";
      for (var k = 0; k < 4; k++){ var yy = y - h * (.25 + k * .22), w = h * (.34 - k * .07); g.beginPath(); g.moveTo(x, yy - h * .28); g.lineTo(x - w, yy + h * .12); g.lineTo(x + w, yy + h * .12); g.closePath(); g.fill(); } }
    var trees = [];
    for (var i = 0; i < 70; i++){ var dd = i / 70; trees.push([VXl + 70 + dd * 520 + hs(i, 4, 9) * 30, HZ + 2 + dd * dd * 300, 26 + dd * dd * 300 + hs(i, 5, 9) * 12]); }
    for (var i = 0; i < 40; i++) trees.push([40 + hs(i, 6, 9) * 420, HZ + 6 + hs(i, 7, 9) * 18, 18 + hs(i, 8, 9) * 10]);
    trees.sort(function(a, b){ return a[1] - b[1]; }).forEach(function(tr){ pine(tr[0], tr[1], tr[2]); });
  })();
  var land = cv(LW, LH), lg = land.getContext("2d");
  function drawLand(t){
    lg.drawImage(base, 0, 0);
    var gr = lg.createLinearGradient(0, HZ, 0, LH); gr.addColorStop(0, "#9a9590"); gr.addColorStop(1, "#5c5854");
    lg.fillStyle = gr; lg.beginPath(); lg.moveTo(VXl - 10, HZ); lg.lineTo(VXl + 10, HZ); lg.lineTo(VXl + 340, LH); lg.lineTo(VXl - 340, LH); lg.closePath(); lg.fill();
    lg.strokeStyle = "rgba(245,245,240,.9)"; lg.lineWidth = 1.5;
    for (var s = -1; s <= 1; s += 2){ lg.beginPath(); lg.moveTo(VXl + s * 8, HZ); lg.lineTo(VXl + s * 318, LH); lg.stroke(); }
    var ph = (t * 2.2) % 1; lg.fillStyle = "#e8c35a";
    for (var i = 0; i < 14; i++){ var z0 = (i + ph) / 14, z1 = Math.min(1, (i + ph + .45) / 14), y0 = HZ + Math.pow(z0, 2.2) * (LH - HZ), y1 = HZ + Math.pow(z1, 2.2) * (LH - HZ), w0 = .6 + z0 * 7, w1 = .6 + z1 * 7;
      lg.beginPath(); lg.moveTo(VXl - w0, y0); lg.lineTo(VXl + w0, y0); lg.lineTo(VXl + w1, y1); lg.lineTo(VXl - w1, y1); lg.closePath(); lg.fill(); }
    var r = lg.createRadialGradient(860, 70, 0, 860, 70, 380); r.addColorStop(0, "rgba(255,240,215,.55)"); r.addColorStop(1, "rgba(255,240,215,0)"); lg.fillStyle = r; lg.fillRect(0, 0, LW, LH);
  }
  var car = new Image(); car.src = carSrc;
  var CAR = {x: 660 + 300, y: 440 + 120, w: 520};             /* kartochka markazi bo'yicha */
  function sCar(g, t, c){
    g.fillStyle = "#f3f0ea"; g.fillRect(0, 0, W, H);
    brand(g, true);
    var cx = 960 + 460, cy = 470;                                /* kompozitsiya o'ngda: chapda sarlavha uchun joy */
    var sc = .62, dr = 1 + .02 * Math.sin(t * .15) + .015 * c;
    g.save(); g.translate(cx, cy); g.scale(sc * dr, sc * dr);
    drawLand(t);
    g.save(); g.shadowColor = "rgba(40,30,20,.35)"; g.shadowBlur = 80; g.shadowOffsetY = 40;
    g.drawImage(land, -LW / 2, -LH / 2); g.restore();
    var bob = Math.sin(t * 11) * 1.2 + Math.sin(t * 4.3) * 1, sway = Math.sin(t * 1.3) * 3;
    var cw = 480, ch = car.naturalWidth ? cw * car.naturalHeight / car.naturalWidth : cw * .9, x0 = -cw / 2 + sway, y0 = 150 - ch * .45 + bob;
    var sh = g.createRadialGradient(sway, y0 + ch - 6, 10, sway, y0 + ch - 6, cw * .5);
    sh.addColorStop(0, "rgba(0,0,0,.5)"); sh.addColorStop(1, "rgba(0,0,0,0)");
    g.save(); g.scale(1, .12); g.fillStyle = sh; g.beginPath(); g.arc(sway, (y0 + ch - 6) / .12, cw * .5, 0, 7); g.fill(); g.restore();
    if (car.complete && car.naturalWidth) g.drawImage(car, x0, y0, cw, ch);
    g.save(); g.globalCompositeOperation = "screen"; var gl = .55 + .25 * Math.pow(Math.sin(t * 2.2), 2);
    [[-.36, .335], [.36, .335]].forEach(function(p){ var rx = sway + p[0] * cw, ry = y0 + p[1] * ch, rg = g.createRadialGradient(rx, ry, 0, rx, ry, 70);
      rg.addColorStop(0, "rgba(255,60,30," + (.55 * gl).toFixed(3) + ")"); rg.addColorStop(1, "rgba(255,60,30,0)"); g.fillStyle = rg; g.fillRect(rx - 70, ry - 70, 140, 140); });
    g.restore();
    g.restore();
  }
  /* stop-chiroqlar nuqtasi (kirish zoom'i uchun) */
  var CAR_FOCUS = [960 + 460, 470 + .62 * (150 - 432 * .45 + 432 * .335)];

  /* ---- sahnalarni slaydlarga bog'lash: bo'lim slaydlari (sec2) chegarasi ---- */
  var ORDER = [sOrbit, sSat, sHaze, sCorr, sNeb, sRibbon, sCar, sCar];
  var LIGHT = [sHaze, sCar];
  var sceneOf = [], startOf = [], sec = 0, st = 0;
  slides.forEach(function(s, i){
    if (s.querySelector(".sec2")){ sec++; if (ORDER[sec] !== ORDER[sec - 1]) st = i; }
    sceneOf.push(ORDER[Math.min(sec, ORDER.length - 1)]); startOf.push(st);
    if (s.querySelector(".sec2,.cover")){ s.classList.add("hero"); if (LIGHT.indexOf(sceneOf[i]) >= 0) s.classList.add("onlight"); }
  });

  var J = 0, from = 0, target = 0, t0 = performance.now();
  var bufA = cv(W, H), bufB = cv(W, H), gA = bufA.getContext("2d"), gB = bufB.getContext("2d");
  function draw(g, i, t, c, z, fx, fy){
    g.save(); if (z !== 1){ g.translate(fx, fy); g.scale(z, z); g.translate(-fx, -fy); }
    sceneOf[i](g, t, c); g.restore();
  }
  function frame(now){
    var t = (now - t0) / 1000, N = slides.length;
    var i0 = clamp(Math.floor(J), 0, N - 1), i1 = Math.min(N - 1, i0 + 1), f = J - i0;
    if (f < 1e-4 || sceneOf[i0] === sceneOf[i1]){
      draw(ctx, i0, t, J - startOf[i0], 1, 960, 540);
      return;
    }
    /* bo'limlararo o'tish: eski sahna ichkariga "uchib" ketadi, yangisi chiqib keladi */
    var e = io(f), toCar = sceneOf[i1] === sCar;
    draw(gA, i0, t, i0 - startOf[i0] + f, 1 + .9 * e, 960, 540);
    var zB = toCar ? Math.exp(Math.log(2.8) * (1 - e)) : 1 + .3 * (1 - e);
    draw(gB, i1, t, 0, zB, toCar ? CAR_FOCUS[0] : 960, toCar ? CAR_FOCUS[1] : 540);
    ctx.globalAlpha = 1; ctx.drawImage(bufA, 0, 0);
    ctx.globalAlpha = sm((f - .25) / .5); ctx.drawImage(bufB, 0, 0);
    var fl = Math.max(0, 1 - Math.abs(f - .5) / .14); ctx.globalAlpha = fl * .55;
    ctx.fillStyle = LIGHT.indexOf(sceneOf[i1]) >= 0 ? "#fff8ee" : "#ffe2b0"; ctx.fillRect(0, 0, W, H);
    ctx.globalAlpha = 1;
  }
  return {
    resize: function(){},
    frame: frame,
    frameT: function(t){ frame(t0 + t * 1000); },
    setJ: function(j){ J = j; },
    setTarget: function(t){ from = J; target = t; },
    snap: function(j){ J = j; from = j; target = j; }
  };
}
