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

## License

**PROPRIETARY SOFTWARE LICENSE**

Copyright 2025 Marco Martinelli do Carmo Prado. All rights reserved.

This software is proprietary. The source code is made available for viewing purposes only. Copying, modification, distribution, or commercial use is expressly prohibited without written permission from the copyright holder.

View the complete terms in the [LICENSE](LICENSE) file.

---

Developed by Marco Martinelli do Carmo Prado
