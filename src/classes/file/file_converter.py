'''
Script para conversão de tipos de arquivo, de um para outro
Especializado em converter arquivos XLS para XLSX usando pandas
'''

import os
import glob
import shutil
import pandas as pd
from pathlib import Path
from src.classes.file.path_manager import obter_caminho_dados


class FileConverter:
    """
    Classe responsável por converter arquivos XLS para XLSX
    e gerenciar as pastas temporária, raw e converted
    """
    
    def __init__(self, municipio="ribeirao_neves"):
        """
        Inicializa o conversor de arquivos
        
        Args:
            municipio: Nome do município para organização das pastas
        """
        # Define os diretórios base usando path_manager
        self.base_dir = obter_caminho_dados(os.path.join("betha", municipio))
        self.temp_dir = os.path.join(self.base_dir, "temp")
        self.raw_dir = os.path.join(self.base_dir, "raw")
        self.converted_dir = os.path.join(self.base_dir, "converted")
        
        # Cria as pastas se não existirem
        self._criar_estrutura_pastas()
    
    def _criar_estrutura_pastas(self):
        """Cria a estrutura de pastas necessária"""
        for pasta in [self.temp_dir, self.raw_dir, self.converted_dir]:
            os.makedirs(pasta, exist_ok=True)
            print(f"  ✓ Pasta criada/verificada: {pasta}")
    
    def obter_pasta_temp(self):
        """Retorna o caminho da pasta temporária para downloads"""
        return self.temp_dir
    
    def contar_arquivos_temp(self):
        """
        Conta quantos arquivos XLS existem na pasta temporária
        
        Returns:
            int: Número de arquivos XLS na pasta temp
        """
        arquivos_xls = glob.glob(os.path.join(self.temp_dir, "*.xls"))
        return len(arquivos_xls)
    
    def mover_temp_para_raw(self):
        """
        Move arquivos da pasta temp para raw após confirmação de download
        
        Returns:
            int: Número de arquivos movidos
        """
        try:
            arquivos_xls = glob.glob(os.path.join(self.temp_dir, "*.xls"))
            contador = 0
            
            for arquivo in arquivos_xls:
                nome_arquivo = os.path.basename(arquivo)
                destino = os.path.join(self.raw_dir, nome_arquivo)
                
                # Se arquivo já existe no destino, adiciona numeração
                if os.path.exists(destino):
                    base, ext = os.path.splitext(nome_arquivo)
                    i = 1
                    while os.path.exists(os.path.join(self.raw_dir, f"{base}_{i}{ext}")):
                        i += 1
                    destino = os.path.join(self.raw_dir, f"{base}_{i}{ext}")
                
                shutil.move(arquivo, destino)
                contador += 1
                print(f"    ✓ Arquivo movido: {nome_arquivo}")
            
            print(f"  ✓ {contador} arquivos movidos de temp para raw")
            return contador
            
        except Exception as e:
            print(f"  ✗ Erro ao mover arquivos: {e}")
            return 0
    
    def limpar_pasta_temp(self):
        """Limpa todos os arquivos da pasta temporária"""
        try:
            arquivos = glob.glob(os.path.join(self.temp_dir, "*"))
            for arquivo in arquivos:
                os.remove(arquivo)
            print("  ✓ Pasta temp limpa")
        except Exception as e:
            print(f"  ✗ Erro ao limpar pasta temp: {e}")
    
    def converter_xls_para_xlsx(self, arquivo_xls):
        """
        Converte um arquivo XLS para XLSX
        
        Args:
            arquivo_xls: Caminho do arquivo XLS
            
        Returns:
            str: Caminho do arquivo XLSX convertido ou None se falhou
        """
        try:
            # Define o nome do arquivo de saída
            nome_base = os.path.basename(arquivo_xls)
            nome_sem_ext = os.path.splitext(nome_base)[0]
            arquivo_xlsx = os.path.join(self.converted_dir, f"{nome_sem_ext}.xlsx")
            
            # Lê o arquivo XLS
            df = pd.read_excel(arquivo_xls, engine='xlrd')
            
            # Salva como XLSX
            df.to_excel(arquivo_xlsx, index=False, engine='openpyxl')
            
            print(f"    ✓ Convertido: {nome_base} → {nome_sem_ext}.xlsx")
            return arquivo_xlsx
            
        except Exception as e:
            print(f"    ✗ Erro ao converter {arquivo_xls}: {e}")
            return None
    
    def converter_todos_raw(self):
        """
        Converte todos os arquivos XLS da pasta raw para XLSX
        
        Returns:
            tuple: (total_arquivos, arquivos_convertidos)
        """
        print("\n--- Iniciando conversão de arquivos XLS para XLSX ---")
        
        arquivos_xls = glob.glob(os.path.join(self.raw_dir, "*.xls"))
        total = len(arquivos_xls)
        convertidos = 0
        
        if total == 0:
            print("  ⚠ Nenhum arquivo XLS encontrado na pasta raw")
            return 0, 0
        
        print(f"  - {total} arquivos XLS encontrados para conversão")
        
        for arquivo in arquivos_xls:
            if self.converter_xls_para_xlsx(arquivo):
                convertidos += 1
        
        print(f"\n  ✓ Conversão concluída: {convertidos}/{total} arquivos convertidos")
        return total, convertidos
    
    def verificar_conversao_completa(self, esperados=10):
        """
        Verifica se todos os arquivos esperados foram convertidos
        
        Args:
            esperados: Número de arquivos esperados (padrão 10)
            
        Returns:
            bool: True se todos os arquivos foram convertidos
        """
        arquivos_convertidos = glob.glob(os.path.join(self.converted_dir, "*.xlsx"))
        quantidade = len(arquivos_convertidos)
        
        if quantidade >= esperados:
            print(f"  ✓ Conversão completa: {quantidade} arquivos XLSX disponíveis")
            return True
        else:
            print(f"  ⚠ Conversão incompleta: {quantidade}/{esperados} arquivos convertidos")
            return False
    
    def obter_arquivos_convertidos(self):
        """
        Retorna lista de arquivos XLSX convertidos

        Returns:
            list: Lista de caminhos dos arquivos XLSX
        """
        return glob.glob(os.path.join(self.converted_dir, "*.xlsx"))

    def verificar_arquivo_duplicado(self, nome_arquivo):
        """
        Verifica se o arquivo é uma duplicata (contém (1), (01), (2), etc.)

        Args:
            nome_arquivo: Nome do arquivo para verificar

        Returns:
            bool: True se é duplicata, False caso contrário
        """
        import re
        # Padrão para detectar duplicatas: arquivo (1).xls, arquivo(01).xls, etc.
        padrao_duplicata = r'\s*\(\d+\)\s*\.xls$'
        return bool(re.search(padrao_duplicata, nome_arquivo))

    def obter_arquivos_unicos_temp(self):
        """
        Retorna lista de arquivos únicos na pasta temp (exclui duplicatas)

        Returns:
            list: Lista de caminhos dos arquivos únicos
        """
        arquivos_xls = glob.glob(os.path.join(self.temp_dir, "*.xls"))
        arquivos_unicos = []

        for arquivo in arquivos_xls:
            nome = os.path.basename(arquivo)
            if not self.verificar_arquivo_duplicado(nome):
                arquivos_unicos.append(arquivo)

        return arquivos_unicos

    def contar_arquivos_unicos_temp(self):
        """
        Conta quantos arquivos únicos existem na pasta temp

        Returns:
            int: Número de arquivos únicos
        """
        return len(self.obter_arquivos_unicos_temp())

    def aguardar_downloads_completos(self, timeout=30):
        """
        Aguarda todos os downloads serem completados

        Args:
            timeout: Tempo máximo de espera em segundos

        Returns:
            bool: True se downloads completados, False se timeout
        """
        import time
        tempo_inicial = time.time()
        arquivos_parciais = []

        while time.time() - tempo_inicial < timeout:
            # Procura por arquivos temporários do Chrome (.crdownload)
            temp_chrome = glob.glob(os.path.join(self.temp_dir, "*.crdownload"))
            temp_part = glob.glob(os.path.join(self.temp_dir, "*.part"))
            temp_tmp = glob.glob(os.path.join(self.temp_dir, "*.tmp"))

            arquivos_parciais = temp_chrome + temp_part + temp_tmp

            if not arquivos_parciais:
                # Nenhum arquivo parcial, downloads completos
                time.sleep(2)  # Aguarda mais 2 segundos para garantir
                return True

            time.sleep(1)

        if arquivos_parciais:
            print(f"  ⚠ Timeout: {len(arquivos_parciais)} downloads ainda em andamento")

        return False

    def mover_unicos_temp_para_raw(self):
        """
        Move apenas arquivos únicos da pasta temp para raw

        Returns:
            int: Número de arquivos únicos movidos
        """
        try:
            arquivos_unicos = self.obter_arquivos_unicos_temp()
            contador = 0

            for arquivo in arquivos_unicos:
                nome_arquivo = os.path.basename(arquivo)
                destino = os.path.join(self.raw_dir, nome_arquivo)

                # Se arquivo já existe no destino, adiciona numeração
                if os.path.exists(destino):
                    base, ext = os.path.splitext(nome_arquivo)
                    i = 1
                    while os.path.exists(os.path.join(self.raw_dir, f"{base}_{i}{ext}")):
                        i += 1
                    destino = os.path.join(self.raw_dir, f"{base}_{i}{ext}")

                shutil.move(arquivo, destino)
                contador += 1
                print(f"    ✓ Arquivo único movido: {nome_arquivo}")

            # Limpa arquivos duplicados que sobraram
            arquivos_duplicados = glob.glob(os.path.join(self.temp_dir, "*.xls"))
            for dup in arquivos_duplicados:
                os.remove(dup)
                print(f"    ✗ Duplicata removida: {os.path.basename(dup)}")

            print(f"  ✓ {contador} arquivos únicos movidos de temp para raw")
            return contador

        except Exception as e:
            print(f"  ✗ Erro ao mover arquivos únicos: {e}")
            return 0