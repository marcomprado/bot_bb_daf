#!/usr/bin/env python3
# Base class for all bot implementations

from abc import ABC


class BotBase(ABC):
    # Classe base para todos os bots do sistema

    def __init__(self):
        # Inicializa atributos comuns
        self.navegador = None
        self.wait = None
        self._cancelado = False
        self._navegadores_extras = {}  # {nome: navegador}

    def registrar_navegador(self, nome, navegador):
        # Registra um navegador adicional para ser gerenciado pelo cancelamento
        self._navegadores_extras[nome] = navegador

    def remover_navegador(self, nome):
        # Remove um navegador do registro
        self._navegadores_extras.pop(nome, None)

    def _obter_todos_navegadores(self):
        # Retorna lista de tuplas (nome, navegador) com todos os navegadores ativos
        navegadores = []
        if self.navegador:
            navegadores.append(("principal", self.navegador))
        for nome, nav in self._navegadores_extras.items():
            if nav:
                navegadores.append((nome, nav))
        return navegadores

    def cancelar(self, forcado=False):
        # Cancela a execução e fecha o navegador
        self._cancelado = True

        if forcado:
            self._cancelar_forcado()
        else:
            self._cancelar_normal()

    def _cancelar_normal(self):
        # Cancelamento normal - fecha todos os navegadores graciosamente
        print(f"Cancelando execução {self.__class__.__name__}...")
        self.fechar_navegadores()

    def _cancelar_forcado(self):
        # Cancelamento forçado - fecha todas as abas e força quit em todos os navegadores
        print(f"Cancelamento forçado {self.__class__.__name__}: fechando todas as abas...")

        for nome, nav in self._obter_todos_navegadores():
            try:
                # Tenta fechar todas as janelas abertas
                handles = nav.window_handles
                for handle in handles:
                    try:
                        nav.switch_to.window(handle)
                        nav.close()
                    except:
                        pass
            except:
                pass

            # Força fechamento do navegador
            try:
                nav.quit()
            except:
                pass

            print(f"  ✓ Navegador {nome} fechado")

        # Limpa referências
        self.navegador = None
        self.wait = None
        self._navegadores_extras.clear()
        print("Todos os navegadores foram fechados")

    def fechar_navegadores(self):
        # Fecha todos os navegadores registrados
        for nome, nav in self._obter_todos_navegadores():
            try:
                nav.quit()
                print(f"✓ Navegador {nome} fechado")
            except Exception as e:
                print(f"Aviso: Erro ao fechar navegador {nome} - {e}")

        self.navegador = None
        self.wait = None
        self._navegadores_extras.clear()

    def fechar_navegador(self):
        # Compatibilidade - fecha todos os navegadores
        self.fechar_navegadores()

    def cancelar_forcado(self):
        # Atalho para cancelamento forçado
        self.cancelar(forcado=True)

    def esta_cancelado(self):
        # Verifica se a execução foi cancelada
        return self._cancelado

    def resetar_cancelamento(self):
        # Reseta o flag de cancelamento
        self._cancelado = False
