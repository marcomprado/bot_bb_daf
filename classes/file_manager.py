"""
Classe responsável por gerenciar operações com arquivos
"""

import os


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
        """
        self.arquivo_cidades = arquivo_cidades
        print(f"📁 FileManager inicializado para arquivo: {self.arquivo_cidades}")
    
    def verificar_arquivo_existe(self):
        """
        Verifica se o arquivo de cidades existe
        
        Returns:
            bool: True se o arquivo existe, False caso contrário
        """
        exists = os.path.exists(self.arquivo_cidades)
        if not exists:
            print(f"❌ Arquivo '{self.arquivo_cidades}' não encontrado!")
        return exists
    
    def carregar_cidades(self):
        """
        Carrega a lista de cidades do arquivo
        
        Returns:
            list: Lista de cidades (strings) ou lista vazia em caso de erro
        """
        if not self.verificar_arquivo_existe():
            print("Crie o arquivo 'cidades.txt' com uma cidade por linha.")
            return []
        
        try:
            with open(self.arquivo_cidades, 'r', encoding='utf-8') as arquivo:
                # Lê todas as linhas, remove espaços em branco e filtra linhas vazias
                cidades = [linha.strip() for linha in arquivo if linha.strip()]
            
            if not cidades:
                print(f"❌ Arquivo '{self.arquivo_cidades}' está vazio!")
                return []
            
            print(f"✅ {len(cidades)} cidades carregadas do arquivo {self.arquivo_cidades}")
            self._exibir_cidades_carregadas(cidades)
            return cidades
            
        except UnicodeDecodeError:
            print(f"❌ Erro de codificação no arquivo '{self.arquivo_cidades}'. Verifique se está em UTF-8.")
            return []
        except PermissionError:
            print(f"❌ Sem permissão para ler o arquivo '{self.arquivo_cidades}'.")
            return []
        except Exception as e:
            print(f"❌ Erro inesperado ao carregar cidades: {e}")
            return []
    
    def _exibir_cidades_carregadas(self, cidades):
        """
        Exibe as cidades carregadas para confirmação visual
        
        Args:
            cidades (list): Lista de cidades carregadas
        """
        print("🏙️ Cidades que serão processadas:")
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
            print("❌ Nenhuma cidade encontrada para processar.")
            return False
        
        print(f"✅ Lista de cidades validada: {len(cidades)} cidades prontas para processamento.")
        return True 