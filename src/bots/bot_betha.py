#!/usr/bin/env python3
"""
Bot Betha - Automação do sistema contábil Betha Cloud
Contém toda a lógica de scraping e navegação
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import sys
import os
import time
from typing import Dict, Optional
from datetime import datetime
import unicodedata

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.classes.chrome_driver import ChromeDriverSimples
from src.classes.file.file_converter import FileConverter
from src.classes.methods.cancel_method import BotBase


class BotBetha(BotBase):
    """
    Classe responsável pela automação do sistema Betha Cloud
    """
    
    def __init__(self, cidade_config=None, ano=None):
        """
            cidade_config: Dict com 'nome', 'Login' e 'Senha' da cidade
            ano: Ano para processar (usado para selecionar exercício)
        """
        super().__init__()  # Inicializa BotBase
        self.url = "https://contabil.betha.cloud"
        self.timeout = 30
        
        # Configuração da cidade
        if cidade_config:
            self.nome_cidade = cidade_config.get('nome', '')
            self.usuario = cidade_config.get('Login', '')
            self.senha = cidade_config.get('Senha', '')
        else:
            # Valores padrão para testes
            self.nome_cidade = 'Ribeirão das Neves'
            self.usuario = "breno.ribeirao"
            self.senha = "Brc123456789!"
        
        # Ano de processamento
        self.ano = ano if ano else datetime.now().year
    
    def configurar_navegador(self):
        """
        Configura e inicializa o navegador Chrome
        
        Returns:
            bool: True se configurado com sucesso
        """
        try:
            # Obter o diretório de download temporário para o município
            nome_cidade_normalizado = self._normalizar_nome_cidade(self.nome_cidade)
            file_converter = FileConverter(nome_cidade_normalizado)
            download_dir = file_converter.obter_pasta_temp()
            
            driver_simples = ChromeDriverSimples(download_dir=download_dir)
            self.navegador = driver_simples.conectar()
            
            if self.navegador:
                self.wait = WebDriverWait(self.navegador, self.timeout)
                print("✓ Navegador configurado com sucesso")
                return True
            else:
                print("✗ Falha ao configurar navegador")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao configurar navegador: {e}")
            return False
    
    def navegar_para_pagina(self):
        """
        Navega para a página inicial do Betha
        
        Returns:
            bool: True se navegou com sucesso
        """
        try:
            print(f"Navegando para: {self.url}")
            self.navegador.get(self.url)
            time.sleep(0.3)  # Aguarda carregamento inicial
            print("✓ Página carregada")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao navegar: {e}")
            return False
    
    def fazer_login(self):
        """
        Realiza login no sistema

        Returns:
            bool: True se login realizado com sucesso
        """
        try:
            print("Fazendo login...")

            # Preenche campo de usuário
            print("  - Preenchendo usuário...")
            campo_usuario = self.wait.until(
                EC.presence_of_element_located((By.ID, "login:iUsuarios"))
            )
            campo_usuario.clear()
            campo_usuario.send_keys(self.usuario)

            # Preenche campo de senha
            print("  - Preenchendo senha...")
            campo_senha = self.navegador.find_element(By.ID, "login:senha")
            campo_senha.clear()
            campo_senha.send_keys(self.senha)

            # Clica no botão de login
            print("  - Clicando em Acessar...")
            botao_acessar = self.navegador.find_element(By.XPATH, "//span[@class='text' and text()='Acessar']")
            botao_acessar.click()
            time.sleep(0.8)  # Aguarda login processar

            print("✓ Login realizado com sucesso")
            return True

        except TimeoutException:
            print("✗ Timeout ao tentar fazer login")
            return False
        except Exception as e:
            print(f"✗ Erro ao fazer login: {e}")
            return False

    def fechar_propaganda(self):
        """
        Fecha o popup de propaganda que aparece após o login
        Clica no botão "Não mostrar novamente"

        Returns:
            bool: True se fechou a propaganda, False se não encontrou
        """
        try:
            # Aguarda um pouco para o popup aparecer
            time.sleep(1)

            # Tenta encontrar o botão de fechar propaganda com timeout curto
            print("  - Verificando propaganda...")
            botao_fechar = WebDriverWait(self.navegador, 3).until(
                EC.element_to_be_clickable((By.ID, "btn-banner-close-rankingStn2025"))
            )

            # Clica no botão "Não mostrar novamente"
            botao_fechar.click()
            print("  ✓ Propaganda fechada")
            time.sleep(0.5)  # Aguarda fechar
            return True

        except TimeoutException:
            # Propaganda não apareceu - não é um erro
            print("  - Sem propaganda")
            return False
        except Exception as e:
            # Erro ao tentar fechar, mas não é crítico
            print(f"  - Aviso: não foi possível fechar propaganda: {e}")
            return False
    
    def selecionar_municipio(self):
        """
        Seleciona o município baseado na configuração
        
        Returns:
            bool: True se selecionado com sucesso
        """
        try:
            nome_sem_acentos = self._remover_acentos(self.nome_cidade.upper())
            municipio_texto = f"MUNICIPIO DE {nome_sem_acentos}"
            print(f"Selecionando município: {municipio_texto}...")
            
            # Clica no município
            municipio = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//h3[@class='ng-binding' and text()='{municipio_texto}']"))
            )
            municipio.click()
            time.sleep(0.2)  # Aguarda carregar

            print(f"✓ {municipio_texto} selecionado")

            # Fechar propaganda se aparecer após selecionar município
            self.fechar_propaganda()

            return True
            
        except TimeoutException:
            print(f"✗ Timeout ao selecionar {municipio_texto}")
            return False
        except Exception as e:
            print(f"✗ Erro ao selecionar município: {e}")
            return False
    
    def selecionar_exercicio(self):
        """
        Seleciona o exercício baseado no ano configurado
        
        Returns:
            bool: True se selecionado com sucesso
        """
        try:
            exercicio_texto = f"Exercício {self.ano}"
            print(f"Selecionando {exercicio_texto}...")
            
            # Clica no exercício
            exercicio = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//h3[@class='ng-binding' and text()='{exercicio_texto}']"))
            )
            exercicio.click()
            time.sleep(0.2)  # Aguarda carregar
            
            print(f"✓ {exercicio_texto} selecionado")
            return True
            
        except TimeoutException:
            print(f"✗ Timeout ao selecionar exercício {exercicio_texto}")
            return False
        except Exception as e:
            print(f"✗ Erro ao selecionar exercício: {e}")
            return False
    
    def pressionar_f4(self):
        """
        Pressiona a tecla F4
        
        Returns:
            bool: True se pressionado com sucesso
        """
        try:
            print("Pressionando F4...")
            
            # Envia F4 para o body da página
            body = self.navegador.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.F4)
            time.sleep(0.2)  # Aguarda ação ser processada
            
            print("✓ F4 pressionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao pressionar F4: {e}")
            return False
    
    def navegar_relatorios_favoritos(self):
        """
        Navega para Relatórios Favoritos

        Returns:
            bool: True se navegou com sucesso
        """
        try:
            print("Navegando para Relatórios Favoritos...")

            # Clica em Relatórios Favoritos
            relatorios_favoritos = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@data-ng-click=\"executandoCtrl.alterarVisualizacao('RELATORIOSFAVORITOS')\"]"))
            )
            relatorios_favoritos.click()
            time.sleep(0.2)  # Aguarda carregar

            print("✓ Relatórios Favoritos acessado")
            return True

        except TimeoutException:
            print("✗ Timeout ao navegar para Relatórios Favoritos")
            return False
        except Exception as e:
            print(f"✗ Erro ao navegar para Relatórios Favoritos: {e}")
            return False

    def executar_relatorio_individual(self, nome_relatorio, func_relatorio, args_relatorio):
        """
        Executa um único relatório com navegador novo

        Args:
            nome_relatorio: Nome do relatório para log
            func_relatorio: Função que processa o relatório
            args_relatorio: Argumentos para a função do relatório

        Returns:
            bool: True se executado com sucesso
        """
        try:
            # Verifica cancelamento antes de iniciar
            if self._cancelado:
                print(f"Processamento de {nome_relatorio} cancelado")
                return False
            print("\n" + "="*50)
            print(f"INICIANDO PROCESSAMENTO: {nome_relatorio}")
            print("="*50)

            # 1. Configurar navegador
            if not self.configurar_navegador():
                print(f"✗ Falha ao configurar navegador para {nome_relatorio}")
                return False

            # Verifica cancelamento após configuração
            if self._cancelado:
                self.fechar_navegador()
                return False

            # 2. Navegar para página
            if not self._cancelado and not self.navegar_para_pagina():
                print(f"✗ Falha ao navegar para página para {nome_relatorio}")
                self.fechar_navegador()
                return False

            # 3. Fazer login
            if not self._cancelado and not self.fazer_login():
                print(f"✗ Falha ao fazer login para {nome_relatorio}")
                self.fechar_navegador()
                return False

            # 4. Selecionar município
            if not self._cancelado and not self.selecionar_municipio():
                print(f"✗ Falha ao selecionar município para {nome_relatorio}")
                self.fechar_navegador()
                return False

            # 5. Selecionar exercício
            if not self._cancelado and not self.selecionar_exercicio():
                print(f"✗ Falha ao selecionar exercício para {nome_relatorio}")
                self.fechar_navegador()
                return False

            # 6. Pressionar F4
            if not self._cancelado and not self.pressionar_f4():
                print(f"✗ Falha ao pressionar F4 para {nome_relatorio}")
                self.fechar_navegador()
                return False

            # 7. Navegar para Relatórios Favoritos
            if not self._cancelado and not self.navegar_relatorios_favoritos():
                print(f"✗ Falha ao navegar para Relatórios Favoritos para {nome_relatorio}")
                self.fechar_navegador()
                return False

            # Verifica cancelamento antes de executar relatório
            if self._cancelado:
                self.fechar_navegador()
                return False

            print(f"\n--- Executando {nome_relatorio} ---")

            # 8. Executar o relatório específico
            # Atualizar args com navegador e wait atuais
            args_atualizados = list(args_relatorio)
            args_atualizados[0] = self.navegador  # Substituir navegador
            args_atualizados[1] = self.wait       # Substituir wait

            sucesso = func_relatorio(*args_atualizados)

            if sucesso:
                print(f"✓ {nome_relatorio} processado com sucesso")
            else:
                print(f"✗ Falha ao processar {nome_relatorio}")

            # 9. Fechar navegador
            self.fechar_navegador()

            print("="*50 + "\n")
            return sucesso

        except Exception as e:
            print(f"✗ Erro ao executar {nome_relatorio}: {e}")
            self.fechar_navegador()
            return False

    def executar_completo(self) -> Dict:
        """
        Executa o fluxo completo do bot

        TODAS as cidades usam estratégia de navegadores individuais.
        Vai direto para o script da cidade sem navegação prévia.

        Returns:
            Dict: Resultado da execução com status e mensagens
        """
        resultado = {
            'sucesso': False,
            'mensagem': '',
            'etapas_concluidas': []
        }

        try:
            # Verifica cancelamento antes de iniciar
            if self._cancelado:
                resultado['mensagem'] = "Processamento cancelado"
                return resultado
            print("\n" + "="*60)
            print("INICIANDO BOT BETHA")
            print("="*60 + "\n")

            print(f"✓ Processando: {self.nome_cidade}")
            print("  → Usando estratégia de navegadores individuais")
            print("  → Script da cidade gerenciará toda a navegação\n")

            # Executar script da cidade diretamente (sem navegador prévio)
            # TODAS as cidades agora usam navegadores individuais
            if not self._executar_script_cidade():
                resultado['mensagem'] = f"Falha ao executar script específico da cidade {self.nome_cidade}"
                return resultado

            resultado['etapas_concluidas'].append(f"Script da cidade {self.nome_cidade} executado")

            # Sucesso
            resultado['sucesso'] = True
            resultado['mensagem'] = "Processo concluído com sucesso!"

            print("\n" + "="*60)
            print("PROCESSO CONCLUÍDO")
            print("="*60 + "\n")

            return resultado

        except Exception as e:
            resultado['mensagem'] = f"Erro inesperado: {str(e)}"
            print(f"\n✗ Erro inesperado: {e}")
            return resultado
    
    # Métodos de cancelamento e fechamento herdados de BotBase
    
    def _remover_acentos(self, texto):
        """
        Remove acentos de um texto
        
        Args:
            texto: Texto com acentos
            
        Returns:
            str: Texto sem acentos
        """
        # Normaliza o texto e remove acentos
        texto_normalizado = unicodedata.normalize('NFD', texto)
        texto_sem_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
        return texto_sem_acentos
    
    def _executar_script_cidade(self):
        """
        Executa dinamicamente o script específico para cada cidade
        Procura por arquivo bot_[nome_cidade].py e executa função executar_script_[nome_cidade]

        TODAS as cidades usam navegadores individuais.

        Returns:
            bool: True se executado com sucesso
        """
        try:
            # Verifica cancelamento
            if self._cancelado:
                print("Script da cidade cancelado")
                return False
            print(f"\nExecutando script específico para: {self.nome_cidade}")

            # Converte nome da cidade para nome do módulo usando mapeamento especial
            nome_modulo, nome_funcao = self._obter_nomes_modulo_funcao(self.nome_cidade)

            print(f"Procurando módulo: {nome_modulo}")

            try:
                # Importa dinamicamente o módulo específico da cidade
                modulo_cidade = __import__(f"src.bots.betha.{nome_modulo}", fromlist=[nome_funcao])

                # Obtém a função específica do módulo
                if hasattr(modulo_cidade, nome_funcao):
                    funcao_script = getattr(modulo_cidade, nome_funcao)
                    print(f"✓ Script encontrado: {nome_funcao}")

                    nome_cidade_normalizado = self._normalizar_nome_cidade(self.nome_cidade)

                    # TODAS as cidades usam navegadores individuais
                    # Passar None para navegador e wait - o script criará seus próprios
                    # Passar callback de cancelamento para verificar o estado
                    print("  → Executando com navegadores individuais")
                    try:
                        # Tentar passar o callback de cancelamento
                        return funcao_script(None, None, self.ano, nome_cidade_normalizado,
                                           cancelado_callback=lambda: self._cancelado)
                    except TypeError:
                        # Se o script não aceita o parâmetro cancelado_callback, executar sem ele
                        print("  → Script não suporta cancelamento, executando sem callback")
                        return funcao_script(None, None, self.ano, nome_cidade_normalizado)
                else:
                    print(f"✗ Função {nome_funcao} não encontrada no módulo {nome_modulo}")
                    return False

            except ImportError:
                print(f"✗ Módulo {nome_modulo} não encontrado")
                print(f"✗ Cidade {self.nome_cidade} não possui implementação")
                return False

        except Exception as e:
            print(f"✗ Erro ao executar script da cidade: {e}")
            return False

    def _obter_nomes_modulo_funcao(self, nome_cidade):
        """
        Converte nome da cidade para nome do módulo e função
        Usa mapeamento especial para cidades com nomes complexos

        Args:
            nome_cidade: Nome completo da cidade

        Returns:
            tuple: (nome_modulo, nome_funcao)
        """
        # Mapeamentos especiais para cidades com nomes que não seguem padrão simples
        mapeamentos_especiais = {
            'Ribeirão das Neves': ('bot_ribeirao', 'executar_script_ribeirao'),
            'Congonhas': ('bot_congonhas', 'executar_script_congonhas'),
            # Futuros mapeamentos especiais podem ser adicionados aqui
            # 'São João del Rei': ('bot_sao_joao_del_rei', 'executar_script_sao_joao_del_rei'),
        }

        # Verifica se existe mapeamento especial
        if nome_cidade in mapeamentos_especiais:
            return mapeamentos_especiais[nome_cidade]

        # Usa normalização padrão para outras cidades
        nome_normalizado = self._normalizar_nome_cidade(nome_cidade)
        nome_modulo = f"bot_{nome_normalizado}"
        nome_funcao = f"executar_script_{nome_normalizado}"
        return nome_modulo, nome_funcao

    def _normalizar_nome_cidade(self, nome_cidade):
        """
        Normaliza o nome da cidade para uso em caminhos de arquivo
        Remove acentos, espaços e converte para lowercase com underscores
        
        Args:
            nome_cidade: Nome da cidade original
            
        Returns:
            str: Nome normalizado (ex: "Ribeirão das Neves" -> "ribeirao_neves")
        """
        # Remove acentos
        nome_sem_acentos = self._remover_acentos(nome_cidade)
        # Converte para lowercase e substitui espaços por underscores
        nome_normalizado = nome_sem_acentos.lower().replace(" ", "_")
        return nome_normalizado
    
