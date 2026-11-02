"""Montaj: "Birinchi qadamlar" — namuna (Sony kino-reklama) grammatikasida.

Namunaning 47 ta kesish nuqtasi va musiqasi aynan saqlanadi, shuning uchun har bir
kesish musiqa zarbiga tushadi. Kadrlar: foydalanuvchi videolari va rasmlari.

  python3 montaj.py probe 3.5 12.5 ...   -> ish/probe/*.jpg (tekshiruv kadrlari)
  python3 montaj.py render                -> chiqish/Birinchi_qadamlar.mp4

Manba: ish/src/<IMG>.mp4 (1080x1920, 30 fps, all-intra; tayyorlash buyrug'i README da).
"""
import math, os, subprocess, sys
from functools import lru_cache
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 24
DUR = 66.827
REF = os.path.join(HERE, "namuna", "namuna.mp4")
FONT_DIR = "/usr/share/fonts/opentype/inter/"
BAND = 608  # 16:9 keng kino oynasi (vertikal kadr ichida)

# ---------------------------------------------------------------- shotlist
# (boshlanish, manba, kirish_s, tezlik, (H0,H1), (cx0,cx1), (cy0,cy1), punch, grade)
# manba: video "2027" yoki rasm "r01"; "black" / "white" maxsus.
# H = ko'rinish balandligi (manba balandligiga nisbatan), cx, cy = markaz (0..1).
S = [
    (0.000, "r10", 0, 1, (.50, .44), (.46, .46), (.80, .80), 0, "amber"),
    (1.125, "2031", .5, .6, (.78, .70), (.52, .52), (.62, .60), 0, "amber"),
    (2.417, "2036", 6.0, 1, (.80, .78), (.50, .52), (.22, .22), 0, "amber"),
    (2.958, "r01", 0, 1, (.34, .30), (.47, .47), (.33, .33), 0, "amber"),
    (4.250, "2032", 21.0, 1, (.55, .52), (.48, .48), (.82, .82), .04, "amber"),
    (4.875, "2028", 11.6, 1, (.42, .38), (.40, .40), (.58, .58), .04, "amber"),
    (5.542, "2029", 26.0, 1, (.70, .64), (.56, .56), (.58, .58), .04, "amber"),
    (6.250, "black", 0, 1, None, None, None, 0, "amber"),
    (7.833, "2027", 19.0, .55, (.86, .74), (.52, .52), (.52, .50), 0, "amber"),
    # 1. KASHFIYOT — iliq oltin
    (12.083, "2032", 2.0, .6, (1.0, .90), (.55, .56), (.48, .46), 0, "golden"),
    (13.917, "2026", .5, .7, (.72, .62), (.60, .58), (.56, .56), .03, "golden"),
    (16.500, "r06", 0, 1, (.72, .66), (.47, .47), (.52, .50), .05, "golden"),
    (17.583, "2028", 11.0, 1, (.80, .74), (.54, .54), (.56, .56), .05, "golden"),
    (18.667, "2029", 22.4, .7, (.92, .74), (.55, .56), (.56, .58), .03, "golden"),
    # 2. JASORAT — sovuq po'lat
    (21.625, "r05", 0, 1, (1.0, .88), (.55, .55), (.55, .55), 0, "steel"),
    (23.792, "2027", 1.0, .8, (.72, .64), (.52, .54), (.56, .56), .04, "steel"),
    (25.792, "r04", 0, 1, (.88, .66), (.50, .52), (.60, .58), .03, "steel"),
    (28.250, "2028", 1.0, 1, (.70, .66), (.45, .45), (.56, .56), .05, "steel"),
    (28.917, "r08", 0, 1, (.62, .58), (.50, .50), (.56, .56), .05, "steel"),
    (29.500, "2027", 17.4, .8, (.76, .68), (.56, .55), (.54, .52), .04, "steel"),
    (31.042, "r02", 0, 1, (.70, .62), (.55, .55), (.48, .46), .05, "steel"),
    (32.167, "2027", 21.0, .75, (.80, .70), (.46, .48), (.56, .55), .04, "steel"),
    # 3. QUVONCH — firuza
    (33.583, "2026", 13.4, .6, (1.0, .92), (.55, .56), (.52, .52), 0, "teal"),
    (36.375, "r03", 0, 1, (.72, .54), (.50, .48), (.46, .40), .03, "teal"),
    (38.792, "2027", 26.0, 1, (.56, .52), (.50, .50), (.46, .46), .05, "teal"),
    (39.500, "r07", 0, 1, (.72, .60), (.48, .48), (.54, .52), .04, "teal"),
    (40.875, "2032", 15.0, .75, (.86, .70), (.52, .52), (.56, .56), .03, "teal"),
    (44.167, "2027", 28.0, 1, (.72, .66), (.50, .50), (.52, .52), .05, "teal"),
    (45.375, "2036", 3.0, .7, (.78, .70), (.55, .56), (.60, .58), .04, "teal"),
    (47.125, "2031", 3.0, 1, (.70, .64), (.55, .55), (.62, .62), .04, "teal"),
    # 4. QADAM — tuproq rangi, musiqa cho'qqisi
    (47.875, "r10", 0, 1, (1.0, .80), (.45, .45), (.58, .62), 0, "earth"),
    (50.458, "2036", 0.0, 1, (.80, .74), (.50, .50), (.52, .52), .06, "earth"),
    (51.208, "2027", 30.0, 1, (.76, .70), (.50, .50), (.55, .55), .06, "earth"),
    (52.000, "2036", 4.4, .55, (.82, .70), (.55, .56), (.58, .56), .04, "earth"),
    (54.792, "white", 0, 1, None, None, None, 0, "earth"),
    (54.875, "2027", 33.4, 1, (.72, .66), (.50, .50), (.55, .55), .07, "earth"),
    (56.167, "white", 0, 1, None, None, None, 0, "earth"),
    (56.250, "r01", 0, 1, (.56, .50), (.48, .48), (.42, .40), .07, "earth"),
    (56.958, "white", 0, 1, None, None, None, 0, "earth"),
    (57.000, "2029", 26.4, 1, (.70, .66), (.56, .56), (.60, .60), .07, "golden"),
    (57.417, "r03", 0, 1, (.62, .58), (.50, .50), (.44, .42), .07, "teal"),
    (57.750, "2026", 20.0, 1, (.70, .64), (.50, .50), (.56, .56), .07, "steel"),
    (58.125, "r06", 0, 1, (.70, .64), (.47, .47), (.52, .52), .07, "golden"),
    (58.500, "2032", 31.0, 1, (.72, .66), (.50, .50), (.56, .56), .07, "teal"),
    (58.792, "r02", 0, 1, (.66, .60), (.55, .55), (.46, .46), .07, "earth"),
    (59.083, "2027", 36.4, .8, (.74, .66), (.50, .50), (.56, .58), .03, "amber"),
    (60.250, "r08", 0, 1, (.80, .70), (.50, .50), (.56, .55), 0, "amber"),
    (61.500, "2036", 7.6, .5, (.86, .76), (.52, .52), (.56, .54), 0, "amber"),
]
CUTS = [s[0] for s in S] + [DUR]
END_BLACK = 64.05     # epilog kadri qorayadi (musiqadagi sukunat 64.0-64.9)
FINAL_T = 64.96       # yakuniy sarlavha (musiqadagi so'nggi zarba)
WHIPS = [21.625, 33.583]          # yo'nalishli "whip" o'tishlar
BLOOMS = [12.083, 47.875]          # nur portlashi (drop)
LEAKS = [(12.083, 1.8), (47.875, 2.4), (7.833, 2.0)]

# ---------------------------------------------------------------- grades
G = {
    "amber":  dict(mix=[[1.10, .16, 0], [.06, .84, 0], [0, .10, .62]], sat=.72, exp=-.30, con=1.22,
                   sh=(.05, .025, -.01), hi=(.07, .035, -.03), fade=.012),
    "golden": dict(mix=[[1.06, .12, 0], [.03, .94, .03], [0, .08, .80]], sat=.86, exp=-.05, con=1.14,
                   sh=(-.01, .015, .035), hi=(.06, .03, -.03), fade=.01),
    "steel":  dict(mix=[[.90, .08, .02], [.02, .90, .08], [.02, .10, .98]], sat=.52, exp=-.12, con=1.16,
                   sh=(0, .015, .05), hi=(-.01, .015, .04), fade=.012),
    "teal":   dict(mix=[[.84, .10, .06], [0, .94, .10], [0, .16, 1.04]], sat=.82, exp=-.08, con=1.16,
                   sh=(-.02, .02, .05), hi=(.035, .02, 0), fade=.01),
    "earth":  dict(mix=[[1.06, .14, 0], [.06, .84, .05], [.02, .10, .70]], sat=.70, exp=-.12, con=1.20,
                   sh=(.04, .02, 0), hi=(.07, .04, -.01), fade=.012),
}


def ease(x):  # sinus in-out
    x = min(max(x, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def expo_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - 2 ** (-10 * x) if x < 1 else 1.0


def shot_at(t):
    for i in range(len(S) - 1, -1, -1):
        if t >= S[i][0]:
            return i
    return 0


# ---------------------------------------------------------------- sources
_caps = {}


@lru_cache(maxsize=64)
def vframe(name, n):
    cap = _caps.get(name)
    if cap is None:
        cap = _caps[name] = cv2.VideoCapture(os.path.join(HERE, "ish", "src", name + ".mp4"))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = max(0, min(n, total - 1))
    cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, f = cap.read()
    if not ok:
        raise RuntimeError(f"{name} kadr {n} o'qilmadi")
    return f


@lru_cache(maxsize=16)
def photo(name):
    return cv2.imread(os.path.join(HERE, "kirish", "rasm_" + name[1:] + ".jpg"))


def source_frame(name, st):
    if name.startswith("r"):
        return photo(name)
    x = st * 30.0
    a = int(math.floor(x)); f = x - a
    fa = vframe(name, a)
    if f < 0.08:
        return fa
    fb = vframe(name, a + 1)
    return cv2.addWeighted(fa, 1 - f, fb, f, 0)


def frame_shot(i, t):
    st, name, tin, speed, Hs, cxs, cys, punch, _ = S[i]
    if name in ("black", "white"):
        v = 0 if name == "black" else 255
        return np.full((H, W, 3), v, np.uint8)
    end = CUTS[i + 1]
    u = t - st
    p = ease(u / (end - st))
    img = source_frame(name, tin + u * speed)
    sh, sw = img.shape[:2]
    vh = (Hs[0] + (Hs[1] - Hs[0]) * p) * sh
    vw = vh * W / H
    if vw > sw:  # tor manbada ko'rinish kengligi chegarasi
        vw = sw; vh = vw * H / W
    cx = (cxs[0] + (cxs[1] - cxs[0]) * p) * sw
    cy = (cys[0] + (cys[1] - cys[0]) * p) * sh
    cx = min(max(cx, vw / 2), sw - vw / 2)
    cy = min(max(cy, vh / 2), sh - vh / 2)
    sc = H / vh
    sc *= 1 + punch * math.exp(-u / 0.16)     # zarbda "punch-in"
    M = np.float32([[sc, 0, W / 2 - sc * cx], [0, sc, H / 2 - sc * cy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ---------------------------------------------------------------- look
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((_xx - W / 2) / (W * .62)) ** 2 + ((_yy - H / 2) / (H * .62)) ** 2)
VIGN = (1 - 0.42 * np.clip(_r - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)
del _yy, _xx, _r


def grade(rgb, g):
    x = rgb @ np.float32(g["mix"]).T
    x *= 2 ** g["exp"]
    lum = x @ np.float32([.2126, .7152, .0722])
    x = lum[..., None] + (x - lum[..., None]) * g["sat"]
    x = np.clip(x, 0, 1.4)
    # filmik egri: kontrast + yumshoq yelka
    x = 0.5 + (x - 0.5) * g["con"]
    x = np.clip(x, 0, None)
    x = x / (1 + 0.6 * np.clip(x - 0.75, 0, None))
    lum = np.clip(x @ np.float32([.2126, .7152, .0722]), 0, 1)[..., None]
    x = x + np.float32(g["sh"]) * (1 - lum) ** 2 + np.float32(g["hi"]) * lum ** 2
    x = x * (1 - g["fade"]) + g["fade"]
    return x


TARGET = {"amber": .30, "golden": .40, "steel": .36, "teal": .37, "earth": .36}


@lru_cache(maxsize=64)
def shot_gain(i):
    """Har kadr uchun doimiy ekspozitsiya: manbalar yorug'ligi har xil, bo'lim bir tekis ko'rinsin."""
    st, name = S[i][0], S[i][1]
    if name in ("black", "white"):
        return 1.0
    t = (st + CUTS[i + 1]) / 2
    rgb = frame_shot(i, t)[::8, ::8, ::-1].astype(np.float32) / 255.0
    g = G[S[i][8]]
    m = float((grade(rgb, g) @ np.float32([.2126, .7152, .0722])).mean())
    return float(np.clip((TARGET[S[i][8]] / max(m, 1e-3)) ** 0.8, 0.62, 1.25))


def halation(x):
    small = cv2.resize(x, (W // 8, H // 8), interpolation=cv2.INTER_AREA)
    hl = np.clip(small - 0.80, 0, None)
    hl = cv2.GaussianBlur(hl, (0, 0), 6)
    hl = cv2.resize(hl, (W, H), interpolation=cv2.INTER_LINEAR)
    return x + hl * np.float32([1.0, .55, .35]) * 0.55


GRAIN = []
_rng = np.random.default_rng(7)
for _ in range(12):
    gsm = _rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    gsm = cv2.GaussianBlur(gsm, (0, 0), 0.7)
    GRAIN.append(cv2.resize(gsm, (W, H), interpolation=cv2.INTER_LINEAR))


def leak(t, t0, dur):
    """Iliq nur oqimi: diagonal bo'ylab suzuvchi yumshoq dog'."""
    u = (t - t0) / dur
    if u < 0 or u > 1:
        return None
    a = math.sin(math.pi * u) ** 1.5 * 0.30
    cx = W * (-0.1 + 1.2 * u); cy = H * (0.25 + 0.3 * u)
    small = np.zeros((H // 8, W // 8), np.float32)
    cv2.circle(small, (int(cx / 8), int(cy / 8)), int(W / 8 * 0.55), 1.0, -1)
    small = cv2.GaussianBlur(small, (0, 0), 22)
    m = cv2.resize(small, (W, H))[..., None]
    return m * np.float32([1.0, .55, .22]) * a


# ---------------------------------------------------------------- text
@lru_cache(maxsize=8)
def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def text_layer(txt, size, track, weight="Inter-Light.otf", alpha=1.0, blur=0.0):
    f = font(weight, size)
    widths = [f.getlength(ch) for ch in txt]
    tw = sum(widths) + track * size * (len(txt) - 1)
    pad = int(size * 0.8 + blur * 3)
    im = Image.new("L", (int(tw) + 2 * pad, int(size * 1.6) + 2 * pad), 0)
    d = ImageDraw.Draw(im)
    x = pad
    for ch, w in zip(txt, widths):
        d.text((x, pad), ch, font=f, fill=int(255 * alpha))
        x += w + track * size
    if blur > 0.3:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 255.0, pad, size


def put_text(x, txt, cx, cy, size, track, a, blur=0.0, weight="Inter-Light.otf", color=(1, 1, 1)):
    if a <= 0.003:
        return
    m, pad, sz = text_layer(txt, size, round(track, 3), weight, 1.0, round(blur, 1))
    h, w = m.shape
    x0 = int(cx - w / 2); y0 = int(cy - pad - sz * 0.62)
    xa, ya = max(x0, 0), max(y0, 0)
    xb, yb = min(x0 + w, W), min(y0 + h, H)
    if xb <= xa or yb <= ya:
        return
    mm = m[ya - y0:yb - y0, xa - x0:xb - x0, None] * a
    sh = cv2.GaussianBlur(mm, (0, 0), size * 0.35)
    sh = sh[..., None] if sh.ndim == 2 else sh
    x[ya:yb, xa:xb] *= 1 - 0.45 * np.clip(sh * 2.2, 0, 1)
    region = x[ya:yb, xa:xb]
    x[ya:yb, xa:xb] = region * (1 - mm) + np.float32(color) * mm


def env(t, a, b, fi=0.35, fo=0.35):
    if t < a or t > b:
        return 0.0
    return ease((t - a) / fi) * ease((b - t) / fo)


def titles(x, t):
    # namunadagi "Cinema Line / FX3" kabi: ko'z kadri yonida
    a = env(t, 3.15, 4.2, .25, .2)
    put_text(x, "KUZ", W * .16, H / 2, 30, .5, a * .9)
    put_text(x, "2026", W * .84, H / 2, 30, .5, a * .9)
    # "a film by / THOMAS GOH" o'rnida
    a = env(t, 8.3, 11.75, .6, .5)
    put_text(x, "bir kichik", W * .19, H / 2, 30, .18, a * .9)
    put_text(x, "QAHRAMON HAQIDA", W * .80, H / 2, 24, .42, a * .9, weight="Inter-Regular.otf")
    # bo'lim nomlari
    for t0, t1, word in [(12.35, 13.75, "KASHFIYOT"), (21.85, 23.65, "JASORAT"),
                         (33.85, 36.15, "QUVONCH"), (48.15, 50.30, "QADAM")]:
        a = env(t, t0, t1, .45, .35)
        if a > 0:
            k = (t - t0) / (t1 - t0)
            put_text(x, word, W / 2, H / 2, 64, .42 + .14 * k, a * .92,
                     blur=max(0, 6 * (1 - (t - t0) / .45)), weight="Inter-ExtraLight.otf")
    # epilog shiori
    a = env(t, 62.15, 63.85, .5, .45)
    put_text(x, "HAR BIR QADAM", W / 2, H / 2 - 30, 30, .45, a * .9, weight="Inter-Regular.otf")
    put_text(x, "bir kashfiyot", W / 2, H / 2 + 30, 34, .12, a * .9, weight="Inter-Light.otf")
    # yakuniy sarlavha (namunadagi logotip o'rnida)
    if t >= FINAL_T:
        u = t - FINAL_T
        a = ease(u / .5) * ease((DUR - t) / .35)
        glow = max(0.0, 1 - u / .9)
        if glow > 0:
            put_text(x, "BIRINCHI QADAMLAR", W / 2, H / 2, 56, .30, a * glow * .8, blur=14,
                     weight="Inter-Regular.otf", color=(.35, .55, 1.0))
        put_text(x, "BIRINCHI QADAMLAR", W / 2, H / 2, 56, .30, a * (1 - .6 * glow), weight="Inter-Regular.otf")
        put_text(x, "2026", W / 2, H / 2 + 74, 22, .6, a * .7 * ease((u - .35) / .5))


# ---------------------------------------------------------------- band (kino tasmasi)
def band_height(t):
    if t < 12.083:
        return BAND
    if t < 61.5:
        return BAND + (H - BAND) * expo_out((t - 12.083) / .55)
    return H - (H - BAND) * ease((t - 61.5) / 1.1)


# ---------------------------------------------------------------- frame
def render_frame(n):
    t = n / FPS
    if t >= END_BLACK and t < FINAL_T:
        return np.zeros((H, W, 3), np.uint8)
    if t >= FINAL_T:
        x = np.zeros((H, W, 3), np.float32)
        titles(x, t)
        x = halation(x) * 1.0
        x += GRAIN[n % len(GRAIN)][..., None] * 0.02
        return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)[..., ::-1]

    i = shot_at(t)
    bgr = frame_shot(i, t)
    # yo'nalishli whip o'tish
    for T in WHIPS:
        if T - .125 <= t < T + .167:
            if t < T:
                q = (t - (T - .125)) / .125; dx = -q * q * 760
            else:
                q = 1 - (t - T) / .167; dx = q * q * 760
            k = int(1 + q * 140)
            bgr = np.roll(bgr, int(dx), axis=1)
            bgr = cv2.blur(bgr, (k | 1, 1))
    rgb = bgr[..., ::-1].astype(np.float32) / 255.0
    x = grade(rgb, G[S[i][8]]) * shot_gain(i)
    x = halation(x)
    for t0, d in LEAKS:
        L = leak(t, t0, d)
        if L is not None:
            x = x + L
    for T in BLOOMS:   # drop zarbidagi nur portlashi
        if T <= t < T + .4:
            x = x + (1 - x) * 0.85 * math.exp(-(t - T) / .07)
    if S[i][1] == "white":
        x[:] = 1.0
    # oq chaqnashdan keyingi kadrda yorug'lik izi
    if i > 0 and S[i - 1][1] == "white" and S[i][1] != "white":
        x = x + (1 - x) * 0.6 * math.exp(-(t - S[i][0]) / .05)
    x *= VIGN
    x += GRAIN[n % len(GRAIN)][..., None] * 0.028
    x = np.clip(x, 0, 1)
    titles(x, t)
    # 6.25-7.83 qora pauza: oldingi kadrdan qisqa so'nish
    bh = band_height(t)
    if bh < H - 1:
        top = int(round((H - bh) / 2))
        x[:top] = 0; x[H - top:] = 0
    if t >= 63.4:  # epilog qorayadi
        x *= 1 - ease((t - 63.4) / (END_BLACK - 63.4))
    return (x * 255 + 0.5).astype(np.uint8)[..., ::-1]


def probe(times):
    out = os.path.join(HERE, "ish", "probe"); os.makedirs(out, exist_ok=True)
    for tt in times:
        n = int(round(float(tt) * FPS))
        cv2.imwrite(os.path.join(out, f"{float(tt):06.2f}.jpg"), render_frame(n), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(out)


def render():
    os.makedirs(os.path.join(HERE, "chiqish"), exist_ok=True)
    master = os.path.join(HERE, "ish", "video_only.mp4")
    N = int(math.floor(DUR * FPS))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-vf", "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p",
                            "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709",
                            "-color_trc", "bt709", "-c:v", "libx264", "-crf", "15", "-preset", "slow",
                            "-tune", "grain", master], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, fr in enumerate(pool.imap(render_frame, range(N), chunksize=6)):
            enc.stdin.write(fr.tobytes())
            if k % 120 == 0:
                print(f"{k}/{N}", flush=True)
    enc.stdin.close(); enc.wait()
    final = os.path.join(HERE, "chiqish", "Birinchi_qadamlar.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", master, "-i", REF, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart",
                    final], check=True)
    print(final)


if __name__ == "__main__":
    if sys.argv[1] == "probe":
        probe(sys.argv[2:])
    else:
        render()
