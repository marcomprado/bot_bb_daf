#!/usr/bin/env python3
"""
Sistema de Execução Automática de Scripts
Gerencia a execução agendada dos scripts BB DAF, FNDE e Betha
"""

import os
import sys
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Adiciona o diretório raiz ao path (só em desenvolvimento, não em executável)
if not hasattr(sys, '_MEIPASS'):
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Importa configurações e gerenciadores
from src.classes.config_page import ConfigManager
from src.classes.date_calculator import DateCalculator
from src.classes.file.file_manager import FileManager
from src.classes.file.path_manager import obter_caminho_dados, obter_caminho_recurso
from src.classes.methods.cancel_method import BotBase

# Importa os bots
from src.bots.bot_bbdaf import BotBBDAF
from src.bots.bot_fnde import BotFNDE
from src.bots.bot_betha import BotBetha

# Importa utilitários
from src.classes.data_extractor import DataExtractor
from src.classes.methods.parallel_processor import ProcessadorParalelo


class AutomaticExecutor(BotBase):
    """
    Classe responsável pela execução automática dos scripts
    conforme configuração definida pelo usuário
    """

    def __init__(self):
        """Inicializa o executor automático"""
        super().__init__()

        # Gerenciadores
        self.config_manager = ConfigManager()
        self.date_calculator = DateCalculator()
        self.file_manager = FileManager()

        # Thread de monitoramento
        self.monitoring_thread = None
        self.monitoring_active = False

        # Controle de estado para evitar loops
        self._config_loading = False
        self._last_saved_config = None
        self._restart_pending = False
        self._restart_timer = None

        # Configurações de execução
        self.exec_config = self._load_execution_config()

        # Status de execução
        self.is_executing = False
        self.last_execution_date = None
        self.last_execution_time = None  # Armazena datetime completo da última execução
        self.last_execution_date_only = None  # Armazena apenas a data da última execução (sem hora)
        self.next_execution_time = None

        # Bots em execução
        self.current_bots = []

    def _load_execution_config(self) -> Dict:
        """
        Carrega as configurações de execução automática do user_config.json

        Returns:
            Dict com configurações de execução ou dict vazio se não houver
        """
        self._config_loading = True

        # Apenas carrega configuração salva, sem defaults
        saved_config = self.config_manager.get_config('automatic_execution', None)

        if saved_config is not None:
            result = saved_config
        else:
            # Retorna configuração vazia se não houver nada salvo
            result = {
                'enabled': False,
                'scripts': {},
                'period': 'Diariamente',
                'weekdays': {},
                'time': '08:00',
                'execution_mode': 'Individual',
                'parallel_instances': 2
            }

        self._config_loading = False
        self._last_saved_config = result.copy() if result else {}
        return result


    def save_execution_config(self, config: Dict):
        """
        Atualiza as configurações de execução automática NA MEMÓRIA
        NÃO salva em arquivo - isso é responsabilidade da UI

        Args:
            config: Configurações a atualizar
        """
        # Evita salvamento durante carregamento
        if self._config_loading:
            return

        # Verifica se houve mudança real na configuração
        if self._last_saved_config == config:
            return

        # Determina se precisa reiniciar o monitoramento
        needs_restart = False
        if self._last_saved_config:
            # Só reinicia se mudaram configurações críticas
            critical_changed = (
                self._last_saved_config.get('enabled') != config.get('enabled') or
                self._last_saved_config.get('time') != config.get('time') or
                self._last_saved_config.get('period') != config.get('period') or
                self._last_saved_config.get('weekdays') != config.get('weekdays')
            )
            needs_restart = critical_changed and config.get('enabled', False)
        else:
            needs_restart = config.get('enabled', False)

        # Atualiza configuração APENAS na memória
        self.exec_config = config
        self._last_saved_config = config.copy()
        # REMOVIDO: self.config_manager.set_config() - não salva mais nada

        # Se desabilitou, para o monitoramento
        if not config.get('enabled', False) and self.monitoring_active:
            self.stop_monitoring()
        # Se habilitou ou mudou configuração crítica, reinicia
        elif needs_restart:
            if not self._restart_pending:
                self._restart_pending = True
                # Cancela timer anterior se existir
                if self._restart_timer:
                    self._restart_timer.cancel()
                # Usa timer para debounce de 500ms
                self._restart_timer = threading.Timer(0.5, self._delayed_restart)
                self._restart_timer.start()

    def _delayed_restart(self):
        """
        Reinicia o monitoramento após delay (debounce)
        """
        self._restart_pending = False
        self._restart_timer = None
        if self.exec_config.get('enabled', False):
            self.restart_monitoring()

    def start_monitoring(self):
        """Inicia o monitoramento para execução automática"""
        if not self.exec_config.get('enabled', False):
            print("⚠ Execução automática está desabilitada")
            return False

        if self.monitoring_active:
            # Já está ativo, não precisa fazer nada
            return True

        self.monitoring_active = True

        # Detecta se está rodando como executável PyInstaller
        is_executable = hasattr(sys, '_MEIPASS')

        # Em executável, não usar daemon para evitar problemas
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=False if is_executable else True
        )
        self.monitoring_thread.start()

        print(f"✓ Monitoramento de execução automática iniciado ({'executável' if is_executable else 'desenvolvimento'})")
        self._calculate_next_execution()
        if self.next_execution_time:
            print(f"  Próxima execução: {self.next_execution_time.strftime('%d/%m/%Y %H:%M')}")

        return True

    def stop_monitoring(self):
        """Para o monitoramento de execução automática"""
        if not self.monitoring_active:
            return

        self.monitoring_active = False

        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            self.monitoring_thread = None

        print("✓ Monitoramento de execução automática parado")

    def restart_monitoring(self):
        """Reinicia o monitoramento com as novas configurações"""
        # Só reinicia se realmente estiver monitorando
        if self.monitoring_active:
            self.stop_monitoring()
            time.sleep(0.2)  # Pausa menor para melhor responsividade
            self.start_monitoring()
        else:
            # Se não estava ativo, apenas inicia
            self.start_monitoring()

    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                # Verifica se deve executar agora
                if self._should_execute_now():
                    self._execute_scheduled_scripts()

                # Aguarda 30 segundos antes de verificar novamente
                time.sleep(30)

            except Exception as e:
                print(f"✗ Erro no monitoramento: {e}")
                time.sleep(60)  # Aguarda mais tempo em caso de erro

    def _should_execute_now(self) -> bool:
        """
        Verifica se é hora de executar os scripts

        Returns:
            True se deve executar agora
        """
        if self.is_executing:
            return False

        if not self.exec_config.get('enabled', False):
            return False

        now = datetime.now()

        # Verifica se já executou recentemente (evita execuções duplicadas)
        if self.last_execution_time:
            time_since_last = (now - self.last_execution_time).total_seconds()

            # Verifica se mudou de dia
            if self.last_execution_date_only and now.date() != self.last_execution_date_only:
                # Mudou de dia, resetar controle de execução
                print(f"📅 Novo dia detectado: {now.date()}")
                self.last_execution_time = None
                self.last_execution_date_only = None
            elif time_since_last < 180:
                # Mesmo dia e executou há menos de 3 minutos - evita duplicação
                return False

        # Verifica horário
        scheduled_time = self.exec_config.get('time', '08:00')
        try:
            hour, minute = map(int, scheduled_time.split(':'))
            scheduled_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Verifica se está no minuto correto (com tolerância de 45 segundos)
            time_diff = abs((now - scheduled_datetime).total_seconds())
            if time_diff > 45:  # Mais de 45 segundos de diferença
                return False

        except Exception as e:
            print(f"✗ Erro ao processar horário agendado: {e}")
            return False

        # Verifica período
        period = self.exec_config.get('period', 'Diariamente')

        if period == 'Diariamente':
            return True

        elif period == 'Semanalmente':
            # Mapeia dias da semana
            weekday_map = {
                0: 'seg',
                1: 'ter',
                2: 'qua',
                3: 'qui',
                4: 'sex',
                5: 'sab',
                6: 'dom'
            }

            current_weekday = weekday_map.get(now.weekday())
            weekdays = self.exec_config.get('weekdays', {})

            return weekdays.get(current_weekday, False)

        elif period == 'Mensalmente':
            # Executa sempre no dia 1 de cada mês
            if now.day == 1:
                return True
            else:
                # Log informativo quando não é dia 1
                if now.day == 2 and self.last_execution_date_only != now.date():
                    print(f"📅 Aguardando dia 1 do próximo mês para execução mensal")

        return False

    def _calculate_next_execution(self):
        """Calcula a próxima execução agendada"""
        if not self.exec_config.get('enabled', False):
            self.next_execution_time = None
            return

        now = datetime.now()
        scheduled_time = self.exec_config.get('time', '08:00')

        try:
            hour, minute = map(int, scheduled_time.split(':'))
            next_exec = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Se já passou o horário hoje, calcula para o próximo dia aplicável
            if next_exec <= now:
                next_exec += timedelta(days=1)

            period = self.exec_config.get('period', 'Diariamente')

            if period == 'Semanalmente':
                weekdays = self.exec_config.get('weekdays', {})
                weekday_map = {
                    0: 'seg', 1: 'ter', 2: 'qua', 3: 'qui',
                    4: 'sex', 5: 'sab', 6: 'dom'
                }

                # Encontra o próximo dia da semana habilitado
                for days_ahead in range(1, 8):
                    check_date = now + timedelta(days=days_ahead)
                    check_date = check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    weekday = weekday_map.get(check_date.weekday())

                    if weekdays.get(weekday, False):
                        next_exec = check_date
                        break

            elif period == 'Mensalmente':
                # Sempre no dia 1 do próximo mês
                if now.day >= 1:  # Se já passou ou é dia 1
                    if now.month == 12:
                        next_exec = datetime(now.year + 1, 1, 1, hour, minute, 0, 0)
                    else:
                        next_exec = datetime(now.year, now.month + 1, 1, hour, minute, 0, 0)

            self.next_execution_time = next_exec

        except Exception as e:
            print(f"✗ Erro ao calcular próxima execução: {e}")
            self.next_execution_time = None

    def _execute_scheduled_scripts(self):
        """Executa os scripts agendados"""
        self.is_executing = True
        current_time = datetime.now()
        self.last_execution_date = current_time
        self.last_execution_time = current_time  # Armazena o datetime completo
        self.last_execution_date_only = current_time.date()  # Armazena apenas a data

        print("\n" + "="*60)
        print(f"🤖 Iniciando execução automática - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("="*60)

        try:
            scripts = self.exec_config.get('scripts', {})
            mode = self.exec_config.get('execution_mode', 'Individual')

            # Executa BB DAF se habilitado
            if scripts.get('bb_daf', False):
                print("\n📊 Executando BB DAF...")
                self._execute_bbdaf(mode)

            # Executa FNDE se habilitado
            if scripts.get('fnde', False):
                print("\n📚 Executando FNDE...")
                self._execute_fnde(mode)

            # Executa Betha se habilitado
            if scripts.get('betha', False):
                print("\n🏢 Executando Betha...")
                self._execute_betha(mode)

            print("\n" + "="*60)
            print("✓ Execução automática concluída com sucesso")
            print("="*60)

        except Exception as e:
            print(f"\n✗ Erro durante execução automática: {e}")

        finally:
            self.is_executing = False
            self._calculate_next_execution()

            if self.next_execution_time:
                print(f"\n⏰ Próxima execução: {self.next_execution_time.strftime('%d/%m/%Y %H:%M')}")

    def _execute_bbdaf(self, mode: str):
        """
        Executa o bot BB DAF com parâmetros padrão

        Args:
            mode: Modo de execução (Individual ou Paralela)
        """
        try:
            # Obtém datas padrão (últimos 30 dias)
            data_final = datetime.now()
            data_inicial = data_final - timedelta(days=30)

            # Carrega TODAS as cidades (cidades.txt) para execução automática
            file_manager_auto = FileManager("cidades.txt")  # 852 cidades completas
            cidades = file_manager_auto.carregar_cidades()

            if not cidades:
                print("  ⚠ Nenhuma cidade configurada para BB DAF")
                return

            print(f"  • Período: {data_inicial.strftime('%d/%m/%Y')} até {data_final.strftime('%d/%m/%Y')}")
            print(f"  • Cidades: {len(cidades)} cidades")
            print(f"  • Modo: {mode}")

            if mode == 'Paralela':
                # Execução paralela
                num_instancias = self.exec_config.get('parallel_instances', 2)
                processador = ProcessadorParalelo()
                resultado = processador.executar_paralelo_threads(
                    num_instancias=num_instancias,
                    data_inicial=data_inicial.strftime("%d/%m/%Y"),
                    data_final=data_final.strftime("%d/%m/%Y")
                )
            else:
                # Execução individual
                bot = BotBBDAF()
                bot.configurar_extrator_dados(DataExtractor("bbdaf"))
                self.current_bots.append(bot)

                resultado = bot.executar_completo(
                    cidades=cidades,
                    data_inicial=data_inicial.strftime("%d/%m/%Y"),
                    data_final=data_final.strftime("%d/%m/%Y")
                )

                bot.fechar_navegador()
                self.current_bots.remove(bot)

            if resultado and resultado.get('sucesso'):
                print("  ✓ BB DAF executado com sucesso")
            else:
                erro = resultado.get('erro', 'Erro desconhecido') if resultado else 'Erro na execução'
                print(f"  ✗ Falha na execução BB DAF: {erro}")

        except Exception as e:
            print(f"  ✗ Erro ao executar BB DAF: {e}")

    def _execute_fnde(self, mode: str):
        """
        Executa o bot FNDE para todas as cidades

        Args:
            mode: Modo de execução (Individual ou Paralela)
        """
        try:
            # Parâmetros
            ano = datetime.now().year

            # Carrega TODAS as cidades (cidades.txt) para execução automática
            file_manager_auto = FileManager("cidades.txt")  # 852 cidades completas
            municipios = file_manager_auto.carregar_cidades()

            if not municipios:
                print("  ⚠ Nenhuma cidade configurada para FNDE")
                return

            print(f"  • Ano: {ano}")
            print(f"  • Municípios: {len(municipios)} cidades")
            print(f"  • Modo: {mode}")

            if mode == 'Paralela':
                # Execução paralela
                num_instancias = self.exec_config.get('parallel_instances', 2)

                bot = BotFNDE()
                self.current_bots.append(bot)

                resultado = bot.executar_paralelo(str(ano), num_instancias)

                self.current_bots.remove(bot)

                if resultado and resultado.get('sucesso'):
                    print("  ✓ FNDE executado com sucesso (paralelo)")
                else:
                    erro = resultado.get('erro', 'Erro desconhecido') if resultado else 'Erro na execução'
                    print(f"  ✗ Falha na execução FNDE: {erro}")
            else:
                # Execução individual
                bot = BotFNDE()
                self.current_bots.append(bot)

                if not bot.configurar_navegador():
                    print("  ✗ Erro ao configurar navegador para FNDE")
                    self.current_bots.remove(bot)
                    return

                # Processa cada município
                sucessos = 0
                falhas = 0

                for municipio in municipios:
                    if self.esta_cancelado():
                        print("  ⚠ Execução cancelada pelo usuário")
                        break

                    try:
                        resultado = bot.processar_municipio(
                            ano=str(ano),
                            municipio=municipio.upper()
                        )

                        if resultado['sucesso']:
                            sucessos += 1
                        else:
                            falhas += 1
                            print(f"  ✗ Falha em {municipio}: {resultado.get('mensagem', 'Erro desconhecido')}")

                    except Exception as e:
                        falhas += 1
                        print(f"  ✗ Erro ao processar {municipio}: {e}")

                print(f"  ✓ FNDE executado: {sucessos} sucessos, {falhas} falhas")

                bot.fechar_navegador()
                self.current_bots.remove(bot)

        except Exception as e:
            print(f"  ✗ Erro ao executar FNDE: {e}")

    def _execute_betha(self, mode: str):
        """
        Executa o bot Betha com parâmetros padrão

        Args:
            mode: Modo de execução
        """
        try:
            # Carrega configurações das cidades (recurso empacotado)
            config_path = obter_caminho_recurso("src/bots/betha/city_betha.json")

            if not os.path.exists(config_path):
                print(f"  ⚠ Arquivo de configuração city_betha.json não encontrado em: {config_path}")
                return

            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                cidades = config_data.get('cidades', [])

            if not cidades:
                print("  ⚠ Nenhuma cidade configurada para Betha")
                return

            ano = datetime.now().year
            print(f"  • Ano: {ano}")
            print(f"  • Cidades: {len(cidades)} cidades")
            print(f"  • Modo: {mode}")

            # Processa cada cidade
            for cidade_config in cidades:
                cidade_nome = cidade_config.get('nome')

                if self.esta_cancelado():
                    print("  ⚠ Execução cancelada pelo usuário")
                    break

                print(f"\n  Processando {cidade_nome}...")

                try:
                    bot = BotBetha(cidade_config, ano)
                    self.current_bots.append(bot)

                    resultado = bot.executar_completo()

                    if resultado['sucesso']:
                        print(f"  ✓ {cidade_nome} processado com sucesso")
                    else:
                        print(f"  ✗ Falha em {cidade_nome}: {resultado['mensagem']}")

                    bot.fechar_navegador()
                    self.current_bots.remove(bot)

                    # Pausa entre cidades
                    time.sleep(2)

                except Exception as e:
                    print(f"  ✗ Erro ao processar {cidade_nome}: {e}")

            print("  ✓ Betha executado com sucesso")

        except Exception as e:
            print(f"  ✗ Erro ao executar Betha: {e}")

    def cancelar(self, forcado=False):
        """
        Cancela a execução automática em andamento

        Args:
            forcado: Se True, força cancelamento
        """
        super().cancelar(forcado)

        # Cancela timer de restart se existir
        if self._restart_timer:
            self._restart_timer.cancel()
            self._restart_timer = None
            self._restart_pending = False

        # Cancela todos os bots em execução
        for bot in self.current_bots:
            try:
                bot.cancelar(forcado)
            except:
                pass

        self.current_bots.clear()
        self.is_executing = False

        print("✓ Execução automática cancelada")

    def get_status(self) -> Dict:
        """
        Obtém o status atual do executor automático

        Returns:
            Dict com informações de status
        """
        return {
            'enabled': self.exec_config.get('enabled', False),
            'monitoring_active': self.monitoring_active,
            'is_executing': self.is_executing,
            'last_execution': self.last_execution_date.strftime('%d/%m/%Y %H:%M:%S') if self.last_execution_date else None,
            'next_execution': self.next_execution_time.strftime('%d/%m/%Y %H:%M') if self.next_execution_time else None,
            'configured_scripts': self.exec_config.get('scripts', {}),
            'period': self.exec_config.get('period', 'Diariamente'),
            'scheduled_time': self.exec_config.get('time', '08:00'),
            'execution_mode': self.exec_config.get('execution_mode', 'Individual')
        }


# Singleton global para o executor automático
_automatic_executor_instance = None

def get_automatic_executor() -> AutomaticExecutor:
    """
    Obtém a instância singleton do executor automático

    Returns:
        AutomaticExecutor: Instância única do executor
    """
    global _automatic_executor_instance

    if _automatic_executor_instance is None:
        _automatic_executor_instance = AutomaticExecutor()

    return _automatic_executor_instance


def start_automatic_execution():
    """Inicia o sistema de execução automática"""
    executor = get_automatic_executor()
    return executor.start_monitoring()


def stop_automatic_execution():
    """Para o sistema de execução automática"""
    executor = get_automatic_executor()
    executor.stop_monitoring()


def update_execution_config(config: Dict):
    """
    Atualiza as configurações de execução automática

    Args:
        config: Novas configurações
    """
    executor = get_automatic_executor()
    executor.save_execution_config(config)


def get_execution_status() -> Dict:
    """
    Obtém o status da execução automática

    Returns:
        Dict com status atual
    """
    executor = get_automatic_executor()
    return executor.get_status()


# Para testes diretos
if __name__ == "__main__":
    print("Sistema de Execução Automática")
    print("-" * 40)

    # Exemplo de configuração
    test_config = {
        'enabled': True,
        'scripts': {
            'bb_daf': True,
            'fnde': False,
            'betha': False
        },
        'period': 'Diariamente',
        'time': '14:00',
        'execution_mode': 'Individual'
    }

    # Atualiza configuração
    update_execution_config(test_config)

    # Obtém status
    status = get_execution_status()
    print("Status atual:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    # Inicia monitoramento
    if start_automatic_execution():
        print("\nMonitoramento iniciado. Pressione Ctrl+C para parar...")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            stop_automatic_execution()
            print("\nMonitoramento parado.")