#!/usr/bin/env python3
"""
Bot de scraping para o sistema FNDE (Fundo Nacional de Desenvolvimento da Educação)
Extrai dados de liberações financeiras para municípios de Minas Gerais
"""

from selenium import webdriver
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes.chrome_driver import ChromeDriverSimples
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
import platform
import time
from datetime import datetime
from typing import List, Dict, Optional


def obter_caminho_dados(nome_arquivo):
    """
    Obtém o caminho correto para arquivos de dados (reutilizado do data_extractor.py)
    """
    try:
        if hasattr(sys, '_MEIPASS'):
            if platform.system() == "Darwin":
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            elif platform.system() == "Windows":
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            else:
                user_data_dir = os.path.expanduser("~/.sistema_fvn")
            
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)
                
            return os.path.join(user_data_dir, nome_arquivo)
        else:
            return nome_arquivo
    except Exception:
        return nome_arquivo


class BotFNDE:
    """
    Bot de scraping para o site do FNDE
    
    Funcionalidades:
    - Navega ao site FNDE com parâmetros específicos
    - Preenche formulário (ano, município, entidade)
    - Extrai tabela de resultados preservando formatação
    - Salva em Excel com nome personalizado
    - Processa múltiplas cidades automaticamente
    """
    
    def __init__(self, timeout=15):
        """
        Inicializa o bot FNDE
        
        Args:
            timeout (int): Tempo limite para aguardar elementos (segundos)
        """
        self.base_url = "https://www.fnde.gov.br/pls/simad/internet_fnde.LIBERACOES_01_PC"
        self.timeout = timeout
        self.navegador = None
        self.wait = None
        self.municipios_mg = self._carregar_municipios_mg()
        
        # Configuração de diretórios
        self.diretorio_base = obter_caminho_dados("arquivos_baixados")
        self.diretorio_fnde = os.path.join(self.diretorio_base, "fnde")
        self.data_hoje = datetime.now().strftime("%Y-%m-%d")
        self.diretorio_saida = os.path.join(self.diretorio_fnde, self.data_hoje)
        
        self._criar_diretorios()
    
    def _criar_diretorios(self):
        """Cria estrutura de diretórios necessária"""
        try:
            for diretorio in [self.diretorio_base, self.diretorio_fnde, self.diretorio_saida]:
                if not os.path.exists(diretorio):
                    os.makedirs(diretorio)
        except Exception as e:
            print(f"Aviso: Erro ao criar diretórios - {e}")
    
    def _carregar_municipios_mg(self) -> List[str]:
        """
        Carrega lista de municípios de MG do arquivo cidades.txt
        
        Returns:
            List[str]: Lista com nomes dos municípios
        """
        try:
            caminho_cidades = obter_caminho_dados("cidades.txt")
            if os.path.exists(caminho_cidades):
                with open(caminho_cidades, "r", encoding="utf-8") as arquivo:
                    cidades = [linha.strip() for linha in arquivo if linha.strip()]
                print(f"Carregados {len(cidades)} municípios de MG")
                return cidades
            else:
                print("Arquivo cidades.txt não encontrado. Usando lista padrão.")
                return ["BELO HORIZONTE", "UBERLANDIA", "CONTAGEM"]
        except Exception as e:
            print(f"Erro ao carregar municípios: {e}")
            return ["BELO HORIZONTE"]
    
    def configurar_navegador(self) -> bool:
        """
        Configura o navegador Chrome usando conexão direta simples
        
        Returns:
            bool: True se configuração bem-sucedida
        """
        try:
            # Usa a classe simples para conectar direto ao ChromeDriver
            driver_simples = ChromeDriverSimples()
            self.navegador = driver_simples.conectar()
            
            if self.navegador:
                self.wait = WebDriverWait(self.navegador, self.timeout)
                print("✓ Navegador Chrome configurado com sucesso")
                return True
            else:
                print("✗ Falha ao conectar com ChromeDriver")
                return False
            
        except Exception as e:
            print(f"✗ Erro ao configurar navegador: {e}")
            return False
    
    def abrir_pagina_fnde(self, ano: str, municipio: Optional[str] = None) -> bool:
        """
        Abre a página FNDE com parâmetros iniciais
        
        Args:
            ano (str): Ano para consulta (2000-2025)
            municipio (str, optional): Nome do município específico
            
        Returns:
            bool: True se página carregada com sucesso
        """
        try:
            # URL com parâmetros iniciais
            url_completa = f"{self.base_url}?p_ano={ano}&p_programa=&p_uf=MG"
            
            print(f"Abrindo página FNDE para ano {ano}...")
            self.navegador.get(url_completa)
            
            # Aguarda formulário carregar
            select_ano = self.wait.until(
                EC.presence_of_element_located((By.NAME, "p_ano"))
            )
            
            print("Página FNDE carregada com sucesso")
            return True
            
        except TimeoutException:
            print("Timeout: Página demorou para carregar")
            return False
        except Exception as e:
            print(f"Erro ao abrir página FNDE: {e}")
            return False
    
    def preencher_formulario(self, ano: str, municipio: str) -> bool:
        """
        Preenche o formulário FNDE com os dados fornecidos
        
        Args:
            ano (str): Ano para consulta
            municipio (str): Nome do município
            
        Returns:
            bool: True se preenchimento bem-sucedido
        """
        try:
            print(f"Preenchendo formulário para {municipio} - {ano}")
            
            # 1. Seleciona o ano
            select_ano = Select(self.navegador.find_element(By.NAME, "p_ano"))
            select_ano.select_by_value(ano)
            time.sleep(0.5)
            
            # 2. Aguarda dropdown de municípios carregar e seleciona município
            municipio_encontrado = self._selecionar_municipio(municipio)
            if not municipio_encontrado:
                print(f"Município '{municipio}' não encontrado na lista")
                return False
            
            # 3. Seleciona entidade como PREFEITURA (sempre "02")
            select_entidade = Select(self.navegador.find_element(By.NAME, "p_tp_entidade"))
            select_entidade.select_by_value("02")  # PREFEITURA
            time.sleep(0.3)
            
            print("Formulário preenchido com sucesso")
            return True
            
        except NoSuchElementException as e:
            print(f"Elemento não encontrado no formulário: {e}")
            return False
        except Exception as e:
            print(f"Erro ao preencher formulário: {e}")
            return False
    
    def _selecionar_municipio(self, nome_municipio: str) -> bool:
        """
        Seleciona município no dropdown
        
        Args:
            nome_municipio (str): Nome do município a ser selecionado
            
        Returns:
            bool: True se município foi encontrado e selecionado
        """
        try:
            select_municipio = Select(self.navegador.find_element(By.NAME, "p_municipio"))
            
            # Procura pelo município na lista de opções
            for opcao in select_municipio.options:
                texto_opcao = opcao.text.upper().strip()
                nome_procurado = nome_municipio.upper().strip()
                
                # Busca exata ou contém o nome
                if nome_procurado == texto_opcao or nome_procurado in texto_opcao:
                    select_municipio.select_by_visible_text(opcao.text)
                    print(f"Município selecionado: {opcao.text}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao selecionar município: {e}")
            return False
    
    def executar_busca(self) -> bool:
        """
        Clica no botão Buscar e aguarda resultado
        
        Returns:
            bool: True se busca executada com sucesso
        """
        try:
            print("Executando busca...")
            
            # Clica no botão Buscar
            botao_buscar = self.navegador.find_element(By.NAME, "buscar")
            botao_buscar.click()
            
            # Aguarda página de resultados carregar
            # Procura por uma tabela ou indicador de que os dados carregaram
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.TAG_NAME, "table")),
                    EC.presence_of_element_located((By.CLASS_NAME, "tabela")),
                    EC.presence_of_element_located((By.XPATH, "//table")),
                    EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Liberações")
                )
            )
            
            print("Busca executada e resultados carregados")
            return True
            
        except TimeoutException:
            print("Timeout: Resultados demoraram para carregar")
            return False
        except Exception as e:
            print(f"Erro ao executar busca: {e}")
            return False
    
    def extrair_tabela_html(self) -> str:
        """
        Extrai a tabela HTML completa da página de resultados
        
        Returns:
            str: HTML da tabela ou string vazia se erro
        """
        try:
            print("Extraindo tabela HTML...")
            
            # Obtém HTML completo da página
            html_pagina = self.navegador.page_source
            
            # Usa BeautifulSoup para encontrar e extrair tabelas
            soup = BeautifulSoup(html_pagina, 'html.parser')
            
            # Procura por tabelas na página
            tabelas = soup.find_all('table')
            
            if tabelas:
                # Pega a maior tabela (provavelmente a de dados)
                tabela_principal = max(tabelas, key=lambda t: len(str(t)))
                print(f"Tabela extraída com {len(tabela_principal.find_all('tr'))} linhas")
                return str(tabela_principal)
            else:
                print("Nenhuma tabela encontrada na página")
                return ""
                
        except Exception as e:
            print(f"Erro ao extrair tabela HTML: {e}")
            return ""
    
    def salvar_excel(self, html_tabela: str, municipio: str, ano: str) -> bool:
        """
        Salva tabela HTML em arquivo Excel preservando formatação
        
        Args:
            html_tabela (str): HTML da tabela
            municipio (str): Nome do município
            ano (str): Ano da consulta
            
        Returns:
            bool: True se arquivo salvo com sucesso
        """
        try:
            if not html_tabela:
                print("HTML da tabela está vazio")
                return False
            
            print(f"Salvando arquivo Excel para {municipio}...")
            
            # Converte HTML para DataFrame do pandas
            df_lista = pd.read_html(html_tabela)
            
            if not df_lista:
                print("Não foi possível converter HTML para DataFrame")
                return False
            
            # Pega o primeiro/maior DataFrame
            df = df_lista[0] if len(df_lista) == 1 else max(df_lista, key=len)
            
            # Cria nome do arquivo: ANO_MUNICIPIO.xlsx
            nome_municipio_limpo = municipio.replace(" ", "_").replace("/", "_")
            nome_arquivo = f"{ano}_{nome_municipio_limpo}.xlsx"
            caminho_arquivo = os.path.join(self.diretorio_saida, nome_arquivo)
            
            # Salva em Excel com formatação
            with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados_FNDE')
                
                # Aplica formatação básica
                worksheet = writer.sheets['Dados_FNDE']
                
                # Ajusta largura das colunas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Arquivo salvo: {caminho_arquivo}")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar arquivo Excel: {e}")
            return False
    
    def processar_municipio(self, ano: str, municipio: str) -> Dict[str, any]:
        """
        Processa um município específico
        
        Args:
            ano (str): Ano para consulta
            municipio (str): Nome do município
            
        Returns:
            Dict: Resultado do processamento
        """
        resultado = {
            'municipio': municipio,
            'ano': ano,
            'sucesso': False,
            'erro': None,
            'arquivo': None
        }
        
        try:
            print(f"\n=== Processando: {municipio} ({ano}) ===")
            
            # 1. Abre página FNDE
            if not self.abrir_pagina_fnde(ano, municipio):
                resultado['erro'] = "Falha ao abrir página FNDE"
                return resultado
            
            # 2. Preenche formulário
            if not self.preencher_formulario(ano, municipio):
                resultado['erro'] = "Falha ao preencher formulário"
                return resultado
            
            # 3. Executa busca
            if not self.executar_busca():
                resultado['erro'] = "Falha ao executar busca"
                return resultado
            
            # 4. Extrai tabela
            html_tabela = self.extrair_tabela_html()
            if not html_tabela:
                resultado['erro'] = "Falha ao extrair tabela"
                return resultado
            
            # 5. Salva Excel
            if not self.salvar_excel(html_tabela, municipio, ano):
                resultado['erro'] = "Falha ao salvar arquivo Excel"
                return resultado
            
            resultado['sucesso'] = True
            resultado['arquivo'] = f"{ano}_{municipio.replace(' ', '_')}.xlsx"
            print(f"✓ Processamento concluído para {municipio}")
            
        except Exception as e:
            resultado['erro'] = f"Erro inesperado: {str(e)}"
            print(f"✗ Erro ao processar {municipio}: {e}")
        
        return resultado
    
    def processar_todos_municipios(self, ano: str) -> Dict[str, any]:
        """
        Processa todos os municípios de MG para um ano específico
        
        Args:
            ano (str): Ano para consulta
            
        Returns:
            Dict: Estatísticas do processamento
        """
        print(f"\n=== INICIANDO PROCESSAMENTO DE TODOS OS MUNICÍPIOS - ANO {ano} ===")
        print(f"Total de municípios: {len(self.municipios_mg)}")
        
        estatisticas = {
            'total': len(self.municipios_mg),
            'sucessos': 0,
            'erros': 0,
            'municipios_processados': [],
            'municipios_erro': []
        }
        
        for i, municipio in enumerate(self.municipios_mg, 1):
            print(f"\nProgresso: {i}/{len(self.municipios_mg)} municípios")
            
            resultado = self.processar_municipio(ano, municipio)
            
            if resultado['sucesso']:
                estatisticas['sucessos'] += 1
                estatisticas['municipios_processados'].append(municipio)
            else:
                estatisticas['erros'] += 1
                estatisticas['municipios_erro'].append({
                    'municipio': municipio,
                    'erro': resultado['erro']
                })
            
            # Pequena pausa entre municípios
            time.sleep(0.5)
        
        # Calcula taxa de sucesso
        estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100
        
        print(f"\n=== PROCESSAMENTO CONCLUÍDO ===")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
        
        return estatisticas
    
    def fechar_navegador(self):
        """Fecha o navegador"""
        try:
            if self.navegador:
                self.navegador.quit()
                print("Navegador fechado")
        except Exception as e:
            print(f"Erro ao fechar navegador: {e}")
    
    def obter_lista_municipios(self) -> List[str]:
        """
        Retorna lista de municípios carregados
        
        Returns:
            List[str]: Lista de municípios de MG
        """
        return self.municipios_mg.copy()


# Função de teste/exemplo
def main():
    """Função de teste do bot FNDE"""
    bot = BotFNDE()
    
    try:
        if not bot.configurar_navegador():
            print("Falha ao configurar navegador")
            return 1
        
        # Teste com um município específico
        resultado = bot.processar_municipio("2025", "BELO HORIZONTE")
        
        if resultado['sucesso']:
            print("Teste executado com sucesso!")
        else:
            print(f"Teste falhou: {resultado['erro']}")
        
    except KeyboardInterrupt:
        print("\nProcessamento interrompido pelo usuário")
    finally:
        bot.fechar_navegador()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())