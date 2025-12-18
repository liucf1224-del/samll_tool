# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# 添加 PyQt5 的二进制依赖
pyqt5_binaries = collect_dynamic_libs("PyQt5")

# 添加 VC++ 运行时 DLL
vc_redist_dlls = []
for dll in ["vcruntime140.dll", "msvcp140.dll", "vcruntime140_1.dll"]:
    dll_path = os.path.join(os.environ["SYSTEMROOT"], "System32", dll)
    if os.path.exists(dll_path):
        vc_redist_dlls.append((dll_path, "."))

# 收集 Qt 平台插件
pyqt5_plugins = []
for entry in collect_data_files("PyQt5", True):
    if "plugins" in entry[0]:
        pyqt5_plugins.append(entry)

a = Analysis(
    ['excel_tool.py'],
    pathex=[os.getcwd()],
    binaries=pyqt5_binaries + vc_redist_dlls,
    datas=pyqt5_plugins + [("icon.ico", ".")] if os.path.exists("icon.ico") else pyqt5_plugins,
    hiddenimports=['openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='excel_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 保持窗口应用
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)