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

# Adiciona xlwings com todos os seus recursos
tmp_ret = collect_all('xlwings')
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
    'psutil',
    'PIL',           # Pillow (nome correto do módulo)
    'lxml',
    'bs4',           # beautifulsoup4 (nome correto do módulo)
    'requests',
    'urllib3',
    'concurrent.futures',
    'threading',
    'dateutil',      # python-dateutil (nome correto do módulo)
    'dotenv',        # python-dotenv (para .env config)
    'pymupdf4llm',   # PDF text extraction com IA
    'openai',        # OpenRouter API integration
]

# Adiciona módulos xlwings específicos
hiddenimports += [
    'xlwings._xlmac',      # Para macOS
    'xlwings._xlwindows',  # Para Windows
    'xlwings.conversion',
    'xlwings.main',
    'xlwings.utils',
]

# Adiciona dependências Windows (condicionalmente)
if sys.platform == 'win32':
    hiddenimports += [
        'win32com',
        'win32com.client',
        'win32com.client.makepy',
        'pythoncom',
    ]

# Adiciona módulos src.view (GUIs)
hiddenimports += [
    'src',
    'src.view',
    'src.view.gui1',
    'src.view.gui2',
    'src.view.gui3',
    'src.view.gui4',
    'src.view.gui5',
    'src.view.view_config',
    'src.view.modules',
    'src.view.modules.buttons',
    'src.view.modules.city_selector',
    'src.view.modules.loading_indicator',
]

# Adiciona módulos src.bots
hiddenimports += [
    'src.bots',
    'src.bots.bot_bbdaf',
    'src.bots.bot_fnde',
    'src.bots.bot_betha',
    'src.bots.bot_cons_fns',
    'src.bots.bot_portal_saude',
    'src.bots.betha',
    'src.bots.betha.bot_ribeirao',
]

# Adiciona módulos src.classes
hiddenimports += [
    'src.classes',
    'src.classes.__init__',
    'src.classes.chrome_driver',
    'src.classes.city_manager',
    'src.classes.city_splitter',
    'src.classes.config',
    'src.classes.config_page',
    'src.classes.data_extractor',
    'src.classes.date_calculator',
    'src.classes.report_generator',
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
    'src.classes.methods.pdf_to_table',
]

# Processa .env para garantir UTF-8 sem BOM
env_source = os.path.join(base_dir, 'src', 'config', '.env')
env_temp = os.path.join(base_dir, 'src', 'config', '.env.tmp')

if os.path.exists(env_source):
    # Lê o .env removendo BOM se existir
    with open(env_source, 'r', encoding='utf-8-sig') as f:
        env_content = f.read()

    # Salva sem BOM
    with open(env_temp, 'w', encoding='utf-8') as f:
        f.write(env_content)

    # Substitui o original temporariamente
    os.replace(env_temp, env_source)
    print("✓ .env processado: UTF-8 sem BOM garantido")

# Adiciona arquivos de dados
datas += [
    ('cidades.txt', '.'),  # Arquivo de cidades
    # user_config.json NÃO incluído - será criado dinamicamente no sistema do usuário
    # Assets estão em src/assets
    ('src/assets/app_icon.ico', 'src/assets'),  # Ícone principal
    ('src/assets/*.png', 'src/assets'),  # Imagens PNG
    ('src/assets/*.svg', 'src/assets'),  # Imagens SVG
    ('src/config/.env', 'src/config'),  # Configuração API keys (processado sem BOM)
    # Adiciona toda a estrutura src
    ('src/view/*.py', 'src/view'),
    ('src/view/modules/*.py', 'src/view/modules'),
    ('src/bots/*.py', 'src/bots'),
    ('src/bots/betha/*.py', 'src/bots/betha'),
    ('src/bots/betha/city_betha.json', 'src/bots/betha'),  # JSON de configuração das cidades
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
    excludes=['xlwings.rest'],  # Requer werkzeug, não é usado no projeto
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# Configuração diferente para macOS (onedir) vs outras plataformas (onefile)
if sys.platform == 'darwin':
    # macOS: usa onedir mode para evitar warning de deprecação
    exe = EXE(
        pyz,
        a.scripts,
        [],  # Sem binaries e datas embutidos para onedir
        exclude_binaries=True,
        name='Sistema_FVN',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # False para ocultar console
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='src/assets/app_icon.ico',
    )

    # Cria o bundle para macOS
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='Sistema_FVN',
    )

    app = BUNDLE(
        coll,
        name='Sistema_FVN.app',
        icon='src/assets/app_icon.ico',
        bundle_identifier='com.fvn.sistema',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSMinimumSystemVersion': '10.10.0',
        },
    )
else:
    # Windows/Linux: usa onefile mode tradicional
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
        console=False,  # False para ocultar console
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='src/assets/app_icon.ico',
    )