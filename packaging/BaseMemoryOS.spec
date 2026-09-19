# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for the packaged desktop application.

Run from the repo root:
    pyinstaller packaging/BaseMemoryOS.spec

Produces dist/BaseMemoryOS.exe (single file, windowed - no console
window on launch) on Windows, and an equivalent platform binary on
whatever OS actually runs PyInstaller (PyInstaller does not cross-
compile; a Windows .exe must be built on Windows, which is what
.github/workflows/build-windows.yml does in CI).

The end user's machine needs none of: Python, pip, Git. This bundles
its own Python runtime and every dependency (PySide6 included).
"""

import sys
from pathlib import Path

block_cipher = None

repo_root = Path(SPECPATH).resolve().parent
src_dir = repo_root / "src"

a = Analysis(
    [str(repo_root / "packaging" / "launch_app.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="BaseMemoryOS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # windowed subsystem - no console window on launch
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
