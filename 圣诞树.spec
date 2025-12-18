# -*- mode: python ; coding: utf-8 -*-

block_cipher = None  # 无加密（如需加密，需初始化加密器）

# 配置资源文件
added_files = [
    # ('res', 'res'),   第一个参数是源目录，第二个参数是打包后的目录 这个是通用
    ('res/Icon1.ico', 'res'),
    ('res/Star*.png', 'res'),
    ('res/img*.png', 'res'),
    ('res/imgTree.png', 'res')
    # 只包含必要的资源，避免通配符匹配过多文件
]

a = Analysis(
    ['christmas_tree_app_pyqt5.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',      # 另一个GUI库，与PyQt5冲突
        'sqlite3',       # 数据库模块
        'unittest',      # 测试框架
        'doctest',       # 文档测试
        'xml',           # XML处理
        'email',         # 邮件处理
        'http',          # HTTP服务器/客户端
        'logging',       # 日志模块（如果你自己实现了日志则保留）
        'ctypes',        # C语言调用（如果未使用则排除）
        'distutils',     # 安装工具
        'PIL',           # 图像处理（如果你用PyQt5的QPixmap则排除）
        'numpy',         # 科学计算（未使用）
        'pandas',        # 数据分析（未使用）
        'matplotlib',    # 绘图库（未使用）
        'scipy',         # 科学计算（未使用）
    ],# 排除的模块
    win_no_prefer_redirects=False, # 新增的开始 控制Windows DLL重定向
    win_private_assemblies=False, # 控制Windows私有程序集
    # cipher=block_cipher,#新增的结束 启用加密
    noarchive=False,
    optimize=0,
)
# pyz = PYZ(a.pure)
# a.zipped_data ：包含所有可压缩的数据文件，添加后可以被加密    cipher=block_cipher ：启用加密，适合需要保护代码的场景
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='圣诞树',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True, # 启用UPX压缩
    upx_exclude=[],# 排除不适合压缩的文件
    runtime_tmpdir=None,
    console=False, # 隐藏控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='res/Icon1.ico'  # 应用图标
)
