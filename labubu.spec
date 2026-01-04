# -*- mode: python ; coding: utf-8 -*-

# 定义需要包含的资源文件
datas = [
    ('res/Icon1.ico', 'res'),
    ('res/labubu00.png', 'res'),
    ('res/labubu01.png', 'res'),
    ('res/labubu02.png', 'res'),
    ('res/labubu03.png', 'res'),
    ('res/labubu04.png', 'res'),
    ('res/labubu05.png', 'res'),
    ('res/labubu06.png', 'res'),
    ('res/labubu07.png', 'res'),
    ('res/labubu08.png', 'res'),
    ('res/labubu09.png', 'res'),
    ('res/labubu10.png', 'res'),
    ('res/labubu11.png', 'res'),
    ('res/labubu12.png', 'res'),
    ('res/labubu13.png', 'res'),
    ('res/labubu14.png', 'res'),
    ('res/labubu15.png', 'res'),
    ('res/labubu16.png', 'res'),
    ('res/labubu17.png', 'res'),
    ('res/Star4.png', 'res'),
    ('res/Star5.png', 'res'),
    ('res/Star6.png', 'res'),
]

# 定义需要排除的模块
excludes = [
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'tkinter',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtWebEngineCore',
    'PyQt5.QtWebChannel',
    'PyQt5.QtNetwork',
    'PyQt5.QtOpenGL',
    'PyQt5.QtXml',
    'PyQt5.QtSql',
    'PyQt5.QtTest',
    'PyQt5.QtHelp',
    'PyQt5.QtDesigner',
    'PyQt5.QtAxContainer',
    'PyQt5.QtDBus',
    'PyQt5.QtLocation',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.QtPositioning',
    'PyQt5.QtPrintSupport',
    'PyQt5.QtQml',
    'PyQt5.QtQuick',
    'PyQt5.QtQuickWidgets',
    'PyQt5.QtSensors',
    'PyQt5.QtSerialPort',
    'PyQt5.QtWebSockets',
]


a = Analysis(
    ['christmas_man.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,  # 使用最大优化级别
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Labubu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 移除调试信息
    upx=True,  # 使用UPX压缩
    upx_exclude=['vcruntime140.dll', 'msvcp140.dll'],  # 排除某些可能导致问题的DLL
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['res\Icon1.ico'],
)