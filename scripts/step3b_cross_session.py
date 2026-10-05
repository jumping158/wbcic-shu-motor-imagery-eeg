# -*- coding: utf-8 -*-
# 作用：阶段3B 跨天迁移（第1天训练→第2/3天测试；及 +目标前20%适应）。支持断点续跑。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' scripts\step3b_cross_session.py
import os
import sys
import csv
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import eeg_utils as eu

import mne
mne.set_log_level("ERROR")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

RES = os.path.join(ROOT, "results", "step3b")
FIG = os.path.join(ROOT, "figures")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
CSV = os.path.join(RES, "cross_session.csv")


def prep(sub, ses):
    X, y = eu.load_session(sub, ses)
    return eu.window(eu.bandpass(X), 0.5, 2.5), y


def fit_score(Xtr, ytr, Xte, yte):
    clf = eu.make_csp_lda(4)
    clf.fit(Xtr, ytr)
    return float(clf.score(Xte, yte))


def main():
    subjects = eu.list_subjects()
    done = set()
    if os.path.exists(CSV):
        with open(CSV, newline="", encoding="utf-8-sig") as f:
            done = {r["subject"] for r in csv.DictReader(f)}
    new = not os.path.exists(CSV)
    fout = open(CSV, "a", newline="", encoding="utf-8-sig")
    w = csv.writer(fout)
    cols = ["subject", "direct_12", "direct_13", "direct_mean", "adapt_12", "adapt_13", "adapt_mean"]
    if new:
        w.writerow(cols); fout.flush()
    for sub in subjects:
        if sub in done:
            continue
        X1, y1 = prep(sub, "ses-01")
        d, a = [], []
        for tgt in ["ses-02", "ses-03"]:
            Xt, yt = prep(sub, tgt)
            d.append(fit_score(X1, y1, Xt, yt))
            n20 = int(0.2 * len(yt))
            Xtr = np.concatenate([X1, Xt[:n20]]); ytr = np.concatenate([y1, yt[:n20]])
            a.append(fit_score(Xtr, ytr, Xt[n20:], yt[n20:]))
        w.writerow([sub, round(d[0], 4), round(d[1], 4), round(np.mean(d), 4),
                    round(a[0], 4), round(a[1], 4), round(np.mean(a), 4)]); fout.flush()
        print(sub, flush=True)
    fout.close()

    with open(CSV, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    dmean = np.array([float(r["direct_mean"]) for r in rows])
    amean = np.array([float(r["adapt_mean"]) for r in rows])
    within = None
    p = os.path.join(ROOT, "results", "step3a", "within_session.csv")
    if os.path.exists(p):
        with open(p, newline="", encoding="utf-8-sig") as f:
            within = float(np.mean([float(r["mean"]) for r in csv.DictReader(f)]))
    print("within=%.4f direct=%.4f adapt=%.4f" % (within, dmean.mean(), amean.mean()))

    labels = ([("同一次采集内\n(3A)", within)] if within else []) + \
             [("跨天直接迁移", dmean.mean()), ("跨天+少量适应", amean.mean())]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar([l for l, _ in labels], [v for _, v in labels], color=["#4C72B0", "#DD8452", "#55A868"][:len(labels)])
    ax.axhline(0.5, color="gray", ls="--", lw=1.2, label="机会水平 50%")
    ax.axhline(0.6112, color="red", ls=":", lw=1.2, label="论文 CSP+SVM 61.12%")
    for i, (_, v) in enumerate(labels):
        ax.text(i, v + 0.01, "%.3f" % v, ha="center")
    ax.set_ylabel("平均准确率"); ax.set_ylim(0.4, 0.9)
    ax.set_title("3B：同一次采集内 vs 跨天直接迁移 vs 跨天+少量适应")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FIG, "cross_session.png"), dpi=150)


if __name__ == "__main__":
    main()
