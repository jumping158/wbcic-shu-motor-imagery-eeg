# -*- coding: utf-8 -*-
# 作用：不下载整个压缩包，仅通过 HTTP Range 读取 figshare 上 edf_files.zip / mat_files.zip 的目录，
#       列出其中所有文件名与大小，并特别标出 sub-001 的文件。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' list_zips.py

from remotezip import RemoteZip

ZIPS = {
    "edf_files.zip": "https://ndownloader.figshare.com/files/36728991",
    "mat_files.zip": "https://ndownloader.figshare.com/files/36728994",
}

for label, url in ZIPS.items():
    print("=" * 70)
    print(f"{label}  ({url})")
    print("=" * 70)
    try:
        with RemoteZip(url) as z:
            infos = z.infolist()
            print(f"共 {len(infos)} 个条目")
            total = 0
            s1 = []
            for it in infos:
                total += it.file_size
                line = f"  {it.filename}  {it.file_size} 字节"
                if "sub-001" in it.filename:
                    s1.append(line)
            print(f"解压后总大小约 {total/1e6:.1f} MB")
            print("--- sub-001 条目 ---")
            for line in s1:
                print(line)
            print("--- 前 5 个条目示例 ---")
            for it in infos[:5]:
                print(f"  {it.filename}  {it.file_size} 字节")
    except Exception as e:
        print(f"  [!] 读取失败：{type(e).__name__}: {e}")
    print()
