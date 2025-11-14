#!/usr/bin/env python3
"""
Bot de scraping para o sistema Consulta FNS (Fundo Nacional de Saúde) extraindo dados de contas bancárias para municípios de Minas Gerais
"""

from selenium import webdriver
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.classes.chrome_driver import ChromeDriverSimples
from src.classes.methods.cancel_method import BotBase
from src.classes.config import CONSFNS_CONFIG, SELETORES_CONSFNS, MENSAGENS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import glob
from datetime import datetime
from typing import List, Dict, Optional
from src.classes.file.path_manager import obter_caminho_dados


class BotConsFNS(BotBase):
    """
    Bot de scraping para o site Consulta FNS

    Funcionalidades:
    - Navega ao site Consulta FNS
    - Preenche formulário (estado e município)
    - Executa consulta e aguarda carregamento
    - Gera e baixa planilha Excel
    - Renomeia arquivo com nome da cidade
    - Processa múltiplas cidades automaticamente
    """

    def __init__(self, timeout=10):
        """Inicializa o bot ConsFNS"""
        super().__init__()
        self.base_url = CONSFNS_CONFIG['url_base']
        self.timeout = timeout
        self.timeout_carregamento_max = CONSFNS_CONFIG['timeout_carregamento_maximo']
        self.municipios_mg = self._carregar_municipios_mg()
        self._cancelado = False
        self._em_execucao = False
        self._campo_esfera_presente = False
        self.processador_paralelo = None
        self.diretorio_consfns = obter_caminho_dados(CONSFNS_CONFIG['diretorio_saida'])
        self.data_hoje = datetime.now().strftime("%Y-%m-%d")
        self.diretorio_saida = os.path.join(self.diretorio_consfns, self.data_hoje)
        self.diretorio_download = os.path.join(self.diretorio_consfns, "temp_downloads")
        self._criar_diretorios()

    def _criar_diretorios(self):
        """Cria estrutura de diretórios necessária"""
        try:
            for diretorio in [self.diretorio_consfns, self.diretorio_saida, self.diretorio_download]:
                if not os.path.exists(diretorio):
                    os.makedirs(diretorio)
                    print(f"Diretório criado: {diretorio}")
        except Exception as e:
            print(f"Aviso: Erro ao criar diretórios - {e}")

    def _carregar_municipios_mg(self) -> List[str]:
        """Carrega lista de municípios de MG do arquivo cidades.txt"""
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

    def _verificar_cancelamento(self, resultado: Dict) -> bool:
        """Verifica se execução foi cancelada e atualiza resultado"""
        if self._cancelado:
            resultado['erro'] = "Processamento cancelado"
            return True
        return False

    def _criar_estatisticas(self, total: int) -> Dict:
        """Cria estrutura de estatísticas para processamento"""
        return {
            'total': total,
            'sucessos': 0,
            'erros': 0,
            'municipios_processados': [],
            'municipios_erro': []
        }

    def _atualizar_estatisticas(self, estatisticas: Dict, resultado: Dict):
        """Atualiza estatísticas com resultado do processamento de um município"""
        if resultado['sucesso']:
            estatisticas['sucessos'] += 1
            estatisticas['municipios_processados'].append(resultado['municipio'])
        else:
            estatisticas['erros'] += 1
            estatisticas['municipios_erro'].append({
                'municipio': resultado['municipio'],
                'erro': resultado['erro']
            })

    def _calcular_taxa_sucesso(self, estatisticas: Dict):
        """Calcula e adiciona taxa de sucesso às estatísticas"""
        if estatisticas['total'] > 0:
            estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100
        else:
            estatisticas['taxa_sucesso'] = 0

    def _imprimir_estatisticas(self, estatisticas: Dict, titulo: str = "PROCESSAMENTO CONCLUÍDO"):
        """Imprime resumo das estatísticas de processamento"""
        print(f"\n=== {titulo} ===")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")

    def configurar_navegador(self) -> bool:
        """Configura o navegador Chrome com diretório de download personalizado"""
        try:
            driver_simples = ChromeDriverSimples(download_dir=self.diretorio_download)
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

    def abrir_pagina_consfns(self) -> bool:
        """Abre a página Consulta FNS"""
        try:
            print(f"Abrindo página Consulta FNS...")
            self.navegador.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELETORES_CONSFNS['select_estado'])))
            time.sleep(1.5)
            print("✓ Página Consulta FNS carregada com sucesso")
            return True
        except TimeoutException:
            print("✗ Timeout: Página demorou para carregar")
            return False
        except Exception as e:
            print(f"✗ Erro ao abrir página Consulta FNS: {e}")
            return False

    def preencher_formulario(self, municipio: str) -> bool:
        """Preenche o formulário Consulta FNS com os dados fornecidos"""
        try:
            print(f"Preenchendo formulário para {municipio}")
            print("Selecionando estado MINAS GERAIS...")
            time.sleep(1)
            select_estado = Select(self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['select_estado']))
            select_estado.select_by_visible_text(CONSFNS_CONFIG['uf_padrao'])
            WebDriverWait(self.navegador, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_CONSFNS['select_municipio']))
            )
            time.sleep(1)
            if not self._selecionar_municipio(municipio):
                print(f"✗ Município '{municipio}' não encontrado na lista")
                return False
            self._verificar_e_selecionar_esfera()
            print("✓ Formulário preenchido com sucesso")
            return True
        except NoSuchElementException as e:
            print(f"✗ Elemento não encontrado no formulário: {e}")
            return False
        except Exception as e:
            print(f"✗ Erro ao preencher formulário: {e}")
            return False

    def _selecionar_municipio(self, nome_municipio: str) -> bool:
        """Seleciona município no dropdown (busca exata ou parcial)"""
        try:
            select_municipio = Select(self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['select_municipio']))
            nome_procurado = nome_municipio.upper().strip()
            for opcao in select_municipio.options:
                texto_opcao = opcao.text.upper().strip()
                if nome_procurado == texto_opcao or nome_procurado in texto_opcao:
                    select_municipio.select_by_visible_text(opcao.text)
                    print(f"✓ Município selecionado: {opcao.text}")
                    return True
            return False
        except Exception as e:
            print(f"✗ Erro ao selecionar município: {e}")
            return False

    def _verificar_e_selecionar_esfera(self) -> bool:
        """Verifica se o campo 'esfera' aparece e seleciona 'MUNICIPAL' (campo condicional)"""
        try:
            WebDriverWait(self.navegador, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELETORES_CONSFNS['select_esfera']))
            )
            print("Campo 'esfera' detectado - selecionando MUNICIPAL...")
            select_esfera = Select(self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['select_esfera']))
            select_esfera.select_by_value("MUNICIPAL")
            if CONSFNS_CONFIG['pausa_apos_selecao_esfera'] > 0:
                time.sleep(CONSFNS_CONFIG['pausa_apos_selecao_esfera'])
            self._campo_esfera_presente = True
            print("✓ Esfera selecionada: MUNICIPAL")
            return True
        except TimeoutException:
            return False
        except Exception as e:
            print(f"Aviso: Erro ao verificar campo esfera: {e}")
            return False

    def executar_consulta(self) -> bool:
        """Clica no botão Consultar e aguarda resultado"""
        try:
            print("Executando consulta...")
            botao_consultar = self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['botao_consultar'])
            botao_consultar.click()
            print(MENSAGENS['consfns_aguardando'])
            WebDriverWait(self.navegador, self.timeout_carregamento_max).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_CONSFNS['botao_gerar_planilha']))
            )
            if self._campo_esfera_presente:
                print("⏳ Campo 'esfera' detectado - aguardando 30s para garantir carregamento completo...")
                time.sleep(30)
                print("✓ Aguardo concluído")
            print("✓ Consulta executada e resultados carregados")
            return True
        except TimeoutException:
            print("✗ Timeout: Resultados demoraram para carregar")
            return False
        except Exception as e:
            print(f"✗ Erro ao executar consulta: {e}")
            return False

    def gerar_planilha(self, municipio: str) -> Optional[str]:
        """Clica no botão Gerar Planilha e aguarda download com retry automático"""
        max_tentativas = 3
        for tentativa in range(1, max_tentativas + 1):
            try:
                if tentativa == 1:
                    print(MENSAGENS['consfns_download'])
                else:
                    print(f"⚠️ Tentativa {tentativa}/{max_tentativas} - Tentando baixar novamente...")
                arquivos_antes = set(os.listdir(self.diretorio_download))
                botao_gerar = self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['botao_gerar_planilha'])
                botao_gerar.click()
                if CONSFNS_CONFIG['pausa_antes_download'] > 0:
                    time.sleep(CONSFNS_CONFIG['pausa_antes_download'])
                arquivo_baixado = self._aguardar_download(arquivos_antes, timeout=30)
                if arquivo_baixado:
                    arquivo_final = self._renomear_arquivo(arquivo_baixado, municipio)
                    print(f"✓ Planilha gerada: {arquivo_final}")
                    return arquivo_final
                else:
                    if tentativa < max_tentativas:
                        print(f"⚠️ Arquivo .xlsx não foi baixado - aguardando antes de tentar novamente...")
                        time.sleep(2)
                    else:
                        print(f"✗ Falha após {max_tentativas} tentativas - arquivo .xlsx não foi baixado")
                        return None
            except Exception as e:
                if tentativa < max_tentativas:
                    print(f"⚠️ Erro na tentativa {tentativa}: {e} - tentando novamente...")
                    time.sleep(2)
                else:
                    print(f"✗ Erro ao gerar planilha após {max_tentativas} tentativas: {e}")
                    return None
        return None

    def _aguardar_download(self, arquivos_antes: set, timeout: int = 30) -> Optional[str]:
        """Aguarda um arquivo .xlsx ser baixado no diretório"""
        tempo_inicio = time.time()
        while time.time() - tempo_inicio < timeout:
            if self._cancelado:
                return None
            arquivos_agora = set(os.listdir(self.diretorio_download))
            novos_arquivos = arquivos_agora - arquivos_antes
            arquivos_xlsx = [f for f in novos_arquivos
                           if f.endswith('.xlsx') and not f.endswith(('.crdownload', '.tmp', '.html'))]
            if arquivos_xlsx:
                arquivo_path = os.path.join(self.diretorio_download, arquivos_xlsx[0])
                if os.path.exists(arquivo_path) and os.path.getsize(arquivo_path) > 0:
                    time.sleep(1)
                    print(f"✓ Arquivo .xlsx detectado: {arquivos_xlsx[0]} ({os.path.getsize(arquivo_path)} bytes)")
                    return arquivo_path
            time.sleep(0.5)
        return None

    def _renomear_arquivo(self, arquivo_original: str, municipio: str) -> str:
        """Renomeia arquivo baixado com nome do município"""
        try:
            nome_municipio_limpo = municipio.replace(" ", "_").replace("/", "_").upper()
            _, extensao = os.path.splitext(arquivo_original)
            if not extensao:
                extensao = '.xlsx'
            novo_nome = f"{nome_municipio_limpo}{extensao}"
            caminho_final = os.path.join(self.diretorio_saida, novo_nome)
            import shutil
            shutil.move(arquivo_original, caminho_final)
            return caminho_final
        except Exception as e:
            print(f"Aviso: Erro ao renomear arquivo - {e}")
            return arquivo_original

    def processar_municipio(self, municipio: str) -> Dict[str, any]:
        """Processa um município específico com sessão Chrome dedicada"""
        resultado = {'municipio': municipio, 'sucesso': False, 'erro': None, 'arquivo': None}
        try:
            if self._verificar_cancelamento(resultado):
                return resultado
            self._campo_esfera_presente = False
            self._em_execucao = True
            print(f"\n=== Processando: {municipio} ===")

            print("Abrindo Chrome para este município...")
            if self._verificar_cancelamento(resultado) or not self.configurar_navegador():
                resultado['erro'] = resultado.get('erro') or "Falha ao configurar navegador Chrome"
                return resultado

            if self._verificar_cancelamento(resultado) or not self.abrir_pagina_consfns():
                resultado['erro'] = resultado.get('erro') or "Falha ao abrir página ConsFNS"
                return resultado

            if self._verificar_cancelamento(resultado) or not self.preencher_formulario(municipio):
                resultado['erro'] = resultado.get('erro') or "Falha ao preencher formulário"
                return resultado

            if self._verificar_cancelamento(resultado) or not self.executar_consulta():
                resultado['erro'] = resultado.get('erro') or "Falha ao executar consulta"
                return resultado

            if self._verificar_cancelamento(resultado):
                return resultado
            arquivo_salvo = self.gerar_planilha(municipio)
            if not arquivo_salvo:
                resultado['erro'] = "Falha ao gerar planilha"
                return resultado

            resultado['sucesso'] = True
            resultado['arquivo'] = arquivo_salvo
            print(f"✓ Processamento concluído para {municipio}")
        except Exception as e:
            resultado['erro'] = f"Erro inesperado: {str(e)}"
            print(f"✗ Erro ao processar {municipio}: {e}")
        finally:
            self._em_execucao = False
            print("Fechando Chrome...")
            self.limpar_recursos()
        return resultado

    def processar_todos_municipios(self) -> Dict[str, any]:
        """Processa todos os municípios de MG"""
        print(f"\n{MENSAGENS['inicio_consfns']}")
        print(f"{MENSAGENS['consfns_todos_municipios']}")
        print(f"Total de municípios: {len(self.municipios_mg)}")
        estatisticas = self._criar_estatisticas(len(self.municipios_mg))
        try:
            for i, municipio in enumerate(self.municipios_mg, 1):
                if self._cancelado:
                    print(f"\nProcessamento cancelado no município {i}")
                    break
                print(f"\nProgresso: {i}/{len(self.municipios_mg)} municípios")
                resultado = self.processar_municipio(municipio)
                self._atualizar_estatisticas(estatisticas, resultado)
        except Exception as e:
            print(f"Erro durante processamento em lote: {e}")
        self._calcular_taxa_sucesso(estatisticas)
        try:
            arquivo_relatorio = self._gerar_relatorio(estatisticas)
            if arquivo_relatorio:
                print(f"📄 Relatório gerado: {arquivo_relatorio}")
        except Exception as e:
            print(f"Aviso: Erro ao gerar relatório - {e}")
        self._imprimir_estatisticas(estatisticas)
        return estatisticas

    def _gerar_relatorio(self, estatisticas: Dict) -> str:
        """Gera relatório TXT com estatísticas do processamento"""
        try:
            from datetime import datetime
            nome_arquivo = f"RELATORIO_CONSFNS_{self.data_hoje}.txt"
            caminho_relatorio = os.path.join(self.diretorio_consfns, nome_arquivo)
            data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            linhas = []
            linhas.append("=" * 60)
            linhas.append("RELATÓRIO DE PROCESSAMENTO - CONSULTA FNS")
            linhas.append("=" * 60)
            linhas.append("")
            linhas.append(f"Data: {data_hora_atual}")
            linhas.append("")
            linhas.append("ESTATÍSTICAS GERAIS:")
            linhas.append(f"- Total de municípios: {estatisticas['total']}")
            linhas.append(f"- Sucessos: {estatisticas['sucessos']}")
            linhas.append(f"- Erros: {estatisticas['erros']}")
            linhas.append(f"- Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
            linhas.append("")
            if estatisticas['erros'] > 0 and estatisticas.get('municipios_erro'):
                linhas.append("=" * 60)
                linhas.append(f"MUNICÍPIOS COM ERRO ({len(estatisticas['municipios_erro'])}):")
                linhas.append("=" * 60)
                linhas.append("")
                for i, erro_info in enumerate(estatisticas['municipios_erro'], 1):
                    municipio = erro_info.get('municipio', 'Desconhecido')
                    erro = erro_info.get('erro', 'Erro não especificado')
                    linhas.append(f"{i}. {municipio}")
                    linhas.append(f"   Erro: {erro}")
                    linhas.append("")
            else:
                linhas.append("=" * 60)
                linhas.append("NENHUM ERRO REGISTRADO - EXECUÇÃO 100% SUCESSO!")
                linhas.append("=" * 60)
                linhas.append("")
            linhas.append("=" * 60)
            linhas.append("FIM DO RELATÓRIO")
            linhas.append("=" * 60)
            with open(caminho_relatorio, 'w', encoding='utf-8') as arquivo:
                arquivo.write('\n'.join(linhas))
            print(f"📄 Relatório gerado: {caminho_relatorio}")
            return caminho_relatorio
        except Exception as e:
            print(f"Aviso: Erro ao gerar relatório - {e}")
            return None

    def processar_lote_municipios(self, municipios: List[str]) -> Dict[str, any]:
        """Processa um lote específico de municípios (para uso paralelo)"""
        print(f"\n=== PROCESSANDO LOTE DE {len(municipios)} MUNICÍPIOS - CONSFNS ===")
        estatisticas = self._criar_estatisticas(len(municipios))
        try:
            for i, municipio in enumerate(municipios, 1):
                if self._cancelado:
                    print(f"\nProcessamento cancelado no município {i}")
                    break
                print(f"\nProgresso do lote: {i}/{len(municipios)} - {municipio}")
                resultado = self.processar_municipio(municipio)
                self._atualizar_estatisticas(estatisticas, resultado)
                if not self._cancelado:
                    time.sleep(CONSFNS_CONFIG['pausa_entre_municipios'])
        except Exception as e:
            print(f"Erro durante processamento do lote: {e}")
            return {'sucesso': False, 'erro': str(e)}
        self._calcular_taxa_sucesso(estatisticas)
        self._imprimir_estatisticas(estatisticas, "LOTE CONCLUÍDO")
        return {'sucesso': True, 'estatisticas': estatisticas}

    def executar_paralelo(self, num_instancias: int = 2) -> Dict[str, any]:
        """Executa processamento paralelo de municípios usando ProcessadorParalelo"""
        try:
            from src.classes.methods.parallel_processor import ProcessadorParalelo
            print(f"\n=== INICIANDO PROCESSAMENTO PARALELO CONSFNS ===")
            print(f"Instâncias: {num_instancias}")
            self.processador_paralelo = ProcessadorParalelo()
            resultado = self.processador_paralelo.executar_paralelo_consfns(self, num_instancias)
            resultado['processador'] = self.processador_paralelo
            if resultado['sucesso']:
                stats = resultado['estatisticas']
                stats['titulo_customizado'] = "PROCESSAMENTO PARALELO CONCLUÍDO"
                self._imprimir_estatisticas(stats, "PROCESSAMENTO PARALELO CONCLUÍDO")
                try:
                    arquivo_relatorio = self._gerar_relatorio(stats)
                    if arquivo_relatorio:
                        print(f"📄 Relatório gerado: {arquivo_relatorio}")
                except Exception as e:
                    print(f"Aviso: Erro ao gerar relatório - {e}")
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
                try:
                    for handle in self.navegador.window_handles:
                        self.navegador.switch_to.window(handle)
                        self.navegador.close()
                except:
                    pass
                self.navegador.quit()
                self.navegador = None
                self.wait = None
        except Exception:
            pass

    def fechar_navegador(self):
        """Fecha o navegador com limpeza completa"""
        self.limpar_recursos()
        print("Navegador fechado e recursos liberados")

    def __del__(self):
        """Garante fechamento do navegador ao destruir objeto"""
        self.limpar_recursos()

    def cancelar(self, forcado=False):
        """Cancela execução e limpa recursos"""
        self._em_execucao = False
        if forcado and hasattr(self, 'processador_paralelo') and self.processador_paralelo:
            print("Cancelando processador paralelo ConsFNS...")
            self.processador_paralelo.cancelar()
            self.processador_paralelo = None
        super().cancelar(forcado=forcado)

    def cancelar_forcado(self):
        """Mantido para compatibilidade - usar cancelar(forcado=True)"""
        self.cancelar(forcado=True)

    def obter_lista_municipios(self) -> List[str]:
        """Retorna lista de municípios carregados"""
        return self.municipios_mg.copy()
