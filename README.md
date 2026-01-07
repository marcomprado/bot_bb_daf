# Sistema FVN - Municipal Data Automation System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://www.selenium.dev)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-orange.svg)](https://github.com/TomSchimansky/CustomTkinter)

A comprehensive Python-based web scraping automation system designed for extracting municipal financial and administrative data from Brazilian government systems. The system features a modern GUI, parallel processing capabilities, and scheduled automation for efficient data collection across 852 municipalities in Minas Gerais.

## Overview

Sistema FVN is a multi-module automation platform that interfaces with four distinct government systems:

**BB DAF System**: Extracts public data from the Fundo de Participação dos Municípios of Banco do Brasil, providing detailed municipal revenue information with customizable date ranges and multi-city batch processing.

**FNDE System**: Extracts the public data from Fundo Nacional de Desenvolvimento da Educação to collect education funding data, enabling automated retrieval and structured export of educational financial information.

**Betha Cloud System**: Automates municipal accounting system interactions. Supports dynamic PPA Pluri Annual calculation and municipality-specific report generation with automated XLS to XLSX conversion using xlwings to preserve the original formatting.

**Consulta FNS System**: Extracts public health fund bank account data through automation form submission and file download workflows.

The system currently supports 852 municipalities in Minas Gerais, with capabilities for up to 5 threads parallel processing, scheduled execution, and comprehensive error handling.

## Key Features

- **Parallel Processing**: Thread-based (GUI) and subprocess-based (CLI) execution modes supporting up to 5 concurrent instances with intelligent city distribution
- **Automatic Scheduled Execution**: Configurable daily or weekly automation with per-script enable/disable and time-based triggers
- **Modern GUI Interface**: CustomTkinter-based tabbed interface with real-time progress tracking and intuitive controls
- **Cross-Platform Executable**: PyInstaller builds for Windows (single executable), macOS (.app bundle), and Linux
- **Intelligent File Management**: Automatic directory creation, file naming conventions, and format conversion (XLS to XLSX)
- **Configuration Management**: Dual-layer configuration with system settings (URLs, selectors, timeouts) and user preferences (download paths, schedules)

## Architecture & Design

### Object-Oriented Architecture

The system follows a strict separation of concerns with a three-layer architecture:

**UI Layer** (`src/view/`): Pure presentation logic handling user input and display. Each scraping system has a dedicated GUI module (gui1.py - gui4.py) that only collects parameters and displays results. No business logic resides in UI components.

**Business Logic Layer** (`src/bots/`): Core automation engines implementing Selenium-based web scraping workflows. Each bot inherits from BotBase and implements system-specific navigation, data extraction, and file generation logic.

**Utility Layer** (`src/classes/`): Shared components providing ChromeDriver management, Excel generation, date calculations, file operations, and configuration management.

### Class Hierarchy

```
BotBase (cancel_method.py)
├── BotBBDAF (bot_bbdaf.py)
├── BotFNDE (bot_fnde.py)
├── BotBetha (bot_betha.py)
└── BotConsFNS (bot_cons_fns.py)

AutomaticExecutor (auto_execution.py)
ProcessadorParalelo (parallel_processor.py)
DataExtractor (data_extractor.py)
ChromeDriverSimples (chrome_driver.py)
```

### Design Patterns

- **Template Method**: BotBase provides cancellation framework inherited by all bots
- **Factory Pattern**: ButtonFactory creates standardized UI components
- **Strategy Pattern**: ProcessadorParalelo supports interchangeable execution modes (threads/subprocesses)
- **Separation of Concerns**: Strict layer boundaries between UI, business logic, and utilities

### Data Flow

1. User input collected via GUI.
2. main.py orchestrates bot instantiation with appropriate configuration
3. Bot executes automation workflow (navigation, form filling, data extraction)
4. DataExtractor processes HTML and generates formatted Excel files
5. Files saved to organized directory structure with automatic naming
6. Status and progress reported back to UI or console

## Technical Stack

**Core Technologies**:
- Python 3.8+ 
- Selenium 4.0+ 
- CustomTkinter 5.2+ 
- Google Chrome + ChromeDriver

**Key Dependencies**:
- Pandas 2.0+ (data manipulation and analysis)
- BeautifulSoup4 4.12+ (HTML parsing)
- OpenPyXL 3.1+ (Excel file generation)
- xlwings 0.30+ (XLS to XLSX conversion)
- Pillow 10.0+ (image processing)
- psutil 5.9+ (process and system monitoring)
- python-dateutil 2.8+ (date handling utilities)
- lxml 4.9+ (XML/HTML processing)

**Codebase Statistics**: Approximately 7,700 lines of Python code across core modules

## Project Structure

```
bot-bb/
├── main.py                          # Entry point - orchestrates entire system
├── main.spec                        # PyInstaller build configuration
├── requirements.txt                 # Python dependencies
├── user_config.json                 # User preferences (download dir, schedules)
├── cidades.txt                      # 852 MG municipalities reference
├── listed_cities.txt               # Dynamic city selection output
├── LICENSE                          # Proprietary license
├── CLAUDE.md                        # AI assistant instructions
│
├── src/                            # Source code directory
│   ├── view/                       # UI Layer (Pure presentation)
│   │   ├── gui1.py                # BB DAF interface
│   │   ├── gui2.py                # FNDE interface
│   │   ├── gui3.py                # Betha interface
│   │   ├── gui4.py                # Consulta FNS interface
│   │   ├── view_config.py         # Settings page (ConfigGUI)
│   │   └── modules/               # Reusable UI components
│   │       └── buttons.py         # Button factory
│   │
│   ├── bots/                      # Business Logic Layer
│   │   ├── bot_bbdaf.py          # BB DAF automation engine
│   │   ├── bot_fnde.py           # FNDE scraping engine
│   │   ├── bot_betha.py          # Betha Cloud automation
│   │   ├── bot_cons_fns.py       # Consulta FNS scraping
│   │   └── betha/                # City-specific scripts
│   │       ├── city_betha.json   # Login credentials per municipality
│   │       └── bot_ribeirao.py   # Example: Ribeirão das Neves logic
│   │
│   ├── classes/                   # Utility Layer
│   │   ├── central.py           # Centralized system configuration
│   │   ├── config_page.py        # User settings manager
│   │   ├── chrome_driver.py      # Direct ChromeDriver connection
│   │   ├── data_extractor.py     # Excel generation & formatting
│   │   ├── date_calculator.py    # Date range utilities
│   │   ├── city_splitter.py      # City distribution algorithm
│   │   ├── run_instance.py       # Subprocess execution helper
│   │   │
│   │   ├── methods/              # Advanced execution methods
│   │   │   ├── parallel_processor.py  # Parallel execution manager
│   │   │   ├── auto_execution.py      # Scheduled automation
│   │   │   └── cancel_method.py       # BotBase with cancellation
│   │   │
│   │   └── file/                 # File handling utilities
│   │       ├── file_manager.py   # General file operations
│   │       ├── file_converter.py # XLS to XLSX conversion
│   │       └── path_manager.py   # Path resolution for executables
│   │
│   └── assets/                    # Static resources
│       ├── app_icon.ico          # Application icon
│       └── *.png                 # UI icons

```

## System-Specific Features

### BB DAF System
- Multi-city batch processing (852 MG municipalities)
- Custom date range selection with validation
- Parallel execution (up to 5 concurrent instances)
- Excel generation with formatting and formulas
- Automatic retry on transient failures
- City distribution algorithm for load balancing

### FNDE System
- Year selection (2000-2025)
- Municipality filtering
- Table extraction with formatting preservation
- Automatic file naming by municipality

### Betha Cloud System
- Dynamic PPA calculation (4-year blocks from 1998)
- Municipality-specific report processing logic
- XLS to XLSX conversion using xlwings
- Temporary download directory management

### Consulta FNS System
- State/municipality cascading selection
- Excel export automation
- File renaming by city
- Progress tracking and status updates

## License

**PROPRIETARY SOFTWARE LICENSE**

Copyright 2025 Marco Martinelli do Carmo Prado. All rights reserved.

This software is proprietary. The source code is made available for viewing purposes only. Copying, modification, distribution, or commercial use is expressly prohibited without written permission from the copyright holder.

View the complete terms in the [LICENSE](LICENSE) file.

---

Developed by Marco Martinelli do Carmo Prado
