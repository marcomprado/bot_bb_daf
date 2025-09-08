#!/usr/bin/env python3
"""
Módulo de seleção de cidades com janela popup para Windows
"""

import platform
import customtkinter as ctk
from tkinter import Toplevel, StringVar

def is_windows():
    """Verifica se o sistema é Windows"""
    return platform.system() == "Windows"


class CitySelectionWindow:
    """Janela de seleção de cidades para Windows"""
    
    def __init__(self, parent, cidades, titulo="Seleção de Cidades"):
        """
        Inicializa janela de seleção
        
        Args:
            parent: Janela pai
            cidades: Lista de cidades disponíveis
            titulo: Título da janela
        """
        self.result = []
        self.cidades = sorted(cidades)
        
        # Cria janela popup
        self.window = Toplevel(parent)
        self.window.title(titulo)
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Centraliza janela
        self.window.transient(parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Campo de busca
        self.search_var = StringVar()
        search_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Buscar cidade...",
            textvariable=self.search_var
        )
        search_entry.pack(fill="x", padx=5, pady=5)
        self.search_var.trace("w", self._filter_cities)
        
        # Frame scrollable para lista
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame, height=350)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Checkboxes para cada cidade
        self.check_vars = {}
        self.check_widgets = {}
        for cidade in self.cidades:
            var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(
                self.scroll_frame,
                text=cidade.title(),
                variable=var
            )
            checkbox.pack(anchor="w", pady=2)
            self.check_vars[cidade] = var
            self.check_widgets[cidade] = checkbox
        
        # Frame de botões
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=5)
        
        # Botões de ação
        ctk.CTkButton(
            button_frame,
            text="Selecionar Todas",
            command=self._select_all,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Limpar",
            command=self._clear_all,
            width=80
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="OK",
            command=self._confirm,
            width=80
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self._cancel,
            width=80
        ).pack(side="right", padx=5)
    
    def _filter_cities(self, *args):
        """Filtra cidades baseado na busca"""
        search_text = self.search_var.get().lower()
        
        for cidade, widget in self.check_widgets.items():
            if search_text in cidade.lower():
                widget.pack(anchor="w", pady=2)
            else:
                widget.pack_forget()
    
    def _select_all(self):
        """Seleciona todas as cidades visíveis"""
        search_text = self.search_var.get().lower()
        for cidade, var in self.check_vars.items():
            if not search_text or search_text in cidade.lower():
                var.set(True)
    
    def _clear_all(self):
        """Desmarca todas as cidades"""
        for var in self.check_vars.values():
            var.set(False)
    
    def _confirm(self):
        """Confirma seleção e fecha janela"""
        self.result = [cidade for cidade, var in self.check_vars.items() if var.get()]
        self.window.destroy()
    
    def _cancel(self):
        """Cancela e fecha janela"""
        self.result = []
        self.window.destroy()
    
    def show(self):
        """Mostra janela e aguarda resultado"""
        self.window.wait_window()
        return self.result