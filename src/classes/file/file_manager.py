"""
Classe responsável por gerenciar operações com arquivos
"""

import os
import sys
import platform
from typing import List
from src.classes.file.path_manager import obter_caminho_dados
from src.classes.city_manager import CityManager


class FileManager:
    """
    Classe responsável por gerenciar operações com arquivos
    
    Funcionalidades:
    - Carregar lista de cidades do arquivo cidades.txt
    - Validar existência e conteúdo de arquivos
    - Tratamento de erros relacionados a arquivos
    """
    
    def __init__(self, arquivo_cidades="cidades.txt"):
        """
        Inicializa o gerenciador de arquivos

        Args:
            arquivo_cidades (str): Nome do arquivo que contém a lista de cidades
                                 Por padrão usa 'cidades.txt' (852 municípios de MG)
        """
        # Armazena nome do arquivo (sem path completo ainda)
        self.arquivo_cidades = arquivo_cidades
        self.city_manager = CityManager()
    
    def verificar_arquivo_existe(self):
        """
        Verifica se o arquivo de cidades existe

        Returns:
            bool: True se o arquivo existe, False caso contrário
        """
        caminho_arquivo = obter_caminho_dados(self.arquivo_cidades)
        exists = os.path.exists(caminho_arquivo)
        if not exists:
            print(f"Arquivo '{self.arquivo_cidades}' não encontrado!")
        return exists
    
    def carregar_cidades(self) -> List[str]:
        """
        Carrega a lista de cidades do arquivo usando CityManager

        Returns:
            list: Lista de cidades (strings) ou lista vazia em caso de erro
        """
        # Delega para CityManager para cidades.txt
        if self.arquivo_cidades == "cidades.txt":
            return self.city_manager.obter_municipios_mg()
        else:
            # Arquivo customizado - mantém lógica original
            try:
                caminho = obter_caminho_dados(self.arquivo_cidades)
                if os.path.exists(caminho):
                    with open(caminho, "r", encoding="utf-8") as f:
                        cidades = [linha.strip() for linha in f if linha.strip()]
                    if cidades:
                        print(f"{len(cidades)} cidades carregadas")
                        return cidades
            except Exception as e:
                print(f"⚠ Erro ao carregar {self.arquivo_cidades}: {e}")
            return []
    
    def _exibir_cidades_carregadas(self, cidades):
        """
        Exibe as cidades carregadas para confirmação visual
        
        Args:
            cidades (list): Lista de cidades carregadas
        """
        print("Cidades que serão processadas:")
        for i, cidade in enumerate(cidades, 1):
            print(f"   {i}. {cidade}")
    
    def validar_lista_cidades(self, cidades):
        """
        Valida se a lista de cidades não está vazia
        
        Args:
            cidades (list): Lista de cidades para validar
        
        Returns:
            bool: True se a lista é válida, False caso contrário
        """
        if not cidades:
            print("Nenhuma cidade encontrada para processar.")
            return False
        
        return True 