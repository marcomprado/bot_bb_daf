# Pacote classes para organização do projeto de web scraping
# Contém todas as classes necessárias para automação web

from .automation_core import AutomationCore
from .web_scraping_bot import WebScrapingBot
from .data_extractor import DataExtractor
from .date_calculator import DateCalculator
from .file_manager import FileManager

__all__ = [
    'AutomationCore',
    'WebScrapingBot', 
    'DataExtractor',
    'DateCalculator',
    'FileManager'
] 