#!/usr/bin/env python3
"""
Script auxiliar para executar uma instância do bot
Usado pelo ProcessadorParalelo para execução via subprocess
"""

import sys
from bots.bot_bbdaf import BotBBDAF
from classes.data_extractor import DataExtractor

def main():
    """Executa uma instância do bot com os parâmetros fornecidos"""
    if len(sys.argv) < 4:
        print("Uso: run_instance.py <arquivo_cidades> <data_inicial> <data_final>")
        return 1
    
    arquivo_cidades = sys.argv[1]
    data_inicial = sys.argv[2]
    data_final = sys.argv[3]
    
    # Inicializa e executa o bot
    bot = BotBBDAF()
    bot.configurar_extrator_dados(DataExtractor())
    
    resultado = bot.executar_completo(
        arquivo_cidades=arquivo_cidades,
        data_inicial=data_inicial,
        data_final=data_final
    )
    
    if resultado['sucesso']:
        stats = resultado['estatisticas']
        print(f"\nProcessamento concluído:")
        print(f"   Total: {stats['total']} cidades")
        print(f"   Sucessos: {stats['sucessos']}")
        print(f"   Erros: {stats['erros']}")
        print(f"   Taxa de sucesso: {stats['taxa_sucesso']:.1f}%")
        return 0
    else:
        print(f"Erro: {resultado['erro']}")
        return 1

if __name__ == "__main__":
    sys.exit(main())