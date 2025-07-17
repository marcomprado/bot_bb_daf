"""
Núcleo centralizado de automação - elimina duplicação de código
Classe base reutilizada tanto pela versão terminal quanto pela GUI
"""

import sys
import os
from datetime import datetime
from typing import List, Callable, Dict, Any, Optional

from .web_scraping_bot import WebScrapingBot
from .data_extractor import DataExtractor
from .date_calculator import DateCalculator
from .file_manager import FileManager


class AutomationCore:
    """
    Núcleo centralizado da automação FPM
    
    Elimina duplicação entre versão terminal e GUI
    Classe base reutilizada por ambas as interfaces
    """
    
    def __init__(self, callback_status: Optional[Callable] = None):
        """
        Inicializa núcleo de automação
        
        Args:
            callback_status: Função opcional para logs (GUI)
        """
        self.callback_status = callback_status
        
        # Componentes principais
        self.bot = None
        self.data_extractor = None
        self.file_manager = None
        self.date_calculator = None
        
        # Estado
        self.navegador_inicializado = False
        self.resultados_processamento = []
        self.processo_cancelado = False
    
    def _log(self, mensagem: str):
        """Log com callback opcional"""
        if self.callback_status:
            self.callback_status(mensagem)
    
    def inicializar_componentes(self) -> Dict[str, Any]:
        """
        Inicializa todos os componentes necessários
        
        Returns:
            dict: Resultado da inicialização
        """
        try:
            # Inicializa componentes
            self.file_manager = FileManager()
            self.date_calculator = DateCalculator()
            self.data_extractor = DataExtractor()
            self.bot = WebScrapingBot()
            
            # Configura extrator no bot
            self.bot.configurar_extrator_dados(self.data_extractor)
            
            return {'sucesso': True}
            
        except Exception as e:
            erro = f"Erro ao inicializar componentes: {str(e)}"
            self._log(f"❌ {erro}")
            return {'sucesso': False, 'erro': erro}
    
    def configurar_navegador(self) -> Dict[str, Any]:
        """
        Configura navegador uma única vez
        
        Returns:
            dict: Resultado da configuração
        """
        try:
            if not self.bot.configurar_navegador():
                return {
                    'sucesso': False,
                    'erro': 'Falha na configuração do navegador Chrome'
                }
            
            self.navegador_inicializado = True
            return {'sucesso': True}
            
        except Exception as e:
            erro = f"Erro ao configurar navegador: {str(e)}"
            self._log(f"❌ {erro}")
            return {'sucesso': False, 'erro': erro}
    
    def abrir_pagina_inicial(self) -> Dict[str, Any]:
        """
        Abre página inicial do sistema
        
        Returns:
            dict: Resultado da abertura
        """
        try:
            if not self.bot.abrir_pagina_inicial():
                return {
                    'sucesso': False,
                    'erro': 'Falha ao carregar página inicial'
                }
            
            return {'sucesso': True}
            
        except Exception as e:
            erro = f"Erro ao abrir página: {str(e)}"
            self._log(f"❌ {erro}")
            return {'sucesso': False, 'erro': erro}
    
    def carregar_cidades_do_arquivo(self) -> Dict[str, Any]:
        """
        Carrega cidades do arquivo listed_cities.txt (arquivo dinâmico gerado pela GUI)
        
        Returns:
            dict: Resultado com lista de cidades
        """
        try:
            cidades = self.file_manager.carregar_cidades()
            
            if not self.file_manager.validar_lista_cidades(cidades):
                return {
                    'sucesso': False,
                    'erro': 'Nenhuma cidade válida encontrada'
                }
            
            return {
                'sucesso': True,
                'cidades': cidades
            }
            
        except Exception as e:
            erro = f"Erro ao carregar cidades: {str(e)}"
            self._log(f"❌ {erro}")
            return {'sucesso': False, 'erro': erro}
    
    def calcular_datas_padrao(self) -> tuple:
        """
        Calcula datas padrão (último mês)
        
        Returns:
            tuple: (data_inicial, data_final) formatadas
        """
        return self.date_calculator.obter_datas_formatadas()
    
    def processar_cidade_individual(self, cidade: str, data_inicial: str, data_final: str) -> Dict[str, Any]:
        """
        Processa uma única cidade
        
        Args:
            cidade: Nome da cidade
            data_inicial: Data inicial DD/MM/AAAA
            data_final: Data final DD/MM/AAAA
        
        Returns:
            dict: Resultado do processamento
        """
        try:
            sucesso = self.bot.processar_cidade(cidade, data_inicial, data_final)
            
            if sucesso:
                arquivo_gerado = self._localizar_arquivo_gerado(cidade)
                return {
                    'sucesso': True,
                    'cidade': cidade,
                    'arquivo_gerado': arquivo_gerado
                }
            else:
                return {
                    'sucesso': False,
                    'cidade': cidade,
                    'erro': 'Falha no processamento'
                }
                
        except Exception as e:
            return {
                'sucesso': False,
                'cidade': cidade,
                'erro': f'Erro: {str(e)}'
            }
    
    def processar_lista_cidades_terminal(self, cidades: List[str], data_inicial: str, data_final: str) -> Dict[str, Any]:
        """
        Processamento para versão terminal (usa método do bot)
        
        Args:
            cidades: Lista de cidades
            data_inicial: Data inicial
            data_final: Data final
        
        Returns:
            dict: Estatísticas do processamento
        """
        try:
            print(f"🚀 Processamento iniciado: {len(cidades)} cidades")
            
            estatisticas = self.bot.processar_lista_cidades(cidades, data_inicial, data_final)
            
            # SEMPRE fechar navegador no final do processamento terminal
            self._fechar_navegador_e_finalizar()
            
            return {
                'sucesso': True,
                'estatisticas': estatisticas
            }
            
        except Exception as e:
            erro = f"Erro no processamento: {str(e)}"
            self._log(f"❌ {erro}")
            # Fechar navegador em caso de erro também
            self._fechar_navegador_e_finalizar()
            return {'sucesso': False, 'erro': erro}
    
    def processar_lista_cidades_gui(self, cidades: List[str], data_inicial: str, data_final: str, 
                                   callback_progresso: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Processamento para GUI com callback de progresso
        
        Args:
            cidades: Lista de cidades
            data_inicial: Data inicial
            data_final: Data final
            callback_progresso: Callback para progresso individual
        
        Returns:
            dict: Resultado consolidado
        """
        sucessos = 0
        erros = 0
        self.resultados_processamento = []
        self.processo_cancelado = False
        
        try:
            for i, cidade in enumerate(cidades):
                # Verifica se foi cancelado
                if self.processo_cancelado:
                    break
                
                # Callback de início
                if callback_progresso:
                    continuar = callback_progresso(cidade, 'iniciando', i)
                    if not continuar:
                        self.processo_cancelado = True
                        break
                
                # Processa cidade
                resultado = self.processar_cidade_individual(cidade, data_inicial, data_final)
                self.resultados_processamento.append(resultado)
                
                # Callback de resultado
                if callback_progresso:
                    if resultado['sucesso']:
                        sucessos += 1
                        detalhes = None
                        if resultado.get('arquivo_gerado'):
                            detalhes = f"Arquivo: {os.path.basename(resultado['arquivo_gerado'])}"
                        
                        continuar = callback_progresso(cidade, 'sucesso', i, detalhes)
                    else:
                        erros += 1
                        continuar = callback_progresso(cidade, 'erro', i, resultado.get('erro'))
                    
                    if not continuar:
                        self.processo_cancelado = True
                        break
                
                # Volta para página inicial (exceto última cidade)
                if i < len(cidades) - 1:
                    if not self.bot.voltar_pagina_inicial():
                        break
                    
                    import time
                    time.sleep(2)
            
            # Gera relatório consolidado
            self._gerar_relatorio_consolidado()
            
            # SEMPRE fechar navegador no final do processamento GUI
            self._fechar_navegador_e_finalizar()
            
            return {
                'sucesso': True,
                'total_processadas': sucessos + erros,
                'sucessos': sucessos,
                'erros': erros,
                'resultados_detalhados': self.resultados_processamento,
                'cancelado': self.processo_cancelado
            }
            
        except Exception as e:
            erro = f"Erro no processamento GUI: {str(e)}"
            self._log(f"❌ {erro}")
            # Fechar navegador em caso de erro também
            self._fechar_navegador_e_finalizar()
            return {'sucesso': False, 'erro': erro}
    
    def cancelar_processamento(self):
        """
        Cancela o processamento atual e fecha navegador
        """
        self.processo_cancelado = True
        self._fechar_navegador_e_finalizar()
    
    def _fechar_navegador_e_finalizar(self):
        """
        Fecha navegador de forma segura e marca processo como finalizado
        """
        try:
            if (self.bot and 
                hasattr(self.bot, 'navegador') and 
                self.bot.navegador and 
                self.navegador_inicializado):
                
                self.bot.fechar_navegador()
                self.navegador_inicializado = False
                print("🔒 Navegador fechado")
        except Exception:
            pass
    
    def _localizar_arquivo_gerado(self, cidade: str) -> Optional[str]:
        """Localiza arquivo Excel gerado para cidade"""
        try:
            if hasattr(self.data_extractor, 'diretorio_saida'):
                diretorio = self.data_extractor.diretorio_saida
                
                import glob
                municipio_formatado = cidade.replace(' ', '_').replace('/', '_').replace('\\', '_')
                padrao = os.path.join(diretorio, f"{municipio_formatado}_*.xlsx")
                arquivos = glob.glob(padrao)
                
                if arquivos:
                    return max(arquivos, key=os.path.getctime)
            
            return None
            
        except Exception:
            return None
    
    def _gerar_relatorio_consolidado(self):
        """Gera relatório consolidado"""
        try:
            if hasattr(self.data_extractor, 'gerar_relatorio_consolidado'):
                relatorio = self.data_extractor.gerar_relatorio_consolidado(
                    self.resultados_processamento
                )
                if relatorio:
                    self._log(f"📋 Relatório consolidado: {os.path.basename(relatorio)}")
        except Exception:
            pass
    
    def fechar_navegador(self):
        """Fecha navegador de forma segura (método público para compatibilidade)"""
        self._fechar_navegador_e_finalizar()
    
    def executar_fluxo_completo_terminal(self, arquivo_cidades: str = "listed_cities.txt") -> int:
        """
        Fluxo completo para versão terminal
        
        Args:
            arquivo_cidades: Arquivo com lista de cidades
        
        Returns:
            int: Código de saída (0=sucesso, 1=erro)
        """
        try:
            # Inicialização
            resultado = self.inicializar_componentes()
            if not resultado['sucesso']:
                return 1
            
            # Carrega cidades
            resultado = self.carregar_cidades_do_arquivo()
            if not resultado['sucesso']:
                return 1
            
            cidades = resultado['cidades']
            
            # Calcula datas
            data_inicial, data_final = self.calcular_datas_padrao()
            
            # Configura navegador
            resultado = self.configurar_navegador()
            if not resultado['sucesso']:
                return 1
            
            # Abre página
            resultado = self.abrir_pagina_inicial()
            if not resultado['sucesso']:
                self._fechar_navegador_e_finalizar()
                return 1
            
            # Processa cidades
            resultado = self.processar_lista_cidades_terminal(cidades, data_inicial, data_final)
            
            # Aguarda usuário (navegador já foi fechado no processamento)
            input("Pressione Enter para finalizar...")
            
            if resultado['sucesso']:
                estatisticas = resultado['estatisticas']
                return 0 if estatisticas['erros'] == 0 else 1
            else:
                return 1
                
        except KeyboardInterrupt:
            print("\n⏹️ Interrompido pelo usuário")
            self._fechar_navegador_e_finalizar()
            return 130
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            self._fechar_navegador_e_finalizar()
            return 1 