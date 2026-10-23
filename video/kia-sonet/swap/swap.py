# -*- coding: utf-8 -*-
"""Reel ichidagi mashinani Kia Sonet (orqa ko'rinish) bilan almashtirish.

Kadrlar: 267..298 (8.9–9.95 s). Qadamlar har kadr uchun:
  1) asl mashina niqobi (qorong'i + qizil piksellar, ekran chegarasi ichida) → qobiq;
  2) asl mashina o'rni inpaint qilinadi;
  3) Sonet o'lchami/joyi asl mashina bbox'idan (yaqin kadrlarda stop-chiroq chizig'idan);
  4) rang (LAB Reinhard, 280-kadrdagi asl mashina bo'yicha), yorug'lik va xiralik
     (asl kadrdan baholanadi) moslanadi; ekran pastki/yuqori chegarasi va qora
     tasma bilan kesiladi.

    python3 swap.py FRAMES_DIR SONET_PNG OUT_DIR
"""
import sys, os, cv2, numpy as np

FR, SONET, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
A, B = 267, 298
RED_F = .336                      # Sonet stop-chiroq chizig'i balandlik ulushi
SLOPE = (839 - 904) / 550.0       # ekran qiyaligi (pastki chet: (90,904) → (640,839))

son = cv2.imread(SONET, cv2.IMREAD_UNCHANGED).astype(np.float32)
SH, SW = son.shape[:2]


def load(i):
    return cv2.imread(os.path.join(FR, '%04d.png' % i))


yy, xx = np.mgrid[0:1280, 0:720]
U = yy - SLOPE * (xx - 90)        # qiya "qator" koordinatasi
BOT = 904 - 3
TOP_LINE = 372 + (432 - 372) * (xx - 65) / 600.0


def car_mask(im):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(int)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    red = ((hsv[..., 0] < 10) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 110) & (hsv[..., 2] > 100)
    m = ((g < 150) | red).astype(np.uint8)
    m[(U > BOT) | (yy < TOP_LINE + 3)] = 0
    m[:, :70] = 0; m[:, 690:] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, l, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, 4])
    comp = (l == k).astype(np.uint8)
    ry = np.nonzero(red & (comp > 0))[0]
    hull = cv2.convexHull(cv2.findNonZero(comp))
    hm = np.zeros_like(comp); cv2.fillConvexPoly(hm, hull, 1)
    return hm, st[k][:4], (float(np.median(ry)) if len(ry) else None)


# ---- 1) geometriya: o'lchanadigan kadrlar 268..284, keyin statik ----
geo, masks = {}, {}
for i in range(268, 285):
    hm, (x, y, w, h), ry = car_mask(load(i))
    masks[i] = hm
    W = w * .96; H = W * SH / SW
    if i == 268:
        top = ry - RED_F * H                      # pastki qismi ekrandan chiqib ketgan
    else:
        top = y + h - H
    geo[i] = [x + w / 2, top, W]
# vaqt bo'yicha silliqlash (statik qismda titrashni yo'qotadi)
ks = sorted(geo)
arr = np.array([geo[k] for k in ks])
sm = arr.copy()
for j in range(1, len(ks) - 1):
    if ks[j] >= 271:
        sm[j] = (arr[j - 1] + 2 * arr[j] + arr[j + 1]) / 4
for k, v in zip(ks, sm):
    geo[k] = list(v)
stat = np.mean([geo[k] for k in range(277, 285)], axis=0)
for k in range(277, B + 1):
    geo[k] = list(stat)
# 267: o'ta yaqin kadr — eksponensial zoom ekstrapolyatsiyasi, chiroq chizig'i bo'yicha
W267 = geo[268][2] * (geo[268][2] / geo[269][2]) ** .9
geo[267] = [geo[268][0] - 10, 607 - RED_F * W267 * SH / SW, W267]
masks[267] = np.zeros((1280, 720), np.uint8); masks[267][(U <= BOT) & (yy >= TOP_LINE)] = 1
for k in range(285, B + 1):
    masks[k] = masks[284]

# ---- 2) rang: 280-kadrdagi asl mashina → Sonet (LAB o'rtacha/og'ish) ----
ref = load(280)
er = cv2.erode(masks[280], np.ones((9, 9), np.uint8)) > 0
lab_ref = cv2.cvtColor(ref, cv2.COLOR_BGR2LAB).astype(np.float32)[er]
s_rgb = son[..., :3].clip(0, 255).astype(np.uint8)
s_lab = cv2.cvtColor(s_rgb, cv2.COLOR_BGR2LAB).astype(np.float32)
sa = son[..., 3] > 200
mu_s, sd_s = s_lab[sa].mean(0), s_lab[sa].std(0)
mu_r, sd_r = lab_ref.mean(0), lab_ref.std(0)
k_sd = np.array([min(1.0, sd_r[0] / sd_s[0]) * .9 + .1, 1, 1])     # kontrastni biroz saqlaymiz
s_lab2 = (s_lab - mu_s) * k_sd + np.array([min(mu_r[0], mu_s[0]), mu_r[1] * .6 + mu_s[1] * .4, mu_r[2] * .6 + mu_s[2] * .4])
print('L ref %.0f sonet %.0f' % (mu_r[0], mu_s[0]))
son_rgb = cv2.cvtColor(s_lab2.clip(0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
# chiroqlarni yorqin qoldiramiz (asl videoda ham yonib turibdi)
hsv_s = cv2.cvtColor(s_rgb, cv2.COLOR_BGR2HSV)
redm = (((hsv_s[..., 0] < 10) | (hsv_s[..., 0] > 170)) & (hsv_s[..., 1] > 100)).astype(np.float32)
redm = cv2.GaussianBlur(redm, (0, 0), 3)[..., None]
son_rgb = son_rgb * (1 - redm) + son[..., :3] * redm
son_a = son[..., 3] / 255.0

# ---- 3) yorug'lik va xiralik har kadr uchun (284 ga nisbatan) ----
REG = (slice(600, 880), slice(250, 590))
base = cv2.cvtColor(load(284), cv2.COLOR_BGR2GRAY).astype(np.float32)


def band_rows(g):
    """Qora tasmalar orasidagi yorug' qism: har ustunda yorug' oraliq, chetlari to'g'ri chiziq."""
    xs, tops, bots = [], [], []
    for x in list(range(110, 255, 5)) + list(range(590, 645, 5)):   # mashina ustunlari chetda qoladi
        col = np.r_[0, (g[380:940, x] > 55).astype(int), 0]
        d = np.diff(col); st, en = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
        if len(st):
            k = np.argmax(en - st)                       # eng uzun yorug' oraliq
            if en[k] - st[k] > 10:
                xs.append(x); tops.append(380 + st[k]); bots.append(380 + en[k] - 1)
    pt, pb = np.polyfit(xs, tops, 1), np.polyfit(xs, bots, 1)
    yt, yb = np.polyval(pt, xx), np.polyval(pb, xx)
    clip = ((yy >= yt + 1) & (yy <= yb - 1)).astype(np.float32)
    return cv2.GaussianBlur(clip, (0, 0), 1.0)


def text_layer(im):
    """Sayt matni (oq yozuvlar mashina ustida): rangli top-hat — qo'shiladigan yorug'lik qatlami."""
    ker = np.ones((17, 17), np.uint8)
    th = np.dstack([cv2.morphologyEx(im[..., c], cv2.MORPH_TOPHAT, ker) for c in range(3)]).astype(np.float32)
    w = np.clip((th.mean(2) - 8) / 14, 0, 1)
    return th * w[..., None]


def est_blur(i):
    if i <= 284:
        return 0.0, 1.0
    g = cv2.cvtColor(load(i), cv2.COLOR_BGR2GRAY).astype(np.float32)
    a, b = base[REG], g[REG]
    keep = b > 40
    best = (1e18, 0, 1)
    for s in np.arange(0, 16, .5):
        c = cv2.GaussianBlur(a, (0, 0), s) if s > 0 else a
        gain = (b[keep] * c[keep]).sum() / max(1, (c[keep] ** 2).sum())
        e = ((c * gain - b)[keep] ** 2).mean()
        if e < best[0]:
            best = (e, s, gain)
    return best[1], best[2]


for i in range(A, B + 1):
    im = load(i)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sig, gain = est_blur(i)
    # asl mashinani olib tashlash
    dil = 7 + int(sig * 1.5)
    m = cv2.dilate(masks[i], np.ones((dil * 2 + 1, dil * 2 + 1), np.uint8))
    clean = cv2.inpaint(im, m * 255, 9, cv2.INPAINT_TELEA)
    if sig > 0:
        clean = cv2.GaussianBlur(clean, (0, 0), max(.5, sig * .6)) * (m[..., None] > 0) + clean * (m[..., None] == 0)
        clean = clean.astype(np.uint8)
    # Sonet
    cx, top, W = geo[i]
    H = W * SH / SW
    # yerga tushgan soya (inpaint izini ham yopadi)
    sh = np.zeros((1280, 720), np.float32)
    cv2.ellipse(sh, (int(cx), int(top + H * .93)), (int(W * .47), int(W * .07)), 0, 0, 360, 1, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 4 + W * .02 + sig)[..., None] * .55 * (U <= BOT)[..., None]
    if i >= 288:
        sh *= band_rows(g)[..., None]
    clean = (clean.astype(np.float32) * (1 - sh) + np.array([40, 38, 36], np.float32) * sh).astype(np.uint8)
    M = np.float32([[W / SW, 0, cx - W / 2], [0, H / SH, top]])
    rgb = cv2.warpAffine(son_rgb, M, (720, 1280), flags=cv2.INTER_AREA if W < SW else cv2.INTER_CUBIC)
    al = cv2.warpAffine(son_a.astype(np.float32), M, (720, 1280), flags=cv2.INTER_LINEAR)
    s = 1.3 + sig + {267: 3.0, 268: 1.6, 269: .8}.get(i, 0)   # zoom-out kadrlarida harakat xiraligi
    rgb = cv2.GaussianBlur(rgb * al[..., None], (0, 0), s)
    al = cv2.GaussianBlur(al, (0, 0), s)
    rgb = rgb / np.maximum(al[..., None], 1e-3)
    rgb = (rgb * .86 + 22) * gain          # ekran: qora nuqtalar ko'tarilgan, kontrast past
    # kesish: ekran chegaralari va qora tasma
    clip = ((U <= BOT + 2) & (yy >= TOP_LINE) & (xx >= 68) & (xx <= 688)).astype(np.float32)
    clip = cv2.GaussianBlur(clip, (0, 0), 1)
    if i >= 288:
        br = band_rows(g)
        clip *= br
        clean = (clean * br[..., None] + im * (1 - br[..., None])).astype(np.uint8)
    al = (al * clip)[..., None]
    # yengil plyonka shovqini (asl video tekstura)
    rng = np.random.default_rng(i)
    rgb += rng.normal(0, 2.2, rgb.shape)
    out = clean.astype(np.float32) * (1 - al) + rgb * al
    if i >= 286:                               # sayt yozuvlari mashina ustida qoladi
        out += text_layer(im) * ((al > .02) & (yy[..., None] < 668))   # yozuv qatori 600–665
    cv2.imwrite(os.path.join(OUT, '%04d.png' % i), out.clip(0, 255).astype(np.uint8))
    print(i, 'blur %.1f gain %.2f' % (sig, gain), [round(v) for v in geo[i]], flush=True)
