# -*- coding: utf-8 -*-
# 作用：实证"能不能手动/不带密码打开"这个加密 zip。
#   依次尝试：1) 不输密码列目录；2) 不输密码解压；3) 空密码解压；4) 错误密码解压。
# 运行：& 'D:\eeg-project\.venv\Scripts\python.exe' demo_open.py

import zipfile
import pyzipper

P = r"D:\eeg-project\data\raw\code_files.zip"

# 找一个"真文件"条目（跳过纯目录）
with zipfile.ZipFile(P) as z:
    infos = z.infolist()
    target = next(i for i in infos if i.file_size > 0 and (i.flag_bits & 0x1))
    names = [i.filename for i in infos]

print("=" * 60)
print("【1】不输密码，只列目录（ZIP 的目录本身不加密）")
print(f"    条目总数：{len(infos)}")
print(f"    前 5 个：{names[1:6]}")
print("    -> 结论：能『看见』文件名和大小，但只是目录。")

print("=" * 60)
print("【2】不输密码，直接解压一个条目（python 标准库）")
with zipfile.ZipFile(P) as z:
    try:
        data = z.read(target.filename)
        print(f"    竟然成功，解出 {len(data)} 字节")
    except Exception as e:
        print(f"    失败：{type(e).__name__}: {e}")

print("=" * 60)
print("【3】用『空密码』解压（兼容 AES 的 pyzipper）")
try:
    with pyzipper.AESZipFile(P) as z:
        z.read(target.filename, pwd=b"")
    print("    空密码成功")
except Exception as e:
    print(f"    失败：{type(e).__name__}: {e}")

print("=" * 60)
print("【4】用『错误密码 1234』解压")
try:
    with pyzipper.AESZipFile(P) as z:
        z.read(target.filename, pwd=b"1234")
    print("    竟然成功")
except Exception as e:
    print(f"    失败：{type(e).__name__}: {e}")

print("=" * 60)
print(f"被测条目：{target.filename}（压缩方式={target.compress_type}，加密位={hex(target.flag_bits)}）")
