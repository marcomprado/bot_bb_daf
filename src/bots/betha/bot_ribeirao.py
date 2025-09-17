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
            return False '''

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

        # Baixar todos os arquivos do Gerenciador de extensões
        print("\n" + "="*60)
        print("INICIANDO DOWNLOAD DE TODOS OS ARQUIVOS GERADOS")
        print("="*60)

        if baixar_arquivos(navegador, wait, file_converter, min_arquivos=10):
            print("\n✓ Download e conversão de arquivos concluídos com sucesso")
        else:
            print("\n⚠ Alguns arquivos podem não ter sido baixados/convertidos")

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
                EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-1']/parent::a"))
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
            EC.element_to_be_clickable((By.ID, "76014315"))
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-4']/parent::a"))
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
                "//span[@id='select2-chosen-4']/parent::a"
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
        
        # 2. Selecionar ano no dropdown (s2id_autogen4)
        print(f"  - Selecionando ano: {ano}...")
        dropdown_ano = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='s2id_autogen4']/a"))
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
                "//span[@id='select2-chosen-6']/parent::a"
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
                "//span[@id='select2-chosen-7']/parent::a"
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-9']/parent::a"))
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-10']/parent::a"))
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-11']/parent::a"))
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-12']/parent::a"))
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-20']/parent::a"))
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
        
        # 3. Selecionar "Comparativo orçado/arrecadado (c/ previsão atualizada (Líquido))" (ID: select2-chosen-8)
        print("  - Selecionando 'Comparativo orçado/arrecadado (c/ previsão atualizada (Líquido))'...")
        dropdown_comparativo = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-8']/parent::a"))
        )
        dropdown_comparativo.click()
        time.sleep(1)

        opcao_comparativo = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-8']//div[contains(@class, 'select2-result-label') and contains(text(), 'Comparativo orçado/arrecadado (c/ previsão atualizada (Líquido))')]"))
        )
        opcao_comparativo.click()
        time.sleep(1)

        # 4. Selecionar "Recurso" no Agrupar por (ID: select2-chosen-11)
        print("  - Selecionando 'Recurso' no Agrupar por...")
        dropdown_agrupar = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-11']/parent::a"))
        )
        dropdown_agrupar.click()
        time.sleep(1)

        opcao_recurso = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-11']//div[contains(@class, 'select2-result-label') and contains(text(), 'Recurso')]"))
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
        
        # 3. Selecionar "MUNICIPIO DE RIBEIRAO DAS NEVES" (ID: select2-chosen-2)
        print("  - Selecionando 'MUNICIPIO DE RIBEIRAO DAS NEVES'...")
        dropdown_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-2']/parent::a"))
        )
        dropdown_municipio.click()
        time.sleep(1)

        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-2']//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE RIBEIRAO DAS NEVES')]"))
        )
        opcao_municipio.click()
        time.sleep(1)

        # 4. Selecionar "Primeiro dia do mês" (ID: select2-chosen-4)
        print("  - Selecionando 'Primeiro dia do mês'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-4']/parent::a"))
        )
        dropdown_data_inicio.click()
        time.sleep(1)

        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-4']//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do mês')]"))
        )
        opcao_primeiro_dia.click()
        time.sleep(1)

        # 5. Selecionar "Último dia do mês" (ID: select2-chosen-6)
        print("  - Selecionando 'Último dia do mês'...")
        dropdown_data_fim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-6']/parent::a"))
        )
        dropdown_data_fim.click()
        time.sleep(1)

        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-6']//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do mês')]"))
        )
        opcao_ultimo_dia.click()
        time.sleep(1)

        # 6. Alterar "Realizado" para "Previsto/Realizado" (ID: select2-chosen-7)
        print("  - Selecionando 'Previsto/Realizado'...")
        dropdown_realizado = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-7']/parent::a"))
        )
        dropdown_realizado.click()
        time.sleep(1)

        opcao_previsto_realizado = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//ul[@id='select2-results-7']//div[contains(@class, 'select2-result-label') and contains(text(), 'Previsto/Realizado')]"))
        )
        opcao_previsto_realizado.click()
        time.sleep(1)

        # 7. Adicionar "Conta Bancaria" nas Colunas Complementares (ID: s2id_autogen8)
        print("  - Adicionando 'Conta Bancaria' às colunas complementares...")
        campo_colunas = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen8"))
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

        # 8. Adicionar "Recurso" no Agrupar por (ID: s2id_autogen9)
        print("  - Adicionando 'Recurso' ao agrupamento...")
        campo_agrupar = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen9"))
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
        
        # 3. Selecionar "MUNICIPIO DE RIBEIRAO DAS NEVES" (ID: s2id_autogen3)
        print("  - Selecionando município 'MUNICIPIO DE RIBEIRAO DAS NEVES'...")
        campo_municipio = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen3"))
        )
        campo_municipio.click()
        time.sleep(1)

        # Selecionar a opção que aparece
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE RIBEIRAO DAS NEVES')]"))
        )
        opcao_municipio.click()
        time.sleep(1)

        # 4. Selecionar "Primeiro dia do ano" (ID: select2-chosen-7)
        print("  - Selecionando 'Primeiro dia do ano'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-7']/parent::a"))
        )
        dropdown_data_inicio.click()
        time.sleep(1)

        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do ano')]"))
        )
        opcao_primeiro_dia.click()
        time.sleep(1)

        
        # 5. Alterar "Data específica" para "Último dia do ano" (ID: select2-chosen-9)
        print("  - Selecionando 'Último dia do ano'...")
        dropdown_data_final = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-9']/parent::a"))
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-16']/parent::a"))
        )
        dropdown_organograma.click()
        time.sleep(1)
        
        opcao_organograma = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Organograma Nível 2')]"))
        )
        opcao_organograma.click()
        time.sleep(2)
        
        # 7. Selecionar "Subfunção" (ID: select2-chosen-72)
        print("  - Selecionando 'Subfunção'...")
        dropdown_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-17']/parent::a"))
        )
        dropdown_subfuncao.click()
        time.sleep(1)
        
        opcao_subfuncao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Subfunção')]"))
        )
        opcao_subfuncao.click()
        time.sleep(2)
        
        # 8. Selecionar "Ação" (ID: select2-chosen-73)
        print("  - Selecionando 'Ação'...")
        dropdown_acao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-18']/parent::a"))
        )
        dropdown_acao.click()
        time.sleep(1)
        
        opcao_acao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Ação')]"))
        )
        opcao_acao.click()
        time.sleep(2)
        
        # 9. Alterar "Não" para "Sim" (ID: select2-chosen-74)
        print("  - Selecionando 'Sim'...")
        dropdown_nao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-19']/parent::a"))
        )
        dropdown_nao.click()
        time.sleep(1)
        
        opcao_sim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Sim')]"))
        )
        opcao_sim.click()
        time.sleep(3)
        
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
        
        # 3. Alterar "Sim" para "Não" (ID: select2-chosen-1)
        print("  - Selecionando 'Não'...")
        dropdown_sim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-1']/parent::a"))
        )
        dropdown_sim.click()
        time.sleep(1)
        
        opcao_nao = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Não')]"))
        )
        opcao_nao.click()
        time.sleep(1)
        
        # 4. Selecionar opção "MUNICIPIO DE RIBEIRAO DAS NEVES" no dropdown.
        print("  - Selecionando 'MUNICIPIO DE RIBEIRAO DAS NEVES'...")
        campo_municipio = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen3"))
        )
        campo_municipio.click()
        time.sleep(1)

        # Selecionar a opção diretamente
        opcao_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'MUNICIPIO DE RIBEIRAO DAS NEVES')]"))
        )
        opcao_municipio.click()
        time.sleep(1)

        # 5. Alterar "Data específica" para "Primeiro dia do mês" (ID: select2-chosen-6)
        print("  - Selecionando 'Primeiro dia do mês'...")
        dropdown_data_inicio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-6']/parent::a"))
        )
        dropdown_data_inicio.click()
        time.sleep(1)
        
        opcao_primeiro_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Primeiro dia do mês')]"))
        )
        opcao_primeiro_dia.click()
        time.sleep(1)
        
        # 6. Alterar "Data específica" para "Último dia do mês" (ID: select2-chosen-49)
        print("  - Selecionando 'Último dia do mês'...")
        dropdown_data_fim = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-8']/parent::a"))
        )
        dropdown_data_fim.click()
        time.sleep(1)
        
        opcao_ultimo_dia = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select2-result-label') and contains(text(), 'Último dia do mês')]"))
        )
        opcao_ultimo_dia.click()
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
        
        # 2. Selecionar "MUNICIPIO DE RIBEIRAO DAS NEVES" (ID: select2-chosen-2)
        print("  - Selecionando 'MUNICIPIO DE RIBEIRAO DAS NEVES'...")
        dropdown_municipio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-2']/parent::a"))
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-4']/parent::a"))
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
            EC.element_to_be_clickable((By.XPATH, "//span[@id='select2-chosen-6']/parent::a"))
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


def baixar_arquivos(navegador, wait, file_converter, min_arquivos=10, max_tentativas=2):
    """
    Função para baixar todos os arquivos do Gerenciador de extensões
    Navega pelo gerenciador, baixa arquivos e implementa retry se necessário

    Args:
        navegador: Instância do WebDriver
        wait: Instância do WebDriverWait
        file_converter: Instância do FileConverter
        min_arquivos: Número mínimo de arquivos únicos esperados
        max_tentativas: Número máximo de tentativas

    Returns:
        bool: True se conseguiu baixar o mínimo de arquivos
    """
    try:
        print("\n" + "="*60)
        print("PROCESSO DE DOWNLOAD DE ARQUIVOS")
        print("="*60)

        tentativa = 1

        while tentativa <= max_tentativas:
            print(f"\n--- Tentativa {tentativa}/{max_tentativas} ---")

            # Limpar pasta temp antes de começar
            if tentativa == 1:
                file_converter.limpar_pasta_temp()

            # 1. Abrir Gerenciador de extensões
            print("\n  - Abrindo Gerenciador de extensões...")
            try:
                gerenciador_link = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//a[@data-ng-click='executandoCtrl.abrirAdmExtensoes()' and contains(@title, 'execuções')]"
                    ))
                )
                gerenciador_link.click()
                time.sleep(3)  # Aguarda carregamento
            except TimeoutException:
                print("  ✗ Não foi possível abrir o Gerenciador de extensões")
                tentativa += 1
                continue

            arquivos_baixados = 0
            paginas_processadas = 0
            max_paginas = 10  # Limite de segurança

            # 2. Navegar pelas páginas e baixar arquivos
            while paginas_processadas < max_paginas:
                print(f"\n  - Processando página {paginas_processadas + 1}...")

                # Atualizar andamento
                try:
                    botao_atualizar = wait.until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//button[@data-ng-click='vm.carregarMinhasExecucoes()' and contains(., 'Atualizar andamento')]"
                        ))
                    )
                    botao_atualizar.click()
                    time.sleep(2)
                except TimeoutException:
                    print("    ⚠ Botão de atualizar não encontrado")

                # Baixar arquivos "Resultado" na página atual
                try:
                    botoes_download = navegador.find_elements(
                        By.XPATH,
                        "//button[@data-ng-click='vm.downloadResultado(execucao)' and contains(., 'Resultado')]"
                    )

                    if botoes_download:
                        print(f"    - {len(botoes_download)} arquivos encontrados")
                        for i, botao in enumerate(botoes_download, 1):
                            try:
                                if botao.is_enabled():
                                    botao.click()
                                    arquivos_baixados += 1
                                    print(f"      ✓ Download {i}/{len(botoes_download)} iniciado")
                                    time.sleep(1)
                                else:
                                    print(f"      ⚠ Download {i}/{len(botoes_download)} ainda não disponível")
                            except Exception as e:
                                print(f"      ✗ Erro ao baixar arquivo {i}: {e}")
                    else:
                        print("    - Nenhum arquivo disponível nesta página")

                except Exception as e:
                    print(f"    ✗ Erro ao buscar arquivos: {e}")

                # Tentar ir para próxima página
                try:
                    botao_proxima = navegador.find_element(
                        By.XPATH,
                        "//button[@data-ng-click='vm.nextPage()' and contains(., 'Próxima')]"
                    )

                    if botao_proxima.is_enabled() and "disabled" not in botao_proxima.get_attribute("class"):
                        botao_proxima.click()
                        time.sleep(2)
                        paginas_processadas += 1
                    else:
                        print("\n    - Fim da paginação")
                        break

                except Exception:
                    print("\n    - Não há mais páginas")
                    break

            # 3. Processar downloads completados
            sucesso = False
            if arquivos_baixados > 0:
                print(f"\n  - Aguardando conclusão de {arquivos_baixados} downloads...")
                if file_converter.aguardar_downloads_completos(timeout=60):
                    print("    ✓ Downloads concluídos")
                    sucesso = True
                else:
                    print("    ⚠ Alguns downloads podem não ter sido concluídos")
                    sucesso = True  # Continua mesmo assim
            else:
                print("\n  ⚠ Nenhum arquivo foi baixado")

            if sucesso:
                # Contar arquivos únicos
                arquivos_unicos = file_converter.contar_arquivos_unicos_temp()
                print(f"\n  - Total de arquivos únicos: {arquivos_unicos}")

                if arquivos_unicos >= min_arquivos:
                    print(f"  ✓ Objetivo alcançado: {arquivos_unicos}/{min_arquivos} arquivos")

                    # Mover arquivos únicos para pasta raw
                    print("\n--- Movendo arquivos para processamento ---")
                    movidos = file_converter.mover_unicos_temp_para_raw()

                    if movidos > 0:
                        # Converter arquivos XLS para XLSX
                        print("\n--- Convertendo arquivos para XLSX ---")
                        total, convertidos = file_converter.converter_todos_raw()

                        if convertidos > 0:
                            print(f"\n✓ Processo completo: {convertidos} arquivos convertidos")
                            return True
                        else:
                            print("\n⚠ Nenhum arquivo foi convertido")
                    else:
                        print("\n⚠ Nenhum arquivo foi movido para processamento")

                else:
                    print(f"  ⚠ Apenas {arquivos_unicos}/{min_arquivos} arquivos únicos")

                    if tentativa < max_tentativas:
                        print(f"\n  - Aguardando 300 segundos antes da próxima tentativa...")
                        print("    (Aguardando sistema gerar mais relatórios)")

                        # Mostrar progresso a cada 30 segundos
                        for i in range(10):
                            time.sleep(30)
                            tempo_restante = 300 - (i + 1) * 30
                            if tempo_restante > 0:
                                print(f"    ... {tempo_restante} segundos restantes")

                        # Voltar para Relatórios Favoritos antes da próxima tentativa
                        print("\n  - Retornando aos Relatórios Favoritos...")
                        try:
                            navegador.back()  # Voltar da página do gerenciador
                            time.sleep(2)
                        except:
                            pass

            tentativa += 1

        print(f"\n✗ Não foi possível baixar {min_arquivos} arquivos únicos após {max_tentativas} tentativas")

        # Mesmo falhando, tenta processar o que conseguiu
        arquivos_unicos = file_converter.contar_arquivos_unicos_temp()
        if arquivos_unicos > 0:
            print(f"\n  - Processando {arquivos_unicos} arquivos disponíveis...")
            movidos = file_converter.mover_unicos_temp_para_raw()
            if movidos > 0:
                total, convertidos = file_converter.converter_todos_raw()
                if convertidos > 0:
                    print(f"  ✓ {convertidos} arquivos convertidos com sucesso")
                    return True

        return False

    except Exception as e:
        print(f"\n✗ Erro no processo de download: {e}")
        return False


# end