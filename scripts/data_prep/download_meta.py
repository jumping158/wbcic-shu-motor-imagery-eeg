# -*- coding: utf-8 -*-
# 作用：从 figshare 下载本数据集的说明文件与 sub-001 的事件文件（都是小文件）。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' download_meta.py

import os
import requests

OUT = r"D:\eeg-project\data\metadata"
os.makedirs(OUT, exist_ok=True)

FILES = {
    "README.txt": "https://ndownloader.figshare.com/files/36729006",
    "dataset_description.json": "https://ndownloader.figshare.com/files/34166145",
    "participants.json": "https://ndownloader.figshare.com/files/34166148",
    "participants.tsv": "https://ndownloader.figshare.com/files/34166151",
    "task-motorimagery_channels.tsv": "https://ndownloader.figshare.com/files/34166154",
    "task-motorimagery_coordsystem.json": "https://ndownloader.figshare.com/files/34166157",
    "task-motorimagery_eeg.json": "https://ndownloader.figshare.com/files/34166160",
    "task-motorimagery_electrodes.tsv": "https://ndownloader.figshare.com/files/34166163",
    "task-motorimagery_events.json": "https://ndownloader.figshare.com/files/34166166",
    "sub-001_ses-01_task_motorimagery_events.tsv": "https://ndownloader.figshare.com/files/34166184",
    "sub-001_ses-02_task_motorimagery_events.tsv": "https://ndownloader.figshare.com/files/34166187",
    "sub-001_ses-03_task_motorimagery_events.tsv": "https://ndownloader.figshare.com/files/34166190",
    "sub-001_ses-04_task_motorimagery_events.tsv": "https://ndownloader.figshare.com/files/34166193",
    "sub-001_ses-05_task_motorimagery_events.tsv": "https://ndownloader.figshare.com/files/34166196",
}

for name, url in FILES.items():
    dst = os.path.join(OUT, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        print(f"已存在，跳过：{name}")
        continue
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    with open(dst, "wb") as f:
        f.write(r.content)
    print(f"下载 {name}: {len(r.content)} 字节")

print("元数据下载完成 ->", OUT)
