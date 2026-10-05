# baseline_sources.md —— 数据集引用与论文报告基线（带出处）

> 用途：阶段1B 的对比参照。**本文件只记录"论文报告的数字"，我方实际跑出的数字另记（见 accuracy_by_session.csv 等），两者绝不混写。**
> 主数据集：WBCIC-SHU（2025）。
> 摘录人：DeepSeek 执行端；所有出处均已核对原文（Scientific Data, open access）。

---

## 一、数据集引用（写论文/README 用）

**正式引用：**
> Yang, B., Rong, F., Xie, Y., Li, D., Zhang, J., Li, F., Shi, G., & Gao, X. (2025). *A multi-day and high-quality EEG dataset for motor imagery brain-computer interface.* **Scientific Data, 12, 488.** DOI: 10.1038/s41597-025-04826-y

**数据集本体（figshare）：**
> Yang, B. & Rong, F. *WBCIC-SHU motor imagery dataset.* figshare. DOI: 10.25452/figshare.plus.22671172 （许可 CC BY 4.0）

**论文内引用数据集的方式（参考文献 19）：**
> Yang, B. & Fenqi, R. Source code for: WBCIC-SHU motor imagery dataset. Figshare 10.25452/figshare.plus.22671172 (2023).

---

## 二、数据集基本参数（出处：论文 Methods / Data Records / Table 3）

| 项目 | 数值 | 出处 |
|---|---|---|
| 被试总数 | 62 名健康右利手（17–30 岁，18 名女性），均为 BCI 新手 | Methods → Participants and environment |
| 二分类(2C)被试数 | **论文写 51 人**；`participants_2C.tsv` 实列 52 行；processed 数据 153 个 session = 51×3 | 论文 vs 数据文件，**存在 1 人出入，须在报告里注明** |
| 三分类(3C)被试数 | 11 人 | Methods |
| 采集次数 | 每人 **3 次**，不同日期 | Methods → Experimental paradigm |
| 每次试次数 | 2C：40 试次/block × 5 block = **200 试次**（每类 100）；3C：300 试次 | Methods / Data Records |
| 单试次时长 | 7.5 s = 提示 **1.5 s** + 运动想象 **4 s** + 休息 2 s | Methods → Experimental paradigm |
| 单次采集时长 | 约 35–48 min（含睁眼 60 s、闭眼 60 s、5 个 MI block） | Methods |
| 通道 | 64 导帽：1–59 为 EEG，60 为 ECG，61–64 为 EOG；预处理后 **58 导** | Methods → Data collection / preprocessing |
| 采样率 | 原始 **1000 Hz**；预处理降到 **250 Hz** | Methods |
| 设备 | Neuracle 无线 EEG（EEGCap64-V3.0） | task-motorimagery_eeg.json |
| 参考/地 | 预处理后**以 Pz 为重参考** | Methods → preprocessing |
| 事件编码 | value 1=左手抓握，2=右手抓握，3=脚勾 | task-motorimagery_events.json |

**processed MAT 的存储格式（出处：Data Records，并经我方实测确认）**：
- `data`：`[58 × 1000 × 200]` = 通道 × 时间点 × 试次（250 Hz，4 s＝1000 点）；
- `labels`：`[1 × 200]`，取值 1/2（2C）。

**口径说明（直接用）**：processed 数据已经过 去 ECG/EOG、Pz 重参考、0.5–40 Hz FIR 带通 + 50 Hz 陷波、取提示后 4 s、去基线、250 Hz 降采样。**因此我方不应再重复这些滤波/重参考**（除非有明确理由）。

---

## 三、论文报告的基线数字（**只记论文数字**，出处精确到图/表）

### 3.1 2C 数据集平均分类准确率（出处：讨论段 + Fig. 7(a)）
> 原文：*"the classification accuracies achieved by each algorithm ... with 61.12% (CSP + SVM), 67.46% (FBCSP + SVM), 85.32% (EEGNet), 84.47% (deepConvNet) and 78.40% (FBCNet)."*

| 算法 | 准确率 | 出处 |
|---|---|---|
| CSP + SVM | **61.12%** | Fig. 7(a) 正文 |
| FBCSP + SVM | **67.46%** | Fig. 7(a) 正文 |
| EEGNet | **85.32%** | Fig. 7(a) 正文 |
| deepConvNet | **84.47%** | Fig. 7(a) 正文 |
| FBCNet | **78.40%** | Fig. 7(a) 正文 |

- 平均范围：**153 个独立 session**（51×3）；机会水平线 p=0.0138（Fig. 7 红色点划线）。
- **与我方最可比的是 CSP+SVM = 61.12%、FBCSP+SVM = 67.46%**（我方阶段1B/3A 用 CSP+LDA，阶段3C 用 FBCSP）。

### 3.2 3C 数据集平均分类准确率（出处：讨论段 + Fig. 7(b)）
| 算法 | 准确率 |
|---|---|
| FBCSP + SVM | 58.40% |
| EEGNet | 75.34% |
| deepConvNet | 76.90%（论文摘要主推） |
| FBCNet | 74.77% |

### 3.3 分 session 平均准确率（出处：Table 2，算法 EEGNet）
| 数据集 | Session 1 | Session 2 | Session 3 |
|---|---|---|---|
| 2C | **81.77%** | **86.63%** | **88.90%** |
| 3C | 71.91% | 75.52% | 83.27% |

> 论文解读：session1 最低、session3 最高，提示被试在多次 MI 后能力随练习提升（Learning effect）。
> **注意**：Table 2 是 EEGNet 的跨 session 数字，**不是**"用 session1 训练、直接测 session2/3"的跨天迁移数字。论文没有给出与 SHU2022 类似的"直接跨天迁移 vs 适应"对比表；这恰是我方 3B 能补的空白。

### 3.4 与其他数据集的可比性（出处：Table 3 与 Table 4）
**Table 3（数据集特征）：**

| 数据集 | 被试数 | session 数 | 类别数 | 通道数 |
|---|---|---|---|---|
| BCI IV-2a | 9 | 2 | 4 | 22 |
| OpenBMI | 54 | 2 | 2 | 20 |
| **本文 2C** | **51** | **3** | **2** | **58** |
| 本文 3C | 11 | 3 | 3 | 58 |

**Table 4（同一套算法下的平均解码准确率）：**

| 数据集 | EEGNet | deepConvNet | FBCNet |
|---|---|---|---|
| BCI IV-2a | 73.13% | 72.20% | 79.03% |
| OpenBMI | 70.89% | 68.33% | 74.70% |
| **2C** | **85.31%** | **84.47%** | **78.40%** |
| 3C | 75.34% | 76.90% | 74.77% |

> 注：Table 4 的 2C-EEGNet 写作 85.31%，正文 Fig. 7(a) 段写 85.32%，**存在 0.01% 的排版差异**，引用时以正文 85.32% 为准并注明。

---

## 四、论文/作者代码里的方法与超参数（出处：论文 Methods + 随数据集发布的 code.rar）

| 环节 | 论文/作者代码的设置 | 出处 |
|---|---|---|
| 评估方式 | **10 折交叉验证**（CSP/FBCSP/deep 统一） | Methods → Classification performance |
| CSP 特征 | 作者 `code/Machine_learning/CSP/`：CSP(n_components=**10**, log=False) + **SVM** | code.rar, ws.py |
| CSP 频段 | 作者代码 `mnebandFilter(..., 3, 35)` → **3–35 Hz** | code.rar, ws.py |
| CSP 时间窗 | `mne.Epochs(..., 0, 4-0.004)` → **0–~4 s**（整段 MI） | code.rar, data_preprocess.py |
| FBCSP 通道 | 作者 `Preprocess.py` 只用 **20 个运动区通道**：FC5,FC3,FC1,FC2,FC4,FC6,C5,C3,C1,Cz,C2,C4,C6,CP5,CP3,CP1,CPz,CP2,CP4,CP6 | code.rar, FBCSP/bin/Preprocess.py |
| 深度学习 | EEGNet/deepConvNet/FBCNet，batch 16，lr 0.001，NLLLoss，Adam；两阶段训练 | Methods → Classification performance |

> **给阶段1B 的依据**：Claude 要求"通道/频段/时间窗先查原论文设置，并写明出处"——上方即出处。
> **我的选择（需在讲解中说明理由）**：`n_components` 用 **4**（任务规定），频段与时间窗可参考作者代码的 **3–35 Hz、0–4 s**，或按惯用的 **8–30 Hz、提示后 0.5–2.5 s**；两者都会在本阶段做对比并说明。通道：全 58 导（与作者 CSP 一致）优于只看 20 导。

---

## 五、我方自己跑出的数字（**另行记录，禁止与上面混用**）

| 内容 | 文件 | 状态 |
|---|---|---|
| 单被试各 session CSP+LDA 5 折准确率 | results/step1b/accuracy_by_session.csv | 待跑 |
| （阶段3）within/cross/FBCSP | results/step3*/** | 待跑 |

（本节留空占位，跑出后由脚本写入或在此登记。）
