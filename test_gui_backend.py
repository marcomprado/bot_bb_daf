#!/usr/bin/env python3
"""
Testador completo para diagnosticar problemas GUI/Backend
Identifica incompatibilidades Windows e problemas de configuração
"""

import sys
import os
import subprocess
from datetime import datetime

# Adiciona o diretório atual ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestadorGUIBackend:
    """Testador completo para GUI e Backend"""
    
    def __init__(self):
        self.resultados = []
        self.plataforma = sys.platform
        self.diretorio_trabalho = os.getcwd()
        
    def log(self, mensagem, tipo="INFO"):
        """Log formatado com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        cores = {
            "INFO": "\033[36m",      # Ciano
            "SUCESSO": "\033[32m",   # Verde
            "ERRO": "\033[31m",      # Vermelho
            "AVISO": "\033[33m",     # Amarelo
            "CAMINHO": "\033[35m",   # Magenta
            "RESET": "\033[0m"       # Reset
        }
        
        cor = cores.get(tipo, cores["INFO"])
        reset = cores["RESET"]
        
        if tipo == "CAMINHO":
            icone = "📁"
        elif tipo == "SUCESSO":
            icone = "✅"
        elif tipo == "ERRO":
            icone = "❌"
        elif tipo == "AVISO":
            icone = "⚠️"
        else:
            icone = "ℹ️"
        
        print(f"{cor}[{timestamp}] {icone} {mensagem}{reset}")
    
    def separador(self, titulo):
        """Separador visual"""
        linha = "=" * 70
        self.log(f"\n{linha}", "INFO")
        self.log(f"🔍 {titulo}", "INFO")
        self.log(linha, "INFO")
    
    def teste_1_imports_gui(self):
        """Teste 1: Verificação de imports da GUI"""
        self.separador("TESTE 1: IMPORTS DA GUI")
        
        try:
            # Testa CustomTkinter
            import customtkinter as ctk
            self.log(f"CustomTkinter importado: v{ctk.__version__}", "SUCESSO")
            
            # Testa Tkinter padrão
            import tkinter as tk
            self.log(f"Tkinter padrão importado: v{tk.TkVersion}", "SUCESSO")
            
            # Testa messagebox
            from tkinter import messagebox
            self.log("tkinter.messagebox importado", "SUCESSO")
            
            # Testa threading
            import threading
            self.log("threading importado", "SUCESSO")
            
            return True
            
        except ImportError as e:
            self.log(f"Erro de importação GUI: {e}", "ERRO")
            self.log("Solução: pip install customtkinter", "AVISO")
            return False
        except Exception as e:
            self.log(f"Erro inesperado GUI: {e}", "ERRO")
            return False
    
    def teste_2_imports_backend(self):
        """Teste 2: Verificação de imports do backend"""
        self.separador("TESTE 2: IMPORTS DO BACKEND")
        
        try:
            # Testa imports das classes
            from classes import AutomationCore, WebScrapingBot, DataExtractor, DateCalculator, FileManager
            self.log("Classes principais importadas", "SUCESSO")
            
            # Testa Selenium
            from selenium import webdriver
            self.log("Selenium WebDriver importado", "SUCESSO")
            
            # Testa outras dependências
            import pandas as pd
            self.log(f"Pandas importado: v{pd.__version__}", "SUCESSO")
            
            from bs4 import BeautifulSoup
            self.log("BeautifulSoup importado", "SUCESSO")
            
            import openpyxl
            self.log(f"OpenPyXL importado: v{openpyxl.__version__}", "SUCESSO")
            
            return True
            
        except ImportError as e:
            self.log(f"Erro de importação backend: {e}", "ERRO")
            self.log("Solução: pip install -r requirements.txt", "AVISO")
            return False
        except Exception as e:
            self.log(f"Erro inesperado backend: {e}", "ERRO")
            return False
    
    def teste_3_arquivos_necessarios(self):
        """Teste 3: Verificação de arquivos necessários"""
        self.separador("TESTE 3: ARQUIVOS NECESSÁRIOS")
        
        arquivos_obrigatorios = [
            'gui_main.py',
            'main.py', 
            'config.py',
            'cidades.txt',
            'classes/__init__.py',
            'classes/automation_core.py'
        ]
        
        todos_existem = True
        
        self.log(f"Diretório de trabalho: {self.diretorio_trabalho}", "CAMINHO")
        
        for arquivo in arquivos_obrigatorios:
            caminho_completo = os.path.join(self.diretorio_trabalho, arquivo)
            
            if os.path.exists(arquivo):
                self.log(f"✓ {arquivo}", "SUCESSO")
                self.log(f"  📁 Localizado em: {caminho_completo}", "CAMINHO")
            else:
                self.log(f"✗ {arquivo} - NÃO ENCONTRADO", "ERRO")
                self.log(f"  📁 Esperado em: {caminho_completo}", "CAMINHO")
                todos_existem = False
        
        # Verifica arquivo dinâmico
        arquivo_dinamico = 'listed_cities.txt'
        caminho_dinamico = os.path.join(self.diretorio_trabalho, arquivo_dinamico)
        
        if os.path.exists(arquivo_dinamico):
            self.log(f"✓ {arquivo_dinamico} (dinâmico)", "SUCESSO")
            self.log(f"  📁 Localizado em: {caminho_dinamico}", "CAMINHO")
        else:
            self.log(f"ℹ {arquivo_dinamico} - Será criado pela GUI", "AVISO")
            self.log(f"  📁 Será criado em: {caminho_dinamico}", "CAMINHO")
        
        return todos_existem
    
    def teste_4_inicializacao_backend(self):
        """Teste 4: Inicialização do backend"""
        self.separador("TESTE 4: INICIALIZAÇÃO DO BACKEND")
        
        try:
            from classes.automation_core import AutomationCore
            
            # Testa inicialização
            core = AutomationCore()
            self.log("AutomationCore inicializado", "SUCESSO")
            
            # Testa inicialização de componentes
            resultado = core.inicializar_componentes()
            
            if resultado.get('sucesso'):
                self.log("Componentes inicializados com sucesso", "SUCESSO")
                
                # Verifica componentes individuais
                if hasattr(core, 'file_manager') and core.file_manager:
                    self.log("✓ FileManager carregado", "SUCESSO")
                if hasattr(core, 'date_calculator') and core.date_calculator:
                    self.log("✓ DateCalculator carregado", "SUCESSO")
                if hasattr(core, 'data_extractor') and core.data_extractor:
                    self.log("✓ DataExtractor carregado", "SUCESSO")
                    
                    # Mostra onde o DataExtractor salvará arquivos
                    diretorio_saida = getattr(core.data_extractor, 'diretorio_saida', 'Não definido')
                    self.log(f"  📁 Arquivos serão salvos em: {diretorio_saida}", "CAMINHO")
                    
                if hasattr(core, 'bot') and core.bot:
                    self.log("✓ WebScrapingBot carregado", "SUCESSO")
                
                return True
            else:
                erro = resultado.get('erro', 'Erro desconhecido')
                self.log(f"Falha na inicialização: {erro}", "ERRO")
                return False
                
        except Exception as e:
            self.log(f"Erro na inicialização: {e}", "ERRO")
            return False
    
    def teste_5_calculo_datas(self):
        """Teste 5: Cálculo de datas"""
        self.separador("TESTE 5: CÁLCULO DE DATAS")
        
        try:
            from classes.date_calculator import DateCalculator
            
            calc = DateCalculator()
            data_inicial, data_final = calc.obter_datas_formatadas()
            
            self.log(f"Data inicial calculada: {data_inicial}", "SUCESSO")
            self.log(f"Data final calculada: {data_final}", "SUCESSO")
            
            # Valida formato
            import re
            padrao_data = r'\d{2}/\d{2}/\d{4}'
            
            if re.match(padrao_data, data_inicial) and re.match(padrao_data, data_final):
                self.log("Formato de datas válido (DD/MM/AAAA)", "SUCESSO")
                return True
            else:
                self.log("Formato de datas inválido", "ERRO")
                return False
                
        except Exception as e:
            self.log(f"Erro no cálculo de datas: {e}", "ERRO")
            return False
    
    def teste_6_carregamento_cidades(self):
        """Teste 6: Carregamento de cidades"""
        self.separador("TESTE 6: CARREGAMENTO DE CIDADES")
        
        try:
            from classes.file_manager import FileManager
            
            # Testa arquivo estático
            fm_estatico = FileManager("cidades.txt")
            caminho_estatico = os.path.join(self.diretorio_trabalho, "cidades.txt")
            
            self.log(f"Testando arquivo estático: cidades.txt", "INFO")
            self.log(f"📁 Caminho: {caminho_estatico}", "CAMINHO")
            
            if fm_estatico.verificar_arquivo_existe():
                cidades_estatico = fm_estatico.carregar_cidades()
                self.log(f"✓ Arquivo estático: {len(cidades_estatico)} cidades", "SUCESSO")
            else:
                self.log("✗ Arquivo estático não encontrado", "ERRO")
                return False
            
            # Testa arquivo dinâmico
            fm_dinamico = FileManager("listed_cities.txt") 
            caminho_dinamico = os.path.join(self.diretorio_trabalho, "listed_cities.txt")
            
            self.log(f"Testando arquivo dinâmico: listed_cities.txt", "INFO")
            self.log(f"📁 Caminho: {caminho_dinamico}", "CAMINHO")
            
            if fm_dinamico.verificar_arquivo_existe():
                cidades_dinamico = fm_dinamico.carregar_cidades()
                self.log(f"✓ Arquivo dinâmico: {len(cidades_dinamico)} cidades", "SUCESSO")
            else:
                self.log("ℹ Arquivo dinâmico não existe (será criado pela GUI)", "AVISO")
            
            return True
            
        except Exception as e:
            self.log(f"Erro no carregamento: {e}", "ERRO")
            return False
    
    def teste_7_execucao_python(self):
        """Teste 7: Comando Python para subprocess"""
        self.separador("TESTE 7: EXECUÇÃO PYTHON")
        
        comandos_teste = [
            ["python", "--version"],
            ["python3", "--version"], 
            [sys.executable, "--version"]
        ]
        
        self.log(f"Executável Python atual: {sys.executable}", "CAMINHO")
        self.log(f"Plataforma: {self.plataforma}", "INFO")
        
        comando_funcionou = None
        
        for comando in comandos_teste:
            try:
                self.log(f"Testando: {' '.join(comando)}", "INFO")
                
                resultado = subprocess.run(
                    comando, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                if resultado.returncode == 0:
                    versao = resultado.stdout.strip()
                    self.log(f"✓ Sucesso: {versao}", "SUCESSO")
                    comando_funcionou = comando[0]
                else:
                    self.log(f"✗ Falhou (código {resultado.returncode})", "ERRO")
                    if resultado.stderr:
                        self.log(f"  Erro: {resultado.stderr.strip()}", "ERRO")
                        
            except subprocess.TimeoutExpired:
                self.log(f"✗ Timeout: {comando[0]}", "ERRO")
            except FileNotFoundError:
                self.log(f"✗ Comando não encontrado: {comando[0]}", "ERRO")
            except Exception as e:
                self.log(f"✗ Erro: {e}", "ERRO")
        
        if comando_funcionou:
            self.log(f"Comando recomendado: {comando_funcionou}", "SUCESSO")
            
            if comando_funcionou == "python" and self.plataforma.startswith("win"):
                self.log("⚠️ POSSÍVEL PROBLEMA WINDOWS:", "AVISO")
                self.log("   Use sys.executable em vez de 'python'", "AVISO")
                
            return True
        else:
            self.log("❌ NENHUM COMANDO PYTHON FUNCIONOU", "ERRO")
            return False
    
    def teste_8_simulacao_subprocess(self):
        """Teste 8: Simulação de subprocess da GUI"""
        self.separador("TESTE 8: SIMULAÇÃO SUBPROCESS GUI")
        
        # Localiza main.py
        caminho_main = os.path.join(self.diretorio_trabalho, "main.py")
        self.log(f"Arquivo main.py: {caminho_main}", "CAMINHO")
        
        if not os.path.exists(caminho_main):
            self.log("❌ main.py não encontrado", "ERRO")
            return False
        
        # Testa diferentes abordagens de subprocess
        abordagens = [
            {
                'nome': 'Abordagem atual GUI',
                'comando': ["python", "main.py"]
            },
            {
                'nome': 'Abordagem recomendada',
                'comando': [sys.executable, "main.py"] 
            },
            {
                'nome': 'Caminho absoluto main.py',
                'comando': [sys.executable, caminho_main]
            }
        ]
        
        pelo_menos_uma_funcionou = False
        
        for abordagem in abordagens:
            self.log(f"Testando: {abordagem['nome']}", "INFO")
            self.log(f"Comando: {' '.join(abordagem['comando'])}", "CAMINHO")
            
            try:
                # Simula apenas o início do processo (não executa completamente)
                proc = subprocess.Popen(
                    abordagem['comando'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.diretorio_trabalho
                )
                
                # Aguarda um pouco e termina
                import time
                time.sleep(2)
                
                # Verifica se o processo ainda está rodando
                if proc.poll() is None:
                    self.log("✓ Processo iniciou corretamente", "SUCESSO")
                    proc.terminate()  # Termina processo
                    proc.wait()
                    pelo_menos_uma_funcionou = True
                else:
                    # Processo já terminou - pode ser erro
                    stdout, stderr = proc.communicate()
                    if proc.returncode == 0:
                        self.log("✓ Processo executou e terminou normalmente", "SUCESSO")
                        pelo_menos_uma_funcionou = True
                    else:
                        self.log(f"✗ Processo falhou (código {proc.returncode})", "ERRO")
                        if stderr:
                            self.log(f"  Erro: {stderr[:200]}", "ERRO")
                
            except FileNotFoundError as e:
                self.log(f"✗ Arquivo não encontrado: {e}", "ERRO")
            except Exception as e:
                self.log(f"✗ Erro inesperado: {e}", "ERRO")
        
        if pelo_menos_uma_funcionou:
            self.log("✅ Pelo menos uma abordagem funcionou", "SUCESSO")
        else:
            self.log("❌ NENHUMA ABORDAGEM FUNCIONOU", "ERRO")
            self.log("Possível problema no sistema ou dependências", "AVISO")
        
        return pelo_menos_uma_funcionou
    
    def teste_9_compatibilidade_windows(self):
        """Teste 9: Verificações específicas do Windows"""
        self.separador("TESTE 9: COMPATIBILIDADE WINDOWS")
        
        if not self.plataforma.startswith("win"):
            self.log("Sistema não é Windows - Teste ignorado", "INFO")
            return True
        
        self.log("Sistema Windows detectado", "INFO")
        
        # Verifica uso de sys.executable
        try:
            # Lê o arquivo gui_main.py para verificar o subprocess
            caminho_gui = os.path.join(self.diretorio_trabalho, "gui_main.py")
            self.log(f"Verificando arquivo GUI: {caminho_gui}", "CAMINHO")
            
            if os.path.exists(caminho_gui):
                with open(caminho_gui, 'r', encoding='utf-8') as f:
                    conteudo_gui = f.read()
                
                # Procura por subprocess calls
                linhas = conteudo_gui.split('\n')
                problemas_encontrados = []
                
                for i, linha in enumerate(linhas, 1):
                    if 'subprocess' in linha and 'python' in linha and 'sys.executable' not in linha:
                        if '["python"' in linha or "['python'" in linha:
                            problemas_encontrados.append((i, linha.strip()))
                
                if problemas_encontrados:
                    self.log("⚠️ PROBLEMAS WINDOWS ENCONTRADOS:", "AVISO")
                    for num_linha, linha in problemas_encontrados:
                        self.log(f"  Linha {num_linha}: {linha}", "ERRO")
                    
                    self.log("SOLUÇÃO:", "AVISO")
                    self.log("  Substitua ['python', 'main.py'] por", "AVISO") 
                    self.log("  [sys.executable, 'main.py']", "AVISO")
                    
                    return False
                else:
                    self.log("✓ Código parece compatível com Windows", "SUCESSO")
                    return True
            else:
                self.log("❌ gui_main.py não encontrado", "ERRO")
                return False
                
        except Exception as e:
            self.log(f"Erro na verificação Windows: {e}", "ERRO")
            return False
    
    def teste_10_integracao_completa(self):
        """Teste 10: Teste de integração end-to-end"""
        self.separador("TESTE 10: INTEGRAÇÃO COMPLETA")
        
        try:
            # Importa GUI principal
            caminho_gui = os.path.join(self.diretorio_trabalho, "gui_main.py")
            self.log(f"Importando GUI de: {caminho_gui}", "CAMINHO")
            
            # Adiciona ao sys.path se necessário
            dir_gui = os.path.dirname(caminho_gui)
            if dir_gui not in sys.path:
                sys.path.insert(0, dir_gui)
            
            # Importa sem executar
            spec = importlib.util.spec_from_file_location("gui_main", caminho_gui)
            gui_module = importlib.util.module_from_spec(spec)
            
            # EXECUTA o módulo para carregar as classes
            spec.loader.exec_module(gui_module)
            
            self.log("✓ Módulo GUI carregado", "SUCESSO")
            
            # Verifica classes principais
            if hasattr(gui_module, 'GUIMain'):
                self.log("✓ Classe GUIMain encontrada", "SUCESSO")
            else:
                self.log("✗ Classe GUIMain não encontrada", "ERRO")
                # Lista todas as classes disponíveis para debug
                classes_encontradas = [nome for nome in dir(gui_module) if nome[0].isupper()]
                self.log(f"Classes encontradas: {classes_encontradas}", "INFO")
                return False
            
            # Testa criação da classe (sem executar GUI)
            try:
                # Mock do CustomTkinter para evitar abrir janela
                import customtkinter as ctk
                ctk.set_appearance_mode("dark")
                
                self.log("✓ Configuração inicial da GUI OK", "SUCESSO")
                
            except Exception as e:
                self.log(f"Problema na configuração GUI: {e}", "AVISO")
            
            # Verifica integração com backend
            from classes.automation_core import AutomationCore
            core = AutomationCore()
            
            if core.inicializar_componentes()['sucesso']:
                self.log("✓ Integração GUI-Backend OK", "SUCESSO")
                return True
            else:
                self.log("✗ Problema na integração", "ERRO")
                return False
                
        except Exception as e:
            self.log(f"Erro na integração: {e}", "ERRO")
            return False
    
    def executar_todos_testes(self):
        """Executa todos os testes em sequência"""
        print("\n" + "="*70)
        print("🔬 TESTADOR GUI/BACKEND - DIAGNÓSTICO COMPLETO")
        print("="*70)
        
        self.log(f"Python: {sys.version}", "INFO")
        self.log(f"Plataforma: {sys.platform}", "INFO")
        self.log(f"Diretório: {self.diretorio_trabalho}", "CAMINHO")
        
        testes = [
            ("Imports GUI", self.teste_1_imports_gui),
            ("Imports Backend", self.teste_2_imports_backend), 
            ("Arquivos Necessários", self.teste_3_arquivos_necessarios),
            ("Inicialização Backend", self.teste_4_inicializacao_backend),
            ("Cálculo de Datas", self.teste_5_calculo_datas),
            ("Carregamento Cidades", self.teste_6_carregamento_cidades),
            ("Execução Python", self.teste_7_execucao_python),
            ("Subprocess GUI", self.teste_8_simulacao_subprocess),
            ("Compatibilidade Windows", self.teste_9_compatibilidade_windows),
            ("Integração Completa", self.teste_10_integracao_completa)
        ]
        
        sucessos = 0
        falhas = 0
        
        for nome_teste, funcao_teste in testes:
            try:
                if funcao_teste():
                    self.resultados.append((nome_teste, "SUCESSO"))
                    sucessos += 1
                else:
                    self.resultados.append((nome_teste, "FALHA"))
                    falhas += 1
            except Exception as e:
                self.log(f"Erro inesperado no teste {nome_teste}: {e}", "ERRO")
                self.resultados.append((nome_teste, "ERRO"))
                falhas += 1
        
        self._gerar_relatorio_final(sucessos, falhas)
        
        return sucessos, falhas
    
    def _gerar_relatorio_final(self, sucessos, falhas):
        """Gera relatório final consolidado"""
        self.separador("RELATÓRIO FINAL")
        
        total = sucessos + falhas
        taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
        
        self.log(f"Total de testes: {total}", "INFO")
        self.log(f"Sucessos: {sucessos}", "SUCESSO")
        self.log(f"Falhas: {falhas}", "ERRO")
        self.log(f"Taxa de sucesso: {taxa_sucesso:.1f}%", "INFO")
        
        print("\n📋 DETALHES DOS TESTES:")
        for nome, resultado in self.resultados:
            if resultado == "SUCESSO":
                self.log(f"✅ {nome}", "SUCESSO")
            else:
                self.log(f"❌ {nome}", "ERRO")
        
        # Diagnóstico e recomendações
        print("\n🎯 DIAGNÓSTICO:")
        
        if falhas == 0:
            self.log("🎉 SISTEMA PERFEITO! Tudo funcionando.", "SUCESSO")
        elif taxa_sucesso >= 80:
            self.log("⚠️ Sistema quase OK. Pequenos ajustes necessários.", "AVISO")
        elif taxa_sucesso >= 60:
            self.log("🔧 Sistema com problemas. Correções necessárias.", "AVISO")
        else:
            self.log("🆘 Sistema com problemas graves. Revisão completa necessária.", "ERRO")
        
        # Adiciona informações sobre caminhos
        self.log("📁 INFORMAÇÕES DE CAMINHOS:", "CAMINHO")
        self.log(f"  Diretório de trabalho: {self.diretorio_trabalho}", "CAMINHO")
        self.log(f"  Python executável: {sys.executable}", "CAMINHO")
        
        arquivos_importantes = ['gui_main.py', 'main.py', 'cidades.txt', 'listed_cities.txt']
        for arquivo in arquivos_importantes:
            caminho = os.path.join(self.diretorio_trabalho, arquivo)
            existe = "✓" if os.path.exists(arquivo) else "✗"
            self.log(f"  {existe} {arquivo}: {caminho}", "CAMINHO")

# Adiciona import necessário
import importlib.util

def main():
    """Função principal"""
    testador = TestadorGUIBackend()
    sucessos, falhas = testador.executar_todos_testes()
    
    return 0 if falhas == 0 else 1

if __name__ == "__main__":
    exit(main()) 