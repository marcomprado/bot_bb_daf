"""
Bot BB DAF - Automação completa do sistema de arrecadação federal do Banco do Brasil
Contém toda a lógica de scraping, processamento e coordenação
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import sys
import os
import time
import subprocess
import threading
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import concurrent.futures

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.classes.chrome_driver import ChromeDriverSimples
from src.classes.data_extractor import DataExtractor
from src.classes.date_calculator import DateCalculator
from src.classes.file.file_manager import FileManager
from src.classes.city_splitter import CitySplitter
from src.classes.config import SISTEMA_CONFIG, SELETORES_CSS, ARQUIVOS_CONFIG
from src.classes.methods.cancel_method import BotBase


class BotBBDAF(BotBase):
    """
    Classe principal responsável pela automação web do sistema de arrecadação federal
    
    Funcionalidades:
    - Configuração e inicialização do navegador Chrome
    - Navegação e interação com elementos da página
    - Preenchimento automático de formulários
    - Processamento de múltiplas cidades
    - Tratamento de erros e recuperação automática
    """
    
    def __init__(self, url=None, timeout=None):
        """
        Inicializa o bot de web scraping
        
        Args:
            url (str): URL do sistema a ser acessado (padrão: config.py)
            timeout (int): Tempo limite para espera de elementos (padrão: config.py)
        """
        super().__init__()  # Inicializa BotBase
        self.url = url or SISTEMA_CONFIG['url_sistema']
        self.timeout = timeout or SISTEMA_CONFIG['timeout_selenium']
        self.data_extractor = None  # Extrator de dados (opcional)
    
    def configurar_extrator_dados(self, data_extractor):
        """
        Configura o extrator de dados para processamento automático
        
        Args:
            data_extractor: Instância da classe DataExtractor
        """
        self.data_extractor = data_extractor
    
    def configurar_navegador(self):
        """
        Configura e inicializa o navegador Chrome usando conexão direta simples

        Returns:
            bool: True se a configuração foi bem-sucedida, False caso contrário
        """
        try:
            # Configura Chrome em modo headless (execução em background)
            opcoes = webdriver.ChromeOptions()
            opcoes.add_argument("--headless=new")
            opcoes.add_argument("--disable-gpu")
            opcoes.add_argument("--window-size=1920,1080")

            # Usa a classe simples para conectar direto ao ChromeDriver
            driver_simples = ChromeDriverSimples()
            self.navegador = driver_simples.conectar(chrome_options=opcoes)

            if self.navegador:
                # Configura o WebDriverWait para aguardar elementos aparecerem
                self.wait = WebDriverWait(self.navegador, self.timeout)
                return True
            else:
                return False

        except Exception:
            return False
    
    def abrir_pagina_inicial(self):
        """
        Abre a página inicial do sistema e aguarda carregar
        
        Returns:
            bool: True se a página foi carregada com sucesso, False caso contrário
        """
        try:
            self.navegador.get(self.url)
            
            # Aguarda o campo de nome do beneficiário aparecer para confirmar que a página carregou
            campo_beneficiario = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELETORES_CSS['campo_beneficiario']))
            )
            
            return True
            
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def preencher_nome_cidade(self, cidade):
        """
        Preenche o campo "Nome do Beneficiário" com o nome da cidade
        
        Args:
            cidade (str): Nome da cidade a ser inserida
        
        Returns:
            bool: True se o preenchimento foi bem-sucedido, False caso contrário
        """
        try:
            # Localiza o campo usando o seletor configurado
            campo_beneficiario = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELETORES_CSS['campo_beneficiario']))
            )
            
            # Limpa o campo e digita o nome da cidade
            campo_beneficiario.clear()
            campo_beneficiario.send_keys(cidade)
            
            # Aguarda um momento para o sistema processar a entrada
            time.sleep(SISTEMA_CONFIG['pausa_apos_preenchimento'])
            
            return True
            
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def selecionar_cidade_mg(self, cidade):
        """
        Clica no botão seletor e escolhe especificamente a cidade do estado MG
        
        Args:
            cidade (str): Nome da cidade para buscar com estado MG
        
        Returns:
            bool: True se a seleção foi bem-sucedida, False caso contrário
        """
        try:
            # Aguarda e clica no botão seletor de beneficiário
            botao_seletor = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_CSS['botao_seletor_beneficiario']))
            )
            
            botao_seletor.click()
            
            # Aguarda o dropdown aparecer
            time.sleep(SISTEMA_CONFIG['pausa_entre_campos'])
            
            # Procura por todas as opções que contêm "MG" no title
            opcoes_mg = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELETORES_CSS['opcao_cidade_mg']))
            )
            
            # Procura pela cidade específica do MG
            cidade_encontrada = False
            for opcao in opcoes_mg:
                title_opcao = opcao.get_attribute('title')
                if title_opcao and cidade.upper() in title_opcao.upper():
                    
                    # Clica na opção da cidade MG
                    opcao.click()
                    cidade_encontrada = True
                    
                    # Aguarda a seleção ser processada
                    time.sleep(SISTEMA_CONFIG['pausa_apos_preenchimento'])
                    break
            
            return cidade_encontrada
            
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def clicar_botao_continuar(self):
        """
        Clica no botão "Continuar" para avançar para a próxima etapa
        
        Returns:
            bool: True se o clique foi bem-sucedido, False caso contrário
        """
        try:
            # Localiza o primeiro botão usando o seletor configurado
            botao_continuar = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_CSS['botao_continuar_inicial']))
            )
            
            # Clica no botão Continuar para avançar para a próxima etapa
            botao_continuar.click()
            
            # Aguarda a página de seleção de datas carregar completamente
            time.sleep(SISTEMA_CONFIG['pausa_apos_clique'])
            return True
            
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def preencher_datas(self, data_inicial, data_final):
        """
        Preenche os campos de data inicial e final
        
        Args:
            data_inicial (str): Data inicial no formato DD/MM/AAAA
            data_final (str): Data final no formato DD/MM/AAAA
        
        Returns:
            bool: True se o preenchimento foi bem-sucedido, False caso contrário
        """
        try:
            # Procura pelos campos de data usando o seletor configurado
            # Este seletor é mais estável que os IDs únicos que podem mudar
            campos_data = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELETORES_CSS['campos_data']))
            )
            
            # Verifica se encontrou pelo menos 2 campos de data (inicial e final)
            if len(campos_data) >= 2:
                # Preenche o primeiro campo: Data inicial
                campo_data_inicial = campos_data[0]
                campo_data_inicial.clear()  # Limpa qualquer valor pré-existente
                campo_data_inicial.send_keys(data_inicial)  # Insere data no formato DD/MM/AAAA
                
                # Pequena pausa entre os preenchimentos para evitar conflitos
                time.sleep(SISTEMA_CONFIG['pausa_entre_campos'])
                
                # Preenche o segundo campo: Data final
                campo_data_final = campos_data[1]
                campo_data_final.clear()  # Limpa qualquer valor pré-existente
                campo_data_final.send_keys(data_final)  # Insere data no formato DD/MM/AAAA
                
                # Aguarda um momento para o sistema processar e validar as datas inseridas
                time.sleep(SISTEMA_CONFIG['pausa_apos_preenchimento'])
                return True
                
            else:
                return False
                
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def clicar_segundo_botao_continuar(self):
        """
        Clica no segundo botão "Continuar" após preencher as datas para ir para a próxima página
        Pressiona ESC antes do clique para fechar qualquer calendário que possa estar bloqueando
        
        Returns:
            bool: True se o clique foi bem-sucedido, False caso contrário
        """
        try:
            # Pressiona ESC para fechar qualquer calendário aberto antes de clicar no botão
            self.navegador.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(SISTEMA_CONFIG['pausa_esc_calendario'])
            
            # Localiza e clica no segundo botão "Continuar"
            botao_continuar_datas = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELETORES_CSS['botao_continuar_datas']))
            )
            
            botao_continuar_datas.click()
            
            # Aguarda a próxima página carregar completamente
            time.sleep(SISTEMA_CONFIG['pausa_apos_clique'])
            return True
            
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def voltar_pagina_inicial(self):
        """
        Volta para a página inicial para processar a próxima cidade
        
        Returns:
            bool: True se conseguiu voltar com sucesso, False caso contrário
        """
        try:
            self.navegador.get(self.url)
            
            # Aguarda a página carregar novamente
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELETORES_CSS['campo_beneficiario']))
            )
            return True
            
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def processar_cidade(self, cidade, data_inicial, data_final):
        """
        Processa uma cidade completa: nome → continuar → selecionar MG → datas → continuar
        
        Args:
            cidade (str): Nome da cidade
            data_inicial (str): Data inicial no formato DD/MM/AAAA
            data_final (str): Data final no formato DD/MM/AAAA
        
        Returns:
            bool: True se o processamento foi bem-sucedido, False caso contrário
        """
        try:
            # PASSO 1: Preenche o campo "Nome do Beneficiário" com o nome da cidade
            if not self.preencher_nome_cidade(cidade):
                return False
            
            # PASSO 2: Clica no primeiro botão "Continuar" para ir para a página de seleção
            if not self.clicar_botao_continuar():
                return False
            
            # PASSO 3: Seleciona especificamente a cidade do estado MG
            if not self.selecionar_cidade_mg(cidade):
                return False
            
            # PASSO 4: Preenche os campos de data inicial e final
            if not self.preencher_datas(data_inicial, data_final):
                return False
            
            # PASSO 5: Clica no segundo botão "Continuar" para ir para a página de resultados
            if not self.clicar_segundo_botao_continuar():
                return False
            
            # PASSO 6: Extrai dados da página de resultados (se extrator estiver configurado)
            if hasattr(self, 'data_extractor') and self.data_extractor:
                resultado_extracao = self.data_extractor.processar_pagina_resultados(self.navegador, cidade)
                if resultado_extracao.get('sucesso'):
                    print(f"{cidade.title()}: {resultado_extracao.get('registros_encontrados', 0)} registros")
            
            return True
            
        except Exception:
            return False
    
    def processar_lista_cidades(self, cidades, data_inicial, data_final):
        """
        Processa uma lista completa de cidades automaticamente
        
        Args:
            cidades (list): Lista de nomes de cidades
            data_inicial (str): Data inicial no formato DD/MM/AAAA
            data_final (str): Data final no formato DD/MM/AAAA
        
        Returns:
            dict: Estatísticas do processamento (sucessos, erros, total)
        """
        total_cidades = len(cidades)
        sucessos = 0
        erros = 0
        
        for i, cidade in enumerate(cidades, 1):
            print(f"Processando {i}/{total_cidades}: {cidade.title()}")
            
            # Processa a cidade atual
            sucesso = self.processar_cidade(cidade, data_inicial, data_final)
            
            if sucesso:
                sucessos += 1
            else:
                erros += 1
                print(f"Falha: {cidade.title()}")
            
            # Volta para a página inicial para a próxima cidade (exceto na última)
            if i < total_cidades:
                if not self.voltar_pagina_inicial():
                    print("Erro crítico: Impossível continuar")
                    break
                
                # Pausa entre as cidades
                time.sleep(SISTEMA_CONFIG['pausa_entre_cidades'])
        

        
        # Retorna estatísticas do processamento
        estatisticas = {
            'total': total_cidades,
            'sucessos': sucessos,
            'erros': erros,
            'taxa_sucesso': (sucessos / total_cidades) * 100 if total_cidades > 0 else 0
        }
        
        print(f"\nConcluído: {sucessos}/{total_cidades} sucessos ({estatisticas['taxa_sucesso']:.1f}%)")
        
        return estatisticas
    
    def aguardar_usuario(self):
        """
        Mantém o navegador aberto até que o usuário pressione Enter
        """
        print("\nVerifique os resultados na janela do navegador.")
        input("Pressione Enter para fechar o navegador...")
    
    # Métodos de cancelamento e fechamento herdados de BotBase

    # Métodos de cancelamento e fechamento herdados de BotBase

    def cancelar_forcado(self):
        """Mantido para compatibilidade - usar cancelar(forcado=True)"""
        self.cancelar(forcado=True)
    
    def executar_completo(self, cidades: List[str] = None, data_inicial: str = None, 
                         data_final: str = None, arquivo_cidades: str = None):
        """
        Executa o processamento completo com todos os passos
        
        Args:
            cidades: Lista de cidades ou None para carregar do arquivo
            data_inicial: Data inicial ou None para calcular automaticamente
            data_final: Data final ou None para calcular automaticamente
            arquivo_cidades: Arquivo de cidades customizado
        
        Returns:
            dict: Estatísticas do processamento
        """
        try:
            # 1. Carrega cidades se não fornecidas
            if cidades is None:
                file_manager = FileManager(arquivo_cidades or ARQUIVOS_CONFIG['arquivo_cidades'])
                if not file_manager.verificar_arquivo_existe():
                    print("Arquivo de cidades não encontrado.")
                    return {'sucesso': False, 'erro': 'Arquivo de cidades não encontrado'}
                
                cidades = file_manager.carregar_cidades()
                if not file_manager.validar_lista_cidades(cidades):
                    return {'sucesso': False, 'erro': 'Lista de cidades inválida'}
            
            # 2. Calcula datas se não fornecidas
            if data_inicial is None or data_final is None:
                date_calculator = DateCalculator()
                data_inicial, data_final = date_calculator.obter_datas_formatadas()
            
            print(f"Período: {data_inicial} até {data_final}")
            print(f"Total de cidades: {len(cidades)}")
            
            # 3. Configura navegador
            if not self.configurar_navegador():
                return {'sucesso': False, 'erro': 'Falha ao configurar navegador'}
            
            # 4. Abre página inicial
            if not self.abrir_pagina_inicial():
                self.fechar_navegador()
                return {'sucesso': False, 'erro': 'Falha ao abrir página inicial'}
            
            # 5. Processa cidades
            estatisticas = self.processar_lista_cidades(cidades, data_inicial, data_final)
            
            # 6. Fecha navegador
            self.fechar_navegador()
            
            return {
                'sucesso': True,
                'estatisticas': estatisticas
            }
            
        except Exception as e:
            if self.navegador:
                self.fechar_navegador()
            return {'sucesso': False, 'erro': str(e)}
    
    def executar_paralelo(self, num_instancias: int, data_inicial: str = None, 
                         data_final: str = None):
        """
        Executa processamento paralelo com múltiplas instâncias
        
        Args:
            num_instancias: Número de instâncias paralelas
            data_inicial: Data inicial ou None para calcular automaticamente
            data_final: Data final ou None para calcular automaticamente
        
        Returns:
            dict: Resultados consolidados de todas as instâncias
        """
        try:
            # 1. Prepara divisão de cidades
            city_splitter = CitySplitter()
            resultado_divisao = city_splitter.dividir_cidades(num_instancias)
            
            if not resultado_divisao.get('sucesso'):
                return {'sucesso': False, 'erro': resultado_divisao.get('erro')}
            
            # 2. Calcula datas se necessário
            if data_inicial is None or data_final is None:
                date_calculator = DateCalculator()
                data_inicial, data_final = date_calculator.obter_datas_formatadas()
            
            arquivos_criados = resultado_divisao['arquivos_criados']
            resultados = []
            
            # 3. Executa instâncias em paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_instancias) as executor:
                futures = []
                
                for arquivo_info in arquivos_criados:
                    # Cria nova instância do bot para cada thread
                    bot = BotBBDAF()
                    bot.configurar_extrator_dados(DataExtractor("bbdaf"))
                    
                    # Submete para execução
                    future = executor.submit(
                        bot.executar_completo,
                        arquivo_cidades=arquivo_info['arquivo'],
                        data_inicial=data_inicial,
                        data_final=data_final
                    )
                    futures.append((future, arquivo_info))
                
                # Coleta resultados
                for future, arquivo_info in futures:
                    resultado = future.result()
                    resultado['instancia'] = arquivo_info['instancia']
                    resultados.append(resultado)
                    
                    # Remove arquivo temporário
                    try:
                        os.remove(arquivo_info['arquivo'])
                    except:
                        pass
            
            # 4. Consolida estatísticas
            total_sucessos = sum(r['estatisticas']['sucessos'] for r in resultados if r.get('sucesso'))
            total_erros = sum(r['estatisticas']['erros'] for r in resultados if r.get('sucesso'))
            total_cidades = sum(r['estatisticas']['total'] for r in resultados if r.get('sucesso'))
            
            return {
                'sucesso': True,
                'resultados_instancias': resultados,
                'estatisticas_consolidadas': {
                    'total': total_cidades,
                    'sucessos': total_sucessos,
                    'erros': total_erros,
                    'taxa_sucesso': (total_sucessos / total_cidades * 100) if total_cidades > 0 else 0
                }
            }
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)} 