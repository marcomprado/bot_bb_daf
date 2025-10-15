#!/usr/bin/env python3
"""
GUI1 - Interface gráfica para o sistema BB DAF
Interface de usuário pura, sem lógica de negócio
"""

import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Callable

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.classes.city_splitter import CitySplitter
from src.classes.file.path_manager import obter_caminho_dados, obter_caminho_recurso, copiar_arquivo_cidades_se_necessario
from src.view.modules.buttons import ButtonFactory


class GUI1:
    """Interface gráfica principal para o sistema BB DAF"""
    
    def __init__(self, parent_frame: ctk.CTkFrame = None, 
                 on_executar: Callable = None,
                 on_cancelar: Callable = None):
        """
        Inicializa a GUI1
        
        Args:
            parent_frame: Frame pai onde a GUI será criada
            on_executar: Callback quando usuário clica em executar
            on_cancelar: Callback quando usuário clica em cancelar
        """
        self.parent_frame = parent_frame
        self.on_executar = on_executar
        self.on_cancelar = on_cancelar
        
        # Estado da interface
        self.executando = False
        
        # Dados
        self.lista_cidades = []
        self.cidades_selecionadas = []
        self.cidade_selecionada = ctk.StringVar()  # Para o dropdown
        
        # Variáveis de data
        self.data_inicial_var = ctk.StringVar()
        self.data_final_var = ctk.StringVar()
        
        # Sistema de divisão de cidades
        caminho_cidades = obter_caminho_dados("cidades.txt")
        self.city_splitter = CitySplitter(caminho_cidades)
        self.num_instancias = 1
        self.modo_execucao = "individual"
        
        # Frame principal da GUI1
        self.main_frame = None
        
        self._configurar_datas_padrao()
        self._criar_interface()
        self._carregar_cidades()
        
        # Atualiza dropdown após carregar cidades
        if hasattr(self, 'dropdown_cidade'):
            self.dropdown_cidade.configure(values=self._obter_opcoes_cidades())
            if self.lista_cidades:
                self.cidade_selecionada.set("Todas as Cidades")
    
    def _configurar_datas_padrao(self):
        """Configura datas padrão"""
        data_atual = datetime.now()
        data_inicial = data_atual - timedelta(days=30)
        
        self.data_inicial_var.set(data_inicial.strftime("%d/%m/%Y"))
        self.data_final_var.set(data_atual.strftime("%d/%m/%Y"))
    
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
        """Cria seção de seleção de datas - RESPONSIVA"""
        # Frame das datas
        frame_datas = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        frame_datas.pack(fill="x", padx=20, pady=(0, 20))
        
        # Título da seção
        label_datas = ctk.CTkLabel(
            frame_datas,
            text="Período de Consulta",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_datas.pack(pady=(15, 5))
        
        # Subtítulo com informação sobre limite
        label_subtitulo_datas = ctk.CTkLabel(
            frame_datas,
            text="O sistema abrange no máximo o periodo de um mês por pesquisa",
            font=ctk.CTkFont(size=12),
            text_color="#6c757d"
        )
        label_subtitulo_datas.pack(pady=(0, 10))
        
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
        
        # Adiciona validação para aceitar apenas números e barras
        self.entry_data_inicial.bind('<KeyPress>', self._validar_tecla_data)
        self.entry_data_inicial.bind('<FocusOut>', lambda e: self._formatar_data_completa(self.data_inicial_var))
        
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
        
        # Adiciona validação para aceitar apenas números e barras
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
    
    def _carregar_cidades(self):
        """Carrega lista de cidades do arquivo"""
        try:
            caminho_arquivo = obter_caminho_dados("cidades.txt")
            if os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                    self.lista_cidades = [linha.strip() for linha in arquivo if linha.strip()]
            
            # Atualiza dropdown após carregar cidades
            if hasattr(self, 'dropdown_cidade') and self.lista_cidades:
                self.dropdown_cidade.configure(values=self._obter_opcoes_cidades())
                self.cidade_selecionada.set("Todas as Cidades")
                self._on_cidade_change("Todas as Cidades")
                
        except Exception as e:
            self._mostrar_erro(f"Erro ao carregar cidades: {str(e)}")
            self.lista_cidades = []
    
    def _salvar_cidades_selecionadas(self):
        """Salva cidades selecionadas no arquivo listed_cities.txt"""
        try:
            caminho_arquivo = obter_caminho_dados("listed_cities.txt")
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                for cidade in self.cidades_selecionadas:
                    arquivo.write(f"{cidade}\n")
        except Exception as e:
            raise Exception(f"Erro ao salvar cidades: {str(e)}")
    
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
        """Valida se os dados estão corretos"""
        # Atualiza cidades selecionadas com base no dropdown
        self._atualizar_cidades_selecionadas()
        
        # Verifica se há cidades selecionadas
        if not self.cidades_selecionadas:
            self._mostrar_erro("Por favor, selecione pelo menos uma cidade!")
            return False
        
        # Verifica formato das datas
        try:
            data_inicial = datetime.strptime(self.data_inicial_var.get(), "%d/%m/%Y")
            data_final = datetime.strptime(self.data_final_var.get(), "%d/%m/%Y")
        except ValueError:
            self._mostrar_erro("Formato de data inválido! Use DD/MM/AAAA")
            return False
        
        # Verifica se a data inicial é anterior à data final
        if data_inicial >= data_final:
            self._mostrar_erro("A data inicial deve ser anterior à data final!")
            return False
        
        # Verifica se o período não excede 30 dias
        diferenca_dias = (data_final - data_inicial).days
        if diferenca_dias > 30:
            self._mostrar_erro(f"O período selecionado é de {diferenca_dias} dias. O sistema permite no máximo 30 dias por pesquisa!")
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
        """Dispara callback de execução ou cancelamento"""
        if self.executando:
            # Se está executando, dispara callback de cancelar
            if self.on_cancelar:
                self.on_cancelar()
            self._habilitar_interface(True)
            return
        
        # Valida dados
        if not self._validar_dados():
            return
        
        # Prepara parâmetros
        parametros = self.obter_parametros()
        
        # Desabilita interface
        self._habilitar_interface(False)
        
        # Dispara callback de execução
        if self.on_executar:
            self.on_executar(parametros)
    
    def obter_parametros(self) -> Dict:
        """
        Obtém os parâmetros configurados na interface
        
        Returns:
            dict: Parâmetros para execução
        """
        return {
            'modo': self.modo_execucao,
            'cidades': self.cidades_selecionadas.copy(),
            'data_inicial': self.data_inicial_var.get(),
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