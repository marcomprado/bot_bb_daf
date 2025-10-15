#!/usr/bin/env python3
"""
Módulo de seleção de cidades com janela popup para Windows
Usa versão otimizada automaticamente para listas grandes
"""

import platform
import tkinter as tk
from tkinter import ttk, Toplevel, StringVar, BooleanVar


def is_windows():
    """Verifica se o sistema é Windows"""
    return platform.system() == "Windows"


# Importação condicional da versão otimizada
try:
    from src.view.modules.optimized_selector import OptimizedCitySelector, OptimizedYearSelector
    OPTIMIZED_AVAILABLE = True
except ImportError:
    OPTIMIZED_AVAILABLE = False


class CitySelectionWindow:
    """Janela de seleção de cidades para Windows usando tkinter puro"""
    
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
        
        # Centraliza janela na tela
        self.window.update_idletasks()
        width = 400
        height = 500
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Campo de busca
        self.search_var = StringVar()
        search_frame = tk.Frame(main_frame, bg="white")
        search_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(search_frame, text="Buscar:", bg="white").pack(side="left", padx=(0, 5))
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        self.search_var.trace("w", self._filter_cities)
        
        # Frame com scrollbar para lista
        list_frame = tk.Frame(main_frame, bg="white")
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="white")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Checkboxes para cada cidade
        self.check_vars = {}
        self.check_widgets = {}
        for cidade in self.cidades:
            var = BooleanVar(value=False)
            checkbox = tk.Checkbutton(
                self.scrollable_frame,
                text=cidade.title(),
                variable=var,
                bg="white",
                anchor="w",
                justify="left"
            )
            checkbox.pack(anchor="w", fill="x", pady=1)
            self.check_vars[cidade] = var
            self.check_widgets[cidade] = checkbox
        
        # Frame de botões
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill="x", pady=(5, 0))
        
        # Botões de ação
        tk.Button(
            button_frame,
            text="Selecionar Todas",
            command=self._select_all,
            width=15
        ).pack(side="left", padx=2)
        
        tk.Button(
            button_frame,
            text="Limpar",
            command=self._clear_all,
            width=10
        ).pack(side="left", padx=2)
        
        tk.Button(
            button_frame,
            text="OK",
            command=self._confirm,
            width=10,
            bg="#0066cc",
            fg="white"
        ).pack(side="right", padx=2)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=self._cancel,
            width=10
        ).pack(side="right", padx=2)
        
        # Foca no campo de busca
        search_entry.focus_set()
    
    def _filter_cities(self, *args):
        """Filtra cidades baseado na busca"""
        search_text = self.search_var.get().lower()
        
        for cidade, widget in self.check_widgets.items():
            if search_text in cidade.lower():
                widget.pack(anchor="w", fill="x", pady=1)
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


def create_city_selector(parent, items, selected_items=None, title="Seleção"):
    """
    Cria seletor de cidades apropriado baseado no sistema e tamanho da lista

    Args:
        parent: Janela pai
        items: Lista de itens disponíveis
        selected_items: Lista de itens pré-selecionados
        title: Título da janela

    Returns:
        Lista de itens selecionados ou None se cancelado
    """
    # Usa versão otimizada para Windows com listas grandes
    if is_windows() and OPTIMIZED_AVAILABLE and len(items) > 100:
        selector = OptimizedCitySelector(parent, items, selected_items, title)
        return selector.show()
    else:
        # Usa versão antiga para listas pequenas ou se otimizada não disponível
        selector = CitySelectionWindow(parent, items, title)
        result = selector.show()

        # Se usuário cancelou (lista vazia) e havia seleção prévia, retorna None
        # para indicar cancelamento ao invés de lista vazia
        if not result and selected_items:
            return None
        return result


def create_year_selector(parent, years, selected_years=None, title="Seleção de Anos"):
    """
    Cria seletor de anos apropriado para Windows

    Args:
        parent: Janela pai
        years: Lista de anos disponíveis
        selected_years: Lista de anos pré-selecionados
        title: Título da janela

    Returns:
        Lista de anos selecionados ou None se cancelado
    """
    if is_windows() and OPTIMIZED_AVAILABLE:
        selector = OptimizedYearSelector(parent, years, selected_years, title)
        return selector.show()
    else:
        # Fallback para versão de cidades adaptada para anos
        selector = CitySelectionWindow(parent, years, title)
        result = selector.show()

        if not result and selected_years:
            return None
        return result