#!/usr/bin/env python3
"""
Bot de scraping para o Portal Saude MG - Resolucoes PDF
Extrai documentos PDF do portal antigo de saude de Minas Gerais
"""

from selenium import webdriver
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.classes.chrome_driver import ChromeDriverSimples
from src.classes.methods.cancel_method import BotBase
from src.classes.config import PORTAL_SAUDE_CONFIG, SELETORES_PORTAL_SAUDE
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import shutil
import requests
from datetime import datetime
from typing import List, Dict, Optional, Callable
from urllib.parse import urljoin
from src.classes.file.path_manager import obter_caminho_dados


# Mapeamento de meses (nome -> numero)
MESES_PARA_NUMERO = {
    "Janeiro": "01",
    "Fevereiro": "02",
    "Março": "03",
    "Abril": "04",
    "Maio": "05",
    "Junho": "06",
    "Julho": "07",
    "Agosto": "08",
    "Setembro": "09",
    "Outubro": "10",
    "Novembro": "11",
    "Dezembro": "12",
    "Todos os Meses": None,
}


class BotPortalSaude(BotBase):
    """
    Bot de scraping para o Portal Saude MG

    Funcionalidades:
    - Navega ao portal com filtros de ano e mes
    - Executa scroll infinito para carregar todos os resultados
    - Coleta links de documentos PDF
    - Baixa e valida arquivos PDF
    - Suporta cancelamento e execucao paralela
    """

    def __init__(self, timeout: int = 10):
        """Inicializa o bot Portal Saude MG"""
        super().__init__()
        self.base_url = PORTAL_SAUDE_CONFIG['url_base']
        self.params_base = PORTAL_SAUDE_CONFIG['params_base']
        self.timeout = timeout
        self.timeout_scroll = PORTAL_SAUDE_CONFIG['timeout_scroll']
        self._cancelado = False
        self._em_execucao = False
        self.navegador = None
        self.wait = None

        # Diretorios
        self.diretorio_base = obter_caminho_dados(PORTAL_SAUDE_CONFIG['diretorio_saida'])
        self._criar_diretorios()

    def _criar_diretorios(self):
        """Cria estrutura de diretorios necessaria"""
        try:
            if not os.path.exists(self.diretorio_base):
                os.makedirs(self.diretorio_base)
                print(f"Diretorio criado: {self.diretorio_base}")
        except Exception as e:
            print(f"Aviso: Erro ao criar diretorio - {e}")

    def _gerar_periodos(self, ano: str, mes: str = None) -> List[tuple]:
        """
        Gera lista de periodos (ano, mes_numero) para processar
        """
        periodos = []
        ano_atual = datetime.now().year
        mes_atual = datetime.now().month

        # Determina lista de anos
        if ano == "Todos os Anos":
            anos = [str(a) for a in range(2007, ano_atual + 1)]
        else:
            anos = [ano]

        # Para cada ano, determina lista de meses
        for ano_item in anos:
            ano_int = int(ano_item)

            if mes is None or mes == "Todos os Meses":
                # Determina ate qual mes processar
                if ano_int == ano_atual:
                    # Ano atual: processa ate mes atual
                    meses = [f"{m:02d}" for m in range(1, mes_atual + 1)]
                else:
                    # Anos anteriores: processa todos os 12 meses
                    meses = [f"{m:02d}" for m in range(1, 13)]
            else:
                # Mes especifico selecionado
                mes_num = MESES_PARA_NUMERO.get(mes)
                if mes_num:
                    meses = [mes_num]
                else:
                    meses = ["01"]  # Fallback

            # Adiciona periodos
            for mes_num in meses:
                periodos.append((ano_item, mes_num))

        print(f"Periodos a processar: {len(periodos)}")
        return periodos

    def _obter_diretorio_saida(self, ano: str, mes: str = None) -> str:
        """
        Retorna diretorio de saida organizado por ano/mes
        Pattern: portal_saude_mg/[ano]/[mes]_[nome]/
        """
        # Mapeamento de numero para nome do mes
        NUMERO_PARA_NOME = {
            "01": "janeiro", "02": "fevereiro", "03": "marco", "04": "abril",
            "05": "maio", "06": "junho", "07": "julho", "08": "agosto",
            "09": "setembro", "10": "outubro", "11": "novembro", "12": "dezembro"
        }

        ano_dir = os.path.join(self.diretorio_base, ano)

        if mes and mes != "Todos os Meses":
            # Verifica se mes ja e um numero (ex: "01")
            if mes in NUMERO_PARA_NOME:
                mes_num = mes
                mes_nome = NUMERO_PARA_NOME[mes]
            else:
                # Mes e um nome (ex: "Janeiro")
                mes_num = MESES_PARA_NUMERO.get(mes, "01")
                mes_nome = mes.lower()

            mes_dir = f"{mes_num}_{mes_nome}"
            return os.path.join(ano_dir, mes_dir)
        else:
            return os.path.join(ano_dir, "todos_meses")

    def _verificar_cancelamento(self, resultado: Dict = None) -> bool:
        """Verifica se execucao foi cancelada e fecha navegador"""
        if self._cancelado:
            if resultado:
                resultado['erro'] = "Processamento cancelado"
            # Fecha navegador imediatamente
            self.fechar_navegador()
            return True
        return False

    def configurar_navegador(self) -> bool:
        """Configura o navegador Chrome em modo headless"""
        try:
            opcoes = webdriver.ChromeOptions()
            # opcoes.add_argument("--headless=new")  # Desabilitado para testes
            opcoes.add_argument("--disable-gpu")
            opcoes.add_argument("--window-size=1920,1080")
            opcoes.add_argument("--no-sandbox")
            opcoes.add_argument("--disable-dev-shm-usage")

            driver_simples = ChromeDriverSimples()
            self.navegador = driver_simples.conectar(chrome_options=opcoes)

            if self.navegador:
                self.wait = WebDriverWait(self.navegador, self.timeout)
                self.navegador.implicitly_wait(PORTAL_SAUDE_CONFIG['timeout_selenium'])
                print("Navegador Chrome configurado com sucesso")
                return True
            else:
                print("Falha ao conectar com ChromeDriver")
                return False

        except Exception as e:
            print(f"Erro ao configurar navegador: {e}")
            return False

    def _construir_url(self, ano: str, mes: str = None) -> str:
        """
        Constroi URL com filtros de ano e mes
        """
        # Determina valor do ano
        if ano == "Todos os Anos":
            ano_param = "0"
        else:
            ano_param = ano

        # Determina valor do mes
        if mes and mes != "Todos os Meses":
            # Se mes ja e numero (ex: "01"), usa direto
            if mes.isdigit() and len(mes) == 2:
                mes_num = mes
            else:
                # Se mes e nome (ex: "Janeiro"), converte para numero
                mes_num = MESES_PARA_NUMERO.get(mes, "")
        else:
            mes_num = ""

        # Monta URL
        url = f"{self.base_url}?by_year={ano_param}&by_month={mes_num}&{self.params_base}"
        return url

    def abrir_pagina(self, ano: str, mes: str = None) -> bool:
        """Abre a pagina do portal com os filtros aplicados"""
        try:
            url = self._construir_url(ano, mes)
            print(f"Abrindo pagina: {url}")
            self.navegador.get(url)

            # Aguarda carregamento da pagina
            WebDriverWait(self.navegador, PORTAL_SAUDE_CONFIG['timeout_carregamento_maximo']).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Aguardo adicional para conteudo dinamico

            # Verifica se pagina carregou corretamente
            if self._verificar_pagina_carregada():
                print("Pagina carregada com sucesso")
                return True
            else:
                print("Aviso: Elementos da pagina nao encontrados, tentando continuar...")
                return True  # Continua mesmo assim

        except TimeoutException:
            print("Timeout: Pagina demorou para carregar")
            return False
        except Exception as e:
            print(f"Erro ao abrir pagina: {e}")
            return False

    def _verificar_pagina_carregada(self) -> bool:
        """Verifica se a pagina carregou corretamente"""
        try:
            # Verifica presenca de elementos essenciais
            elementos_ano = self.navegador.find_elements(By.CSS_SELECTOR, SELETORES_PORTAL_SAUDE['select_ano'])
            elementos_busca = self.navegador.find_elements(By.CSS_SELECTOR, SELETORES_PORTAL_SAUDE['input_busca'])
            return len(elementos_ano) > 0 or len(elementos_busca) > 0
        except Exception:
            return False

    def _carregar_todos_resultados(self) -> int:
        """
        Executa scroll infinito para carregar todos os resultados
        """
        print("Iniciando scroll infinito para carregar resultados...")

        scroll_count = 0
        max_scrolls = PORTAL_SAUDE_CONFIG['max_scrolls']
        scrolls_sem_conteudo = 0
        scrolls_sem_conteudo_max = PORTAL_SAUDE_CONFIG['scrolls_sem_conteudo_max']
        tempo_inicio = time.time()
        timeout_scroll = PORTAL_SAUDE_CONFIG['timeout_scroll']

        contagem_inicial = self._contar_resultados()
        print(f"Resultados iniciais: {contagem_inicial}")

        while scroll_count < max_scrolls:
            # Verifica cancelamento
            if self._verificar_cancelamento():
                print("Scroll cancelado pelo usuario")
                break

            # Verifica timeout
            if time.time() - tempo_inicio > timeout_scroll:
                print("Timeout de scroll atingido")
                break

            # Verifica se chegou ao fim da pagina
            if self._esta_no_fim_pagina():
                print("Fim da pagina atingido")
                break

            contagem_atual = self._contar_resultados()

            # Executa scroll
            self.navegador.execute_script("window.scrollBy(0, 500);")
            time.sleep(PORTAL_SAUDE_CONFIG['pausa_entre_scrolls'])

            nova_contagem = self._contar_resultados()

            # Verifica se houve novo conteudo
            if nova_contagem > contagem_atual:
                print(f"  Scroll #{scroll_count + 1}: +{nova_contagem - contagem_atual} itens (total: {nova_contagem})")
                scrolls_sem_conteudo = 0
            else:
                scrolls_sem_conteudo += 1
                if scrolls_sem_conteudo >= scrolls_sem_conteudo_max:
                    print(f"Nenhum conteudo novo por {scrolls_sem_conteudo_max} scrolls - finalizando")
                    break

            scroll_count += 1

            # Log periodico
            if scroll_count % 10 == 0:
                tempo_decorrido = time.time() - tempo_inicio
                print(f"  Progresso: {scroll_count} scrolls, {nova_contagem} itens, {tempo_decorrido:.1f}s")

        contagem_final = self._contar_resultados()
        print(f"Scroll concluido: {contagem_final} itens em {scroll_count} scrolls")
        return contagem_final

    def _contar_resultados(self) -> int:
        """Conta numero atual de resultados na pagina"""
        try:
            links = self.navegador.find_elements(By.CSS_SELECTOR, SELETORES_PORTAL_SAUDE['link_documento'])
            return len(links)
        except Exception:
            return 0

    def _esta_no_fim_pagina(self) -> bool:
        """Verifica se esta no fim da pagina"""
        try:
            altura_pagina = self.navegador.execute_script("return document.body.scrollHeight")
            posicao_atual = self.navegador.execute_script("return window.pageYOffset + window.innerHeight")
            return posicao_atual >= altura_pagina - 200
        except Exception:
            return False

    def _coletar_links_pdf(self) -> List[Dict[str, str]]:
        """
        Coleta todos os links de documentos PDF

        Returns:
            Lista de dicionarios com url, titulo e texto
        """
        try:
            print("Coletando links de documentos...")

            links_elementos = self.navegador.find_elements(By.CSS_SELECTOR, SELETORES_PORTAL_SAUDE['link_documento'])
            pdf_links = []
            urls_vistas = set()

            for link in links_elementos:
                try:
                    href = link.get_attribute("href")
                    texto = link.text.strip()

                    if href and texto and href not in urls_vistas:
                        urls_vistas.add(href)
                        pdf_links.append({
                            'url': href,
                            'titulo': texto,
                            'texto': texto
                        })
                except Exception:
                    continue

            print(f"Coletados {len(pdf_links)} links unicos de documentos")
            return pdf_links

        except Exception as e:
            print(f"Erro ao coletar links: {e}")
            return []

    def _baixar_arquivo(self, url: str, filepath: str, max_tentativas: int = 3) -> bool:
        """
        Baixa arquivo com retry logic

        Args:
            url: URL do arquivo
            filepath: Caminho destino
            max_tentativas: Numero maximo de tentativas

        Returns:
            True se download bem sucedido
        """
        for tentativa in range(1, max_tentativas + 1):
            try:
                if self._verificar_cancelamento():
                    return False

                # Garante URL absoluta
                if not url.startswith('http'):
                    url = urljoin(self.base_url, url)

                response = requests.get(
                    url,
                    stream=True,
                    timeout=30,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                response.raise_for_status()

                # Salva arquivo
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                return True

            except Exception as e:
                if tentativa < max_tentativas:
                    print(f"  Tentativa {tentativa}/{max_tentativas} falhou: {e}")
                    time.sleep(2 * tentativa)  # Backoff exponencial
                else:
                    print(f"  Falha apos {max_tentativas} tentativas: {url}")

        return False

    def _validar_pdf(self, filepath: str) -> bool:
        """
        Valida se arquivo e um PDF valido

        Args:
            filepath: Caminho do arquivo

        Returns:
            True se arquivo e PDF valido
        """
        try:
            if not os.path.exists(filepath):
                return False

            # Verifica tamanho minimo
            tamanho = os.path.getsize(filepath)
            if tamanho < PORTAL_SAUDE_CONFIG['tamanho_minimo_pdf']:
                print(f"  Arquivo muito pequeno: {tamanho} bytes")
                return False

            # Verifica header PDF
            with open(filepath, 'rb') as f:
                header = f.read(5)
                if not header.startswith(b'%PDF-'):
                    print(f"  Arquivo nao e PDF valido")
                    return False

            return True

        except Exception as e:
            print(f"  Erro ao validar PDF: {e}")
            return False

    def _extrair_nome_arquivo(self, url: str, titulo: str) -> str:
        """
        Extrai nome do arquivo da URL ou usa titulo sanitizado

        Args:
            url: URL do arquivo
            titulo: Titulo do documento

        Returns:
            Nome do arquivo sanitizado
        """
        from urllib.parse import urlparse, unquote
        import re

        try:
            # Tenta extrair nome da URL
            parsed = urlparse(url)
            nome_original = os.path.basename(unquote(parsed.path))

            # Se nome valido e termina com .pdf, usa ele
            if nome_original and nome_original.lower().endswith('.pdf'):
                # Sanitiza o nome (remove caracteres invalidos)
                nome_sanitizado = re.sub(r'[<>:"/\\|?*]', '_', nome_original)
                return nome_sanitizado

            # Fallback: usa titulo sanitizado
            titulo_limpo = re.sub(r'[<>:"/\\|?*]', '_', titulo)
            titulo_limpo = titulo_limpo[:100]  # Limita tamanho
            return f"{titulo_limpo}.pdf"

        except Exception:
            # Fallback final: usa titulo simples
            return f"documento_{hash(url) % 10000}.pdf"

    def _baixar_pdfs(
        self,
        links: List[Dict[str, str]],
        ano: str,
        mes: str = None,
        callback_progresso: Callable = None
    ) -> List[Dict[str, str]]:
        """
        Baixa todos os PDFs da lista usando nomes originais

        Args:
            links: Lista de links para baixar
            ano: Ano do filtro
            mes: Mes do filtro
            callback_progresso: Funcao de callback para progresso

        Returns:
            Lista de arquivos baixados com sucesso
        """
        arquivos_baixados = []
        diretorio_saida = self._obter_diretorio_saida(ano, mes)

        # Cria diretorio de saida
        if not os.path.exists(diretorio_saida):
            os.makedirs(diretorio_saida)

        print(f"Iniciando download de {len(links)} PDFs para {diretorio_saida}")

        for ordem, link_info in enumerate(links, 1):
            if self._verificar_cancelamento():
                print("Downloads cancelados pelo usuario")
                break

            try:
                # Usa nome original do arquivo
                nome_arquivo = self._extrair_nome_arquivo(link_info['url'], link_info['titulo'])
                filepath = os.path.join(diretorio_saida, nome_arquivo)

                # Verifica se ja existe
                if os.path.exists(filepath) and self._validar_pdf(filepath):
                    print(f"  [{ordem}/{len(links)}] Ja existe: {nome_arquivo}")
                    arquivos_baixados.append({
                        'caminho': filepath,
                        'url': link_info['url'],
                        'titulo': link_info['titulo']
                    })
                    continue

                print(f"  [{ordem}/{len(links)}] Baixando: {link_info['titulo'][:50]}...")

                # Callback de progresso
                if callback_progresso:
                    callback_progresso("downloading", f"Baixando {ordem}/{len(links)}", ordem, len(links))

                # Baixa arquivo
                if self._baixar_arquivo(link_info['url'], filepath):
                    # Valida PDF
                    if self._validar_pdf(filepath):
                        arquivos_baixados.append({
                            'caminho': filepath,
                            'url': link_info['url'],
                            'titulo': link_info['titulo']
                        })
                        print(f"  [{ordem}/{len(links)}] Sucesso: {nome_arquivo}")
                    else:
                        # Remove arquivo invalido
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        print(f"  [{ordem}/{len(links)}] PDF invalido removido")
                else:
                    print(f"  [{ordem}/{len(links)}] Falha no download")

                time.sleep(PORTAL_SAUDE_CONFIG['pausa_entre_downloads'])

            except Exception as e:
                print(f"  [{ordem}/{len(links)}] Erro: {e}")
                continue

        print(f"Downloads concluidos: {len(arquivos_baixados)}/{len(links)} arquivos")
        return arquivos_baixados

    # def call_pdf2excel_converter

    def _processar_periodo_unico(
        self,
        ano: str,
        mes: str,
        callback_progresso: Callable = None
    ) -> Dict:
        """
        Processa um unico periodo (ano/mes)

        Args:
            ano: Ano para filtrar
            mes: Mes para filtrar (numero ex: "01")
            callback_progresso: Funcao de callback para progresso

        Returns:
            Dicionario com resultado do processamento
        """
        resultado = {
            'sucesso': False,
            'erro': None,
            'arquivos_baixados': [],
            'total_links': 0,
            'total_baixados': 0,
            'diretorio_saida': None
        }

        try:
            print(f"\n--- Processando: {ano}/{mes} ---")

            # 1. Configura navegador
            if callback_progresso:
                callback_progresso("init", f"Configurando navegador para {mes}/{ano}...")

            if self._verificar_cancelamento(resultado):
                return resultado

            if not self.configurar_navegador():
                resultado['erro'] = "Falha ao configurar navegador"
                return resultado

            # 2. Abre pagina com filtros
            if callback_progresso:
                callback_progresso("navigation", f"Abrindo pagina {mes}/{ano}...")

            if self._verificar_cancelamento(resultado):
                return resultado

            if not self.abrir_pagina(ano, mes):
                resultado['erro'] = "Falha ao abrir pagina do portal"
                return resultado

            # 3. Carrega todos os resultados (scroll infinito)
            if callback_progresso:
                callback_progresso("loading", f"Carregando resultados {mes}/{ano}...")

            if self._verificar_cancelamento(resultado):
                return resultado

            total_itens = self._carregar_todos_resultados()

            # 4. Coleta links de PDFs
            if callback_progresso:
                callback_progresso("collecting", f"Coletando links {mes}/{ano}...")

            if self._verificar_cancelamento(resultado):
                return resultado

            links_pdf = self._coletar_links_pdf()
            resultado['total_links'] = len(links_pdf)

            if not links_pdf:
                print(f"  Nenhum documento encontrado para {mes}/{ano}")
                resultado['sucesso'] = True  # Nao e erro, apenas nao ha documentos
                return resultado

            # 5. Baixa PDFs
            if callback_progresso:
                callback_progresso("downloading", f"Baixando {len(links_pdf)} PDFs de {mes}/{ano}...")

            arquivos = self._baixar_pdfs(links_pdf, ano, mes, callback_progresso)
            resultado['arquivos_baixados'] = arquivos
            resultado['total_baixados'] = len(arquivos)
            resultado['diretorio_saida'] = self._obter_diretorio_saida(ano, mes)

            # Sucesso
            if not self._verificar_cancelamento(resultado):
                resultado['sucesso'] = True
                print(f"  Periodo {mes}/{ano} concluido: {len(arquivos)} arquivos")

        except Exception as e:
            resultado['erro'] = f"Erro inesperado: {str(e)}"
            print(f"Erro ao processar {mes}/{ano}: {e}")

        finally:
            # Fecha navegador apos cada periodo
            self.fechar_navegador()

        return resultado

    def processar(
        self,
        ano: str,
        mes: str = None,
        callback_progresso: Callable = None
    ) -> Dict:
        """
        Executa o processamento completo, ciclando por periodos se necessario

        Args:
            ano: Ano para filtrar ou "Todos os Anos"
            mes: Mes para filtrar ou "Todos os Meses" ou None
            callback_progresso: Funcao de callback para progresso

        Returns:
            Dicionario com resultado consolidado do processamento
        """
        resultado_final = {
            'sucesso': False,
            'erro': None,
            'arquivos_baixados': [],
            'total_links': 0,
            'total_baixados': 0,
            'diretorio_saida': self.diretorio_base,
            'periodos_processados': 0,
            'periodos_total': 0
        }

        try:
            self._em_execucao = True
            self._cancelado = False

            print(f"\n{'='*60}")
            print(f"PORTAL SAUDE MG - SCRAPING")
            print(f"Ano: {ano} | Mes: {mes or 'Todos'}")
            print(f"{'='*60}\n")

            # Gera lista de periodos a processar
            periodos = self._gerar_periodos(ano, mes)
            resultado_final['periodos_total'] = len(periodos)

            if not periodos:
                resultado_final['erro'] = "Nenhum periodo para processar"
                return resultado_final

            # Processa cada periodo
            for idx, (ano_periodo, mes_periodo) in enumerate(periodos, 1):
                if self._verificar_cancelamento(resultado_final):
                    print(f"\nProcessamento cancelado no periodo {idx}/{len(periodos)}")
                    break

                if callback_progresso:
                    callback_progresso(
                        "processing",
                        f"Periodo {idx}/{len(periodos)}: {mes_periodo}/{ano_periodo}",
                        idx,
                        len(periodos)
                    )

                # Processa periodo individual
                resultado_periodo = self._processar_periodo_unico(
                    ano_periodo,
                    mes_periodo,
                    callback_progresso
                )

                # Acumula resultados
                resultado_final['total_links'] += resultado_periodo.get('total_links', 0)
                resultado_final['total_baixados'] += resultado_periodo.get('total_baixados', 0)
                resultado_final['arquivos_baixados'].extend(
                    resultado_periodo.get('arquivos_baixados', [])
                )
                resultado_final['periodos_processados'] = idx

                # Log de progresso
                print(f"  Progresso geral: {idx}/{len(periodos)} periodos")

            # Sucesso se pelo menos um periodo foi processado
            if not self._verificar_cancelamento(resultado_final):
                resultado_final['sucesso'] = True
                print(f"\n{'='*60}")
                print(f"PROCESSAMENTO CONCLUIDO!")
                print(f"  Periodos processados: {resultado_final['periodos_processados']}/{len(periodos)}")
                print(f"  Total de links: {resultado_final['total_links']}")
                print(f"  Total de arquivos: {resultado_final['total_baixados']}")
                print(f"  Diretorio base: {resultado_final['diretorio_saida']}")
                print(f"{'='*60}\n")

                # Process PDFs with AI if downloads succeeded
                if resultado_final['total_baixados'] > 0 and resultado_final['arquivos_baixados']:
                    print(f"{'='*60}")
                    print(f"PROCESSAMENTO DE PDFs COM IA")
                    print(f"{'='*60}\n")

                    try:
                        from src.classes.methods.pdf_to_table import PDFToTableConverter

                        # Create converter instance
                        converter = PDFToTableConverter()

                        # Process the specific files from this run
                        excel_result = converter.process_file_list(
                            pdf_files=resultado_final['arquivos_baixados'],
                            output_dir=resultado_final['diretorio_saida']
                        )

                        if excel_result['success']:
                            # Add Excel info to result
                            resultado_final['excel_consolidado'] = excel_result['excel_path']
                            resultado_final['pdfs_processados'] = excel_result['total_processed']
                            resultado_final['pdfs_com_sucesso'] = excel_result['successful']
                            resultado_final['pdfs_com_falha'] = excel_result['failed']

                            print(f"\n[SUCESSO] Excel consolidado gerado:")
                            print(f"  Arquivo: {excel_result['excel_path']}")
                            print(f"  PDFs processados: {excel_result['total_processed']}")
                            print(f"  Sucessos: {excel_result['successful']}")
                            print(f"  Falhas: {excel_result['failed']}")
                        else:
                            print(f"\n[AVISO] Falha ao gerar Excel: {excel_result.get('error')}")

                    except Exception as e:
                        # Don't fail the entire bot run if Excel generation fails
                        print(f"\n[AVISO] Erro ao processar PDFs com IA: {e}")
                        import traceback
                        traceback.print_exc()

        except Exception as e:
            resultado_final['erro'] = f"Erro inesperado: {str(e)}"
            print(f"Erro durante processamento: {e}")

        finally:
            self._em_execucao = False
            # Garante que navegador esta fechado
            self.fechar_navegador()

        return resultado_final

    def fechar_navegador(self):
        """Fecha o navegador e libera recursos"""
        try:
            if self.navegador:
                try:
                    for handle in self.navegador.window_handles:
                        self.navegador.switch_to.window(handle)
                        self.navegador.close()
                except Exception:
                    pass
                self.navegador.quit()
                self.navegador = None
                self.wait = None
                print("Navegador fechado")
        except Exception:
            pass

    def cancelar(self, forcado: bool = False):
        """Cancela execucao em andamento"""
        self._cancelado = True
        self._em_execucao = False
        if forcado:
            self.fechar_navegador()
        super().cancelar(forcado=forcado)
        print("Processamento cancelado")

    def __del__(self):
        """Garante fechamento do navegador ao destruir objeto"""
        self.fechar_navegador()
