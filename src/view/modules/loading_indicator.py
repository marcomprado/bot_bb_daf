#!/usr/bin/env python3
"""
LoadingIndicator - Componente de loading visual para GUIs
Exibe indicador animado durante processamento em todas as interfaces
"""

import customtkinter as ctk
from typing import Optional


class LoadingIndicator:
    """
    Componente reutilizavel de loading indicator

    Features:
    - Mostra barra de progresso indeterminada animada
    - Texto de status personalizavel
    - Show/hide com animacao suave
    - Estilo consistente com ButtonFactory
    """

    # Configuracoes de estilo
    PROGRESS_BAR_HEIGHT = 8
    PROGRESS_BAR_WIDTH = 450
    PROGRESS_COLOR = "#01A2FF"  # Cor do SVG spinning-dots.svg
    PROGRESS_BG_COLOR = "#e9ecef"
    TEXT_COLOR = "#495057"
    FONT_SIZE = 13

    def __init__(self, parent):
        """
        Inicializa o loading indicator

        Args:
            parent: Container pai (geralmente frame_acoes)
        """
        self.parent = parent
        self.frame = None
        self.progress_bar = None
        self.label_status = None
        self._visible = False

        self._criar_componente()

    def _criar_componente(self):
        """Cria estrutura do componente"""
        # Frame container transparente
        self.frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
            height=50
        )

        # Label de status
        self.label_status = ctk.CTkLabel(
            self.frame,
            text="Processando...",
            font=ctk.CTkFont(size=self.FONT_SIZE),
            text_color=self.TEXT_COLOR
        )
        self.label_status.pack(pady=(5, 8))

        # Barra de progresso indeterminada
        self.progress_bar = ctk.CTkProgressBar(
            self.frame,
            mode="indeterminate",  # Animacao continua
            height=self.PROGRESS_BAR_HEIGHT,
            width=self.PROGRESS_BAR_WIDTH,
            progress_color=self.PROGRESS_COLOR,
            fg_color=self.PROGRESS_BG_COLOR,
            corner_radius=self.PROGRESS_BAR_HEIGHT // 2
        )
        self.progress_bar.pack(pady=(0, 5))

    def show(self, status_text: str = "Processando..."):
        """
        Mostra o loading indicator

        Args:
            status_text: Texto de status a exibir
        """
        if not self._visible:
            self.label_status.configure(text=status_text)
            self.frame.pack(fill="x", padx=15, pady=(10, 15))
            self.progress_bar.start()  # Inicia animacao
            self._visible = True

    def hide(self):
        """Esconde o loading indicator"""
        if self._visible:
            self.progress_bar.stop()  # Para animacao
            self.frame.pack_forget()
            self._visible = False

    def update_status(self, status_text: str):
        """
        Atualiza texto de status sem esconder/mostrar

        Args:
            status_text: Novo texto de status
        """
        if self._visible:
            self.label_status.configure(text=status_text)

    def is_visible(self) -> bool:
        """Retorna se loading esta visivel"""
        return self._visible
