#!/usr/bin/env python3
"""
Bot de scraping para o sistema FNDE (Fundo Nacional de Desenvolvimento da Educação)
Extrai dados de liberações financeiras para municípios de Minas Gerais
"""

from selenium import webdriver
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.classes.chrome_driver import ChromeDriverSimples
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
import io
from datetime import datetime
from typing import List, Dict, Optional
from src.classes.path_manager import obter_caminho_dados


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
    
    def __init__(self, timeout=8):
        """
        Inicializa o bot FNDE
        
        Args:
            timeout (int): Tempo limite para aguardar elementos (segundos) - otimizado para 8s
        """
        self.base_url = "https://www.fnde.gov.br/pls/simad/internet_fnde.LIBERACOES_01_PC"
        self.timeout = timeout
        self.navegador = None
        self.wait = None
        self.municipios_mg = self._carregar_municipios_mg()
        
        # Flags de controle para evitar vazamento de memória
        self._cancelado = False
        self._em_execucao = False
        
        # Configuração de diretórios
        # Chama apenas "fnde" para evitar duplicação da pasta arquivos_baixados
        self.diretorio_fnde = obter_caminho_dados("fnde")
        # Para compatibilidade com código existente
        self.diretorio_base = os.path.dirname(self.diretorio_fnde)
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
            time.sleep(0.2)
            
            # 2. Aguarda dropdown de municípios carregar e seleciona município
            # Aguarda explicitamente o dropdown carregar após mudança do ano
            WebDriverWait(self.navegador, 5).until(
                EC.element_to_be_clickable((By.NAME, "p_municipio"))
            )
            
            municipio_encontrado = self._selecionar_municipio(municipio)
            if not municipio_encontrado:
                print(f"Município '{municipio}' não encontrado na lista")
                return False
            
            # 3. Seleciona entidade como PREFEITURA (sempre "02")
            select_entidade = Select(self.navegador.find_element(By.NAME, "p_tp_entidade"))
            select_entidade.select_by_value("02")  # PREFEITURA
            time.sleep(0.1)
            
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
            
            # Procura pelo município na lista de opções (otimizado)
            nome_procurado = nome_municipio.upper().strip()
            
            # Primeiro tenta busca exata para economia de tempo
            for opcao in select_municipio.options:
                texto_opcao = opcao.text.upper().strip()
                if nome_procurado == texto_opcao:
                    select_municipio.select_by_visible_text(opcao.text)
                    print(f"Município selecionado: {opcao.text}")
                    return True
            
            # Se não encontrou exato, tenta busca por contém
            for opcao in select_municipio.options:
                texto_opcao = opcao.text.upper().strip()
                if nome_procurado in texto_opcao:
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
            
            # Aguarda página de resultados carregar (otimizado para 6s)
            # Procura por uma tabela ou indicador de que os dados carregaram
            WebDriverWait(self.navegador, 6).until(
                EC.any_of(
                    EC.presence_of_element_located((By.TAG_NAME, "table")),
                    EC.presence_of_element_located((By.CLASS_NAME, "tabela")),
                    EC.presence_of_element_located((By.XPATH, "//table"))
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
            try:
                df_lista = pd.read_html(io.StringIO(html_tabela))
            except ImportError as e:
                print(f"Erro de dependência: {e}")
                print("Execute: pip install lxml")
                return False
            except ValueError as e:
                print(f"Erro ao parsear HTML: {e}")
                return False
            
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
            # Verifica se foi cancelado antes de começar
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado pelo usuário"
                return resultado
            
            self._em_execucao = True
            print(f"\n=== Processando: {municipio} ({ano}) ===")
            
            # 1. Abre página FNDE
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
                return resultado
            if not self.abrir_pagina_fnde(ano, municipio):
                resultado['erro'] = "Falha ao abrir página FNDE"
                return resultado
            
            # 2. Preenche formulário
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
                return resultado
            if not self.preencher_formulario(ano, municipio):
                resultado['erro'] = "Falha ao preencher formulário"
                return resultado
            
            # 3. Executa busca
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
                return resultado
            if not self.executar_busca():
                resultado['erro'] = "Falha ao executar busca"
                return resultado
            
            # 4. Extrai tabela
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
                return resultado
            html_tabela = self.extrair_tabela_html()
            if not html_tabela:
                resultado['erro'] = "Falha ao extrair tabela"
                return resultado
            
            # 5. Salva Excel
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
                return resultado
            if not self.salvar_excel(html_tabela, municipio, ano):
                resultado['erro'] = "Falha ao salvar arquivo Excel"
                return resultado
            
            resultado['sucesso'] = True
            resultado['arquivo'] = f"{ano}_{municipio.replace(' ', '_')}.xlsx"
            print(f"✓ Processamento concluído para {municipio}")
            
        except Exception as e:
            resultado['erro'] = f"Erro inesperado: {str(e)}"
            print(f"✗ Erro ao processar {municipio}: {e}")
        finally:
            self._em_execucao = False
        
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
        
        try:
            for i, municipio in enumerate(self.municipios_mg, 1):
                # Verifica cancelamento antes de processar cada município
                if self._cancelado:
                    print(f"\nProcessamento cancelado no município {i}")
                    break
                
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
                
                # Pequena pausa entre municípios (otimizada)
                if not self._cancelado:
                    time.sleep(0.2)
        
        except Exception as e:
            print(f"Erro durante processamento em lote: {e}")
        finally:
            self.limpar_recursos()
        
        # Calcula taxa de sucesso
        estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100
        
        print(f"\n=== PROCESSAMENTO CONCLUÍDO ===")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
        
        return estatisticas
    
    def processar_lote_municipios(self, ano: str, municipios: List[str]) -> Dict[str, any]:
        """
        Processa um lote específico de municípios (para uso paralelo)
        
        Args:
            ano (str): Ano para consulta
            municipios (List[str]): Lista de municípios para processar
            
        Returns:
            Dict: Estatísticas do processamento do lote
        """
        print(f"\n=== PROCESSANDO LOTE DE {len(municipios)} MUNICÍPIOS - ANO {ano} ===")
        
        estatisticas = {
            'total': len(municipios),
            'sucessos': 0,
            'erros': 0,
            'municipios_processados': [],
            'municipios_erro': []
        }
        
        try:
            for i, municipio in enumerate(municipios, 1):
                # Verifica cancelamento antes de processar cada município
                if self._cancelado:
                    print(f"\nProcessamento cancelado no município {i}")
                    break
                
                print(f"\nProgresso do lote: {i}/{len(municipios)} - {municipio}")
                
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
                
                # Pequena pausa entre municípios (otimizada)
                if not self._cancelado:
                    time.sleep(0.2)
        
        except Exception as e:
            print(f"Erro durante processamento do lote: {e}")
            return {'sucesso': False, 'erro': str(e)}
        
        # Calcula taxa de sucesso
        estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100
        
        print(f"\n=== LOTE CONCLUÍDO ===")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
        
        return {'sucesso': True, 'estatisticas': estatisticas}
    
    def executar_paralelo(self, ano: str, num_instancias: int = 2) -> Dict[str, any]:
        """
        Executa processamento paralelo de municípios usando ProcessadorParalelo
        
        Args:
            ano (str): Ano para consulta
            num_instancias (int): Número de instâncias paralelas (máximo 5)
            
        Returns:
            Dict: Resultados consolidados do processamento paralelo com referência ao processador
        """
        try:
            from classes.parallel_processor import ProcessadorParalelo
            
            print(f"\n=== INICIANDO PROCESSAMENTO PARALELO FNDE ===")
            print(f"Ano: {ano}")
            print(f"Instâncias: {num_instancias}")
            
            # Armazena referência do processador para cancelamento
            self.processador_paralelo = ProcessadorParalelo()
            resultado = self.processador_paralelo.executar_paralelo_fnde(self, ano, num_instancias)
            
            # Adiciona referência do processador ao resultado
            resultado['processador'] = self.processador_paralelo
            
            if resultado['sucesso']:
                stats = resultado['estatisticas']
                print(f"\n=== PROCESSAMENTO PARALELO CONCLUÍDO ===")
                print(f"Total: {stats['total']} municípios")
                print(f"Sucessos: {stats['sucessos']}")
                print(f"Erros: {stats['erros']}")
                print(f"Taxa de sucesso: {stats['taxa_sucesso']:.1f}%")
            else:
                print(f"\n=== ERRO NO PROCESSAMENTO PARALELO ===")
                print(f"Erro: {resultado['erro']}")
            
            return resultado
            
        except Exception as e:
            return {'sucesso': False, 'erro': f'Erro ao iniciar processamento paralelo: {str(e)}'}
    
    def limpar_recursos(self):
        """Limpa todos os recursos e fecha navegador com segurança"""
        try:
            if hasattr(self, 'navegador') and self.navegador:
                # Fecha todas as abas abertas
                try:
                    for handle in self.navegador.window_handles:
                        self.navegador.switch_to.window(handle)
                        self.navegador.close()
                except:
                    pass  # Ignora erros ao fechar abas
                
                # Encerra o processo do navegador
                self.navegador.quit()
                self.navegador = None
                self.wait = None
        except Exception:
            pass  # Silencia todos os erros durante limpeza
    
    def fechar_navegador(self):
        """Fecha o navegador com limpeza completa"""
        self.limpar_recursos()
        print("Navegador fechado e recursos liberados")
    
    def __del__(self):
        """Garante fechamento do navegador ao destruir objeto"""
        self.limpar_recursos()
    
    def cancelar(self):
        """Cancela execução e limpa recursos"""
        print("Cancelando processamento...")
        self._cancelado = True
        self._em_execucao = False
        self.limpar_recursos()
        print("Processamento cancelado e recursos liberados")
    
    def cancelar_forcado(self):
        """Cancela e força fechamento de TODAS as abas do Chrome"""
        print("Cancelamento forçado FNDE: fechando todas as abas do Chrome...")
        self._cancelado = True
        self._em_execucao = False
        
        # Se tiver processador paralelo ativo, cancela ele também
        if hasattr(self, 'processador_paralelo') and self.processador_paralelo:
            print("Cancelando processador paralelo FNDE...")
            self.processador_paralelo.cancelar()
            self.processador_paralelo = None
        
        if hasattr(self, 'navegador') and self.navegador:
            try:
                # Fecha TODAS as janelas e abas abertas
                handles = self.navegador.window_handles.copy()  # Copia a lista
                for handle in handles:
                    try:
                        self.navegador.switch_to.window(handle)
                        self.navegador.close()
                    except:
                        pass  # Ignora erros ao fechar abas individuais
                
                # Força encerramento do processo
                self.navegador.quit()
                self.navegador = None
                self.wait = None
                
            except Exception as e:
                print(f"Erro durante cancelamento forçado: {e}")
                # Tenta encerramento direto como último recurso
                try:
                    self.navegador.quit()
                    self.navegador = None
                    self.wait = None
                except:
                    pass
        
        print("Cancelamento forçado concluído - todas as abas fechadas")
    
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