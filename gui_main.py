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
from datetime import datetime, timedelta
from typing import List


class SeletorCidades:
    """Popup nativo para seleção de cidades"""
    
    def __init__(self, parent, lista_cidades):
        self.parent = parent
        self.lista_cidades = lista_cidades
        self.cidades_selecionadas = []
        
        # Janela popup
        self.popup = tk.Toplevel(parent.janela)
        self.popup.title("Seleção de Cidades")
        self.popup.geometry("450x550")
        self.popup.resizable(False, False)
        self.popup.configure(bg='#f8f9fa')
        self.popup.transient(parent.janela)
        self.popup.grab_set()
        
        # Centraliza popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (550 // 2)
        self.popup.geometry(f"450x550+{x}+{y}")
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria interface do seletor com melhor visibilidade"""
        # Título
        titulo = tk.Label(
            self.popup,
            text="Selecione as Cidades",
            font=("Arial", 18, "bold"),
            bg='#f8f9fa',
            fg='#212529',
            pady=15
        )
        titulo.pack()
        
        # Frame para listbox e scrollbar
        frame_lista = tk.Frame(self.popup, bg='#f8f9fa')
        frame_lista.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Listbox com seleção múltipla
        self.listbox = tk.Listbox(
            frame_lista,
            selectmode="multiple",
            font=("Arial", 12),
            height=18,
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
        
        # Adiciona cidades à listbox
        for cidade in self.lista_cidades:
            self.listbox.insert(tk.END, cidade.title())
        
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
    
    def _limpar_selecao(self):
        """Limpa toda a seleção"""
        self.listbox.selection_clear(0, tk.END)
    
    def _confirmar(self):
        """Confirma seleção e fecha popup"""
        indices_selecionados = self.listbox.curselection()
        self.cidades_selecionadas = [
            self.lista_cidades[i] for i in indices_selecionados
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
        
        # Janela principal - RESPONSIVA
        self.janela = ctk.CTk()
        self.janela.title("Sistema FVN")
        self.janela.geometry("750x700")  # Altura reduzida
        self.janela.resizable(True, True)
        self.janela.minsize(600, 550)  # Tamanho mínimo responsivo
        self.janela.configure(fg_color="#f8f9fa")
        
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
        
        self._configurar_datas_padrao()
        self._centralizar_janela()
        self._criar_interface()
        self._carregar_cidades()
    
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
            text="Automação de consultas",
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
    
    def _criar_botoes_acao(self, parent):
        """Cria apenas botão principal de execução - RESPONSIVO"""
        # Container menor apenas para botão executar
        frame_executar = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="white",
            border_width=2,
            border_color="#0066cc"
        )
        frame_executar.pack(fill="x", padx=20, pady=(10, 30))
        
        # Botão Executar centralizado - TAMANHO PADRONIZADO
        self.botao_executar = ctk.CTkButton(
            frame_executar,
            text="EXECUTAR PROCESSAMENTO",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=55,  # MESMO TAMANHO DOS OUTROS
            corner_radius=27,
            fg_color="#0066cc",
            hover_color="#0052a3",
            command=self._executar_main,
            width=400  # Largura específica para o botão principal
        )
        self.botao_executar.pack(pady=15, padx=20)
        
        # Adicionar efeito hover
        self._adicionar_efeito_hover(self.botao_executar)
    
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
                botao.configure(width=400, height=55)  # Botão principal
        
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
        
        # Atualiza botões (removido botao_limpar)
        self.botao_todas.configure(state="normal" if habilitado else "disabled")
        self.botao_individual.configure(state="normal" if habilitado else "disabled")
        
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
            
        except Exception as e:
            self._mostrar_erro(f"Erro ao executar: {str(e)}")
            self._habilitar_interface(True)
    
    def _cancelar_execucao(self):
        """Cancela a execução em andamento"""
        try:
            self._cancelado = True
            
            if hasattr(self, 'processo') and self.processo:
                # Termina o processo
                self.processo.terminate()
                
                # Aguarda um pouco e força encerramento se necessário
                try:
                    self.processo.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.processo.kill()
                    self.processo.wait()
            
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
            with open("listed_cities.txt", "w", encoding="utf-8") as arquivo:
                for cidade in self.cidades_selecionadas:
                    arquivo.write(f"{cidade}\n")
        except Exception as e:
            raise Exception(f"Erro ao salvar cidades: {str(e)}")
    
    def _carregar_cidades(self):
        """Carrega lista de cidades do arquivo"""
        try:
            if os.path.exists("cidades.txt"):
                with open("cidades.txt", "r", encoding="utf-8") as arquivo:
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