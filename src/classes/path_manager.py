#!/usr/bin/env python3
"""
Gerenciador de Caminhos e Arquivos
Centraliza toda a lógica de resolução de caminhos e manipulação de arquivos
"""

import os
import sys
import platform


def obter_caminho_recurso(nome_arquivo):
    """
    Obtém o caminho correto para um arquivo de recurso
    Funciona tanto em desenvolvimento quanto em executável empacotado
    
    Args:
        nome_arquivo (str): Nome do arquivo de recurso
        
    Returns:
        str: Caminho completo para o arquivo
    """
    try:
        # Se estamos em um executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # No executável, usa o diretório temporário do PyInstaller
            base_path = sys._MEIPASS
        else:
            # No desenvolvimento, usa o diretório do projeto
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        return os.path.join(base_path, nome_arquivo)
    except Exception:
        # Fallback para caminho relativo
        return nome_arquivo


def obter_caminho_dados(nome_arquivo):
    """
    Obtém o caminho correto para arquivos de dados (que precisam ser modificáveis)
    
    Args:
        nome_arquivo (str): Nome do arquivo de dados
        
    Returns:
        str: Caminho completo para o arquivo de dados
    """
    try:
        # Importa ConfigManager aqui para evitar importação circular
        from src.classes.config_page import ConfigManager
        config_manager = ConfigManager()
        
        # Casos especiais que NÃO devem usar o diretório configurado
        arquivos_sistema = ['cidades.txt', 'listed_cities.txt']
        
        if any(nome_arquivo.endswith(arquivo) for arquivo in arquivos_sistema):
            # Arquivos do sistema ficam no diretório da aplicação
            if hasattr(sys, '_MEIPASS'):
                # Para executável PyInstaller
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
        else:
            # Para arquivos_baixados e outros, usa o diretório configurado
            return config_manager.get_file_path(nome_arquivo)
            
    except Exception:
        # Fallback para o comportamento original
        if hasattr(sys, '_MEIPASS'):
            if platform.system() == "Darwin":  # macOS
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            elif platform.system() == "Windows":
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            else:  # Linux
                user_data_dir = os.path.expanduser("~/.sistema_fvn")
            
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)
                
            return os.path.join(user_data_dir, nome_arquivo)
        else:
            return nome_arquivo


def copiar_arquivo_cidades_se_necessario():
    """
    Copia o arquivo cidades.txt para o diretório de dados do usuário se necessário
    """
    try:
        # Se estamos em um executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            arquivo_origem = obter_caminho_recurso("cidades.txt")
            arquivo_destino = obter_caminho_dados("cidades.txt")
            
            # Se o arquivo não existe no diretório do usuário, copia do recurso
            if not os.path.exists(arquivo_destino) and os.path.exists(arquivo_origem):
                import shutil
                shutil.copy2(arquivo_origem, arquivo_destino)
                print(f"Arquivo cidades.txt copiado para: {arquivo_destino}")
    except Exception as e:
        print(f"Aviso: Erro ao copiar arquivo cidades.txt - {e}")