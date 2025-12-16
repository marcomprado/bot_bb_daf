#!/usr/bin/env python3
"""
Logging utility for PDF-to-Table converter with PyInstaller support.
Writes logs to file in user's config directory when console is hidden.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path


def get_log_directory():
    """
    Get appropriate log directory based on environment.

    Returns:
        str: Path to log directory (created if doesn't exist)
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller EXE - use OS-specific user directory
        import platform
        system = platform.system()

        if system == "Darwin":
            # macOS
            log_dir = os.path.expanduser("~/Library/Application Support/Sistema_FVN/logs")
        elif system == "Windows":
            # Windows
            log_dir = os.path.expanduser("~/AppData/Local/Sistema_FVN/logs")
        else:
            # Linux
            log_dir = os.path.expanduser("~/.config/sistema_fvn/logs")
    else:
        # Development mode - use project directory
        # Get project root (3 levels up from this file)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        log_dir = os.path.join(project_root, 'logs')

    # Create directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    return log_dir


def setup_pdf_logger(name='pdf_to_table'):
    """
    Setup logger that writes to both file and console.

    In PyInstaller builds with hidden console, file logging is critical.

    Args:
        name (str): Logger name (default: 'pdf_to_table')

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler - always logs everything
    log_dir = get_log_directory()
    log_filename = f'{name}_{datetime.now().strftime("%Y%m%d")}.log'
    log_file = os.path.join(log_dir, log_filename)

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler - only if console exists (dev mode or console enabled)
    # In PyInstaller with console=False, sys.stdout/stderr might be None
    try:
        if sys.stdout is not None:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
    except:
        # If console setup fails, just use file logging
        pass

    # Log initialization message
    logger.info(f"{'='*60}")
    logger.info(f"Logger inicializado: {name}")
    logger.info(f"Arquivo de log: {log_file}")
    logger.info(f"Modo: {'PyInstaller EXE' if hasattr(sys, '_MEIPASS') else 'Desenvolvimento'}")
    if hasattr(sys, '_MEIPASS'):
        logger.info(f"_MEIPASS: {sys._MEIPASS}")
    logger.info(f"{'='*60}")

    return logger


def log_and_print(logger, level, message):
    """
    Log to file and print to console (if available).

    This is useful for messages that should appear in GUI console
    even when running as EXE.

    Args:
        logger (logging.Logger): Logger instance
        level (int): Logging level (e.g., logging.INFO)
        message (str): Message to log/print
    """
    # Log to file
    logger.log(level, message)

    # Also try print for GUI console compatibility
    try:
        print(message)
    except:
        # If print fails (e.g., no stdout), just rely on file logging
        pass
