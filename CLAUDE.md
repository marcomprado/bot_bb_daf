# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run main system (GUI interface - recommended)
python main.py

# Run in CLI mode with auto city detection
python main.py --cli [data_inicial] [data_final]

# Run parallel processing via CLI
python main.py --parallel [num_instances]

# Build executable using PyInstaller
pyinstaller main.spec

# Check dependencies (included in main.py)
python main.py  # includes dependency verification
```

### Virtual Environment
```bash
# Create virtual environment
python -m venv venv     # Windows
python3 -m venv venv    # macOS/Linux

# Activate virtual environment
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

## Architecture Overview

This is a Python web scraping automation system with triple functionality:
1. **BB DAF**: Extracting FPM (Fundo de Participação dos Municípios) data from Banco do Brasil
2. **FNDE**: Scraping data from FNDE (Fundo Nacional de Desenvolvimento da Educação) system
3. **BETHA**: Automating Betha Cloud municipal accounting system with city-specific report processing

The system was recently refactored for clear separation of concerns with dedicated folders for different responsibilities.

### Core Architecture

**System Entry Point**: `main.py` orchestrates the entire system, providing both GUI and CLI modes, and manages the triple-scraper interface with tabbed navigation.

**Business Logic Layer**: `src/bots/` directory contains the scraping engines:
- **BotBBDAF** (`src/bots/bot_bbdaf.py`): Complete BB DAF automation with single/parallel processing
- **BotFNDE** (`src/bots/bot_fnde.py`): FNDE system automation
- **BotBetha** (`src/bots/bot_betha.py`): Betha Cloud system automation with dynamic city configuration
- **City-Specific Scripts** (`src/bots/betha/`): Municipality-specific processing logic after reaching "Relatórios Favoritos"

**Utility Layer**: `src/classes/` directory contains shared utilities and configuration:
- **ChromeDriverSimples** (`src/classes/chrome_driver.py`): Direct ChromeDriver connection without webdriver-manager
- **DataExtractor** (`src/classes/data_extractor.py`): HTML parsing and Excel generation with formatting
- **Configuration** (`src/classes/config.py`): Centralized settings, CSS selectors, and constants
- **ConfigPage** (`src/classes/config_page.py`): Manages user preferences stored in `user_config.json`
- **DateCalculator** (`src/classes/date_calculator.py`): Date range utilities for report processing
- **CitySplitter** (`src/classes/city_splitter.py`): City distribution algorithm for parallel processing
- **BotBase** (`src/classes/methods/cancel_method.py`): Base class providing cancellation support to all bots
- **ProcessadorParalelo** (`src/classes/methods/parallel_processor.py`): Manages parallel execution (thread/subprocess modes)
- **AutomaticExecutor** (`src/classes/methods/auto_execution.py`): Scheduled execution system for automated runs
- **FileManager** (`src/classes/file/file_manager.py`): File operations and directory management
- **FileConverter** (`src/classes/file/file_converter.py`): XLS to XLSX conversion using xlwings for Betha downloads
- **PathManager** (`src/classes/file/path_manager.py`): Path resolution for bundled executables

**UI Layer**: Separate GUI files for each scraper with tabbed interface:
- **GUI1** (`src/view/gui1.py`): Pure UI for BB DAF system (parameter collection only)
- **GUI2** (`src/view/gui2.py`): Pure UI for FNDE system
- **GUI3** (`src/view/gui3.py`): Pure UI for Betha system (year/city/parallel selection)
- **ConfigGUI** (`src/view/view_config.py`): Settings page for download directory and automatic execution
- **UI Modules** (`src/view/modules/`): Reusable components (buttons, city selector)

### Key Architectural Principles

1. **Separation of Concerns**: Each layer has distinct responsibilities
2. **No Business Logic in UI**: GUIs only collect parameters and display results
3. **Unified Entry Point**: `main.py` composes and coordinates all components
4. **Parallel Processing**: Built-in support for multiple Chrome instances via ProcessadorParalelo
5. **Configuration Centralization**: All settings moved to `classes/config.py`

### Data Flow

**BB DAF Flow**:
1. User selects cities and dates via GUI1 or CLI
2. main.py creates BotBBDAF instance with DataExtractor
3. Bot handles complete automation: navigation → form filling → data extraction → Excel generation
4. Files saved to `arquivos_baixados/YYYY-MM-DD/` directory

**FNDE Flow**:
1. User selects year and municipality via GUI2
2. main.py creates BotFNDE instance
3. Bot processes FNDE website and generates data files
4. Files saved to `arquivos_baixados/fnde/` directory

**Betha Flow**:
1. User selects years (1998-2029) and cities via GUI3, with parallel execution options
2. main.py creates BotBetha instance with city configuration from `city_betha.json`
3. Bot navigates: login → select municipality → calculate PPA (4-year blocks) → select exercise year → press F4 → reach "Relatórios Favoritos"
4. City-specific script branching executes municipality-specific report processing
5. Files saved to `arquivos_baixados/betha/` directory

**Parallel Processing Flow**:
1. ProcessadorParalelo divides cities into chunks
2. Multiple BotBBDAF instances run concurrently (threads or subprocesses)
3. Results are consolidated and reported

### File Organization

```
├── main.py                     # System orchestrator and entry point
├── main.spec                   # PyInstaller build specification
├── requirements.txt            # Python dependencies
├── user_config.json            # User preferences (download dir, auto-execution settings)
├── src/                        # Source code directory
│   ├── view/                   # UI layer
│   │   ├── gui1.py            # BB DAF UI (parameters only)
│   │   ├── gui2.py            # FNDE UI (parameters only)
│   │   ├── gui3.py            # Betha UI (year/city/parallel selection)
│   │   ├── view_config.py     # Settings UI (ConfigGUI)
│   │   └── modules/           # UI components (buttons, city_selector)
│   ├── bots/                   # Business logic engines
│   │   ├── bot_bbdaf.py       # BB DAF complete automation logic
│   │   ├── bot_fnde.py        # FNDE scraping logic
│   │   ├── bot_betha.py       # Betha Cloud automation with dynamic city config
│   │   └── betha/             # City-specific Betha processing scripts
│   │       ├── city_betha.json        # Login credentials per municipality
│   │       └── bot_[city_name].py     # City-specific report logic
│   ├── classes/                # Shared utilities and config
│   │   ├── config.py          # Centralized configuration (URLs, selectors, timeouts)
│   │   ├── config_page.py     # User config manager (reads/writes user_config.json)
│   │   ├── chrome_driver.py   # Direct ChromeDriver connection
│   │   ├── data_extractor.py  # Excel generation and formatting
│   │   ├── date_calculator.py # Date range utilities
│   │   ├── city_splitter.py   # City distribution for parallel processing
│   │   ├── run_instance.py    # Helper for subprocess parallel execution
│   │   ├── methods/           # Advanced execution methods
│   │   │   ├── parallel_processor.py  # Parallel execution manager
│   │   │   ├── auto_execution.py      # Scheduled/automatic execution
│   │   │   └── cancel_method.py       # BotBase with cancellation support
│   │   └── file/              # File handling utilities
│   │       ├── file_manager.py        # General file operations
│   │       ├── file_converter.py      # XLS to XLSX conversion (xlwings)
│   │       └── path_manager.py        # Path resolution for executables
│   └── assets/                 # Static assets (icons, images)
├── cidades.txt                 # Static reference (852 MG cities)
├── listed_cities.txt           # Dynamic file generated by GUI city selection
├── arquivos_baixados/          # Output directory for downloaded/generated files
│   ├── YYYY-MM-DD/            # BB DAF files organized by date
│   ├── fnde/                  # FNDE system outputs
│   └── betha/                 # Betha Cloud reports
```

### Browser Requirements

- Google Chrome must be installed
- ChromeDriver is now connected directly (no webdriver-manager dependency)
- Direct connection improves reliability on macOS ARM64 systems

### Configuration Management

The system uses two types of configuration:

**System Configuration** (`src/classes/config.py`):
- `SISTEMA_CONFIG`: URLs, timeouts, pauses (optimized for speed)
- `SELETORES_CSS`: CSS selectors for web elements
- `FNDE_CONFIG`: FNDE-specific settings
- `ARQUIVOS_CONFIG`: File paths and encoding
- `MENSAGENS`: Log messages and status indicators

**User Configuration** (`user_config.json` managed by `src/classes/config_page.py`):
- `download_directory`: Custom output directory for files
- `window_geometry`: GUI window size preferences
- `automatic_execution`: Scheduled execution settings
  - `enabled`: Boolean to activate/deactivate auto-execution
  - `scripts`: Which bots to run (bb_daf, fnde, betha)
  - `period`: "Diariamente" or "Semanalmente"
  - `weekdays`: Which days of week to run (seg, ter, qua, qui, sex, sab, dom)
  - `time`: Execution time (HH:MM format)
  - `execution_mode`: "Sequencial" or "Paralela"
  - `parallel_instances`: Number of concurrent instances for parallel mode

### Import Path Structure

The codebase uses a `src/` directory structure with automatic path resolution:

- **main.py** (root): Imports modules using `src.` prefix (e.g., `from src.view.gui1 import GUI1`)
- **Files within src/**: Use `sys.path.append()` to resolve imports to the root directory, then import with `src.` prefix
- **Key pattern**: Most files add three directory levels up to path: `sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))`

### Parallel Processing

Two modes available via ProcessadorParalelo:
1. **Thread-based**: Multiple BotBBDAF instances in threads (GUI mode)
2. **Subprocess-based**: Multiple Python processes (CLI mode)

### Betha System Architecture

The Betha Cloud automation system has unique characteristics that require special handling:

#### **City Configuration System**:
- Each municipality requires different login credentials stored in `src/bots/betha/city_betha.json`
- Format: `{"cidades": [{"nome": "City Name", "Login": "username", "Senha": "password"}]}`
- Municipality names are automatically normalized (accents removed) for web element matching

#### **Dynamic Year/PPA Calculation**:
- PPAs (Plano Plurianual) are calculated automatically based on selected year
- Formula: PPAs are 4-year blocks starting from 1998 (1998-2001, 2002-2005, 2006-2009, etc.)
- Exercise year matches the selected processing year

#### **City-Specific Script Branching**:
- After reaching "Relatórios Favoritos", execution branches to city-specific modules
- Pattern: `src/bots/betha/bot_[city_name].py` (e.g., `bot_ribeirao.py` for Ribeirão das Neves)
- Each city module implements specific report processing logic
- Fallback to generic processing for cities without specific scripts

#### **Report Processing Logic**:
- Reports are processed individually with proper waits and error handling
- Current month detection for limiting processing scope
- XLS export format selection and automated execution
- Visual feedback with time delays for development debugging

#### **File Conversion for Betha**:
- Betha Cloud exports XLS format (old Excel format)
- FileConverter uses xlwings library for reliable XLS to XLSX conversion
- Temporary download directory created per municipality: `arquivos_baixados/betha/[city_name]/temp/`
- Files are converted and moved to final location: `arquivos_baixados/betha/[city_name]/[year]/`
- Temporary files are cleaned up after successful conversion

### Testing & Validation

Manual validation through:
- GUI parameter validation (dates, city selection, year ranges)
- Chrome browser detection at startup
- File permissions and directory creation
- Dependency verification in main.py
- City configuration JSON validation

### Automatic Execution System

The system supports scheduled automatic execution via `AutomaticExecutor` class:

**Activation**:
- Configured through ConfigGUI settings page (gear icon in main window)
- Settings stored in `user_config.json` under `automatic_execution`
- Monitoring thread starts on application launch if `enabled: true`

**Execution Flow**:
1. AutomaticExecutor checks current time against configured schedule
2. If time matches and enabled, creates appropriate bot instance(s)
3. Executes in sequential or parallel mode based on configuration
4. Logs execution status and errors
5. Waits for next scheduled time

**Scheduling Options**:
- Daily execution at specific time
- Weekly execution on selected weekdays
- Per-script enable/disable (BB DAF, FNDE, Betha)
- Parallel mode with configurable instance count

### Bot Cancellation System

All bots inherit from `BotBase` class providing cancellation support:

**Implementation**:
- `self.cancelado` flag tracked by all bot operations
- `verificar_cancelamento()` method raises exception if cancelled
- Called between automation steps to allow graceful termination

**Usage in GUI**:
- "Cancelar" button sets bot's `cancelado` flag to `True`
- Bot checks flag periodically and terminates current operation
- Browser closes and resources are cleaned up
- Status returned to GUI for user feedback

### Selenium Automation Patterns

#### **XPath Selectors for Select2 Dropdowns**:
For Select2 dropdowns, use: `//span[@id='select2-chosen-X']/parent::a`
- Uses unique span ID (more reliable)
- Navigates to parent `<a>` element that needs to be clicked
- Doesn't depend on CSS classes that may change
- Cleaner XPath syntax

### PyInstaller Build Configuration

The `main.spec` file handles cross-platform executable generation:

**macOS Build** (onedir mode):
- Uses `BUNDLE` to create `.app` package
- Directory structure: `Sistema_FVN.app/Contents/MacOS/`
- Prevents deprecation warnings on macOS
- Includes proper bundle identifier and Info.plist

**Windows/Linux Build** (onefile mode):
- Single executable file: `Sistema_FVN.exe` or `Sistema_FVN`
- All dependencies embedded in executable
- No console window (`console=False`)

**Hidden Imports**:
- All `src` modules explicitly listed to ensure inclusion
- Selenium, pandas, openpyxl, xlwings, customtkinter
- City-specific Betha scripts in `src/bots/betha/`

**Data Files**:
- `cidades.txt`, `user_config.json`, `city_betha.json`
- Application icon and assets
- All Python source files for runtime imports