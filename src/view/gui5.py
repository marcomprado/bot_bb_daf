#!/usr/bin/env python3
"""
GUI5 - Interface grafica Resolucoes
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import sys
import platform
import subprocess
import threading
from datetime import datetime
from typing import List

# Adiciona o diretorio raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.view.modules.buttons import ButtonFactory
from src.view.modules.loading_indicator import LoadingIndicator


class GUI5:
    """Interface grafica com selecao de Ano e Mes"""

    def __init__(self, parent_container):
        """
        Inicializa a GUI5
        """
        self.parent_container = parent_container

        # Estado da execucao
        self.executando = False
        self.thread_execucao = None
        self._cancelado = False

        # Bot Portal Saude
        self.bot_portal_saude = None

        # Variaveis de configuracao
        self.ano_var = ctk.StringVar()
        self.mes_var = ctk.StringVar()

        # Frame principal
        self.main_frame = None

        # Loading indicator
        self.loading_indicator = None

        # Configurar valores padrao
        self._configurar_valores_padrao()

        # Cria a interface
        self._criar_interface()

    def _configurar_valores_padrao(self):
        """Configura valores padrao"""
        # Define valor padrao do ano (ano atual)
        ano_atual = datetime.now().year
        self.ano_var.set(str(ano_atual))

        # Define valor padrao do mes (mes atual)
        mes_atual = datetime.now().month
        meses_nomes = [
            "Janeiro", "Fevereiro", "Março", "Abril",
            "Maio", "Junho", "Julho", "Agosto",
            "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        mes_nome = meses_nomes[mes_atual - 1]  # Ajusta indice (1-12 -> 0-11)
        self.mes_var.set(mes_nome)

    def _obter_opcoes_anos(self) -> List[str]:
        """Retorna lista de opcoes para o dropdown de anos"""
        ano_atual = datetime.now().year
        anos = ["Todos os Anos"]
        # Adiciona anos de 2007 ate o ano atual
        for ano in range(2007, ano_atual + 1):
            anos.append(str(ano))
        return anos

    def _obter_opcoes_meses(self) -> List[str]:
        """Retorna lista de opcoes para o dropdown de meses"""
        meses = [
            "Todos os Meses",
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro"
        ]
        return meses

    def _on_ano_change(self, valor):
        """Callback quando ano e alterado"""
        if valor == "Todos os Anos":
            self.label_status_periodo.configure(
                text="Todos os anos selecionados (2007 ate atual)"
            )
        else:
            self.label_status_periodo.configure(
                text=f"Ano selecionado: {valor}"
            )

    def _on_mes_change(self, valor):
        """Callback quando mes e alterado"""
        if valor == "Todos os Meses":
            self.label_status_mes.configure(
                text="Todos os meses selecionados"
            )
        else:
            self.label_status_mes.configure(
                text=f"Mes selecionado: {valor}"
            )

    def _criar_interface(self):
        """Cria a interface completa com scroll"""
        # Frame scrollable principal
        self.main_frame = ctk.CTkScrollableFrame(
            self.parent_container,
            corner_radius=0,
            fg_color="#f8f9fa"
        )

        # Cabecalho
        self._criar_cabecalho(self.main_frame)

        # Secoes principais
        self._criar_secao_periodo(self.main_frame)
        self._criar_botoes_acao(self.main_frame)

    def _criar_cabecalho(self, parent):
        """Cria cabecalho da interface"""
        # Container do cabecalho
        frame_cabecalho = ctk.CTkFrame(
            parent,
            corner_radius=0,
            fg_color="#ffffff",
            border_width=0,
            border_color="#dee2e6"
        )
        frame_cabecalho.pack(fill="x", padx=0, pady=(0, 30))

        # Titulo principal
        label_titulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Portal Antigo Saude MG",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#212529"
        )
        label_titulo.pack(pady=(30, 5))

        # Subtitulo
        label_subtitulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Selecione o periodo para consulta",
            font=ctk.CTkFont(size=16),
            text_color="#6c757d"
        )
        label_subtitulo.pack(pady=(0, 30))

    def _criar_secao_periodo(self, parent):
        """Cria secao de selecao de periodo (Ano e Mes)"""
        # Frame do periodo
        frame_periodo = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        frame_periodo.pack(fill="x", padx=20, pady=(0, 20))

        # Titulo da secao
        label_periodo = ctk.CTkLabel(
            frame_periodo,
            text="Seleção de Periodo",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_periodo.pack(pady=(15, 10))

        # Container para os dropdowns lado a lado
        container_dropdowns = ctk.CTkFrame(frame_periodo, fg_color="transparent")
        container_dropdowns.pack(fill="x", padx=15, pady=(0, 15))

        # Frame para centralizar os dropdowns
        frame_central = ctk.CTkFrame(container_dropdowns, fg_color="transparent")
        frame_central.pack(expand=True)

        # === Dropdown de Ano ===
        frame_ano = ctk.CTkFrame(frame_central, fg_color="transparent")
        frame_ano.pack(side="left", padx=20)

        label_ano = ctk.CTkLabel(
            frame_ano,
            text="Selecione o Ano:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_ano.pack(pady=(0, 5))

        self.dropdown_ano = ctk.CTkOptionMenu(
            frame_ano,
            values=self._obter_opcoes_anos(),
            variable=self.ano_var,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=200,
            height=40,
            command=self._on_ano_change
        )
        self.dropdown_ano.pack()

        # Label de status do ano
        self.label_status_periodo = ctk.CTkLabel(
            frame_ano,
            text=f"Ano selecionado: {self.ano_var.get()}",
            font=ctk.CTkFont(size=12),
            text_color="#6c757d"
        )
        self.label_status_periodo.pack(pady=(5, 0))

        # === Dropdown de Mes ===
        frame_mes = ctk.CTkFrame(frame_central, fg_color="transparent")
        frame_mes.pack(side="left", padx=20)

        label_mes = ctk.CTkLabel(
            frame_mes,
            text="Selecione o Mês:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_mes.pack(pady=(0, 5))

        self.dropdown_mes = ctk.CTkOptionMenu(
            frame_mes,
            values=self._obter_opcoes_meses(),
            variable=self.mes_var,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=200,
            height=40,
            command=self._on_mes_change
        )
        self.dropdown_mes.pack()

        # Label de status do mes
        self.label_status_mes = ctk.CTkLabel(
            frame_mes,
            text=f"Mes selecionado: {self.mes_var.get()}",
            font=ctk.CTkFont(size=12),
            text_color="#6c757d"
        )
        self.label_status_mes.pack(pady=(5, 0))

    def _criar_botoes_acao(self, parent):
        """Cria botoes de acao principais"""
        # Container para os botoes
        frame_acoes = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="white",
            border_width=2,
            border_color="#0066cc"
        )
        frame_acoes.pack(fill="x", padx=20, pady=(10, 30))

        # Loading indicator
        self.loading_indicator = LoadingIndicator(frame_acoes)

        # Container interno para centralizar botoes
        container_botoes = ctk.CTkFrame(frame_acoes, fg_color="transparent")
        container_botoes.pack(pady=15)

        # Botao Executar usando ButtonFactory
        self.botao_executar = ButtonFactory.create_execute_button(
            container_botoes,
            command=self._executar_consulta,
            width=280
        )
        self.botao_executar.configure(text="EXECUTAR CONSULTA")
        self.botao_executar.pack(side="left", padx=10)

        # Botao Abrir Pasta usando ButtonFactory
        self.botao_abrir_pasta = ButtonFactory.create_folder_button(
            container_botoes,
            command=self._abrir_pasta,
            width=160
        )
        self.botao_abrir_pasta.pack(side="left", padx=10)

        # Adicionar efeito hover aos botoes
        ButtonFactory.add_hover_effect(self.botao_executar, 280)
        ButtonFactory.add_hover_effect(self.botao_abrir_pasta, 160)

    def _executar_consulta(self):
        """Executa a consulta ou cancela execucao em andamento"""
        if self.executando:
            self._cancelar_execucao()
            return

        try:
            self._iniciar_execucao()
        except Exception as e:
            self._mostrar_erro(f"Erro ao executar: {str(e)}")
            self._habilitar_interface(True)

    def _iniciar_execucao(self):
        """Inicia o processo de consulta Portal Saude MG"""
        # Desabilita interface e muda botao para cancelar
        self._habilitar_interface(False)

        # Execucao real em thread separada
        def executar_thread():
            try:
                from src.bots.bot_portal_saude import BotPortalSaude

                # Cria instancia do bot
                self.bot_portal_saude = BotPortalSaude()

                # Obtem parametros selecionados
                ano = self.ano_var.get()
                mes = self.mes_var.get()

                print(f"Iniciando consulta Portal Saude MG - Ano: {ano}, Mes: {mes}")

                # Executa processamento
                resultado = self.bot_portal_saude.processar(ano, mes)

                if not self._cancelado:
                    if resultado.get('sucesso'):
                        self.parent_container.after(0, self._finalizar_execucao_sucesso, resultado)
                    else:
                        self.parent_container.after(0, self._finalizar_execucao_erro, resultado.get('erro'))

            except Exception as e:
                if not self._cancelado:
                    self.parent_container.after(0, self._finalizar_execucao_erro, str(e))

            finally:
                # Limpa recursos do bot
                if self.bot_portal_saude:
                    self.bot_portal_saude.fechar_navegador()
                    self.bot_portal_saude = None

                self.executando = False

        # Inicializa flag de cancelamento
        self._cancelado = False

        # Inicia thread
        self.thread_execucao = threading.Thread(target=executar_thread, daemon=True)
        self.thread_execucao.start()

    def _cancelar_execucao(self):
        """Cancela a execucao em andamento"""
        try:
            self._cancelado = True

            # Cancela o bot se estiver executando
            if self.bot_portal_saude:
                self.bot_portal_saude.cancelar(forcado=True)

            self._habilitar_interface(True)
            self._mostrar_info("Consulta cancelada com sucesso")

        except Exception as e:
            self._mostrar_erro(f"Erro ao cancelar: {str(e)}")
            self._habilitar_interface(True)

    def _finalizar_execucao_sucesso(self, resultado):
        """Finaliza execucao com sucesso"""
        if self._cancelado:
            return

        self._habilitar_interface(True)

        mensagem = (
            f"Consulta concluida com sucesso!\n\n"
            f"Links encontrados: {resultado.get('total_links', 0)}\n"
            f"Arquivos baixados: {resultado.get('total_baixados', 0)}\n\n"
            f"Diretorio: {resultado.get('diretorio_saida', '')}"
        )
        self._mostrar_info(mensagem)

    def _finalizar_execucao_erro(self, erro):
        """Finaliza execucao com erro"""
        if self._cancelado:
            return

        self._habilitar_interface(True)
        self._mostrar_erro(f"Erro durante execucao: {erro}")

    def _abrir_pasta(self):
        """Abre a pasta de arquivos do Portal Saude MG no explorador"""
        try:
            from src.classes.file.path_manager import obter_caminho_dados

            # Caminho da pasta
            pasta = obter_caminho_dados("arquivos_baixados/portal_saude_mg")

            # Cria a pasta se nao existir
            if not os.path.exists(pasta):
                os.makedirs(pasta)
                print(f"Pasta criada: {pasta}")

            # Detecta o sistema operacional e abre a pasta
            sistema = platform.system()

            if sistema == "Windows":
                os.startfile(pasta)
            elif sistema == "Darwin":
                subprocess.run(["open", pasta])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", pasta])
            else:
                self._mostrar_erro(f"Sistema operacional '{sistema}' nao suportado")
                return

            print(f"Pasta aberta: {pasta}")

        except Exception as e:
            self._mostrar_erro(f"Erro ao abrir pasta: {str(e)}")

    def _habilitar_interface(self, habilitado=True):
        """Habilita/desabilita elementos da interface"""
        self.executando = not habilitado

        # Atualiza dropdown de ano
        if hasattr(self, 'dropdown_ano'):
            self.dropdown_ano.configure(state="normal" if habilitado else "disabled")

        # Atualiza dropdown de mes
        if hasattr(self, 'dropdown_mes'):
            self.dropdown_mes.configure(state="normal" if habilitado else "disabled")

        # Controla loading indicator
        if self.loading_indicator:
            if habilitado:
                self.loading_indicator.hide()
            else:
                self.loading_indicator.show("Processando...")

        # Botao abrir pasta sempre fica habilitado
        self.botao_abrir_pasta.configure(state="normal")

        # Atualiza botao executar/cancelar
        if habilitado:
            # Modo normal - botao azul "EXECUTAR"
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=False)
            self.botao_executar.configure(
                text="EXECUTAR CONSULTA",
                state="normal"
            )
        else:
            # Modo execucao - botao vermelho "CANCELAR"
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=True)
            self.botao_executar.configure(
                text="CANCELAR CONSULTA",
                state="normal"
            )

    def _mostrar_erro(self, mensagem):
        """Mostra mensagem de erro"""
        messagebox.showerror("Erro", mensagem)

    def _mostrar_info(self, mensagem):
        """Mostra mensagem informativa"""
        messagebox.showinfo("Informacao", mensagem)

    def obter_parametros(self):
        """Retorna os parametros selecionados na interface"""
        return {
            "ano": self.ano_var.get(),
            "mes": self.mes_var.get()
        }

    def mostrar(self):
        """Mostra esta interface"""
        if self.main_frame:
            self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def ocultar(self):
        """Oculta esta interface"""
        if self.main_frame:
            self.main_frame.pack_forget()
