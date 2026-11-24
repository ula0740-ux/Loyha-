"""Cut the two DOST vans out of the slide-9 photo (assets/dost_vans.jpg) with OpenCV GrabCut (classical, offline),
and build a clean background plate by inpainting where they stood. Output: assets/van_a.png, van_b.png (RGBA, cropped,
with their offsets in assets/vans.json) and assets/dost_plate.jpg. Run: python3 -I build/cut_vans.py assets"""
import json, sys
from pathlib import Path
import cv2, numpy as np

A = Path(sys.argv[1]); img = cv2.imread(str(A / 'dost_vans.jpg')); H, W = img.shape[:2]
VANS = {'van_a': (636, 292, 600, 432), 'van_b': (1214, 280, 446, 450)}   # x, y, w, h (generous boxes)
masks, meta = {}, {}
for name, (x, y, w, h) in VANS.items():
    m = np.zeros((H, W), np.uint8); bg = np.zeros((1, 65), np.float64); fg = np.zeros((1, 65), np.float64)
    cv2.grabCut(img, m, (x, y, w, h), bg, fg, 8, cv2.GC_INIT_WITH_RECT)
    fgm = np.where((m == 1) | (m == 3), 255, 0).astype(np.uint8)
    # keep the largest component, close small holes (windows), cut the floor reflection below the tyres
    n, lab, st, _ = cv2.connectedComponentsWithStats(fgm)
    k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); fgm = np.where(lab == k, 255, 0).astype(np.uint8)
    fgm = cv2.morphologyEx(fgm, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    cnts, _ = cv2.findContours(fgm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); fgm[:] = 0
    cv2.drawContours(fgm, cnts, -1, 255, -1)
    masks[name] = fgm
for name, (x, y, w, h) in VANS.items():
    m = masks[name].copy()
    if name == 'van_a': m[masks['van_b'] > 0] = 0      # van B is in front where they touch
    soft = cv2.GaussianBlur(m, (5, 5), 0)
    ys, xs = np.where(m > 0); x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([img[y0:y1, x0:x1], soft[y0:y1, x0:x1]])
    cv2.imwrite(str(A / f'{name}.png'), rgba)
    meta[name] = {'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'h': int(y1 - y0), 'W': W, 'H': H}
# clean plate: the vans AND their floor reflections are removed (the film draws its own reflection under the moving
# cut-outs). Each row inside the region is filled by interpolating between the pixels just left and right of it
# (the showroom's walls and floor run in horizontal bands), then softened and given a little grain back.
union = cv2.dilate(np.maximum(masks['van_a'], masks['van_b']), np.ones((41, 41), np.uint8))
ys, xs = np.where(union > 0); y_top, x_l, x_r = ys.min(), max(0, xs.min() - 10), min(W - 1, xs.max() + 12)
region = np.zeros((H, W), np.uint8); region[y_top:, x_l:x_r] = 0
for y in range(y_top, H):                        # vans plus everything below them (reflections) down to the bottom
    row = union[y] > 0 if y < ys.max() else np.ones(W, bool)
    if y >= ys.max() - 60: row = np.zeros(W, bool); row[x_l:x_r] = True
    region[y][row] = 255
region[:, :x_l] = 0; region[:, x_r:] = 0
fill = img.astype(np.float32).copy()
for y in range(H):
    xsr = np.where(region[y] > 0)[0]
    if not len(xsr): continue
    a, b = max(0, xsr.min() - 6), min(W - 1, xsr.max() + 6)
    ca, cb = img[y, max(0, a - 8):a + 1].mean(0), img[y, b:min(W, b + 9)].mean(0)
    k = np.linspace(0, 1, b - a + 1)[:, None]
    fill[y, a:b + 1] = ca * (1 - k) + cb * k
fill = cv2.GaussianBlur(fill, (0, 0), sigmaX=12, sigmaY=3)
noise = np.random.default_rng(3).normal(0, 3.0, fill.shape).astype(np.float32)
alpha = cv2.GaussianBlur(region, (41, 41), 0)[..., None] / 255.0
plate = np.clip(img * (1 - alpha) + (fill + noise) * alpha, 0, 255).astype(np.uint8)
cv2.imwrite(str(A / 'dost_plate.jpg'), plate, [cv2.IMWRITE_JPEG_QUALITY, 90])
(A / 'vans.json').write_text(json.dumps(meta, indent=1)); print(meta)
# the left third of the source picture carries the slide's own UI frames: crop it away for the film plate
CROP = (600, 100, 1672, 800)   # x0, y0, x1, y1 in source pixels
x0, y0, x1, y1 = CROP
cv2.imwrite(str(A / 'dost_plate_crop.jpg'), plate[y0:y1, x0:x1], [cv2.IMWRITE_JPEG_QUALITY, 90])
meta['crop'] = {'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
(A / 'vans.json').write_text(json.dumps(meta, indent=1)); print('crop', CROP)
