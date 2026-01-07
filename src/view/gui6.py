#!/usr/bin/env python3
"""
Interface gráfica - Pagamentos de Resoluções
Sistema para consulta de Pagamentos Orçamentárias e Restos a Pagar - MG
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

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# from src.bots.bot_pagamentos_res import BotPagamentosRes  # A ser implementado
from src.classes.city_manager import CityManager
from src.view.modules.buttons import ButtonFactory
from src.view.modules.loading_indicator import LoadingIndicator


class GUI6:
    """Interface gráfica para Pagamentos de Resoluções"""

    def __init__(self, parent_container):
        self.parent_container = parent_container

        # Estado da execução
        self.executando = False
        self.processo = None
        self.thread_execucao = None
        self._cancelado = False

        # Variáveis de configuração
        self.ano_var = ctk.StringVar()
        self.municipio_var = ctk.StringVar()
        self.lista_municipios = []
        self.municipios_selecionados = []  # Para preservar seleção no Windows

        # Bot de Pagamentos de Resoluções
        self.bot_pagamentos_res = None

        # Loading indicator
        self.loading_indicator = None

        self._configurar_valores_padrao()
        self._criar_interface()

    def _configurar_valores_padrao(self):
        """Configura valores padrão"""
        ano_atual = datetime.now().year
        self.ano_var.set(str(ano_atual))

        # Carrega lista de municípios usando CityManager
        self.city_manager = CityManager()
        self.lista_municipios = self.city_manager.obter_municipios_mg()

        # Define valor padrão do município
        if self.lista_municipios:
            self.municipio_var.set("Todos os Municípios")

    def _criar_interface(self):
        """Cria a interface da aba com scroll"""
        # Frame scrollable principal
        self.main_frame = ctk.CTkScrollableFrame(
            self.parent_container,
            corner_radius=0,
            fg_color="#f8f9fa"
        )

        # Cabeçalho
        self._criar_cabecalho(self.main_frame)

        # Seções principais
        self._criar_secao_ano(self.main_frame)
        self._criar_secao_municipios(self.main_frame)
        self._criar_botoes_acao(self.main_frame)

    def _criar_cabecalho(self, parent):
        """Cria cabeçalho"""
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
            text="Sistema Pagamentos de Resoluções",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#212529"
        )
        label_titulo.pack(pady=(30, 5))

        # Subtítulo
        label_subtitulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Orçamentárias e Restos a Pagar - Saúde MG",
            font=ctk.CTkFont(size=16),
            text_color="#6c757d"
        )
        label_subtitulo.pack(pady=(0, 30))

    def _criar_secao_ano(self, parent):
        """Cria seção de seleção do ano"""
        # Frame do ano
        frame_ano = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        frame_ano.pack(fill="x", padx=20, pady=(0, 20))

        # Título da seção
        label_ano = ctk.CTkLabel(
            frame_ano,
            text="Ano para Consulta",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_ano.pack(pady=(15, 10))

        # Container do campo de ano
        container_ano = ctk.CTkFrame(frame_ano, fg_color="transparent")
        container_ano.pack(fill="x", padx=15, pady=(0, 15))

        # Campo de ano centralizado
        frame_ano_campo = ctk.CTkFrame(container_ano, fg_color="transparent")
        frame_ano_campo.pack(expand=True)

        label_ano_campo = ctk.CTkLabel(
            frame_ano_campo,
            text="Selecione o Ano:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_ano_campo.pack(pady=(0, 5))

        # Dropdown com anos de 2000 a 2025
        anos_disponiveis = [str(ano) for ano in range(2025, 1999, -1)]  # 2025 até 2000
        self.dropdown_ano = ctk.CTkOptionMenu(
            frame_ano_campo,
            values=anos_disponiveis,
            variable=self.ano_var,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=150,
            height=40
        )
        self.dropdown_ano.pack()

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

        # Loading indicator
        self.loading_indicator = LoadingIndicator(frame_acoes)

        # Container interno para centralizar botões
        container_botoes = ctk.CTkFrame(frame_acoes, fg_color="transparent")
        container_botoes.pack(pady=15)

        # Botão Executar usando ButtonFactory
        self.botao_executar = ButtonFactory.create_execute_button(
            container_botoes,
            command=self._executar_scraper,
            width=280
        )
        self.botao_executar.pack(side="left", padx=10)

        # Botão Abrir Pasta usando ButtonFactory
        self.botao_abrir_pasta = ButtonFactory.create_folder_button(
            container_botoes,
            command=self._abrir_pasta_pagamentos_res,
            width=160
        )
        self.botao_abrir_pasta.pack(side="left", padx=10)

        # Adicionar efeito hover aos botões
        ButtonFactory.add_hover_effect(self.botao_executar, 280)
        ButtonFactory.add_hover_effect(self.botao_abrir_pasta, 160)


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

    def _mostrar_erro(self, mensagem):
        """Mostra mensagem de erro"""
        messagebox.showerror("Erro", mensagem)

    def _mostrar_info(self, mensagem):
        """Mostra mensagem informativa"""
        messagebox.showinfo("Informação", mensagem)

    def _validar_dados(self):
        """Valida se os dados estão corretos"""
        # Verifica se ano está selecionado
        ano = self.ano_var.get()
        if not ano or not ano.isdigit():
            self._mostrar_erro("Selecione um ano válido!")
            return False

        # Verifica se município está selecionado
        municipio = self.municipio_var.get()
        if not municipio:
            self._mostrar_erro("Selecione um município!")
            return False

        return True

    def _habilitar_interface(self, habilitado=True):
        """Habilita/desabilita elementos da interface"""
        self.executando = not habilitado

        # Atualiza controles
        self.dropdown_ano.configure(state="normal" if habilitado else "disabled")

        # Atualiza dropdown de municípios (todas as plataformas)
        if hasattr(self, 'dropdown_municipio'):
            self.dropdown_municipio.configure(state="normal" if habilitado else "disabled")

        # Controla loading indicator
        if self.loading_indicator:
            if habilitado:
                self.loading_indicator.hide()
            else:
                self.loading_indicator.show("Processando...")

        # Botão abrir pasta sempre fica habilitado
        self.botao_abrir_pasta.configure(state="normal")

        # Atualiza botão executar/cancelar
        if habilitado:
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=False)
            self.botao_executar.configure(state="normal")
        else:
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=True)
            self.botao_executar.configure(state="normal")

    def _executar_scraper(self):
        """Executa o scraper ou cancela execução"""
        if self.executando:
            self._cancelar_execucao()
            return

        # Valida dados
        if not self._validar_dados():
            return

        try:
            self._executar_processo()
        except Exception as e:
            self._mostrar_erro(f"Erro ao executar: {str(e)}")
            self._habilitar_interface(True)

    def _executar_processo(self):
        """Executa o processo principal do scraper de Pagamentos de Resoluções"""
        # Desabilita interface e muda botão para cancelar
        self._habilitar_interface(False)

        # Executa em thread separada
        def executar_subprocess():
            try:
                # Inicializa bot de Pagamentos de Resoluções
                from src.bots.bot_pagamentos_res import BotPagamentosRes
                self.bot_pagamentos_res = BotPagamentosRes()

                # Configurar navegadores
                if not self.bot_pagamentos_res.configurar_navegadores():
                    if not self._cancelado:
                        self.parent_container.after(0, self._finalizar_execucao_erro, "Falha ao configurar navegadores")
                    return

                ano = self.ano_var.get()
                municipio_selecionado = self.municipio_var.get()

                # Processa de acordo com seleção
                if municipio_selecionado == "Todos os Municípios":
                    # Processa todos os municípios sequencialmente
                    estatisticas = self.bot_pagamentos_res.processar_todos_municipios(ano)
                    if not self._cancelado:
                        self.parent_container.after(0, self._finalizar_execucao_todos, estatisticas)
                else:
                    # Processa município específico
                    resultado = self.bot_pagamentos_res.processar_municipio(ano, municipio_selecionado)
                    if not self._cancelado:
                        self.parent_container.after(0, self._finalizar_execucao_individual, resultado)

            except Exception as e:
                if not self._cancelado:
                    self.parent_container.after(0, self._finalizar_execucao_erro, str(e))
            finally:
                # Fechar navegadores
                if self.bot_pagamentos_res:
                    self.bot_pagamentos_res.fechar_navegadores()

        # Inicializa flag de cancelamento
        self._cancelado = False

        # Inicia thread
        self.thread_execucao = threading.Thread(target=executar_subprocess, daemon=True)
        self.thread_execucao.start()

    def _cancelar_execucao(self):
        """Cancela a execução em andamento com cancelamento forçado"""
        try:
            self._cancelado = True

            # TODO: Usa o método de cancelamento forçado quando bot estiver implementado
            # if self.bot_pagamentos_res:
            #     self.bot_pagamentos_res.cancelar_forcado()

            self._habilitar_interface(True)
            self._mostrar_info("Processamento cancelado")
        except Exception as e:
            self._mostrar_erro(f"Erro ao cancelar: {str(e)}")
            self._habilitar_interface(True)

    def _finalizar_execucao_todos(self, estatisticas):
        """Finaliza execução de todos os municípios"""
        if self._cancelado:
            return

        self._habilitar_interface(True)
        mensagem = f"Processamento concluído!\n\n"
        mensagem += f"Total: {estatisticas['total']} municípios\n"
        mensagem += f"Sucessos: {estatisticas['sucessos']}\n"
        mensagem += f"Erros: {estatisticas['erros']}\n"
        mensagem += f"Taxa de sucesso: {estatisticas['taxa_sucesso']:.1f}%"
        self._mostrar_info(mensagem)

    def _finalizar_execucao_individual(self, resultado):
        """Finaliza execução de município individual"""
        if self._cancelado:
            return

        self._habilitar_interface(True)

        if resultado['sucesso']:
            mensagem = f"Processamento concluído com sucesso!\n\n"
            mensagem += f"Município: {resultado['municipio']}\n"
            mensagem += f"Ano: {resultado['ano']}\n\n"

            # Mostra informações dos dois arquivos gerados
            if resultado['orcamentarios']['sucesso']:
                mensagem += f"✓ Orçamentários: {resultado['orcamentarios']['arquivo']}\n"
            else:
                mensagem += f"✗ Orçamentários: {resultado['orcamentarios'].get('erro', 'Erro desconhecido')}\n"

            if resultado['restos_a_pagar']['sucesso']:
                mensagem += f"✓ Restos a Pagar: {resultado['restos_a_pagar']['arquivo']}"
            else:
                mensagem += f"✗ Restos a Pagar: {resultado['restos_a_pagar'].get('erro', 'Erro desconhecido')}"

            self._mostrar_info(mensagem)
        else:
            # Mostra erros de ambos
            erros = []
            if not resultado['orcamentarios']['sucesso']:
                erros.append(f"Orçamentários: {resultado['orcamentarios'].get('erro', 'Erro desconhecido')}")
            if not resultado['restos_a_pagar']['sucesso']:
                erros.append(f"Restos a Pagar: {resultado['restos_a_pagar'].get('erro', 'Erro desconhecido')}")

            mensagem_erro = f"Erro ao processar {resultado['municipio']}:\n" + "\n".join(erros)
            self._mostrar_erro(mensagem_erro)

    def _finalizar_execucao_erro(self, erro):
        """Finaliza execução em caso de erro"""
        if self._cancelado:
            return

        self._habilitar_interface(True)
        self._mostrar_erro(f"Erro durante execução: {erro}")

    def _abrir_pasta_pagamentos_res(self):
        """Abre a pasta de arquivos de Pagamentos de Resoluções no explorador"""
        try:
            # Caminho da pasta usando path_manager
            from src.classes.file.path_manager import obter_caminho_dados
            pasta_pagamentos_res = obter_caminho_dados("pagamentos_resolucoes")

            # Cria a pasta se não existir
            if not os.path.exists(pasta_pagamentos_res):
                os.makedirs(pasta_pagamentos_res)

            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(pasta_pagamentos_res)
            elif sistema == "Darwin":
                subprocess.run(["open", pasta_pagamentos_res])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", pasta_pagamentos_res])
            else:
                self._mostrar_erro(f"Sistema operacional '{sistema}' não suportado")
                return

            print(f"Pasta Pagamentos de Resoluções aberta: {pasta_pagamentos_res}")

        except Exception as e:
            self._mostrar_erro(f"Erro ao abrir pasta: {str(e)}")

    def mostrar(self):
        """Mostra esta interface"""
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def ocultar(self):
        """Oculta esta interface"""
        self.main_frame.pack_forget()
