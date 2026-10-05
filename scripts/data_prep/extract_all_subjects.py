# -*- coding: utf-8 -*-
# 作用：用分块 Range（可断点续传）下载 WBCIC-SHU(2025) 全部 51 名被试的 2C processed MAT（153 个文件），
#       逐个解压 deflate 到 processed\ 目录。可重复运行以续传。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' extract_all_subjects.py

import os
import time
import struct
import zlib

import requests
from remotezip import RemoteZip
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://ndownloader.figshare.com/files/51001884"
ROOT = "WBCIC_SHU Motor Imagery dataset/"
OUT = r"D:\eeg-project\data\WBCIC-SHU2025\processed"
os.makedirs(OUT, exist_ok=True)


def robust_get(start, end, tries=6):
    for a in range(tries):
        try:
            r = requests.get(URL, headers={"Range": "bytes=%d-%d" % (start, end)}, timeout=(30, 180))
            if r.status_code == 206:
                return r.content
            raise IOError("HTTP %d" % r.status_code)
        except Exception:
            time.sleep(1 + a)
    raise IOError("下载块失败 %d-%d" % (start, end))


def download_one(info):
    dst = os.path.join(OUT, os.path.basename(info.filename))
    total = info.compress_size
    if os.path.exists(dst) and os.path.getsize(dst) == info.file_size:
        return "skip"
    lh = robust_get(info.header_offset, info.header_offset + 29)
    fields = struct.unpack("<IHHHHHIIIHH", lh)
    ds = info.header_offset + 30 + fields[9] + fields[10]
    zpath = dst + ".z"
    # 续传压缩流
    while True:
        done = os.path.getsize(zpath) if os.path.exists(zpath) else 0
        if done >= total:
            break
        try:
            r = requests.get(URL, headers={"Range": "bytes=%d-%d" % (ds + done, ds + total - 1)},
                             stream=True, timeout=(30, 180))
            if r.status_code != 206:
                r.close()
                raise IOError("HTTP %d" % r.status_code)
            with open(zpath, "ab") as f:
                for c in r.iter_content(1 << 20):
                    f.write(c)
            r.close()
        except Exception:
            time.sleep(2)
    # 解压
    with open(zpath, "rb") as f:
        data = zlib.decompress(f.read(), -15) if info.compress_type == 8 else f.read()
    with open(dst, "wb") as f:
        f.write(data)
    os.remove(zpath)
    if len(data) != info.file_size:
        return "SIZEERR:%s" % os.path.basename(dst)
    return "ok"


def main():
    z = None
    for a in range(6):
        try:
            z = RemoteZip(URL)
            infos = z.infolist()
            break
        except Exception as e:
            print("读取目录重试", a, type(e).__name__)
            time.sleep(3)
    mats = [i for i in infos if "2C dataset_processeddata" in i.filename and i.filename.endswith(".mat")]
    mats.sort(key=lambda i: i.filename)
    print("待下载 MAT：%d 个，合计 %.2f GB" %
          (len(mats), sum(i.compress_size for i in mats) / 1e9))

    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(download_one, i): i for i in mats}
        for fut in as_completed(futs):
            done += 1
            st = fut.result()
            if done % 5 == 0 or st.startswith("SIZEERR"):
                print("[%3d/%d] %s" % (done, len(mats), st), flush=True)

    files = [f for f in os.listdir(OUT) if f.endswith(".mat")]
    print("完成：processed 目录共 %d 个 MAT，合计 %.2f GB" %
          (len(files), sum(os.path.getsize(os.path.join(OUT, f)) for f in files) / 1e9))


if __name__ == "__main__":
    main()
