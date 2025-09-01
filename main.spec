# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

# Diretório base do projeto
base_dir = os.path.dirname(os.path.abspath(SPECPATH))

# Coleta todos os imports de customtkinter
datas = []
binaries = []
hiddenimports = []

# Adiciona customtkinter
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Adiciona tkinter
hiddenimports += ['tkinter', 'tkinter.ttk', 'tkinter.messagebox']

# Adiciona módulos do selenium
hiddenimports += [
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.chrome.options',
]

# Adiciona outros módulos necessários
hiddenimports += [
    'pandas',
    'openpyxl',
    'bs4',
    'requests',
    'urllib3',
    'concurrent.futures',
]

# Adiciona classes e bots do projeto
hiddenimports += [
    'classes',
    'classes.file_manager',
    'classes.date_calculator',
    'classes.data_extractor',
    'classes.city_splitter',
    'classes.chrome_driver',
    'classes.config',
    'classes.parallel_processor',
    'bots',
    'bots.bot_bbdaf',
    'bots.bot_fnde',
]

# Adiciona arquivos de dados
datas += [
    ('cidades.txt', '.'),  # Arquivo de cidades
    ('assets/app_icon.ico', 'assets'),  # Ícone
    ('classes/*.py', 'classes'),  # Módulos Python
    ('bots/*.py', 'bots'),  # Bots
    ('gui1.py', '.'),  # GUI BB DAF
    ('gui2.py', '.'),  # GUI FNDE
    ('run_instance.py', '.'),  # Helper para execução paralela
]

# Configuração do Analysis
a = Analysis(
    ['main.py'],
    pathex=[base_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='Sistema_FVN',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False para não mostrar console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',
)

# Para macOS
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Sistema_FVN.app',
        icon='assets/app_icon.ico',
        bundle_identifier='com.fvn.sistema',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.10.0',
        },
    )