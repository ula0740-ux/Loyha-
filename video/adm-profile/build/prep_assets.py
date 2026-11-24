"""Extract and polish the visuals used by film.html from the source deck (treated as untrusted data).
Run:  python3 -I build/prep_assets.py src/ADM_Global_Company_Profile_UZB.pptx assets
Nothing from the deck is executed; only image blobs are read (python-pptx + Pillow)."""
import io, json, sys, zipfile
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
from pptx import Presentation

src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
z = zipfile.ZipFile(src)
def media(name): return Image.open(io.BytesIO(z.read('ppt/media/' + name)))
def save_jpg(im, name, q=88): im.convert('RGB').save(out / name, quality=q, optimize=True)
def up(im, f): return im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)

# full-bleed photos (slides 1, 3, 4, 7, 9, 12)
for n, f in [('hero_factory.jpg', 'image33.jpeg'), ('dost_car.jpg', 'image34.jpeg'), ('goals_bg.jpg', 'image45.jpeg'),
             ('dost_vans.jpg', 'image109.jpeg'), ('eco_bg.jpg', 'image144.jpeg')]:
    save_jpg(media(f), n)
# slide 5: aerial site plan, cropped from the slide picture (deck callout boxes left out), upscaled 2x
aer = media('image47.jpeg').crop((450, 276, 1548, 753))
aer = up(aer, 2).filter(ImageFilter.UnsharpMask(2, 60, 2)); save_jpg(ImageEnhance.Contrast(aer).enhance(1.05), 'aerial.jpg', 90)
# slide 6 / 7 3D maps (RGBA), upscaled 2x
up(media('image48.png'), 2).filter(ImageFilter.UnsharpMask(2, 50, 2)).save(out / 'map_geo.png', optimize=True)
up(media('image78.png'), 2).filter(ImageFilter.UnsharpMask(2, 50, 2)).save(out / 'map_logi.png', optimize=True)
media('image46.png').save(out / 'goals_bars.png', optimize=True)
# slide 10: R&D centre building (top-right photo of the slide header)
rd = media('image114.jpeg'); save_jpg(up(rd.crop((1030, 0, 1500, 150)), 2.4), 'rnd_building.jpg')
# ADM logo (vector)
(out / 'adm_logo.svg').write_bytes(z.read('ppt/media/image70.svg'))

# pictures with captions: slide 8 (cars), slide 9 (van types), slide 11 (R&D steps)
prs = Presentation(src); info = {}
def shapes(sl):
    for sh in sl.shapes:
        if sh.shape_type == 6: yield from sh.shapes
        else: yield sh
for si in (8, 9, 11):
    sl = prs.slides[si - 1]; pics, labels = [], []
    for sh in shapes(sl):
        if sh.shape_type == 13 and sh.width < prs.slide_width * .5:
            try: pics.append((sh, sh.image.blob, sh.image.ext))
            except Exception: pass
        elif sh.has_text_frame and sh.text_frame.text.strip():
            labels.append((sh, ' '.join(sh.text_frame.text.split())))
    items = []
    for k, (sh, blob, ext) in enumerate(pics):
        cx, bot = sh.left + sh.width / 2, sh.top + sh.height
        cand = [(abs(l.left + l.width / 2 - cx) + abs(l.top - bot) * 2, t) for l, t in labels if l.top > sh.top + sh.height * .4 and l.top - bot < 40 * 12700]
        name = min(cand)[1] if cand else ''
        fn = f's{si}_{k:02d}.{"png" if ext == "png" else "jpg"}'
        im = Image.open(io.BytesIO(blob))
        im.thumbnail((900, 900))
        if ext == 'png': im.save(out / fn, optimize=True)
        else: save_jpg(im, fn)
        items.append({'file': fn, 'label': name, 'x': sh.left / 12700, 'y': sh.top / 12700, 'w': sh.width / 12700, 'h': sh.height / 12700})
    info[f'slide{si}'] = items
(out / 'pictures.json').write_text(json.dumps(info, ensure_ascii=False, indent=1))
print('ok', len(list(out.iterdir())), 'files')
