# -*- coding: utf-8 -*-
# 作用：检查本机 Python 环境是否可跑 EEG 分析，收集各库版本号和 MNE 系统信息，写入 env.txt。
# 运行命令（Windows PowerShell）：
#   & 'D:\eeg-project\.venv\Scripts\python.exe' step0_check_env.py

import sys
import platform
import datetime


def main():
    lines = []
    lines.append("=" * 60)
    lines.append("阶段0 · 环境检查报告 env.txt")
    lines.append("生成时间：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("=" * 60)

    # 1) Python 解释器信息
    lines.append("")
    lines.append("[Python]")
    lines.append("  版本      : " + sys.version.replace("\n", " "))
    lines.append("  解释器路径: " + sys.executable)
    lines.append("  操作系统  : " + platform.platform())

    # 2) 关键库版本（逐个 import，缺哪个也能报出来，不整体崩）
    lines.append("")
    lines.append("[关键库版本]")
    libs = ["numpy", "scipy", "pandas", "matplotlib", "sklearn", "sklearn.linear_model", "h5py", "mne"]
    for name in libs:
        try:
            mod = __import__(name)
            ver = getattr(mod, "__version__", "未知")
            lines.append(f"  {name:24s}: {ver}")
        except Exception as e:  # noqa
            lines.append(f"  {name:24s}: 导入失败 -> {e}")

    # 3) MNE 系统信息（MNE 的 dx 诊断信息，含 BLAS/编译器等）
    lines.append("")
    lines.append("[mne.sys_info()]")
    try:
        import io
        import contextlib
        import mne
        # 不同 MNE 版本 sys_info() 行为不一：有的返回字符串，有的直接打印并返回 None。
        # 统一用 stdout 捕获，保证一定能拿到内容。
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mne.sys_info()
        info = buf.getvalue().strip()
        lines.append(info if info else "(mne.sys_info() 无输出)")
    except Exception as e:  # noqa
        lines.append("  mne.sys_info() 调用失败 -> " + str(e))

    text = "\n".join(lines)
    # 同时打印到屏幕并存盘，方便 run_log 与文件核对
    print(text)
    with open("env.txt", "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print("\n已写入 env.txt")


if __name__ == "__main__":
    main()
