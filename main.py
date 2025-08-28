#!/usr/bin/env python3
"""
Script principal SIMPLIFICADO para automação FPM
Usa as classes diretamente sem AutomationCore intermediário

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
import os
from bots.web_scraping_bot import WebScrapingBot
from classes.data_extractor import DataExtractor
from classes.date_calculator import DateCalculator
from classes.file_manager import FileManager


def main():
    """
    Função principal SIMPLIFICADA que usa as classes diretamente
    """
    print("=" * 60)
    print("SISTEMA DE AUTOMAÇÃO WEB - ARRECADAÇÃO FEDERAL")
    print("=" * 60)
    
    try:
        # 1. Carrega cidades
        file_manager = FileManager()
        if not file_manager.verificar_arquivo_existe():
            print("Use a interface gráfica para selecionar cidades primeiro.")
            return 1
        
        cidades = file_manager.carregar_cidades()
        if not file_manager.validar_lista_cidades(cidades):
            return 1
        
        # 2. Carrega datas: primeiro verifica argumentos, senão calcula automaticamente
        if len(sys.argv) >= 3:
            data_inicial = sys.argv[1]
            data_final = sys.argv[2]
            print(f"Usando datas fornecidas: {data_inicial} até {data_final}")
        else:
            print("Calculando datas automaticamente...")
            date_calculator = DateCalculator()
            data_inicial, data_final = date_calculator.obter_datas_formatadas()
        
        # 3. Inicializa componentes
        data_extractor = DataExtractor()
        bot = WebScrapingBot()
        bot.configurar_extrator_dados(data_extractor)
        
        # 4. Configura navegador
        print("Configurando navegador...")
        if not bot.configurar_navegador():
            print("Falha na configuração do navegador Chrome")
            return 1
        
        # 5. Abre página inicial
        print("Abrindo página inicial...")
        if not bot.abrir_pagina_inicial():
            print("Falha ao carregar página inicial")
            bot.fechar_navegador()
            return 1
        
        # 6. Processa todas as cidades
        print(f"Processando {len(cidades)} cidades...")
        estatisticas = bot.processar_lista_cidades(cidades, data_inicial, data_final)
        
        # 7. Fecha navegador automaticamente
        print("Fechando navegador...")
        bot.fechar_navegador()
        
        # 8. Exibe estatísticas finais
        print(f"\nProcessamento concluído:")
        print(f"   Total: {estatisticas['total']} cidades")
        print(f"   Sucessos: {estatisticas['sucessos']}")
        print(f"   Erros: {estatisticas['erros']}")
        print(f"   Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
        
        # 9. Aguarda usuário
        input("\nPressione Enter para finalizar...")
        
        # 10. Retorna código baseado nos erros
        return 0 if estatisticas['erros'] == 0 else 1
        
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário")
        if 'bot' in locals():
            bot.fechar_navegador()
        return 130
    except Exception as e:
        print(f"Erro inesperado: {e}")
        if 'bot' in locals():
            bot.fechar_navegador()
        return 1


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
        print("Dependências ausentes encontradas:")
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
    print("Verificando dependências...")
    
    if not verificar_dependencias():
        sys.exit(1)
    
    print("Todas as dependências estão instaladas.")
    
    # Executa a função principal e sai com o código de retorno apropriado
    codigo_saida = main()
    sys.exit(codigo_saida) 