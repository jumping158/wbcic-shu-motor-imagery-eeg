# -*- coding: utf-8 -*-
# 作用：排查数据集密码问题的辅助脚本。
#   1) 列出该 figshare 文章各版本的说明：哪些文件被加密；
#   2) 下载最小的加密包 code_files.zip；
#   3) 用一组常见密码尝试解出其中一个很小的加密条目，判断是否存在"弱密码"。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' pwtest.py

import os
import requests
import zipfile

API = "https://api.figshare.com/v2/articles/19228725"

print("=" * 60)
print("[1] 各版本文件与加密情况（按 compress_type 判断）")
# 列出各版本的 file id 列表（figshare 通过 article 版本接口拿到的 files 里含 download_url）
for vid in [1, 2, 3]:
    try:
        r = requests.get(f"{API}/versions/{vid}", timeout=60)
        j = r.json()
        fs = j.get("files", [])
        print(f"  version {vid}: {len(fs)} 个文件")
        for f in fs[:20]:
            print("     ", f.get("name"), f.get("size"))
    except Exception as e:
        print(f"  version {vid} 查询失败：{e}")

print()
print("=" * 60)
print("[2] 下载 code_files.zip（最小加密包）用于试密码")
CODE_URL = "https://ndownloader.figshare.com/files/36728988"
CODE_ZIP = r"D:\eeg-project\data\raw\code_files.zip"
os.makedirs(os.path.dirname(CODE_ZIP), exist_ok=True)
if not (os.path.exists(CODE_ZIP) and os.path.getsize(CODE_ZIP) > 0):
    with requests.get(CODE_URL, stream=True, timeout=600) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        done = 0
        with open(CODE_ZIP, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
                done += len(chunk)
        print(f"  下载完成 {done} 字节 (期望 {total})")
else:
    print(f"  已存在 {os.path.getsize(CODE_ZIP)} 字节")

print()
print("=" * 60)
print("[3] 尝试常见密码")
try:
    import pyzipper
except Exception as e:
    print("  pyzipper 不可用：", e)
    raise SystemExit

# 找一个很小的加密条目来测试
with pyzipper.AESZipFile(CODE_ZIP) as z:
    infos = z.infolist()
    enc = [i for i in infos if (i.flag_bits & 0x1) and i.file_size > 0]
    print(f"  含 {len(enc)} 个加密条目，取最小的测试：", enc[0].filename if enc else None)
    # 按解压后大小排序取最小的
    enc.sort(key=lambda i: i.file_size)
    target = enc[0]
    print(f"  测试条目：{target.filename}  ({target.file_size} 字节)")

candidates = [
    "SHU", "shu", "SHU_dataset", "shudataset", "shu_dataset", "SHU2022", "shu2022",
    "SHU2021", "shu2021", "yangbanghua", "yang", "123456", "12345678", "000000",
    "1234", "password", "bci", "BCI", "SHU-BCI", "shu-bci", "shubci", "ma", "JunMa",
    "junma", "motor", "motori", "eeg", "EEG", "bio", "shu.edu.cn", "shu123",
]

ok = None
for pw in candidates:
    try:
        with pyzipper.AESZipFile(CODE_ZIP) as z:
            data = z.read(target.filename, pwd=pw.encode("utf-8"))
            ok = pw
            print(f"  [命中] 密码 = {pw!r}  (解出 {len(data)} 字节)")
            break
    except RuntimeError:
        continue
    except Exception as e:
        print(f"  尝试 {pw!r} 异常：{type(e).__name__}: {e}")

if ok is None:
    print("  常见密码全部失败 —— 需要向作者索取密码。")
