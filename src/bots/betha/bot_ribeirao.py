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
        # # Anexo 03 (Implemented)
        # # Anexo 08
        # # Anexo IV
        # # Anexo VII
        # # Balancete Bancario
        # # Balancete da Despesa
        # # Balancete da Receita
        # # Balancete dos Recursos
        # # Extrato da Receita
        # # Relacao de Empenhos - CMM
        # # Relacao de Pagamentos Efetuados 
        # # Relacao geral de liquidacoes por periodo
        
        
def executar_script_ribeirao(navegador, wait):
    """
    Executa o script especifico para Ribeirao das Neves
    
    Este script e executado apos chegar em "Relatorios Favoritos"
    e contem a logica especifica para este municipio
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        
    Returns:
        bool: True se executado com sucesso
    """
    try:
        print("\n" + "="*60)
        print("SCRIPT RIBEIRAO DAS NEVES - PROCESSANDO RELATORIOS")
        print("="*60)
        
        # Processar Anexo 03
        if not _processar_anexo_03(navegador, wait):
            print("⚠ Falha ao processar Anexo 03")
            return False
        
        
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
        time.sleep(2)
        
        # 2. Alterar "Sim" para "Não"
        print("  - Selecionando 'Não'...")
        dropdown_sim = wait.until(
            EC.element_to_be_clickable((By.ID, "select2-chosen-281"))
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
        campo_municipio = wait.until(
            EC.element_to_be_clickable((By.ID, "s2id_autogen283"))
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
        radio_xls = wait.until(
            EC.element_to_be_clickable((By.ID, "rb-export-as-xls"))
        )
        radio_xls.click()
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