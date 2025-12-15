# Pacote classes para organização do projeto de web scraping
# Contém todas as classes necessárias para automação web

from .chrome_driver import ChromeDriverSimples
from .data_extractor import DataExtractor
from .date_calculator import DateCalculator
from .file.file_manager import FileManager
from .file.file_converter import FileConverter
from .file.path_manager import obter_caminho_dados, obter_caminho_recurso, copiar_arquivo_cidades_se_necessario
from .city_manager import CitySplitter
from .methods.parallel_processor import ProcessadorParalelo
from .methods.cancel_method import BotBase
from .methods.auto_execution import AutomaticExecutor
from .config import *

__all__ = [
    'ChromeDriverSimples',
    'DataExtractor',
    'DateCalculator',
    'FileManager',
    'FileConverter',
    'CitySplitter',
    'ProcessadorParalelo',
    'BotBase',
    'AutomaticExecutor',
    'obter_caminho_dados',
    'obter_caminho_recurso',
    'copiar_arquivo_cidades_se_necessario'
]