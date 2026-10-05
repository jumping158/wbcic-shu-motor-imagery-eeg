# -*- coding: utf-8 -*-
# 作用：读取 WBCIC-SHU v5 大压缩包的目录（不下载），按目录聚合体积，
#       并单独统计"二分类(2C)预处理"部分的大小，用于判断是否 ≤30 GB。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' analyze_wbcic_zip.py

from remotezip import RemoteZip
from collections import defaultdict

URL = "https://ndownloader.figshare.com/files/51001884"

with RemoteZip(URL) as z:
    infos = z.infolist()

print("总条目：%d" % len(infos))
print()

# 按前 3 段路径聚合
agg = defaultdict(lambda: [0, 0, 0])  # count, uncompressed, compressed
for i in infos:
    parts = i.filename.split("/")
    key = "/".join(parts[:3]) if len(parts) >= 3 else i.filename
    agg[key][0] += 1
    agg[key][1] += i.file_size
    agg[key][2] += i.compress_size

print("=== 按目录聚合（Top 30，按解压后大小降序）===")
for k, v in sorted(agg.items(), key=lambda x: -x[1][1])[:30]:
    print("  %9.2f MB (压缩 %9.2f MB)  x%-5d  %s" % (v[1] / 1e6, v[2] / 1e6, v[0], k))

print()
print("=== 所有含 'process' 的条目（前 60）===")
proc = [i for i in infos if "process" in i.filename.lower()]
tot_u = sum(i.file_size for i in proc)
tot_c = sum(i.compress_size for i in proc)
print("含 'process' 的条目数=%d，解压总大小=%.2f MB，压缩总大小=%.2f MB" % (len(proc), tot_u / 1e6, tot_c / 1e6))
for i in proc[:60]:
    print("   %8.2f MB | %8.2f MB | %s" % (i.file_size / 1e6, i.compress_size / 1e6, i.filename))

print()
print("=== 顶层结构（前 2 层目录）===")
lvl2 = defaultdict(lambda: [0, 0])
for i in infos:
    parts = i.filename.split("/")
    key = "/".join(parts[:2]) if len(parts) >= 2 else i.filename
    lvl2[key][0] += 1
    lvl2[key][1] += i.file_size
for k, v in sorted(lvl2.items(), key=lambda x: -x[1][1])[:20]:
    print("  %9.2f MB  x%-5d  %s" % (v[1] / 1e6, v[0], k))
