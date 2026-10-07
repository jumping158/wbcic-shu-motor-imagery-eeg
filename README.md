# Motor Imagery EEG Classification — WBCIC-SHU (2025) 运动想象脑电分类

**中文** | [English](#english)

一个端到端的运动想象（左手/右手）脑电分类复现项目：从数据、预处理、CSP/LDA、跨天迁移，到更强的 FBCSP。
本项目用于学习并复现公开数据集上的经典 MI-BCI 流程。

> 说明：代码在 AI 辅助下完成，分析与结果解释由作者负责。

---

## 1. 项目简介

- **任务**：左右手运动想象二分类。
- **数据**：上海大学杨帮华组公开的 **WBCIC-SHU (2025)** 数据集（51 名被试 × 3 天，58 导，250 Hz）。
- **方法**：CSP+LDA（同一次采集内、跨天迁移）、FBCSP+LDA（滤波器组 CSP + 互信息选特征）。
- **纪律**：所有"要学习"的步骤（CSP、特征选择、分类器）都放进 sklearn `Pipeline`，在交叉验证内部拟合，杜绝数据泄漏；随机种子固定 `random_state=42`。

## 2. 数据集引用

> Yang, B., Rong, F., Xie, Y., Li, D., Zhang, J., Li, F., Shi, G., & Gao, X. (2025).
> *A multi-day and high-quality EEG dataset for motor imagery brain-computer interface.*
> **Scientific Data, 12, 488.** DOI: 10.1038/s41597-025-04826-y
> 数据集（figshare）：DOI 10.25452/figshare.plus.22671172（许可 CC BY 4.0）

论文报告的 2C 基线（供对照，非本项目实测）：CSP+SVM **61.12%**、FBCSP+SVM **67.46%**、EEGNet **85.32%**。

## 3. 目录结构

```
.
├── src/                     # 公共函数（数据加载、带通、CSP+LDA、交叉验证）
│   └── eeg_utils.py
├── scripts/                 # 各阶段脚本
│   ├── step0_check_env.py
│   ├── step1_mi_csp_lda.py      # PhysioNet 入门示例（数据方提供）
│   ├── step1a_explore.py        # 数据结构探查
│   ├── step1b_single_subject.py # 单被试 CSP+LDA
│   ├── step2_signal.py          # 波形/PSD/时频
│   ├── step3a_all_subjects.py   # 全被试 within-session
│   ├── step3b_cross_session.py  # 跨天迁移
│   ├── step3c_fbcsp.py          # FBCSP
│   └── data_prep/               # 数据下载/抽取辅助脚本
├── results/                 # 结果（csv/txt）
├── figures/                 # 图（png）
├── requirements.txt
├── LICENSE                  # MIT
└── README.md
```

## 4. 环境安装

需要 Python 3.11。建议用虚拟环境：

```bash
python -m venv .venv
# Windows
.venv\Scripts\python.exe -m pip install -r requirements.txt
# 国内可用镜像（如 -i https://mirrors.aliyun.com/pypi/simple）
```

## 5. 复现步骤

1. 从 figshare 下载 **WBCIC-SHU** 的 `derivatives/2C dataset_processeddata`（约 6.6 GB，未加密，可按需抽取）。
2. 将各 session 的 MAT 放到 `data/WBCIC-SHU2025/processed/`，命名如 `sub-001_ses-01_task-motorimagery_eeg.mat`。
3. 依次运行（在项目根目录）：

```bash
python scripts/step1a_explore.py
python scripts/step1b_single_subject.py
python scripts/step2_signal.py
python scripts/step3a_all_subjects.py   # 支持断点续跑
python scripts/step3b_cross_session.py
python scripts/step3c_fbcsp.py
```

> 结果数字输出到 `results/`，图输出到 `figures/`。原始数据不入库（见 `.gitignore`）。

## 6. 主要结果（均为本项目实测）

**阶段1 · 单被试 sub-001（within-session，5 折分层 CV）**

| 设置 | session1 | session2 | session3 | 平均 |
|---|---|---|---|---|
| 8–30 Hz / 0.5–2.5 s | 70.0% | 59.5% | 48.5% | 59.3% |
| 3–35 Hz / 0–4 s（作者口径） | 63.5% | 63.5% | 49.0% | 58.7% |

见 `figures/accuracy_by_session.png`、`figures/csp_patterns_session1.png`。

**阶段2 · 信号**：单被试示例见 `figures/raw_snippet.png`、`figures/psd.png`、`figures/tfr_C3_C4.png`。**群体水平（51 人 × 3 天）对侧 ERD**：以“右手−左手”的 mu/beta log 功率差衡量，单电极层面只有 C4 显示显著的对侧效应（mu p=0.014、beta p=3.3e-5，70–78% 被试方向一致）；C3 没有一致的对侧效应（mu 中位数方向相反，43% 被试方向一致，p=0.34）。左右半球不对称的原因尚不清楚，可能与 Pz 参考、个体差异或左手想象更容易诱发有关，这是可以继续检验的问题。群体均值地形图上 mu 频段呈左负右正的对侧模式（左侧峰值偏 C3 后方），beta 频段主要表现为右半球效应；均值图与单电极中位数检验不完全一致，说明效应在被试间差异较大（`figures/group_erd_topomap.png`）。

**阶段3A · 全被试 within-session（51 人，CSP+LDA）**

- 总体平均 **0.5904 ± 0.1220**；低于 60% 的被试 **36 人（70.6%）**。
- 与论文 CSP+SVM 61.12% 接近（本项目为 4 分量+LDA，论文为 10 分量+SVM）。
- 见 `figures/within_session.png`。

**阶段3B · 跨天迁移**

| 情况 | 平均准确率 |
|---|---|
| 同一次采集内（3A） | 0.5904 |
| 跨天直接迁移（第 1 天训练→第 2、3 天测试） | **0.5255 ± 0.0661** |
| 跨天 + 目标采集前 20% 试次适应 | **0.5718 ± 0.1091** |

配对检验（n=51，Wilcoxon 符号秩）：适应 vs 直接迁移 **p=1.0e-5**；适应 vs 同一次采集内 **p=0.019**（适应后 0.5718 仍低于同一次采集内 0.5904）。见 `figures/cross_session.png`。

**阶段3C · FBCSP vs CSP（配对比较）**

| 方法 | 平均准确率 |
|---|---|
| CSP + LDA（3A） | 0.5904 ± 0.1220 |
| **FBCSP + LDA（3C）** | **0.6087 ± 0.1172** |
| Wilcoxon 符号秩检验 | **p = 0.0366（显著）** |

见 `figures/fbcsp_vs_csp.png`。

> 结果文件：`results/within_session.csv`、`results/cross_session.csv`、`results/fbcsp_vs_csp.csv`、`results/accuracy_by_session.csv`、`results/group_erd_c3c4.csv`、`results/stats_tests.txt`。

## 7. 局限性

- 只做了传统方法（CSP/LDA、FBCSP/LDA）；未跑深度学习（论文用 EEGNet 达 85.32%）。
- 频段/时间窗为固定选择（8–30 Hz / 0.5–2.5 s），未做个体化调参。
- 单被试阶段（阶段1/2）只看了 1 人，不能代表全体。
- 阶段2 时频图因所用数据无提示前静息段，基线采用"整段平均功率"，会压缩 ERD 幅度。
- 未做坏道/ICA 等更细的伪迹处理（处理数据已由作者做过去通道、重参考、带通、降采样）。

## 8. 致谢与声明

- 数据来自 Yang Banghua 团队，请按其论文要求引用。
- 代码在 AI 辅助下完成，**分析与结果解释由作者负责**。

---

<a name="english"></a>
## English

An end-to-end reproduction of left/right-hand **motor imagery EEG classification** on the public
**WBCIC-SHU (2025)** dataset: data exploration → CSP/LDA → cross-session transfer → FBCSP.

**Dataset citation:** Yang, B., Rong, F., Xie, Y., Li, D., Zhang, J., Li, F., Shi, G., & Gao, X. (2025).
*A multi-day and high-quality EEG dataset for motor imagery brain-computer interface.* Scientific Data, 12, 488.
DOI: 10.1038/s41597-025-04826-y. Dataset: 10.25452/figshare.plus.22671172 (CC BY 4.0).

**Install:** `python -m venv .venv` then `pip install -r requirements.txt` (Python 3.11).

**Reproduce:** download the `2C dataset_processeddata` MAT files (~6.6 GB) into
`data/WBCIC-SHU2025/processed/`, then run the scripts in `scripts/` in order
(`step1a` → `step1b` → `step2` → `step3a` → `step3b` → `step3c`).
All model fitting (CSP, feature selection, classifier) happens inside a scikit-learn
`Pipeline` under cross-validation to avoid data leakage; `random_state=42` throughout.

**Key results (measured):**
- 3A within-session (51 subjects, CSP+LDA): **0.5904 ± 0.1220** (36/51 subjects < 60%).
- 3B cross-session: within **0.5904** → direct transfer **0.5255 ± 0.0661** → +20% adaptation **0.5718 ± 0.1091** (adaptation vs direct: Wilcoxon **p=1.0e-5**; adaptation still below within-session, p=0.019).
- 3C FBCSP+LDA vs CSP+LDA: **0.6087 vs 0.5904**, Wilcoxon **p = 0.0366** (significant).
- Group-level contralateral ERD (51 subjects): only C4 showed a significant contralateral effect at the electrode level (mu p=0.014, beta p=3.3e-5; 70–78% subjects consistent); C3 showed no consistent contralateral effect (mu median in the opposite direction, 43% consistent, p=0.34), and the hemispheric asymmetry remains unexplained (possibly Pz reference, inter-subject variability, or left-hand imagery being easier to evoke). The group-mean topomap shows a left-negative/right-positive pattern at mu (peak just posterior to C3) and mainly a right-hemisphere effect at beta; the mean map and the single-electrode median tests are not fully consistent, indicating substantial between-subject variability.
- Paper reference (2C): CSP+SVM 61.12%, FBCSP+SVM 67.46%, EEGNet 85.32%.

**Limitations:** traditional methods only (no deep learning); fixed band/time-window; single-subject
analyses are not representative; TFR uses an epoch-mean baseline (no pre-stimulus rest in the provided data).

> The code was produced with AI assistance; the analysis and interpretation of results are the author's responsibility.
