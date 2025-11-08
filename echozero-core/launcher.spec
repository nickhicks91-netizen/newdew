# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for EchoZero standalone application

Build commands:
    # Windows
    pyinstaller launcher.spec --clean

    # macOS
    pyinstaller launcher.spec --clean --windowed

    # Linux
    pyinstaller launcher.spec --clean
"""

import sys
from pathlib import Path

# Get base directory
block_cipher = None
base_dir = Path('.').absolute()

# Collect all Python source files
source_files = []
for pattern in ['src/**/*.py', '*.py']:
    source_files.extend([
        (str(f), str(f.parent)) for f in base_dir.glob(pattern)
        if f.name != 'launcher.py'
    ])

# Collect data files
data_files = [
    ('config/config.yaml', 'config'),
    ('README.md', '.'),
]

# Collect all package dependencies
hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'streamlit',
    'streamlit.web.cli',
    'fastapi',
    'torch',
    'numpy',
    'plotly',
    'anthropic',
    'sentence_transformers',
    'mne',
    'yaml',
    'pydantic',
]

a = Analysis(
    ['launcher.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=data_files + source_files,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='EchoZero',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for windowed app (no console)
    disable_windowing_hook=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add your icon file here: 'icon.ico' or 'icon.icns'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EchoZero',
)

# macOS app bundle (optional)
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='EchoZero.app',
        icon=None,  # Add 'icon.icns' here
        bundle_identifier='com.echozero.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
