#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Congonhas - Script especifico para o municipio de Congonhas
Contem a logica especifica apos navegar para Relatorios Favoritos

- Baseado em @bot_ribeirao.py
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.classes.file.file_converter import FileConverter
from src.bots.bot_betha import BotBetha
import json

#   Classe para funções auxiliares
class RelatorioProcessamento:
    """
    Classe para gerar relatório detalhado do processamento em arquivo TXT
    """

    def __init__(self, nome_cidade="congonhas", ano=None):
        """
        Inicializa o relatório de processamento

        Args:
            nome_cidade: Nome da cidade sendo processada
            ano: Ano do processamento
        """
        self.nome_cidade = nome_cidade.upper().replace("_", " ")
        self.ano = ano
        self.eventos = []
        self.inicio = datetime.now()
        self.fim = None
        self.arquivos_baixados = 0
        self.arquivos_convertidos = 0
        self.erros = []
        self.avisos = []

    def adicionar_evento(self, mensagem, tipo="INFO"):
        """
        Adiciona um evento ao relatório

        Args:
            mensagem: Mensagem do evento
            tipo: Tipo do evento (INFO, ERRO, AVISO, SUCESSO)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.eventos.append({
            "timestamp": timestamp,
            "tipo": tipo,
            "mensagem": mensagem
        })

        if tipo == "ERRO":
            self.erros.append(mensagem)
        elif tipo == "AVISO":
            self.avisos.append(mensagem)

    def definir_arquivos_baixados(self, quantidade):
        """Define a quantidade de arquivos baixados"""
        self.arquivos_baixados = quantidade

    def definir_arquivos_convertidos(self, quantidade):
        """Define a quantidade de arquivos convertidos"""
        self.arquivos_convertidos = quantidade

    def finalizar(self):
        """Marca o fim do processamento"""
        self.fim = datetime.now()

    def calcular_tempo_total(self):
        """Calcula o tempo total de processamento"""
        if self.fim:
            delta = self.fim - self.inicio
            minutos = delta.seconds // 60
            segundos = delta.seconds % 60
            return f"{minutos}min {segundos}seg"
        return "Em andamento"

    def gerar_relatorio(self):
        """
        Gera o conteúdo do relatório em formato texto

        Returns:
            str: Conteúdo do relatório formatado
        """
        linhas = []
        linhas.append("="*60)
        linhas.append(f"RELATÓRIO DE PROCESSAMENTO - {self.nome_cidade}")
        linhas.append("="*60)
        linhas.append(f"Data/Hora Início: {self.inicio.strftime('%d/%m/%Y %H:%M:%S')}")

        if self.ano:
            linhas.append(f"Ano Processado: {self.ano}")

        linhas.append("")
        linhas.append("EVENTOS DO PROCESSO:")
        linhas.append("-"*40)

        for evento in self.eventos:
            prefixo = ""
            if evento["tipo"] == "ERRO":
                prefixo = "✗ "
            elif evento["tipo"] == "AVISO":
                prefixo = "⚠ "
            elif evento["tipo"] == "SUCESSO":
                prefixo = "✓ "

            linhas.append(f"[{evento['timestamp']}] {prefixo}{evento['mensagem']}")

        linhas.append("")
        linhas.append("RESUMO:")
        linhas.append("-"*40)
        linhas.append(f"Total de arquivos baixados: {self.arquivos_baixados}")
        linhas.append(f"Total de arquivos convertidos: {self.arquivos_convertidos}")
        linhas.append(f"Erros encontrados: {len(self.erros)}")
        linhas.append(f"Avisos registrados: {len(self.avisos)}")
        linhas.append(f"Tempo total: {self.calcular_tempo_total()}")

        if self.erros:
            linhas.append("")
            linhas.append("ERROS DETALHADOS:")
            linhas.append("-"*40)
            for i, erro in enumerate(self.erros, 1):
                linhas.append(f"{i}. {erro}")

        if self.avisos:
            linhas.append("")
            linhas.append("AVISOS DETALHADOS:")
            linhas.append("-"*40)
            for i, aviso in enumerate(self.avisos, 1):
                linhas.append(f"{i}. {aviso}")

        linhas.append("")
        if self.fim:
            linhas.append(f"Data/Hora Fim: {self.fim.strftime('%d/%m/%Y %H:%M:%S')}")
            status = "SUCESSO" if self.arquivos_convertidos >= 10 else "PARCIAL"
            if len(self.erros) > 0:
                status = "COM ERROS"
            linhas.append(f"Status Final: {status}")
        else:
            linhas.append("Status: EM ANDAMENTO")

        linhas.append("="*60)

        return "\n".join(linhas)

    def salvar_relatorio(self, diretorio_destino):
        """
        Salva o relatório em arquivo TXT

        Args:
            diretorio_destino: Diretório onde salvar o relatório

        Returns:
            str: Caminho do arquivo salvo
        """
        try:
            # Gera nome único para o arquivo
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nome_arquivo = f"relatorio_processamento_{timestamp}.txt"
            caminho_completo = os.path.join(diretorio_destino, nome_arquivo)

            # Salva o relatório
            conteudo = self.gerar_relatorio()
            with open(caminho_completo, 'w', encoding='utf-8') as f:
                f.write(conteudo)

            print(f"\n✓ Relatório salvo em: {nome_arquivo}")
            return caminho_completo

        except Exception as e:
            print(f"\n✗ Erro ao salvar relatório: {e}")
            return None
        
#.  Execução principal do script Ribeirão das Neves

def executar_script_congonhas(navegador, wait, ano=None, nome_cidade="congonhas", cancelado_callback=None):
    """
    Executa o script especifico para Congonhas

    Este script e executado apos chegar em "Relatorios Favoritos"
    e contem a logica especifica para este municipio

    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar os relatorios
        nome_cidade: Nome da cidade para organização de pastas
        cancelado_callback: Função que retorna True se a execução foi cancelada

    Returns:
        bool: True se executado com sucesso
    """
    try:
        print("\n" + "="*60)
        print("SCRIPT CONGONHAS")
        print("="*60)

        # Obter configuração da cidade
        cidade_config = None
        try:
            # Buscar configuração do arquivo JSON com acesso direto O(1)
            json_path = os.path.join(os.path.dirname(__file__), 'city_betha.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                cidades_obj = config_data.get('cidades', {})

                # Normaliza o nome da cidade para usar como chave
                cidade_key = nome_cidade.lower().replace(' ', '_')

                # Busca direta por chave (novo formato dict - O(1))
                if isinstance(cidades_obj, dict):
                    cidade_config = cidades_obj.get(cidade_key)
                else:
                    # Fallback: formato antigo array - busca linear
                    for cidade in cidades_obj:
                        if cidade['nome'].lower().replace(' ', '_') == cidade_key:
                            cidade_config = cidade
                            break
        except Exception as e:
            print(f"⚠ Aviso: Não foi possível carregar configuração da cidade: {e}")

        # Inicializar conversor de arquivos
        file_converter = FileConverter(nome_cidade)
        print(f"\n✓ Sistema de arquivos inicializado para {nome_cidade}")


        # Lista de relatórios para processar
        relatorios = [
            {"nome": "Anexo 03", "func": _processar_anexo_03, "args": (None, None)},
            {"nome": "Anexo 08", "func": _processar_anexo_08, "args": (None, None)},
            {"nome": "Anexo IV", "func": _processar_anexo_iv, "args": (None, None, ano)},
            {"nome": "Anexo VII", "func": _processar_anexo_vii, "args": (None, None, ano)},
            {"nome": "Balancete da Despesa", "func": _processar_balancete_despesa, "args": (None, None, ano)},
            {"nome": "Balancete da Receita", "func": _processar_balancete_receita, "args": (None, None, ano)},
            {"nome": "Extrato da Receita", "func": _processar_extrato_receita, "args": (None, None, ano)},
            {"nome": "Relação de Empenhos - CMM", "func": _processar_relacao_empenhos, "args": (None, None, ano)},
            {"nome": "Relação de Pagamentos Efetuados", "func": _processar_relacao_pagamentos, "args": (None, None, ano)},
            {"nome": "Relação geral de liquidações por período", "func": _processar_relacao_liquidacoes, "args": (None, None, ano)}
        ]

        # Lista para rastrear relatórios processados com sucesso
        relatorios_processados = []
        relatorios_falhados = []

        # Processar cada relatório com navegador novo
        for i, relatorio in enumerate(relatorios):
            # Verificar se foi cancelado
            if cancelado_callback and cancelado_callback():
                print("\n⚠ Processamento cancelado pelo usuário")
                relatorios_falhados.append(relatorio['nome'] + " (cancelado)")
                break

            print(f"\n[{i+1}/{len(relatorios)}] Iniciando navegador novo para: {relatorio['nome']}")

            # Criar nova instância do bot para cada relatório
            bot_temp = BotBetha(cidade_config, ano)

            # Se temos um callback de cancelamento, verificar antes de executar
            if cancelado_callback and cancelado_callback():
                print(f"⚠ Cancelado antes de executar {relatorio['nome']}")
                bot_temp.fechar_navegador()
                relatorios_falhados.append(relatorio['nome'] + " (cancelado)")
                break

            # Executar relatório individual com navegador próprio
            sucesso = bot_temp.executar_relatorio_individual(
                nome_relatorio=relatorio['nome'],
                func_relatorio=relatorio['func'],
                args_relatorio=relatorio['args']
            )

            if sucesso:
                relatorios_processados.append(relatorio['nome'])
                print(f"✓ [{i+1}/{len(relatorios)}] {relatorio['nome']} concluído com sucesso")
            else:
                relatorios_falhados.append(relatorio['nome'])
                print(f"✗ [{i+1}/{len(relatorios)}] {relatorio['nome']} falhou")

            # Navegador já foi fechado automaticamente pelo executar_relatorio_individual
            print(f"Navegador fechado. Relatórios processados: {len(relatorios_processados)}/{len(relatorios)}")

            # Baixar arquivos após o 5º relatório (índice 4)
            if i == 4 and len(relatorios_processados) > 0:
                print("\n" + "="*60)
                print("DOWNLOAD APÓS 5º RELATÓRIO")
                print("="*60)
                bot_download = BotBetha(cidade_config, ano)
                if bot_download.configurar_navegador():
                    if (bot_download.navegar_para_pagina() and
                        bot_download.fazer_login() and
                        bot_download.selecionar_municipio() and
                        bot_download.selecionar_exercicio() and
                        bot_download.pressionar_f4() and
                        bot_download.navegar_relatorios_favoritos()):
                        baixar_ultimos_5_arquivos(bot_download.navegador, bot_download.wait, file_converter, 600)
                    bot_download.fechar_navegador()

            # Baixar arquivos após o 10º relatório (índice 9)
            if i == 9 and len(relatorios_processados) > 0:
                print("\n" + "="*60)
                print("DOWNLOAD APÓS 10º RELATÓRIO")
                print("="*60)
                bot_download = BotBetha(cidade_config, ano)
                if bot_download.configurar_navegador():
                    if (bot_download.navegar_para_pagina() and
                        bot_download.fazer_login() and
                        bot_download.selecionar_municipio() and
                        bot_download.selecionar_exercicio() and
                        bot_download.pressionar_f4() and
                        bot_download.navegar_relatorios_favoritos()):
                        baixar_ultimos_5_arquivos(bot_download.navegador, bot_download.wait, file_converter, 900)
                    bot_download.fechar_navegador()

        # Resumo do processamento
        print("\n" + "="*60)
        print("RESUMO DO PROCESSAMENTO")
        print("="*60)
        print(f"✓ Relatórios processados com sucesso: {len(relatorios_processados)}")
        if relatorios_processados:
            for rel in relatorios_processados:
                print(f"  • {rel}")

        if relatorios_falhados:
            print(f"\n✗ Relatórios que falharam: {len(relatorios_falhados)}")
            for rel in relatorios_falhados:
                print(f"  • {rel}")

        # Verificar se foi cancelado antes da conversão final
        foi_cancelado = cancelado_callback and cancelado_callback()

        # FASE FINAL: Converter todos os arquivos baixados
        if len(relatorios_processados) > 0 and not foi_cancelado:
            print("\n" + "="*60)
            print("FASE FINAL: CONVERSÃO DOS ARQUIVOS")
            print("="*60)

            total_baixados, total_convertidos = converter_arquivos_finais(file_converter)

            # Gerar relatório final
            gerar_relatorio_final(relatorios_processados, relatorios_falhados, total_baixados, total_convertidos, ano, nome_cidade)

        elif foi_cancelado:
            print("\n⚠ Conversão final cancelada pelo usuário")
        else:
            print("\n⚠ Nenhum relatório foi processado com sucesso, pulando conversão")

        print("\n" + "="*60)
        if foi_cancelado:
            print("SCRIPT CONGONHAS - CANCELADO")
        else:
            print("SCRIPT CONGONHAS CONCLUÍDO")
        print(f"Total processado: {len(relatorios_processados)}/{len(relatorios)} relatórios")
        print("="*60)

        # Retornar sucesso apenas se não foi cancelado e teve processamentos
        return len(relatorios_processados) > 0 and not foi_cancelado
        
    except Exception as e:
        print(f"\n✗ Erro no script de Congonhas: {e}")
        return False


def _processar_anexo_03(navegador, wait):
    """
    Processa o relatorio Anexo 03 - Demonstrativo da Receita Corrente Liquida
    """
    try:
        print("\n--- Processando Anexo 03 ---")
        
        # 1. Clicar no link do Anexo 03
        print("  - Clicando no Anexo 03...")
        anexo_03 = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Anexo 03 - Demonstrativo da Receita Corrente Líquida')]"
            ))
        )
        anexo_03.click()

        # 2. Alterar "Sim" para "Não"
        print("  - Selecionando 'Não'...")
        try:
            # Tentar primeiro pelo ID do span
            dropdown_sim = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-1']/parent::a"))
            )
        except TimeoutException:
            # Fallback: clicar no link pai com classe select2-choice
            print("    - Tentando seletor alternativo...")
            dropdown_sim = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice' and .//span[text()='Sim']]"))
            )

        dropdown_sim.click()

        # Selecionar "Não" na lista
        opcao_nao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and text()='Não']"))
        )
        opcao_nao.click()

        # 3. Selecionar município
        print("  - Selecionando município...")
        try:
            # Tentar primeiro pelo ID s2id_autogen3
            campo_municipio = wait.until(
                EC.element_to_be_clickable((By.ID, "s2id_autogen3"))
            )
        except TimeoutException:
            # Fallback: buscar por classe select2-input
            print("    - Tentando seletor alternativo...")
            campo_municipio = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.select2-input.select2-default"))
            )
        
        campo_municipio.click()
        campo_municipio.clear()
        campo_municipio.send_keys("MUNICIPIO DE CONGONHAS")

        # Selecionar a opção que aparece
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE CONGONHAS')]"))
        )
        opcao_municipio.click()

        # 4. Inserir mês atual
        print("  - Inserindo mês atual...")
        mes_atual = datetime.now().month
        mes_formatado = f"{mes_atual:02d}"
        
        campo_mes = wait.until(
            EC.element_to_be_clickable((By.ID, "76014315"))
        )
        campo_mes.clear()
        campo_mes.send_keys(mes_formatado)

        # 5. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()

        # 6. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 7. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Anexo 03 processado com sucesso (mês {mes_formatado})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Anexo 03")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Anexo 03: {e}")
        return False


def _processar_anexo_08(navegador, wait):
    """
    Processa o relatorio Anexo 08 - Demonstrativo das Receitas e Despesas com Manutencao e Desenvolvimento do Ensino
    """
    try:
        print("\n--- Processando Anexo 08 ---")
        
        # 1. Clicar no link do Anexo 08
        print("  - Clicando no Anexo 08...")
        anexo_08 = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Anexo 08 - Demonstrativo das Receitas e Despesas com Manutenção e Desenvolvimento do Ensino - MDE')]"
            ))
        )
        anexo_08.click()

        # 2. Alterar de Bimestral para Mensal
        print("  - Alterando de Bimestral para Mensal...")
        # Localizar especificamente o dropdown que contém "Bimestral"
        select2_dropdown = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-4']/parent::a"))
        )
        select2_dropdown.click()

        # Selecionar opção "Mensal"
        opcao_mensal = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='select2-result-label' and text()='Mensal']"))
        )
        opcao_mensal.click()

        # 3. Inserir mês atual
        print("  - Inserindo mês atual...")
        mes_atual = datetime.now().month
        mes_formatado = f"{mes_atual:02d}"
        
        campo_mes = wait.until(
            EC.element_to_be_clickable((By.ID, "75828397"))
        )
        campo_mes.clear()
        campo_mes.send_keys(mes_formatado)

        # 4. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()

        # 5. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 6. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Anexo 08 processado com sucesso (mês {mes_formatado})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Anexo 08")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Anexo 08: {e}")
        return False


def _processar_anexo_iv(navegador, wait, ano):
    """
    Processa o relatorio Anexo IV - Demonstrativo das Receitas com Acoes e Servicos Publicos de Saude
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar o relatorio
        
    Returns:
        bool: True se processado com sucesso
    """
    try:
        print("\n--- Processando Anexo IV ---")
        
        # Verificar se ano foi fornecido
        if not ano:
            ano = datetime.now().year
            print(f"  - Usando ano atual: {ano}")
        
        # 1. Clicar no link do Anexo IV
        print("  - Clicando no Anexo IV...")
        anexo_iv = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Anexo IV - Demonstrativo das Receitas com Ações e Serviços Públicos de Saúde - A partir de 2023')]"
            ))
        )
        anexo_iv.click()

        # 2. Inserir ano
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "74986691"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))

        # 3. Alterar "Anual" para "Mensal"
        print("  - Selecionando 'Mensal'...")
        dropdown_anual = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//span[@id='select2-chosen-4']/parent::a"
            ))
        )
        dropdown_anual.click()

        # Selecionar "Mensal" na lista
        opcao_mensal = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and text()='Mensal']"))
        )
        opcao_mensal.click()

        # 4. Inserir mês atual (sem zero na frente)
        print("  - Inserindo mês atual...")
        mes_atual = datetime.now().month
        mes_sem_zero = str(mes_atual)  # Sem zero na frente: 1, 2, ..., 12
        
        campo_mes = wait.until(
            EC.element_to_be_clickable((By.ID, "74986694"))
        )
        campo_mes.clear()
        campo_mes.send_keys(mes_sem_zero)

        # 5. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()

        # 6. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 7. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Anexo IV processado com sucesso (ano: {ano}, mês: {mes_sem_zero})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Anexo IV")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Anexo IV: {e}")
        return False


def _processar_anexo_vii(navegador, wait, ano):
    """
    Processa o relatorio Anexo VII - Demonstrativo da Despesa de Pessoal por Poder - A partir de 2023
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar o relatorio
        
    Returns:
        bool: True se processado com sucesso
    """
    # Mapeamento dos meses em português
    meses_portugues = {
        1: "1 - Janeiro",
        2: "2 - Fevereiro", 
        3: "3 - Março",
        4: "4 - Abril",
        5: "5 - Maio",
        6: "6 - Junho",
        7: "7 - Julho",
        8: "8 - Agosto",
        9: "9 - Setembro",
        10: "10 - Outubro",
        11: "11 - Novembro",
        12: "12 - Dezembro"
    }
    
    try:
        print("\n--- Processando Anexo VII ---")
        
        # Verificar se ano foi fornecido
        if not ano:
            ano = datetime.now().year
            print(f"  - Usando ano atual: {ano}")
        
        # 1. Clicar no link do Anexo VII
        print("  - Clicando no Anexo VII...")
        anexo_vii = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Anexo VII - Demonstrativo da Despesa de Pessoal por Poder - A partir de 2023')]"
            ))
        )
        anexo_vii.click()

        # 2. Selecionar ano no dropdown (s2id_autogen4)
        print(f"  - Selecionando ano: {ano}...")
        dropdown_ano = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='s2id_autogen4']/a"))
        )
        dropdown_ano.click()

        # Selecionar o ano na lista
        opcao_ano = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'select2-result-label') and text()='{ano}']"))
        )
        opcao_ano.click()

        # 3. Alterar "Não" para "Sim" (select2-chosen-6)
        print("  - Selecionando 'Sim'...")
        dropdown_nao = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//span[@id='select2-chosen-6']/parent::a"
            ))
        )
        dropdown_nao.click()

        # Selecionar "Sim" na lista
        opcao_sim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and text()='Sim']"))
        )
        opcao_sim.click()

        # 4. Selecionar mês atual no dropdown (select2-chosen-7)
        print("  - Selecionando mês atual...")
        mes_atual = datetime.now().month
        mes_formatado = meses_portugues[mes_atual]

        dropdown_mes = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//span[@id='select2-chosen-7']/parent::a"
            ))
        )
        dropdown_mes.click()

        # Selecionar a opção do mês que aparece (formato "1 - Janeiro")
        opcao_mes = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'select2-result-label') and contains(text(), '{mes_formatado}')]"))
        )
        opcao_mes.click()

        # 5. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        
        # 6. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 7. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Anexo VII processado com sucesso (ano: {ano}, mês: {mes_formatado})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Anexo VII")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Anexo VII: {e}")
        return False


def _processar_balancete_despesa(navegador, wait, ano):
    """
    Processa o relatorio Balancete da Despesa
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar o relatorio
        
    Returns:
        bool: True se processado com sucesso
    """
    try:
        print("\n--- Processando Balancete da Despesa ---")
        
        # Verificar se ano foi fornecido
        if not ano:
            ano = datetime.now().year
            print(f"  - Usando ano atual: {ano}")
        
        # 1. Clicar no link do Balancete da despesa
        print("  - Clicando no Balancete da despesa...")
        balancete_despesa = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Balancete da despesa')]"
            ))
        )
        balancete_despesa.click()

        # 2. Inserir ano (ID: 75897447)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "75897447"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))

        # 3. Alterar dropdown de "Natureza da despesa (LOA)" para "Número despesa + Recurso (LOA)" (ID: select2-chosen-9)
        print("  - Selecionando 'Número despesa + Recurso (LOA)'...")
        dropdown_natureza = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-9']/parent::a"))
        )
        dropdown_natureza.click()

        opcao_numero_despesa = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-9']//div[contains(text(), 'Número despesa + Recurso (LOA)')]"))
        )
        opcao_numero_despesa.click()

        # 4. Selecionar "Organograma Nível 2" (ID: select2-chosen-10)
        print("  - Selecionando 'Organograma Nível 2'...")
        dropdown_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-10']/parent::a"))
        )
        dropdown_organograma.click()

        opcao_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-10']//div[contains(text(), 'Organograma Nível 2')]"))
        )
        opcao_organograma.click()

        # 5. Selecionar "Função" (ID: select2-chosen-11)
        print("  - Selecionando 'Função'...")
        dropdown_funcao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-11']/parent::a"))
        )
        dropdown_funcao.click()

        opcao_funcao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-11']//div[contains(text(), 'Função')]"))
        )
        opcao_funcao.click()

        # 6. Selecionar "Subfunção" (ID: select2-chosen-12)
        print("  - Selecionando 'Subfunção'...")
        dropdown_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-12']/parent::a"))
        )
        dropdown_subfuncao.click()

        opcao_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-12']//div[contains(text(), 'Subfunção')]"))
        )
        opcao_subfuncao.click()

        # 7. Selecionar "2 / Especificação da Fonte" (ID: select2-chosen-20)
        print("  - Selecionando '2 / Especificação da Fonte'...")
        dropdown_especificacao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-20']/parent::a"))
        )
        dropdown_especificacao.click()

        opcao_especificacao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-20']//div[contains(text(), '2 / Especificação da Fonte')]"))
        )
        opcao_especificacao.click()

        # 8. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        
        # 9. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 10. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Balancete da Despesa processado com sucesso (ano: {ano})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Balancete da Despesa")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Balancete da Despesa: {e}")
        return False


def _processar_balancete_receita(navegador, wait, ano):
    """
    Processa o relatorio Balancete da Receita
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar o relatorio
        
    Returns:
        bool: True se processado com sucesso
    """
    try:
        print("\n--- Processando Balancete da Receita ---")
        
        # Verificar se ano foi fornecido
        if not ano:
            ano = datetime.now().year
            print(f"  - Usando ano atual: {ano}")
        
        # 1. Clicar no link do Balancete da Receita
        print("  - Clicando no Balancete da Receita...")
        balancete_receita = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Balancete da Receita')]"
            ))
        )
        balancete_receita.click()

        # 2. Inserir ano (ID: 74984816)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "74984816"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))

        # 3. Selecionar "Comparativo orçado/arrecadado (c/ previsão atualizada (Líquido))" (ID: select2-chosen-8)
        print("  - Selecionando 'Comparativo orçado/arrecadado (c/ previsão atualizada (Líquido))'...")
        dropdown_comparativo = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-8']/parent::a"))
        )
        dropdown_comparativo.click()

        opcao_comparativo = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-8']//div[contains(@class, 'select2-result-label') and contains(text(), 'Comparativo orçado/arrecadado (c/ previsão atualizada (Líquido))')]"))
        )
        opcao_comparativo.click()

        # 4. Selecionar "Recurso" no Agrupar por (ID: select2-chosen-11)
        print("  - Selecionando 'Recurso' no Agrupar por...")
        dropdown_agrupar = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-11']/parent::a"))
        )
        dropdown_agrupar.click()

        opcao_recurso = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-11']//div[contains(@class, 'select2-result-label') and contains(text(), 'Recurso')]"))
        )
        opcao_recurso.click()

        # 5. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        
        # 6. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 7. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Balancete da Receita processado com sucesso (ano: {ano})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Balancete da Receita")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Balancete da Receita: {e}")
        return False


def _processar_extrato_receita(navegador, wait, ano):
    """
    Processa o relatorio Extrato da Receita
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar o relatorio
        
    Returns:
        bool: True se processado com sucesso
    """
    try:
        print("\n--- Processando Extrato da Receita ---")
        
        # Verificar se ano foi fornecido
        if not ano:
            ano = datetime.now().year
            print(f"  - Usando ano atual: {ano}")
        
        # 1. Clicar no link do Extrato da receita
        print("  - Clicando no Extrato da receita...")
        extrato_receita = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Extrato da receita')]"
            ))
        )
        extrato_receita.click()

        # 2. Inserir ano (ID: 75383299)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "75383299"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))

        # 3. Selecionar "MUNICIPIO DE CONGONHAS" (ID: select2-chosen-2)
        print("  - Selecionando 'MUNICIPIO DE CONGONHAS'...")
        dropdown_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-2']/parent::a"))
        )
        dropdown_municipio.click()

        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-2']//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE CONGONHAS')]"))
        )
        opcao_municipio.click()

        # 4. Selecionar "Primeiro dia do mês" (ID: select2-chosen-4)
        print("  - Selecionando 'Primeiro dia do mês'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-4']/parent::a"))
        )
        dropdown_data_inicio.click()

        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-4']//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do mês')]"))
        )
        opcao_primeiro_dia.click()

        # 5. Selecionar "Último dia do mês" (ID: select2-chosen-6)
        print("  - Selecionando 'Último dia do mês'...")
        dropdown_data_fim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-6']/parent::a"))
        )
        dropdown_data_fim.click()

        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-6']//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do mês')]"))
        )
        opcao_ultimo_dia.click()

        # 6. Alterar "Realizado" para "Previsto/Realizado" (ID: select2-chosen-7)
        print("  - Selecionando 'Previsto/Realizado'...")
        dropdown_realizado = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-7']/parent::a"))
        )
        dropdown_realizado.click()

        opcao_previsto_realizado = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-7']//div[contains(@class, 'select2-result-label') and contains(text(), 'Previsto/Realizado')]"))
        )
        opcao_previsto_realizado.click()

        # 7. Adicionar "Conta Bancaria" nas Colunas Complementares (ID: s2id_autogen8)
        print("  - Adicionando 'Conta Bancaria' às colunas complementares...")
        campo_colunas = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen8"))
        )
        campo_colunas.click()
        campo_colunas.send_keys("Conta Bancaria")

        # Selecionar a opção "Conta Bancaria" quando aparecer
        opcao_conta_bancaria = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Conta Bancaria')]"))
        )
        opcao_conta_bancaria.click()

        # 8. Adicionar "Recurso" no Agrupar por (ID: s2id_autogen9)
        print("  - Adicionando 'Recurso' ao agrupamento...")
        campo_agrupar = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen9"))
        )
        campo_agrupar.click()
        campo_agrupar.send_keys("Recurso")

        # Selecionar a opção "Recurso" quando aparecer
        opcao_recurso = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Recurso')]"))
        )
        opcao_recurso.click()

        # 9. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        
        # 10. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 11. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Extrato da Receita processado com sucesso (ano: {ano})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Extrato da Receita")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Extrato da Receita: {e}")
        return False


def _processar_relacao_empenhos(navegador, wait, ano):
    """
    Processa o relatorio Relação de Empenhos - CMM
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar o relatorio
        
    Returns:
        bool: True se processado com sucesso
    """
    try:
        print("\n--- Processando Relação de Empenhos - CMM ---")
        
        # Verificar se ano foi fornecido
        if not ano:
            ano = datetime.now().year
            print(f"  - Usando ano atual: {ano}")
        
        # 1. Clicar no link da Relação de Empenhos - CMM
        print("  - Clicando na Relação de Empenhos - CMM...")
        relacao_empenhos = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Relação de Empenhos - CMM')]"
            ))
        )
        relacao_empenhos.click()

        # 2. Inserir ano (ID: 74429635)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "74429635"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))

        # 3. Selecionar "MUNICIPIO DE CONGONHAS" (ID: s2id_autogen3)
        print("  - Selecionando município 'MUNICIPIO DE CONGONHAS'...")
        campo_municipio = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen3"))
        )
        campo_municipio.click()

        # Selecionar a opção que aparece
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE CONGONHAS')]"))
        )
        opcao_municipio.click()

        # 4. Selecionar "Primeiro dia do ano" (ID: select2-chosen-7)
        print("  - Selecionando 'Primeiro dia do ano'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-7']/parent::a"))
        )
        dropdown_data_inicio.click()

        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do ano')]"))
        )
        opcao_primeiro_dia.click()


        # 5. Alterar "Data específica" para "Último dia do ano" (ID: select2-chosen-9)
        print("  - Selecionando 'Último dia do ano'...")
        dropdown_data_final = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-9']/parent::a"))
        )
        dropdown_data_final.click()

        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do ano')]"))
        )
        opcao_ultimo_dia.click()

        # 6. Selecionar "Organograma Nível 2" (ID: select2-chosen-71)
        print("  - Selecionando 'Organograma Nível 2'...")
        dropdown_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-16']/parent::a"))
        )
        dropdown_organograma.click()

        opcao_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Organograma Nível 2')]"))
        )
        opcao_organograma.click()

        # 7. Selecionar "Subfunção" (ID: select2-chosen-72)
        print("  - Selecionando 'Subfunção'...")
        dropdown_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-17']/parent::a"))
        )
        dropdown_subfuncao.click()

        opcao_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Subfunção')]"))
        )
        opcao_subfuncao.click()

        # 8. Selecionar "Ação" (ID: select2-chosen-73)
        print("  - Selecionando 'Ação'...")
        dropdown_acao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-18']/parent::a"))
        )
        dropdown_acao.click()

        opcao_acao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Ação')]"))
        )
        opcao_acao.click()

        # 9. Alterar "Não" para "Sim" (ID: select2-chosen-74)
        print("  - Selecionando 'Sim'...")
        dropdown_nao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-19']/parent::a"))
        )
        dropdown_nao.click()

        opcao_sim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Sim')]"))
        )
        opcao_sim.click()

        # 10. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        
        # 11. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 12. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Relação de Empenhos - CMM processada com sucesso (ano: {ano})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Relação de Empenhos - CMM")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Relação de Empenhos - CMM: {e}")
        return False


def _processar_relacao_pagamentos(navegador, wait, ano):
    """
    Processa o relatorio Relação de Pagamentos Efetuados
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar o relatorio
        
    Returns:
        bool: True se processado com sucesso
    """
    try:
        print("\n--- Processando Relação de Pagamentos Efetuados ---")
        
        # Verificar se ano foi fornecido
        if not ano:
            ano = datetime.now().year
            print(f"  - Usando ano atual: {ano}")
        
        # 1. Clicar no link da Relação de Pagamentos Efetuados
        print("  - Clicando na Relação de Pagamentos Efetuados...")
        relacao_pagamentos = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Relação de Pagamentos Efetuados')]"
            ))
        )
        relacao_pagamentos.click()

        # 2. Inserir ano (ID: 75685838)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "75685838"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))

        # 3. Alterar "Sim" para "Não" (ID: select2-chosen-1)
        print("  - Selecionando 'Não'...")
        dropdown_sim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-1']/parent::a"))
        )
        dropdown_sim.click()

        opcao_nao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Não')]"))
        )
        opcao_nao.click()

        # 4. Selecionar opção "MUNICIPIO DE CONGONHAS" no dropdown.
        print("  - Selecionando 'MUNICIPIO DE CONGONHAS'...")
        campo_municipio = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen3"))
        )
        campo_municipio.click()

        # Selecionar a opção diretamente
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE CONGONHAS')]"))
        )
        opcao_municipio.click()

        # 5. Alterar "Data específica" para "Primeiro dia do mês" (ID: select2-chosen-6)
        print("  - Selecionando 'Primeiro dia do mês'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-6']/parent::a"))
        )
        dropdown_data_inicio.click()

        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do mês')]"))
        )
        opcao_primeiro_dia.click()

        # 6. Alterar "Data específica" para "Último dia do mês" (ID: select2-chosen-49)
        print("  - Selecionando 'Último dia do mês'...")
        dropdown_data_fim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-8']/parent::a"))
        )
        dropdown_data_fim.click()

        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do mês')]"))
        )
        opcao_ultimo_dia.click()

        # 8. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        
        # 9. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 10. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Relação de Pagamentos Efetuados processada com sucesso (ano: {ano})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Relação de Pagamentos Efetuados")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Relação de Pagamentos Efetuados: {e}")
        return False


def _processar_relacao_liquidacoes(navegador, wait, ano):
    """
    Processa o relatorio Relação geral de liquidações por período - Agrupadas por ação e natureza da despesa - CMM
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar o relatorio
        
    Returns:
        bool: True se processado com sucesso
    """
    try:
        print("\n--- Processando Relação geral de liquidações por período ---")
        
        # Verificar se ano foi fornecido
        if not ano:
            ano = datetime.now().year
            print(f"  - Usando ano atual: {ano}")
        
        # 1. Clicar no link da Relação geral de liquidações por período
        print("  - Clicando na Relação geral de liquidações por período...")
        relacao_liquidacoes = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'ng-binding') and contains(text(), 'Relação geral de liquidações por período - Agrupadas por ação e natureza da despesa - CMM')]"
            ))
        )
        relacao_liquidacoes.click()

        # 2. Selecionar "MUNICIPIO DE CONGONHAS" (ID: select2-chosen-2)
        print("  - Selecionando 'MUNICIPIO DE CONGONHAS'...")
        dropdown_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-2']/parent::a"))
        )
        dropdown_municipio.click()

        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE CONGONHAS')]"))
        )
        opcao_municipio.click()

        # 3. Inserir ano usando campo com ng-model especial
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[ng-model='vm.newInput']"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))
        campo_ano.send_keys(Keys.ENTER)  # Pressionar Enter para confirmar

        # 4. Alterar "Data específica" para "Primeiro dia do ano" (ID: select2-chosen-409)
        print("  - Selecionando 'Primeiro dia do ano'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-4']/parent::a"))
        )
        dropdown_data_inicio.click()

        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do ano')]"))
        )
        opcao_primeiro_dia.click()

        # 5. Alterar "Data específica" para "Último dia do ano" (ID: select2-chosen-411)
        print("  - Selecionando 'Último dia do ano'...")
        dropdown_data_fim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-6']/parent::a"))
        )
        dropdown_data_fim.click()

        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do ano')]"))
        )
        opcao_ultimo_dia.click()

        # 6. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        
        # 7. Selecionar formato XLS
        print("  - Selecionando formato XLS...")
        try:
            # Tentar clicar diretamente no radio button
            radio_xls = wait.until(
                EC.presence_of_element_located((By.ID, "rb-export-as-xls"))
            )
            navegador.execute_script("arguments[0].click();", radio_xls)
        except Exception:
            # Fallback: clicar no label associado
            print("    - Tentando clicar no label...")
            label_xls = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='rb-export-as-xls']"))
            )
            label_xls.click()
        time.sleep(1)
        
        # 8. Executar relatório
        print("  - Executando relatório...")
        botao_executar = wait.until(
            EC.element_to_be_clickable((By.ID, "executarRelComParams"))
        )
        botao_executar.click()
        time.sleep(1)  # Aguardar processamento
        
        print(f"  ✓ Relação geral de liquidações processada com sucesso (ano: {ano})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Relação geral de liquidações")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Relação geral de liquidações: {e}")
        return False


def baixar_ultimos_5_arquivos(navegador, wait, file_converter, espera_segundos=300):
    """
    Função para baixar todos os arquivos disponíveis

    Args:
        navegador: Instância do WebDriver
        wait: Instância do WebDriverWait
        file_converter: Instância do FileConverter
        espera_segundos: Tempo de espera antes de baixar (300 ou 600 segundos)

    Returns:
        int: Número de arquivos baixados com sucesso
    """

    print(f"\n--- Baixando arquivos (espera de {espera_segundos}s) ---")

    # Aguardar o tempo especificado
    print(f"⏳ Aguardando {espera_segundos} segundos...")
    minutos = espera_segundos // 60
    for i in range(minutos):
        time.sleep(60)
        restante = espera_segundos - (i + 1) * 60
        if restante > 0:
            print(f"   {restante} segundos restantes...")
    print("✓ Tempo de espera concluído")

    # Abrir Gerenciador de extensões
    print("\nAbrindo Gerenciador de extensões...")
    gerenciador = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//a[@data-ng-click='executandoCtrl.abrirAdmExtensoes()' and contains(@title, 'execuções')]"
        ))
    )
    gerenciador.click()
    time.sleep(2)
    print("✓ Gerenciador aberto")

    # Atualizar andamento
    print("Atualizando andamento...")
    botao_atualizar = navegador.find_element(
        By.XPATH,
        "//button[@data-ng-click='vm.carregarMinhasExecucoes()']"
    )
    botao_atualizar.click()
    time.sleep(2)
    print("✓ Andamento atualizado")

    # Baixar todos os arquivos disponíveis
    print("\nBaixando arquivos disponíveis...")
    botoes_download = navegador.find_elements(
        By.XPATH,
        "//button[@data-ng-show='vm.gerouResultado(execucao)' and @data-ng-click='vm.downloadResultado(execucao)']"
    )

    arquivos_baixados = 0
    total_botoes = len(botoes_download)

    if botoes_download:
        print(f"Encontrados {total_botoes} botões de download...")
        for i, botao in enumerate(botoes_download, 1):
            try:
                # Tentar clicar no botão
                ActionChains(navegador).move_to_element(botao).click().perform()
                arquivos_baixados += 1
                print(f"  ✓ Download {arquivos_baixados} iniciado (botão {i}/{total_botoes})")
                time.sleep(1)  # Pequena pausa entre cliques
            except Exception as e:
                # Botão não é clicável, apenas pular para o próximo
                print(f"  - Botão {i}/{total_botoes} não clicável, pulando...")
                continue
    else:
        print("⚠ Nenhum arquivo encontrado")

    # Aguardar downloads completarem
    if arquivos_baixados > 0:
        print(f"\nAguardando conclusão de {arquivos_baixados} downloads...")
        time.sleep(5)  # Aguarda 5 segundos para downloads terminarem
        print("✓ Downloads concluídos")

    print(f"\n✅ {arquivos_baixados} arquivos baixados com sucesso\n")
    return arquivos_baixados


def converter_arquivos_finais(file_converter):
    """
    Converte todos os arquivos baixados de XLS para XLSX

    Args:
        file_converter: Instância do FileConverter

    Returns:
        tuple: (total_baixados, total_convertidos)
    """
    print("\n" + "="*60)
    print("CONVERSÃO FINAL DOS ARQUIVOS")
    print("="*60)

    # Contar arquivos únicos baixados
    arquivos_unicos = file_converter.contar_arquivos_unicos_temp()
    print(f"\nTotal de arquivos únicos baixados: {arquivos_unicos}")

    if arquivos_unicos == 0:
        print("⚠ Nenhum arquivo para converter")
        return 0, 0

    # Mover arquivos para pasta raw
    print("\nMovendo arquivos para processamento...")
    movidos = file_converter.mover_unicos_temp_para_raw()
    print(f"✓ {movidos} arquivos movidos")

    # Converter XLS para XLSX
    print("\nConvertendo arquivos XLS para XLSX...")
    total, convertidos = file_converter.converter_todos_raw()

    if convertidos > 0:
        print(f"\n✅ CONVERSÃO COMPLETA: {convertidos} arquivos convertidos")
    else:
        print("\n⚠ Nenhum arquivo foi convertido")

    return total, convertidos


def gerar_relatorio_final(relatorios_processados, relatorios_falhados, total_baixados, total_convertidos, ano, nome_cidade):
    
    # Gera um arquivo de relatório TXT com o resumo do processamento
    
    try:
        from datetime import datetime
        import os
        from src.classes.file.path_manager import obter_caminho_dados

        # Criar pasta de saída se não existir (usando diretório configurado pelo usuário)
        pasta_saida = obter_caminho_dados(os.path.join("betha", nome_cidade, str(ano)))
        os.makedirs(pasta_saida, exist_ok=True)

        # Nome do arquivo de relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_relatorio = os.path.join(pasta_saida, f"relatorio_processamento_{timestamp}.txt")

        # Gerar conteúdo do relatório
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RELATÓRIO DE PROCESSAMENTO - BETHA SISTEMAS\n")
            f.write("="*60 + "\n\n")

            f.write(f"Município: {nome_cidade.replace('_', ' ').title()}\n")
            f.write(f"Ano: {ano}\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("\n")

            f.write("-"*60 + "\n")
            f.write("RESUMO DO PROCESSAMENTO\n")
            f.write("-"*60 + "\n")
            f.write(f"Total de relatórios processados: {len(relatorios_processados)}/{len(relatorios_processados) + len(relatorios_falhados)}\n")
            f.write(f"Total de arquivos baixados: {total_baixados}\n")
            f.write(f"Total de arquivos convertidos: {total_convertidos}\n")
            f.write("\n")

            if relatorios_processados:
                f.write("RELATÓRIOS PROCESSADOS COM SUCESSO:\n")
                for i, rel in enumerate(relatorios_processados, 1):
                    f.write(f"  {i}. {rel}\n")
                f.write("\n")

            if relatorios_falhados:
                f.write("RELATÓRIOS QUE FALHARAM:\n")
                for i, rel in enumerate(relatorios_falhados, 1):
                    f.write(f"  {i}. {rel}\n")
                f.write("\n")

            f.write("-"*60 + "\n")
            f.write("FIM DO RELATÓRIO\n")
            f.write("-"*60 + "\n")

        print(f"\n✓ Relatório salvo em: {arquivo_relatorio}")
        return arquivo_relatorio

    except Exception as e:
        print(f"\n⚠ Erro ao gerar relatório: {e}")
        return None


# end
