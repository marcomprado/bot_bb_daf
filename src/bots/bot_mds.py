#!/usr/bin/env python3
"""
Bot de scraping para o sistema MDS (Ministério do Desenvolvimento Social)
URLs:
    Parcelas pagas : https://aplicacoes.mds.gov.br/suaswebcons/restrito/execute.jsf?b=*dpotvmubsQbsdfmbtQbhbtNC&event=*fyjcjs
    Saldo por Conta : https://aplicacoes.mds.gov.br/suaswebcons/restrito/execute.jsf?b=*tbmepQbsdfmbtQbhbtNC&event=*fyjcjs

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
from src.classes.central import MDS_CONFIG, SELETORES_MDS_PARCELAS, SELETORES_MDS_SALDO, MENSAGENS


class BotMDS(BotBase):
    # Bot de scraping MDS com sincronização de duas URLs simultâneas

    def __init__(self, timeout=None):
        # Inicializa o bot MDS usando configurações centralizadas de central.py
        super().__init__()

        # URLs do MDS (central.py)
        self.url_parcelas = MDS_CONFIG['url_parcelas']
        self.url_saldo = MDS_CONFIG['url_saldo']

        # Duas instâncias de navegador
        self.navegador_parcelas = None
        self.navegador_saldo = None
        self.wait_parcelas = None
        self.wait_saldo = None

        # Configurações (central.py)
        self.timeout = timeout or MDS_CONFIG['timeout_selenium']
        self.max_tentativas = MDS_CONFIG['max_tentativas_espera']
        self.max_retries = MDS_CONFIG['max_retries']
        self.city_manager = CityManager()
        self.municipios_mg = self.city_manager.obter_municipios_mg()

        # Flags de controle
        self._cancelado = False
        self._em_execucao = False

        # Configuração de diretórios (central.py)
        self.diretorio_mds = obter_caminho_dados(MDS_CONFIG['diretorio_saida'])
        self.diretorio_base = os.path.dirname(self.diretorio_mds)

        self._criar_diretorios()
        self.report_gen = ReportGenerator(self.diretorio_mds, MDS_CONFIG['prefixo_relatorio'])

    def _criar_diretorios(self):
        # Cria estrutura de diretórios necessária
        try:
            for diretorio in [self.diretorio_base, self.diretorio_mds]:
                if not os.path.exists(diretorio):
                    os.makedirs(diretorio)
        except Exception as e:
            print(f"Aviso: Erro ao criar diretórios - {e}")

    def configurar_navegador(self) -> bool:
        # Método compatível com GUI7 - configura AMBOS os navegadores
        return self.configurar_navegadores()

    def configurar_navegadores(self) -> bool:
        # Configura DUAS instâncias Chrome com diretórios de download separados (central.py)
        try:
            print("Configurando navegadores MDS...")

            # Criar diretórios finais
            self.dir_parcela = os.path.join(self.diretorio_mds, MDS_CONFIG['subdiretorios_finais'][0])
            self.dir_saldo = os.path.join(self.diretorio_mds, MDS_CONFIG['subdiretorios_finais'][1])
            os.makedirs(self.dir_parcela, exist_ok=True)
            os.makedirs(self.dir_saldo, exist_ok=True)

            # Navegador 1: Parcelas Pagas (baixa direto em mds/parcela/)
            opcoes_parcelas = webdriver.ChromeOptions()
            opcoes_parcelas.add_argument("--headless=new")
            opcoes_parcelas.add_argument("--disable-gpu")
            opcoes_parcelas.add_argument("--window-size=1920,1080")

            driver_parcelas = ChromeDriverSimples(download_dir=self.dir_parcela)
            self.navegador_parcelas = driver_parcelas.conectar(chrome_options=opcoes_parcelas)
            self.wait_parcelas = WebDriverWait(self.navegador_parcelas, self.timeout)

            # Navegador 2: Saldo por Conta (baixa direto em mds/saldo/)
            opcoes_saldo = webdriver.ChromeOptions()
            #opcoes_saldo.add_argument("--headless=new")
            opcoes_saldo.add_argument("--disable-gpu")
            opcoes_saldo.add_argument("--window-size=1920,1080")

            driver_saldo = ChromeDriverSimples(download_dir=self.dir_saldo)
            self.navegador_saldo = driver_saldo.conectar(chrome_options=opcoes_saldo)
            self.wait_saldo = WebDriverWait(self.navegador_saldo, self.timeout)

            # Abre as URLs
            print("Abrindo URLs do MDS...")
            self.navegador_parcelas.get(self.url_parcelas)
            self.navegador_saldo.get(self.url_saldo)

            print("✓ Navegadores configurados com sucesso (modo headless)")
            return True

        except Exception as e:
            print(f"✗ Erro ao configurar navegadores: {e}")
            return False

    def _sleep_cancelavel(self, segundos: float):
        # Sleep que pode ser interrompido por cancelamento
        inicio = time.time()
        while time.time() - inicio < segundos:
            if self._cancelado:
                return
            time.sleep(0.1)  # Verifica a cada 100ms

    def esperar_elemento_disponivel(self, navegador, wait, by, seletor, acao_callback, max_tentativas=None):
        # Tenta realizar ação até N vezes devido ao loading do site MDS (central.py)
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

            except (TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, StaleElementReferenceException):
                if self._cancelado:
                    return False
                if tentativa == max_tentativas:
                    print(f"  ✗ Timeout após {max_tentativas} tentativas")
                    return False
                time.sleep(MDS_CONFIG['pausa_tentativa_espera'])  # Aguarda antes de tentar novamente (central.py)

        return False

    def verificar_resultado_vazio(self, navegador, wait) -> bool:
        # Verifica se a pesquisa retornou "Nenhum registro encontrado"
        try:
            # Tenta encontrar a mensagem de "sem registros" com timeout curto (2 segundos)
            mensagem = WebDriverWait(navegador, 2).until(
                EC.presence_of_element_located((By.XPATH, "//span[@id='mensagens']//div[@class='info']"))
            )
            texto = mensagem.text.strip().lower()

            # Verifica se contém "nenhum registro" ou similar
            if "nenhum registro" in texto or "sem registros" in texto or "not found" in texto:
                print(f"  ⓘ Nenhum registro encontrado para este município")
                return True

        except:
            # Se não encontrou a mensagem em 2 segundos, assume que há resultados
            pass

        return False

    def processar_parcelas(self, municipio: str, ano: str, max_retries=None) -> Dict:
        # Processa URL de Parcelas Pagas: seleciona ano, UF=MG, município, pesquisar, gerar CSV, renomear (central.py)
        if self._cancelado:
            return {'sucesso': False, 'municipio': municipio, 'tipo': 'parcelas', 'erro': 'Cancelado'}

        municipio_upper = municipio.upper()
        max_retries = max_retries or self.max_retries

        for tentativa in range(1, max_retries + 1):
            if self._cancelado:
                return {'sucesso': False, 'municipio': municipio, 'tipo': 'parcelas', 'erro': 'Cancelado'}

            try:
                print(f"  [PARCELAS] Processando {municipio} (tentativa {tentativa})")

                # Passo 1: Selecionar ano (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_parcelas,
                    self.wait_parcelas,
                    By.ID,
                    SELETORES_MDS_PARCELAS['select_ano'],
                    lambda el: Select(el).select_by_value(ano)
                ):
                    raise Exception("Timeout ao selecionar ano")

                # Aguarda UF dropdown carregar após seleção de ano
                try:
                    self.wait_parcelas.until(
                        EC.presence_of_element_located((By.ID, SELETORES_MDS_PARCELAS['select_uf']))
                    )
                except:
                    pass

                # Passo 2: Selecionar UF = MG (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_parcelas,
                    self.wait_parcelas,
                    By.ID,
                    SELETORES_MDS_PARCELAS['select_uf'],
                    lambda el: Select(el).select_by_value(MDS_CONFIG['uf_padrao'])
                ):
                    raise Exception("Timeout ao selecionar UF")

                # Aguarda Município dropdown carregar após seleção de UF
                try:
                    self.wait_parcelas.until(
                        EC.presence_of_element_located((By.ID, SELETORES_MDS_PARCELAS['select_municipio']))
                    )
                except:
                    pass

                # Passo 3: Selecionar município (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_parcelas,
                    self.wait_parcelas,
                    By.ID,
                    SELETORES_MDS_PARCELAS['select_municipio'],
                    lambda el: Select(el).select_by_visible_text(municipio_upper)
                ):
                    raise Exception("Timeout ao selecionar município")

                # Aguarda botão Pesquisar estar disponível após seleção de município
                try:
                    self.wait_parcelas.until(
                        EC.element_to_be_clickable((By.ID, SELETORES_MDS_PARCELAS['botao_pesquisar']))
                    )
                except:
                    pass

                # Passo 4: Clicar pesquisar (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_parcelas,
                    self.wait_parcelas,
                    By.ID,
                    SELETORES_MDS_PARCELAS['botao_pesquisar'],
                    lambda el: el.click()
                ):
                    raise Exception("Timeout ao clicar pesquisar")

                # Verificar se retornou registros
                if self.verificar_resultado_vazio(self.navegador_parcelas, self.wait_parcelas):
                    print(f"  ⓘ [PARCELAS] Sem dados para {municipio} - continuando")
                    return {
                        'sucesso': True,  # Considera sucesso (município processado, sem dados)
                        'municipio': municipio,
                        'tipo': 'parcelas',
                        'arquivo': None,  # Nenhum arquivo gerado
                        'sem_dados': True  # Flag indicando ausência de dados
                    }

                # Passo 5: Clicar gerar CSV (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_parcelas,
                    self.wait_parcelas,
                    By.XPATH,
                    SELETORES_MDS_PARCELAS['botao_gerar_csv'],
                    lambda el: el.click()
                ):
                    raise Exception("Timeout ao gerar CSV")

                # Aguarda download (central.py)
                self._sleep_cancelavel(MDS_CONFIG['pausa_aguarda_download'])

                # Passo 6: Renomear arquivo (central.py)
                arquivo_renomeado = self._renomear_ultimo_download(
                    self.dir_parcela,
                    MDS_CONFIG['formato_arquivo'].format(municipio=municipio)
                )

                print(f"  ✓ [PARCELAS] {municipio} processado com sucesso")
                return {
                    'sucesso': True,
                    'municipio': municipio,
                    'tipo': 'parcelas',
                    'arquivo': arquivo_renomeado
                }

            except Exception as e:
                print(f"  ✗ [PARCELAS] Erro em {municipio}: {e}")

                if tentativa < max_retries:
                    # Fecha e reabre navegador
                    try:
                        self.navegador_parcelas.quit()
                    except:
                        pass
                    self._reconfigurar_navegador_parcelas()
                    continue
                else:
                    return {
                        'sucesso': False,
                        'municipio': municipio,
                        'tipo': 'parcelas',
                        'erro': str(e)
                    }

        return {'sucesso': False, 'municipio': municipio, 'tipo': 'parcelas', 'erro': 'Max retries'}

    def processar_saldo(self, municipio: str, ano: str, mes: str, max_retries=None) -> Dict:
        # Processa URL de Saldo por Conta: seleciona ano, UF=MG, mês, esfera=MUNICIPAL, município, pesquisar, gerar CSV, renomear (central.py)
        if self._cancelado:
            return {'sucesso': False, 'municipio': municipio, 'tipo': 'saldo', 'erro': 'Cancelado'}

        municipio_upper = municipio.upper()
        max_retries = max_retries or self.max_retries

        for tentativa in range(1, max_retries + 1):
            if self._cancelado:
                return {'sucesso': False, 'municipio': municipio, 'tipo': 'saldo', 'erro': 'Cancelado'}

            try:
                print(f"  [SALDO] Processando {municipio} (tentativa {tentativa})")

                # Passo 1: Selecionar ano (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_saldo,
                    self.wait_saldo,
                    By.ID,
                    SELETORES_MDS_SALDO['select_ano'],
                    lambda el: Select(el).select_by_value(ano)
                ):
                    raise Exception("Timeout ao selecionar ano")

                # Aguarda UF dropdown carregar após seleção de ano
                try:
                    self.wait_saldo.until(
                        EC.presence_of_element_located((By.ID, SELETORES_MDS_SALDO['select_uf']))
                    )
                except:
                    pass

                # Passo 2: Selecionar UF = MG (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_saldo,
                    self.wait_saldo,
                    By.ID,
                    SELETORES_MDS_SALDO['select_uf'],
                    lambda el: Select(el).select_by_value(MDS_CONFIG['uf_padrao'])
                ):
                    raise Exception("Timeout ao selecionar UF")

                # Aguarda Mês dropdown carregar após seleção de UF
                try:
                    self.wait_saldo.until(
                        EC.presence_of_element_located((By.ID, SELETORES_MDS_SALDO['select_mes']))
                    )
                except:
                    pass

                # Passo 3: Selecionar mês (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_saldo,
                    self.wait_saldo,
                    By.ID,
                    SELETORES_MDS_SALDO['select_mes'],
                    lambda el: Select(el).select_by_visible_text(mes)
                ):
                    raise Exception("Timeout ao selecionar mês")

                # Aguarda Esfera dropdown carregar após seleção de mês
                try:
                    self.wait_saldo.until(
                        EC.presence_of_element_located((By.ID, SELETORES_MDS_SALDO['select_esfera']))
                    )
                except:
                    pass

                # Passo 4: Selecionar Esfera = MUNICIPAL (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_saldo,
                    self.wait_saldo,
                    By.ID,
                    SELETORES_MDS_SALDO['select_esfera'],
                    lambda el: Select(el).select_by_value(MDS_CONFIG['esfera_padrao'])
                ):
                    raise Exception("Timeout ao selecionar esfera")

                # Aguarda Município dropdown carregar após seleção de esfera
                try:
                    self.wait_saldo.until(
                        EC.presence_of_element_located((By.ID, SELETORES_MDS_SALDO['select_municipio']))
                    )
                except:
                    pass

                # Passo 5: Selecionar município (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_saldo,
                    self.wait_saldo,
                    By.ID,
                    SELETORES_MDS_SALDO['select_municipio'],
                    lambda el: Select(el).select_by_visible_text(municipio_upper)
                ):
                    raise Exception("Timeout ao selecionar município")

                # Aguarda botão Pesquisar estar disponível após seleção de município
                try:
                    self.wait_saldo.until(
                        EC.element_to_be_clickable((By.ID, SELETORES_MDS_SALDO['botao_pesquisar']))
                    )
                except:
                    pass

                # Passo 6: Clicar pesquisar (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_saldo,
                    self.wait_saldo,
                    By.ID,
                    SELETORES_MDS_SALDO['botao_pesquisar'],
                    lambda el: el.click()
                ):
                    raise Exception("Timeout ao clicar pesquisar")

                # Aguardar 60 segundos após pesquisar
                print("  ⏱ [SALDO] Aguardando 60 segundos após pesquisa...")
                self._sleep_cancelavel(60)

                # Verificar se retornou registros
                if self.verificar_resultado_vazio(self.navegador_saldo, self.wait_saldo):
                    print(f"  ⓘ [SALDO] Sem dados para {municipio} - continuando")
                    return {
                        'sucesso': True,  # Considera sucesso (município processado, sem dados)
                        'municipio': municipio,
                        'tipo': 'saldo',
                        'arquivo': None,  # Nenhum arquivo gerado
                        'sem_dados': True  # Flag indicando ausência de dados
                    }

                # Passo 7: Clicar gerar CSV (central.py)
                if not self.esperar_elemento_disponivel(
                    self.navegador_saldo,
                    self.wait_saldo,
                    By.XPATH,
                    SELETORES_MDS_SALDO['botao_gerar_csv'],
                    lambda el: el.click()
                ):
                    raise Exception("Timeout ao gerar CSV")

                # Aguarda download (central.py)
                self._sleep_cancelavel(MDS_CONFIG['pausa_aguarda_download'])

                # Passo 8: Renomear arquivo (central.py)
                arquivo_renomeado = self._renomear_ultimo_download(
                    self.dir_saldo,
                    MDS_CONFIG['formato_arquivo'].format(municipio=municipio)
                )

                print(f"  ✓ [SALDO] {municipio} processado com sucesso")
                return {
                    'sucesso': True,
                    'municipio': municipio,
                    'tipo': 'saldo',
                    'arquivo': arquivo_renomeado
                }

            except Exception as e:
                print(f"  ✗ [SALDO] Erro em {municipio}: {e}")

                if tentativa < max_retries:
                    # Fecha e reabre navegador
                    try:
                        self.navegador_saldo.quit()
                    except:
                        pass
                    self._reconfigurar_navegador_saldo()
                    continue
                else:
                    return {
                        'sucesso': False,
                        'municipio': municipio,
                        'tipo': 'saldo',
                        'erro': str(e)
                    }

        return {'sucesso': False, 'municipio': municipio, 'tipo': 'saldo', 'erro': 'Max retries'}

    def processar_municipio(self, ano: str, mes: str, municipio: str) -> Dict:
        # Processa município nas DUAS URLs simultaneamente com threading sincronizado
        print(f"\n{'='*60}")
        print(f"Processando: {municipio} - {mes}/{ano}")
        print(f"{'='*60}")

        resultado_consolidado = {
            'municipio': municipio,
            'ano': ano,
            'mes': mes,
            'parcelas': None,
            'saldo': None,
            'sucesso': False
        }

        # Thread 1: Parcelas Pagas
        def executar_parcelas():
            resultado_consolidado['parcelas'] = self.processar_parcelas(municipio, ano)

        # Thread 2: Saldo por Conta
        def executar_saldo():
            resultado_consolidado['saldo'] = self.processar_saldo(municipio, ano, mes)

        # Executa ambas em paralelo
        thread_parcelas = threading.Thread(target=executar_parcelas, daemon=True)
        thread_saldo = threading.Thread(target=executar_saldo, daemon=True)

        thread_parcelas.start()
        thread_saldo.start()

        # AGUARDA AMBAS TERMINAREM (sincronização) - com verificação de cancelamento
        while thread_parcelas.is_alive() or thread_saldo.is_alive():
            if self._cancelado:
                print("\n⚠ Processamento de threads cancelado")
                return {
                    'municipio': municipio,
                    'ano': ano,
                    'mes': mes,
                    'parcelas': None,
                    'saldo': None,
                    'sucesso': False
                }
            thread_parcelas.join(timeout=0.1)
            thread_saldo.join(timeout=0.1)

        # Verifica se ambas tiveram sucesso
        if (resultado_consolidado['parcelas'] and resultado_consolidado['parcelas']['sucesso'] and
            resultado_consolidado['saldo'] and resultado_consolidado['saldo']['sucesso']):
            resultado_consolidado['sucesso'] = True
            print(f"✓ {municipio} processado com SUCESSO em ambas as URLs")
        else:
            print(f"✗ {municipio} teve falha em pelo menos uma URL")

        return resultado_consolidado

    def processar_todos_municipios(self, ano: str, mes: str) -> Dict:
        # Processa todos os 853 municípios de MG e retorna estatísticas
        print(f"\n{'='*60}")
        print(f"PROCESSANDO TODOS OS MUNICÍPIOS - {mes}/{ano}")
        print(f"Total de municípios: {len(self.municipios_mg)}")
        print(f"{'='*60}\n")

        estatisticas = {
            'total': len(self.municipios_mg),
            'sucessos': 0,
            'erros': 0,
            'parcelas_ok': 0,
            'saldo_ok': 0,
            'taxa_sucesso': 0.0
        }

        for i, municipio in enumerate(self.municipios_mg, 1):
            if self._cancelado:
                print("\n⚠ Processamento cancelado pelo usuário")
                break

            print(f"\n[{i}/{len(self.municipios_mg)}] {municipio}")

            resultado = self.processar_municipio(ano, mes, municipio)

            if resultado['sucesso']:
                estatisticas['sucessos'] += 1
            else:
                estatisticas['erros'] += 1

            if resultado['parcelas'] and resultado['parcelas']['sucesso']:
                estatisticas['parcelas_ok'] += 1

            if resultado['saldo'] and resultado['saldo']['sucesso']:
                estatisticas['saldo_ok'] += 1

        # Calcula taxa de sucesso
        if estatisticas['total'] > 0:
            estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100

        print(f"\n{'='*60}")
        print("PROCESSAMENTO CONCLUÍDO")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos completos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Parcelas OK: {estatisticas['parcelas_ok']}")
        print(f"Saldo OK: {estatisticas['saldo_ok']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
        print(f"{'='*60}\n")

        return estatisticas

    def _renomear_ultimo_download(self, diretorio: str, novo_nome: str) -> str:
        # Renomeia o último arquivo CSV baixado no diretório (central.py)
        for _ in range(MDS_CONFIG['timeout_renomear_arquivo']):
            if self._cancelado:
                raise Exception("Cancelado pelo usuário")

            try:
                arquivos = [f for f in os.listdir(diretorio) if f.endswith('.csv') and not f.startswith('.')]
                if arquivos:
                    # Pega o arquivo mais recente
                    arquivo_mais_recente = max(
                        [os.path.join(diretorio, f) for f in arquivos],
                        key=os.path.getctime
                    )

                    # Renomeia no mesmo diretório (já está no lugar final)
                    caminho_final = os.path.join(diretorio, novo_nome)
                    os.rename(arquivo_mais_recente, caminho_final)
                    return caminho_final
            except Exception:
                pass

            time.sleep(MDS_CONFIG['pausa_tentativa_espera'])  # Aguarda antes de tentar novamente (central.py)

        raise Exception("Arquivo CSV não foi baixado")

    def _reconfigurar_navegador_parcelas(self):
        # Reconfigura navegador de parcelas após erro (central.py)
        opcoes = webdriver.ChromeOptions()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--disable-gpu")
        opcoes.add_argument("--window-size=1920,1080")

        driver = ChromeDriverSimples(download_dir=self.dir_parcela)
        self.navegador_parcelas = driver.conectar(chrome_options=opcoes)
        self.wait_parcelas = WebDriverWait(self.navegador_parcelas, self.timeout)
        self.navegador_parcelas.get(self.url_parcelas)

    def _reconfigurar_navegador_saldo(self):
        # Reconfigura navegador de saldo após erro (central.py)
        opcoes = webdriver.ChromeOptions()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--disable-gpu")
        opcoes.add_argument("--window-size=1920,1080")

        driver = ChromeDriverSimples(download_dir=self.dir_saldo)
        self.navegador_saldo = driver.conectar(chrome_options=opcoes)
        self.wait_saldo = WebDriverWait(self.navegador_saldo, self.timeout)
        self.navegador_saldo.get(self.url_saldo)

    def fechar_navegador(self):
        # Método compatível com GUI7 - fecha AMBOS os navegadores
        self.fechar_navegadores()

    def fechar_navegadores(self):
        # Fecha ambos os navegadores
        try:
            if self.navegador_parcelas:
                self.navegador_parcelas.quit()
                print("✓ Navegador parcelas fechado")
        except Exception as e:
            print(f"Aviso: Erro ao fechar navegador parcelas - {e}")

        try:
            if self.navegador_saldo:
                self.navegador_saldo.quit()
                print("✓ Navegador saldo fechado")
        except Exception as e:
            print(f"Aviso: Erro ao fechar navegador saldo - {e}")

    def cancelar_forcado(self):
        """Cancela execução e fecha navegadores imediatamente, matando processos Chrome"""
        import subprocess
        import platform

        self._cancelado = True
        print("\n⚠ Cancelamento forçado iniciado...")

        # Fecha navegador parcelas de forma agressiva
        if self.navegador_parcelas:
            print("  → Fechando navegador parcelas...")
            try:
                # Mata o processo do ChromeDriver service primeiro
                if hasattr(self.navegador_parcelas, 'service') and hasattr(self.navegador_parcelas.service, 'process'):
                    try:
                        print("    • Terminando processo ChromeDriver (parcelas)...")
                        self.navegador_parcelas.service.process.terminate()
                        self.navegador_parcelas.service.process.wait(timeout=2)
                    except:
                        try:
                            print("    • Matando processo ChromeDriver (parcelas)...")
                            self.navegador_parcelas.service.process.kill()
                        except:
                            pass

                # Depois tenta quit() normal
                print("    • Chamando quit() (parcelas)...")
                self.navegador_parcelas.quit()
                print("    ✓ Navegador parcelas fechado")
            except Exception as e:
                print(f"    ⚠ Erro ao fechar navegador parcelas: {e}")
            finally:
                self.navegador_parcelas = None

        # Fecha navegador saldo de forma agressiva
        if self.navegador_saldo:
            print("  → Fechando navegador saldo...")
            try:
                # Mata o processo do ChromeDriver service primeiro
                if hasattr(self.navegador_saldo, 'service') and hasattr(self.navegador_saldo.service, 'process'):
                    try:
                        print("    • Terminando processo ChromeDriver (saldo)...")
                        self.navegador_saldo.service.process.terminate()
                        self.navegador_saldo.service.process.wait(timeout=2)
                    except:
                        try:
                            print("    • Matando processo ChromeDriver (saldo)...")
                            self.navegador_saldo.service.process.kill()
                        except:
                            pass

                # Depois tenta quit() normal
                print("    • Chamando quit() (saldo)...")
                self.navegador_saldo.quit()
                print("    ✓ Navegador saldo fechado")
            except Exception as e:
                print(f"    ⚠ Erro ao fechar navegador saldo: {e}")
            finally:
                self.navegador_saldo = None

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
    # Teste do bot MDS
    print("Testando BotMDS...")

    bot = BotMDS()

    if bot.configurar_navegadores():
        # Teste com um município
        resultado = bot.processar_municipio("2025", "01", "BELO HORIZONTE")
        print(f"\nResultado: {resultado}")

        bot.fechar_navegadores()
    else:
        print("Falha ao configurar navegadores")
