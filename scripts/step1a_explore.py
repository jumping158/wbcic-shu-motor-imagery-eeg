# -*- coding: utf-8 -*-
# 作用：探查 WBCIC-SHU(2025) 数据集（sub-001）的文件清单与 MAT 内部结构。
#       对每个 .mat 打印变量名、类型、形状、dtype；若有标签变量则打印类别分布。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' step1a_explore.py

import os
import numpy as np
import scipy.io as sio

DATA = r"D:\eeg-project\data\WBCIC-SHU2025"
OUT = r"D:\eeg-project\results\step1a\explore.txt"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

lines = []


def log(s=""):
    print(s)
    lines.append(str(s))


log("=" * 74)
log("WBCIC-SHU(2025) 数据探查 -- sub-001")
log("figshare: https://doi.org/10.25452/figshare.plus.22671172  (v5)")
log("=" * 74)

# ---------- 一、文件清单 ----------
log("\n[一] 文件清单（含大小，MB）")
for root, dirs, files in os.walk(DATA):
    if "code_ref_code" in root:
        continue
    for fn in sorted(files):
        fp = os.path.join(root, fn)
        rel = os.path.relpath(fp, DATA)
        log("  %10.3f MB   %s" % (os.path.getsize(fp) / 1e6, rel))

# ---------- 二、MAT 结构 ----------
log("\n[二] MAT 文件内部结构")
mats = sorted(
    f for f in os.listdir(DATA)
    if f.endswith(".mat")
)
for fn in mats:
    fp = os.path.join(DATA, fn)
    log("\n  --- %s (%.2f MB) ---" % (fn, os.path.getsize(fp) / 1e6))
    try:
        mat = sio.loadmat(fp)
        keys = [k for k in mat.keys() if not k.startswith("__")]
        log("    变量名: %s" % keys)
        for k in keys:
            v = mat[k]
            log("      %-12s type=%-10s shape=%-22s dtype=%s" %
                (k, type(v).__name__, str(getattr(v, "shape", None)), getattr(v, "dtype", None)))
            # 若像标签，打印类别分布
            if v.size <= 1000 and np.issubdtype(v.dtype, np.number):
                vals, counts = np.unique(np.ravel(v), return_counts=True)
                log("        取值分布: %s" % dict(zip(vals.tolist(), counts.tolist())))
    except NotImplementedError:
        log("    [!] 疑似 v7.3(HDF5)，改用 h5py")
        import h5py
        with h5py.File(fp, "r") as h:
            def visit(name, obj):
                if isinstance(obj, h5py.Dataset):
                    log("      %-20s shape=%s dtype=%s" % (name, obj.shape, obj.dtype))
            h.visititems(visit)
    except Exception as e:
        log("    [!] 读取失败: %s: %s" % (type(e).__name__, e))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n已写入 %s" % OUT)
