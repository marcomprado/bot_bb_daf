#!/usr/bin/env python3
"""
Bot de scraping para o sistema Pagamentos de Resoluções
URLs:
    Pagamentos Orçamentários: http://pagamentoderesolucoes.saude.mg.gov.br/pagamentos-orcamentarios
    Restos a Pagar: http://pagamentoderesolucoes.saude.mg.gov.br/restos-a-pagar
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
import sys
import os
import time
import threading
from datetime import datetime
from typing import List, Dict, Optional

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.classes.chrome_driver import ChromeDriverSimples
from src.classes.methods.cancel_method import BotBase
from src.classes.report_generator import ReportGenerator
from src.classes.file.path_manager import obter_caminho_dados
from src.classes.city_manager import CityManager
from src.classes.central import (
    PAGAMENTOS_RES_CONFIG,
    SELETORES_PAGAMENTOS_RES_ORCAMENTARIOS,
    SELETORES_PAGAMENTOS_RES_RESTOS,
    MENSAGENS
)


class BotPagamentosRes(BotBase):
    """Bot de scraping Pagamentos de Resoluções com sincronização de duas URLs simultâneas"""

    def __init__(self, timeout=None):
        """Inicializa o bot Pagamentos de Resoluções usando configurações centralizadas de central.py"""
        super().__init__()

        # URLs do sistema (central.py)
        self.url_orcamentarios = PAGAMENTOS_RES_CONFIG['url_orcamentarios']
        self.url_restos_a_pagar = PAGAMENTOS_RES_CONFIG['url_restos_a_pagar']

        # Duas instâncias de navegador
        self.navegador_orcamentarios = None
        self.navegador_restos = None
        self.wait_orcamentarios = None
        self.wait_restos = None

        # Configurações (central.py)
        self.timeout = timeout or PAGAMENTOS_RES_CONFIG['timeout_selenium']
        self.max_tentativas = PAGAMENTOS_RES_CONFIG['max_tentativas_espera']
        self.max_retries = PAGAMENTOS_RES_CONFIG['max_retries']
        self.city_manager = CityManager()
        self.municipios_mg = self.city_manager.obter_municipios_mg()

        # Flags de controle
        self._cancelado = False
        self._em_execucao = False

        # Configuração de diretórios (central.py)
        self.diretorio_pagamentos_res = obter_caminho_dados(PAGAMENTOS_RES_CONFIG['diretorio_saida'])
        self.diretorio_base = os.path.dirname(self.diretorio_pagamentos_res)

        self._criar_diretorios()
        self.report_gen = ReportGenerator(self.diretorio_pagamentos_res, PAGAMENTOS_RES_CONFIG['prefixo_relatorio'])

    def _criar_diretorios(self):
        """Cria estrutura de diretórios necessária"""
        try:
            for diretorio in [self.diretorio_base, self.diretorio_pagamentos_res]:
                if not os.path.exists(diretorio):
                    os.makedirs(diretorio)
        except Exception as e:
            print(f"Aviso: Erro ao criar diretórios - {e}")

    def configurar_navegador(self) -> bool:
        """Método compatível com GUI6 - configura AMBOS os navegadores"""
        return self.configurar_navegadores()

    def configurar_navegadores(self) -> bool:
        """Configura DUAS instâncias Chrome com diretórios de download separados (central.py)"""
        try:
            print("Configurando navegadores Pagamentos de Resoluções...")

            # Criar diretórios finais
            self.dir_orcamentarios = os.path.join(self.diretorio_pagamentos_res, PAGAMENTOS_RES_CONFIG['subdiretorios_finais'][0])
            self.dir_restos_a_pagar = os.path.join(self.diretorio_pagamentos_res, PAGAMENTOS_RES_CONFIG['subdiretorios_finais'][1])
            os.makedirs(self.dir_orcamentarios, exist_ok=True)
            os.makedirs(self.dir_restos_a_pagar, exist_ok=True)

            # Navegador 1: Pagamentos Orçamentários
            opcoes_orcamentarios = webdriver.ChromeOptions()
            #opcoes_orcamentarios.add_argument("--headless=new")
            opcoes_orcamentarios.add_argument("--disable-gpu")
            opcoes_orcamentarios.add_argument("--window-size=1920,1080")

            # Opções para forçar HTTP e evitar redirecionamento HTTPS/403
            opcoes_orcamentarios.add_argument("--ignore-certificate-errors")
            opcoes_orcamentarios.add_argument("--allow-insecure-localhost")
            opcoes_orcamentarios.add_argument("--allow-running-insecure-content")
            opcoes_orcamentarios.add_argument("--disable-web-security")
            opcoes_orcamentarios.add_argument("--no-proxy-server")
            opcoes_orcamentarios.add_argument("--disable-features=InsecureDownloadWarnings")
            opcoes_orcamentarios.add_argument("--unsafely-treat-insecure-origin-as-secure=http://pagamentoderesolucoes.saude.mg.gov.br")

            # User-Agent customizado para evitar bloqueio
            opcoes_orcamentarios.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            # Preferências para desabilitar upgrade automático HTTPS
            prefs_orcamentarios = {
                "profile.default_content_setting_values.mixed_content": 1,
                "profile.block_third_party_cookies": False,
                "profile.cookie_controls_mode": 0,
            }
            opcoes_orcamentarios.add_experimental_option("prefs", prefs_orcamentarios)

            driver_orcamentarios = ChromeDriverSimples(download_dir=self.dir_orcamentarios)
            self.navegador_orcamentarios = driver_orcamentarios.conectar(chrome_options=opcoes_orcamentarios)
            self.wait_orcamentarios = WebDriverWait(self.navegador_orcamentarios, self.timeout)

            # Navegador 2: Restos a Pagar
            opcoes_restos = webdriver.ChromeOptions()
            #opcoes_restos.add_argument("--headless=new")
            opcoes_restos.add_argument("--disable-gpu")
            opcoes_restos.add_argument("--window-size=1920,1080")

            # Opções para forçar HTTP e evitar redirecionamento HTTPS/403
            opcoes_restos.add_argument("--ignore-certificate-errors")
            opcoes_restos.add_argument("--allow-insecure-localhost")
            opcoes_restos.add_argument("--allow-running-insecure-content")
            opcoes_restos.add_argument("--disable-web-security")
            opcoes_restos.add_argument("--no-proxy-server")
            opcoes_restos.add_argument("--disable-features=InsecureDownloadWarnings")
            opcoes_restos.add_argument("--unsafely-treat-insecure-origin-as-secure=http://pagamentoderesolucoes.saude.mg.gov.br")

            # User-Agent customizado para evitar bloqueio
            opcoes_restos.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            # Preferências para desabilitar upgrade automático HTTPS
            prefs_restos = {
                "profile.default_content_setting_values.mixed_content": 1,
                "profile.block_third_party_cookies": False,
                "profile.cookie_controls_mode": 0,
            }
            opcoes_restos.add_experimental_option("prefs", prefs_restos)

            driver_restos = ChromeDriverSimples(download_dir=self.dir_restos_a_pagar)
            self.navegador_restos = driver_restos.conectar(chrome_options=opcoes_restos)
            self.wait_restos = WebDriverWait(self.navegador_restos, self.timeout)

            # Abre as URLs
            print("Abrindo URLs do sistema Pagamentos de Resoluções...")
            self.navegador_orcamentarios.get(self.url_orcamentarios)
            self.navegador_restos.get(self.url_restos_a_pagar)

            print("✓ Navegadores configurados com sucesso")
            return True

        except Exception as e:
            print(f"✗ Erro ao configurar navegadores: {e}")
            return False

    def _sleep_cancelavel(self, segundos: float):
        """Sleep que pode ser interrompido por cancelamento"""
        inicio = time.time()
        while time.time() - inicio < segundos:
            if self._cancelado:
                return
            time.sleep(0.1)  # Verifica a cada 100ms

    def esperar_elemento_disponivel(self, navegador, wait, by, seletor, acao_callback, max_tentativas=None):
        """Tenta realizar ação até N vezes devido ao loading do site (central.py)"""
        max_tentativas = max_tentativas or self.max_tentativas
        for tentativa in range(1, max_tentativas + 1):
            if self._cancelado:
                return False

            try:
                elemento = wait.until(
                    EC.element_to_be_clickable((by, seletor))
                )
                acao_callback(elemento)
                if tentativa > 1:
                    print(f"  ✓ Ação executada (tentativa {tentativa})")
                return True

            except (TimeoutException, NoSuchElementException, ElementNotInteractableException,
                    ElementClickInterceptedException, StaleElementReferenceException):
                if self._cancelado:
                    return False
                if tentativa == max_tentativas:
                    print(f"  ✗ Timeout após {max_tentativas} tentativas")
                    return False
                time.sleep(PAGAMENTOS_RES_CONFIG['pausa_tentativa_espera'])  # Aguarda antes de tentar novamente (central.py)

        return False

    def verificar_resultado_vazio(self, navegador, wait) -> bool:
        """Verifica se a pesquisa retornou 'Nenhum registro encontrado'"""
        try:
            # Tenta encontrar a mensagem de "sem registros" com timeout curto (2 segundos)
            mensagem = WebDriverWait(navegador, 2).until(
                EC.presence_of_element_located((By.XPATH, "//td[@class='dataTables_empty']"))
            )
            texto = mensagem.text.strip().lower()

            # Verifica se contém "nenhum registro" ou similar
            if "nenhum registro" in texto or "sem registros" in texto or "no data" in texto or "no matching" in texto:
                print(f"  ⓘ Nenhum registro encontrado para este município")
                return True

        except:
            # Se não encontrou a mensagem em 2 segundos, assume que há resultados
            pass

        return False

    def processar_orcamentarios(self, municipio: str, ano: str) -> Dict:
        """Processa URL de Pagamentos Orçamentários: seleciona ano, município, consultar, gerar CSV, renomear (central.py)"""
        if self._cancelado:
            return {'sucesso': False, 'municipio': municipio, 'tipo': 'orcamentarios', 'erro': 'Cancelado'}

        municipio_upper = municipio.upper()
        municipio_arquivo = municipio.replace(" ", "_").upper()

        try:
            print(f"  [ORÇAMENTÁRIOS] Processando {municipio}")

            # Passo 1: Selecionar ano
            if not self.esperar_elemento_disponivel(
                self.navegador_orcamentarios,
                self.wait_orcamentarios,
                By.ID,
                SELETORES_PAGAMENTOS_RES_ORCAMENTARIOS['select_ano'],
                lambda el: Select(el).select_by_visible_text(ano)
            ):
                raise Exception("Timeout ao selecionar ano")

            # Aguarda dropdown de município carregar
            try:
                self.wait_orcamentarios.until(
                    EC.presence_of_element_located((By.ID, SELETORES_PAGAMENTOS_RES_ORCAMENTARIOS['select_municipio']))
                )
            except:
                pass

            # Passo 2: Selecionar município
            if not self.esperar_elemento_disponivel(
                self.navegador_orcamentarios,
                self.wait_orcamentarios,
                By.ID,
                SELETORES_PAGAMENTOS_RES_ORCAMENTARIOS['select_municipio'],
                lambda el: Select(el).select_by_visible_text(municipio_upper)
            ):
                raise Exception("Timeout ao selecionar município")

            # Aguarda botão Consultar estar disponível
            try:
                self.wait_orcamentarios.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_PAGAMENTOS_RES_ORCAMENTARIOS['botao_consultar']))
                )
            except:
                pass

            # Passo 3: Clicar consultar
            if not self.esperar_elemento_disponivel(
                self.navegador_orcamentarios,
                self.wait_orcamentarios,
                By.CSS_SELECTOR,
                SELETORES_PAGAMENTOS_RES_ORCAMENTARIOS['botao_consultar'],
                lambda el: el.click()
            ):
                raise Exception("Timeout ao clicar consultar")

            # Aguarda após consulta
            self._sleep_cancelavel(PAGAMENTOS_RES_CONFIG['pausa_apos_consulta'])

            # Verificar se retornou registros
            if self.verificar_resultado_vazio(self.navegador_orcamentarios, self.wait_orcamentarios):
                print(f"  ⓘ [ORÇAMENTÁRIOS] Sem dados para {municipio} - continuando")

                # Recarrega página para voltar ao estado inicial (próximo município)
                self.navegador_orcamentarios.get(self.url_orcamentarios)

                return {
                    'sucesso': True,
                    'municipio': municipio,
                    'tipo': 'orcamentarios',
                    'arquivo': None,
                    'sem_dados': True
                }

            # Passo 4: Clicar gerar CSV e aguardar download
            if not self.esperar_elemento_disponivel(
                self.navegador_orcamentarios,
                self.wait_orcamentarios,
                By.CSS_SELECTOR,
                SELETORES_PAGAMENTOS_RES_ORCAMENTARIOS['botao_gerar_csv'],
                lambda el: el.click()
            ):
                raise Exception("Timeout ao gerar CSV")

            # Passo 5: Aguardar arquivo CSV ser baixado (30s timeout)
            arquivo_baixado = self._aguardar_download_csv(self.dir_orcamentarios, timeout=30)

            if arquivo_baixado is None:
                if self._cancelado:
                    raise Exception("Download cancelado pelo usuário")
                else:
                    raise Exception("Arquivo CSV não foi baixado (timeout 30s)")

            # Passo 6: Renomear com retry (Windows file locking)
            arquivo_renomeado = self._renomear_arquivo_com_retry(
                arquivo_baixado,
                PAGAMENTOS_RES_CONFIG['formato_arquivo_orcamentarios'].format(municipio=municipio_arquivo)
            )

            print(f"  ✓ [ORÇAMENTÁRIOS] {municipio} processado com sucesso")

            # Recarrega página para voltar ao estado inicial (próximo município)
            self.navegador_orcamentarios.get(self.url_orcamentarios)

            return {
                'sucesso': True,
                'municipio': municipio,
                'tipo': 'orcamentarios',
                'arquivo': arquivo_renomeado
            }

        except Exception as e:
            print(f"  ✗ [ORÇAMENTÁRIOS] Erro em {municipio}: {e}")

            # Recarrega página mesmo em caso de erro (próximo município)
            try:
                self.navegador_orcamentarios.get(self.url_orcamentarios)
            except:
                pass

            return {
                'sucesso': False,
                'municipio': municipio,
                'tipo': 'orcamentarios',
                'erro': str(e)
            }

    def processar_restos_a_pagar(self, municipio: str, ano: str) -> Dict:
        """Processa URL de Restos a Pagar: seleciona ano, município, consultar, gerar CSV, renomear (central.py)"""
        if self._cancelado:
            return {'sucesso': False, 'municipio': municipio, 'tipo': 'restos_a_pagar', 'erro': 'Cancelado'}

        municipio_upper = municipio.upper()
        municipio_arquivo = municipio.replace(" ", "_").upper()

        try:
            print(f"  [RESTOS A PAGAR] Processando {municipio}")

            # Passo 1: Selecionar ano
            if not self.esperar_elemento_disponivel(
                self.navegador_restos,
                self.wait_restos,
                By.ID,
                SELETORES_PAGAMENTOS_RES_RESTOS['select_ano'],
                lambda el: Select(el).select_by_visible_text(ano)
            ):
                raise Exception("Timeout ao selecionar ano")

            # Aguarda dropdown de município carregar
            try:
                self.wait_restos.until(
                    EC.presence_of_element_located((By.ID, SELETORES_PAGAMENTOS_RES_RESTOS['select_municipio']))
                )
            except:
                pass

            # Passo 2: Selecionar município
            if not self.esperar_elemento_disponivel(
                self.navegador_restos,
                self.wait_restos,
                By.ID,
                SELETORES_PAGAMENTOS_RES_RESTOS['select_municipio'],
                lambda el: Select(el).select_by_visible_text(municipio_upper)
            ):
                raise Exception("Timeout ao selecionar município")

            # Aguarda botão Consultar estar disponível
            try:
                self.wait_restos.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_PAGAMENTOS_RES_RESTOS['botao_consultar']))
                )
            except:
                pass

            # Passo 3: Clicar consultar
            if not self.esperar_elemento_disponivel(
                self.navegador_restos,
                self.wait_restos,
                By.CSS_SELECTOR,
                SELETORES_PAGAMENTOS_RES_RESTOS['botao_consultar'],
                lambda el: el.click()
            ):
                raise Exception("Timeout ao clicar consultar")

            # Aguarda após consulta
            self._sleep_cancelavel(PAGAMENTOS_RES_CONFIG['pausa_apos_consulta'])

            # Verificar se retornou registros
            if self.verificar_resultado_vazio(self.navegador_restos, self.wait_restos):
                print(f"  ⓘ [RESTOS A PAGAR] Sem dados para {municipio} - continuando")

                # Recarrega página para voltar ao estado inicial (próximo município)
                self.navegador_restos.get(self.url_restos_a_pagar)

                return {
                    'sucesso': True,
                    'municipio': municipio,
                    'tipo': 'restos_a_pagar',
                    'arquivo': None,
                    'sem_dados': True
                }

            # Passo 4: Clicar gerar CSV e aguardar download
            if not self.esperar_elemento_disponivel(
                self.navegador_restos,
                self.wait_restos,
                By.CSS_SELECTOR,
                SELETORES_PAGAMENTOS_RES_RESTOS['botao_gerar_csv'],
                lambda el: el.click()
            ):
                raise Exception("Timeout ao gerar CSV")

            # Passo 5: Aguardar arquivo CSV ser baixado (30s timeout)
            arquivo_baixado = self._aguardar_download_csv(self.dir_restos_a_pagar, timeout=30)

            if arquivo_baixado is None:
                if self._cancelado:
                    raise Exception("Download cancelado pelo usuário")
                else:
                    raise Exception("Arquivo CSV não foi baixado (timeout 30s)")

            # Passo 6: Renomear com retry (Windows file locking)
            arquivo_renomeado = self._renomear_arquivo_com_retry(
                arquivo_baixado,
                PAGAMENTOS_RES_CONFIG['formato_arquivo_restos'].format(municipio=municipio_arquivo)
            )

            print(f"  ✓ [RESTOS A PAGAR] {municipio} processado com sucesso")

            # Recarrega página para voltar ao estado inicial (próximo município)
            self.navegador_restos.get(self.url_restos_a_pagar)

            return {
                'sucesso': True,
                'municipio': municipio,
                'tipo': 'restos_a_pagar',
                'arquivo': arquivo_renomeado
            }

        except Exception as e:
            print(f"  ✗ [RESTOS A PAGAR] Erro em {municipio}: {e}")

            # Recarrega página mesmo em caso de erro (próximo município)
            try:
                self.navegador_restos.get(self.url_restos_a_pagar)
            except:
                pass

            return {
                'sucesso': False,
                'municipio': municipio,
                'tipo': 'restos_a_pagar',
                'erro': str(e)
            }

    def processar_municipio(self, ano: str, municipio: str) -> Dict:
        """Processa município nas DUAS URLs simultaneamente com threading sincronizado"""
        print(f"\n{'='*60}")
        print(f"Processando: {municipio} - {ano}")
        print(f"{'='*60}")

        resultado_consolidado = {
            'municipio': municipio,
            'ano': ano,
            'orcamentarios': None,
            'restos_a_pagar': None,
            'sucesso': False
        }

        # Thread 1: Pagamentos Orçamentários
        def executar_orcamentarios():
            resultado_consolidado['orcamentarios'] = self.processar_orcamentarios(municipio, ano)

        # Thread 2: Restos a Pagar
        def executar_restos():
            resultado_consolidado['restos_a_pagar'] = self.processar_restos_a_pagar(municipio, ano)

        # Executa ambas em paralelo
        thread_orcamentarios = threading.Thread(target=executar_orcamentarios, daemon=True)
        thread_restos = threading.Thread(target=executar_restos, daemon=True)

        thread_orcamentarios.start()
        thread_restos.start()

        # AGUARDA AMBAS TERMINAREM (sincronização) - com verificação de cancelamento
        while thread_orcamentarios.is_alive() or thread_restos.is_alive():
            if self._cancelado:
                print("\n⚠ Processamento de threads cancelado")
                return {
                    'municipio': municipio,
                    'ano': ano,
                    'orcamentarios': None,
                    'restos_a_pagar': None,
                    'sucesso': False
                }
            thread_orcamentarios.join(timeout=0.1)
            thread_restos.join(timeout=0.1)

        # Verifica se ambas tiveram sucesso
        if (resultado_consolidado['orcamentarios'] and resultado_consolidado['orcamentarios']['sucesso'] and
            resultado_consolidado['restos_a_pagar'] and resultado_consolidado['restos_a_pagar']['sucesso']):
            resultado_consolidado['sucesso'] = True
            print(f"✓ {municipio} processado com SUCESSO em ambas as URLs")
        else:
            print(f"✗ {municipio} teve falha em pelo menos uma URL")

        return resultado_consolidado

    def processar_todos_municipios(self, ano: str) -> Dict:
        """Processa todos os 853 municípios de MG e retorna estatísticas"""
        print(f"\n{'='*60}")
        print(f"PROCESSANDO TODOS OS MUNICÍPIOS - {ano}")
        print(f"Total de municípios: {len(self.municipios_mg)}")
        print(f"{'='*60}\n")

        estatisticas = {
            'total': len(self.municipios_mg),
            'sucessos': 0,
            'erros': 0,
            'orcamentarios_ok': 0,
            'restos_ok': 0,
            'taxa_sucesso': 0.0
        }

        for i, municipio in enumerate(self.municipios_mg, 1):
            if self._cancelado:
                print("\n⚠ Processamento cancelado pelo usuário")
                break

            print(f"\n[{i}/{len(self.municipios_mg)}] {municipio}")

            resultado = self.processar_municipio(ano, municipio)

            if resultado['sucesso']:
                estatisticas['sucessos'] += 1
            else:
                estatisticas['erros'] += 1

            if resultado['orcamentarios'] and resultado['orcamentarios']['sucesso']:
                estatisticas['orcamentarios_ok'] += 1

            if resultado['restos_a_pagar'] and resultado['restos_a_pagar']['sucesso']:
                estatisticas['restos_ok'] += 1

        # Calcula taxa de sucesso
        if estatisticas['total'] > 0:
            estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100

        print(f"\n{'='*60}")
        print("PROCESSAMENTO CONCLUÍDO")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos completos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Orçamentários OK: {estatisticas['orcamentarios_ok']}")
        print(f"Restos a Pagar OK: {estatisticas['restos_ok']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
        print(f"{'='*60}\n")

        return estatisticas

    def _aguardar_download_csv(self, diretorio: str, timeout: int = 30) -> Optional[str]:
        """Aguarda arquivo CSV usando timestamp (compatível com Windows .exe)"""
        self._sleep_cancelavel(3.0)

        for tentativa in range(timeout):
            if self._cancelado:
                return None

            try:
                arquivos = [f for f in os.listdir(diretorio)
                           if f.endswith('.csv') and not f.endswith(('.crdownload', '.tmp')) and not f.startswith('.')]

                if arquivos:
                    arquivo_mais_recente = max([os.path.join(diretorio, f) for f in arquivos], key=os.path.getctime)
                    if os.path.exists(arquivo_mais_recente) and os.path.getsize(arquivo_mais_recente) > 0:
                        print(f"  ✓ CSV detectado: {os.path.basename(arquivo_mais_recente)} ({os.path.getsize(arquivo_mais_recente)} bytes)")
                        return arquivo_mais_recente
            except:
                if tentativa % 5 == 0:
                    print(f"  ⓘ Aguardando arquivo CSV ({tentativa}s/{timeout}s)...")

            time.sleep(1.0)

        print(f"  ✗ Timeout ({timeout}s) - arquivo CSV não foi baixado")
        return None

    def _renomear_arquivo_com_retry(self, arquivo_original: str, novo_nome: str, max_tentativas: int = 3) -> str:
        """Renomeia arquivo com retry para lidar com file locking do Windows

        Args:
            arquivo_original: Caminho completo do arquivo original
            novo_nome: Apenas o nome do arquivo (sem path)
            max_tentativas: Número máximo de tentativas (padrão: 3)

        Returns:
            Caminho completo do arquivo renomeado

        Notes:
            - Windows pode bloquear arquivo temporariamente após download
            - Tenta até max_tentativas vezes com 0.5s de pausa entre tentativas
            - Retorna arquivo original se rename falhar (não-fatal, preserva dados)
        """
        diretorio = os.path.dirname(arquivo_original)
        caminho_final = os.path.join(diretorio, novo_nome)

        # Se já está com o nome correto, retorna
        if arquivo_original == caminho_final:
            return caminho_final

        # Tenta renomear com retry
        for tentativa in range(1, max_tentativas + 1):
            try:
                os.rename(arquivo_original, caminho_final)
                if tentativa > 1:
                    print(f"  ✓ Arquivo renomeado (tentativa {tentativa})")
                return caminho_final

            except PermissionError as e:
                # Windows file locking - tenta novamente
                if tentativa < max_tentativas:
                    print(f"  ⓘ Arquivo bloqueado (tentativa {tentativa}/{max_tentativas}) - aguardando...")
                    time.sleep(0.5)
                else:
                    # Última tentativa falhou - avisa mas não quebra
                    print(f"  ⚠ Aviso: Não foi possível renomear arquivo após {max_tentativas} tentativas: {e}")
                    return arquivo_original

            except Exception as e:
                # Outro erro - avisa mas não quebra
                print(f"  ⚠ Aviso: Erro ao renomear arquivo - {e}")
                return arquivo_original

        return arquivo_original

    def fechar_navegador(self):
        """Método compatível com GUI6 - fecha AMBOS os navegadores"""
        self.fechar_navegadores()

    def fechar_navegadores(self):
        """Fecha ambos os navegadores"""
        try:
            if self.navegador_orcamentarios:
                self.navegador_orcamentarios.quit()
                print("✓ Navegador orçamentários fechado")
        except Exception as e:
            print(f"Aviso: Erro ao fechar navegador orçamentários - {e}")

        try:
            if self.navegador_restos:
                self.navegador_restos.quit()
                print("✓ Navegador restos a pagar fechado")
        except Exception as e:
            print(f"Aviso: Erro ao fechar navegador restos a pagar - {e}")

    def cancelar_forcado(self):
        """Cancela execução e fecha navegadores imediatamente, matando processos Chrome"""
        import subprocess
        import platform

        self._cancelado = True
        print("\n⚠ Cancelamento forçado iniciado...")

        # Fecha navegador orçamentários de forma agressiva
        if self.navegador_orcamentarios:
            print("  → Fechando navegador orçamentários...")
            try:
                # Mata o processo do ChromeDriver service primeiro
                if hasattr(self.navegador_orcamentarios, 'service') and hasattr(self.navegador_orcamentarios.service, 'process'):
                    try:
                        print("    • Terminando processo ChromeDriver (orçamentários)...")
                        self.navegador_orcamentarios.service.process.terminate()
                        self.navegador_orcamentarios.service.process.wait(timeout=2)
                    except:
                        try:
                            print("    • Matando processo ChromeDriver (orçamentários)...")
                            self.navegador_orcamentarios.service.process.kill()
                        except:
                            pass

                # Depois tenta quit() normal
                print("    • Chamando quit() (orçamentários)...")
                self.navegador_orcamentarios.quit()
                print("    ✓ Navegador orçamentários fechado")
            except Exception as e:
                print(f"    ⚠ Erro ao fechar navegador orçamentários: {e}")
            finally:
                self.navegador_orcamentarios = None

        # Fecha navegador restos a pagar de forma agressiva
        if self.navegador_restos:
            print("  → Fechando navegador restos a pagar...")
            try:
                # Mata o processo do ChromeDriver service primeiro
                if hasattr(self.navegador_restos, 'service') and hasattr(self.navegador_restos.service, 'process'):
                    try:
                        print("    • Terminando processo ChromeDriver (restos)...")
                        self.navegador_restos.service.process.terminate()
                        self.navegador_restos.service.process.wait(timeout=2)
                    except:
                        try:
                            print("    • Matando processo ChromeDriver (restos)...")
                            self.navegador_restos.service.process.kill()
                        except:
                            pass

                # Depois tenta quit() normal
                print("    • Chamando quit() (restos)...")
                self.navegador_restos.quit()
                print("    ✓ Navegador restos a pagar fechado")
            except Exception as e:
                print(f"    ⚠ Erro ao fechar navegador restos: {e}")
            finally:
                self.navegador_restos = None

        # Mata todos os processos Chrome/ChromeDriver restantes (fallback)
        print("  → Limpando processos Chrome restantes...")
        try:
            sistema = platform.system()
            if sistema == "Darwin":  # macOS
                subprocess.run(["pkill", "-f", "Chrome"], stderr=subprocess.DEVNULL, timeout=3)
                subprocess.run(["pkill", "-f", "chromedriver"], stderr=subprocess.DEVNULL, timeout=3)
            elif sistema == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stderr=subprocess.DEVNULL, timeout=3)
                subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe"], stderr=subprocess.DEVNULL, timeout=3)
            elif sistema == "Linux":
                subprocess.run(["pkill", "-f", "chrome"], stderr=subprocess.DEVNULL, timeout=3)
                subprocess.run(["pkill", "-f", "chromedriver"], stderr=subprocess.DEVNULL, timeout=3)
        except Exception as e:
            print(f"    ⚠ Erro ao limpar processos: {e}")

        # Aguarda processos terminarem completamente
        time.sleep(1)
        print("✓ Cancelamento forçado concluído - todos os processos Chrome fechados")


if __name__ == "__main__":
    # Teste do bot Pagamentos de Resoluções
    print("Testando BotPagamentosRes...")

    bot = BotPagamentosRes()

    if bot.configurar_navegadores():
        # Teste com um município
        resultado = bot.processar_municipio("2025", "BELO HORIZONTE")
        print(f"\nResultado: {resultado}")

        bot.fechar_navegadores()
    else:
        print("Falha ao configurar navegadores")
