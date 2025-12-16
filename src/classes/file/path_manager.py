#!/usr/bin/env python3
# Gerenciador de Caminhos e Arquivos

import os
import sys
import platform


def obter_caminho_recurso(nome_arquivo):
    # Obtém o caminho correto para um arquivo de recurso
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


def obter_diretorio_config():
    # Obtém o diretório de configuração da aplicação
    if hasattr(sys, '_MEIPASS'):
        if platform.system() == "Darwin":
            config_dir = os.path.expanduser("~/Library/Application Support/Sistema_FVN")
        elif platform.system() == "Windows":
            config_dir = os.path.expanduser("~/AppData/Local/Sistema_FVN")
        else:
            config_dir = os.path.expanduser("~/.config/sistema_fvn")
    else:
        config_dir = "."

    if config_dir and config_dir != ".":
        os.makedirs(config_dir, exist_ok=True)

    return config_dir


def obter_caminho_dados(nome_arquivo):
    # Obtém o caminho correto para arquivos de dados
    # Arquivos de sistema ficam no diretório de configuração
    arquivos_sistema = ['cidades.txt']

    if any(nome_arquivo.endswith(arquivo) for arquivo in arquivos_sistema):
        return os.path.join(obter_diretorio_config(), nome_arquivo)

    # Arquivos de download usam diretório configurado
    try:
        from src.classes.config_page import ConfigManager
        config_manager = ConfigManager()
        download_dir = config_manager.get_download_directory()

        if download_dir is None:
            raise ValueError(
                "Diretório de download não configurado. "
                "Configure nas Configurações do sistema."
            )

        # Evita duplicação de "arquivos_baixados" no caminho
        if nome_arquivo == "arquivos_baixados":
            return download_dir
        elif nome_arquivo.startswith("arquivos_baixados/") or nome_arquivo.startswith("arquivos_baixados\\"):
            nome_arquivo_clean = nome_arquivo.replace("arquivos_baixados/", "").replace("arquivos_baixados\\", "")
            return config_manager.get_file_path(nome_arquivo_clean)
        else:
            return config_manager.get_file_path(nome_arquivo)

    except ImportError:
        raise ValueError("ConfigManager não disponível")


def copiar_arquivo_cidades_se_necessario():
    # Copia cidades.txt para o diretório de configuração (apenas em executáveis)
    try:
        if hasattr(sys, '_MEIPASS'):
            arquivo_origem = obter_caminho_recurso("cidades.txt")
            arquivo_destino = obter_caminho_dados("cidades.txt")

            if not os.path.exists(arquivo_destino) and os.path.exists(arquivo_origem):
                import shutil
                shutil.copy2(arquivo_origem, arquivo_destino)
                print(f"✓ cidades.txt copiado para: {arquivo_destino}")
    except Exception as e:
        print(f"⚠ Erro ao copiar cidades.txt: {e}")