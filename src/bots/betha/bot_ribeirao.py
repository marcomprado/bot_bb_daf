#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Ribeirao das Neves - Script especifico para o municipio de Ribeirao das Neves
Contem a logica especifica apos navegar para Relatorios Favoritos
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.classes.file_converter import FileConverter
        ### Order of the scripts
        # # Anexo 03
        # # Anexo 08
        # # Anexo IV
        # # Anexo VII
        # # Balancete da Despesa
        
        # # Balancete da Receita
        # # Extrato da Receita
        # # Relacao de Empenhos - CMM
        # # Relacao de Pagamentos Efetuados 
        # # Relacao geral de liquidacoes por periodo

        # # Baixar todos os arquivos
        
        
def executar_script_ribeirao(navegador, wait, ano=None, nome_cidade="ribeirao_neves"):
    """
    Executa o script especifico para Ribeirao das Neves
    
    Este script e executado apos chegar em "Relatorios Favoritos"
    e contem a logica especifica para este municipio
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        ano: Ano para processar os relatorios
        nome_cidade: Nome da cidade para organização de pastas
        
    Returns:
        bool: True se executado com sucesso
    """
    try:
        print("\n" + "="*60)
        print("SCRIPT RIBEIRAO DAS NEVES - PROCESSANDO RELATORIOS")
        print("="*60)
        
        # Inicializar conversor de arquivos
        file_converter = FileConverter(nome_cidade)
        print(f"\n✓ Sistema de arquivos inicializado para {nome_cidade}")
        
        '''# Processar Anexo 03
        if not _processar_anexo_03(navegador, wait):
            print("⚠ Falha ao processar Anexo 03")
            return False 
        
        # Processar Anexo 08
        if not _processar_anexo_08(navegador, wait):
            print("⚠ Falha ao processar Anexo 08")
            return False
        
        # Processar Anexo IV
        if not _processar_anexo_iv(navegador, wait, ano):
            print("⚠ Falha ao processar Anexo IV")
            return False
        
        # Processar Anexo VII
        if not _processar_anexo_vii(navegador, wait, ano):
            print("⚠ Falha ao processar Anexo VII")
            return False
        
        # Processar Balancete da Despesa
        if not _processar_balancete_despesa(navegador, wait, ano):
            print("⚠ Falha ao processar Balancete da Despesa")
            return False'''
        
        # Processar Baixar os ultimos 5 (Primeiro lote)
        if not _baixar_ultimos_5(navegador, wait, 1, file_converter):
            print("⚠ Falha ao baixar primeiro lote de arquivos")
            # Continuar mesmo se falhar 
        
        # Processar Balancete da Receita
        if not _processar_balancete_receita(navegador, wait, ano):
            print("⚠ Falha ao processar Balancete da Receita")
            return False
        
        # Processar Extrato da Receita
        if not _processar_extrato_receita(navegador, wait, ano):
            print("⚠ Falha ao processar Extrato da Receita")
            return False
        
        # Processar Relação de Empenhos - CMM
        if not _processar_relacao_empenhos(navegador, wait, ano):
            print("⚠ Falha ao processar Relação de Empenhos - CMM")
            return False
        
        # Processar Relação de Pagamentos Efetuados
        if not _processar_relacao_pagamentos(navegador, wait, ano):
            print("⚠ Falha ao processar Relação de Pagamentos Efetuados")
            return False
        
        # Processar Relação geral de liquidações por período
        if not _processar_relacao_liquidacoes(navegador, wait, ano):
            print("⚠ Falha ao processar Relação geral de liquidações por período")
            return False
                
        # Processar Baixar os ultimos 5 (Segundo lote)
        if not _baixar_ultimos_5(navegador, wait, 2, file_converter):
            print("⚠ Falha ao baixar segundo lote de arquivos")
            # Continuar mesmo se falhar
        
        # Converter todos os arquivos XLS para XLSX
        print("\n--- Processando conversão final dos arquivos ---")
        total, convertidos = file_converter.converter_todos_raw()
        if convertidos > 0:
            print(f"  ✓ {convertidos} arquivos convertidos para XLSX com sucesso")
        else:
            print("  ⚠ Nenhum arquivo foi convertido")
        
        print("\n✓ Script de Ribeirao das Neves concluido com sucesso")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro no script de Ribeirao das Neves: {e}")
        return False


def _processar_anexo_03(navegador, wait):
    """
    Processa o relatorio Anexo 03 - Demonstrativo da Receita Corrente Liquida
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        
    Returns:
        bool: True se processado com sucesso
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
        time.sleep(3)  # Aguardar carregamento da página
        
        # 2. Alterar "Sim" para "Não"
        print("  - Selecionando 'Não'...")
        try:
            # Tentar primeiro pelo ID do span
            dropdown_sim = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-1']]"))
            )
        except TimeoutException:
            # Fallback: clicar no link pai com classe select2-choice
            print("    - Tentando seletor alternativo...")
            dropdown_sim = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice' and .//span[text()='Sim']]"))
            )
        
        dropdown_sim.click()
        time.sleep(1)
        
        # Selecionar "Não" na lista
        opcao_nao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and text()='Não']"))
        )
        opcao_nao.click()
        time.sleep(1)
        
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
        campo_municipio.send_keys("MUNICIPIO DE RIBEIRAO DAS NEVES")
        time.sleep(1)
        
        # Selecionar a opção que aparece
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE RIBEIRAO DAS NEVES')]"))
        )
        opcao_municipio.click()
        time.sleep(1)
        
        # 4. Inserir mês atual
        print("  - Inserindo mês atual...")
        mes_atual = datetime.now().month
        mes_formatado = f"{mes_atual:02d}"
        
        campo_mes = wait.until(
            EC.element_to_be_clickable((By.ID, "75525299"))
        )
        campo_mes.clear()
        campo_mes.send_keys(mes_formatado)
        time.sleep(1)
        
        # 5. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Alterar de Bimestral para Mensal
        print("  - Alterando de Bimestral para Mensal...")
        # Localizar especificamente o dropdown que contém "Bimestral"
        select2_dropdown = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[@class='select2-choice' and .//span[@id='select2-chosen-4' and contains(text(), 'Bimestral')]]"
            ))
        )
        select2_dropdown.click()
        time.sleep(1)
        
        # Selecionar opção "Mensal"
        opcao_mensal = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='select2-result-label' and text()='Mensal']"))
        )
        opcao_mensal.click()
        time.sleep(2) 
        
        # 3. Inserir mês atual
        print("  - Inserindo mês atual...")
        mes_atual = datetime.now().month
        mes_formatado = f"{mes_atual:02d}"
        
        campo_mes = wait.until(
            EC.element_to_be_clickable((By.ID, "75828397"))
        )
        campo_mes.clear()
        campo_mes.send_keys(mes_formatado)
        time.sleep(1)
        
        # 4. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Inserir ano
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "74986691"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))
        time.sleep(1)
        
        # 3. Alterar "Anual" para "Mensal"
        print("  - Selecionando 'Mensal'...")
        dropdown_anual = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[@class='select2-choice' and .//span[@id='select2-chosen-4' and contains(text(), 'Anual')]]"
            ))
        )
        dropdown_anual.click()
        time.sleep(1)
        
        # Selecionar "Mensal" na lista
        opcao_mensal = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and text()='Mensal']"))
        )
        opcao_mensal.click()
        time.sleep(1)
        
        # 4. Inserir mês atual (sem zero na frente)
        print("  - Inserindo mês atual...")
        mes_atual = datetime.now().month
        mes_sem_zero = str(mes_atual)  # Sem zero na frente: 1, 2, ..., 12
        
        campo_mes = wait.until(
            EC.element_to_be_clickable((By.ID, "74986694"))
        )
        campo_mes.clear()
        campo_mes.send_keys(mes_sem_zero)
        time.sleep(1)
        
        # 5. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Selecionar ano no dropdown (select2-chosen-5)
        print(f"  - Selecionando ano: {ano}...")
        dropdown_ano = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'select2-choice') and .//span[@id='select2-chosen-5']]"
            ))
        )
        dropdown_ano.click()
        time.sleep(1)
        
        # Selecionar o ano na lista
        opcao_ano = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'select2-result-label') and text()='{ano}']"))
        )
        opcao_ano.click()
        time.sleep(1)
        
        # 3. Alterar "Não" para "Sim" (select2-chosen-6)
        print("  - Selecionando 'Sim'...")
        dropdown_nao = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[@class='select2-choice' and .//span[@id='select2-chosen-6' and contains(text(), 'Não')]]"
            ))
        )
        dropdown_nao.click()
        time.sleep(1)
        
        # Selecionar "Sim" na lista
        opcao_sim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and text()='Sim']"))
        )
        opcao_sim.click()
        time.sleep(1)
        
        # 4. Selecionar mês atual no dropdown (select2-chosen-7)
        print("  - Selecionando mês atual...")
        mes_atual = datetime.now().month
        mes_formatado = meses_portugues[mes_atual]
        
        dropdown_mes = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, 
                "//a[contains(@class, 'select2-choice') and .//span[@id='select2-chosen-7']]"
            ))
        )
        dropdown_mes.click()
        time.sleep(1)
        
        # Selecionar a opção do mês que aparece (formato "1 - Janeiro")
        opcao_mes = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'select2-result-label') and contains(text(), '{mes_formatado}')]"))
        )
        opcao_mes.click()
        time.sleep(1)
        
        # 5. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Inserir ano (ID: 75897447)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "75897447"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))
        time.sleep(1)
        
        # 3. Alterar dropdown de "Natureza da despesa (LOA)" para "Número despesa + Recurso (LOA)" (ID: select2-chosen-9)
        print("  - Selecionando 'Número despesa + Recurso (LOA)'...")
        dropdown_natureza = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-9']]"))
        )
        dropdown_natureza.click()
        time.sleep(1)
        
        opcao_numero_despesa = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-9']//div[contains(text(), 'Número despesa + Recurso (LOA)')]"))
        )
        opcao_numero_despesa.click()
        time.sleep(1)
        
        # 4. Selecionar "Organograma Nível 2" (ID: select2-chosen-10)
        print("  - Selecionando 'Organograma Nível 2'...")
        dropdown_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'select2-choice')][.//span[@id='select2-chosen-10']]"))
        )
        dropdown_organograma.click()
        time.sleep(1)

        opcao_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-10']//div[contains(text(), 'Organograma Nível 2')]"))
        )
        opcao_organograma.click()
        time.sleep(1)
        
        # 5. Selecionar "Função" (ID: select2-chosen-11)
        print("  - Selecionando 'Função'...")
        dropdown_funcao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'select2-choice')][.//span[@id='select2-chosen-11']]"))
        )
        dropdown_funcao.click()
        time.sleep(1)

        opcao_funcao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-11']//div[contains(text(), 'Função')]"))
        )
        opcao_funcao.click()
        time.sleep(1)
        
        # 6. Selecionar "Subfunção" (ID: select2-chosen-12)
        print("  - Selecionando 'Subfunção'...")
        dropdown_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'select2-choice')][.//span[@id='select2-chosen-12']]"))
        )
        dropdown_subfuncao.click()
        time.sleep(1)

        opcao_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-12']//div[contains(text(), 'Subfunção')]"))
        )
        opcao_subfuncao.click()
        time.sleep(1)
        
        # 7. Selecionar "2 / Especificação da Fonte" (ID: select2-chosen-20)
        print("  - Selecionando '2 / Especificação da Fonte'...")
        dropdown_especificacao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'select2-choice')][.//span[@id='select2-chosen-20']]"))
        )
        dropdown_especificacao.click()
        time.sleep(1)
        
        opcao_especificacao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-20']//div[contains(text(), '2 / Especificação da Fonte')]"))
        )
        opcao_especificacao.click()
        time.sleep(1)
        
        # 8. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Inserir ano (ID: 74984816)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "74984816"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))
        time.sleep(1)
        
        # 3. O dropdown "Comparativo orçado/arrecadado (c/ previsão atualizada (Líquido))" (ID: select2-chosen-330) 
        # já vem selecionado por padrão, então não é necessário alterá-lo
        print("  - Mantendo seleção padrão: 'Comparativo orçado/arrecadado (c/ previsão atualizada (Líquido))'...")
        
        # 4. Selecionar "Recurso" (ID: select2-chosen-333)
        print("  - Selecionando 'Recurso'...")
        dropdown_recurso = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-333']]"))
        )
        dropdown_recurso.click()
        time.sleep(1)
        
        opcao_recurso = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Recurso')]"))
        )
        opcao_recurso.click()
        time.sleep(1)
        
        # 5. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Inserir ano (ID: 75383299)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "75383299"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))
        time.sleep(1)
        
        # 3. Manter "MUNICIPIO DE RIBEIRAO DAS NEVES" (já selecionado por padrão)
        print("  - Mantendo seleção: 'MUNICIPIO DE RIBEIRAO DAS NEVES'...")
        
        # 4. Manter "Primeiro dia do mês" (já selecionado por padrão)
        print("  - Mantendo seleção: 'Primeiro dia do mês'...")
        
        # 5. Manter "Último dia do mês" (já selecionado por padrão)  
        print("  - Mantendo seleção: 'Último dia do mês'...")
        
        # 6. Alterar "Realizado" para "Previsto/Realizado" (ID: select2-chosen-455)
        print("  - Selecionando 'Previsto/Realizado'...")
        dropdown_realizado = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-455']]"))
        )
        dropdown_realizado.click()
        time.sleep(1)
        
        opcao_previsto_realizado = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Previsto/Realizado')]"))
        )
        opcao_previsto_realizado.click()
        time.sleep(1)
        
        # 7. Adicionar "Conta Bancaria" nas Colunas Complementares (ID: s2id_autogen456)
        print("  - Adicionando 'Conta Bancaria' às colunas complementares...")
        campo_colunas = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen456"))
        )
        campo_colunas.click()
        campo_colunas.send_keys("Conta Bancaria")
        time.sleep(1)
        
        # Selecionar a opção "Conta Bancaria" quando aparecer
        opcao_conta_bancaria = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Conta Bancaria')]"))
        )
        opcao_conta_bancaria.click()
        time.sleep(1)
        
        # 8. Adicionar "Recurso" no Agrupar por (ID: s2id_autogen457)
        print("  - Adicionando 'Recurso' ao agrupamento...")
        campo_agrupar = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen457"))
        )
        campo_agrupar.click()
        campo_agrupar.send_keys("Recurso")
        time.sleep(1)
        
        # Selecionar a opção "Recurso" quando aparecer
        opcao_recurso = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Recurso')]"))
        )
        opcao_recurso.click()
        time.sleep(1)
        
        # 9. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Inserir ano (ID: 74429635)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "74429635"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))
        time.sleep(1)
        
        # 3. Selecionar "MUNICIPIO DE RIBEIRAO DAS NEVES" (ID: s2id_autogen58)
        print("  - Selecionando 'MUNICIPIO DE RIBEIRAO DAS NEVES'...")
        campo_municipio = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen58"))
        )
        campo_municipio.click()
        campo_municipio.send_keys("MUNICIPIO DE RIBEIRAO DAS NEVES")
        time.sleep(1)
        
        # Selecionar a opção que aparece
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE RIBEIRAO DAS NEVES')]"))
        )
        opcao_municipio.click()
        time.sleep(1)
        
        # 4. Manter "Primeiro dia do ano" (já selecionado por padrão)
        print("  - Mantendo seleção: 'Primeiro dia do ano'...")
        
        # 5. Alterar "Data específica" para "Último dia do ano" (ID: select2-chosen-64)
        print("  - Selecionando 'Último dia do ano'...")
        dropdown_data_final = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-64']]"))
        )
        dropdown_data_final.click()
        time.sleep(1)
        
        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do ano')]"))
        )
        opcao_ultimo_dia.click()
        time.sleep(1)
        
        # 6. Selecionar "Organograma Nível 2" (ID: select2-chosen-71)
        print("  - Selecionando 'Organograma Nível 2'...")
        dropdown_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-71']]"))
        )
        dropdown_organograma.click()
        time.sleep(1)
        
        opcao_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Organograma Nível 2')]"))
        )
        opcao_organograma.click()
        time.sleep(1)
        
        # 7. Selecionar "Subfunção" (ID: select2-chosen-72)
        print("  - Selecionando 'Subfunção'...")
        dropdown_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-72']]"))
        )
        dropdown_subfuncao.click()
        time.sleep(1)
        
        opcao_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Subfunção')]"))
        )
        opcao_subfuncao.click()
        time.sleep(1)
        
        # 8. Selecionar "Ação" (ID: select2-chosen-73)
        print("  - Selecionando 'Ação'...")
        dropdown_acao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-73']]"))
        )
        dropdown_acao.click()
        time.sleep(1)
        
        opcao_acao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Ação')]"))
        )
        opcao_acao.click()
        time.sleep(1)
        
        # 9. Alterar "Não" para "Sim" (ID: select2-chosen-74)
        print("  - Selecionando 'Sim'...")
        dropdown_nao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-74']]"))
        )
        dropdown_nao.click()
        time.sleep(1)
        
        opcao_sim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Sim')]"))
        )
        opcao_sim.click()
        time.sleep(1)
        
        # 10. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Inserir ano (ID: 75685838)
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.ID, "75685838"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))
        time.sleep(1)
        
        # 3. Alterar "Sim" para "Não" (ID: select2-chosen-311)
        print("  - Selecionando 'Não'...")
        dropdown_sim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-311']]"))
        )
        dropdown_sim.click()
        time.sleep(1)
        
        opcao_nao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Não')]"))
        )
        opcao_nao.click()
        time.sleep(1)
        
        # 4. Selecionar "MUNICIPIO DE RIBEIRAO DAS NEVES" (ID: s2id_autogen313)
        print("  - Selecionando 'MUNICIPIO DE RIBEIRAO DAS NEVES'...")
        campo_municipio = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen313"))
        )
        campo_municipio.click()
        campo_municipio.send_keys("MUNICIPIO DE RIBEIRAO DAS NEVES")
        time.sleep(1)
        
        # Selecionar a opção que aparece
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE RIBEIRAO DAS NEVES')]"))
        )
        opcao_municipio.click()
        time.sleep(1)
        
        # 5. Alterar "Data específica" para "Primeiro dia do mês" (ID: select2-chosen-316)
        print("  - Selecionando 'Primeiro dia do mês'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-316']]"))
        )
        dropdown_data_inicio.click()
        time.sleep(1)
        
        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do mês')]"))
        )
        opcao_primeiro_dia.click()
        time.sleep(1)
        
        # 6. Alterar "Data específica" para "Último dia do mês" (ID: select2-chosen-318)
        print("  - Selecionando 'Último dia do mês'...")
        dropdown_data_fim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-318']]"))
        )
        dropdown_data_fim.click()
        time.sleep(1)
        
        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do mês')]"))
        )
        opcao_ultimo_dia.click()
        time.sleep(1)
        
        # 7. Clicar no botão de fechar seleção (se necessário)
        print("  - Limpando seleção se necessário...")
        try:
            botao_fechar = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "abbr.select2-search-choice-close"))
            )
            botao_fechar.click()
            time.sleep(1)
        except TimeoutException:
            print("    - Nenhuma seleção para limpar")
        
        # 8. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
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
        time.sleep(2)
        
        # 2. Selecionar "MUNICIPIO DE RIBEIRAO DAS NEVES" (ID: select2-chosen-407)
        print("  - Selecionando 'MUNICIPIO DE RIBEIRAO DAS NEVES'...")
        dropdown_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-407']]"))
        )
        dropdown_municipio.click()
        time.sleep(1)
        
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE RIBEIRAO DAS NEVES')]"))
        )
        opcao_municipio.click()
        time.sleep(1)
        
        # 3. Inserir ano usando campo com ng-model especial
        print(f"  - Inserindo ano: {ano}...")
        campo_ano = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[ng-model='vm.newInput']"))
        )
        campo_ano.clear()
        campo_ano.send_keys(str(ano))
        campo_ano.send_keys(Keys.ENTER)  # Pressionar Enter para confirmar
        time.sleep(1)
        
        # 4. Alterar "Data específica" para "Primeiro dia do ano" (ID: select2-chosen-409)
        print("  - Selecionando 'Primeiro dia do ano'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-409']]"))
        )
        dropdown_data_inicio.click()
        time.sleep(1)
        
        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do ano')]"))
        )
        opcao_primeiro_dia.click()
        time.sleep(1)
        
        # 5. Alterar "Data específica" para "Último dia do ano" (ID: select2-chosen-411)
        print("  - Selecionando 'Último dia do ano'...")
        dropdown_data_fim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='select2-choice'][.//span[@id='select2-chosen-411']]"))
        )
        dropdown_data_fim.click()
        time.sleep(1)
        
        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do ano')]"))
        )
        opcao_ultimo_dia.click()
        time.sleep(1)
        
        # 6. Abrir opções de execução
        print("  - Abrindo opções de execução...")
        botao_opcoes = wait.until(
            EC.element_to_be_clickable((By.ID, "verOpcoes"))
        )
        botao_opcoes.click()
        time.sleep(1)
        
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
        time.sleep(3)  # Aguardar processamento
        
        print(f"  ✓ Relação geral de liquidações processada com sucesso (ano: {ano})")
        return True
        
    except TimeoutException:
        print("  ✗ Timeout ao processar Relação geral de liquidações")
        return False
    except Exception as e:
        print(f"  ✗ Erro ao processar Relação geral de liquidações: {e}")
        return False


def _baixar_ultimos_5(navegador, wait, lote, file_converter):
    """
    Baixa os últimos 5 relatórios executados do Gerenciador de extensões
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        lote: Número do lote (1 para primeiro, 2 para segundo)
        file_converter: Instância do FileConverter para gerenciar arquivos
        
    Returns:
        bool: True se executado com sucesso
    """
    max_tentativas = 3
    tentativa = 1
    
    # Limpar pasta temp antes de começar
    if lote == 1:
        file_converter.limpar_pasta_temp()
    
    while tentativa <= max_tentativas:
        try:
            print(f"\n--- Baixando últimos 5 arquivos (Lote {lote}, Tentativa {tentativa}/{max_tentativas}) ---")
            
            # 1. Clicar no Gerenciador de extensões
            print("  - Abrindo Gerenciador de extensões...")
            gerenciador = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    "//a[contains(@title, 'visualizar as suas execuções') and contains(@data-ng-click, 'abrirAdmExtensoes')]"
                ))
            )
            gerenciador.click()
            time.sleep(1)
            
            # 2. Clicar no botão Atualizar andamento
            print("  - Atualizando andamento...")
            botao_atualizar = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@data-ng-click, 'carregarMinhasExecucoes')]"
                ))
            )
            botao_atualizar.click()
            time.sleep(1)
            
            # 3. Encontrar e clicar em todos os botões de download "Resultado"
            print("  - Procurando botões de download...")
            botoes_download = navegador.find_elements(
                By.XPATH,
                "//button[contains(@data-ng-click, 'downloadResultado') and contains(@data-ng-show, 'gerouResultado')]"
            )
            
            num_downloads = len(botoes_download)
            print(f"  - Encontrados {num_downloads} botões de download")
            
            # Clicar em cada botão de download
            for i, botao in enumerate(botoes_download, 1):
                try:
                    print(f"    - Baixando arquivo {i}/{num_downloads}...")
                    botao.click()
                    time.sleep(1)  # Pequena pausa entre downloads
                except Exception as e:
                    print(f"    ⚠ Erro ao baixar arquivo {i}: {e}")
            
            # Aguardar downloads serem salvos
            time.sleep(1)
            
            # Verificar quantos arquivos foram baixados para a pasta temp
            arquivos_na_temp = file_converter.contar_arquivos_temp()
            print(f"  - {arquivos_na_temp} arquivos encontrados na pasta temp")
            
            # Verificar se baixou pelo menos 5 arquivos
            if num_downloads >= 5 and arquivos_na_temp >= 5:
                print(f"  ✓ {num_downloads} downloads iniciados, {arquivos_na_temp} arquivos confirmados")
                
                # Mover arquivos de temp para raw
                movidos = file_converter.mover_temp_para_raw()
                print(f"  ✓ {movidos} arquivos movidos para pasta raw")
                
                # 4. Fechar o modal
                print("  - Fechando modal...")
                try:
                    botao_fechar = wait.until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//button[@type='button' and @class='close' and @data-dismiss='modal']"
                        ))
                    )
                    botao_fechar.click()
                    time.sleep(1)
                except TimeoutException:
                    print("    - Modal já fechado ou não encontrado")
                
                return True
            else:
                print(f"  ⚠ Apenas {num_downloads} arquivos baixados (esperado: 5+)")
                
                if tentativa < max_tentativas:
                    print(f"  - Aguardando 5 minutos antes da próxima tentativa...")
                    
                    # Fechar modal antes de esperar
                    try:
                        botao_fechar = navegador.find_element(
                            By.XPATH,
                            "//button[@type='button' and @class='close' and @data-dismiss='modal']"
                        )
                        botao_fechar.click()
                    except:
                        pass
                    
                    time.sleep(300)  # Aguardar 5 minutos
                    tentativa += 1
                else:
                    print(f"  - Continuando com {num_downloads} arquivos após {max_tentativas} tentativas")
                    
                    # Fechar modal
                    try:
                        botao_fechar = navegador.find_element(
                            By.XPATH,
                            "//button[@type='button' and @class='close' and @data-dismiss='modal']"
                        )
                        botao_fechar.click()
                    except:
                        pass
                    
                    return True
                    
        except TimeoutException:
            print(f"  ✗ Timeout ao processar downloads (Tentativa {tentativa})")
            if tentativa >= max_tentativas:
                return False
            tentativa += 1
            time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente
            
        except Exception as e:
            print(f"  ✗ Erro ao processar downloads: {e}")
            if tentativa >= max_tentativas:
                return False
            tentativa += 1
            time.sleep(60)
    
    return False


# end