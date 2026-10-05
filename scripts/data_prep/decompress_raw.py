# -*- coding: utf-8 -*-
# 作用：把上一步下载到的"deflate 压缩流"解压成真正的 BDF 文件。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' decompress_raw.py

import os
import zlib
from remotezip import RemoteZip

URL = "https://ndownloader.figshare.com/files/51001884"
ROOT = "WBCIC_SHU Motor Imagery dataset/"
RAW = r"D:\eeg-project\data\WBCIC-SHU2025\raw"

Z = RemoteZip(URL)

pairs = [
    (ROOT + "sourcedata/2C dataset/sub-001/ses-01/eeg/data.bdf", os.path.join(RAW, "data.bdf")),
    (ROOT + "sourcedata/2C dataset/sub-001/ses-01/eeg/evt.bdf", os.path.join(RAW, "evt.bdf")),
]

for member, path in pairs:
    info = Z.getinfo(member)
    print("%s: compress_type=%d csize=%d usize=%d" %
          (os.path.basename(path), info.compress_type, info.compress_size, info.file_size))
    if os.path.getsize(path) == info.file_size:
        print("  似乎已是解压态，跳过")
        continue
    with open(path, "rb") as f:
        raw = f.read()
    data = zlib.decompress(raw, -15) if info.compress_type == 8 else raw
    if len(data) != info.file_size:
        print("  [!] 解压后大小 %d != 期望 %d" % (len(data), info.file_size))
    with open(path, "wb") as f:
        f.write(data)
    print("  解压完成 -> %d 字节" % len(data))

print("\n最终原始目录：")
for fn in sorted(os.listdir(RAW)):
    print("  ", fn, os.path.getsize(os.path.join(RAW, fn)))
