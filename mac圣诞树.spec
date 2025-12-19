# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None  # 不加密，体积更小

# 资源文件配置（跨平台兼容）
added_files = [
    (os.path.join('res', 'Icon1.ico'), 'res'),
    (os.path.join('res', 'Icon1.icns'), 'res'),
    (os.path.join('res', 'Star*.png'), 'res'),
    (os.path.join('res', 'img*.png'), 'res'),
    (os.path.join('res', 'imgTree.png'), 'res'),
]

a = Analysis(
    ['christmas_tree_app_pyqt5.py'],
    datas=added_files,
    excludes=['tkinter', 'sqlite3', 'unittest', 'doctest', 'xml', 'email', 'http', 'distutils'],
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 生成可执行文件
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
    name='圣诞树',
    console=False,
    icon=os.path.join('res', 'Icon1.icns'),  # mac使用icns图标
    upx=True,  # 启用压缩
)

# 生成mac应用包
app = BUNDLE(
    exe,
    name='圣诞树.app',
    icon=os.path.join('res', 'Icon1.icns'),
    info_plist={
        'NSHighResolutionCapable': True,  # 支持Retina
    }
)