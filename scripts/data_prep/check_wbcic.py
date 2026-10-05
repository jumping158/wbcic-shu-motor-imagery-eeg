# -*- coding: utf-8 -*-
# 作用：检查 WBCIC-SHU (figshare 22671172) 各版本的文件清单、大小，以及主压缩包是否加密。
# 注意：本脚本【不下载】大文件，只用 HTTP Range 读取 zip 的目录（central directory）。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' check_wbcic.py

import requests
from remotezip import RemoteZip

print("=" * 70)
print("【一】各版本文件清单")
url_by_version = {}
for v in range(1, 6):
    try:
        r = requests.get("https://api.figshare.com/v2/articles/22671172/versions/%d" % v, timeout=60)
        j = r.json()
        fs = j.get("files", [])
        print("--- version %d: %d files, DOI=%s" % (v, len(fs), j.get("doi")))
        for f in fs:
            print("     ", f.get("name"), "|", f.get("size"), "|", f.get("download_url"))
        if fs:
            url_by_version[v] = fs[0].get("download_url")
    except Exception as e:
        print("version %d 查询失败: %s" % (v, e))

print()
print("=" * 70)
print("【二】尝试读取各版本压缩包目录（判断是否加密、内部结构）")
for v, url in url_by_version.items():
    print("--- version %d  zip: %s" % (v, url))
    try:
        with RemoteZip(url) as z:
            infos = z.infolist()
            print("     条目数: %d" % len(infos))
            total = sum(i.file_size for i in infos)
            print("     解压后总大小: %.1f MB" % (total / 1e6))
            # 是否加密
            enc = [i for i in infos if i.flag_bits & 0x1]
            print("     加密条目数: %d" % len(enc))
            for i in infos[:12]:
                print("       ", i.filename, i.file_size, "flag=" + hex(i.flag_bits))
    except Exception as e:
        print("     [!] 读取失败: %s: %s" % (type(e).__name__, e))
