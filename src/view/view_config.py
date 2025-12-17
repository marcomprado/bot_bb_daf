#!/usr/bin/env python3
"""
Interface Gráfica para a tela "Configurações do Sistema"
"""

import sys
import os
import platform
import customtkinter as ctk
from tkinter import filedialog
import tkinter.messagebox as messagebox
import tkinter as tk

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importa o gerenciador de configurações e fábrica de botões
from src.classes.config_page import ConfigManager
from src.view.modules.buttons import ButtonFactory

# Importa o sistema de execução automática
from src.classes.methods.auto_execution import (
    update_execution_config,
    get_execution_status,
    start_automatic_execution,
    stop_automatic_execution
)


class ConfigGUI:
    """Interface de configuração do sistema"""

    def __init__(self, parent_frame):
        """
        Inicializa a GUI de configurações
        """
        self.parent_frame = parent_frame
        self.config_manager = ConfigManager()

        # Variáveis de controle para execução automática - SEM valores default
        self.execucao_auto_var = tk.BooleanVar(value=False)
        self.script_bb_var = tk.BooleanVar(value=False)
        self.script_fnde_var = tk.BooleanVar(value=False)
        self.script_betha_var = tk.BooleanVar(value=False)
        self.script_consfns_var = tk.BooleanVar(value=False)
        self.periodo_var = tk.StringVar(value="")  # Vazio - será preenchido do JSON
        self.horario_var = tk.StringVar(value="")  # Vazio - será preenchido do JSON
        self.hora_var = tk.StringVar(value="")     # Vazio - será preenchido do JSON
        self.minuto_var = tk.StringVar(value="")   # Vazio - será preenchido do JSON
        self.modo_exec_var = tk.StringVar(value="")  # Vazio - será preenchido do JSON

        # Variáveis para dias da semana
        self.dia_seg_var = tk.BooleanVar(value=False)
        self.dia_ter_var = tk.BooleanVar(value=False)
        self.dia_qua_var = tk.BooleanVar(value=False)
        self.dia_qui_var = tk.BooleanVar(value=False)
        self.dia_sex_var = tk.BooleanVar(value=False)
        self.dia_sab_var = tk.BooleanVar(value=False)
        self.dia_dom_var = tk.BooleanVar(value=False)

        # Timer para debounce de salvamento
        self._save_timer = None
        # IMPORTANTE: Inicia com True para prevenir salvamentos durante inicialização
        self._loading_config = True
        
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
        # Container principal scrollable
        self.scroll_container = ctk.CTkScrollableFrame(
            self.main_frame,
            corner_radius=0,
            fg_color="#f8f9fa"
        )
        self.scroll_container.pack(fill="both", expand=True)
        
        # Cabeçalho
        self._criar_cabecalho(self.scroll_container)

        # Seção: Diretório de Download
        self._criar_secao_diretorio(self.scroll_container)

        # Seção: Execução Automática
        self._criar_secao_execucao_automatica(self.scroll_container)

        # Botões de ação no final
        self._criar_botoes_acao(self.scroll_container)
    
    def _criar_secao_diretorio(self, parent):
        """
        Cria a seção de configuração de diretório
        
        Args:
            parent: Container pai
        """
        # Frame da seção
        secao_frame = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        secao_frame.pack(fill="x", padx=20, pady=(0, 20))
        
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

    def _criar_cabecalho(self, parent):
        """Cria cabeçalho da interface"""
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
            text="Configurações do Sistema",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#212529"
        )
        label_titulo.pack(pady=(30, 5))

        # Subtítulo
        label_subtitulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Gerencie as preferências e configurações do sistema",
            font=ctk.CTkFont(size=16),
            text_color="#6c757d"
        )
        label_subtitulo.pack(pady=(0, 30))

    def _criar_secao_execucao_automatica(self, parent):
        """
        Cria a seção de configuração de execução automática

        Args:
            parent: Container pai
        """
        # Frame principal da seção
        self.secao_exec_frame = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        self.secao_exec_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Frame do título com switch
        titulo_frame = ctk.CTkFrame(
            self.secao_exec_frame,
            fg_color="transparent"
        )
        titulo_frame.pack(fill="x", padx=15, pady=(15, 5))

        # Título da seção
        titulo_secao = ctk.CTkLabel(
            titulo_frame,
            text="Execução Automática",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#34495e"
        )
        titulo_secao.pack(side="left")

        # Switch de ativação
        self.switch_execucao = ctk.CTkSwitch(
            titulo_frame,
            text="",
            variable=self.execucao_auto_var,
            command=self._toggle_execucao_automatica,
            width=45,
            height=24
        )
        self.switch_execucao.pack(side="left", padx=(15, 0))

        # Descrição
        descricao = ctk.CTkLabel(
            self.secao_exec_frame,
            text="Se esta opção estiver ativada, o programa vai executar os scripts selecionados\nautomaticamente no momento escolhido pelo usuário.",
            font=ctk.CTkFont(size=13),
            text_color="#7f8c8d",
            justify="left"
        )
        descricao.pack(anchor="w", padx=15, pady=(0, 15))

        # Container para todos os campos (inicialmente oculto)
        self.campos_exec_frame = ctk.CTkFrame(
            self.secao_exec_frame,
            fg_color="transparent"
        )
        # Não fazer pack aqui - será controlado pelo toggle

        # Seção de seleção de scripts
        self._criar_selecao_scripts(self.campos_exec_frame)

        # Seção de período de execução
        self._criar_selecao_periodo(self.campos_exec_frame)

        # Seção de dias da semana (inicialmente oculta)
        self._criar_selecao_dias_semana(self.campos_exec_frame)

        # Seção de horário
        self._criar_selecao_horario(self.campos_exec_frame)

        # Seção de modo de execução
        self._criar_selecao_modo_execucao(self.campos_exec_frame)

        # NÃO chamar toggle durante inicialização - valores vêm apenas do JSON

    def _criar_selecao_scripts(self, parent):
        """Cria checkboxes para seleção de scripts"""
        scripts_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=10
        )
        scripts_frame.pack(fill="x", pady=(0, 15))

        label_scripts = ctk.CTkLabel(
            scripts_frame,
            text="Scripts para executar:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_scripts.pack(anchor="w", padx=10, pady=(10, 5))

        # Container para checkboxes centralizado
        checks_container = ctk.CTkFrame(scripts_frame, fg_color="transparent")
        checks_container.pack(fill="x", padx=10, pady=(0, 10))

        checks_frame = ctk.CTkFrame(checks_container, fg_color="transparent")
        checks_frame.pack(expand=True)

        self.check_bb = ctk.CTkCheckBox(
            checks_frame,
            text="BB DAF",
            variable=self.script_bb_var,
            command=self._on_config_change,
            font=ctk.CTkFont(size=13)
        )
        self.check_bb.pack(side="left", padx=(0, 20))

        self.check_fnde = ctk.CTkCheckBox(
            checks_frame,
            text="FNDE",
            variable=self.script_fnde_var,
            command=self._on_config_change,
            font=ctk.CTkFont(size=13)
        )
        self.check_fnde.pack(side="left", padx=(0, 20))

        self.check_betha = ctk.CTkCheckBox(
            checks_frame,
            text="Betha",
            variable=self.script_betha_var,
            command=self._on_config_change,
            font=ctk.CTkFont(size=13)
        )
        self.check_betha.pack(side="left", padx=(0, 20))

        self.check_consfns = ctk.CTkCheckBox(
            checks_frame,
            text="Consulta FNS",
            variable=self.script_consfns_var,
            command=self._on_config_change,
            font=ctk.CTkFont(size=13)
        )
        self.check_consfns.pack(side="left")

    def _criar_selecao_periodo(self, parent):
        """Cria dropdown para seleção de período"""
        periodo_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=10
        )
        periodo_frame.pack(fill="x", pady=(0, 15))

        # Container centralizado
        container_periodo = ctk.CTkFrame(periodo_frame, fg_color="transparent")
        container_periodo.pack(fill="x", padx=15, pady=(15, 15))

        frame_periodo_campo = ctk.CTkFrame(container_periodo, fg_color="transparent")
        frame_periodo_campo.pack(expand=True)

        label_periodo = ctk.CTkLabel(
            frame_periodo_campo,
            text="Período de execução:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_periodo.pack(pady=(0, 5))

        self.dropdown_periodo = ctk.CTkOptionMenu(
            frame_periodo_campo,
            values=["Diariamente", "Semanalmente", "Mensalmente"],
            variable=self.periodo_var,
            command=self._on_periodo_change,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=220,
            height=40
        )
        self.dropdown_periodo.pack()

    def _criar_selecao_dias_semana(self, parent):
        """Cria checkboxes para seleção de dias da semana"""
        self.dias_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=10
        )
        # Inicialmente oculto

        # Container centralizado
        container_dias = ctk.CTkFrame(self.dias_frame, fg_color="transparent")
        container_dias.pack(fill="x", padx=15, pady=15)

        frame_dias_campo = ctk.CTkFrame(container_dias, fg_color="transparent")
        frame_dias_campo.pack(expand=True)

        label_dias = ctk.CTkLabel(
            frame_dias_campo,
            text="Dias da semana:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_dias.pack(pady=(0, 10))

        # Container para checkboxes dos dias
        dias_checks_frame = ctk.CTkFrame(
            frame_dias_campo,
            fg_color="transparent"
        )
        dias_checks_frame.pack()

        # Criar checkboxes para cada dia
        dias = [
            ("Seg", self.dia_seg_var),
            ("Ter", self.dia_ter_var),
            ("Qua", self.dia_qua_var),
            ("Qui", self.dia_qui_var),
            ("Sex", self.dia_sex_var),
            ("Sáb", self.dia_sab_var),
            ("Dom", self.dia_dom_var)
        ]

        self.dias_checks = []
        for dia_nome, dia_var in dias:
            check = ctk.CTkCheckBox(
                dias_checks_frame,
                text=dia_nome,
                variable=dia_var,
                command=self._on_config_change,
                font=ctk.CTkFont(size=12),
                width=60
            )
            check.pack(side="left", padx=(0, 8))
            self.dias_checks.append(check)

    def _criar_selecao_horario(self, parent):
        """Cria campo para seleção de horário"""
        horario_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=10
        )
        horario_frame.pack(fill="x", pady=(0, 15))

        # Container centralizado
        container_horario = ctk.CTkFrame(horario_frame, fg_color="transparent")
        container_horario.pack(fill="x", padx=15, pady=15)

        frame_horario_campo = ctk.CTkFrame(container_horario, fg_color="transparent")
        frame_horario_campo.pack(expand=True)

        label_horario = ctk.CTkLabel(
            frame_horario_campo,
            text="Horário de execução (formato 24h):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_horario.pack(pady=(0, 5))

        # Frame para entrada de horário
        entry_container = ctk.CTkFrame(frame_horario_campo, fg_color="transparent")
        entry_container.pack(pady=(0, 5))

        # Frame para campos de hora e minuto
        time_frame = ctk.CTkFrame(entry_container, fg_color="transparent")
        time_frame.pack()

        # Campo de hora
        self.entry_hora = ctk.CTkEntry(
            time_frame,
            textvariable=self.hora_var,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=50,
            height=40,
            justify="center"
        )
        self.entry_hora.pack(side="left")
        self.entry_hora.bind("<KeyRelease>", self._validar_hora)
        self.entry_hora.bind("<FocusOut>", self._formatar_hora)

        # Label do :
        label_dois_pontos = ctk.CTkLabel(
            time_frame,
            text=":",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#495057"
        )
        label_dois_pontos.pack(side="left", padx=5)

        # Campo de minuto
        self.entry_minuto = ctk.CTkEntry(
            time_frame,
            textvariable=self.minuto_var,
            font=ctk.CTkFont(size=16, weight="bold"),
            width=50,
            height=40,
            justify="center"
        )
        self.entry_minuto.pack(side="left")
        self.entry_minuto.bind("<KeyRelease>", self._validar_minuto)
        self.entry_minuto.bind("<FocusOut>", self._formatar_minuto)

        # Botão Salvar
        self.btn_salvar_horario = ctk.CTkButton(
            time_frame,
            text="Salvar",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=70,
            height=40,
            fg_color="#28a745",
            hover_color="#218838",
            command=self._salvar_horario_manual
        )
        self.btn_salvar_horario.pack(side="left", padx=(10, 0))

        # Label de exemplo
        label_exemplo = ctk.CTkLabel(
            frame_horario_campo,
            text="Use as setas ou digite para ajustar o horário",
            font=ctk.CTkFont(size=12),
            text_color="#6c757d"
        )
        label_exemplo.pack(pady=(5, 0))

    def _criar_selecao_modo_execucao(self, parent):
        """Cria dropdown para modo de execução"""
        modo_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=10
        )
        modo_frame.pack(fill="x", pady=(0, 15))

        # Título da seção
        label_titulo = ctk.CTkLabel(
            modo_frame,
            text="Modo de Execução",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#495057"
        )
        label_titulo.pack(pady=(15, 10))

        # Container para o dropdown
        container_modo = ctk.CTkFrame(modo_frame, fg_color="transparent")
        container_modo.pack(fill="x", padx=15, pady=(0, 15))

        # Campo de modo centralizado
        frame_modo = ctk.CTkFrame(container_modo, fg_color="transparent")
        frame_modo.pack(expand=True)

        label_modo = ctk.CTkLabel(
            frame_modo,
            text="Selecione o Modo:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_modo.pack(pady=(0, 5))

        self.dropdown_modo = ctk.CTkOptionMenu(
            frame_modo,
            values=[
                "Individual",
                "Paralelo (2 instâncias)",
                "Paralelo (3 instâncias)",
                "Paralelo (4 instâncias)",
                "Paralelo (5 instâncias)"
            ],
            variable=self.modo_exec_var,
            command=self._on_modo_change_exec,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=200,
            height=40
        )
        self.dropdown_modo.pack()

        # Label de info sobre execução
        self.label_info_modo = ctk.CTkLabel(
            modo_frame,
            text="Modo Individual: Processa sequencialmente",
            font=ctk.CTkFont(size=12),
            text_color="#6c757d"
        )
        self.label_info_modo.pack(pady=(5, 15))

    def _toggle_execucao_automatica(self):
        """Mostra/oculta campos baseado no switch e atualiza configuração"""
        estado = self.execucao_auto_var.get()

        # Mostrar ou ocultar o container de campos
        if estado:
            # Mostrar campos
            self.campos_exec_frame.pack(fill="x", padx=15, pady=(0, 15))
            # Atualizar cor de fundo da seção para indicar ativação
            self.secao_exec_frame.configure(fg_color="#e8f4fd", border_color="#0066cc")
        else:
            # Ocultar campos
            self.campos_exec_frame.pack_forget()
            # Ocultar também dias da semana se estiver visível
            if hasattr(self, 'dias_frame'):
                self.dias_frame.pack_forget()
            # Voltar cor padrão
            self.secao_exec_frame.configure(fg_color="#f8f9fa", border_color="#dee2e6")

        # Salva a configuração apenas se não estiver carregando
        if not self._loading_config:
            self._salvar_config_execucao_automatica()


    def _validar_hora(self, event):
        """Valida entrada de hora"""
        valor = self.hora_var.get()
        # Remove caracteres não numéricos
        valor = ''.join(filter(str.isdigit, valor))

        if len(valor) > 2:
            valor = valor[:2]

        if valor:
            hora = int(valor)
            if hora > 23:
                valor = "23"

        self.hora_var.set(valor)

    def _validar_minuto(self, event):
        """Valida entrada de minuto"""
        valor = self.minuto_var.get()
        # Remove caracteres não numéricos
        valor = ''.join(filter(str.isdigit, valor))

        if len(valor) > 2:
            valor = valor[:2]

        if valor:
            minuto = int(valor)
            if minuto > 59:
                valor = "59"

        self.minuto_var.set(valor)

    def _formatar_hora(self, event):
        """Formata hora com dois dígitos"""
        valor = self.hora_var.get()
        if valor:
            self.hora_var.set(valor.zfill(2))
        else:
            self.hora_var.set("00")

    def _formatar_minuto(self, event):
        """Formata minuto com dois dígitos"""
        valor = self.minuto_var.get()
        if valor:
            self.minuto_var.set(valor.zfill(2))
        else:
            self.minuto_var.set("00")

    def _salvar_horario_manual(self):
        """Salva o horário quando o botão Salvar é clicado"""
        # Formata os valores
        hora = self.hora_var.get().zfill(2)
        minuto = self.minuto_var.get().zfill(2)

        # Atualiza as variáveis
        self.hora_var.set(hora)
        self.minuto_var.set(minuto)

        # Salva a configuração
        self._salvar_config_execucao_automatica()

        # Feedback visual
        self.btn_salvar_horario.configure(text="✓ Salvo", fg_color="#17a2b8")
        self.parent_frame.after(1500, lambda: self.btn_salvar_horario.configure(text="Salvar", fg_color="#28a745"))

    def _on_periodo_change(self, periodo):
        """Mostra/oculta dias da semana baseado no período selecionado"""
        if periodo == "Semanalmente":
            self.dias_frame.pack(fill="x", pady=(0, 15), after=self.dropdown_periodo.master.master.master)
        else:
            self.dias_frame.pack_forget()

        # Salva configuração quando muda o período
        self._on_config_change()

    def _on_modo_change_exec(self, valor):
        """Callback quando modo de execução é alterado"""
        if "Paralelo" in valor:
            instancias = valor.split("(")[1].split(" ")[0]
            self.label_info_modo.configure(
                text=f"Modo Paralelo: {instancias} navegadores simultâneos"
            )
        else:
            self.label_info_modo.configure(
                text="Modo Individual: Processa sequencialmente"
            )

        # Salva configuração quando muda o modo
        self._on_config_change()

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
        # Marca que está carregando para evitar salvamentos desnecessários
        self._loading_config = True

        # Atualiza valores antes de mostrar
        current_dir = self.config_manager.get_download_directory()
        self.dir_entry.configure(state="normal")
        self.dir_entry.delete(0, "end")
        self.dir_entry.insert(0, current_dir)
        self.dir_entry.configure(state="readonly")

        # Carrega configuração da execução automática do user_config.json
        saved_config = self.config_manager.get_config('automatic_execution', None)

        if saved_config:
            # Usa configuração salva
            self.execucao_auto_var.set(saved_config.get('enabled', False))

            # Carrega scripts habilitados
            scripts = saved_config.get('scripts', {})
            self.script_bb_var.set(scripts.get('bb_daf', False))
            self.script_fnde_var.set(scripts.get('fnde', False))
            self.script_betha_var.set(scripts.get('betha', False))
            self.script_consfns_var.set(scripts.get('cons_fns', False))

            # Carrega período e horário EXATAMENTE como está no JSON
            self.periodo_var.set(saved_config.get('period', ''))
            scheduled_time = saved_config.get('time', '')
            if scheduled_time and ':' in scheduled_time:
                hora, minuto = scheduled_time.split(':')
                # NÃO usa zfill - mantém exatamente como está no JSON
                self.hora_var.set(hora)
                self.minuto_var.set(minuto)
                self.horario_var.set(scheduled_time)

            # Carrega dias da semana
            weekdays = saved_config.get('weekdays', {})
            self.dia_seg_var.set(weekdays.get('seg', False))
            self.dia_ter_var.set(weekdays.get('ter', False))
            self.dia_qua_var.set(weekdays.get('qua', False))
            self.dia_qui_var.set(weekdays.get('qui', False))
            self.dia_sex_var.set(weekdays.get('sex', False))
            self.dia_sab_var.set(weekdays.get('sab', False))
            self.dia_dom_var.set(weekdays.get('dom', False))

            # Carrega modo de execução
            exec_mode = saved_config.get('execution_mode', 'Individual')
            parallel_instances = saved_config.get('parallel_instances', 2)
            if exec_mode == 'Paralela':
                self.modo_exec_var.set(f"Paralelo ({parallel_instances} instâncias)")
            else:
                self.modo_exec_var.set("Individual")

            # Atualiza visualização dos campos
            if self.execucao_auto_var.get():
                self.campos_exec_frame.pack(fill="x", padx=15, pady=(0, 15))
                self.secao_exec_frame.configure(
                    fg_color="#e8f4fd",
                    border_color="#0066cc"
                )
            else:
                self.campos_exec_frame.pack_forget()
                self.secao_exec_frame.configure(
                    fg_color="#f8f9fa",
                    border_color="#dee2e6"
                )
        else:
            # Não há configuração salva, define valores mínimos para não quebrar a UI
            # Mas NÃO salva ainda - só salva quando usuário fizer mudanças
            self.execucao_auto_var.set(False)

            # Define valores mínimos para os campos não ficarem vazios
            self.periodo_var.set("Diariamente")
            self.hora_var.set("08")
            self.minuto_var.set("00")
            self.horario_var.set("08:00")
            self.modo_exec_var.set("Individual")

        # NÃO modifica valores - mantém exatamente como vieram do JSON
        # Removido código que usava zfill() para modificar valores

        # Marca que terminou de carregar
        self._loading_config = False

        # Mostra o frame
        self.main_frame.pack(fill="both", expand=True)
    
    def _on_config_change(self):
        """Chamado quando qualquer configuração muda (exceto horário)"""
        # Salva imediatamente para configurações que não são o horário
        self._salvar_config_execucao_automatica()

    def _salvar_config_execucao_automatica(self):
        """Salva as configurações de execução automática"""
        # Obtém horário SEM modificação - vem direto do JSON
        hora = self.hora_var.get()
        minuto = self.minuto_var.get()
        # Só cria horário se ambos existem
        if hora and minuto:
            horario = f"{hora}:{minuto}"
        else:
            # Usa o valor que já estava salvo
            horario = self.horario_var.get()

        # Obtém número de instâncias paralelas do modo selecionado
        modo_exec = self.modo_exec_var.get()
        parallel_instances = 2  # Padrão
        if "Paralelo" in modo_exec:
            try:
                parallel_instances = int(modo_exec.split("(")[1].split(" ")[0])
            except:
                parallel_instances = 2

        # Cria dicionário de configuração
        config = {
            'enabled': self.execucao_auto_var.get(),
            'scripts': {
                'bb_daf': self.script_bb_var.get(),
                'fnde': self.script_fnde_var.get(),
                'betha': self.script_betha_var.get(),
                'cons_fns': self.script_consfns_var.get()
            },
            'period': self.periodo_var.get(),
            'weekdays': {
                'seg': self.dia_seg_var.get(),
                'ter': self.dia_ter_var.get(),
                'qua': self.dia_qua_var.get(),
                'qui': self.dia_qui_var.get(),
                'sex': self.dia_sex_var.get(),
                'sab': self.dia_sab_var.get(),
                'dom': self.dia_dom_var.get()
            },
            'time': horario,
            'execution_mode': 'Paralela' if "Paralelo" in modo_exec else 'Individual',
            'parallel_instances': parallel_instances
        }

        # Salva no arquivo user_config.json
        self.config_manager.set_config('automatic_execution', config)
        self.config_manager.save_config_to_file()  # Salva explicitamente no arquivo

        # Atualiza a configuração no executor automático
        update_execution_config(config)

        # Se habilitado, inicia o monitoramento; senão, para
        if config['enabled']:
            start_automatic_execution()
        else:
            stop_automatic_execution()

    def ocultar(self):
        """Oculta a GUI de configurações"""
        self.main_frame.pack_forget()