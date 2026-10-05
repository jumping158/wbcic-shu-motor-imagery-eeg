# -*- coding: utf-8 -*-
# 作用：阶段3C 滤波器组 CSP（FBCSP）。8 频带各 CSP(4,log) + 互信息选特征 + LDA；与 3A 配对检验。
#       整条流程放进 Pipeline，折内拟合防泄漏。支持断点续跑。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' scripts\step3c_fbcsp.py
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
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from scipy.stats import wilcoxon

RES = os.path.join(ROOT, "results", "step3c")
FIG = os.path.join(ROOT, "figures")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
BANDS = [(4, 8), (8, 12), (12, 16), (16, 20), (20, 24), (24, 28), (28, 32), (32, 40)]
ACC = os.path.join(RES, "fbcsp_persession.csv")


def _mi(X, y):
    return mutual_info_classif(X, y, random_state=42)


class FilterBankCSP(BaseEstimator, TransformerMixin):
    def __init__(self, n_components=4):
        self.n_components = n_components

    def fit(self, X, y):
        self.csp_ = [CSP(n_components=self.n_components, reg=None, log=True).fit(X[:, k], y)
                     for k in range(X.shape[1])]
        return self

    def transform(self, X):
        return np.hstack([c.transform(X[:, k]) for k, c in enumerate(self.csp_)])


def build_pipe(k=8):
    return make_pipeline(FilterBankCSP(), SelectKBest(score_func=_mi, k=k), LinearDiscriminantAnalysis())


def load_bands(sub, ses):
    X, y = eu.load_session(sub, ses)
    Xb = np.stack([eu.window(eu.bandpass(X, lo, hi), 0.5, 2.5) for (lo, hi) in BANDS], axis=1)
    return Xb, y


def main():
    subjects = eu.list_subjects()
    done = set()
    if os.path.exists(ACC):
        with open(ACC, newline="", encoding="utf-8-sig") as f:
            done = {(r["subject"], r["session"]) for r in csv.DictReader(f)}
    new = not os.path.exists(ACC)
    fout = open(ACC, "a", newline="", encoding="utf-8-sig")
    w = csv.writer(fout)
    if new:
        w.writerow(["subject", "session", "acc_mean", "acc_std"]); fout.flush()
    for sub in subjects:
        for ses in eu.SESSIONS:
            if (sub, ses) in done:
                continue
            Xb, y = load_bands(sub, ses)
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            s = cross_val_score(build_pipe(), Xb, y, cv=cv, n_jobs=1)
            w.writerow([sub, ses, round(float(s.mean()), 4), round(float(s.std()), 4)]); fout.flush()
        print(sub, flush=True)
    fout.close()

    per = {}
    with open(ACC, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            per.setdefault(r["subject"], []).append(float(r["acc_mean"]))
    fb = {k: float(np.mean(v)) for k, v in per.items()}
    cp = {}
    with open(os.path.join(ROOT, "results", "step3a", "within_session.csv"), newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            cp[r["subject"]] = float(r["mean"])
    subs = sorted(set(fb) & set(cp))
    a = np.array([cp[s] for s in subs]); b = np.array([fb[s] for s in subs])
    with open(os.path.join(RES, "fbcsp_vs_csp.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["subject", "csp_lda", "fbcsp_lda", "diff"])
        for i, s in enumerate(subs):
            w.writerow([s, round(a[i], 4), round(b[i], 4), round(b[i] - a[i], 4)])
    stat, p = wilcoxon(a, b)
    print("CSP=%.4f FBCSP=%.4f wilcoxon p=%.5f" % (a.mean(), b.mean(), p))

    fig, ax = plt.subplots(figsize=(12, 5))
    for idx in np.argsort(a):
        ax.plot([0, 1], [a[idx], b[idx]], color="gray", alpha=0.5, lw=0.8)
    ax.scatter([0] * len(a), a, color="#4C72B0", s=6, zorder=3, label="CSP+LDA")
    ax.scatter([1] * len(b), b, color="#DD8452", s=6, zorder=3, label="FBCSP+LDA")
    ax.axhline(0.5, color="gray", ls="--", lw=1.1, label="机会水平 50%")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["CSP+LDA\n(3A)", "FBCSP+LDA\n(3C)"])
    ax.set_ylabel("within-session 准确率"); ax.set_ylim(0.3, 1.0)
    ax.set_title("3C：每名被试 CSP vs FBCSP（配对连线），Wilcoxon p=%.3g" % p)
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FIG, "fbcsp_vs_csp.png"), dpi=150)


if __name__ == "__main__":
    main()
