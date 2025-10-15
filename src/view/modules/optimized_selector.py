#!/usr/bin/env python3
"""
Módulo de seleção otimizado para listas grandes no Windows
Usa Listbox ao invés de checkboxes individuais para melhor performance
"""

import tkinter as tk
from tkinter import ttk, Toplevel, StringVar
import platform


def is_windows():
    """Verifica se o sistema é Windows"""
    return platform.system() == "Windows"


class OptimizedCitySelector:
    """Janela otimizada de seleção para grandes listas (850+ cidades)"""

    def __init__(self, parent, items, selected_items=None, title="Seleção de Cidades"):
        """
        Inicializa janela de seleção otimizada

        Args:
            parent: Janela pai
            items: Lista de itens disponíveis
            selected_items: Lista de itens pré-selecionados
            title: Título da janela
        """
        self.result = None  # None indica cancelamento
        self.items = sorted(items)
        self.filtered_items = self.items.copy()
        self.initial_selection = selected_items or []

        # Cria janela popup
        self.window = Toplevel(parent)
        self.window.title(title)
        self.window.geometry("450x600")
        self.window.resizable(False, False)

        # Centraliza janela na tela
        self.window.update_idletasks()
        width = 450
        height = 600
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

        tk.Label(search_frame, text="Buscar:", bg="white", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 10))
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_var.trace("w", self._filter_items)

        # Label contador
        self.counter_label = tk.Label(
            main_frame,
            text=f"0 de {len(self.items)} selecionados",
            bg="white",
            font=("Arial", 10, "bold"),
            fg="#0066cc"
        )
        self.counter_label.pack(fill="x", pady=(5, 5))

        # Frame da lista com scrollbar
        list_frame = tk.Frame(main_frame, bg="white")
        list_frame.pack(fill="both", expand=True, pady=5)

        # Listbox com scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.listbox = tk.Listbox(
            list_frame,
            selectmode="extended",  # Permite seleção múltipla
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            height=20,
            exportselection=False  # Mantém seleção ao perder foco
        )
        scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Preenche listbox
        for item in self.items:
            self.listbox.insert(tk.END, item.title())

        # Pré-seleciona itens
        self._pre_select_items()

        # Bind para atualizar contador
        self.listbox.bind("<<ListboxSelect>>", self._update_counter)

        # Frame de botões de seleção rápida
        quick_frame = tk.Frame(main_frame, bg="white")
        quick_frame.pack(fill="x", pady=(5, 5))

        tk.Button(
            quick_frame,
            text="Selecionar Visíveis",
            command=self._select_visible,
            width=18,
            bg="#f0f0f0",
            font=("Arial", 9)
        ).pack(side="left", padx=2)

        tk.Button(
            quick_frame,
            text="Limpar Visíveis",
            command=self._clear_visible,
            width=18,
            bg="#f0f0f0",
            font=("Arial", 9)
        ).pack(side="left", padx=2)

        tk.Button(
            quick_frame,
            text="Inverter Seleção",
            command=self._invert_selection,
            width=18,
            bg="#f0f0f0",
            font=("Arial", 9)
        ).pack(side="left", padx=2)

        # Frame de botões principais
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill="x", pady=(10, 0))

        # Botões de ação
        tk.Button(
            button_frame,
            text="Selecionar Todas",
            command=self._select_all,
            width=15,
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="Limpar Todas",
            command=self._clear_all,
            width=12,
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="OK",
            command=self._confirm,
            width=10,
            bg="#0066cc",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side="right", padx=2)

        tk.Button(
            button_frame,
            text="Cancelar",
            command=self._cancel,
            width=10,
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(side="right", padx=2)

        # Atualiza contador inicial
        self._update_counter()

        # Foca no campo de busca
        self.search_entry.focus_set()

        # Bind ESC para cancelar
        self.window.bind("<Escape>", lambda e: self._cancel())

    def _pre_select_items(self):
        """Pré-seleciona itens baseado na seleção inicial"""
        if not self.initial_selection:
            return

        # Normaliza para comparação
        initial_normalized = [item.upper() for item in self.initial_selection]

        for i in range(self.listbox.size()):
            item_text = self.listbox.get(i)
            if item_text.upper() in initial_normalized:
                self.listbox.selection_set(i)

    def _filter_items(self, *args):
        """Filtra itens baseado na busca"""
        search_text = self.search_var.get().lower()

        # Salva seleção atual
        current_selection = self._get_selected_items()

        # Limpa e repopula listbox
        self.listbox.delete(0, tk.END)

        self.filtered_items = []
        for item in self.items:
            if search_text in item.lower():
                self.listbox.insert(tk.END, item.title())
                self.filtered_items.append(item)

        # Restaura seleção para itens visíveis
        for i in range(self.listbox.size()):
            item_text = self.listbox.get(i)
            if item_text.upper() in [s.upper() for s in current_selection]:
                self.listbox.selection_set(i)

        self._update_counter()

    def _get_selected_items(self):
        """Obtém lista de itens selecionados"""
        selected = []
        for i in self.listbox.curselection():
            item_text = self.listbox.get(i)
            # Encontra o item original (case-sensitive)
            for original in self.items:
                if original.upper() == item_text.upper():
                    selected.append(original)
                    break
        return selected

    def _update_counter(self, event=None):
        """Atualiza contador de seleções"""
        count = len(self.listbox.curselection())
        total = len(self.items)
        self.counter_label.config(text=f"{count} de {total} selecionados")

    def _select_visible(self):
        """Seleciona todos os itens visíveis (filtrados)"""
        for i in range(self.listbox.size()):
            self.listbox.selection_set(i)
        self._update_counter()

    def _clear_visible(self):
        """Limpa seleção dos itens visíveis"""
        for i in range(self.listbox.size()):
            self.listbox.selection_clear(i)
        self._update_counter()

    def _invert_selection(self):
        """Inverte a seleção atual"""
        current = set(self.listbox.curselection())
        for i in range(self.listbox.size()):
            if i in current:
                self.listbox.selection_clear(i)
            else:
                self.listbox.selection_set(i)
        self._update_counter()

    def _select_all(self):
        """Seleciona todos os itens (mesmo os filtrados)"""
        # Limpa filtro temporariamente
        self.search_var.set("")
        self._filter_items()
        # Seleciona tudo
        for i in range(self.listbox.size()):
            self.listbox.selection_set(i)
        self._update_counter()

    def _clear_all(self):
        """Desmarca todos os itens"""
        # Limpa filtro temporariamente
        self.search_var.set("")
        self._filter_items()
        # Limpa seleção
        self.listbox.selection_clear(0, tk.END)
        self._update_counter()

    def _confirm(self):
        """Confirma seleção e fecha janela"""
        self.result = self._get_selected_items()
        self.window.destroy()

    def _cancel(self):
        """Cancela e fecha janela sem modificar seleção"""
        self.result = None  # None indica cancelamento
        self.window.destroy()

    def show(self):
        """Mostra janela e aguarda resultado"""
        self.window.wait_window()
        return self.result


class OptimizedYearSelector:
    """Janela otimizada para seleção de anos"""

    def __init__(self, parent, years, selected_years=None, title="Seleção de Anos"):
        """
        Inicializa janela de seleção de anos

        Args:
            parent: Janela pai
            years: Lista de anos disponíveis
            selected_years: Lista de anos pré-selecionados
            title: Título da janela
        """
        self.result = None
        self.years = sorted(years)
        self.initial_selection = selected_years or []

        # Cria janela popup
        self.window = Toplevel(parent)
        self.window.title(title)
        self.window.geometry("300x500")
        self.window.resizable(False, False)

        # Centraliza janela
        self.window.update_idletasks()
        width = 300
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

        # Label contador
        self.counter_label = tk.Label(
            main_frame,
            text=f"0 de {len(self.years)} selecionados",
            bg="white",
            font=("Arial", 10, "bold"),
            fg="#0066cc"
        )
        self.counter_label.pack(fill="x", pady=(0, 10))

        # Frame da lista
        list_frame = tk.Frame(main_frame, bg="white")
        list_frame.pack(fill="both", expand=True)

        # Listbox com scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.listbox = tk.Listbox(
            list_frame,
            selectmode="extended",
            yscrollcommand=scrollbar.set,
            font=("Arial", 11),
            height=15,
            exportselection=False
        )
        scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Preenche listbox
        for year in self.years:
            self.listbox.insert(tk.END, str(year))

        # Pré-seleciona anos
        self._pre_select_years()

        # Bind para atualizar contador
        self.listbox.bind("<<ListboxSelect>>", self._update_counter)

        # Frame de botões
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill="x", pady=(10, 0))

        tk.Button(
            button_frame,
            text="Todos",
            command=self._select_all,
            width=10,
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="Limpar",
            command=self._clear_all,
            width=10,
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="OK",
            command=self._confirm,
            width=8,
            bg="#0066cc",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side="right", padx=2)

        tk.Button(
            button_frame,
            text="Cancelar",
            command=self._cancel,
            width=8,
            bg="#f0f0f0",
            font=("Arial", 10)
        ).pack(side="right", padx=2)

        # Atualiza contador inicial
        self._update_counter()

        # Bind ESC para cancelar
        self.window.bind("<Escape>", lambda e: self._cancel())

    def _pre_select_years(self):
        """Pré-seleciona anos baseado na seleção inicial"""
        if not self.initial_selection:
            return

        initial_str = [str(y) for y in self.initial_selection]

        for i in range(self.listbox.size()):
            if self.listbox.get(i) in initial_str:
                self.listbox.selection_set(i)

    def _update_counter(self, event=None):
        """Atualiza contador de seleções"""
        count = len(self.listbox.curselection())
        total = len(self.years)
        self.counter_label.config(text=f"{count} de {total} selecionados")

    def _select_all(self):
        """Seleciona todos os anos"""
        for i in range(self.listbox.size()):
            self.listbox.selection_set(i)
        self._update_counter()

    def _clear_all(self):
        """Limpa todas as seleções"""
        self.listbox.selection_clear(0, tk.END)
        self._update_counter()

    def _confirm(self):
        """Confirma seleção"""
        selected = []
        for i in self.listbox.curselection():
            selected.append(self.listbox.get(i))
        self.result = selected
        self.window.destroy()

    def _cancel(self):
        """Cancela sem modificar"""
        self.result = None
        self.window.destroy()

    def show(self):
        """Mostra janela e retorna resultado"""
        self.window.wait_window()
        return self.result