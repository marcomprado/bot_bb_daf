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
    'xlrd',
    'xlwings',
    'psutil',
    'PIL',
    'Pillow',
    'lxml',
    'bs4',
    'beautifulsoup4',
    'requests',
    'urllib3',
    'concurrent.futures',
    'threading',
    'dateutil',
    'python_dateutil',
]

# Adiciona módulos src.view (GUIs)
hiddenimports += [
    'src',
    'src.view',
    'src.view.gui1',
    'src.view.gui2',
    'src.view.gui3',
    'src.view.view_config',
    'src.view.modules',
    'src.view.modules.buttons',
    'src.view.modules.city_selector',
]

# Adiciona módulos src.bots
hiddenimports += [
    'src.bots',
    'src.bots.bot_bbdaf',
    'src.bots.bot_fnde',
    'src.bots.bot_betha',
    'src.bots.betha',
    'src.bots.betha.bot_ribeirao',
]

# Adiciona módulos src.classes
hiddenimports += [
    'src.classes',
    'src.classes.__init__',
    'src.classes.chrome_driver',
    'src.classes.city_splitter',
    'src.classes.config',
    'src.classes.config_page',
    'src.classes.data_extractor',
    'src.classes.date_calculator',
    'src.classes.run_instance',
    # Submódulo file
    'src.classes.file',
    'src.classes.file.file_converter',
    'src.classes.file.file_manager',
    'src.classes.file.path_manager',
    # Submódulo methods
    'src.classes.methods',
    'src.classes.methods.auto_execution',
    'src.classes.methods.cancel_method',
    'src.classes.methods.parallel_processor',
]

# Adiciona arquivos de dados
datas += [
    ('cidades.txt', '.'),  # Arquivo de cidades
    ('user_config.json', '.'),  # Configuração do usuário
    ('assets/*.ico', 'assets'),  # Ícones
    ('assets/*.png', 'assets'),  # Imagens PNG
    # Adiciona toda a estrutura src
    ('src/view/*.py', 'src/view'),
    ('src/view/modules/*.py', 'src/view/modules'),
    ('src/bots/*.py', 'src/bots'),
    ('src/bots/betha/*.py', 'src/bots/betha'),
    ('src/bots/betha/*.json', 'src/bots/betha'),
    ('src/classes/*.py', 'src/classes'),
    ('src/classes/file/*.py', 'src/classes/file'),
    ('src/classes/methods/*.py', 'src/classes/methods'),
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