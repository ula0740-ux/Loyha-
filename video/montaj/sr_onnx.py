"""realesr-general-x4v3.pth -> ONNX (torchsiz). Real-ESRGAN SRVGGNetCompact arxitekturasi.

  python3 sr_onnx.py   ->  ish/models/realesr-general-x4v3.onnx
"""
import collections, os, pickle, zipfile

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper

HERE = os.path.dirname(os.path.abspath(__file__))
PTH = os.path.join(HERE, "ish", "models", "realesr-general-x4v3.pth")
OUT = os.path.join(HERE, "ish", "models", "realesr-general-x4v3.onnx")


def load_pth(path):
    z = zipfile.ZipFile(path)
    root = z.namelist()[0].split("/")[0]

    class Storage:
        def __init__(self, key, dtype):
            self.key, self.dtype = key, dtype

    def rebuild(storage, offset, size, stride, *args):
        raw = np.frombuffer(z.read(f"{root}/data/{storage.key}"), storage.dtype)
        return np.lib.stride_tricks.as_strided(
            raw[offset:], shape=size, strides=[s * raw.itemsize for s in stride]).copy()

    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if name == "_rebuild_tensor_v2":
                return rebuild
            if name == "FloatStorage":
                return np.float32
            if mod == "collections" and name == "OrderedDict":
                return collections.OrderedDict
            raise pickle.UnpicklingError(f"{mod}.{name}")

        def persistent_load(self, pid):
            _, dtype, key, _, _ = pid
            return Storage(key, dtype)

    return U(z.open(f"{root}/data.pkl")).load()


def main():
    sd = load_pth(PTH)
    sd = sd.get("params", sd)
    keys = sorted({int(k.split(".")[1]) for k in sd})
    nodes, inits = [], []
    cur = "input"
    for idx in keys:
        w = sd[f"body.{idx}.weight"]
        if w.ndim == 4:
            b = sd[f"body.{idx}.bias"]
            inits += [numpy_helper.from_array(w, f"w{idx}"), numpy_helper.from_array(b, f"b{idx}")]
            nodes.append(helper.make_node("Conv", [cur, f"w{idx}", f"b{idx}"], [f"c{idx}"], pads=[1, 1, 1, 1]))
            cur = f"c{idx}"
        else:  # PReLU: kanal bo'yicha qiyalik
            inits.append(numpy_helper.from_array(w.reshape(-1, 1, 1), f"a{idx}"))
            nodes.append(helper.make_node("PRelu", [cur, f"a{idx}"], [f"p{idx}"]))
            cur = f"p{idx}"
    nodes.append(helper.make_node("DepthToSpace", [cur], ["ps"], blocksize=4, mode="CRD"))
    inits.append(numpy_helper.from_array(np.array([1, 1, 4, 4], np.float32), "scales"))
    nodes.append(helper.make_node("Resize", ["input", "", "scales"], ["up"], mode="nearest"))
    nodes.append(helper.make_node("Add", ["ps", "up"], ["output"]))
    g = helper.make_graph(nodes, "srvgg",
                          [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, None, None])],
                          [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 3, None, None])], inits)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 13)], ir_version=8)
    onnx.checker.check_model(m)
    onnx.save(m, OUT)
    print(OUT, len(keys), "qatlam")


if __name__ == "__main__":
    main()
