#!/usr/bin/env python3
"""
Script para execução paralela de instâncias do sistema FPM
Aceita um arquivo de cidades específico como parâmetro

Uso: python main_parallel.py [arquivo_cidades]
"""

import sys
import os
from classes.web_scraping_bot import WebScrapingBot
from classes.data_extractor import DataExtractor
from classes.date_calculator import DateCalculator
from classes.file_manager import FileManager


def main():
    """
    Função principal para execução paralela
    """
    # Verifica se foi passado arquivo de cidades como parâmetro
    if len(sys.argv) > 1:
        arquivo_cidades = sys.argv[1]
    else:
        arquivo_cidades = "listed_cities.txt"
    
    # Identifica a instância pelo nome do arquivo
    instancia_id = "Principal"
    if "instancia_" in arquivo_cidades:
        try:
            instancia_id = f"Instancia {arquivo_cidades.split('_')[-1].split('.')[0]}"
        except:
            pass
    
    print("=" * 60)
    print(f"SISTEMA FPM - {instancia_id.upper()}")
    print("=" * 60)
    
    try:
        # 1. Carrega cidades do arquivo específico
        file_manager = FileManager(arquivo_cidades)
        if not file_manager.verificar_arquivo_existe():
            print(f"Arquivo {arquivo_cidades} não encontrado.")
            return 1
        
        cidades = file_manager.carregar_cidades()
        if not file_manager.validar_lista_cidades(cidades):
            return 1
        
        print(f"{instancia_id}: {len(cidades)} cidades a processar")
        
        # 2. Calcula datas
        date_calculator = DateCalculator()
        data_inicial, data_final = date_calculator.obter_datas_formatadas()
        
        # 3. Inicializa componentes
        data_extractor = DataExtractor()
        bot = WebScrapingBot()
        bot.configurar_extrator_dados(data_extractor)
        
        # 4. Configura navegador
        print(f"{instancia_id}: Configurando navegador...")
        if not bot.configurar_navegador():
            print(f"{instancia_id}: Falha na configuração do navegador Chrome")
            return 1
        
        # 5. Abre página inicial
        print(f"{instancia_id}: Abrindo página inicial...")
        if not bot.abrir_pagina_inicial():
            print(f"{instancia_id}: Falha ao carregar página inicial")
            bot.fechar_navegador()
            return 1
        
        # 6. Processa todas as cidades
        print(f"{instancia_id}: Processando {len(cidades)} cidades...")
        estatisticas = bot.processar_lista_cidades(cidades, data_inicial, data_final)
        
        # 7. Fecha navegador automaticamente
        print(f"{instancia_id}: Fechando navegador...")
        bot.fechar_navegador()
        
        # 8. Exibe estatísticas finais
        print(f"\n{instancia_id} - Processamento concluído:")
        print(f"   Total: {estatisticas['total']} cidades")
        print(f"   Sucessos: {estatisticas['sucessos']}")
        print(f"   Erros: {estatisticas['erros']}")
        print(f"   Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
        
        # 9. Retorna código baseado nos erros
        return 0 if estatisticas['erros'] == 0 else 1
        
    except KeyboardInterrupt:
        print(f"\n{instancia_id}: Interrompido pelo usuário")
        if 'bot' in locals():
            bot.fechar_navegador()
        return 130
    except Exception as e:
        print(f"{instancia_id}: Erro inesperado: {e}")
        if 'bot' in locals():
            bot.fechar_navegador()
        return 1


if __name__ == "__main__":
    """
    Ponto de entrada do programa
    """
    codigo_saida = main()
    sys.exit(codigo_saida) 