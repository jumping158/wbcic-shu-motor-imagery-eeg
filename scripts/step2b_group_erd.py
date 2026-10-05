# -*- coding: utf-8 -*-
# 作用：阶段2 补充 —— 群体水平（51 被试 × 3 天）的对侧 ERD 证据。
#   方法：运动想象 0.5–2.5 s 窗内，计算每个通道 mu(8–13)/beta(13–30) 的 log 功率；
#         用"类别对比"代替基线：diff = 右手均值 − 左手均值（逐通道）。
#   预期：C3 为负（右手想象→左半球去同步），C4 为正。在被试水平做配对检验，并报告方向一致比例。
#   输出：C3/C4 单通道统计、全脑 mu(右−左) 群体平均地形图、逐被试差值 csv。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' step2b_group_erd.py
import os
import sys
import csv
import numpy as np

ROOT = r"D:\eeg-project"
sys.path.insert(0, ROOT)
from src import eeg_utils as eu

import mne
mne.set_log_level("ERROR")
from scipy.stats import wilcoxon

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

RES = os.path.join(ROOT, "results", "step2")
FIG = os.path.join(ROOT, "figures")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
BANDS = {"mu": (8, 13), "beta": (13, 30)}


def channel_diff(sub, ses):
    """返回每个通道的 (右手−左手) log 功率，按 mu/beta 两个频段。"""
    X, y = eu.load_session(sub, ses)
    Xw = eu.window(X, 0.5, 2.5)
    out = {}
    for band, (lo, hi) in BANDS.items():
        Xf = eu.bandpass(Xw, lo, hi)
        power = np.log(np.mean(Xf ** 2, axis=-1))      # (200,58)
        out[band] = power[y == 2].mean(0) - power[y == 1].mean(0)  # (58,)
    return out


def main():
    subjects = eu.list_subjects()
    per = {b: [] for b in BANDS}
    for i, sub in enumerate(subjects, 1):
        sess = [channel_diff(sub, s) for s in eu.SESSIONS]
        for b in BANDS:
            per[b].append(np.mean([s[b] for s in sess], axis=0))   # (51,58)
        print("[%d/%d] %s" % (i, len(subjects), sub), flush=True)

    c3 = eu.CH_NAMES.index("C3"); c4 = eu.CH_NAMES.index("C4")
    lines = []
    def log(s=""):
        print(s); lines.append(str(s))

    log("=" * 64)
    log("群体水平对侧 ERD（n=%d 被试，右-左 log 功率差）" % len(subjects))
    log("=" * 64)
    for b in BANDS:
        arr = np.array(per[b])          # (51,58)
        log("\n[%s 频段]" % b)
        for name, idx, expect in [("C3", c3, "负"), ("C4", c4, "正")]:
            d = arr[:, idx]
            stat, p = wilcoxon(d)       # 对 0 的单样本 Wilcoxon
            prop = (d < 0).mean() if expect == "负" else (d > 0).mean()
            log("  %s: 均值=%+.4f  中位数=%+.4f  Wilcoxon p=%.2e  方向(%s)一致被试比例=%.1f%%"
                % (name, d.mean(), np.median(d), p, expect, 100 * prop))

    # 逐被试 csv
    with open(os.path.join(RES, "group_erd_c3c4.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["subject", "mu_C3", "mu_C4", "beta_C3", "beta_C4"])
        for i, sub in enumerate(subjects):
            w.writerow([sub, round(per["mu"][i][c3], 5), round(per["mu"][i][c4], 5),
                        round(per["beta"][i][c3], 5), round(per["beta"][i][c4], 5)])

    # 全脑地形图（mu 与 beta 的群体平均 右-左 差值）
    info = mne.create_info(eu.CH_NAMES, eu.FS, "eeg")
    info.set_montage(mne.channels.make_standard_montage("standard_1020"), on_missing="ignore")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, b in zip(axes, ["mu", "beta"]):
        m = np.mean(per[b], axis=0)
        v = np.percentile(np.abs(m), 98)
        im, _ = mne.viz.plot_topomap(m, info, axes=ax, cmap="RdBu_r", vlim=(-v, v),
                                     show=False, sensors=True, contours=4)
        ax.set_title("%s (8–13 Hz)   右−左 log 功率" % "mu" if b == "mu"
                     else "beta (13–30 Hz)   右−左 log 功率")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("群体平均（n=%d）：右手想象 − 左手想象的 mu/beta log 功率差" % len(subjects))
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "group_erd_topomap.png"), dpi=150)
    log("\n已写 group_erd_c3c4.csv / group_erd_topomap.png")

    open(os.path.join(RES, "group_erd.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
