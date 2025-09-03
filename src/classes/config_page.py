#!/usr/bin/env python3
"""
Gerenciador de Configurações do Usuário
Gerencia as preferências do usuário, incluindo diretório de download
"""

import os
import json
import sys
import platform
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Singleton para gerenciar configurações do usuário
    """
    
    _instance = None
    _config_data = None
    _config_file_path = None
    
    def __new__(cls):
        """Implementa padrão Singleton"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa o gerenciador de configurações"""
        self._config_file_path = self._get_config_file_path()
        self._ensure_config_dir()
        self._load_config()
    
    def _get_config_file_path(self) -> str:
        """
        Obtém o caminho do arquivo de configuração baseado no sistema operacional
        
        Returns:
            str: Caminho completo para o arquivo de configuração
        """
        # Se estamos em um executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # Para executável, usa diretório de dados do usuário
            if platform.system() == "Darwin":  # macOS
                config_dir = os.path.expanduser("~/Library/Application Support/Sistema_FVN")
            elif platform.system() == "Windows":
                config_dir = os.path.expanduser("~/AppData/Local/Sistema_FVN")
            else:  # Linux
                config_dir = os.path.expanduser("~/.config/sistema_fvn")
        else:
            # Em desenvolvimento, usa diretório local
            config_dir = "."
        
        return os.path.join(config_dir, "user_config.json")
    
    def _ensure_config_dir(self):
        """Garante que o diretório de configuração existe"""
        config_dir = os.path.dirname(self._config_file_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
    
    def _get_default_download_dir(self) -> str:
        """
        Obtém o diretório de download padrão baseado no sistema operacional
        
        Returns:
            str: Caminho padrão para downloads
        """
        if hasattr(sys, '_MEIPASS'):
            # Para executável
            if platform.system() in ["Darwin", "Windows"]:
                default_dir = os.path.expanduser("~/Documents/Sistema_FVN/arquivos_baixados")
            else:  # Linux
                default_dir = os.path.expanduser("~/.sistema_fvn/arquivos_baixados")
        else:
            # Em desenvolvimento, usa diretório local
            default_dir = "arquivos_baixados"
        
        # Cria o diretório se não existir
        if not os.path.exists(default_dir):
            os.makedirs(default_dir, exist_ok=True)
        
        return default_dir
    
    def _load_config(self):
        """Carrega as configurações do arquivo JSON"""
        default_config = {
            "download_directory": self._get_default_download_dir(),
            "window_geometry": {
                "width": 900,
                "height": 750
            }
        }
        
        if os.path.exists(self._config_file_path):
            try:
                with open(self._config_file_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge com configurações padrão (preserva novos campos)
                    default_config.update(loaded_config)
                    self._config_data = default_config
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
                self._config_data = default_config
        else:
            self._config_data = default_config
            self._save_config()
    
    def _save_config(self):
        """Salva as configurações no arquivo JSON"""
        try:
            with open(self._config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def get_download_directory(self) -> str:
        """
        Obtém o diretório de download configurado
        
        Returns:
            str: Caminho do diretório de download
        """
        download_dir = self._config_data.get("download_directory", self._get_default_download_dir())
        
        # Verifica se o diretório existe, senão usa o padrão
        if not os.path.exists(download_dir):
            download_dir = self._get_default_download_dir()
            self.set_download_directory(download_dir)
        
        return download_dir
    
    def set_download_directory(self, directory: str) -> bool:
        """
        Define o diretório de download
        
        Args:
            directory: Caminho do novo diretório
            
        Returns:
            bool: True se foi salvo com sucesso
        """
        try:
            # Valida se o diretório existe ou pode ser criado
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            self._config_data["download_directory"] = directory
            self._save_config()
            return True
        except Exception as e:
            print(f"Erro ao definir diretório de download: {e}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração específico
        
        Args:
            key: Chave da configuração
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor da configuração ou padrão
        """
        return self._config_data.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """
        Define um valor de configuração específico
        
        Args:
            key: Chave da configuração
            value: Valor a ser definido
        """
        self._config_data[key] = value
        self._save_config()
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Obtém todas as configurações
        
        Returns:
            Dict com todas as configurações
        """
        return self._config_data.copy()
    
    def reset_to_defaults(self):
        """Redefine todas as configurações para os valores padrão"""
        self._config_data = {
            "download_directory": self._get_default_download_dir(),
            "window_geometry": {
                "width": 900,
                "height": 750
            }
        }
        self._save_config()
    
    def get_file_path(self, filename: str) -> str:
        """
        Obtém o caminho completo para um arquivo no diretório de download
        
        Args:
            filename: Nome do arquivo ou subpasta
            
        Returns:
            str: Caminho completo
        """
        return os.path.join(self.get_download_directory(), filename)


# Função auxiliar para manter compatibilidade com código existente
def obter_caminho_configurado(nome_arquivo: str) -> str:
    """
    Função wrapper para obter caminho usando ConfigManager
    Mantém compatibilidade com código existente
    
    Args:
        nome_arquivo: Nome do arquivo ou subpasta
        
    Returns:
        str: Caminho completo configurado
    """
    config_manager = ConfigManager()
    return config_manager.get_file_path(nome_arquivo)