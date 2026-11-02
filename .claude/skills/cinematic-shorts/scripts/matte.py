#!/usr/bin/env python3
"""Odamni fondan ajratish (segmentatsiya) — "matn odam orqasida", fon almashtirish, relight uchun.
    python3 matte.py FRAMES_DIR OUT_DIR [--model u2net_human_seg|birefnet-portrait|multiclass|selfie] [--smooth 0.6] [--feather 2]
FRAMES_DIR: prep_footage.py chiqargan f_000001.jpg ... ; OUT_DIR: m_000001.png (8-bit alfa, oq = odam).
- u2net_human_seg (rembg, ~170 MB) — standart: uzoq/to'liq bo'y kadrda ham toza, ~1 s/kadr CPU.
- birefnet-portrait (rembg, ~1 GB) — eng aniq chegara (soch), lekin sekin; yakuniy master uchun.
- multiclass / selfie (MediaPipe, 16 MB / 250 KB) — tez, faqat yaqin (portret) kadrlar uchun.
  rembg modellari birinchi ishlatishda ~/.rembg/models ga yuklanadi (pip install "rembg[cpu]").
- --smooth: kadrlararo silliqlash (0 = yo'q, 0.6 = titramaydi), --feather: chegara yumshatish px.
MediaPipe Tasks (pip install mediapipe). Modellar: ../models/*.tflite (Google, Apache-2.0)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

def arg(k, d): return type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
HERE = Path(__file__).resolve().parent.parent / 'models'

def segmenter(kind):
    global mp, vision
    import mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision
    f = HERE / ('selfie_multiclass_256x256.tflite' if kind == 'multiclass' else 'selfie_segmenter.tflite')
    opts = vision.ImageSegmenterOptions(base_options=mpt.BaseOptions(model_asset_path=str(f)),
                                        running_mode=vision.RunningMode.IMAGE, output_confidence_masks=True)
    return vision.ImageSegmenter.create_from_options(opts)

def person_alpha(seg, kind, rgb):
    res = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    cm = res.confidence_masks
    if kind == 'multiclass':  # 0 = fon; 1..5 = soch, badan, yuz, kiyim, boshqa
        return 1.0 - np.squeeze(cm[0].numpy_view())
    return np.squeeze(cm[0].numpy_view())

def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    kind, sm, fe = arg('--model', 'u2net_human_seg'), arg('--smooth', 0.6), arg('--feather', 2)
    if kind in ('multiclass', 'selfie'):
        seg = segmenter(kind); fn = lambda rgb: person_alpha(seg, kind, rgb)
    else:
        from rembg import remove, new_session
        sess = new_session(kind)
        fn = lambda rgb: np.asarray(remove(Image.fromarray(rgb), session=sess, only_mask=True), dtype=np.float32) / 255.0
    prev = None
    files = sorted(src.glob('f_*.jpg')) or sorted(src.glob('*.png')) or sorted(src.glob('*.jpg'))
    for i, f in enumerate(files):
        a = fn(np.asarray(Image.open(f).convert('RGB'))).astype(np.float32)
        if prev is not None and sm > 0: a = sm * prev + (1 - sm) * a
        prev = a
        m = Image.fromarray((np.clip((a - .15) / .7, 0, 1) * 255).astype(np.uint8))
        if fe: m = m.filter(ImageFilter.GaussianBlur(fe))
        m.save(out / ('m_' + f.stem.split('_')[-1] + '.png'))
        if i % 30 == 0: print(i, f.name, flush=True)
    print('done', len(files))

if __name__ == '__main__': main()
