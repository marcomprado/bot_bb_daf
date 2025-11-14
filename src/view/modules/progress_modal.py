#!/usr/bin/env python3
"""
Modal de progresso simples para processamento de municípios
Exibe percentual atualizado dinamicamente com botão de cancelamento
"""

import customtkinter as ctk
from typing import Callable, Optional


class ProgressModal:
    """
    Modal de progresso estilo messagebox com atualização dinâmica de percentual
    """

    def __init__(self, parent, title: str = "Processando Municípios", on_cancel: Optional[Callable] = None):
        """
        Inicializa modal de progresso

        Args:
            parent: Janela pai (CTk ou CTkToplevel)
            title: Título da janela
            on_cancel: Callback para quando usuário clica em Cancelar
        """
        self.parent = parent
        self.on_cancel = on_cancel
        self.closed = False

        # Criar janela modal
        self.window = ctk.CTkToplevel(parent)
        self.window.title(title)
        self.window.geometry("350x200")

        # Configurar modal (bloqueia janela pai)
        self.window.transient(parent)
        self.window.grab_set()

        # Centralizar na janela pai
        self._centralizar()

        # Prevenir fechamento pelo X (deve usar botão Cancelar)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close_attempt)

        # Criar interface
        self._criar_interface()

    def _centralizar(self):
        """Centraliza a janela modal na janela pai"""
        self.window.update_idletasks()

        # Pega dimensões
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        modal_width = 350
        modal_height = 200

        # Calcula posição centralizada
        x = parent_x + (parent_width - modal_width) // 2
        y = parent_y + (parent_height - modal_height) // 2

        self.window.geometry(f"{modal_width}x{modal_height}+{x}+{y}")

    def _criar_interface(self):
        """Cria elementos da interface"""
        # Frame principal com padding
        main_frame = ctk.CTkFrame(self.window, fg_color="#ffffff", corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Label de título
        self.label_titulo = ctk.CTkLabel(
            main_frame,
            text="Processando...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        self.label_titulo.pack(pady=(10, 20))

        # Label de percentual (grande e centralizado)
        self.label_percentual = ctk.CTkLabel(
            main_frame,
            text="... 0% ...",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="#0066cc"
        )
        self.label_percentual.pack(pady=20)

        # Botão Cancelar (importar ButtonFactory apenas quando necessário)
        from src.view.modules.buttons import ButtonFactory

        self.botao_acao = ButtonFactory.create_cancel_button(
            main_frame,
            text="CANCELAR",
            command=self._on_cancel_click,
            width=280
        )
        self.botao_acao.pack(pady=(10, 0))

    def _on_close_attempt(self):
        """Chamado quando usuário tenta fechar janela pelo X"""
        # Trata como cancelamento
        self._on_cancel_click()

    def _on_cancel_click(self):
        """Chamado quando usuário clica em Cancelar"""
        if self.on_cancel and not self.closed:
            self.on_cancel()

    def update_progress(self, percentage: float):
        """
        Atualiza percentual exibido (thread-safe via .after)

        Args:
            percentage: Percentual de progresso (0-100)
        """
        if self.closed:
            return

        # Arredonda para inteiro
        percentage_int = round(percentage)

        # Atualiza label (thread-safe)
        def _update():
            if not self.closed and self.window.winfo_exists():
                self.label_percentual.configure(text=f"... {percentage_int}% ...")

        try:
            self.window.after(0, _update)
        except:
            pass  # Janela pode ter sido destruída

    def show_complete(self, success: bool = True, message: str = ""):
        """
        Mostra estado de conclusão (sucesso ou erro)

        Args:
            success: Se True, mostra sucesso; se False, mostra erro
            message: Mensagem adicional a exibir
        """
        if self.closed:
            return

        def _show():
            if not self.closed and self.window.winfo_exists():
                if success:
                    # Estado de sucesso
                    self.label_titulo.configure(text="Concluído!")
                    self.label_percentual.configure(
                        text="✓ 100%",
                        text_color="#28a745"
                    )

                    # Importar ButtonFactory
                    from src.view.modules.buttons import ButtonFactory

                    # Recriar botão como "Fechar" verde
                    self.botao_acao.destroy()
                    self.botao_acao = ButtonFactory.create_success_button(
                        self.botao_acao.master,
                        text="FECHAR",
                        command=self.close,
                        width=280
                    )
                    self.botao_acao.pack(pady=(10, 0))
                else:
                    # Estado de erro
                    self.label_titulo.configure(text="Erro!")
                    msg_display = message if message else "Processamento falhou"
                    self.label_percentual.configure(
                        text=f"✗ {msg_display}",
                        text_color="#dc3545",
                        font=ctk.CTkFont(size=16, weight="bold")
                    )

                    # Importar ButtonFactory
                    from src.view.modules.buttons import ButtonFactory

                    # Recriar botão como "Fechar" vermelho
                    self.botao_acao.destroy()
                    self.botao_acao = ButtonFactory.create_cancel_button(
                        self.botao_acao.master,
                        text="FECHAR",
                        command=self.close,
                        width=280
                    )
                    self.botao_acao.pack(pady=(10, 0))

        try:
            self.window.after(0, _show)
        except:
            pass

    def close(self):
        """Fecha a janela modal"""
        if self.closed:
            return

        self.closed = True

        def _close():
            try:
                if self.window.winfo_exists():
                    self.window.grab_release()
                    self.window.destroy()
            except:
                pass

        try:
            self.window.after(0, _close)
        except:
            pass

    def is_closed(self) -> bool:
        """Verifica se modal está fechado"""
        return self.closed or not self.window.winfo_exists()
