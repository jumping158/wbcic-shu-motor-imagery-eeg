# -*- coding: utf-8 -*-
"""公共工具函数：数据加载、带通滤波、CSP+LDA 评估。

用于 WBCIC-SHU(2025) 运动想象 EEG 分类项目，供 scripts/ 下各阶段脚本调用。
"""
import os
import numpy as np
import scipy.io as sio
from scipy.signal import butter, filtfilt

from mne.decoding import CSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score

# 默认路径（可在调用时覆盖）
FS = 250
SESSIONS = ["ses-01", "ses-02", "ses-03"]
DATA_DIR = r"D:\eeg-project\data\WBCIC-SHU2025\processed"

# 58 导通道名（= channels.tsv 去掉重参考电极 Pz；与作者代码 ch_names 一致）
CH_NAMES = ["Fpz", "Fp1", "Fp2", "AF3", "AF4", "AF7", "AF8", "Fz", "F1", "F2", "F3", "F4",
            "F5", "F6", "F7", "F8", "FCz", "FC1", "FC2", "FC3", "FC4", "FC5", "FC6", "FT7",
            "FT8", "Cz", "C1", "C2", "C3", "C4", "C5", "C6", "T7", "T8", "CP1", "CP2", "CP3",
            "CP4", "CP5", "CP6", "TP7", "TP8", "P3", "P4", "P5", "P6", "P7", "P8", "POz",
            "PO3", "PO4", "PO5", "PO6", "PO7", "PO8", "Oz", "O1", "O2"]


def bandpass(X, lo=8.0, hi=30.0, fs=FS):
    """沿时间轴做 4 阶 Butterworth 带通（零相位 filtfilt）。X: (..., time)。"""
    b, a = butter(4, [lo / (fs / 2), hi / (fs / 2)], btype="band")
    return filtfilt(b, a, X, axis=-1)


def window(X, tmin=0.5, tmax=2.5, fs=FS):
    """按秒截取时间窗。X: (..., time)。"""
    return X[..., int(tmin * fs):int(tmax * fs)]


def load_session(sub, ses, data_dir=DATA_DIR):
    """读取一个 session 的 processed MAT，返回 X=(n_trial, 58, 1000)、y=(n_trial,)。"""
    mat = sio.loadmat(os.path.join(data_dir, "%s_%s_task-motorimagery_eeg.mat" % (sub, ses)))
    X = mat["data"].astype(np.float64).transpose(2, 0, 1)
    y = np.ravel(mat["labels"]).astype(int)
    return X, y


def list_subjects(data_dir=DATA_DIR):
    return sorted({f.split("_")[0] for f in os.listdir(data_dir) if f.endswith(".mat")})


def make_csp_lda(n_components=4, use_log=True):
    """返回 CSP + LDA 的 sklearn Pipeline（防泄漏：CSP 只在训练折内拟合）。"""
    return make_pipeline(
        CSP(n_components=n_components, reg=None, log=use_log),
        LinearDiscriminantAnalysis(),
    )


def cv_accuracy(X, y, clf=None, n_splits=5, seed=42):
    """5 折分层交叉验证，返回 (平均准确率, 标准差)。"""
    if clf is None:
        clf = make_csp_lda()
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    scores = cross_val_score(clf, X, y, cv=cv, n_jobs=1)
    return float(scores.mean()), float(scores.std())


def within_session_accuracy(sub, ses, lo=8.0, hi=30.0, tmin=0.5, tmax=2.5,
                            n_components=4, data_dir=DATA_DIR):
    """单个 (被试, session) 的 within-session 准确率。"""
    X, y = load_session(sub, ses, data_dir)
    Xw = window(bandpass(X, lo, hi), tmin, tmax)
    return cv_accuracy(Xw, y, make_csp_lda(n_components))
