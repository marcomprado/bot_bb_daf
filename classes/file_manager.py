"""
Classe responsável por gerenciar operações com arquivos
"""

import os
import sys
import platform


def obter_caminho_dados(nome_arquivo):
    """
    Obtém o caminho correto para arquivos de dados (que precisam ser modificáveis)
    
    Args:
        nome_arquivo (str): Nome do arquivo de dados
        
    Returns:
        str: Caminho completo para o arquivo de dados
    """
    try:
        # Se estamos em um executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # Para arquivos de dados modificáveis, usa o diretório do usuário
            if platform.system() == "Darwin":  # macOS
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            elif platform.system() == "Windows":
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            else:  # Linux
                user_data_dir = os.path.expanduser("~/.sistema_fvn")
            
            # Cria o diretório se não existir
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)
                
            return os.path.join(user_data_dir, nome_arquivo)
        else:
            # No desenvolvimento, usa o diretório atual
            return nome_arquivo
    except Exception:
        # Fallback para caminho relativo
        return nome_arquivo


class FileManager:
    """
    Classe responsável por gerenciar operações com arquivos
    
    Funcionalidades:
    - Carregar lista de cidades do arquivo cidades.txt
    - Validar existência e conteúdo de arquivos
    - Tratamento de erros relacionados a arquivos
    """
    
    def __init__(self, arquivo_cidades="listed_cities.txt"):
        """
        Inicializa o gerenciador de arquivos
        
        Args:
            arquivo_cidades (str): Nome do arquivo que contém a lista de cidades
                                 Por padrão usa 'listed_cities.txt' (arquivo dinâmico)
                                 'cidades.txt' é o arquivo estático de referência
        """
        # Usa caminho compatível com executável
        self.arquivo_cidades = obter_caminho_dados(arquivo_cidades)
    
    def verificar_arquivo_existe(self):
        """
        Verifica se o arquivo de cidades existe
        
        Returns:
            bool: True se o arquivo existe, False caso contrário
        """
        exists = os.path.exists(self.arquivo_cidades)
        if not exists:
            print(f"Arquivo '{self.arquivo_cidades}' não encontrado!")
            if "listed_cities.txt" in self.arquivo_cidades:
                print("   Use a interface gráfica (gui_main.py) para selecionar cidades.")
        return exists
    
    def carregar_cidades(self):
        """
        Carrega a lista de cidades do arquivo
        
        Returns:
            list: Lista de cidades (strings) ou lista vazia em caso de erro
        """
        if not self.verificar_arquivo_existe():
            if "listed_cities.txt" in self.arquivo_cidades:
                print("Use a interface gráfica (gui_main.py) para selecionar cidades.")
            else:
                print(f"Crie o arquivo '{self.arquivo_cidades}' com uma cidade por linha.")
            return []
        
        try:
            with open(self.arquivo_cidades, 'r', encoding='utf-8') as arquivo:
                # Lê todas as linhas, remove espaços em branco e filtra linhas vazias
                cidades = [linha.strip() for linha in arquivo if linha.strip()]
            
            if not cidades:
                print(f"Arquivo '{self.arquivo_cidades}' está vazio!")
                return []
            
            print(f"{len(cidades)} cidades carregadas")
            return cidades
            
        except UnicodeDecodeError:
            print(f"Erro de codificação no arquivo '{self.arquivo_cidades}'. Verifique se está em UTF-8.")
            return []
        except PermissionError:
            print(f"Sem permissão para ler o arquivo '{self.arquivo_cidades}'.")
            return []
        except Exception as e:
            print(f"Erro inesperado ao carregar cidades: {e}")
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