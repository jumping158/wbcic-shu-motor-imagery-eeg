# -*- coding: utf-8 -*-
# 作用：从 WBCIC-SHU(2025) v5 大 zip 中按需抽取 sub-001 的 3 次采集预处理 MAT、
#       全部顶层元数据、参考代码 code/。
#       做法：remotezip 只用来读目录；实际取字节用 HTTP Range + 本地解压（避免 remotezip.open 在大包上的问题）。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' extract_wbcic_sub001.py

import os
import struct
import zlib
import requests
from remotezip import RemoteZip

URL = "https://ndownloader.figshare.com/files/51001884"  # v5
ROOT = "WBCIC_SHU Motor Imagery dataset/"
OUT = r"D:\eeg-project\data\WBCIC-SHU2025"
os.makedirs(OUT, exist_ok=True)


def range_get(url, start, end):
    """闭区间 [start, end] 的字节。"""
    r = requests.get(url, headers={"Range": "bytes=%d-%d" % (start, end)}, timeout=300)
    r.raise_for_status()
    return r.content


def extract_member(z, url, member, dst):
    info = z.getinfo(member)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        print("  已存在，跳过: %s" % os.path.basename(dst))
        return os.path.getsize(dst)
    # 读本地文件头 30 字节，拿到文件名/扩展字段长度
    lh = range_get(url, info.header_offset, info.header_offset + 29)
    fields = struct.unpack("<IHHHHHIIIHH", lh)
    fnlen, extralen = fields[9], fields[10]
    data_start = info.header_offset + 30 + fnlen + extralen
    csize = info.compress_size
    raw = range_get(url, data_start, data_start + csize - 1)
    if info.compress_type == 0:
        data = raw
    elif info.compress_type == 8:
        data = zlib.decompress(raw, -15)
    else:
        raise ValueError("未支持的压缩方式: %d (%s)" % (info.compress_type, member))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(data)
    if len(data) != info.file_size:
        print("  [!] 大小不符 %s: 得到 %d, 期望 %d" % (member, len(data), info.file_size))
    print("  抽取 %-72s -> %d 字节 (method=%d)" % (member[len(ROOT):], len(data), info.compress_type))
    return len(data)


z = RemoteZip(URL)
infos = z.infolist()
allnames = [i.filename for i in infos]

# 1) sub-001 三次采集预处理 MAT
targets = sorted([
    n for n in allnames
    if "2C dataset_processeddata/sub-001/" in n and n.endswith("sub-001_ses-01_task-motorimagery_eeg.mat")
    or "2C dataset_processeddata/sub-001/" in n and n.endswith("sub-001_ses-02_task-motorimagery_eeg.mat")
    or "2C dataset_processeddata/sub-001/" in n and n.endswith("sub-001_ses-03_task-motorimagery_eeg.mat")
])

# 2) 顶层元数据文件
meta = []
for n in allnames:
    if not n.startswith(ROOT) or n.endswith("/"):
        continue
    rel = n[len(ROOT):]
    segs = [s for s in rel.split("/") if s]
    if len(segs) == 1:
        meta.append(n)

# 3) 参考代码
code = [n for n in allnames if (ROOT + "code/") in n and not n.endswith("/")]

print("将抽取：MPAT=%d, 元数据=%d, 代码=%d" % (len(targets), len(meta), len(code)))
print("元数据文件：", [m[len(ROOT):] for m in meta])
print()

total = 0
for m in targets + meta:
    total += extract_member(z, URL, m, os.path.join(OUT, os.path.basename(m)))
for c in code:
    rel = c[len(ROOT):].replace("/", os.sep)
    total += extract_member(z, URL, c, os.path.join(OUT, "code_ref", rel))

print("\n总计抽取 %.2f MB" % (total / 1e6))
