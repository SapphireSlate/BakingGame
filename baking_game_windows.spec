# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['baking_game.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config.py', '.'),
    ],
    hiddenimports=[
        'pygame',
        'numpy',
        'scipy',
        'mixbox',
        'moderngl',
        'noise',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BakingGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/game_icon.ico' if os.path.exists('assets/icons/game_icon.ico') else None,
    version='file_version_info.txt',
) 