#!/usr/bin/env python3
"""
Interface Gráfica para Configurações do Sistema
Permite ao usuário configurar preferências como diretório de download
"""

import sys
import os
import platform
import customtkinter as ctk
from tkinter import filedialog
import tkinter.messagebox as messagebox

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importa o gerenciador de configurações e fábrica de botões
from src.classes.config_page import ConfigManager
from src.view.modules.buttons import ButtonFactory


class GUI3:
    """Interface de configuração do sistema"""
    
    def __init__(self, parent_frame):
        """
        Inicializa a GUI de configurações
        
        Args:
            parent_frame: Frame pai onde a GUI será renderizada
        """
        self.parent_frame = parent_frame
        self.config_manager = ConfigManager()
        
        # Frame principal (inicialmente oculto)
        self.main_frame = ctk.CTkFrame(
            self.parent_frame,
            corner_radius=0,
            fg_color="#f8f9fa"
        )
        
        # Cria a interface
        self._criar_interface()
        
        # Inicialmente oculto
        self.ocultar()
    
    def _criar_interface(self):
        """Cria todos os elementos da interface"""
        # Container principal com padding
        container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=10,
            fg_color="white"
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título da página
        titulo = ctk.CTkLabel(
            container,
            text="Configurações do Sistema",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2c3e50"
        )
        titulo.pack(pady=(20, 30))
        
        # Seção: Diretório de Download
        self._criar_secao_diretorio(container)
        
        # Botões de ação no final
        self._criar_botoes_acao(container)
    
    def _criar_secao_diretorio(self, parent):
        """
        Cria a seção de configuração de diretório
        
        Args:
            parent: Container pai
        """
        # Frame da seção
        secao_frame = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color="#f8f9fa"
        )
        secao_frame.pack(fill="x", padx=20, pady=10)
        
        # Título da seção
        titulo_secao = ctk.CTkLabel(
            secao_frame,
            text="Diretório de Download",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#34495e"
        )
        titulo_secao.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Descrição
        descricao = ctk.CTkLabel(
            secao_frame,
            text="Escolha onde os arquivos baixados serão salvos",
            font=ctk.CTkFont(size=13),
            text_color="#7f8c8d"
        )
        descricao.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Frame para o campo de diretório e botão
        dir_frame = ctk.CTkFrame(
            secao_frame,
            fg_color="transparent"
        )
        dir_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Campo de texto para mostrar o diretório atual
        self.dir_entry = ctk.CTkEntry(
            dir_frame,
            placeholder_text="Diretório de download",
            font=ctk.CTkFont(size=14),
            height=40,
            state="readonly"
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Atualiza com o diretório atual
        current_dir = self.config_manager.get_download_directory()
        self.dir_entry.configure(state="normal")
        self.dir_entry.delete(0, "end")
        self.dir_entry.insert(0, current_dir)
        self.dir_entry.configure(state="readonly")
        
        # Botão para selecionar diretório
        self.btn_selecionar = ButtonFactory.create_primary_button(
            dir_frame,
            text="SELECIONAR PASTA",
            command=self._selecionar_diretorio,
            width=180
        )
        self.btn_selecionar.pack(side="right")
        
        # Botão para abrir pasta atual
        self.btn_abrir = ButtonFactory.create_folder_button(
            dir_frame,
            command=self._abrir_diretorio_atual,
            width=140,
            text="ABRIR PASTA"
        )
        self.btn_abrir.pack(side="right", padx=(0, 10))
    
    def _criar_botoes_acao(self, parent):
        """
        Cria botões de ação no final da página
        
        Args:
            parent: Container pai
        """
        # Frame para botões
        botoes_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        botoes_frame.pack(fill="x", padx=20, pady=(30, 20))
        
        # Botão redefinir padrões
        self.btn_redefinir = ButtonFactory.create_secondary_button(
            botoes_frame,
            text="REDEFINIR PADRÕES",
            command=self._redefinir_padroes,
            width=200
        )
        self.btn_redefinir.pack(side="left")
        
        # Espaço informativo à direita
        info_label = ctk.CTkLabel(
            botoes_frame,
            text="As configurações são salvas automaticamente",
            font=ctk.CTkFont(size=12),
            text_color="#95a5a6"
        )
        info_label.pack(side="right")
    
    def _selecionar_diretorio(self):
        """Abre diálogo para selecionar novo diretório de download"""
        # Obtém diretório atual como ponto de partida
        current_dir = self.config_manager.get_download_directory()
        
        # Abre diálogo de seleção de pasta
        selected_dir = filedialog.askdirectory(
            title="Selecione o diretório de download",
            initialdir=current_dir,
            mustexist=False
        )
        
        if selected_dir:
            # Salva o novo diretório
            if self.config_manager.set_download_directory(selected_dir):
                # Atualiza o campo de texto
                self.dir_entry.configure(state="normal")
                self.dir_entry.delete(0, "end")
                self.dir_entry.insert(0, selected_dir)
                self.dir_entry.configure(state="readonly")
                
                # Mostra mensagem de sucesso
                messagebox.showinfo(
                    "Configuração Salva",
                    f"Diretório de download atualizado para:\n{selected_dir}"
                )
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível salvar o diretório selecionado"
                )
    
    def _abrir_diretorio_atual(self):
        """Abre o diretório de download atual no explorador do sistema"""
        import subprocess
        
        diretorio = self.config_manager.get_download_directory()
        
        try:
            # Cria o diretório se não existir
            if not os.path.exists(diretorio):
                os.makedirs(diretorio)
            
            # Abre no explorador do sistema
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(diretorio)
            elif sistema == "Darwin":  # macOS
                subprocess.run(["open", diretorio])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", diretorio])
            else:
                messagebox.showwarning(
                    "Aviso",
                    f"Sistema operacional '{sistema}' não suportado para abrir pasta"
                )
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir pasta: {str(e)}"
            )
    
    def _redefinir_padroes(self):
        """Redefine todas as configurações para os valores padrão"""
        # Confirma com o usuário
        resposta = messagebox.askyesno(
            "Confirmar Redefinição",
            "Deseja realmente redefinir todas as configurações para os valores padrão?"
        )
        
        if resposta:
            # Redefine configurações
            self.config_manager.reset_to_defaults()
            
            # Atualiza o campo de diretório
            current_dir = self.config_manager.get_download_directory()
            self.dir_entry.configure(state="normal")
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, current_dir)
            self.dir_entry.configure(state="readonly")
            
            # Mostra mensagem
            messagebox.showinfo(
                "Configurações Redefinidas",
                "Todas as configurações foram redefinidas para os valores padrão"
            )
    
    def mostrar(self):
        """Mostra a GUI de configurações"""
        # Atualiza valores antes de mostrar
        current_dir = self.config_manager.get_download_directory()
        self.dir_entry.configure(state="normal")
        self.dir_entry.delete(0, "end")
        self.dir_entry.insert(0, current_dir)
        self.dir_entry.configure(state="readonly")
        
        # Mostra o frame
        self.main_frame.pack(fill="both", expand=True)
    
    def ocultar(self):
        """Oculta a GUI de configurações"""
        self.main_frame.pack_forget()