#!/usr/bin/env python3
"""
ButtonFactory - F�brica de bot�es padronizados para as interfaces gr�ficas
Centraliza a cria��o e estiliza��o de bot�es, garantindo consist�ncia visual
"""

import customtkinter as ctk
import os
from PIL import Image


class ButtonFactory:
    """F�brica para criar bot�es padronizados com estilos consistentes"""
    
    # Estilos padrão
    STYLES = {
        'primary': {
            'fg_color': '#0066cc',
            'hover_color': '#0052a3',
            'text_color': 'white',
            'border_width': 0
        },
        'success': {
            'fg_color': '#28a745',
            'hover_color': '#218838',
            'text_color': 'white',
            'border_width': 0
        },
        'danger': {
            'fg_color': '#dc3545',
            'hover_color': '#d32535',
            'text_color': 'white',
            'border_width': 0
        },
        'secondary': {
            'fg_color': '#6c757d',
            'hover_color': '#5a6268',
            'text_color': 'white',
            'border_width': 0
        },
        'cancel': {
            'fg_color': 'transparent',
            'hover_color': '#ffebee',
            'text_color': '#dc3545',
            'border_width': 3,
            'border_color': '#dc3545'
        },
        'tab_active': {
            'fg_color': '#ffffff',
            'text_color': '#0066cc',
            'border_width': 2,
            'border_color': '#0066cc',
            'hover_color': '#f0f8ff'
        },
        'tab_inactive': {
            'fg_color': '#f0f0f0',
            'text_color': '#6c757d',
            'border_width': 1,
            'border_color': '#dee2e6',
            'hover_color': '#e9ecef'
        },
        'icon_button': {
            'fg_color': '#ffffff',
            'text_color': '#0066cc',
            'border_width': 1,
            'border_color': '#dee2e6',
            'hover_color': '#f0f8ff'
        },
        'icon_button_active': {
            'fg_color': '#f0f8ff',
            'text_color': '#0066cc',
            'border_width': 2,
            'border_color': '#0066cc',
            'hover_color': '#e6f2ff'
        }
    }
    
    # Configurações padrão
    DEFAULT_HEIGHT = 55
    DEFAULT_CORNER_RADIUS = 27
    DEFAULT_FONT_SIZE = 16
    
    # Configurações específicas para abas
    TAB_HEIGHT = 40
    TAB_CORNER_RADIUS = 10
    TAB_FONT_SIZE = 14
    
    # Configurações para botões de ícone
    ICON_BUTTON_SIZE = 35
    ICON_SIZE = 20
    
    @classmethod
    def create_primary_button(cls, parent, text="BOT�O", command=None, width=200):
        """
        Cria um bot�o prim�rio azul
        
        Args:
            parent: Container pai do bot�o
            text: Texto do bot�o
            command: Fun��o a ser executada ao clicar
            width: Largura do bot�o
        """
        return ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=cls.DEFAULT_FONT_SIZE, weight="bold"),
            height=cls.DEFAULT_HEIGHT,
            corner_radius=cls.DEFAULT_CORNER_RADIUS,
            width=width,
            command=command,
            **cls.STYLES['primary']
        )
    
    @classmethod
    def create_success_button(cls, parent, text="SUCESSO", command=None, width=200):
        """
        Cria um bot�o de sucesso verde
        
        Args:
            parent: Container pai do bot�o
            text: Texto do bot�o
            command: Fun��o a ser executada ao clicar
            width: Largura do bot�o
        """
        return ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=cls.DEFAULT_FONT_SIZE, weight="bold"),
            height=cls.DEFAULT_HEIGHT,
            corner_radius=cls.DEFAULT_CORNER_RADIUS,
            width=width,
            command=command,
            **cls.STYLES['success']
        )
    
    @classmethod
    def create_danger_button(cls, parent, text="PERIGO", command=None, width=200):
        """
        Cria um bot�o de perigo vermelho
        
        Args:
            parent: Container pai do bot�o
            text: Texto do bot�o
            command: Fun��o a ser executada ao clicar
            width: Largura do bot�o
        """
        return ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=cls.DEFAULT_FONT_SIZE, weight="bold"),
            height=cls.DEFAULT_HEIGHT,
            corner_radius=cls.DEFAULT_CORNER_RADIUS,
            width=width,
            command=command,
            **cls.STYLES['danger']
        )
    
    @classmethod
    def create_secondary_button(cls, parent, text="SECUND�RIO", command=None, width=200):
        """
        Cria um bot�o secund�rio cinza
        
        Args:
            parent: Container pai do bot�o
            text: Texto do bot�o
            command: Fun��o a ser executada ao clicar
            width: Largura do bot�o
        """
        return ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=cls.DEFAULT_FONT_SIZE, weight="bold"),
            height=cls.DEFAULT_HEIGHT,
            corner_radius=cls.DEFAULT_CORNER_RADIUS,
            width=width,
            command=command,
            **cls.STYLES['secondary']
        )
    
    @classmethod
    def create_execute_button(cls, parent, command=None, width=280):
        """
        Cria um bot�o espec�fico para executar scraper
        
        Args:
            parent: Container pai do bot�o
            command: Fun��o a ser executada ao clicar
            width: Largura do bot�o (padr�o 280 para GUI2, pode ser 300 para GUI1)
        """
        return ctk.CTkButton(
            parent,
            text="EXECUTAR SCRAPER",
            font=ctk.CTkFont(size=cls.DEFAULT_FONT_SIZE, weight="bold"),
            height=cls.DEFAULT_HEIGHT,
            corner_radius=cls.DEFAULT_CORNER_RADIUS,
            width=width,
            command=command,
            **cls.STYLES['primary']
        )
    
    @classmethod
    def create_cancel_button(cls, parent, command=None, width=280):
        """
        Cria um bot�o espec�fico para cancelar execu��o
        
        Args:
            parent: Container pai do bot�o
            command: Fun��o a ser executada ao clicar
            width: Largura do bot�o
        """
        button = ctk.CTkButton(
            parent,
            text="CANCELAR SCRAPER",
            font=ctk.CTkFont(size=cls.DEFAULT_FONT_SIZE, weight="bold"),
            height=cls.DEFAULT_HEIGHT,
            corner_radius=cls.DEFAULT_CORNER_RADIUS,
            width=width,
            command=command,
            **cls.STYLES['cancel']
        )
        return button
    
    @classmethod
    def create_folder_button(cls, parent, command=None, width=160, text="ABRIR PASTA"):
        """
        Cria um bot�o espec�fico para abrir pasta com �cone
        
        Args:
            parent: Container pai do bot�o
            command: Fun��o a ser executada ao clicar
            width: Largura do bot�o (padr�o 160 para GUI2, pode ser 200 para GUI1)
            text: Texto do bot�o
        """
        # Tenta carregar o �cone SVG
        icon_image = None
        try:
            # Caminho relativo ao arquivo buttons.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(os.path.dirname(current_dir), '..', 'assets', 'folder-open-svgrepo-com.svg')
            
            if os.path.exists(icon_path):
                # CTKButton n�o suporta SVG diretamente, ent�o usamos sem �cone
                # Em uma vers�o futura, podemos converter SVG para PNG
                pass
        except Exception as e:
            print(f"Aviso: N�o foi poss�vel carregar �cone - {e}")
        
        return ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=cls.DEFAULT_FONT_SIZE, weight="bold"),
            height=cls.DEFAULT_HEIGHT,
            corner_radius=cls.DEFAULT_CORNER_RADIUS,
            width=width,
            command=command,
            **cls.STYLES['success']
        )
    
    @classmethod
    def toggle_execute_cancel(cls, button, is_executing):
        """
        Alterna o estado visual do bot�o entre executar e cancelar
        
        Args:
            button: O bot�o a ser alternado
            is_executing: True para mudar para cancelar, False para executar
        """
        if is_executing:
            # Muda para modo cancelar
            button.configure(
                text="CANCELAR SCRAPER",
                **cls.STYLES['cancel']
            )
        else:
            # Muda para modo executar
            button.configure(
                text="EXECUTAR SCRAPER",
                **cls.STYLES['primary']
            )
    
    @classmethod
    def add_hover_effect(cls, button, original_width, original_height=None):
        """
        Adiciona efeito de crescimento ao passar o mouse sobre o bot�o
        
        Args:
            button: O bot�o que receber� o efeito
            original_width: Largura original do bot�o
            original_height: Altura original do bot�o (padr�o: DEFAULT_HEIGHT)
        """
        if original_height is None:
            original_height = cls.DEFAULT_HEIGHT
        
        def on_enter(event):
            """Aumenta o tamanho do bot�o ao entrar com o mouse"""
            button.configure(
                width=original_width + 8, 
                height=original_height + 3
            )
        
        def on_leave(event):
            """Restaura o tamanho original ao sair com o mouse"""
            button.configure(
                width=original_width,
                height=original_height
            )
        
        # Vincula os eventos
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    @classmethod
    def create_tab_button(cls, parent, text, command=None, width=140, active=False):
        """
        Cria um botão de aba genérico
        
        Args:
            parent: Container pai do botão
            text: Texto da aba
            command: Função a ser executada ao clicar
            width: Largura da aba (padrão 140)
            active: True se a aba está ativa, False se inativa
        """
        style = cls.STYLES['tab_active'] if active else cls.STYLES['tab_inactive']
        
        return ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=cls.TAB_FONT_SIZE, weight="bold"),
            height=cls.TAB_HEIGHT,
            corner_radius=cls.TAB_CORNER_RADIUS,
            width=width,
            command=command,
            **style
        )
    
    @classmethod
    def create_active_tab(cls, parent, text, command=None, width=140):
        """
        Cria uma aba no estado ativo (selecionada)
        
        Args:
            parent: Container pai do botão
            text: Texto da aba
            command: Função a ser executada ao clicar
            width: Largura da aba (padrão 140)
        """
        return cls.create_tab_button(parent, text, command, width, active=True)
    
    @classmethod
    def create_inactive_tab(cls, parent, text, command=None, width=140):
        """
        Cria uma aba no estado inativo (não selecionada)
        
        Args:
            parent: Container pai do botão
            text: Texto da aba
            command: Função a ser executada ao clicar
            width: Largura da aba (padrão 140)
        """
        return cls.create_tab_button(parent, text, command, width, active=False)
    
    @classmethod
    def toggle_tab_state(cls, button, is_active):
        """
        Alterna o estado visual da aba entre ativo e inativo
        
        Args:
            button: O botão da aba a ser alternado
            is_active: True para ativar, False para desativar
        """
        if is_active:
            button.configure(**cls.STYLES['tab_active'])
        else:
            button.configure(**cls.STYLES['tab_inactive'])
    
    @classmethod
    def set_tab_active(cls, button):
        """
        Define uma aba como ativa
        
        Args:
            button: O botão da aba
        """
        cls.toggle_tab_state(button, is_active=True)
    
    @classmethod
    def set_tab_inactive(cls, button):
        """
        Define uma aba como inativa
        
        Args:
            button: O botão da aba
        """
        cls.toggle_tab_state(button, is_active=False)
    
    @classmethod
    def create_icon_folder_button(cls, parent, command=None):
        """
        Cria um botão circular pequeno com ícone de pasta
        
        Args:
            parent: Container pai do botão
            command: Função a ser executada ao clicar
        """
        # Tenta carregar ícone PNG da pasta
        icon_image = None
        icon_text = ""  # Sem texto, apenas ícone
        
        try:
            from PIL import Image
            import customtkinter as ctk
            
            # Caminho para o ícone PNG
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(os.path.dirname(current_dir), '..', 'assets', 'folder-open-svgrepo-com.png')
            
            if os.path.exists(icon_path):
                # Carrega a imagem PNG
                pil_image = Image.open(icon_path)
                
                # Redimensiona para o tamanho do ícone se necessário
                pil_image = pil_image.resize((cls.ICON_SIZE, cls.ICON_SIZE), Image.Resampling.LANCZOS)
                
                # Converte para CTkImage
                icon_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(cls.ICON_SIZE, cls.ICON_SIZE))
            else:
                print(f"Aviso: Ícone não encontrado em {icon_path}")
                icon_text = "📁"  # Fallback para emoji
                
        except Exception as e:
            print(f"Aviso: Não foi possível carregar ícone PNG - {e}")
            # Usa emoji como fallback
            icon_text = "📁"
            icon_image = None
        
        # Cria o botão circular
        button = ctk.CTkButton(
            parent,
            text=icon_text,
            image=icon_image,
            font=ctk.CTkFont(size=16),
            width=cls.ICON_BUTTON_SIZE,
            height=cls.ICON_BUTTON_SIZE,
            corner_radius=cls.ICON_BUTTON_SIZE // 2,  # Circular
            command=command,
            **cls.STYLES['icon_button']
        )
        
        # Adiciona efeito de clique visual
        def on_click(event=None):
            # Efeito de clique - muda temporariamente para estilo ativo
            button.configure(**cls.STYLES['icon_button_active'])
            button.after(150, lambda: button.configure(**cls.STYLES['icon_button']))
            if command:
                command()
        
        # Sobrescreve o comando para adicionar efeito visual
        button.configure(command=on_click)
        
        return button
    
    @classmethod
    def create_icon_config_button(cls, parent, command=None):
        """
        Cria um botão circular pequeno com ícone de configurações
        
        Args:
            parent: Container pai do botão
            command: Função a ser executada ao clicar
        """
        icon_image = None
        icon_text = "⚙️"  # Usa emoji como padrão
        
        try:
            from PIL import Image
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(os.path.dirname(current_dir), '..', 'assets', 'applications-system-svgrepo-com.png')
            
            if os.path.exists(icon_path):
                pil_image = Image.open(icon_path)
                pil_image = pil_image.resize((cls.ICON_SIZE, cls.ICON_SIZE), Image.Resampling.LANCZOS)
                icon_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(cls.ICON_SIZE, cls.ICON_SIZE))
                icon_text = ""
        except:
            pass
        
        return ctk.CTkButton(
            parent,
            text=icon_text,
            image=icon_image,
            font=ctk.CTkFont(size=16),
            width=cls.ICON_BUTTON_SIZE,
            height=cls.ICON_BUTTON_SIZE,
            corner_radius=cls.ICON_BUTTON_SIZE // 2,
            command=command,
            **cls.STYLES['icon_button']
        )
    
    @classmethod
    def add_icon_hover_effect(cls, button):
        """
        Adiciona efeito hover específico para botões de ícone
        
        Args:
            button: O botão de ícone que receberá o efeito
        """
        def on_enter(event):
            """Aplica efeito hover"""
            button.configure(
                width=cls.ICON_BUTTON_SIZE + 2,
                height=cls.ICON_BUTTON_SIZE + 2
            )
        
        def on_leave(event):
            """Remove efeito hover"""
            button.configure(
                width=cls.ICON_BUTTON_SIZE,
                height=cls.ICON_BUTTON_SIZE
            )
        
        # Vincula os eventos
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)