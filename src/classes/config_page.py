#!/usr/bin/env python3
# Gerenciador de Configurações do Usuário

import os
import json
import sys
import platform
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    # Singleton para gerenciar configurações do usuário
    _instance = None
    _config_data = None
    _config_file_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self._config_file_path = self._get_config_file_path()
        self._ensure_config_directory()
        self._load_config()

    def _get_config_file_path(self) -> str:
        # Caminho do arquivo de configuração baseado no OS
        if hasattr(sys, '_MEIPASS'):
            if platform.system() == "Darwin":
                config_dir = os.path.expanduser("~/Library/Application Support/Sistema_FVN")
            elif platform.system() == "Windows":
                config_dir = os.path.expanduser("~/AppData/Local/Sistema_FVN")
            else:
                config_dir = os.path.expanduser("~/.config/sistema_fvn")
        else:
            config_dir = "."

        return os.path.join(config_dir, "user_config.json")

    def _ensure_config_directory(self):
        try:
            config_dir = os.path.dirname(self._config_file_path)
            if config_dir and config_dir != ".":
                os.makedirs(config_dir, exist_ok=True)
                print(f"✓ Diretório de configuração: {config_dir}")
        except Exception as e:
            print(f"⚠ Erro ao criar diretório de configuração: {e}")
    
    
    def _load_config(self):
        # Define configurações padrão
        if platform.system() == "Windows":
            default_geometry = {"width": 650, "height": 950}
        else:
            default_geometry = {"width": 600, "height": 950}

        default_config = {
            "download_directory": None,
            "window_geometry": default_geometry,
            "automatic_execution": {
                "enabled": False,
                "scripts": {
                    "bb_daf": False,
                    "fnde": False,
                    "betha": False
                },
                "period": "Diariamente",
                "weekdays": {
                    "seg": False,
                    "ter": False,
                    "qua": False,
                    "qui": False,
                    "sex": False,
                    "sab": False,
                    "dom": False
                },
                "time": "08:00",
                "execution_mode": "Individual",
                "parallel_instances": 2
            }
        }

        if os.path.exists(self._config_file_path):
            try:
                with open(self._config_file_path, 'r', encoding='utf-8') as f:
                    self._config_data = json.load(f)
                print(f"✓ Configurações carregadas de: {self._config_file_path}")
            except Exception as e:
                print(f"⚠ Erro ao carregar configurações: {e}")
                self._config_data = default_config
                self._save_config()
        else:
            print(f"✓ Criando novo arquivo de configuração: {self._config_file_path}")
            self._config_data = default_config
            self._save_config()

    def _save_config(self):
        try:
            config_dir = os.path.dirname(self._config_file_path)
            if config_dir and config_dir != ".":
                os.makedirs(config_dir, exist_ok=True)

            with open(self._config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"✗ Erro ao salvar configurações: {e}")

    def save_config_to_file(self):
        self._save_config()
    
    def get_download_directory(self) -> str:
        return self._config_data.get("download_directory", None)

    def is_download_directory_configured(self) -> bool:
        download_dir = self._config_data.get("download_directory", None)
        return download_dir is not None and download_dir.strip() != ""
    
    def set_download_directory(self, directory: str) -> bool:
        try:
            self._config_data["download_directory"] = directory
            self._save_config()
            return True
        except Exception as e:
            print(f"Erro ao definir diretório de download: {e}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        return self._config_data.get(key, default)
    
    def set_config(self, key: str, value: Any):
        # Define config em memória (não salva no arquivo)
        self._config_data[key] = value
    
    def get_all_config(self) -> Dict[str, Any]:
        return self._config_data.copy()
    
    def reset_to_defaults(self):
        # Preserva execução automática
        automatic_execution = self._config_data.get('automatic_execution', None)

        if platform.system() == "Windows":
            default_geometry = {"width": 650, "height": 950}
        else:
            default_geometry = {"width": 600, "height": 950}

        self._config_data["download_directory"] = None
        self._config_data["window_geometry"] = default_geometry

        if automatic_execution:
            self._config_data['automatic_execution'] = automatic_execution

        self._save_config()
    
    def get_file_path(self, filename: str) -> str:
        return os.path.join(self.get_download_directory(), filename)


def obter_caminho_configurado(nome_arquivo: str) -> str:
    # Wrapper para compatibilidade
    config_manager = ConfigManager()
    return config_manager.get_file_path(nome_arquivo)