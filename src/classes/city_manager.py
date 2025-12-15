#!/usr/bin/env python3
# Gerenciamento de Listas de Municípios e Divisão para Processamento Paralelo

import os
import sys
import math
from typing import List, Optional, Tuple
from src.classes.file.path_manager import obter_caminho_dados


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

        caminho = obter_caminho_dados("cidades.txt")
        if not os.path.exists(caminho):
            raise FileNotFoundError(
                f"Arquivo obrigatório não encontrado: {caminho}\n"
                "O arquivo cidades.txt é necessário para o funcionamento do sistema."
            )

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                cidades = [linha.strip() for linha in f if linha.strip()]

            if not cidades:
                raise ValueError(f"O arquivo cidades.txt está vazio: {caminho}")

            self._cache_cidades_estaticas = cidades
            print(f"✓ Carregados {len(cidades)} municípios de MG")
            return cidades.copy()

        except Exception as e:
            raise RuntimeError(f"Erro ao carregar cidades.txt: {e}")

    def limpar_cache(self):
        # Limpa cache (útil se arquivos forem modificados externamente)
        self._cache_cidades_estaticas = None
        print("✓ Cache de municípios limpo")


class CitySplitter:
    # Divide lista de cidades em lotes para execução paralela

    def __init__(self, arquivo_cidades="cidades.txt"):
        # Inicializa o divisor de cidades
        if not os.path.isabs(arquivo_cidades):
            self.arquivo_cidades = arquivo_cidades
        else:
            self.arquivo_cidades = arquivo_cidades
        self.city_manager = CityManager()
        self.lista_cidades = []
        self._carregar_cidades()

    def _carregar_cidades(self):
        # Carrega lista completa de cidades usando CityManager
        if self.arquivo_cidades == "cidades.txt":
            self.lista_cidades = self.city_manager.obter_municipios_mg()
            return len(self.lista_cidades) > 0
        else:
            # Arquivo customizado ou caminho absoluto - mantém lógica original
            try:
                caminho = self.arquivo_cidades if os.path.isabs(self.arquivo_cidades) else obter_caminho_dados(self.arquivo_cidades)
                if os.path.exists(caminho):
                    with open(caminho, "r", encoding="utf-8") as f:
                        self.lista_cidades = [linha.strip() for linha in f if linha.strip()]
                    return len(self.lista_cidades) > 0
            except Exception as e:
                print(f"⚠ Erro ao carregar {self.arquivo_cidades}: {e}")
            # Fallback para lista completa
            self.lista_cidades = self.city_manager.obter_municipios_mg()
            return len(self.lista_cidades) > 0

    def obter_total_cidades(self):
        # Retorna o número total de cidades disponíveis
        return len(self.lista_cidades)

    def calcular_distribuicao(self, num_instancias):
        # Calcula como as cidades serão distribuídas entre as instâncias
        total_cidades = len(self.lista_cidades)

        if num_instancias <= 0 or num_instancias > total_cidades:
            return {
                'valido': False,
                'erro': f'Número de instâncias deve ser entre 1 e {total_cidades}'
            }

        # Calcula cidades por instância
        cidades_por_instancia = math.ceil(total_cidades / num_instancias)
        cidades_restantes = total_cidades % num_instancias

        # Distribui as cidades
        distribuicao = []
        inicio = 0

        for i in range(num_instancias):
            # Última instância pode ter menos cidades
            if i == num_instancias - 1:
                fim = total_cidades
            else:
                fim = inicio + cidades_por_instancia
                # Ajusta se passar do total
                if fim > total_cidades:
                    fim = total_cidades

            tamanho_lote = fim - inicio
            if tamanho_lote > 0:
                distribuicao.append({
                    'instancia': i + 1,
                    'inicio': inicio,
                    'fim': fim,
                    'quantidade': tamanho_lote
                })

            inicio = fim

        return {
            'valido': True,
            'total_cidades': total_cidades,
            'num_instancias': len(distribuicao),
            'distribuicao': distribuicao
        }

    def dividir_cidades(self, num_instancias):
        # Divide as cidades em lotes e cria arquivos para cada instância
        distribuicao = self.calcular_distribuicao(num_instancias)

        if not distribuicao['valido']:
            return distribuicao

        try:
            # Remove arquivos anteriores se existirem
            self._limpar_arquivos_instancias()

            arquivos_criados = []

            for lote in distribuicao['distribuicao']:
                # Extrai cidades para esta instância
                inicio = lote['inicio']
                fim = lote['fim']
                cidades_instancia = self.lista_cidades[inicio:fim]

                # Cria arquivo para esta instância - usa caminho de dados
                nome_arquivo = f"listed_cities_instancia_{lote['instancia']}.txt"
                caminho_arquivo = obter_caminho_dados(nome_arquivo)

                with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                    for cidade in cidades_instancia:
                        arquivo.write(f"{cidade}\n")

                arquivos_criados.append({
                    'arquivo': caminho_arquivo,
                    'instancia': lote['instancia'],
                    'cidades': cidades_instancia,
                    'quantidade': len(cidades_instancia)
                })

            return {
                'sucesso': True,
                'arquivos_criados': arquivos_criados,
                'distribuicao': distribuicao
            }

        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao criar arquivos: {str(e)}'
            }

    def _limpar_arquivos_instancias(self):
        # Remove arquivos de instâncias anteriores se existirem
        try:
            import glob

            # Procura arquivos no diretório de dados
            diretorio_dados = os.path.dirname(obter_caminho_dados("dummy"))
            if hasattr(sys, '_MEIPASS'):
                # No executável, usa o diretório de dados do usuário
                padrao = os.path.join(diretorio_dados, "listed_cities_instancia_*.txt")
            else:
                # No desenvolvimento, usa diretório atual
                padrao = "listed_cities_instancia_*.txt"

            arquivos = glob.glob(padrao)
            for arquivo in arquivos:
                try:
                    os.remove(arquivo)
                except:
                    pass
        except Exception:
            pass

    def obter_resumo_distribuicao(self, num_instancias):
        # Gera resumo textual da distribuição para exibir na interface
        distribuicao = self.calcular_distribuicao(num_instancias)

        if not distribuicao['valido']:
            return distribuicao['erro']

        total = distribuicao['total_cidades']
        linhas = [f"Total de cidades: {total}"]
        linhas.append(f"Divididas em {num_instancias} instancias:")

        for lote in distribuicao['distribuicao']:
            linhas.append(f"  Instancia {lote['instancia']}: {lote['quantidade']} cidades")

        return "\n".join(linhas)

    def validar_instancias(self, num_instancias):
        # Valida se o número de instâncias é viável
        if num_instancias < 1:
            return False, "Número mínimo é 1 instância"

        if num_instancias > 20:
            return False, "Número máximo é 20 instâncias"

        total_cidades = len(self.lista_cidades)
        if num_instancias > total_cidades:
            return False, f"Não é possível criar mais instâncias que cidades ({total_cidades})"

        return True, "Configuração válida"
