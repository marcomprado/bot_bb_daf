#!/usr/bin/env python3
"""
Interface gráfica moderna para o sistema de automação FPM
Serve como ponte visual para executar o main.py simplificado
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import sys
import threading
import subprocess
import platform
from datetime import datetime, timedelta
from typing import List
from classes.city_splitter import CitySplitter


def obter_caminho_recurso(nome_arquivo):
    """
    Obtém o caminho correto para um arquivo de recurso
    Funciona tanto em desenvolvimento quanto em executável empacotado
    
    Args:
        nome_arquivo (str): Nome do arquivo de recurso
        
    Returns:
        str: Caminho completo para o arquivo
    """
    try:
        # Se estamos em um executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # No executável, usa o diretório temporário do PyInstaller
            base_path = sys._MEIPASS
        else:
            # No desenvolvimento, usa o diretório do script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_path, nome_arquivo)
    except Exception:
        # Fallback para caminho relativo
        return nome_arquivo


def obter_caminho_dados(nome_arquivo):
    """
    Obtém o caminho correto para arquivos de dados (que precisam ser modificáveis)
    
    Args:
        nome_arquivo (str): Nome do arquivo de dados
        
    Returns:
        str: Caminho completo para o arquivo de dados
    """
    try:
        # Se estamos em um executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # Para arquivos de dados modificáveis, usa o diretório do usuário
            if platform.system() == "Darwin":  # macOS
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            elif platform.system() == "Windows":
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            else:  # Linux
                user_data_dir = os.path.expanduser("~/.sistema_fvn")
            
            # Cria o diretório se não existir
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)
                
            return os.path.join(user_data_dir, nome_arquivo)
        else:
            # No desenvolvimento, usa o diretório atual
            return nome_arquivo
    except Exception:
        # Fallback para caminho relativo
        return nome_arquivo


def copiar_arquivo_cidades_se_necessario():
    """
    Copia o arquivo cidades.txt para o diretório de dados do usuário se necessário
    """
    try:
        # Se estamos em um executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            arquivo_origem = obter_caminho_recurso("cidades.txt")
            arquivo_destino = obter_caminho_dados("cidades.txt")
            
            # Se o arquivo não existe no diretório do usuário, copia do recurso
            if not os.path.exists(arquivo_destino) and os.path.exists(arquivo_origem):
                import shutil
                shutil.copy2(arquivo_origem, arquivo_destino)
                print(f"Arquivo cidades.txt copiado para: {arquivo_destino}")
    except Exception as e:
        print(f"Aviso: Erro ao copiar arquivo cidades.txt - {e}")


class SeletorCidades:
    """Popup nativo para seleção de cidades"""
    
    def __init__(self, parent, lista_cidades):
        self.parent = parent
        self.lista_cidades = lista_cidades
        self.lista_cidades_filtrada = lista_cidades.copy()
        self.cidades_selecionadas = []
        self.indices_selecionados = set()  # Para manter track das seleções
        
        # Janela popup
        self.popup = tk.Toplevel(parent.janela)
        self.popup.title("Seleção de Cidades")
        self.popup.geometry("450x600")  # Aumentado para acomodar pesquisa
        self.popup.resizable(False, False)
        self.popup.configure(bg='#f8f9fa')
        self.popup.transient(parent.janela)
        self.popup.grab_set()
        
        # Centraliza popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (600 // 2)
        self.popup.geometry(f"450x600+{x}+{y}")
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria interface do seletor com melhor visibilidade e pesquisa"""
        # Título
        titulo = tk.Label(
            self.popup,
            text="Selecione as Cidades",
            font=("Arial", 18, "bold"),
            bg='#f8f9fa',
            fg='#212529',
            pady=10
        )
        titulo.pack()
        
        # Frame para pesquisa
        frame_pesquisa = tk.Frame(self.popup, bg='#f8f9fa')
        frame_pesquisa.pack(fill="x", padx=20, pady=(0, 10))
        
        # Label pesquisa
        label_pesquisa = tk.Label(
            frame_pesquisa,
            text="Pesquisar:",
            font=("Arial", 12, "bold"),
            bg='#f8f9fa',
            fg='#495057'
        )
        label_pesquisa.pack(side="top", anchor="w")
        
        # Container para campo de pesquisa e botão limpar
        container_pesquisa = tk.Frame(frame_pesquisa, bg='#f8f9fa')
        container_pesquisa.pack(fill="x", pady=(5, 0))
        
        # Campo de pesquisa
        self.entry_pesquisa = tk.Entry(
            container_pesquisa,
            font=("Arial", 12),
            bg='white',
            fg='#333333',
            relief='solid',
            borderwidth=1,
            insertbackground='#333333'
        )
        self.entry_pesquisa.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_pesquisa.bind('<KeyRelease>', self._on_pesquisa_change)
        self.entry_pesquisa.bind('<Escape>', lambda e: self._limpar_pesquisa())
        
        # Adiciona placeholder text
        self.entry_pesquisa.insert(0, "Digite para pesquisar...")
        self.entry_pesquisa.bind('<FocusIn>', self._on_entry_focus_in)
        self.entry_pesquisa.bind('<FocusOut>', self._on_entry_focus_out)
        self.entry_pesquisa.configure(fg='#999999')
        
        # Botão limpar pesquisa
        btn_limpar_pesquisa = tk.Button(
            container_pesquisa,
            text="Limpar",
            command=self._limpar_pesquisa,
            bg="#6c757d",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=6,
            relief='flat',
            cursor='hand2',
            borderwidth=0
        )
        btn_limpar_pesquisa.pack(side="right")
        
        # Label contador
        self.label_contador = tk.Label(
            frame_pesquisa,
            text=f"Mostrando {len(self.lista_cidades)} cidades",
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#6c757d'
        )
        self.label_contador.pack(side="top", anchor="w", pady=(5, 0))
        
        # Frame para listbox e scrollbar
        frame_lista = tk.Frame(self.popup, bg='#f8f9fa')
        frame_lista.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Listbox com seleção múltipla
        self.listbox = tk.Listbox(
            frame_lista,
            selectmode="multiple",
            font=("Arial", 12),
            height=15,  # Reduzido para acomodar pesquisa
            bg='white',
            fg='#333333',
            selectbackground='#0066cc',
            selectforeground='white',
            relief='solid',
            borderwidth=1,
            highlightthickness=0
        )
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame_lista, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Posiciona listbox e scrollbar
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Popula listbox inicial
        self._atualizar_listbox()
        
        # Permite confirmar com Enter na listbox
        self.listbox.bind('<Double-Button-1>', lambda e: self._confirmar())
        self.listbox.bind('<Return>', lambda e: self._confirmar())
        
        # Permite navegar do campo de pesquisa para a listbox com Tab
        self.entry_pesquisa.bind('<Tab>', self._focus_listbox)
        
        # Dá foco ao campo de pesquisa
        self.entry_pesquisa.focus_set()
        
        # Frame para os 3 botões principais
        frame_botoes = tk.Frame(self.popup, bg='#f8f9fa')
        frame_botoes.pack(fill="x", padx=20, pady=(0, 20))
        
        # Botão Limpar (esquerda)
        btn_limpar = tk.Button(
            frame_botoes,
            text="Limpar",
            command=self._limpar_selecao,
            bg="#6c757d",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            borderwidth=0
        )
        btn_limpar.pack(side="left")
        
        # Botão Cancelar (centro)
        btn_cancelar = tk.Button(
            frame_botoes,
            text="Cancelar",
            command=self._cancelar,
            bg="#dc3545",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            borderwidth=0
        )
        btn_cancelar.pack(side="left", padx=(15, 0))
        
        # Botão Confirmar (direita)
        btn_confirmar = tk.Button(
            frame_botoes,
            text="Confirmar Seleção",
            command=self._confirmar,
            bg="#28a745",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            borderwidth=0
        )
        btn_confirmar.pack(side="right")
        
        # Adicionar efeitos hover nos botões
        self._adicionar_hover_button(btn_limpar, "#6c757d", "#5a6268")
        self._adicionar_hover_button(btn_cancelar, "#dc3545", "#c82333")
        self._adicionar_hover_button(btn_confirmar, "#28a745", "#218838")
    
    def _adicionar_hover_button(self, button, cor_normal, cor_hover):
        """Adiciona efeito hover aos botões do popup"""
        def on_enter(event):
            button.configure(bg=cor_hover)
        
        def on_leave(event):
            button.configure(bg=cor_normal)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def _on_pesquisa_change(self, event):
        """Função chamada quando o usuário digita no campo de pesquisa"""
        texto_atual = self.entry_pesquisa.get()
        
        # Ignora se for o placeholder text
        if texto_atual == "Digite para pesquisar...":
            self._filtrar_cidades("")
            return
        
        termo_pesquisa = texto_atual.lower().strip()
        self._filtrar_cidades(termo_pesquisa)
    
    def _limpar_pesquisa(self):
        """Limpa o campo de pesquisa e mostra todas as cidades"""
        self.entry_pesquisa.delete(0, tk.END)
        self.entry_pesquisa.insert(0, "Digite para pesquisar...")
        self.entry_pesquisa.configure(fg='#999999')
        self._filtrar_cidades("")
    
    def _filtrar_cidades(self, termo):
        """Filtra as cidades baseado no termo de pesquisa"""
        if not termo:
            # Se não há termo, mostra todas as cidades
            self.lista_cidades_filtrada = self.lista_cidades.copy()
        else:
            # Filtra cidades que contêm o termo
            self.lista_cidades_filtrada = [
                cidade for cidade in self.lista_cidades 
                if termo in cidade.lower()
            ]
        
        # Atualiza a listbox e contador
        self._atualizar_listbox()
        self._atualizar_contador()
    
    def _atualizar_listbox(self):
        """Atualiza a listbox com as cidades filtradas mantendo seleções"""
        # Salva quais cidades estavam selecionadas pelo nome
        cidades_selecionadas_nomes = set()
        for i in self.listbox.curselection():
            cidade_original = self.lista_cidades_filtrada[i]
            cidades_selecionadas_nomes.add(cidade_original)
        
        # Limpa listbox
        self.listbox.delete(0, tk.END)
        
        # Adiciona cidades filtradas
        for cidade in self.lista_cidades_filtrada:
            self.listbox.insert(tk.END, cidade.title())
        
        # Restaura seleções
        for i, cidade in enumerate(self.lista_cidades_filtrada):
            if cidade in cidades_selecionadas_nomes:
                self.listbox.selection_set(i)
    
    def _atualizar_contador(self):
        """Atualiza o contador de cidades mostradas"""
        total_filtradas = len(self.lista_cidades_filtrada)
        total_geral = len(self.lista_cidades)
        
        if total_filtradas == total_geral:
            texto = f"Mostrando {total_geral} cidades"
        else:
            texto = f"Mostrando {total_filtradas} de {total_geral} cidades"
        
        self.label_contador.configure(text=texto)
    
    def _on_entry_focus_in(self, event):
        """Remove placeholder quando o campo ganha foco"""
        if self.entry_pesquisa.get() == "Digite para pesquisar...":
            self.entry_pesquisa.delete(0, tk.END)
            self.entry_pesquisa.configure(fg='#333333')
    
    def _on_entry_focus_out(self, event):
        """Adiciona placeholder quando o campo perde foco e está vazio"""
        if not self.entry_pesquisa.get().strip():
            self.entry_pesquisa.delete(0, tk.END)
            self.entry_pesquisa.insert(0, "Digite para pesquisar...")
            self.entry_pesquisa.configure(fg='#999999')
            # Mostra todas as cidades quando limpa a pesquisa
            self._filtrar_cidades("")
    
    def _focus_listbox(self, event):
        """Move foco para a listbox"""
        self.listbox.focus_set()
        if self.listbox.size() > 0:
            self.listbox.selection_set(0)  # Seleciona primeiro item
        return "break"  # Previne comportamento padrão do Tab
    
    def _limpar_selecao(self):
        """Limpa toda a seleção"""
        self.listbox.selection_clear(0, tk.END)
    
    def _confirmar(self):
        """Confirma seleção e fecha popup"""
        indices_selecionados = self.listbox.curselection()
        self.cidades_selecionadas = [
            self.lista_cidades_filtrada[i] for i in indices_selecionados
        ]
        self.popup.destroy()
    
    def _cancelar(self):
        """Cancela seleção"""
        self.cidades_selecionadas = []
        self.popup.destroy()
    
    def obter_selecao(self):
        """Retorna cidades selecionadas"""
        self.popup.wait_window()  # Aguarda popup fechar
        return self.cidades_selecionadas


class GUIMain:
    """Interface gráfica principal que executa main.py"""
    
    def __init__(self):
        # Configuração do tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Copia arquivo cidades.txt se necessário (para executável)
        copiar_arquivo_cidades_se_necessario()
        
        # Janela principal - RESPONSIVA
        self.janela = ctk.CTk()
        self.janela.title("Sistema FVN")
        self.janela.geometry("750x700")  # Altura reduzida
        self.janela.resizable(True, True)
        self.janela.minsize(600, 550)  # Tamanho mínimo responsivo
        self.janela.configure(fg_color="#f8f9fa")
        
        # Configura ícone da aplicação
        self._configurar_icone()
        
        # Estado da execução
        self.executando = False
        self.processo = None
        self.thread_execucao = None
        self._cancelado = False
        
        # Dados
        self.lista_cidades = []
        self.cidades_selecionadas = []
        
        # Variáveis de data
        self.data_inicial_var = ctk.StringVar()
        self.data_final_var = ctk.StringVar()
        
        # Sistema de divisão de cidades - usa caminho correto
        caminho_cidades = obter_caminho_dados("cidades.txt")
        self.city_splitter = CitySplitter(caminho_cidades)
        self.num_instancias = 1
        self.modo_execucao = "individual"  # ou "paralelo"
        
        self._configurar_datas_padrao()
        self._centralizar_janela()
        self._criar_interface()
        self._carregar_cidades()
    
    def _configurar_icone(self):
        """Configura o ícone da aplicação se disponível"""
        try:
            # Lista de possíveis caminhos para o ícone
            caminhos_icone = [
                obter_caminho_recurso("assets/app_icon.ico"),
                obter_caminho_recurso("assets/fvn_icon.ico"), 
                obter_caminho_recurso("assets/logo.ico"),
                obter_caminho_recurso("app_icon.ico"),
                obter_caminho_recurso("icon.ico")
            ]
            
            # Procura pelo ícone nos caminhos possíveis
            icone_encontrado = None
            for caminho in caminhos_icone:
                if os.path.exists(caminho):
                    icone_encontrado = caminho
                    break
            
            # Se encontrou um ícone, aplica à janela
            if icone_encontrado:
                # Para CustomTkinter/Tkinter, usa iconbitmap
                self.janela.iconbitmap(icone_encontrado)
                print(f"Ícone carregado: {icone_encontrado}")
            else:
                # Se não encontrou ícone, apenas informa (não é erro crítico)
                print("Nenhum ícone encontrado. Use 'python assets/convert_to_icon.py sua_logo.png assets/app_icon.ico' para criar um.")
                
        except Exception as e:
            # Se houver erro ao carregar ícone, continua sem ele
            print(f"Aviso: Não foi possível carregar ícone - {e}")
            pass
    
    def _configurar_datas_padrao(self):
        """Configura datas padrão"""
        data_atual = datetime.now()
        data_inicial = data_atual - timedelta(days=30)
        
        self.data_inicial_var.set(data_inicial.strftime("%d/%m/%Y"))
        self.data_final_var.set(data_atual.strftime("%d/%m/%Y"))
    
    def _centralizar_janela(self):
        """Centraliza janela na tela"""
        self.janela.update_idletasks()
        largura = self.janela.winfo_width()
        altura = self.janela.winfo_height()
        pos_x = (self.janela.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.janela.winfo_screenheight() // 2) - (altura // 2)
        self.janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    
    def _criar_interface(self):
        """Cria a interface principal com scroll"""
        # Frame scrollable principal
        self.main_frame = ctk.CTkScrollableFrame(
            self.janela,
            corner_radius=0,
            fg_color="#f8f9fa"
        )
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Cabeçalho
        self._criar_cabecalho(self.main_frame)
        
        # Seções principais
        self._criar_secao_datas(self.main_frame)
        self._criar_secao_cidades(self.main_frame)
        self._criar_secao_execucao_paralela(self.main_frame)
        self._criar_botoes_acao(self.main_frame)
    
    def _criar_cabecalho(self, parent):
        """Cria cabeçalho limpo sem emojis"""
        # Container do cabeçalho
        frame_cabecalho = ctk.CTkFrame(
            parent,
            corner_radius=0,
            fg_color="#ffffff",
            border_width=0,
            border_color="#dee2e6"
        )
        frame_cabecalho.pack(fill="x", padx=0, pady=(0, 30))
        
        # Título principal
        label_titulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Sistema FVN",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#212529"
        )
        label_titulo.pack(pady=(30, 5))
        
        # Subtítulo
        label_subtitulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Automação de consultas - Banco do Brasil",
            font=ctk.CTkFont(size=16),
            text_color="#6c757d"
        )
        label_subtitulo.pack(pady=(0, 30))
    
    def _criar_secao_datas(self, parent):
        """Cria seção de seleção de datas - RESPONSIVA"""
        # Frame das datas
        frame_datas = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        frame_datas.pack(fill="x", padx=20, pady=(0, 20))  # Padding reduzido
        
        # Título da seção
        label_datas = ctk.CTkLabel(
            frame_datas,
            text="Período de Consulta",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_datas.pack(pady=(15, 10))  # Padding reduzido
        
        # Container dos campos de data - RESPONSIVO
        container_campos = ctk.CTkFrame(frame_datas, fg_color="transparent")
        container_campos.pack(fill="x", padx=15, pady=(0, 15))
        
        # Configurar grid responsivo
        container_campos.grid_columnconfigure(0, weight=1)
        container_campos.grid_columnconfigure(1, weight=1)
        
        # Data Inicial
        frame_data_inicial = ctk.CTkFrame(container_campos, fg_color="transparent")
        frame_data_inicial.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        label_inicial = ctk.CTkLabel(
            frame_data_inicial,
            text="Data Inicial:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_inicial.pack()
        
        self.entry_data_inicial = ctk.CTkEntry(
            frame_data_inicial,
            textvariable=self.data_inicial_var,
            placeholder_text="DD/MM/AAAA",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=15,
            justify="center",
            border_width=2,
            border_color="#ced4da"
        )
        self.entry_data_inicial.pack(fill="x", pady=(5, 0))
        
        # Data Final
        frame_data_final = ctk.CTkFrame(container_campos, fg_color="transparent")
        frame_data_final.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        label_final = ctk.CTkLabel(
            frame_data_final,
            text="Data Final:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_final.pack()
        
        self.entry_data_final = ctk.CTkEntry(
            frame_data_final,
            textvariable=self.data_final_var,
            placeholder_text="DD/MM/AAAA",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=15,
            justify="center",
            border_width=2,
            border_color="#ced4da"
        )
        self.entry_data_final.pack(fill="x", pady=(5, 0))
    
    def _criar_secao_cidades(self, parent):
        """Cria seção de seleção de cidades - RESPONSIVA e SIMPLIFICADA"""
        # Frame das cidades
        frame_cidades = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        frame_cidades.pack(fill="x", padx=20, pady=(0, 20))
        
        # Título da seção
        label_cidades = ctk.CTkLabel(
            frame_cidades,
            text="Seleção de Cidades",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_cidades.pack(pady=(15, 10))
        
        # Container principal dos botões - RESPONSIVO com grid (só 2 botões agora)
        container_botoes_principais = ctk.CTkFrame(
            frame_cidades, 
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#dee2e6"
        )
        container_botoes_principais.pack(fill="x", padx=15, pady=(0, 10))
        
        # Configurar grid responsivo - 2 colunas iguais
        container_botoes_principais.grid_columnconfigure(0, weight=1)
        container_botoes_principais.grid_columnconfigure(1, weight=1)
        
        # APENAS 2 BOTÕES COM TAMANHO PADRONIZADO: 240x55px
        
        # Botão Todas as Cidades
        self.botao_todas = ctk.CTkButton(
            container_botoes_principais,
            text="Todas as Cidades",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=55,
            corner_radius=27,
            fg_color="#0066cc",
            hover_color="#0052a3",
            command=self._selecionar_todas_cidades,
            width=240
        )
        self.botao_todas.grid(row=0, column=0, padx=10, pady=12, sticky="ew")
        
        # Botão Selecionar Individualmente
        self.botao_individual = ctk.CTkButton(
            container_botoes_principais,
            text="Selecionar Individual",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=55,
            corner_radius=27,
            fg_color="transparent",
            border_width=3,
            border_color="#0066cc",
            text_color="#0066cc",
            hover_color="#e6f3ff",
            command=self._abrir_seletor_individual,
            width=240
        )
        self.botao_individual.grid(row=0, column=1, padx=10, pady=12, sticky="ew")
        
        # Adicionar efeitos hover para ambos botões
        self._adicionar_efeito_hover(self.botao_todas)
        self._adicionar_efeito_hover(self.botao_individual)
        
        # Label de status da seleção
        self.label_status_selecao = ctk.CTkLabel(
            frame_cidades,
            text="Clique em um dos botões acima para selecionar cidades",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#495057"
        )
        self.label_status_selecao.pack(pady=(0, 15))
    
    def _criar_secao_execucao_paralela(self, parent):
        """Cria seção de execução paralela - NOVA FUNCIONALIDADE"""
        # Frame da execução paralela
        frame_paralela = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        frame_paralela.pack(fill="x", padx=20, pady=(0, 20))
        
        # Título da seção
        label_titulo = ctk.CTkLabel(
            frame_paralela,
            text="Execução Paralela",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_titulo.pack(pady=(15, 10))
        
        # Container dos controles - Grid responsivo
        container_controles = ctk.CTkFrame(
            frame_paralela,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#dee2e6"
        )
        container_controles.pack(fill="x", padx=15, pady=(0, 10))
        
        # Configurar grid - 3 colunas
        container_controles.grid_columnconfigure(0, weight=1)
        container_controles.grid_columnconfigure(1, weight=1)
        container_controles.grid_columnconfigure(2, weight=1)
        
        # Label modo execução
        label_modo = ctk.CTkLabel(
            container_controles,
            text="Modo:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_modo.grid(row=0, column=0, padx=10, pady=12, sticky="w")
        
        # Dropdown modo execução
        self.dropdown_modo = ctk.CTkOptionMenu(
            container_controles,
            values=["Individual", "Paralelo"],
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            command=self._on_modo_change,
            width=140,
            height=35
        )
        self.dropdown_modo.set("Individual")
        self.dropdown_modo.grid(row=0, column=1, padx=10, pady=12, sticky="ew")
        
        # Campo número de instâncias
        self.entry_instancias = ctk.CTkEntry(
            container_controles,
            placeholder_text="Instâncias",
            font=ctk.CTkFont(size=12),
            width=100,
            height=35,
            justify="center",
            state="disabled"
        )
        self.entry_instancias.insert(0, "1")
        self.entry_instancias.grid(row=0, column=2, padx=10, pady=12, sticky="ew")
        
        # Botão calcular distribuição
        self.botao_calcular = ctk.CTkButton(
            frame_paralela,
            text="Calcular Distribuição",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=22,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self._calcular_distribuicao,
            state="disabled",
            width=240
        )
        self.botao_calcular.pack(pady=(0, 10))
        
        # Label de status da distribuição
        self.label_distribuicao = ctk.CTkLabel(
            frame_paralela,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#495057",
            justify="left"
        )
        self.label_distribuicao.pack(pady=(0, 15))
    
    def _on_modo_change(self, valor):
        """Callback quando o modo de execução é alterado"""
        if valor == "Paralelo":
            self.modo_execucao = "paralelo"
            self.entry_instancias.configure(state="normal")
            self.botao_calcular.configure(state="normal")
            self.entry_instancias.delete(0, "end")
            self.entry_instancias.insert(0, "2")
        else:
            self.modo_execucao = "individual"
            self.entry_instancias.configure(state="disabled")
            self.botao_calcular.configure(state="disabled")
            self.entry_instancias.delete(0, "end")
            self.entry_instancias.insert(0, "1")
            self.label_distribuicao.configure(text="")
    
    def _calcular_distribuicao(self):
        """Calcula e exibe a distribuição das cidades"""
        try:
            num_instancias = int(self.entry_instancias.get())
            
            # Valida número de instâncias
            valido, mensagem = self.city_splitter.validar_instancias(num_instancias)
            if not valido:
                self._mostrar_erro(mensagem)
                return
            
            # Calcula distribuição
            resumo = self.city_splitter.obter_resumo_distribuicao(num_instancias)
            self.label_distribuicao.configure(text=resumo)
            self.num_instancias = num_instancias
            
        except ValueError:
            self._mostrar_erro("Digite um número válido de instâncias")
    
    def _criar_botoes_acao(self, parent):
        """Cria botões de ação principais - RESPONSIVO"""
        # Container para os botões
        frame_acoes = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="white",
            border_width=2,
            border_color="#0066cc"
        )
        frame_acoes.pack(fill="x", padx=20, pady=(10, 30))
        
        # Container interno para centralizar botões
        container_botoes = ctk.CTkFrame(frame_acoes, fg_color="transparent")
        container_botoes.pack(pady=15)
        
        # Botão Executar - TAMANHO PADRONIZADO
        self.botao_executar = ctk.CTkButton(
            container_botoes,
            text="EXECUTAR PROCESSAMENTO",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=55,  # MESMO TAMANHO DOS OUTROS
            corner_radius=27,
            fg_color="#0066cc",
            hover_color="#0052a3",
            command=self._executar_main,
            width=300  # Largura ajustada
        )
        self.botao_executar.pack(side="left", padx=10)
        
        # Botão Abrir Pasta - NOVO
        self.botao_abrir_pasta = ctk.CTkButton(
            container_botoes,
            text="ABRIR ARQUIVOS",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=55,
            corner_radius=27,
            fg_color="#28a745",
            hover_color="#218838",
            command=self._abrir_pasta_arquivos,
            width=200
        )
        self.botao_abrir_pasta.pack(side="left", padx=10)
        
        # Adicionar efeito hover aos botões
        self._adicionar_efeito_hover(self.botao_executar)
        self._adicionar_efeito_hover(self.botao_abrir_pasta)
    
    def _adicionar_efeito_hover(self, botao):
        """Adiciona efeito hover de crescimento aos botões - ATUALIZADO"""
        def on_enter(event):
            # Cresce levemente o botão
            current_width = botao.cget("width")
            current_height = botao.cget("height")
            botao.configure(width=current_width + 8, height=current_height + 3)
        
        def on_leave(event):
            # Volta ao tamanho original baseado no tipo de botão
            if botao in [self.botao_todas, self.botao_individual]:
                botao.configure(width=240, height=55)  # Botões padrão atualizados
            elif botao == self.botao_executar:
                botao.configure(width=300, height=55)  # Botão executar
            elif botao == self.botao_abrir_pasta:
                botao.configure(width=200, height=55)  # Botão abrir pasta
        
        # Bind dos eventos de mouse
        botao.bind("<Enter>", on_enter)
        botao.bind("<Leave>", on_leave)
    
    def _mostrar_erro(self, mensagem):
        """Mostra mensagem de erro"""
        messagebox.showerror("Erro", mensagem)
    
    def _mostrar_info(self, mensagem):
        """Mostra mensagem informativa"""
        messagebox.showinfo("Informação", mensagem)
    
    def _mostrar_popup_processo_terminado(self):
        """Mostra popup padrão quando processo é terminado"""
        messagebox.showinfo("Processo Finalizado", "processo foi terminado")
    
    def _abrir_pasta_arquivos(self):
        """Abre a pasta de arquivos baixados no explorador do sistema"""
        try:
            # Caminho da pasta de arquivos baixados - usa função para obter caminho correto
            pasta_arquivos = obter_caminho_dados("arquivos_baixados")
            
            # Cria a pasta se não existir
            if not os.path.exists(pasta_arquivos):
                os.makedirs(pasta_arquivos)
                print(f"Pasta criada: {pasta_arquivos}")
            
            # Detecta o sistema operacional e abre a pasta
            sistema = platform.system()
            
            if sistema == "Windows":
                # Windows - usa os.startfile ou explorer
                os.startfile(pasta_arquivos)
            elif sistema == "Darwin":
                # macOS - usa open
                subprocess.run(["open", pasta_arquivos])
            elif sistema == "Linux":
                # Linux - usa xdg-open
                subprocess.run(["xdg-open", pasta_arquivos])
            else:
                # Sistema não suportado
                self._mostrar_erro(f"Sistema operacional '{sistema}' não suportado para abrir pasta")
                return
            
            print(f"Pasta aberta: {pasta_arquivos}")
            
        except FileNotFoundError:
            self._mostrar_erro("Erro ao abrir pasta: comando do sistema não encontrado")
        except PermissionError:
            self._mostrar_erro("Erro ao abrir pasta: sem permissão de acesso")
        except Exception as e:
            self._mostrar_erro(f"Erro ao abrir pasta: {str(e)}")
    
    def _validar_dados(self):
        """Valida se os dados estão corretos"""
        # Verifica se há cidades selecionadas
        if not self.cidades_selecionadas:
            self._mostrar_erro("Por favor, selecione pelo menos uma cidade!")
            return False
        
        # Verifica formato das datas
        try:
            datetime.strptime(self.data_inicial_var.get(), "%d/%m/%Y")
            datetime.strptime(self.data_final_var.get(), "%d/%m/%Y")
        except ValueError:
            self._mostrar_erro("Formato de data inválido! Use DD/MM/AAAA")
            return False
        
        return True
    
    def _habilitar_interface(self, habilitado=True):
        """Habilita/desabilita elementos da interface"""
        # Atualiza estado
        self.executando = not habilitado
        
        # Atualiza botões de seleção de cidades
        self.botao_todas.configure(state="normal" if habilitado else "disabled")
        self.botao_individual.configure(state="normal" if habilitado else "disabled")
        
        # Atualiza controles de execução paralela
        self.dropdown_modo.configure(state="normal" if habilitado else "disabled")
        if habilitado and self.modo_execucao == "paralelo":
            self.entry_instancias.configure(state="normal")
            self.botao_calcular.configure(state="normal")
        else:
            self.entry_instancias.configure(state="disabled")
            self.botao_calcular.configure(state="disabled")
        
        # Botão abrir pasta sempre fica habilitado
        self.botao_abrir_pasta.configure(state="normal")
        
        # Atualiza botão executar/cancelar
        if habilitado:
            # Modo normal - botão azul "EXECUTAR"
            self.botao_executar.configure(
                text="EXECUTAR PROCESSAMENTO",
                fg_color="#0066cc",
                hover_color="#0052a3",
                border_width=0,
                text_color="white",
                state="normal"
            )
        else:
            # Modo execução - botão vermelho "CANCELAR"
            self.botao_executar.configure(
                text="CANCELAR PROCESSAMENTO",
                fg_color="transparent",
                hover_color="#ffebee",
                border_width=3,
                border_color="#dc3545",
                text_color="#dc3545",
                state="normal"
            )
    
    def _executar_main(self):
        """Executa o main.py como subprocess ou cancela execução"""
        if self.executando:
            # Se está executando, cancela
            self._cancelar_execucao()
            return
        
        # Valida dados
        if not self._validar_dados():
            return
        
        try:
            if self.modo_execucao == "paralelo":
                self._executar_modo_paralelo()
            else:
                self._executar_modo_individual()
                
        except Exception as e:
            self._mostrar_erro(f"Erro ao executar: {str(e)}")
            self._habilitar_interface(True)
    
    def _executar_modo_individual(self):
        """Executa modo individual (uma instância)"""
        # Salva cidades selecionadas no arquivo
        self._salvar_cidades_selecionadas()
        
        # Desabilita interface e muda botão para cancelar
        self._habilitar_interface(False)
        
        # Executa main.py em thread separada
        def executar_subprocess():
            try:
                self.processo = subprocess.Popen(
                    [sys.executable, "main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.getcwd()
                )
                
                # Aguarda processo terminar
                stdout, stderr = self.processo.communicate()
                
                # Cria objeto resultado simulando subprocess.run
                class ResultadoProcesso:
                    def __init__(self, returncode, stdout, stderr):
                        self.returncode = returncode
                        self.stdout = stdout
                        self.stderr = stderr
                
                resultado = ResultadoProcesso(
                    self.processo.returncode,
                    stdout,
                    stderr
                )
                
                # Reabilita interface na thread principal
                if not self._cancelado:
                    self.janela.after(0, self._finalizar_execucao, resultado)
                
            except Exception as e:
                # Reabilita interface em caso de erro
                if not self._cancelado:
                    self.janela.after(0, self._finalizar_execucao_erro, str(e))
        
        # Inicializa flag de cancelamento
        self._cancelado = False
        
        # Inicia thread
        self.thread_execucao = threading.Thread(target=executar_subprocess, daemon=True)
        self.thread_execucao.start()

    def _executar_modo_paralelo(self):
        """Executa modo paralelo (múltiplas instâncias)"""
        # Divide as cidades em arquivos para cada instância
        resultado = self.city_splitter.dividir_cidades(self.num_instancias)
        
        if not resultado.get('sucesso'):
            self._mostrar_erro(f"Erro ao dividir cidades: {resultado.get('erro')}")
            return
        
        # Desabilita interface e muda botão para cancelar
        self._habilitar_interface(False)
        
        # Lista para guardar os processos
        self.processos_paralelos = []
        
        # Executa múltiplas instâncias em thread separada
        def executar_processos_paralelos():
            try:
                arquivos_criados = resultado['arquivos_criados']
                
                # Inicia todos os processos
                for arquivo_info in arquivos_criados:
                    # Usa o script main_parallel.py passando o arquivo específico
                    processo = subprocess.Popen(
                        [sys.executable, "main_parallel.py", arquivo_info['arquivo']],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=os.getcwd()
                    )
                    
                    self.processos_paralelos.append({
                        'processo': processo,
                        'instancia': arquivo_info['instancia'],
                        'arquivo': arquivo_info['arquivo']
                    })
                
                # Aguarda todos os processos terminarem
                resultados = []
                for proc_info in self.processos_paralelos:
                    stdout, stderr = proc_info['processo'].communicate()
                    resultados.append({
                        'instancia': proc_info['instancia'],
                        'returncode': proc_info['processo'].returncode,
                        'stdout': stdout,
                        'stderr': stderr
                    })
                    
                    # Remove arquivo temporário de cidades
                    try:
                        os.remove(proc_info['arquivo'])
                    except:
                        pass
                
                # Reabilita interface na thread principal
                if not self._cancelado:
                    self.janela.after(0, self._finalizar_execucao_paralela, resultados)
            
            except Exception as e:
                # Reabilita interface em caso de erro
                if not self._cancelado:
                    self.janela.after(0, self._finalizar_execucao_erro, str(e))
        
        # Inicializa flag de cancelamento
        self._cancelado = False
        
        # Inicia thread
        self.thread_execucao = threading.Thread(target=executar_processos_paralelos, daemon=True)
        self.thread_execucao.start()
    
    def _finalizar_execucao_paralela(self, resultados):
        """Finaliza execução paralela e mostra resultados"""
        if self._cancelado:
            return
            
            self._habilitar_interface(True)
        
        # Sempre mostra popup padrão de término do processo
        self._mostrar_popup_processo_terminado()
    
    def _cancelar_execucao(self):
        """Cancela a execução em andamento"""
        try:
            self._cancelado = True
            
            # Cancela execução individual
            if hasattr(self, 'processo') and self.processo:
                # Termina o processo
                self.processo.terminate()
                
                # Aguarda um pouco e força encerramento se necessário
                try:
                    self.processo.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.processo.kill()
                    self.processo.wait()
            
            # Cancela execução paralela
            if hasattr(self, 'processos_paralelos') and self.processos_paralelos:
                for proc_info in self.processos_paralelos:
                    try:
                        processo = proc_info['processo']
                        processo.terminate()
                        
                        # Aguarda um pouco e força encerramento se necessário
                        try:
                            processo.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            processo.kill()
                            processo.wait()
                        
                        # Remove arquivo temporário de cidades
                        try:
                            os.remove(proc_info['arquivo'])
                        except:
                            pass
                    except:
                        pass
            
            # Reabilita interface
            self._habilitar_interface(True)
            
            # Mostra mensagem padrão de término do processo
            self._mostrar_popup_processo_terminado()
            
        except Exception as e:
            self._mostrar_erro(f"Erro ao cancelar: {str(e)}")
            self._habilitar_interface(True)
    
    def _finalizar_execucao(self, resultado):
        """Finaliza execução e mostra resultado"""
        if self._cancelado:
            return
            
        self._habilitar_interface(True)
        
        # Sempre mostra popup padrão de término do processo
        self._mostrar_popup_processo_terminado()
    
    def _finalizar_execucao_erro(self, erro):
        """Finaliza execução em caso de erro"""
        if self._cancelado:
            return
            
        self._habilitar_interface(True)
        
        # Sempre mostra popup padrão de término do processo
        self._mostrar_popup_processo_terminado()
    
    def _salvar_cidades_selecionadas(self):
        """Salva cidades selecionadas no arquivo listed_cities.txt (dinâmico)"""
        try:
            caminho_arquivo = obter_caminho_dados("listed_cities.txt")
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                for cidade in self.cidades_selecionadas:
                    arquivo.write(f"{cidade}\n")
        except Exception as e:
            raise Exception(f"Erro ao salvar cidades: {str(e)}")
    
    def _carregar_cidades(self):
        """Carrega lista de cidades do arquivo"""
        try:
            caminho_arquivo = obter_caminho_dados("cidades.txt")
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                    self.lista_cidades = [linha.strip() for linha in arquivo if linha.strip()]
        except Exception as e:
            self._mostrar_erro(f"Erro ao carregar cidades: {str(e)}")
            self.lista_cidades = []
    
    def _selecionar_todas_cidades(self):
        """Seleciona todas as cidades disponíveis"""
        if not self.lista_cidades:
            self._mostrar_erro("Nenhuma cidade disponível!")
            return
        
        self.cidades_selecionadas = self.lista_cidades.copy()
        self.label_status_selecao.configure(
            text=f"Todas as cidades selecionadas ({len(self.cidades_selecionadas)} cidades)"
        )
    
    def _abrir_seletor_individual(self):
        """Abre popup nativo para seleção individual"""
        seletor = SeletorCidades(self, self.lista_cidades)
        resultado = seletor.obter_selecao()
        
        if resultado:
            self.cidades_selecionadas = resultado
            self._atualizar_status_selecao()
    
    def _limpar_selecao(self):
        """Limpa a seleção de cidades"""
        self.cidades_selecionadas = []
        self.label_status_selecao.configure(
            text="Clique em um dos botões acima para selecionar cidades"
        )
    
    def _atualizar_status_selecao(self):
        """Atualiza o texto de status da seleção"""
        if not self.cidades_selecionadas:
            texto = "Clique em um dos botões acima para selecionar cidades"
        elif len(self.cidades_selecionadas) == len(self.lista_cidades):
            texto = f"Todas as cidades selecionadas ({len(self.cidades_selecionadas)} cidades)"
        else:
            texto = f"{len(self.cidades_selecionadas)} cidades selecionadas"
        
        self.label_status_selecao.configure(text=texto)
    
    def _executar_script_direto(self, modo="individual", arquivo_cidades=None):
        """Executa o script diretamente sem subprocess (para executáveis)"""
        try:
            # Importa os módulos necessários
            from classes.file_manager import FileManager
            from classes.date_calculator import DateCalculator
            from classes.data_extractor import DataExtractor
            from classes.web_scraping_bot import WebScrapingBot
            
            # Redireciona stdout para capturar a saída
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                print("=" * 60)
                print("SISTEMA DE AUTOMAÇÃO WEB - ARRECADAÇÃO FEDERAL")
                print("=" * 60)
                
                # 1. Carrega cidades
                # Importa as classes necessárias do diretório correto
                import sys
                import os
                
                # Adiciona o diretório classes ao path se necessário
                if hasattr(sys, '_MEIPASS'):
                    # No executável, os módulos estão no diretório temporário
                    classes_path = os.path.join(sys._MEIPASS, 'classes')
                    if classes_path not in sys.path:
                        sys.path.insert(0, classes_path)
                
                if arquivo_cidades:
                    # Para modo paralelo, o arquivo já vem com caminho completo
                    file_manager = FileManager(arquivo_cidades)
                else:
                    # Para modo individual, usa o arquivo padrão
                    # Não usa obter_caminho_dados pois FileManager já faz isso internamente
                    file_manager = FileManager("listed_cities.txt")
                
                print(f"Arquivo de cidades: {file_manager.arquivo_cidades}")
                print(f"Arquivo existe? {os.path.exists(file_manager.arquivo_cidades)}")
                
                if not file_manager.verificar_arquivo_existe():
                    print("Use a interface gráfica para selecionar cidades primeiro.")
                    return {"returncode": 1, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()}
                
                cidades = file_manager.carregar_cidades()
                if not file_manager.validar_lista_cidades(cidades):
                    return {"returncode": 1, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()}
                
                # 2. Calcula datas
                date_calculator = DateCalculator()
                data_inicial, data_final = date_calculator.obter_datas_formatadas()
                
                # 3. Inicializa componentes
                data_extractor = DataExtractor()
                bot = WebScrapingBot()
                bot.configurar_extrator_dados(data_extractor)
                
                # 4. Configura navegador
                print("Configurando navegador...")
                if not bot.configurar_navegador():
                    print("Falha na configuração do navegador Chrome")
                    return {"returncode": 1, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()}
                
                # 5. Abre página inicial
                print("Abrindo página inicial...")
                if not bot.abrir_pagina_inicial():
                    print("Falha ao carregar página inicial")
                    bot.fechar_navegador()
                    return {"returncode": 1, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()}
                
                # 6. Processa todas as cidades
                print(f"Processando {len(cidades)} cidades...")
                estatisticas = bot.processar_lista_cidades(cidades, data_inicial, data_final)
                
                # 7. Fecha navegador automaticamente
                print("Fechando navegador...")
                bot.fechar_navegador()
                
                # 8. Exibe estatísticas finais
                print(f"\nProcessamento concluído:")
                print(f"   Total: {estatisticas['total']} cidades")
                print(f"   Sucessos: {estatisticas['sucessos']}")
                print(f"   Erros: {estatisticas['erros']}")
                print(f"   Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%")
                
                # Retorna resultado
                returncode = 0 if estatisticas['erros'] == 0 else 1
                return {
                    "returncode": returncode,
                    "stdout": stdout_buffer.getvalue(),
                    "stderr": stderr_buffer.getvalue()
                }
                
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuário")
            if 'bot' in locals():
                bot.fechar_navegador()
            return {"returncode": 130, "stdout": stdout_buffer.getvalue(), "stderr": stderr_buffer.getvalue()}
        except Exception as e:
            print(f"Erro inesperado: {e}")
            if 'bot' in locals():
                bot.fechar_navegador()
            return {"returncode": 1, "stdout": stdout_buffer.getvalue(), "stderr": str(e)}

    def executar(self):
        """Executa loop principal da interface"""
        self.janela.mainloop()


def main():
    """Função principal"""
    try:
        interface = GUIMain()
        interface.executar()
    except Exception as e:
        print(f"Erro ao inicializar interface: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 