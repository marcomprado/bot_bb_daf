#!/usr/bin/env python3
"""
GUI4 - Interface gráfica para Consulta FNS
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import sys
import threading
import subprocess
import platform
from typing import Dict, Callable

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.view.modules.buttons import ButtonFactory


class GUI4:
    """Interface gráfica para Consulta FNS - Fundo Nacional de Saúde"""

    def __init__(self, parent_container):
        """
        Inicializa a GUI4

        Args:
            parent_container: Container pai onde a GUI será criada
        """
        self.parent_container = parent_container

        # Estado da execução
        self.executando = False
        self.thread_execucao = None
        self._cancelado = False

        # Bot FNS (será implementado posteriormente)
        self.bot_cons_fns = None

        # Variáveis de configuração
        self.municipio_var = ctk.StringVar()
        self.lista_municipios = []

        # Frame principal
        self.main_frame = None

        # Configurar valores padrão
        self._configurar_valores_padrao()

        # Cria a interface
        self._criar_interface()

    def _configurar_valores_padrao(self):
        """Configura valores padrão"""
        # Carrega lista de municípios
        self._carregar_municipios()

        # Define valor padrão do município
        if self.lista_municipios:
            self.municipio_var.set("Todos os Municípios")

    def _carregar_municipios(self):
        """Carrega lista de municípios de MG"""
        try:
            # Inicializa bot temporário para obter lista
            from src.bots.bot_fnde import BotFNDE
            bot_temp = BotFNDE()
            self.lista_municipios = bot_temp.obter_lista_municipios()
            print(f"Carregados {len(self.lista_municipios)} municípios")
        except Exception as e:
            print(f"Erro ao carregar municípios: {e}")
            # Fallback para lista básica
            self.lista_municipios = ["BELO HORIZONTE", "UBERLANDIA", "CONTAGEM"]

    def _obter_opcoes_municipios(self):
        """Retorna lista de opções para o dropdown de municípios"""
        opcoes = ["Todos os Municípios"]
        if self.lista_municipios:
            # Adiciona municípios em ordem alfabética
            municipios_ordenados = sorted(self.lista_municipios)
            opcoes.extend([municipio.title() for municipio in municipios_ordenados])
        return opcoes

    def _on_municipio_change(self, valor):
        """Callback quando município é alterado"""
        if valor == "Todos os Municípios":
            self.label_status_municipios.configure(
                text="Todos os municípios de MG selecionados (853 municípios)"
            )
        else:
            self.label_status_municipios.configure(
                text=f"Município selecionado: {valor}"
            )

    def _criar_interface(self):
        """Cria a interface completa com scroll"""
        # Frame scrollable principal
        self.main_frame = ctk.CTkScrollableFrame(
            self.parent_container,
            corner_radius=0,
            fg_color="#f8f9fa"
        )

        # Cabeçalho
        self._criar_cabecalho(self.main_frame)

        # Seções principais
        self._criar_secao_municipios(self.main_frame)
        self._criar_botoes_acao(self.main_frame)

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
            text="Consulta FNS - Fundo Nacional de Saúde",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#212529"
        )
        label_titulo.pack(pady=(30, 5))

        # Subtítulo
        label_subtitulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Consulta automatizada de contas bancárias",
            font=ctk.CTkFont(size=16),
            text_color="#6c757d"
        )
        label_subtitulo.pack(pady=(0, 30))

    def _criar_secao_municipios(self, parent):
        """Cria seção de seleção de municípios"""
        # Frame dos municípios
        frame_municipios = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        frame_municipios.pack(fill="x", padx=20, pady=(0, 20))

        # Título da seção
        label_municipios = ctk.CTkLabel(
            frame_municipios,
            text="Seleção de Municípios",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_municipios.pack(pady=(15, 10))

        # Container do campo de município
        container_municipio = ctk.CTkFrame(frame_municipios, fg_color="transparent")
        container_municipio.pack(fill="x", padx=15, pady=(0, 15))

        # Campo de município centralizado
        frame_municipio_campo = ctk.CTkFrame(container_municipio, fg_color="transparent")
        frame_municipio_campo.pack(expand=True)

        label_municipio_campo = ctk.CTkLabel(
            frame_municipio_campo,
            text="Selecione o Município:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_municipio_campo.pack(pady=(0, 5))

        # Dropdown com municípios (usado em todas as plataformas)
        self.dropdown_municipio = ctk.CTkOptionMenu(
            frame_municipio_campo,
            values=self._obter_opcoes_municipios(),
            variable=self.municipio_var,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=300,
            height=40,
            command=self._on_municipio_change
        )
        self.dropdown_municipio.pack()

        # Label de status da seleção
        self.label_status_municipios = ctk.CTkLabel(
            frame_municipios,
            text="Todos os municípios de MG selecionados (853 municípios)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#495057"
        )
        self.label_status_municipios.pack(pady=(0, 15))

    def _criar_botoes_acao(self, parent):
        """Cria botões de ação principais"""
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

        # Botão Executar usando ButtonFactory
        self.botao_executar = ButtonFactory.create_execute_button(
            container_botoes,
            command=self._executar_consulta,
            width=280
        )
        self.botao_executar.configure(text="EXECUTAR CONSULTA FNS")
        self.botao_executar.pack(side="left", padx=10)

        # Botão Abrir Pasta usando ButtonFactory
        self.botao_abrir_pasta = ButtonFactory.create_folder_button(
            container_botoes,
            command=self._abrir_pasta_fns,
            width=160
        )
        self.botao_abrir_pasta.pack(side="left", padx=10)

        # Adicionar efeito hover aos botões
        ButtonFactory.add_hover_effect(self.botao_executar, 280)
        ButtonFactory.add_hover_effect(self.botao_abrir_pasta, 160)

    def _executar_consulta(self):
        """Executa a consulta FNS ou cancela execução"""
        if self.executando:
            self._cancelar_execucao()
            return

        try:
            self._iniciar_execucao()
        except Exception as e:
            self._mostrar_erro(f"Erro ao executar: {str(e)}")
            self._habilitar_interface(True)

    def _iniciar_execucao(self):
        """Inicia o processo de consulta FNS"""
        # Desabilita interface e muda botão para cancelar
        self._habilitar_interface(False)

        # Simula execução em thread separada (será conectado ao bot depois)
        def executar_thread():
            try:
                import time
                # Por enquanto apenas simula execução
                for i in range(5):
                    if self._cancelado:
                        break
                    time.sleep(1)

                if not self._cancelado:
                    # Finaliza com sucesso
                    self.parent_container.after(0, self._finalizar_execucao_sucesso)

            except Exception as e:
                if not self._cancelado:
                    self.parent_container.after(0, self._finalizar_execucao_erro, str(e))

            finally:
                self.executando = False

        # Inicializa flag de cancelamento
        self._cancelado = False

        # Inicia thread
        self.thread_execucao = threading.Thread(target=executar_thread, daemon=True)
        self.thread_execucao.start()

    def _cancelar_execucao(self):
        """Cancela a execução em andamento"""
        try:
            self._cancelado = True

            # Se tiver um bot implementado, cancelar aqui
            if self.bot_cons_fns:
                # self.bot_cons_fns.cancelar()
                pass

            self._habilitar_interface(True)
            self._mostrar_info("Consulta FNS cancelada com sucesso")

        except Exception as e:
            self._mostrar_erro(f"Erro ao cancelar: {str(e)}")
            self._habilitar_interface(True)

    def _finalizar_execucao_sucesso(self):
        """Finaliza execução com sucesso"""
        if self._cancelado:
            return

        self._habilitar_interface(True)
        self._mostrar_info("Consulta FNS finalizada!\n\nOs arquivos foram salvos na pasta consfns/")

    def _finalizar_execucao_erro(self, erro):
        """Finaliza execução com erro"""
        if self._cancelado:
            return

        self._habilitar_interface(True)
        self._mostrar_erro(f"Erro durante execução: {erro}")

    def _habilitar_interface(self, habilitado=True):
        """Habilita/desabilita elementos da interface"""
        self.executando = not habilitado

        # Atualiza dropdown de municípios
        if hasattr(self, 'dropdown_municipio'):
            self.dropdown_municipio.configure(state="normal" if habilitado else "disabled")

        # Botão abrir pasta sempre fica habilitado
        self.botao_abrir_pasta.configure(state="normal")

        # Atualiza botão executar/cancelar
        if habilitado:
            # Modo normal - botão azul "EXECUTAR"
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=False)
            self.botao_executar.configure(
                text="EXECUTAR CONSULTA FNS",
                state="normal"
            )
        else:
            # Modo execução - botão vermelho "CANCELAR"
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=True)
            self.botao_executar.configure(
                text="CANCELAR CONSULTA FNS",
                state="normal"
            )

    def _abrir_pasta_fns(self):
        """Abre a pasta de arquivos FNS no explorador"""
        try:
            # Caminho da pasta FNS
            from src.classes.file.path_manager import obter_caminho_dados
            pasta_fns = obter_caminho_dados("consfns")

            # Cria a pasta se não existir
            if not os.path.exists(pasta_fns):
                os.makedirs(pasta_fns)
                print(f"Pasta criada: {pasta_fns}")

            # Detecta o sistema operacional e abre a pasta
            sistema = platform.system()

            if sistema == "Windows":
                os.startfile(pasta_fns)
            elif sistema == "Darwin":
                subprocess.run(["open", pasta_fns])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", pasta_fns])
            else:
                self._mostrar_erro(f"Sistema operacional '{sistema}' não suportado")
                return

            print(f"Pasta aberta: {pasta_fns}")

        except Exception as e:
            self._mostrar_erro(f"Erro ao abrir pasta: {str(e)}")

    def _mostrar_erro(self, mensagem):
        """Mostra mensagem de erro"""
        messagebox.showerror("Erro", mensagem)

    def _mostrar_info(self, mensagem):
        """Mostra mensagem informativa"""
        messagebox.showinfo("Informação", mensagem)

    def mostrar(self):
        """Mostra esta interface"""
        if self.main_frame:
            self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def ocultar(self):
        """Oculta esta interface"""
        if self.main_frame:
            self.main_frame.pack_forget()