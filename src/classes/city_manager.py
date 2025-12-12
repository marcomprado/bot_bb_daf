#!/usr/bin/env python3
# Gerenciador Centralizado de Listas de Municípios

import os
from typing import List, Optional
from src.classes.file.path_manager import obter_caminho_dados
from src.classes.config import MUNICIPIOS_MG_FALLBACK


class CityManager:
    # Singleton para gerenciar listas de municípios em toda a aplicação
    _instance = None
    _cache_cidades_estaticas: Optional[List[str]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def obter_municipios_mg(self) -> List[str]:
        # Retorna lista completa de municípios de MG (cidades.txt)
        if self._cache_cidades_estaticas is not None:
            return self._cache_cidades_estaticas.copy()

        try:
            caminho = obter_caminho_dados("cidades.txt")
            if os.path.exists(caminho):
                with open(caminho, "r", encoding="utf-8") as f:
                    cidades = [linha.strip() for linha in f if linha.strip()]

                if cidades:
                    self._cache_cidades_estaticas = cidades
                    print(f"✓ Carregados {len(cidades)} municípios de MG")
                    return cidades.copy()
        except Exception as e:
            print(f"⚠ Erro ao carregar cidades.txt: {e}")

        # Fallback para lista hardcoded em config.py
        print("⚠ Usando fallback MUNICIPIOS_MG_FALLBACK")
        self._cache_cidades_estaticas = MUNICIPIOS_MG_FALLBACK
        return MUNICIPIOS_MG_FALLBACK.copy()

    def limpar_cache(self):
        # Limpa cache (útil se arquivos forem modificados externamente)
        self._cache_cidades_estaticas = None
        print("✓ Cache de municípios limpo")
