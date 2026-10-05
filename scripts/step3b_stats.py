# -*- coding: utf-8 -*-
# 作用：阶段3B 补充统计与检查。
#   1) Wilcoxon 符号秩检验（51 名被试配对）：适应 vs 直接迁移、适应 vs 同一次采集内、直接 vs 同一次采集内；
#   2) 抽查"目标采集前 20% 试次"（前 40 个）里左右手是否平衡。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' step3b_stats.py
import os
import csv
import numpy as np
from scipy.stats import wilcoxon

import sys
ROOT = r"D:\eeg-project"
sys.path.insert(0, ROOT)
from src import eeg_utils as eu

S3B = os.path.join(ROOT, "results", "step3b")
S3A = os.path.join(ROOT, "results", "step3a")
OUT = os.path.join(S3B, "stats_tests.txt")

# 读取 3B
rows = list(csv.DictReader(open(os.path.join(S3B, "cross_session.csv"), encoding="utf-8-sig")))
subs = [r["subject"] for r in rows]
direct = np.array([float(r["direct_mean"]) for r in rows])
adapt = np.array([float(r["adapt_mean"]) for r in rows])
# 读取 3A within
cp = {}
for r in csv.DictReader(open(os.path.join(S3A, "within_session.csv"), encoding="utf-8-sig")):
    cp[r["subject"]] = float(r["mean"])
within = np.array([cp[s] for s in subs])

lines = []
def log(s=""):
    print(s); lines.append(str(s))

log("=" * 64)
log("阶段3B 统计检验（n=%d，Wilcoxon 符号秩，双尾）" % len(subs))
log("=" * 64)
log("均值：within=%.4f  direct=%.4f  adapt=%.4f" % (within.mean(), direct.mean(), adapt.mean()))
log("")
for name, x, y in [("adapt vs direct", adapt, direct),
                   ("adapt vs within", adapt, within),
                   ("direct vs within", direct, within)]:
    stat, p = wilcoxon(x, y)
    log("  %-18s  stat=%.1f  p=%.5f  %s" % (name, stat, p, "显著(p<0.05)" if p < 0.05 else "不显著"))
log("")
log("注意：adapt(%.4f) 仍低于 within(%.4f)，差值 %.4f。" % (adapt.mean(), within.mean(), within.mean() - adapt.mean()))

# 抽查前 20% 试次左右手平衡
log("")
log("=" * 64)
log("抽查：目标采集前 20% 试次（前 40 个）的左右手计数")
log("=" * 64)
bad = []
counts = []
for sub in subs:
    for tgt in ["ses-02", "ses-03"]:
        mat = __import__("scipy.io", fromlist=["loadmat"]).loadmat(
            os.path.join(eu.DATA_DIR, "%s_%s_task-motorimagery_eeg.mat" % (sub, tgt)))
        y = np.ravel(mat["labels"]).astype(int)[:40]
        nL = int((y == 1).sum()); nR = int((y == 2).sum())
        counts.append((nL, nR))
        if abs(nL - nR) > 8:   # 偏差超过 8 个即视为偏斜
            bad.append((sub, tgt, nL, nR))
nL_all = np.array([c[0] for c in counts])
log("共检查 %d 个目标采集（51 被试 × 2 天）" % len(counts))
log("前 40 个试次中左手数：min=%d max=%d 平均=%.1f；右手=40-左手" %
    (nL_all.min(), nL_all.max(), nL_all.mean()))
log("左右差 |nL-nR|>8（即偏差>20%%）的采集数：%d" % len(bad))
for b in bad[:20]:
    log("   %s %s  L=%d R=%d" % b)
log("结论：%s" % ("前 20% 试次左右手大致平衡，无需改用分层抽取。" if not bad
                else "存在偏斜，建议改用分层抽取的 20% 并重跑 3B。"))

open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n已写", OUT)
