#!/usr/bin/env python3
"""
GUI1 - Interface gráfica para o sistema BB DAF
"""

import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import platform
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.classes.city_manager import CitySplitter
from src.classes.file.path_manager import obter_caminho_dados, obter_caminho_recurso, copiar_arquivo_cidades_se_necessario
from src.classes.city_manager import CityManager
from src.view.modules.buttons import ButtonFactory
from src.view.modules.loading_indicator import LoadingIndicator
from src.bots.bot_bbdaf import BotBBDAF
from src.classes.data_extractor import DataExtractor
from src.classes.methods.parallel_processor import ProcessadorParalelo


class GUI1:
    """Interface gráfica principal para o sistema BB DAF"""
    
    def __init__(self, parent_frame: ctk.CTkFrame = None):
        """
        Inicializa a GUI1

        Args:
            parent_frame: Frame pai onde a GUI será criada
        """
        self.parent_frame = parent_frame

        # Estado da execução
        self.executando = False
        self._cancelado = False
        self.bot_atual = None
        self.processador_paralelo = None
        self.thread_execucao = None
        
        # Dados
        self.lista_cidades = []
        self.cidades_selecionadas = []
        self.cidade_selecionada = ctk.StringVar()  # Para o dropdown
        
        # Variável de data
        self.data_final_var = ctk.StringVar()
        
        # Sistema de divisão de cidades
        caminho_cidades = obter_caminho_dados("cidades.txt")
        self.city_splitter = CitySplitter(caminho_cidades)
        self.num_instancias = 1
        self.modo_execucao = "individual"
        
        # Frame principal da GUI1
        self.main_frame = None

        # Loading indicator
        self.loading_indicator = None

        self._configurar_datas_padrao()
        self._criar_interface()

        # Carrega cidades usando CityManager
        self.city_manager = CityManager()
        self.lista_cidades = self.city_manager.obter_municipios_mg()

        # Atualiza dropdown após carregar cidades
        if hasattr(self, 'dropdown_cidade'):
            self.dropdown_cidade.configure(values=self._obter_opcoes_cidades())
            if self.lista_cidades:
                self.cidade_selecionada.set("Todas as Cidades")
    
    def _configurar_datas_padrao(self):
        self.data_final_var.set(datetime.now().strftime("%d/%m/%Y"))
    
    def _criar_interface(self):
        """Cria a interface da GUI1"""
        if self.parent_frame:
            # Frame scrollable principal
            self.main_frame = ctk.CTkScrollableFrame(
                self.parent_frame,
                corner_radius=0,
                fg_color="#f8f9fa"
            )
            
            # Cabeçalho
            self._criar_cabecalho(self.main_frame)
            
            # Seções principais
            self._criar_secao_datas(self.main_frame)
            self._criar_secao_cidades(self.main_frame)
            self._criar_secao_execucao_paralela(self.main_frame)
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
            text="Sistema Scraping Banco do Brasil DAF",
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
        frame_datas = ctk.CTkFrame(
            parent, corner_radius=20, fg_color="#f8f9fa",
            border_width=1, border_color="#dee2e6"
        )
        frame_datas.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            frame_datas, text="Data de Referencia",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#495057"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            frame_datas, text="O sistema consulta os 30 dias anteriores a esta data",
            font=ctk.CTkFont(size=12), text_color="#6c757d"
        ).pack(pady=(0, 10))

        container_campo = ctk.CTkFrame(frame_datas, fg_color="transparent")
        container_campo.pack(pady=(0, 15))

        self.entry_data_final = ctk.CTkEntry(
            container_campo, textvariable=self.data_final_var,
            placeholder_text="DD/MM/AAAA", font=ctk.CTkFont(size=14),
            height=40, width=200, corner_radius=15, justify="center",
            border_width=2, border_color="#ced4da"
        )
        self.entry_data_final.pack()
        self.entry_data_final.bind('<KeyPress>', self._validar_tecla_data)
        self.entry_data_final.bind('<FocusOut>', lambda e: self._formatar_data_completa(self.data_final_var))
    
    def _criar_secao_cidades(self, parent):
        """Cria seção de seleção de cidades - ESTILO DROPDOWN COMO GUI2"""
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
        
        # Container do campo de cidade
        container_cidade = ctk.CTkFrame(frame_cidades, fg_color="transparent")
        container_cidade.pack(fill="x", padx=15, pady=(0, 15))
        
        # Campo de cidade centralizado
        frame_cidade_campo = ctk.CTkFrame(container_cidade, fg_color="transparent")
        frame_cidade_campo.pack(expand=True)
        
        label_cidade_campo = ctk.CTkLabel(
            frame_cidade_campo,
            text="Selecione a Cidade:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_cidade_campo.pack(pady=(0, 5))
        
        # Dropdown com cidades (usado em todas as plataformas)
        self.dropdown_cidade = ctk.CTkOptionMenu(
            frame_cidade_campo,
            values=self._obter_opcoes_cidades(),
            variable=self.cidade_selecionada,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=300,
            height=40,
            command=self._on_cidade_change
        )
        self.dropdown_cidade.pack()

        # Define valor padrão
        if self.lista_cidades:
            self.cidade_selecionada.set("Todas as Cidades")
        
        # Label de status da seleção
        self.label_status_selecao = ctk.CTkLabel(
            frame_cidades,
            text="Todas as cidades de MG selecionadas (852 cidades)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#495057"
        )
        self.label_status_selecao.pack(pady=(0, 15))
    
    def _criar_secao_execucao_paralela(self, parent):
        """Cria seção de execução paralela - SIMPLIFICADA"""
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
            text="Modo de Execução",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_titulo.pack(pady=(15, 10))
        
        # Container dos controles
        container_controles = ctk.CTkFrame(
            frame_paralela,
            fg_color="transparent"
        )
        container_controles.pack(fill="x", padx=15, pady=(0, 10))
        
        # Frame para modo de execução centralizado
        frame_modo = ctk.CTkFrame(container_controles, fg_color="transparent")
        frame_modo.pack(expand=True)
        
        label_modo = ctk.CTkLabel(
            frame_modo,
            text="Selecione o Modo:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_modo.pack(pady=(0, 5))
        
        # Dropdown modo execução - Apenas Individual ou Paralelo
        self.dropdown_modo = ctk.CTkOptionMenu(
            frame_modo,
            values=["Individual", "Paralelo (2 instâncias)", "Paralelo (3 instâncias)", "Paralelo (4 instâncias)", "Paralelo (5 instâncias)"],
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            command=self._on_modo_change,
            width=200,
            height=40
        )
        self.dropdown_modo.set("Individual")
        self.dropdown_modo.pack()
        
        # Label de status da distribuição
        self.label_distribuicao = ctk.CTkLabel(
            frame_paralela,
            text="Modo Paralelo acelera o processamento em até 5x",
            font=ctk.CTkFont(size=12),
            text_color="#495057",
            justify="left"
        )
        self.label_distribuicao.pack(pady=(0, 15))
    
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

        # Loading indicator
        self.loading_indicator = LoadingIndicator(frame_acoes)

        # Container interno para centralizar botões
        container_botoes = ctk.CTkFrame(frame_acoes, fg_color="transparent")
        container_botoes.pack(pady=15)
        
        # Botão Executar usando ButtonFactory
        self.botao_executar = ButtonFactory.create_execute_button(
            container_botoes,
            command=self._executar_main,
            width=300
        )
        self.botao_executar.configure(text="EXECUTAR PROCESSAMENTO")  # Texto customizado para GUI1
        self.botao_executar.pack(side="left", padx=10)
        
        # Botão Abrir Pasta usando ButtonFactory
        self.botao_abrir_pasta = ButtonFactory.create_folder_button(
            container_botoes,
            command=self._abrir_pasta_arquivos,
            width=200,
            text="ABRIR ARQUIVOS"
        )
        self.botao_abrir_pasta.pack(side="left", padx=10)
        
        # Adicionar efeito hover aos botões
        ButtonFactory.add_hover_effect(self.botao_executar, 300)
        ButtonFactory.add_hover_effect(self.botao_abrir_pasta, 200)
    
    
    def _on_modo_change(self, valor):
        """Callback quando o modo de execução é alterado"""
        if valor == "Individual":
            self.modo_execucao = "individual"
            self.num_instancias = 1
            self.label_distribuicao.configure(text="Processamento individual - uma instância do navegador")
        else:
            self.modo_execucao = "paralelo"
            # Extrai número de instâncias do texto
            if "2 instâncias" in valor:
                self.num_instancias = 2
            elif "3 instâncias" in valor:
                self.num_instancias = 3
            elif "4 instâncias" in valor:
                self.num_instancias = 4
            elif "5 instâncias" in valor:
                self.num_instancias = 5
            else:
                self.num_instancias = 2  # Default
            
            # Calcula distribuição automaticamente
            self._calcular_distribuicao()
    
    def _calcular_distribuicao(self):
        """Calcula e exibe a distribuição das cidades"""
        try:
            if self.modo_execucao == "individual":
                self.label_distribuicao.configure(text="Processamento individual - uma instância do navegador")
                return
            
            # Valida número de instâncias (máximo 5)
            if self.num_instancias > 5:
                self.num_instancias = 5
            
            # Calcula distribuição
            if hasattr(self.city_splitter, 'obter_resumo_distribuicao'):
                resumo = self.city_splitter.obter_resumo_distribuicao(self.num_instancias)
                self.label_distribuicao.configure(text=resumo)
            else:
                # Fallback simples
                total_cidades = len(self.cidades_selecionadas) if self.cidades_selecionadas else len(self.lista_cidades)
                cidades_por_instancia = total_cidades // self.num_instancias
                resto = total_cidades % self.num_instancias
                texto = f"Processamento paralelo com {self.num_instancias} instâncias\n"
                texto += f"Aproximadamente {cidades_por_instancia} cidades por instância"
                if resto > 0:
                    texto += f" (+{resto} na primeira instância)"
                self.label_distribuicao.configure(text=texto)
            
        except Exception as e:
            self.label_distribuicao.configure(text=f"Paralelo com {self.num_instancias} instâncias")
    
    def _obter_opcoes_cidades(self):
        """Retorna lista de opções para o dropdown de cidades"""
        opcoes = ["Todas as Cidades"]
        if self.lista_cidades:
            # Adiciona cidades em ordem alfabética
            cidades_ordenadas = sorted(self.lista_cidades)
            opcoes.extend([cidade.title() for cidade in cidades_ordenadas])
        return opcoes
    
    def _on_cidade_change(self, valor):
        """Callback quando cidade é alterada no dropdown"""
        if valor == "Todas as Cidades":
            self.label_status_selecao.configure(
                text=f"Todas as cidades de MG selecionadas ({len(self.lista_cidades)} cidades)"
            )
        else:
            self.label_status_selecao.configure(
                text=f"Cidade selecionada: {valor}"
            )
        
        # Recalcula distribuição se estiver em modo paralelo
        if self.modo_execucao == "paralelo":
            self._calcular_distribuicao()
    
    def _atualizar_cidades_selecionadas(self):
        """Atualiza lista de cidades selecionadas com base no dropdown"""
        valor = self.cidade_selecionada.get()
        
        if valor == "Todas as Cidades" or not valor:
            self.cidades_selecionadas = self.lista_cidades.copy()
        else:
            # Converte de volta para formato original (uppercase)
            cidade_upper = valor.upper()
            # Procura a cidade na lista original
            for cidade in self.lista_cidades:
                if cidade.upper() == cidade_upper:
                    self.cidades_selecionadas = [cidade]
                    break
            else:
                # Se não encontrou, usa como está
                self.cidades_selecionadas = [valor]
    
    def _abrir_pasta_arquivos(self):
        """Abre a pasta de arquivos BB DAF no explorador do sistema"""
        try:
            pasta_arquivos = obter_caminho_dados("bbdaf")
            
            # Cria a pasta se não existir
            if not os.path.exists(pasta_arquivos):
                os.makedirs(pasta_arquivos)
                print(f"Pasta criada: {pasta_arquivos}")
            
            # Detecta o sistema operacional e abre a pasta
            sistema = platform.system()
            
            if sistema == "Windows":
                os.startfile(pasta_arquivos)
            elif sistema == "Darwin":
                subprocess.run(["open", pasta_arquivos])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", pasta_arquivos])
            else:
                self._mostrar_erro(f"Sistema operacional '{sistema}' não suportado")
                return
            
            print(f"Pasta aberta: {pasta_arquivos}")
            
        except Exception as e:
            self._mostrar_erro(f"Erro ao abrir pasta: {str(e)}")
    
    def _validar_tecla_data(self, event):
        """Permite apenas números e barra nos campos de data"""
        # Permite números, barra, backspace, delete, setas
        if event.char.isdigit() or event.char == '/' or event.keysym in ['BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End']:
            return True
        else:
            return "break"  # Bloqueia a tecla
    
    def _formatar_data_completa(self, var_data):
        """Formata a data quando o usuário sai do campo"""
        try:
            texto = var_data.get().strip()
            if not texto:
                return
            
            # Se já está no formato correto, não mexe
            if len(texto) == 10 and texto.count('/') == 2:
                return
            
            # Se tem apenas números, tenta formatar
            apenas_numeros = ''.join(c for c in texto if c.isdigit())
            if len(apenas_numeros) == 8:
                data_formatada = f"{apenas_numeros[:2]}/{apenas_numeros[2:4]}/{apenas_numeros[4:8]}"
                var_data.set(data_formatada)
            
        except Exception:
            pass
    
    def _validar_dados(self):
        self._atualizar_cidades_selecionadas()
        if not self.cidades_selecionadas:
            self._mostrar_erro("Por favor, selecione pelo menos uma cidade!")
            return False
        try:
            datetime.strptime(self.data_final_var.get(), "%d/%m/%Y")
        except ValueError:
            self._mostrar_erro("Formato de data invalido! Use DD/MM/AAAA")
            return False
        return True
    
    def _habilitar_interface(self, habilitado=True):
        """Habilita/desabilita elementos da interface"""
        # Atualiza estado
        self.executando = not habilitado

        # Atualiza dropdown de cidades (todas as plataformas)
        if hasattr(self, 'dropdown_cidade'):
            self.dropdown_cidade.configure(state="normal" if habilitado else "disabled")
        
        # Atualiza controles de execução paralela
        self.dropdown_modo.configure(state="normal" if habilitado else "disabled")

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
            # Modo normal - botão azul "EXECUTAR"
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=False)
            self.botao_executar.configure(
                text="EXECUTAR PROCESSAMENTO",
                state="normal"
            )
        else:
            # Modo execução - botão vermelho "CANCELAR"
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=True)
            self.botao_executar.configure(
                text="CANCELAR PROCESSAMENTO",
                state="normal"
            )
    
    def _executar_main(self):
        """Executa o bot ou cancela execução em andamento"""
        if self.executando:
            self._cancelar_execucao()
            return

        if not self._validar_dados():
            return

        parametros = self.obter_parametros()
        self._habilitar_interface(False)
        self._executar_processo(parametros)

    def _executar_processo(self, parametros: Dict):
        """Inicia execução do bot em thread separada"""
        self._cancelado = False

        def executar_thread():
            try:
                modo = parametros.get('modo', 'individual')

                if modo == 'paralelo':
                    self.processador_paralelo = ProcessadorParalelo()
                    resultado = self.processador_paralelo.executar_paralelo_threads(
                        num_instancias=parametros.get('num_instancias', 2),
                        data_inicial=parametros.get('data_inicial'),
                        data_final=parametros.get('data_final')
                    )
                else:
                    self.bot_atual = BotBBDAF()
                    self.bot_atual.configurar_extrator_dados(DataExtractor("bbdaf"))
                    resultado = self.bot_atual.executar_completo(
                        cidades=parametros.get('cidades'),
                        data_inicial=parametros.get('data_inicial'),
                        data_final=parametros.get('data_final')
                    )

                if not self._cancelado:
                    self.parent_frame.after(0, self._finalizar_execucao, resultado)

            except Exception as e:
                if not self._cancelado:
                    resultado = {'sucesso': False, 'erro': str(e)}
                    self.parent_frame.after(0, self._finalizar_execucao, resultado)

        self.thread_execucao = threading.Thread(target=executar_thread, daemon=True)
        self.thread_execucao.start()

    def _finalizar_execucao(self, resultado: Dict):
        """Processa resultado e limpa referências"""
        self.bot_atual = None
        self.processador_paralelo = None
        self.processar_resultado(resultado)

    def _cancelar_execucao(self):
        """Cancela a execução em andamento"""
        self._cancelado = True

        if self.processador_paralelo:
            self.processador_paralelo.cancelar()

        if self.bot_atual:
            self.bot_atual.fechar_navegador()

        self.bot_atual = None
        self.processador_paralelo = None
        self._habilitar_interface(True)
    
    def obter_parametros(self) -> Dict:
        data_final = datetime.strptime(self.data_final_var.get(), "%d/%m/%Y")
        data_inicial = data_final - timedelta(days=30)
        return {
            'modo': self.modo_execucao,
            'cidades': self.cidades_selecionadas.copy(),
            'data_inicial': data_inicial.strftime("%d/%m/%Y"),
            'data_final': self.data_final_var.get(),
            'num_instancias': self.num_instancias if self.modo_execucao == 'paralelo' else 1
        }
    
    def processar_resultado(self, resultado: Dict):
        """
        Processa o resultado da execução
        
        Args:
            resultado: Resultado retornado pelo bot
        """
        self._habilitar_interface(True)
        
        if resultado.get('sucesso'):
            if 'estatisticas' in resultado:
                stats = resultado['estatisticas']
                mensagem = f"""Processamento concluído!
                
Total: {stats.get('total', 0)} cidades
                Sucessos: {stats.get('sucessos', 0)}
                Erros: {stats.get('erros', 0)}
                Taxa de sucesso: {stats.get('taxa_sucesso', 0):.1f}%"""
                self._mostrar_info(mensagem)
            else:
                self._mostrar_info("Processamento concluído com sucesso!")
        else:
            erro = resultado.get('erro', 'Erro desconhecido')
            self._mostrar_erro(f"Erro no processamento: {erro}")
    
    def atualizar_status(self, mensagem: str):
        """
        Atualiza o status na interface
        
        Args:
            mensagem: Mensagem de status
        """
        if hasattr(self, 'label_status_selecao'):
            self.label_status_selecao.configure(text=mensagem)
    
    def mostrar(self):
        """Mostra a GUI1"""
        if self.main_frame:
            self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    def ocultar(self):
        """Oculta a GUI1"""
        if self.main_frame:
            self.main_frame.pack_forget()
    
    def _mostrar_erro(self, mensagem):
        """Mostra mensagem de erro"""
        messagebox.showerror("Erro", mensagem)
    
    def _mostrar_info(self, mensagem):
        """Mostra mensagem informativa"""
        messagebox.showinfo("Informação", mensagem)
    
    def _mostrar_popup_processo_terminado(self):
        """Mostra popup padrão quando processo é terminado"""
        messagebox.showinfo("Processo Finalizado", "Processo foi terminado")