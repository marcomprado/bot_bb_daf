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
from src.classes.file_converter import FileConverter


class BotBetha:
    """
    Classe responsável pela automação do sistema Betha Cloud
    
    Funcionalidades:
    - Login automático no sistema
    - Navegação para município e PPA específicos
    - Seleção de exercício
    - Execução de comandos via teclado
    """
    
    def __init__(self, cidade_config=None, ano=None):
        """Inicializa o bot Betha
        
        Args:
            cidade_config: Dict com 'nome', 'Login' e 'Senha' da cidade
            ano: Ano para processar (usado para selecionar PPA e exercício)
        """
        self.url = "https://contabil.betha.cloud/#/entidades/ZGF0YWJhc2U6NjI4LGVudGl0eToxMTI4"
        self.timeout = 30
        self.navegador = None
        self.wait = None
        
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
        
        # Calcula o PPA baseado no ano
        self.ppa_inicio, self.ppa_fim = self._calcular_ppa(self.ano)
    
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
            time.sleep(1)  # Aguarda carregamento inicial
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
            time.sleep(1)  # Pausa para visualização
            
            # Preenche campo de usuário
            print("  - Preenchendo usuário...")
            campo_usuario = self.wait.until(
                EC.presence_of_element_located((By.ID, "login:iUsuarios"))
            )
            campo_usuario.clear()
            campo_usuario.send_keys(self.usuario)
            time.sleep(1)  # Pausa para visualização
            
            # Preenche campo de senha
            print("  - Preenchendo senha...")
            campo_senha = self.navegador.find_element(By.ID, "login:senha")
            campo_senha.clear()
            campo_senha.send_keys(self.senha)
            time.sleep(1)  # Pausa para visualização
            
            # Clica no botão de login
            print("  - Clicando em Acessar...")
            botao_acessar = self.navegador.find_element(By.XPATH, "//span[@class='text' and text()='Acessar']")
            botao_acessar.click()
            time.sleep(3)  # Aguarda login processar
            
            print("✓ Login realizado com sucesso")
            return True
            
        except TimeoutException:
            print("✗ Timeout ao tentar fazer login")
            return False
        except Exception as e:
            print(f"✗ Erro ao fazer login: {e}")
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
            time.sleep(1)  # Pausa para visualização
            
            # Clica no município
            municipio = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//h3[@class='ng-binding' and text()='{municipio_texto}']"))
            )
            municipio.click()
            time.sleep(1)  # Aguarda carregar
            
            print(f"✓ {municipio_texto} selecionado")
            return True
            
        except TimeoutException:
            print(f"✗ Timeout ao selecionar {municipio_texto}")
            return False
        except Exception as e:
            print(f"✗ Erro ao selecionar município: {e}")
            return False
    
    def selecionar_ppa(self):
        """
        Seleciona o PPA baseado no ano configurado
        
        Returns:
            bool: True se selecionado com sucesso
        """
        try:
            ppa_texto = f"PPA {self.ppa_inicio} - {self.ppa_fim}"
            print(f"Selecionando {ppa_texto}...")
            time.sleep(1)  # Pausa para visualização
            
            # Clica no PPA
            ppa = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//h3[@class='ng-binding' and text()='{ppa_texto}']"))
            )
            ppa.click()
            time.sleep(1)  # Aguarda carregar
            
            print(f"✓ {ppa_texto} selecionado")
            return True
            
        except TimeoutException:
            print(f"✗ Timeout ao selecionar PPA {ppa_texto}")
            return False
        except Exception as e:
            print(f"✗ Erro ao selecionar PPA: {e}")
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
            time.sleep(1)  # Pausa para visualização
            
            # Clica no exercício
            exercicio = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//h3[@class='ng-binding' and text()='{exercicio_texto}']"))
            )
            exercicio.click()
            time.sleep(1)  # Aguarda carregar
            
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
            time.sleep(1)  # Pausa para visualização
            
            # Envia F4 para o body da página
            body = self.navegador.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.F4)
            time.sleep(1)  # Aguarda ação ser processada
            
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
            time.sleep(1)  # Pausa para visualização
            
            # Clica em Relatórios Favoritos
            relatorios_favoritos = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@data-ng-click=\"executandoCtrl.alterarVisualizacao('RELATORIOSFAVORITOS')\"]"))
            )
            relatorios_favoritos.click()
            time.sleep(1)  # Aguarda carregar
            
            print("✓ Relatórios Favoritos acessado")
            return True
            
        except TimeoutException:
            print("✗ Timeout ao navegar para Relatórios Favoritos")
            return False
        except Exception as e:
            print(f"✗ Erro ao navegar para Relatórios Favoritos: {e}")
            return False
    
    def executar_completo(self) -> Dict:
        """
        Executa o fluxo completo do bot
        
        Returns:
            Dict: Resultado da execução com status e mensagens
        """
        resultado = {
            'sucesso': False,
            'mensagem': '',
            'etapas_concluidas': []
        }
        
        try:
            print("\n" + "="*60)
            print("INICIANDO BOT BETHA")
            print("="*60 + "\n")
            
            # 1. Configurar navegador
            if not self.configurar_navegador():
                resultado['mensagem'] = "Falha ao configurar navegador"
                return resultado
            resultado['etapas_concluidas'].append("Navegador configurado")
            
            # 2. Navegar para página
            if not self.navegar_para_pagina():
                resultado['mensagem'] = "Falha ao navegar para página"
                return resultado
            resultado['etapas_concluidas'].append("Página carregada")
            
            # 3. Fazer login
            if not self.fazer_login():
                resultado['mensagem'] = "Falha ao fazer login"
                return resultado
            resultado['etapas_concluidas'].append("Login realizado")
            
            # 4. Selecionar município
            if not self.selecionar_municipio():
                resultado['mensagem'] = "Falha ao selecionar município"
                return resultado
            resultado['etapas_concluidas'].append("Município selecionado")
            
            # 5. Selecionar PPA
            if not self.selecionar_ppa():
                resultado['mensagem'] = "Falha ao selecionar PPA"
                return resultado
            resultado['etapas_concluidas'].append("PPA selecionado")
            
            # 6. Selecionar exercício
            if not self.selecionar_exercicio():
                resultado['mensagem'] = "Falha ao selecionar exercício"
                return resultado
            resultado['etapas_concluidas'].append("Exercício selecionado")
            
            # 7. Pressionar F4
            if not self.pressionar_f4():
                resultado['mensagem'] = "Falha ao pressionar F4"
                return resultado
            resultado['etapas_concluidas'].append("F4 pressionado")
            
            # 8. Navegar para Relatórios Favoritos
            if not self.navegar_relatorios_favoritos():
                resultado['mensagem'] = "Falha ao navegar para Relatórios Favoritos"
                return resultado
            resultado['etapas_concluidas'].append("Relatórios Favoritos acessado")
            
            # 9. Script de acordo com a cidade
            if not self._executar_script_cidade():
                resultado['mensagem'] = f"Falha ao executar script específico da cidade {self.nome_cidade}"
                return resultado
            resultado['etapas_concluidas'].append(f"Script da cidade {self.nome_cidade} executado")
            
            # Sucesso
            resultado['sucesso'] = True
            resultado['mensagem'] = "Processo concluído com sucesso! Navegador mantido aberto."
            
            print("\n" + "="*60)
            print("PROCESSO CONCLUÍDO - NAVEGADOR MANTIDO ABERTO")
            print("="*60 + "\n")
            
            return resultado
            
        except Exception as e:
            resultado['mensagem'] = f"Erro inesperado: {str(e)}"
            print(f"\n✗ Erro inesperado: {e}")
            return resultado
    
    def fechar_navegador(self):
        """Fecha o navegador se estiver aberto"""
        try:
            if self.navegador:
                self.navegador.quit()
                self.navegador = None
                print("✓ Navegador fechado")
        except Exception as e:
            print(f"Aviso: Erro ao fechar navegador - {e}")
    
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
    
    def _calcular_ppa(self, ano):
        """
        Calcula o período do PPA baseado no ano
        PPAs são períodos de 4 anos começando em 1998
        
        Args:
            ano: Ano para calcular o PPA
            
        Returns:
            tuple: (ano_inicio, ano_fim) do PPA
        """
        # PPAs começam em 1998 e são de 4 em 4 anos
        # 1998-2001, 2002-2005, 2006-2009, etc.
        anos_desde_1998 = ano - 1998
        periodo_ppa = anos_desde_1998 // 4
        
        ppa_inicio = 1998 + (periodo_ppa * 4)
        ppa_fim = ppa_inicio + 3
        
        print(f"Ano {ano} pertence ao PPA {ppa_inicio}-{ppa_fim}")
        return ppa_inicio, ppa_fim
    
    def _executar_script_cidade(self):
        """
        Executa o script específico para cada cidade
        
        Returns:
            bool: True se executado com sucesso
        """
        try:
            print(f"\nExecutando script específico para: {self.nome_cidade}")
            time.sleep(1)
            
            # Mapeia cidades para suas funções específicas
            scripts_cidades = {
                'Ribeirão das Neves': self._executar_script_ribeirao,
                # Adicionar outras cidades conforme necessário
            }
            
            # Busca função específica da cidade
            funcao_cidade = scripts_cidades.get(self.nome_cidade)
            
            if funcao_cidade:
                return funcao_cidade()
            else:
                print(f"⚠ Script específico não encontrado para {self.nome_cidade}")
                
        except Exception as e:
            print(f"✗ Erro ao executar script da cidade: {e}")
            return False
    
    def _executar_script_ribeirao(self):
        """
        Script específico para Ribeirão das Neves
        Importado do módulo bot_ribeirao
        
        Returns:
            bool: True se executado com sucesso
        """
        try:
            # Importa dinamicamente o módulo específico
            from src.bots.betha.bot_ribeirao import executar_script_ribeirao
            
            print("Executando script de Ribeirão das Neves...")
            nome_cidade_normalizado = self._normalizar_nome_cidade("Ribeirão das Neves")
            return executar_script_ribeirao(self.navegador, self.wait, self.ano, nome_cidade_normalizado)
            
        except ImportError:
            print("✗ Módulo bot_ribeirao não encontrado")
            return False
        except Exception as e:
            print(f"✗ Erro no script de Ribeirão: {e}")
            return False
    
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
    
