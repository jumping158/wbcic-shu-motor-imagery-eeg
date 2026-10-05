# -*- coding: utf-8 -*-
# 作用：阶段3A 全部被试 within-session（CSP+LDA，5 折分层 CV）。支持断点续跑。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' scripts\step3a_all_subjects.py
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

RES = os.path.join(ROOT, "results", "step3a")
FIG = os.path.join(ROOT, "figures")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
ACC = os.path.join(RES, "within_session_persession.csv")


def main():
    subjects = eu.list_subjects()
    done = {}
    if os.path.exists(ACC):
        with open(ACC, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                done[(r["subject"], r["session"])] = float(r["acc_mean"])
    new = not os.path.exists(ACC)
    fout = open(ACC, "a", newline="", encoding="utf-8-sig")
    w = csv.writer(fout)
    if new:
        w.writerow(["subject", "session", "acc_mean", "acc_std"]); fout.flush()
    for sub in subjects:
        for ses in eu.SESSIONS:
            if (sub, ses) in done:
                continue
            X, y = eu.load_session(sub, ses)
            Xw = eu.window(eu.bandpass(X), 0.5, 2.5)
            m, sd = eu.cv_accuracy(Xw, y, eu.make_csp_lda(4))
            done[(sub, ses)] = m
            w.writerow([sub, ses, round(m, 4), round(sd, 4)]); fout.flush()
        print(sub, flush=True)
    fout.close()

    rows = []
    for sub in subjects:
        accs = [done.get((sub, s), np.nan) for s in eu.SESSIONS]
        rows.append([sub] + [round(a, 4) for a in accs] + [round(float(np.nanmean(accs)), 4)])
    with open(os.path.join(RES, "within_session.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["subject", "ses-01", "ses-02", "ses-03", "mean"]); w.writerows(rows)
    means = np.array([r[-1] for r in rows])
    print("总体平均±标准差：%.4f ± %.4f" % (means.mean(), means.std(ddof=1)))
    print("低于60%%：%d (%.1f%%)" % (int((means < 0.6).sum()), 100 * (means < 0.6).mean()))

    order = np.argsort(means)[::-1]
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(range(len(means)), means[order], color="#4C72B0")
    ax.axhline(0.5, color="gray", ls="--", lw=1.2, label="机会水平 50%")
    ax.axhline(means.mean(), color="darkorange", lw=1.5, label="总体平均 %.3f" % means.mean())
    ax.axhline(0.6112, color="red", ls=":", lw=1.5, label="论文 CSP+SVM 61.12%")
    ax.set_xticks(range(len(means))); ax.set_xticklabels([subjects[i] for i in order], rotation=90, fontsize=6)
    ax.set_ylabel("within-session 准确率"); ax.set_ylim(0.4, 1.0)
    ax.set_title("3A：全部被试 within-session CSP+LDA（按准确率排序）")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FIG, "within_session.png"), dpi=150)


if __name__ == "__main__":
    main()
