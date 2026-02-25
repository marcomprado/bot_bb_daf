# GUI para o bot bot_mariana_gestcom
import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import platform
import subprocess
import threading
from datetime import datetime
import calendar

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.view.modules.buttons import ButtonFactory
from src.view.modules.loading_indicator import LoadingIndicator
from src.bots.bot_mariana_gestcom import BotMarianaGestcom
from src.classes.file.path_manager import obter_caminho_dados


MESES = [
    "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]
ANOS = [str(a) for a in range(datetime.now().year, 2010, -1)]


class GUI8:

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame

        self.executando = False
        self._cancelado = False
        self.bot_atual = None
        self.thread_execucao = None
        self.main_frame = None
        self.loading_indicator = None

        self.periodo_var = ctk.StringVar(value="Mes e ano atual")
        self.mes_inicial_var = ctk.StringVar(value=MESES[datetime.now().month - 1])
        self.ano_inicial_var = ctk.StringVar(value=str(datetime.now().year))
        self.mes_final_var = ctk.StringVar(value=MESES[datetime.now().month - 1])
        self.ano_final_var = ctk.StringVar(value=str(datetime.now().year))
        self.relatorio_var = ctk.StringVar(value="Todos os relatorios")

        self._criar_interface()

    def _criar_interface(self):
        self.main_frame = ctk.CTkScrollableFrame(
            self.parent_frame, corner_radius=0, fg_color="#f8f9fa"
        )
        self._criar_cabecalho(self.main_frame)
        self._criar_secao_data(self.main_frame)
        self._criar_secao_relatorio(self.main_frame)
        self._criar_botoes_acao(self.main_frame)

    def _criar_cabecalho(self, parent):
        frame_cabecalho = ctk.CTkFrame(
            parent, corner_radius=0, fg_color="#ffffff",
            border_width=0, border_color="#dee2e6"
        )
        frame_cabecalho.pack(fill="x", padx=0, pady=(0, 30))

        ctk.CTkLabel(
            frame_cabecalho, text="Gestcom Mariana",
            font=ctk.CTkFont(size=28, weight="bold"), text_color="#212529"
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            frame_cabecalho, text="Extração de dados do sistema Gestcom - Mariana",
            font=ctk.CTkFont(size=16), text_color="#6c757d"
        ).pack(pady=(0, 30))

    def _criar_secao_data(self, parent):
        frame_data = ctk.CTkFrame(
            parent, corner_radius=20, fg_color="#f8f9fa",
            border_width=1, border_color="#dee2e6"
        )
        frame_data.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            frame_data, text="Data da Consulta",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#495057"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            frame_data, text="Selecione o periodo de consulta dos relatorios :",
            font=ctk.CTkFont(size=12), text_color="#6c757d"
        ).pack(pady=(0, 10))

        # dropdown periodo
        container_periodo = ctk.CTkFrame(frame_data, fg_color="transparent")
        container_periodo.pack(fill="x", padx=15, pady=(0, 15))
        frame_periodo = ctk.CTkFrame(container_periodo, fg_color="transparent")
        frame_periodo.pack(expand=True)

        ctk.CTkOptionMenu(
            frame_periodo,
            values=["Mes e ano atual", "Escolha um periodo..."],
            variable=self.periodo_var,
            font=ctk.CTkFont(size=14), dropdown_font=ctk.CTkFont(size=12),
            width=300, height=40,
            command=self._on_periodo_change
        ).pack()

        # frame oculto com selecao de mes/ano inicial e final
        self.frame_datas_custom = ctk.CTkFrame(frame_data, fg_color="transparent")
        self._criar_par_mes_ano(self.frame_datas_custom, "Periodo inicial:", self.mes_inicial_var, self.ano_inicial_var)
        self._criar_par_mes_ano(self.frame_datas_custom, "Periodo final:", self.mes_final_var, self.ano_final_var)

    def _criar_par_mes_ano(self, parent, label_text, mes_var, ano_var):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=(0, 10))

        ctk.CTkLabel(
            frame, text=label_text,
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#495057"
        ).pack(pady=(0, 5))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack()

        ctk.CTkOptionMenu(
            row, values=MESES, variable=mes_var,
            font=ctk.CTkFont(size=14), dropdown_font=ctk.CTkFont(size=12),
            width=150, height=40
        ).pack(side="left", padx=(0, 5))

        ctk.CTkOptionMenu(
            row, values=ANOS, variable=ano_var,
            font=ctk.CTkFont(size=14), dropdown_font=ctk.CTkFont(size=12),
            width=100, height=40
        ).pack(side="left")

    def _on_periodo_change(self, valor):
        if valor == "Escolha um periodo...":
            self.frame_datas_custom.pack(fill="x", padx=15, pady=(0, 15))
        else:
            self.frame_datas_custom.pack_forget()

    def _criar_secao_relatorio(self, parent):
        frame_relatorio = ctk.CTkFrame(
            parent, corner_radius=20, fg_color="#f8f9fa",
            border_width=1, border_color="#dee2e6"
        )
        frame_relatorio.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            frame_relatorio, text="Relatorio",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#495057"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            frame_relatorio, text="Selecione o tipo de relatorio a ser extraido :",
            font=ctk.CTkFont(size=12), text_color="#6c757d"
        ).pack(pady=(0, 10))

        container = ctk.CTkFrame(frame_relatorio, fg_color="transparent")
        container.pack(fill="x", padx=15, pady=(0, 15))
        frame_campo = ctk.CTkFrame(container, fg_color="transparent")
        frame_campo.pack(expand=True)

        ctk.CTkOptionMenu(
            frame_campo,
            values=["Todos os relatorios", "Listagem de Requerimentos", "Contas Recebidas"],
            variable=self.relatorio_var,
            font=ctk.CTkFont(size=14), dropdown_font=ctk.CTkFont(size=12),
            width=300, height=40
        ).pack()

    def _criar_botoes_acao(self, parent):
        frame_acoes = ctk.CTkFrame(
            parent, corner_radius=20, fg_color="white",
            border_width=2, border_color="#0066cc"
        )
        frame_acoes.pack(fill="x", padx=20, pady=(10, 30))

        self.loading_indicator = LoadingIndicator(frame_acoes)

        container_botoes = ctk.CTkFrame(frame_acoes, fg_color="transparent")
        container_botoes.pack(pady=15)

        self.botao_executar = ButtonFactory.create_execute_button(
            container_botoes, command=self._executar_main, width=280
        )
        self.botao_executar.pack(side="left", padx=10)
        ButtonFactory.add_hover_effect(self.botao_executar, 280)

        self.botao_pasta = ButtonFactory.create_folder_button(
            container_botoes, command=self._abrir_pasta, width=160
        )
        self.botao_pasta.pack(side="left", padx=10)
        ButtonFactory.add_hover_effect(self.botao_pasta, 160)

    def _habilitar_interface(self, habilitado=True):
        self.executando = not habilitado
        if self.loading_indicator:
            if habilitado:
                self.loading_indicator.hide()
            else:
                self.loading_indicator.show("Processando...")
        ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=not habilitado)

    def _executar_main(self):
        if self.executando:
            self._cancelar_execucao()
            return
        self._habilitar_interface(False)
        self._cancelado = False
        self.thread_execucao = threading.Thread(target=self._thread_execucao, daemon=True)
        self.thread_execucao.start()

    def _thread_execucao(self):
        try:
            self.bot_atual = BotMarianaGestcom()
            if not self.bot_atual.configurar_navegador():
                self.parent_frame.after(0, self._finalizar_execucao, {"sucesso": False, "erro": "Falha ao configurar navegador"})
                return
            if not self.bot_atual.fazer_login():
                self.parent_frame.after(0, self._finalizar_execucao, {"sucesso": False, "erro": "Falha ao fazer login"})
                return
            # TODO: logica de processamento sera adicionada aqui
            self.parent_frame.after(0, self._finalizar_execucao, {"sucesso": True})
        except Exception as e:
            if not self._cancelado:
                self.parent_frame.after(0, self._finalizar_execucao, {"sucesso": False, "erro": str(e)})
        finally:
            if self.bot_atual:
                self.bot_atual.fechar_navegador()

    def _finalizar_execucao(self, resultado):
        self.bot_atual = None
        self._habilitar_interface(True)
        if resultado.get("sucesso"):
            messagebox.showinfo("Sucesso", "Processamento concluido")
        else:
            messagebox.showerror("Erro", resultado.get("erro", "Erro desconhecido"))

    def _abrir_pasta(self):
        try:
            pasta = obter_caminho_dados("gestcom_mariana")
            os.makedirs(pasta, exist_ok=True)
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(pasta)
            elif sistema == "Darwin":
                subprocess.run(["open", pasta])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", pasta])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta: {e}")

    def _cancelar_execucao(self):
        self._cancelado = True
        if self.bot_atual:
            self.bot_atual.cancelar(forcado=True)
            self.bot_atual.fechar_navegador()
        self.bot_atual = None
        self._habilitar_interface(True)

    def _ultimo_dia_mes(self, mes, ano):
        return calendar.monthrange(ano, mes)[1]

    def obter_parametros(self):
        if self.periodo_var.get() == "Mes e ano atual":
            mes_ini = datetime.now().month
            ano_ini = datetime.now().year
            mes_fim = mes_ini
            ano_fim = ano_ini
        else:
            mes_ini = MESES.index(self.mes_inicial_var.get()) + 1
            ano_ini = int(self.ano_inicial_var.get())
            mes_fim = MESES.index(self.mes_final_var.get()) + 1
            ano_fim = int(self.ano_final_var.get())
        data_inicial = f"{mes_ini:02d}01{ano_ini}"
        data_final = f"{mes_fim:02d}{self._ultimo_dia_mes(mes_fim, ano_fim):02d}{ano_fim}"
        return {
            "data_inicial": data_inicial,
            "data_final": data_final,
            "relatorio": self.relatorio_var.get()
        }

    def mostrar(self):
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def ocultar(self):
        self.main_frame.pack_forget()
