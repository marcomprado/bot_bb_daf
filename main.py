#!/usr/bin/env python3
"""
Script principal para automação de web scraping do sistema de arrecadação federal
Utiliza programação orientada a objetos para organizar o código de forma modular

Funcionalidades:
- Carrega lista de cidades do arquivo cidades.txt
- Calcula datas automaticamente (atual e um mês anterior)
- Automatiza preenchimento de formulários web
- Processa múltiplas cidades em sequência
- EXTRAÇÃO AUTOMÁTICA DE DADOS: Extrai dados da tabela de resultados
- GERAÇÃO DE EXCEL: Salva dados extraídos em arquivos Excel organizados
- RELATÓRIO CONSOLIDADO: Gera relatório final com estatísticas
- Fornece estatísticas completas de processamento
"""

import sys
from classes.file_manager import FileManager
from classes.date_calculator import DateCalculator
from classes.web_scraping_bot import WebScrapingBot
from classes.data_extractor import DataExtractor


def main():
    """
    Função principal que coordena todo o processo de web scraping
    """
    print("=" * 60)
    print("🚀 SISTEMA DE AUTOMAÇÃO WEB - ARRECADAÇÃO FEDERAL")
    print("=" * 60)
    
    try:
        # ETAPA 1: Inicialização dos componentes
        print("\n📋 ETAPA 1: Inicializando componentes...")
        
        # Inicializa o gerenciador de arquivos
        file_manager = FileManager()
        
        # Inicializa o calculador de datas
        date_calculator = DateCalculator()
        
        # Inicializa o extrator de dados
        data_extractor = DataExtractor()
        
        # Inicializa o bot de web scraping
        bot = WebScrapingBot()
        
        # Configura o extrator de dados no bot
        bot.configurar_extrator_dados(data_extractor)
        
        # ETAPA 2: Carregamento e validação dos dados
        print("\n📁 ETAPA 2: Carregando dados...")
        
        # Carrega a lista de cidades do arquivo
        cidades = file_manager.carregar_cidades()
        
        # Valida se há cidades para processar
        if not file_manager.validar_lista_cidades(cidades):
            print("❌ Encerrando programa: Nenhuma cidade válida encontrada.")
            return 1
        
        # Calcula as datas para a consulta
        data_inicial, data_final = date_calculator.obter_datas_formatadas()
        
        # ETAPA 3: Configuração do navegador
        print("\n🌐 ETAPA 3: Configurando navegador...")
        
        # Configura e inicializa o navegador
        if not bot.configurar_navegador():
            print("❌ Encerrando programa: Falha na configuração do navegador.")
            return 1
        
        # Abre a página inicial do sistema
        if not bot.abrir_pagina_inicial():
            print("❌ Encerrando programa: Falha ao carregar página inicial.")
            bot.fechar_navegador()
            return 1
        
        # ETAPA 4: Processamento das cidades
        print("\n🏙️ ETAPA 4: Processando cidades...")
        
        # Processa todas as cidades da lista
        estatisticas = bot.processar_lista_cidades(cidades, data_inicial, data_final)
        
        # ETAPA 5: Finalização
        print("\n✅ ETAPA 5: Processamento concluído!")
        
        # Aguarda o usuário verificar os resultados
        bot.aguardar_usuario()
        
        # Fecha o navegador
        bot.fechar_navegador()
        
        # Retorna código de sucesso se todas as cidades foram processadas com êxito
        if estatisticas['erros'] == 0:
            print("🎉 Todos os processamentos foram bem-sucedidos!")
            return 0
        else:
            print(f"⚠️ Processamento concluído com {estatisticas['erros']} erro(s).")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Processamento interrompido pelo usuário.")
        if 'bot' in locals() and bot.navegador:
            bot.fechar_navegador()
        return 130  # Código padrão para interrupção por Ctrl+C
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        if 'bot' in locals() and bot.navegador:
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