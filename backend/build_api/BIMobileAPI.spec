# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\gabriel.brito\\Desktop\\Projetos\\BIMobile\\backend\\api_entry.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\gabriel.brito\\Desktop\\Projetos\\BIMobile\\backend\\data', 'data')],
    hiddenimports=['firebird.driver', 'fdb'],
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
    name='BIMobileAPI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
