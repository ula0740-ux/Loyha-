"""v4 opening: dark concrete wall texture (procedural, no stock image) for the logo reveal that recreates the user's
reference video opening (src/user_ref_adm.mp4 0-7 s: chrome 3D logo on a dark rough wall). -> assets/concrete.jpg"""
import numpy as np
from PIL import Image, ImageFilter
rng = np.random.default_rng(7)
W, H = 1920, 1080
def octave(scale):
    n = rng.random((H // scale + 2, W // scale + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((W + 2 * scale, H + 2 * scale), Image.BICUBIC)
    return np.asarray(im, np.float32)[:H, :W] / 255
base = sum(octave(s) * w for s, w in [(240, .12), (96, .14), (32, .2), (8, .24), (2, .3)])
pores = (rng.random((H, W)) > .9975).astype(np.float32)
pores = np.asarray(Image.fromarray((pores * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
v = 22 + 26 * (base - base.mean()) / base.std() * .35 + 18 * base - 40 * pores
v = np.clip(v, 4, 70)
rgb = np.stack([v * 1.0, v * 1.0, v * 1.06], -1).astype(np.uint8)
Image.fromarray(rgb).save('assets/concrete.jpg', quality=88)
print('assets/concrete.jpg', float(v.mean()))
