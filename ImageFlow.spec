# -*- mode: python ; coding: utf-8 -*-
import os
import sys

from PyInstaller.utils.hooks import collect_all

# pillow-heif ships its own native libheif, make sure all of it is bundled
heif_datas, heif_binaries, heif_hiddenimports = collect_all('pillow_heif')

icon_path = os.path.join('ui', 'graphics', 'logo.ico')

a = Analysis(
    ['ImageFlow.py'],
    pathex=[],
    binaries=heif_binaries,
    datas=[(os.path.join('ui', 'graphics'), os.path.join('ui', 'graphics'))] + heif_datas,
    hiddenimports=heif_hiddenimports,
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
    a.datas,
    [],
    name='ImageFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[icon_path],
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='ImageFlow.app',
        icon=icon_path,
        bundle_identifier=None,
    )
