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
    
    
    def _load_config(self):
        """Carrega as configurações do arquivo JSON que sempre existe"""
        try:
            with open(self._config_file_path, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            # Se houver erro na leitura, usa config mínimo
            self._config_data = {
                "download_directory": "arquivos_baixados",
                "window_geometry": {"width": 900, "height": 750}
            }
    
    def _save_config(self):
        """Salva as configurações no arquivo JSON - uso interno"""
        try:
            with open(self._config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def save_config_to_file(self):
        """Método público para salvar configurações - chamado explicitamente pela UI"""
        self._save_config()
    
    def get_download_directory(self) -> str:
        """
        Obtém o diretório de download configurado

        Returns:
            str: Caminho do diretório de download
        """
        # Apenas retorna o que está configurado, sem modificar nada
        return self._config_data.get("download_directory", "arquivos_baixados")
    
    def set_download_directory(self, directory: str) -> bool:
        """
        Define o diretório de download E SALVA no arquivo
        Este é um dos poucos métodos que salva explicitamente

        Args:
            directory: Caminho do novo diretório

        Returns:
            bool: True se foi salvo com sucesso
        """
        try:
            self._config_data["download_directory"] = directory
            self._save_config()  # Salva explicitamente pois usuário escolheu novo diretório
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
        Define um valor de configuração específico NA MEMÓRIA
        NÃO salva automaticamente no arquivo

        Args:
            key: Chave da configuração
            value: Valor a ser definido
        """
        self._config_data[key] = value
        # NÃO salva automaticamente - removido self._save_config()
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Obtém todas as configurações
        
        Returns:
            Dict com todas as configurações
        """
        return self._config_data.copy()
    
    def reset_to_defaults(self):
        """Redefine APENAS diretório e geometria para valores padrão, preserva o resto"""
        # Preserva configurações de execução automática
        automatic_execution = self._config_data.get('automatic_execution', None)

        # Reseta apenas campos básicos
        self._config_data["download_directory"] = "arquivos_baixados"
        self._config_data["window_geometry"] = {
            "width": 900,
            "height": 750
        }

        # Mantém execução automática se existia
        if automatic_execution:
            self._config_data['automatic_execution'] = automatic_execution

        # Salva explicitamente pois usuário clicou no botão
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