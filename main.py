#!/usr/bin/env python3
"""
Script principal para automação de web scraping do sistema de arrecadação federal
Utiliza programação orientada a objetos para organizar o código de forma modular

Funcionalidades:
- Carrega lista de cidades do arquivo listed_cities.txt (gerado pela GUI)
- Calcula datas automaticamente (atual e um mês anterior)
- Automatiza preenchimento de formulários web
- Processa múltiplas cidades em sequência
- EXTRAÇÃO AUTOMÁTICA DE DADOS: Extrai dados da tabela de resultados
- GERAÇÃO DE EXCEL: Salva dados extraídos em arquivos Excel organizados
- RELATÓRIO CONSOLIDADO: Gera relatório final com estatísticas
- Fornece estatísticas completas de processamento
"""

import sys
from classes.automation_core import AutomationCore


def main():
    """
    Função principal que coordena todo o processo de web scraping
    Versão refatorada usando AutomationCore centralizado
    """
    print("=" * 60)
    print("🚀 SISTEMA DE AUTOMAÇÃO WEB - ARRECADAÇÃO FEDERAL")
    print("=" * 60)
    
    # Inicializa núcleo de automação
    automation_core = AutomationCore()
    
    # Executa fluxo completo
    return automation_core.executar_fluxo_completo_terminal()


def verificar_dependencias():
    """
    Verifica se todas as dependências necessárias estão instaladas
    
    Returns:
        bool: True se todas as dependências estão instaladas, False caso contrário
    """
    dependencias_necessarias = [
        'selenium',
        'webdriver_manager',
        'dateutil',
        'bs4',  # BeautifulSoup
        'pandas',
        'openpyxl'
    ]
    
    dependencias_ausentes = []
    
    for dependencia in dependencias_necessarias:
        try:
            __import__(dependencia)
        except ImportError:
            dependencias_ausentes.append(dependencia)
    
    if dependencias_ausentes:
        print("❌ Dependências ausentes encontradas:")
        for dep in dependencias_ausentes:
            print(f"   - {dep}")
        print("\nInstale as dependências executando:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


if __name__ == "__main__":
    """
    Ponto de entrada do programa
    Verifica dependências e executa a função principal
    """
    print("🔍 Verificando dependências...")
    
    if not verificar_dependencias():
        sys.exit(1)
    
    print("✅ Todas as dependências estão instaladas.")
    
    # Executa a função principal e sai com o código de retorno apropriado
    codigo_saida = main()
    sys.exit(codigo_saida) 