# -*- coding: utf-8 -*-
# 作用：阶段2 看懂信号 —— 原始 10 秒波形 / 1-40 Hz PSD / C3、C4 左右手时频图。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' scripts\step2_signal.py
import os
import sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import eeg_utils as eu

from scipy.signal import welch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

import mne
from mne.time_frequency import tfr_morlet
mne.set_log_level("ERROR")

RAW = r"D:\eeg-project\data\WBCIC-SHU2025\raw\data.bdf"
OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)
FS = eu.FS


def make_raw_snippet():
    raw = mne.io.read_raw_bdf(RAW, preload=True, verbose="ERROR")
    picks = [p for p in ["C3", "C4", "VEOU", "ECG"] if p in raw.ch_names]
    sf = raw.info["sfreq"]
    data = raw.get_data(picks=picks, start=int(60 * sf), stop=int(70 * sf))
    t = np.arange(data.shape[1]) / sf
    data = data - data.mean(axis=1, keepdims=True)
    scale = np.std(data, axis=1, keepdims=True); scale[scale == 0] = 1.0
    norm = data / scale
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, p in enumerate(picks):
        ax.plot(t, norm[i] + (len(picks) - 1 - i) * 3, lw=0.8)
    ax.set_yticks([(len(picks) - 1 - i) * 3 for i in range(len(picks))])
    ax.set_yticklabels(picks); ax.set_xlabel("时间 (s)")
    ax.set_title("原始 BDF 10 秒波形（1000 Hz，含眼电/心电，每通道已归一化）")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "raw_snippet.png"), dpi=150)


def make_psd():
    X, y = eu.load_session("sub-001", "ses-01")
    fig, ax = plt.subplots(figsize=(8, 5))
    for name in ["C3", "C4", "Oz", "Fz"]:
        ci = eu.CH_NAMES.index(name)
        f, Pxx = welch(X[:, ci, :], fs=FS, nperseg=256, axis=-1)
        m = (f >= 1) & (f <= 40)
        ax.semilogy(f[m], Pxx[:, m].mean(axis=0), label=name)
    ax.axvspan(8, 13, color="orange", alpha=0.15, label="mu (8–13 Hz)")
    ax.axvspan(13, 30, color="green", alpha=0.10, label="beta (13–30 Hz)")
    ax.set_xlabel("频率 (Hz)"); ax.set_ylabel("功率谱密度 (µV²/Hz)"); ax.set_xlim(1, 40)
    ax.set_title("功率谱（sub-001 ses-01，已处理数据，各通道跨试次平均）")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(OUT, "psd.png"), dpi=150)


def make_tfr():
    X, y = eu.load_session("sub-001", "ses-01")
    freqs = np.arange(4, 41, 2.0); n_cycles = freqs

    def cond_power(ch, cond):
        idx = np.where(y == cond)[0]
        ci = eu.CH_NAMES.index(ch)
        data = X[idx][:, ci:ci + 1, :]
        info = mne.create_info(["X"], FS, "eeg")
        ep = mne.EpochsArray(data, info, tmin=0, verbose="ERROR")
        tfr = tfr_morlet(ep, freqs=freqs, n_cycles=n_cycles, return_itc=False, average=True, verbose="ERROR")
        return tfr.data[0], tfr.times

    panels = {}; vmax = None
    for ri, ch in enumerate(["C3", "C4"]):
        for cj, (cond, cname) in enumerate([(1, "左手"), (2, "右手")]):
            power, times = cond_power(ch, cond)
            base = power.mean(axis=1, keepdims=True)
            pct = 100.0 * (power - base) / base
            panels[(ri, cj)] = (pct, times)
            v = np.percentile(np.abs(pct), 98); vmax = v if vmax is None else max(vmax, v)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey=True)
    im = None
    for ri, ch in enumerate(["C3", "C4"]):
        for cj, (cond, cname) in enumerate([(1, "左手"), (2, "右手")]):
            pct, times = panels[(ri, cj)]
            ax = axes[ri][cj]
            im = ax.imshow(pct, aspect="auto", origin="lower",
                           extent=[times[0], times[-1], freqs[0], freqs[-1]],
                           cmap="RdBu_r", vmin=-vmax, vmax=vmax)
            ax.axhline(8, color="k", ls=":", lw=0.6); ax.axhline(13, color="k", ls=":", lw=0.6)
            ax.set_title("%s · %s想象" % (ch, cname))
    for ax in axes[1]:
        ax.set_xlabel("时间 (s)")
    for ax in axes[:, 0]:
        ax.set_ylabel("频率 (Hz)")
    fig.colorbar(im, ax=axes, shrink=0.8, label="相对基线变化 (%)")
    fig.suptitle("sub-001 ses-01：C3/C4 在左右手想象下的时频图（相对整段平均的百分比变化）")
    fig.savefig(os.path.join(OUT, "tfr_C3_C4.png"), dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    make_raw_snippet(); make_psd(); make_tfr()
    print("已写 figures/raw_snippet.png, psd.png, tfr_C3_C4.png")
