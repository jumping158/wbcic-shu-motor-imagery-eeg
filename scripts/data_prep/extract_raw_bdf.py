# -*- coding: utf-8 -*-
# 作用：从 WBCIC-SHU(2025) v5 大 zip 中，用"可断点续传的 Range"抽取 sub-001 ses-01 的原始 BDF 与事件文件。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' extract_raw_bdf.py

import os
import time
import struct
import requests
from remotezip import RemoteZip

URL = "https://ndownloader.figshare.com/files/51001884"
ROOT = "WBCIC_SHU Motor Imagery dataset/"
OUT = r"D:\eeg-project\data\WBCIC-SHU2025\raw"
os.makedirs(OUT, exist_ok=True)

MEMBERS = [
    ROOT + "sourcedata/2C dataset/sub-001/ses-01/eeg/data.bdf",
    ROOT + "sourcedata/2C dataset/sub-001/ses-01/eeg/evt.bdf",
]

session = requests.Session()


def head_bytes(start, end):
    for a in range(8):
        try:
            r = session.get(URL, headers={"Range": "bytes=%d-%d" % (start, end)}, timeout=(30, 120))
            if r.status_code == 206:
                return r.content
            raise IOError("HTTP %d" % r.status_code)
        except Exception:
            time.sleep(1 + a)
    raise IOError("头部读取失败")


def data_start_of(info):
    lh = head_bytes(info.header_offset, info.header_offset + 29)
    fnlen, extralen = struct.unpack("<IHHHHHIIIHH", lh)[9], struct.unpack("<IHHHHHIIIHH", lh)[10]
    return info.header_offset + 30 + fnlen + extralen


def download(member, dst):
    info = z.getinfo(member)
    total = info.compress_size
    if os.path.exists(dst) and os.path.getsize(dst) == total:
        print("  已存在且完整，跳过:", os.path.basename(dst))
        return
    ds = data_start_of(info)
    print("  %s: 目标 %.1f MB" % (os.path.basename(dst), total / 1e6))
    while True:
        done = os.path.getsize(dst) if os.path.exists(dst) else 0
        if done >= total:
            break
        start = ds + done
        end = ds + total - 1
        try:
            r = session.get(URL, headers={"Range": "bytes=%d-%d" % (start, end)}, stream=True, timeout=(30, 180))
            if r.status_code != 206:
                r.close()
                raise IOError("HTTP %d" % r.status_code)
            with open(dst, "ab") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
            r.close()
        except Exception as e:
            print("    [!] 中断，续传中: %s" % e, flush=True)
            time.sleep(2)
        print("    ... %.1f/%.1f MB" % (os.path.getsize(dst) / 1e6, total / 1e6), flush=True)
    print("  完成 %s: %d 字节" % (os.path.basename(dst), os.path.getsize(dst)))


z = RemoteZip(URL)
for m in MEMBERS:
    download(m, os.path.join(OUT, os.path.basename(m)))

print("原始文件目录：")
for fn in sorted(os.listdir(OUT)):
    print("  ", fn, os.path.getsize(os.path.join(OUT, fn)))
