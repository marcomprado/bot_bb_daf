#!/usr/bin/env python3
"""
Bot de scraping para o sistema Consulta FNS (Fundo Nacional de Saúde)
Extrai dados de contas bancárias para municípios de Minas Gerais
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
        """
        Inicializa o bot ConsFNS

        Args:
            timeout (int): Tempo limite para aguardar elementos (segundos)
        """
        super().__init__()  # Inicializa BotBase
        self.base_url = CONSFNS_CONFIG['url_base']
        self.timeout = timeout
        self.timeout_carregamento_max = CONSFNS_CONFIG['timeout_carregamento_maximo']
        self.municipios_mg = self._carregar_municipios_mg()

        # Flags de controle para evitar vazamento de memória
        self._cancelado = False
        self._em_execucao = False
        self._campo_esfera_presente = False  # Rastreia se campo esfera apareceu
        self.processador_paralelo = None  # Referência ao processador paralelo para cancelamento

        # Configuração de diretórios
        self.diretorio_consfns = obter_caminho_dados(CONSFNS_CONFIG['diretorio_saida'])
        self.data_hoje = datetime.now().strftime("%Y-%m-%d")
        self.diretorio_saida = os.path.join(self.diretorio_consfns, self.data_hoje)

        # Diretório de download temporário
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
        Configura o navegador Chrome com diretório de download personalizado

        Returns:
            bool: True se configuração bem-sucedida
        """
        try:
            # Configura opções do Chrome para download automático
            chrome_options = webdriver.ChromeOptions()

            # Configurações de download
            prefs = {
                "download.default_directory": self.diretorio_download,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Usa a classe simples para conectar direto ao ChromeDriver
            driver_simples = ChromeDriverSimples(download_dir=self.diretorio_download)
            self.navegador = driver_simples.conectar(chrome_options=chrome_options)

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
        """
        Abre a página Consulta FNS

        Returns:
            bool: True se página carregada com sucesso
        """
        try:
            print(f"Abrindo página Consulta FNS...")
            self.navegador.get(self.base_url)

            # Aguarda formulário carregar - espera pelo dropdown de estado
            select_estado = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELETORES_CONSFNS['select_estado']))
            )

            time.sleep(1.5)  # Pausa mínima para garantir carregamento completo

            print("✓ Página Consulta FNS carregada com sucesso")
            return True

        except TimeoutException:
            print("✗ Timeout: Página demorou para carregar")
            return False
        except Exception as e:
            print(f"✗ Erro ao abrir página Consulta FNS: {e}")
            return False

    def preencher_formulario(self, municipio: str) -> bool:
        """
        Preenche o formulário Consulta FNS com os dados fornecidos

        Args:
            municipio (str): Nome do município

        Returns:
            bool: True se preenchimento bem-sucedido
        """
        try:
            print(f"Preenchendo formulário para {municipio}")

            # 1. Seleciona o estado (MINAS GERAIS)
            print("Selecionando estado MINAS GERAIS...")
            time.sleep(1)
            select_estado = Select(self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['select_estado']))
            select_estado.select_by_visible_text(CONSFNS_CONFIG['uf_padrao'])

            # 2. Aguarda dropdown de municípios carregar e seleciona município
            WebDriverWait(self.navegador, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_CONSFNS['select_municipio']))
            )
            
            time.sleep(1)  # Pausa mínima para garantir carregamento do dropdown

            municipio_encontrado = self._selecionar_municipio(municipio)
            if not municipio_encontrado:
                print(f"✗ Município '{municipio}' não encontrado na lista")
                return False

            # 3. Verifica se campo "esfera" apareceu e seleciona "MUNICIPAL" se necessário
            # (Este campo é condicional e aparece apenas para alguns municípios como Belo Horizonte)
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
        """
        Seleciona município no dropdown

        Args:
            nome_municipio (str): Nome do município a ser selecionado

        Returns:
            bool: True se município foi encontrado e selecionado
        """
        try:
            select_municipio = Select(self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['select_municipio']))

            # Normaliza o nome para comparação
            nome_procurado = nome_municipio.upper().strip()

            # Primeiro tenta busca exata
            for opcao in select_municipio.options:
                texto_opcao = opcao.text.upper().strip()
                if nome_procurado == texto_opcao:
                    select_municipio.select_by_visible_text(opcao.text)
                    print(f"✓ Município selecionado: {opcao.text}")
                    return True

            # Se não encontrou exato, tenta busca por contém
            for opcao in select_municipio.options:
                texto_opcao = opcao.text.upper().strip()
                if nome_procurado in texto_opcao:
                    select_municipio.select_by_visible_text(opcao.text)
                    print(f"✓ Município selecionado: {opcao.text}")
                    return True

            return False

        except Exception as e:
            print(f"✗ Erro ao selecionar município: {e}")
            return False

    def _verificar_e_selecionar_esfera(self) -> bool:
        """
        Verifica se o campo "esfera" aparece e seleciona "MUNICIPAL"
        (Campo condicional que aparece para alguns municípios como Belo Horizonte)

        Returns:
            bool: True se campo foi encontrado e selecionado, False se não existe
        """
        try:
            # Tenta localizar o campo esfera com timeout curto (1 segundo) - OTIMIZADO
            # Não é erro se não existir - alguns municípios não têm esse campo
            WebDriverWait(self.navegador, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELETORES_CONSFNS['select_esfera']))
            )

            # Se chegou aqui, o campo existe - vamos selecionar MUNICIPAL
            print("Campo 'esfera' detectado - selecionando MUNICIPAL...")
            select_esfera = Select(self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['select_esfera']))
            select_esfera.select_by_value("MUNICIPAL")

            # Pausa mínima para garantir seleção
            if CONSFNS_CONFIG['pausa_apos_selecao_esfera'] > 0:
                time.sleep(CONSFNS_CONFIG['pausa_apos_selecao_esfera'])

            # Marca que campo esfera foi encontrado (para espera condicional posterior)
            self._campo_esfera_presente = True
            print("✓ Esfera selecionada: MUNICIPAL")
            return True

        except TimeoutException:
            # Campo não existe - isso é normal para a maioria dos municípios
            # Não loga nada para não poluir o console
            return False
        except Exception as e:
            # Erro inesperado ao tentar selecionar
            print(f"Aviso: Erro ao verificar campo esfera: {e}")
            return False

    def executar_consulta(self) -> bool:
        """
        Clica no botão Consultar e aguarda resultado

        Returns:
            bool: True se consulta executada com sucesso
        """
        try:
            print("Executando consulta...")

            # Clica no botão Consultar
            botao_consultar = self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['botao_consultar'])
            botao_consultar.click()

            print(MENSAGENS['consfns_aguardando'])

            # Aguarda o botão "Gerar Planilha" ficar disponível (sem sleep fixo - OTIMIZADO)
            # WebDriverWait já espera inteligentemente até 120s conforme necessário
            WebDriverWait(self.navegador, self.timeout_carregamento_max).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_CONSFNS['botao_gerar_planilha']))
            )

            # Se campo "esfera" apareceu, aguarda 30s adicional para garantir carregamento completo
            if self._campo_esfera_presente:
                print("⏳ Campo 'esfera' detectado - aguardando 30s para garantir carregamento completo...")
                time.sleep(30)
                print("✓ Aguardo concluído")

            print("✓ Consulta executada e resultados carregados")
            return True

        except TimeoutException:
            print("✗ Timeout: Resultados demoraram para carregar (máximo 120s)")
            return False
        except Exception as e:
            print(f"✗ Erro ao executar consulta: {e}")
            return False

    def gerar_planilha(self, municipio: str) -> Optional[str]:
        """
        Clica no botão Gerar Planilha e aguarda download

        Args:
            municipio (str): Nome do município (para renomear arquivo)

        Returns:
            Optional[str]: Caminho do arquivo salvo ou None se erro
        """
        try:
            print(MENSAGENS['consfns_download'])

            # Limpa diretório de download antes de baixar
            arquivos_antes = set(os.listdir(self.diretorio_download))

            # Clica no botão Gerar Planilha
            botao_gerar = self.navegador.find_element(By.CSS_SELECTOR, SELETORES_CONSFNS['botao_gerar_planilha'])
            botao_gerar.click()

            # Pausa mínima antes de verificar download (OTIMIZADO)
            if CONSFNS_CONFIG['pausa_antes_download'] > 0:
                time.sleep(CONSFNS_CONFIG['pausa_antes_download'])

            # Aguarda arquivo ser baixado (máximo 30 segundos)
            arquivo_baixado = self._aguardar_download(arquivos_antes, timeout=30)

            if arquivo_baixado:
                # Renomeia e move arquivo para diretório final
                arquivo_final = self._renomear_arquivo(arquivo_baixado, municipio)
                print(f"✓ Planilha gerada: {arquivo_final}")
                return arquivo_final
            else:
                print("✗ Arquivo não foi baixado")
                return None

        except Exception as e:
            print(f"✗ Erro ao gerar planilha: {e}")
            return None

    def _aguardar_download(self, arquivos_antes: set, timeout: int = 30) -> Optional[str]:
        """
        Aguarda um novo arquivo ser baixado no diretório

        Args:
            arquivos_antes (set): Conjunto de arquivos antes do download
            timeout (int): Tempo máximo de espera em segundos

        Returns:
            Optional[str]: Caminho do arquivo baixado ou None
        """
        tempo_inicio = time.time()

        while time.time() - tempo_inicio < timeout:
            # Verifica se foi cancelado
            if self._cancelado:
                return None

            arquivos_agora = set(os.listdir(self.diretorio_download))
            novos_arquivos = arquivos_agora - arquivos_antes

            # Filtra arquivos temporários do Chrome (.crdownload, .tmp)
            arquivos_completos = [f for f in novos_arquivos if not f.endswith(('.crdownload', '.tmp'))]

            if arquivos_completos:
                # Retorna o caminho completo do primeiro arquivo encontrado
                arquivo = arquivos_completos[0]
                return os.path.join(self.diretorio_download, arquivo)

            # Polling interval otimizado (0.2s em vez de 0.5s) - detecta download mais rápido
            time.sleep(0.2)

        return None

    def _renomear_arquivo(self, arquivo_original: str, municipio: str) -> str:
        """
        Renomeia arquivo baixado com nome do município

        Args:
            arquivo_original (str): Caminho do arquivo original
            municipio (str): Nome do município

        Returns:
            str: Caminho do arquivo renomeado
        """
        try:
            # Remove caracteres especiais do nome do município
            nome_municipio_limpo = municipio.replace(" ", "_").replace("/", "_").upper()

            # Pega a extensão do arquivo original
            _, extensao = os.path.splitext(arquivo_original)
            if not extensao:
                extensao = '.xlsx'  # Assume Excel se não tiver extensão

            # Cria novo nome: apenas o nome da cidade
            novo_nome = f"{nome_municipio_limpo}{extensao}"
            caminho_final = os.path.join(self.diretorio_saida, novo_nome)

            # Move e renomeia arquivo
            import shutil
            shutil.move(arquivo_original, caminho_final)

            return caminho_final

        except Exception as e:
            print(f"Aviso: Erro ao renomear arquivo - {e}")
            # Se falhar, retorna o caminho original
            return arquivo_original

    def processar_municipio(self, municipio: str) -> Dict[str, any]:
        """
        Processa um município específico

        Args:
            municipio (str): Nome do município

        Returns:
            Dict: Resultado do processamento
        """
        resultado = {
            'municipio': municipio,
            'sucesso': False,
            'erro': None,
            'arquivo': None
        }

        try:
            # Verifica se foi cancelado antes de começar
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado pelo usuário"
                return resultado

            # Reseta flag de esfera para novo município
            self._campo_esfera_presente = False
            self._em_execucao = True
            print(f"\n=== Processando: {municipio} ===")

            # 1. Abre página ConsFNS
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
                return resultado
            if not self.abrir_pagina_consfns():
                resultado['erro'] = "Falha ao abrir página ConsFNS"
                return resultado

            # 2. Preenche formulário
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
                return resultado
            if not self.preencher_formulario(municipio):
                resultado['erro'] = "Falha ao preencher formulário"
                return resultado

            # 3. Executa consulta
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
                return resultado
            if not self.executar_consulta():
                resultado['erro'] = "Falha ao executar consulta"
                return resultado

            # 4. Gera planilha
            if self._cancelado:
                resultado['erro'] = "Processamento cancelado"
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

        return resultado

    def processar_todos_municipios(self) -> Dict[str, any]:
        """
        Processa todos os municípios de MG

        Returns:
            Dict: Estatísticas do processamento
        """
        print(f"\n{MENSAGENS['inicio_consfns']}")
        print(f"{MENSAGENS['consfns_todos_municipios']}")
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

                resultado = self.processar_municipio(municipio)

                if resultado['sucesso']:
                    estatisticas['sucessos'] += 1
                    estatisticas['municipios_processados'].append(municipio)
                else:
                    estatisticas['erros'] += 1
                    estatisticas['municipios_erro'].append({
                        'municipio': municipio,
                        'erro': resultado['erro']
                    })
                    
        except Exception as e:
            print(f"Erro durante processamento em lote: {e}")
        finally:
            self.limpar_recursos()

        # Calcula taxa de sucesso
        if estatisticas['total'] > 0:
            estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100
        else:
            estatisticas['taxa_sucesso'] = 0

        # Gera relatório TXT com estatísticas
        try:
            arquivo_relatorio = self._gerar_relatorio(estatisticas)
            if arquivo_relatorio:
                print(f"📄 Relatório gerado: {arquivo_relatorio}")
        except Exception as e:
            print(f"Aviso: Erro ao gerar relatório - {e}")

        print(f"\n=== PROCESSAMENTO CONCLUÍDO ===")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")

        return estatisticas

    def _gerar_relatorio(self, estatisticas: Dict) -> str:
        """
        Gera relatório TXT com estatísticas do processamento

        Args:
            estatisticas: Dict com estatísticas do processamento

        Returns:
            str: Caminho do arquivo de relatório gerado
        """
        try:
            from datetime import datetime

            # Nome do arquivo de relatório
            nome_arquivo = f"RELATORIO_CONSFNS_{self.data_hoje}.txt"
            caminho_relatorio = os.path.join(self.diretorio_saida, nome_arquivo)

            # Data e hora atual para o relatório
            data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Constrói o conteúdo do relatório
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

            # Se houver erros, lista os municípios com erro
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

            # Escreve o arquivo
            with open(caminho_relatorio, 'w', encoding='utf-8') as arquivo:
                arquivo.write('\n'.join(linhas))

            print(f"📄 Relatório gerado: {caminho_relatorio}")
            return caminho_relatorio

        except Exception as e:
            print(f"Aviso: Erro ao gerar relatório - {e}")
            return None

    def processar_lote_municipios(self, municipios: List[str]) -> Dict[str, any]:
        """
        Processa um lote específico de municípios (para uso paralelo)

        Args:
            municipios (List[str]): Lista de municípios para processar

        Returns:
            Dict: Estatísticas do processamento do lote
        """
        print(f"\n=== PROCESSANDO LOTE DE {len(municipios)} MUNICÍPIOS - CONSFNS ===")

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

                resultado = self.processar_municipio(municipio)

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
                    time.sleep(CONSFNS_CONFIG['pausa_entre_municipios'])

        except Exception as e:
            print(f"Erro durante processamento do lote: {e}")
            return {'sucesso': False, 'erro': str(e)}

        # Calcula taxa de sucesso
        estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100 if estatisticas['total'] > 0 else 0

        print(f"\n=== LOTE CONCLUÍDO ===")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")

        return {'sucesso': True, 'estatisticas': estatisticas}

    def executar_paralelo(self, num_instancias: int = 2) -> Dict[str, any]:
        """
        Executa processamento paralelo de municípios usando ProcessadorParalelo

        Args:
            num_instancias (int): Número de instâncias paralelas (máximo 5)

        Returns:
            Dict: Resultados consolidados do processamento paralelo com referência ao processador
        """
        try:
            from src.classes.methods.parallel_processor import ProcessadorParalelo

            print(f"\n=== INICIANDO PROCESSAMENTO PARALELO CONSFNS ===")
            print(f"Instâncias: {num_instancias}")

            # Armazena referência do processador para cancelamento
            self.processador_paralelo = ProcessadorParalelo()
            resultado = self.processador_paralelo.executar_paralelo_consfns(self, num_instancias)

            # Adiciona referência do processador ao resultado
            resultado['processador'] = self.processador_paralelo

            if resultado['sucesso']:
                stats = resultado['estatisticas']
                print(f"\n=== PROCESSAMENTO PARALELO CONCLUÍDO ===")
                print(f"Total: {stats['total']} municípios")
                print(f"Sucessos: {stats['sucessos']}")
                print(f"Erros: {stats['erros']}")
                print(f"Taxa de sucesso: {stats['taxa_sucesso']:.1f}%")

                # Gera relatório TXT com estatísticas
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

    # Método cancelar() sobrescrito para gerenciar _em_execucao
    def cancelar(self, forcado=False):
        """Cancela execução e limpa recursos"""
        self._em_execucao = False

        # Se tiver processador paralelo ativo e for forçado, cancela ele também
        if forcado and hasattr(self, 'processador_paralelo') and self.processador_paralelo:
            print("Cancelando processador paralelo ConsFNS...")
            self.processador_paralelo.cancelar()
            self.processador_paralelo = None

        # Chama método da classe pai
        super().cancelar(forcado=forcado)

    def cancelar_forcado(self):
        """Mantido para compatibilidade - usar cancelar(forcado=True)"""
        self.cancelar(forcado=True)

    def obter_lista_municipios(self) -> List[str]:
        """
        Retorna lista de municípios carregados

        Returns:
            List[str]: Lista de municípios de MG
        """
        return self.municipios_mg.copy()
