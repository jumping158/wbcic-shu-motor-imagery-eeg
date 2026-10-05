# -*- coding: utf-8 -*-
# 作用：单个被试(sub-001)的 within-session 分类（CSP+LDA，5 折分层交叉验证）。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' scripts\step1b_single_subject.py
import os
import sys
import csv
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import eeg_utils as eu

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

import mne
mne.set_log_level("ERROR")
from mne.decoding import CSP

DATA = eu.DATA_DIR
OUT = os.path.join(ROOT, "figures")
RES = os.path.join(ROOT, "results", "step1b")
os.makedirs(OUT, exist_ok=True)
os.makedirs(RES, exist_ok=True)

CONFIGS = {
    "band3-35_win0-4": (3.0, 35.0, 0.0, 4.0),
    "band8-30_win0.5-2.5": (8.0, 30.0, 0.5, 2.5),
}
SES = eu.SESSIONS


def main():
    rows = []
    for ses in SES:
        X, y = eu.load_session("sub-001", ses)
        for name, (lo, hi, tmin, tmax) in CONFIGS.items():
            Xw = eu.window(eu.bandpass(X, lo, hi), tmin, tmax)
            m, s = eu.cv_accuracy(Xw, y, eu.make_csp_lda(4))
            rows.append([ses, name, round(m, 4), round(s, 4)])
            print("sub-001 %s %s -> %.4f ± %.4f" % (ses, name, m, s))

    with open(os.path.join(RES, "accuracy_by_session.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["session", "config", "acc_mean", "acc_std"]); w.writerows(rows)

    names = list(CONFIGS.keys())
    x = np.arange(len(SES)); width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    for k, name in enumerate(names):
        means = [next(r[2] for r in rows if r[0] == s_ and r[1] == name) for s_ in SES]
        errs = [next(r[3] for r in rows if r[0] == s_ and r[1] == name) for s_ in SES]
        ax.bar(x + (k - 0.5) * width, means, width, yerr=errs, capsize=4, label=name,
               color=["#4C72B0", "#DD8452"][k])
    ax.axhline(0.5, color="gray", ls="--", lw=1.2, label="机会水平 50%")
    ax.axhline(0.6112, color="red", ls=":", lw=1.5, label="论文 CSP+SVM 61.12%")
    ax.set_xticks(x); ax.set_xticklabels([s_ + "" for s_ in SES])
    ax.set_ylabel("分类准确率"); ax.set_ylim(0.4, 1.0)
    ax.set_title("sub-001 within-session CSP+LDA（5 折分层交叉验证）")
    ax.legend(fontsize=8, loc="upper left"); fig.tight_layout()
    fig.savefig(os.path.join(OUT, "accuracy_by_session.png"), dpi=150)

    # CSP 空间模式（主设置）
    X, y = eu.load_session("sub-001", "ses-01")
    Xw = eu.window(eu.bandpass(X, 8, 30), 0.5, 2.5)
    info = mne.create_info(eu.CH_NAMES, sfreq=eu.FS, ch_types="eeg")
    info.set_montage(mne.channels.make_standard_montage("standard_1020"), on_missing="ignore")
    csp = CSP(n_components=4, reg=None, log=True).fit(Xw, y)
    fig2 = csp.plot_patterns(info, components=range(4), ch_type="eeg", units="AU", size=1.5, show=False)
    fig2.savefig(os.path.join(OUT, "csp_patterns_session1.png"), dpi=150)
    print("已写 figures/accuracy_by_session.png, figures/csp_patterns_session1.png")


if __name__ == "__main__":
    main()
