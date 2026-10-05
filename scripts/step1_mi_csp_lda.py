# 第一步：在 MNE 自带的公开运动想象数据（PhysioNet EEGBCI）上跑通
# 预处理 → CSP 特征 → LDA 分类 → 交叉验证准确率。
# 运行：python step1_mi_csp_lda.py   （首次运行会自动下载约 10 MB 数据）
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
from mne.datasets import eegbci
from mne.decoding import CSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import ShuffleSplit, cross_val_score
from sklearn.pipeline import Pipeline

mne.set_log_level("WARNING")
SUBJECT = 1
RUNS = [4, 8, 12]  # 想象左手 vs 右手

# 1. 读数据
files = eegbci.load_data(SUBJECT, RUNS)
raw = mne.concatenate_raws([mne.io.read_raw_edf(f, preload=True) for f in files])
eegbci.standardize(raw)
raw.set_montage("standard_1005")
raw.annotations.rename(dict(T1="left_hand", T2="right_hand"))

# 2. 预处理：7–30 Hz 带通（覆盖 mu 和 beta 节律）
raw.filter(7.0, 30.0, skip_by_annotation="edge")

# 3. 分段：提示后 1–2 秒
epochs = mne.Epochs(raw, event_id=["left_hand", "right_hand"], tmin=-1.0, tmax=4.0,
                    picks="eeg", baseline=None, preload=True)
X = epochs.copy().crop(1.0, 2.0).get_data(copy=False)
y = epochs.events[:, -1]
print(f"试次数：{len(y)}，通道数：{X.shape[1]}")

# 4. CSP + LDA，10 次随机划分交叉验证
clf = Pipeline([("CSP", CSP(n_components=4, reg=None, log=True)),
                ("LDA", LinearDiscriminantAnalysis())])
cv = ShuffleSplit(10, test_size=0.2, random_state=42)
scores = cross_val_score(clf, X, y, cv=cv, n_jobs=1)
chance = max(np.mean(y == y[0]), 1 - np.mean(y == y[0]))
print(f"分类准确率：{scores.mean():.3f} ± {scores.std():.3f}（机会水平 {chance:.3f}）")

# 5. 画出 CSP 空间模式（看看判别信息集中在哪些脑区）
csp = CSP(n_components=4, reg=None, log=True).fit(X, y)
fig = csp.plot_patterns(epochs.info, components=range(4), ch_type="eeg", units="Patterns (AU)", size=1.5, show=False)
fig.savefig("csp_patterns.png", dpi=150)
print("已保存 csp_patterns.png")
