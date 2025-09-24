#!/usr/bin/env python3
"""
ProcessadorParalelo - Gerencia execução paralela de múltiplas instâncias do bot
"""

import os
import sys
import subprocess
import threading
import concurrent.futures
from typing import List, Dict, Optional
from datetime import datetime

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.classes.city_splitter import CitySplitter
from src.classes.date_calculator import DateCalculator
from src.classes.file.file_manager import FileManager
from src.classes.config import ARQUIVOS_CONFIG


class ProcessadorParalelo:
    """
    Gerencia a execução paralela do bot BB DAF
    Divide as cidades entre múltiplas instâncias e coordena a execução
    """
    
    def __init__(self):
        """Inicializa o processador paralelo"""
        self.city_splitter = CitySplitter()
        self.date_calculator = DateCalculator()
        self.processos = []
        self.resultados = []
        self._cancelado = False
        self.bots_ativos = []  # Lista para rastrear todas as instâncias de bot ativas
        self.executor = None   # Referência ao executor atual
    
    def executar_paralelo_subprocess(self, num_instancias: int, 
                                    data_inicial: str = None, 
                                    data_final: str = None) -> Dict:
        """
        Executa processamento paralelo usando subprocessos
        Útil quando executando via linha de comando
        
        Args:
            num_instancias: Número de instâncias paralelas (máximo 5)
            data_inicial: Data inicial ou None para calcular
            data_final: Data final ou None para calcular
            
        Returns:
            dict: Resultados consolidados
        """
        try:
            # Limita a 5 instâncias
            if num_instancias > 5:
                num_instancias = 5
                print(f"Número de instâncias limitado a 5")
            # Prepara divisão de cidades
            resultado_divisao = self.city_splitter.dividir_cidades(num_instancias)
            
            if not resultado_divisao.get('sucesso'):
                return {'sucesso': False, 'erro': resultado_divisao.get('erro')}
            
            # Calcula datas se necessário
            if data_inicial is None or data_final is None:
                data_inicial, data_final = self.date_calculator.obter_datas_formatadas()
            
            arquivos_criados = resultado_divisao['arquivos_criados']
            self.processos = []
            
            # Inicia todos os processos
            for arquivo_info in arquivos_criados:
                cmd = [
                    sys.executable,
                    os.path.join(os.path.dirname(__file__), '..', 'run_instance.py'),
                    arquivo_info['arquivo'],
                    data_inicial,
                    data_final
                ]
                
                processo = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.processos.append({
                    'processo': processo,
                    'instancia': arquivo_info['instancia'],
                    'arquivo': arquivo_info['arquivo'],
                    'num_cidades': arquivo_info['num_cidades']
                })
                
                print(f"Instância {arquivo_info['instancia']}: {arquivo_info['num_cidades']} cidades")
            
            # Aguarda conclusão e coleta resultados
            resultados = []
            for proc_info in self.processos:
                stdout, stderr = proc_info['processo'].communicate()
                
                resultados.append({
                    'instancia': proc_info['instancia'],
                    'returncode': proc_info['processo'].returncode,
                    'stdout': stdout,
                    'stderr': stderr,
                    'num_cidades': proc_info['num_cidades']
                })
                
                # Remove arquivo temporário
                try:
                    os.remove(proc_info['arquivo'])
                except:
                    pass
            
            # Consolida resultados
            return self._consolidar_resultados(resultados)
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
    
    def executar_paralelo_threads(self, num_instancias: int,
                                 data_inicial: str = None,
                                 data_final: str = None) -> Dict:
        """
        Executa processamento paralelo usando threads
        Útil quando executando em ambiente Python direto
        
        Args:
            num_instancias: Número de instâncias paralelas (máximo 5)
            data_inicial: Data inicial ou None para calcular
            data_final: Data final ou None para calcular
            
        Returns:
            dict: Resultados consolidados
        """
        try:
            # Limita a 5 instâncias
            if num_instancias > 5:
                num_instancias = 5
                print(f"Número de instâncias limitado a 5")
            from bots.bot_bbdaf import BotBBDAF
            from classes.data_extractor import DataExtractor
            
            # Prepara divisão de cidades
            resultado_divisao = self.city_splitter.dividir_cidades(num_instancias)
            
            if not resultado_divisao.get('sucesso'):
                return {'sucesso': False, 'erro': resultado_divisao.get('erro')}
            
            # Calcula datas se necessário
            if data_inicial is None or data_final is None:
                data_inicial, data_final = self.date_calculator.obter_datas_formatadas()
            
            arquivos_criados = resultado_divisao['arquivos_criados']
            
            # Executa em threads paralelas
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_instancias)
            try:
                futures = []
                
                for arquivo_info in arquivos_criados:
                    # Cria nova instância do bot para cada thread
                    bot = BotBBDAF()
                    bot.configurar_extrator_dados(DataExtractor("bbdaf"))
                    self.bots_ativos.append(bot)  # Registra bot ativo
                    
                    future = self.executor.submit(
                        self._executar_bot_thread,
                        bot,
                        arquivo_info,
                        data_inicial,
                        data_final
                    )
                    futures.append((future, arquivo_info))
                
                # Coleta resultados
                resultados = []
                for future, arquivo_info in futures:
                    if self._cancelado:
                        self.executor.shutdown(wait=False, cancel_futures=True)
                        return {'sucesso': False, 'erro': 'Cancelado pelo usuário'}
                    
                    resultado = future.result()
                    resultado['instancia'] = arquivo_info['instancia']
                    resultado['num_cidades'] = arquivo_info['num_cidades']
                    resultados.append(resultado)
            finally:
                if self.executor:
                    self.executor.shutdown(wait=True)
                    self.executor = None
                self.bots_ativos.clear()  # Limpa lista de bots
            
            # Consolida resultados
            return self._consolidar_resultados(resultados)
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
    
    def _executar_bot_thread(self, bot, arquivo_info, data_inicial, data_final):
        """
        Executa uma instância do bot em thread
        
        Args:
            bot: Instância do BotBBDAF
            arquivo_info: Informações do arquivo de cidades
            data_inicial: Data inicial
            data_final: Data final
            
        Returns:
            dict: Resultado da execução
        """
        try:
            print(f"Instância {arquivo_info['instancia']}: Iniciando processamento...")
            
            resultado = bot.executar_completo(
                arquivo_cidades=arquivo_info['arquivo'],
                data_inicial=data_inicial,
                data_final=data_final
            )
            
            # Remove arquivo temporário
            try:
                os.remove(arquivo_info['arquivo'])
            except:
                pass
            
            return resultado
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
    
    def _consolidar_resultados(self, resultados: List[Dict]) -> Dict:
        """
        Consolida resultados de múltiplas instâncias
        
        Args:
            resultados: Lista de resultados das instâncias
            
        Returns:
            dict: Resultados consolidados
        """
        total_cidades = 0
        total_sucessos = 0
        total_erros = 0
        instancias_sucesso = 0
        instancias_erro = 0
        
        for resultado in resultados:
            if resultado.get('sucesso') or resultado.get('returncode') == 0:
                instancias_sucesso += 1
                # Tenta extrair estatísticas
                if 'estatisticas' in resultado:
                    stats = resultado['estatisticas']
                    total_cidades += stats.get('total', 0)
                    total_sucessos += stats.get('sucessos', 0)
                    total_erros += stats.get('erros', 0)
                elif 'stdout' in resultado:
                    # Tenta parsear do stdout
                    self._parsear_estatisticas_stdout(resultado['stdout'])
            else:
                instancias_erro += 1
        
        taxa_sucesso = (total_sucessos / total_cidades * 100) if total_cidades > 0 else 0
        
        return {
            'sucesso': True,
            'instancias': {
                'total': len(resultados),
                'sucesso': instancias_sucesso,
                'erro': instancias_erro
            },
            'estatisticas': {
                'total': total_cidades,
                'sucessos': total_sucessos,
                'erros': total_erros,
                'taxa_sucesso': taxa_sucesso
            },
            'detalhes': resultados
        }
    
    def _parsear_estatisticas_stdout(self, stdout: str) -> Dict:
        """
        Extrai estatísticas do stdout do processo
        
        Args:
            stdout: Saída do processo
            
        Returns:
            dict: Estatísticas extraídas
        """
        stats = {'total': 0, 'sucessos': 0, 'erros': 0}
        
        # Procura por padrões conhecidos no stdout
        for linha in stdout.split('\n'):
            if 'Total:' in linha:
                try:
                    stats['total'] = int(linha.split(':')[1].split()[0])
                except:
                    pass
            elif 'Sucessos:' in linha:
                try:
                    stats['sucessos'] = int(linha.split(':')[1].split()[0])
                except:
                    pass
            elif 'Erros:' in linha:
                try:
                    stats['erros'] = int(linha.split(':')[1].split()[0])
                except:
                    pass
        
        return stats
    
    def executar_paralelo_fnde(self, bot_template, ano: str, num_instancias: int = 2) -> Dict:
        """
        Executa processamento paralelo do FNDE
        
        Args:
            bot_template: Instância template do BotFNDE
            ano: Ano para consulta
            num_instancias: Número de instâncias paralelas (máximo 5)
            
        Returns:
            Dict: Resultados consolidados
        """
        try:
            # Limita a 5 instâncias
            if num_instancias > 5:
                num_instancias = 5
                print(f"Número de instâncias limitado a 5")
            
            # Importa dinamicamente para evitar dependência circular
            from bots.bot_fnde import BotFNDE
            
            # Obtém lista de municípios e divide em lotes
            municipios = bot_template.obter_lista_municipios()
            lotes = self._dividir_municipios(municipios, num_instancias)
            
            print(f"Dividindo {len(municipios)} municípios em {len(lotes)} lotes paralelos")
            for i, lote in enumerate(lotes, 1):
                print(f"Lote {i}: {len(lote)} municípios")
            
            # Executa em threads paralelas
            resultados = []
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_instancias)
            try:
                futures = []
                
                for i, lote in enumerate(lotes, 1):
                    # Cria nova instância do bot para cada thread
                    bot = BotFNDE()
                    self.bots_ativos.append(bot)  # Registra bot ativo
                    
                    future = self.executor.submit(
                        self._executar_bot_fnde_thread,
                        bot,
                        lote,
                        ano,
                        i
                    )
                    futures.append((future, i, len(lote)))
                
                # Coleta resultados
                for future, instancia, num_municipios in futures:
                    if self._cancelado:
                        self.executor.shutdown(wait=False, cancel_futures=True)
                        return {'sucesso': False, 'erro': 'Cancelado pelo usuário'}
                    
                    resultado = future.result()
                    resultado['instancia'] = instancia
                    resultado['municipios_lote'] = num_municipios
                    resultados.append(resultado)
            finally:
                if self.executor:
                    self.executor.shutdown(wait=True)
                    self.executor = None
                self.bots_ativos.clear()  # Limpa lista de bots
            
            # Consolida estatísticas
            return self._consolidar_resultados_fnde(resultados)
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
    
    def _dividir_municipios(self, municipios: List[str], num_instancias: int) -> List[List[str]]:
        """
        Divide lista de municípios em lotes para processamento paralelo
        
        Args:
            municipios: Lista de municípios
            num_instancias: Número de instâncias paralelas
            
        Returns:
            List[List[str]]: Lista de lotes de municípios
        """
        import math
        
        total_municipios = len(municipios)
        municipios_por_instancia = math.ceil(total_municipios / num_instancias)
        
        lotes = []
        for i in range(num_instancias):
            inicio = i * municipios_por_instancia
            fim = min(inicio + municipios_por_instancia, total_municipios)
            
            if inicio < total_municipios:
                lote = municipios[inicio:fim]
                lotes.append(lote)
        
        return lotes
    
    def _executar_bot_fnde_thread(self, bot, lote_municipios: List[str], ano: str, instancia: int) -> Dict:
        """
        Executa um lote de municípios em uma instância do bot FNDE
        
        Args:
            bot: Instância do BotFNDE
            lote_municipios: Lista de municípios para processar
            ano: Ano da consulta
            instancia: Número da instância
            
        Returns:
            Dict: Resultado do processamento do lote
        """
        try:
            print(f"Instância {instancia}: Iniciando processamento de {len(lote_municipios)} municípios...")
            
            # Verifica se foi cancelado antes de começar
            if self._cancelado:
                print(f"Instância {instancia}: Cancelada antes de iniciar")
                return {'sucesso': False, 'erro': 'Cancelado pelo usuário'}
            
            # Configura navegador
            if not bot.configurar_navegador():
                return {'sucesso': False, 'erro': 'Falha ao configurar navegador'}
            
            # Verifica cancelamento após configurar navegador
            if self._cancelado:
                print(f"Instância {instancia}: Cancelada após configurar navegador")
                bot.limpar_recursos()
                return {'sucesso': False, 'erro': 'Cancelado pelo usuário'}
            
            # Processa lote
            resultado = bot.processar_lote_municipios(ano, lote_municipios)
            
            return resultado
            
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
        finally:
            # Garante limpeza de recursos
            bot.limpar_recursos()
    
    def _consolidar_resultados_fnde(self, resultados: List[Dict]) -> Dict:
        """
        Consolida resultados de múltiplas instâncias FNDE
        
        Args:
            resultados: Lista de resultados das instâncias
            
        Returns:
            Dict: Resultados consolidados
        """
        total_municipios = 0
        total_sucessos = 0
        total_erros = 0
        instancias_sucesso = 0
        instancias_erro = 0
        municipios_processados = []
        municipios_erro = []
        
        for resultado in resultados:
            if resultado.get('sucesso'):
                instancias_sucesso += 1
                # Extrai estatísticas do resultado
                stats = resultado.get('estatisticas', {})
                total_municipios += stats.get('total', 0)
                total_sucessos += stats.get('sucessos', 0)
                total_erros += stats.get('erros', 0)
                municipios_processados.extend(stats.get('municipios_processados', []))
                municipios_erro.extend(stats.get('municipios_erro', []))
            else:
                instancias_erro += 1
        
        taxa_sucesso = (total_sucessos / total_municipios * 100) if total_municipios > 0 else 0
        
        return {
            'sucesso': True,
            'instancias': {
                'total': len(resultados),
                'sucesso': instancias_sucesso,
                'erro': instancias_erro
            },
            'estatisticas': {
                'total': total_municipios,
                'sucessos': total_sucessos,
                'erros': total_erros,
                'taxa_sucesso': taxa_sucesso,
                'municipios_processados': municipios_processados,
                'municipios_erro': municipios_erro
            },
            'detalhes': resultados
        }

    def cancelar(self):
        """Cancela a execução paralela em andamento"""
        print("Cancelando execução paralela - forçando fechamento de todos os bots...")
        self._cancelado = True
        
        # PRIMEIRO: Cancela TODOS os bots ativos forçadamente
        for bot in self.bots_ativos[:]:  # Cria cópia da lista para evitar modificação durante iteração
            try:
                if hasattr(bot, 'cancelar_forcado'):
                    bot.cancelar_forcado()  # Fecha todas as abas do Chrome
                else:
                    bot.cancelar()  # Fallback para método básico
            except Exception as e:
                print(f"Erro ao cancelar bot: {e}")
                continue
        
        # SEGUNDO: Força encerramento do executor de threads
        if self.executor:
            try:
                # Encerra imediatamente cancelando todas as futures
                self.executor.shutdown(wait=False, cancel_futures=True)
                print("Executor de threads cancelado")
            except Exception as e:
                print(f"Erro ao cancelar executor: {e}")
            self.executor = None
        
        # TERCEIRO: Termina todos os processos (modo subprocess)
        for proc_info in self.processos:
            try:
                processo = proc_info['processo']
                processo.terminate()
                
                # Aguarda um pouco e força encerramento se necessário
                try:
                    processo.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    processo.kill()
                    processo.wait()
                
                # Remove arquivo temporário
                try:
                    os.remove(proc_info['arquivo'])
                except:
                    pass
            except:
                pass
        
        # Limpa listas
        self.bots_ativos.clear()
        print("Cancelamento completo - todos os recursos foram liberados")


def main():
    """
    Função principal para execução via linha de comando
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Processador Paralelo BB DAF')
    parser.add_argument('--instancias', type=int, default=2,
                       help='Número de instâncias paralelas (máximo 5)')
    parser.add_argument('--data-inicial', type=str, default=None,
                       help='Data inicial (DD/MM/AAAA)')
    parser.add_argument('--data-final', type=str, default=None,
                       help='Data final (DD/MM/AAAA)')
    parser.add_argument('--modo', choices=['subprocess', 'threads'], 
                       default='subprocess',
                       help='Modo de execução paralela')
    
    args = parser.parse_args()
    
    # Valida número de instâncias
    if args.instancias > 5:
        print(f"Aviso: Número de instâncias limitado a 5 (solicitado: {args.instancias})")
        args.instancias = 5
    elif args.instancias < 1:
        print("Erro: Número de instâncias deve ser pelo menos 1")
        return 1
    
    processador = ProcessadorParalelo()
    
    print(f"Iniciando processamento paralelo com {args.instancias} instâncias...")
    
    if args.modo == 'subprocess':
        resultado = processador.executar_paralelo_subprocess(
            args.instancias,
            args.data_inicial,
            args.data_final
        )
    else:
        resultado = processador.executar_paralelo_threads(
            args.instancias,
            args.data_inicial,
            args.data_final
        )
    
    if resultado['sucesso']:
        print("\nProcessamento concluído com sucesso!")
        stats = resultado['estatisticas']
        print(f"Total: {stats['total']} cidades")
        print(f"Sucessos: {stats['sucessos']}")
        print(f"Erros: {stats['erros']}")
        print(f"Taxa de sucesso: {stats['taxa_sucesso']:.1f}%")
    else:
        print(f"\nErro no processamento: {resultado['erro']}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())