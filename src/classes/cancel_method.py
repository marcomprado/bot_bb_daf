#!/usr/bin/env python3
"""
Base class for all bot implementations
Provides common functionality for browser management and cancellation
"""

from abc import ABC


class BotBase(ABC):
    """
    Classe base para todos os bots do sistema

    Fornece funcionalidade comum para:
    - Gerenciamento de navegador
    - Cancelamento de execução
    - Limpeza de recursos
    """

    def __init__(self):
        """Inicializa atributos comuns"""
        self.navegador = None
        self.wait = None
        self._cancelado = False

    def cancelar(self, forcado=False):
        """
        Cancela a execução e fecha o navegador

        Args:
            forcado: Se True, força fechamento de todas as abas do Chrome
        """
        self._cancelado = True

        if forcado:
            self._cancelar_forcado()
        else:
            self._cancelar_normal()

    def _cancelar_normal(self):
        """Cancelamento normal - fecha navegador graciosamente"""
        print(f"Cancelando execução {self.__class__.__name__}...")
        self.fechar_navegador()

    def _cancelar_forcado(self):
        """Cancelamento forçado - fecha todas as abas e força quit"""
        print(f"Cancelamento forçado {self.__class__.__name__}: fechando todas as abas...")

        if self.navegador:
            try:
                # Tenta fechar todas as janelas abertas
                handles = self.navegador.window_handles
                for handle in handles:
                    try:
                        self.navegador.switch_to.window(handle)
                        self.navegador.close()
                    except:
                        pass  # Ignora erros ao fechar abas individuais
            except:
                pass

            # Força fechamento do navegador
            try:
                self.navegador.quit()
            except:
                pass

            self.navegador = None
            self.wait = None
            print("Todas as abas do Chrome foram fechadas")

    def fechar_navegador(self):
        """Fecha o navegador se estiver aberto"""
        try:
            if self.navegador:
                self.navegador.quit()
                self.navegador = None
                self.wait = None
                print("✓ Navegador fechado")
        except Exception as e:
            print(f"Aviso: Erro ao fechar navegador - {e}")

    def esta_cancelado(self):
        """
        Verifica se a execução foi cancelada

        Returns:
            bool: True se foi cancelado
        """
        return self._cancelado

    def resetar_cancelamento(self):
        """Reseta o flag de cancelamento"""
        self._cancelado = False