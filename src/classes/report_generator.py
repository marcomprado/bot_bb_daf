#!/usr/bin/env python3
"""
Gerador de relatórios TXT para processamento de bots
Fornece utilitários para criação, atualização e geração de relatórios de estatísticas
"""

import os
from datetime import datetime
from typing import Dict, Optional


class ReportGenerator:
    """
    Gerador de relatórios padronizados para processamento de municípios/dados por bots

    Fornece métodos para:
    - Criar e atualizar estruturas de estatísticas
    - Calcular taxas de sucesso
    - Imprimir estatísticas no console
    - Gerar relatórios TXT formatados
    """

    def __init__(self, output_dir: str, report_prefix: str = "RELATORIO"):
        """
        Inicializa gerador de relatórios

        Args:
            output_dir: Diretório onde salvar relatórios
            report_prefix: Prefixo para nome do arquivo (ex: "RELATORIO_CONSFNS")
        """
        self.output_dir = output_dir
        self.report_prefix = report_prefix

    @staticmethod
    def criar_estatisticas(total: int) -> Dict:
        """Cria estrutura de estatísticas para processamento"""
        return {
            'total': total,
            'sucessos': 0,
            'erros': 0,
            'municipios_processados': [],
            'municipios_erro': []
        }

    @staticmethod
    def atualizar_estatisticas(estatisticas: Dict, resultado: Dict):
        """Atualiza estatísticas com resultado do processamento de um município"""
        if resultado['sucesso']:
            estatisticas['sucessos'] += 1
            estatisticas['municipios_processados'].append(resultado['municipio'])
        else:
            estatisticas['erros'] += 1
            estatisticas['municipios_erro'].append({
                'municipio': resultado['municipio'],
                'erro': resultado['erro']
            })

    @staticmethod
    def calcular_taxa_sucesso(estatisticas: Dict):
        """Calcula e adiciona taxa de sucesso às estatísticas"""
        if estatisticas['total'] > 0:
            estatisticas['taxa_sucesso'] = (estatisticas['sucessos'] / estatisticas['total']) * 100
        else:
            estatisticas['taxa_sucesso'] = 0

    @staticmethod
    def imprimir_estatisticas(estatisticas: Dict, titulo: str = "PROCESSAMENTO CONCLUÍDO"):
        """Imprime resumo das estatísticas de processamento"""
        print(f"\n=== {titulo} ===")
        print(f"Total: {estatisticas['total']}")
        print(f"Sucessos: {estatisticas['sucessos']}")
        print(f"Erros: {estatisticas['erros']}")
        print(f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")

    def gerar_relatorio(
        self,
        estatisticas: Dict,
        titulo: str = "RELATÓRIO DE PROCESSAMENTO",
        incluir_municipios_sucesso: bool = False
    ) -> Optional[str]:
        """
        Gera relatório TXT com estatísticas do processamento

        Args:
            estatisticas: Dict com estatísticas (total, sucessos, erros, taxa_sucesso, municipios_erro)
            titulo: Título do relatório
            incluir_municipios_sucesso: Se True, inclui lista de municípios processados com sucesso

        Returns:
            str: Caminho do arquivo de relatório gerado, ou None se erro
        """
        try:
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            nome_arquivo = f"{self.report_prefix}_{data_hoje}.txt"
            caminho_relatorio = os.path.join(self.output_dir, nome_arquivo)
            data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            linhas = []
            linhas.append("=" * 60)
            linhas.append(titulo)
            linhas.append("=" * 60)
            linhas.append("")
            linhas.append(f"Data: {data_hora_atual}")
            linhas.append("")
            linhas.append("ESTATÍSTICAS GERAIS:")
            linhas.append(f"- Total de municípios: {estatisticas['total']}")
            linhas.append(f"- Sucessos: {estatisticas['sucessos']}")
            linhas.append(f"- Erros: {estatisticas['erros']}")
            linhas.append(f"- Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
            linhas.append("")

            if incluir_municipios_sucesso and estatisticas.get('municipios_processados'):
                linhas.append("=" * 60)
                linhas.append(f"MUNICÍPIOS PROCESSADOS COM SUCESSO ({len(estatisticas['municipios_processados'])}):")
                linhas.append("=" * 60)
                linhas.append("")
                for i, municipio in enumerate(estatisticas['municipios_processados'], 1):
                    linhas.append(f"{i}. {municipio}")
                linhas.append("")

            if estatisticas['erros'] > 0 and estatisticas.get('municipios_erro'):
                linhas.append("=" * 60)
                linhas.append(f"MUNICÍPIOS COM ERRO ({len(estatisticas['municipios_erro'])}):")
                linhas.append("=" * 60)
                linhas.append("")
                for i, erro_info in enumerate(estatisticas['municipios_erro'], 1):
                    municipio = erro_info.get('municipio', 'Desconhecido')
                    erro = erro_info.get('erro', 'Erro não especificado')
                    linhas.append(f"{i}. {municipio}")
                    linhas.append(f"   Erro: {erro}")
                    linhas.append("")
            else:
                linhas.append("=" * 60)
                linhas.append("NENHUM ERRO REGISTRADO - EXECUÇÃO 100% SUCESSO!")
                linhas.append("=" * 60)
                linhas.append("")

            linhas.append("=" * 60)
            linhas.append("FIM DO RELATÓRIO")
            linhas.append("=" * 60)

            with open(caminho_relatorio, 'w', encoding='utf-8') as arquivo:
                arquivo.write('\n'.join(linhas))

            print(f"📄 Relatório gerado: {caminho_relatorio}")
            return caminho_relatorio

        except Exception as e:
            print(f"Aviso: Erro ao gerar relatório - {e}")
            return None
