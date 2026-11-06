"""Siqilgan (352x640) videolarni Real-ESRGAN (realesr-general-x4v3) bilan 4x kattalashtirish.

Faqat montajda ishlatiladigan kadrlar ishlanadi: ish/sr/<IMG>/<kadr>.png (1080x1920).
montaj.py bu fayllar bo'lsa, ularni oddiy kattalashtirilgan kadr o'rniga oladi.

  python3 sr_onnx.py   # .pth -> .onnx (bir marta)
  python3 sr.py        # onnxruntime, CPU
"""
import math, os, subprocess, sys

import cv2
import numpy as np
import onnxruntime as ort

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import montaj  # noqa: E402

LOWRES = ["2026", "2027", "2028", "2029", "2032"]


def needed_frames():
    need = {n: set() for n in LOWRES}
    for i, s in enumerate(montaj.S):
        st, name, tin, speed = s[:4]
        if name not in need:
            continue
        dur = montaj.CUTS[i + 1] - st
        a = int(math.floor(tin * 30)) - 1
        b = int(math.ceil((tin + dur * speed) * 30)) + 2
        need[name].update(range(max(a, 0), b))
    return need


def frames_of(name):
    """Asl MOV kadrlari (aylantirish qo'llangan), 30 fps ga moslangan, ish/src bilan bir xil indeks."""
    src = os.path.join(HERE, "kirish", f"IMG_{name}.MOV")
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True)
    w, h = map(int, p.stdout.strip().split(","))
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-an", "-r", "30", "-f", "rawvideo",
                             "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    k = 0
    while True:
        buf = proc.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        yield k, np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        k += 1


def main():
    net = ort.InferenceSession(os.path.join(HERE, "ish", "models", "realesr-general-x4v3.onnx"),
                               providers=["CPUExecutionProvider"])
    need = needed_frames()
    total = sum(len(v) for v in need.values())
    done = 0
    for name in LOWRES:
        out = os.path.join(HERE, "ish", "sr", name)
        os.makedirs(out, exist_ok=True)
        for k, fr in frames_of(name):
            if k not in need[name]:
                continue
            path = os.path.join(out, f"{k:05d}.png")
            done += 1
            if os.path.exists(path):
                continue
            x = np.ascontiguousarray(fr[..., ::-1].astype(np.float32).transpose(2, 0, 1)[None] / 255)
            y = np.clip(net.run(None, {"input": x})[0][0].transpose(1, 2, 0), 0, 1)
            y = (y[..., ::-1] * 255 + 0.5).astype(np.uint8)
            y = cv2.resize(y, (montaj.W, montaj.H), interpolation=cv2.INTER_AREA)
            cv2.imwrite(path, y, [cv2.IMWRITE_PNG_COMPRESSION, 1])
            if done % 50 == 0:
                print(f"{done}/{total}", flush=True)
    print("tayyor", total)


if __name__ == "__main__":
    main()
