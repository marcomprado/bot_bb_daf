# Pacote classes para organização do projeto de web scraping
# Contém todas as classes necessárias para automação web

from .chrome_driver import ChromeDriverSimples
from .data_extractor import DataExtractor
from .date_calculator import DateCalculator
from .file_manager import FileManager
from .city_splitter import CitySplitter
from .parallel_processor import ProcessadorParalelo
from .config import *

__all__ = [
    'ChromeDriverSimples',
    'DataExtractor',
    'DateCalculator',
    'FileManager',
    'CitySplitter',
    'ProcessadorParalelo'
]