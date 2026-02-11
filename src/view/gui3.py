#!/usr/bin/env python3
"""
GUI3 - Interface gráfica para o sistema Betha Cloud
Interface com seleção de anos, cidades e execução paralela
"""

import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import threading
import subprocess
import platform
import json
from datetime import datetime

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.bots.bot_betha import BotBetha
from src.view.modules.buttons import ButtonFactory
from src.view.modules.loading_indicator import LoadingIndicator
from src.classes.file.path_manager import obter_caminho_dados
import time


class GUI3:
    """Interface gráfica para o scraper Betha"""
    
    def __init__(self, parent_container):
        self.parent_container = parent_container

        # Estado da execução
        self.executando = False
        self.bot_betha = None
        self.thread_execucao = None
        self._cancelado = False
        
        # Variáveis de configuração
        self.ano_var = ctk.StringVar()
        self.cidade_var = ctk.StringVar()  # Para Unix/Linux
        self.modo_var = ctk.StringVar()
        self.lista_cidades_betha = []
        self.anos_selecionados = []
        self.cidades_selecionadas = []

        # Armazena referência do executor para cancelamento
        self.executor = None
        self.futures = []
        self.bots_ativos = []  # Lista de instâncias BotBetha ativas

        # Loading indicator
        self.loading_indicator = None

        self._configurar_valores_padrao()
        self._criar_interface()
    
    def _configurar_valores_padrao(self):
        """Configura valores padrão"""
        # Ano atual
        ano_atual = datetime.now().year
        self.ano_var.set(str(ano_atual))

        # Carrega cidades do JSON
        self._carregar_cidades_betha()

        # Define valor padrão do modo de execução
        self.modo_var.set("Individual")
    
    def _carregar_cidades_betha(self):
        """Carrega cidades do arquivo city_betha.json"""
        try:
            caminho_json = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "src", "bots", "betha", "city_betha.json"
            )

            if os.path.exists(caminho_json):
                with open(caminho_json, "r", encoding="utf-8") as arquivo:
                    dados = json.load(arquivo)
                    cidades_obj = dados.get("cidades", {})

                    # Converte objeto para lista para compatibilidade com código existente
                    if isinstance(cidades_obj, dict):
                        self.lista_cidades_betha = list(cidades_obj.values())
                    else:
                        # Mantém compatibilidade com formato antigo (array)
                        self.lista_cidades_betha = cidades_obj if isinstance(cidades_obj, list) else []

                print(f"Carregadas {len(self.lista_cidades_betha)} cidades Betha")
            else:
                print("Arquivo city_betha.json não encontrado")
                self.lista_cidades_betha = []

        except Exception as e:
            print(f"Erro ao carregar cidades Betha: {e}")
            self.lista_cidades_betha = []
    
    def _criar_interface(self):
        """Cria a interface completa"""
        # Frame scrollable principal
        self.main_frame = ctk.CTkScrollableFrame(
            self.parent_container,
            corner_radius=0,
            fg_color="#f8f9fa"
        )
        
        # Cabeçalho
        self._criar_cabecalho(self.main_frame)
        
        # Seções principais
        self._criar_secao_anos(self.main_frame)
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
            text="Sistema Betha Cloud",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#212529"
        )
        label_titulo.pack(pady=(30, 5))
        
        # Subtítulo
        label_subtitulo = ctk.CTkLabel(
            frame_cabecalho,
            text="Automação Contábil Municipal",
            font=ctk.CTkFont(size=16),
            text_color="#6c757d"
        )
        label_subtitulo.pack(pady=(0, 30))
    
    def _criar_secao_anos(self, parent):
        """Cria seção de seleção de anos"""
        # Frame dos anos
        frame_anos = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color="#f8f9fa",
            border_width=1,
            border_color="#dee2e6"
        )
        frame_anos.pack(fill="x", padx=20, pady=(0, 20))
        
        # Título da seção
        label_anos = ctk.CTkLabel(
            frame_anos,
            text="Seleção de Anos",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#495057"
        )
        label_anos.pack(pady=(15, 10))
        
        # Container do campo de ano
        container_ano = ctk.CTkFrame(frame_anos, fg_color="transparent")
        container_ano.pack(fill="x", padx=15, pady=(0, 15))
        
        # Campo de ano centralizado
        frame_ano_campo = ctk.CTkFrame(container_ano, fg_color="transparent")
        frame_ano_campo.pack(expand=True)
        
        label_ano_campo = ctk.CTkLabel(
            frame_ano_campo,
            text="Selecione os Anos:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_ano_campo.pack(pady=(0, 5))

        # Dropdown com anos (usado em todas as plataformas)
        anos_disponiveis = ["Todos os Anos"] + [str(ano) for ano in range(datetime.now().year, 1997, -1)]
        self.dropdown_ano = ctk.CTkOptionMenu(
            frame_ano_campo,
            values=anos_disponiveis,
            variable=self.ano_var,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=300,
            height=40,
            command=self._on_ano_change
        )
        self.dropdown_ano.pack()

        # Label de status da seleção
        status_text = f"Ano atual selecionado ({datetime.now().year})"

        self.label_status_anos = ctk.CTkLabel(
            frame_anos,
            text=status_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#495057"
        )
        self.label_status_anos.pack(pady=(0, 15))
    
    def _criar_secao_cidades(self, parent):
        """Cria seção de seleção de cidades"""
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
            text="Selecione as Cidades:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#495057"
        )
        label_cidade_campo.pack(pady=(0, 5))

        # Dropdown com cidades (usado em todas as plataformas)
        self.dropdown_cidade = ctk.CTkOptionMenu(
            frame_cidade_campo,
            values=self._obter_opcoes_cidades(),
            variable=self.cidade_var,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            width=300,
            height=40,
            command=self._on_cidade_change
        )
        self.dropdown_cidade.pack()
        self.cidade_var.set("Todas as Cidades")

        # Label de status da seleção
        status_text = f"Todas as cidades selecionadas ({len(self.lista_cidades_betha)} cidades)"

        self.label_status_cidades = ctk.CTkLabel(
            frame_cidades,
            text=status_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#495057"
        )
        self.label_status_cidades.pack(pady=(0, 15))
    
    def _criar_secao_execucao_paralela(self, parent):
        """Cria seção de execução paralela"""
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
        
        # Container para o dropdown
        container_modo = ctk.CTkFrame(frame_paralela, fg_color="transparent")
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
        
        # Dropdown com opções de execução
        self.dropdown_modo = ctk.CTkOptionMenu(
            frame_modo,
            values=["Individual", "Paralelo (2 instâncias)", "Paralelo (3 instâncias)", "Paralelo (4 instâncias)", "Paralelo (5 instâncias)"],
            variable=self.modo_var,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=12),
            command=self._on_modo_change,
            width=200,
            height=40
        )
        self.dropdown_modo.pack()
        
        # Label de info sobre execução paralela
        self.label_info_paralela = ctk.CTkLabel(
            frame_paralela,
            text="Modo Individual: Processa sequencialmente",
            font=ctk.CTkFont(size=12),
            text_color="#6c757d"
        )
        self.label_info_paralela.pack(pady=(5, 15))
    
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
        
        # Botão Executar
        self.botao_executar = ButtonFactory.create_execute_button(
            container_botoes,
            command=self._executar_scraper,
            width=280
        )
        self.botao_executar.pack(side="left", padx=10)
        
        # Botão Abrir Pasta
        self.botao_abrir_pasta = ButtonFactory.create_folder_button(
            container_botoes,
            command=self._abrir_pasta_betha,
            width=160
        )
        self.botao_abrir_pasta.pack(side="left", padx=10)
    
    def _obter_opcoes_cidades(self):
        """Retorna lista de opções para o dropdown de cidades"""
        opcoes = ["Todas as Cidades"]
        if self.lista_cidades_betha:
            nomes_cidades = [cidade["nome"] for cidade in self.lista_cidades_betha]
            opcoes.extend(sorted(nomes_cidades))
        return opcoes

    def _on_ano_change(self, valor):
        """Callback quando ano é alterado (Unix)"""
        if valor == "Todos os Anos":
            self.label_status_anos.configure(
                text="Todos os anos selecionados (32 anos)"
            )
        else:
            self.label_status_anos.configure(
                text=f"Ano selecionado: {valor}"
            )
    
    def _on_cidade_change(self, valor):
        """Callback quando cidade é alterada (Unix)"""
        if valor == "Todas as Cidades":
            self.label_status_cidades.configure(
                text=f"Todas as cidades selecionadas ({len(self.lista_cidades_betha)} cidades)"
            )
        else:
            self.label_status_cidades.configure(
                text=f"Cidade selecionada: {valor}"
            )
    
    def _on_modo_change(self, valor):
        """Callback quando modo de execução é alterado"""
        if "Paralelo" in valor:
            instancias = valor.split("(")[1].split(" ")[0]
            self.label_info_paralela.configure(
                text=f"Modo Paralelo: {instancias} navegadores simultâneos"
            )
        else:
            self.label_info_paralela.configure(
                text="Modo Individual: Processa sequencialmente"
            )
    
    def _executar_scraper(self):
        """Executa o scraper ou cancela execução"""
        if self.executando:
            self._cancelar_execucao()
            return

        # Validar seleções
        if not self._validar_selecoes():
            return

        try:
            # Executar em thread separada
            self._executar_processo_thread()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar: {str(e)}")
            self._habilitar_interface(True)
    
    def _abrir_pasta_betha(self):
        """Abre a pasta de arquivos Betha"""
        try:
            # Caminho da pasta Betha
            pasta_betha = obter_caminho_dados("betha")
            
            # Cria a pasta se não existir
            if not os.path.exists(pasta_betha):
                os.makedirs(pasta_betha)
            
            # Abre no explorador do sistema
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(pasta_betha)
            elif sistema == "Darwin":
                subprocess.run(["open", pasta_betha])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", pasta_betha])
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir pasta: {str(e)}")
    
    def mostrar(self):
        """Mostra esta interface"""
        self.main_frame.pack(fill="both", expand=True)
    
    def ocultar(self):
        """Oculta esta interface"""
        self.main_frame.pack_forget()
    
    def _habilitar_interface(self, habilitado=True):
        """Habilita/desabilita elementos da interface"""
        self.executando = not habilitado

        # Atualiza controles de ano (todas as plataformas)
        if hasattr(self, 'dropdown_ano'):
            self.dropdown_ano.configure(state="normal" if habilitado else "disabled")

        # Atualiza controles de cidade (todas as plataformas)
        if hasattr(self, 'dropdown_cidade'):
            self.dropdown_cidade.configure(state="normal" if habilitado else "disabled")

        # Atualiza dropdown de modo
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
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=False)
            self.botao_executar.configure(state="normal")
        else:
            ButtonFactory.toggle_execute_cancel(self.botao_executar, is_executing=True)
            self.botao_executar.configure(state="normal")

    def _cancelar_execucao(self):
        """Cancela a execução em andamento"""
        try:
            self._cancelado = True

            # Cancela bot Betha principal se existir
            if self.bot_betha:
                if hasattr(self.bot_betha, 'cancelar'):
                    self.bot_betha.cancelar()
                else:
                    self.bot_betha.fechar_navegador()

            # Cancela todos os bots ativos (execução paralela)
            for bot in self.bots_ativos:
                try:
                    if hasattr(bot, 'cancelar'):
                        bot.cancelar()
                    else:
                        bot.fechar_navegador()
                except:
                    pass  # Ignorar erros ao cancelar bots
            self.bots_ativos.clear()

            # Cancela executor paralelo se existir
            if self.executor:
                # Tenta cancelar futures pendentes
                for future in self.futures:
                    future.cancel()
                # Shutdown sem esperar
                self.executor.shutdown(wait=False)
                self.executor = None
                self.futures = []

            self._habilitar_interface(True)
            messagebox.showinfo("Cancelado", "Processamento cancelado")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cancelar: {str(e)}")
            self._habilitar_interface(True)

    def cancelar_execucao(self):
        """Método público para cancelamento (mantido para compatibilidade)"""
        self._cancelar_execucao()
    
    def _validar_selecoes(self):
        """Valida as seleções do usuário"""
        # Validar anos (usando dropdown)
        ano_selecionado = self.ano_var.get()
        if ano_selecionado == "Todos os Anos":
            self.anos_selecionados = [str(ano) for ano in range(1998, datetime.now().year + 1)]
        else:
            self.anos_selecionados = [ano_selecionado]

        # Validar cidades (usando dropdown)
        cidade_selecionada = self.cidade_var.get()
        if cidade_selecionada == "Todas as Cidades":
            self.cidades_selecionadas = [cidade["nome"] for cidade in self.lista_cidades_betha]
        else:
            self.cidades_selecionadas = [cidade_selecionada]

        return True

    def _executar_processo_thread(self):
        """Wrapper para executar processo em thread"""
        # Desabilita interface e muda botão para cancelar
        self._habilitar_interface(False)
        self._cancelado = False
        self.executando = True

        # Executa em thread separada
        self.thread_execucao = threading.Thread(target=self._executar_processo, daemon=True)
        self.thread_execucao.start()

    def _executar_processo(self):
        """Executa o processo de scraping"""
        try:
            # Determinar modo de execução
            modo = self.modo_var.get()
            
            if "Paralelo" in modo:
                # Extrair número de instâncias
                num_instancias = int(modo.split("(")[1].split(" ")[0])
                self._executar_paralelo(num_instancias)
            else:
                self._executar_individual()
            
        except Exception as e:
            if not self._cancelado:
                print(f"Erro na execução: {e}")
                self.parent_container.after(0, lambda: messagebox.showerror("Erro", f"Erro durante execução: {str(e)}"))
        finally:
            self.parent_container.after(0, lambda: self._habilitar_interface(True))
            self.executando = False

    def _executar_individual(self):
        """Executa o scraping de forma individual (sequencial)"""
        print("\n" + "="*60)
        print("EXECUÇÃO INDIVIDUAL - BETHA")
        print("="*60)

        total_processamentos = len(self.cidades_selecionadas) * len(self.anos_selecionados)
        contador = 0

        for cidade_nome in self.cidades_selecionadas:
            # Verifica cancelamento
            if self._cancelado:
                print("\nProcessamento cancelado pelo usuário")
                break
            # Buscar configuração da cidade
            cidade_config = self._buscar_config_cidade(cidade_nome)
            if not cidade_config:
                print(f"⚠ Configuração não encontrada para {cidade_nome}")
                continue
            
            for ano in self.anos_selecionados:
                # Verifica cancelamento
                if self._cancelado:
                    print("\nProcessamento cancelado pelo usuário")
                    return

                contador += 1
                print(f"\n[{contador}/{total_processamentos}] Processando {cidade_nome} - Ano {ano}")

                try:
                    # Criar instância do bot com configurações específicas
                    self.bot_betha = BotBetha(cidade_config, int(ano))
                    
                    # Executar o processo completo
                    resultado = self.bot_betha.executar_completo()
                    
                    if resultado['sucesso']:
                        print(f"✓ {cidade_nome} - {ano} processado com sucesso")
                    else:
                        print(f"✗ Falha em {cidade_nome} - {ano}: {resultado['mensagem']}")
                    
                    # Fechar navegador após cada processamento
                    self.bot_betha.fechar_navegador()
                    
                except Exception as e:
                    print(f"✗ Erro ao processar {cidade_nome} - {ano}: {e}")
                
                # Pequena pausa entre processamentos
                if contador < total_processamentos:
                    time.sleep(2)
        
        print("\n" + "="*60)
        print("EXECUÇÃO CONCLUÍDA")
        print("="*60)

        # Mostrar mensagem de conclusão apenas se não foi cancelado
        if not self._cancelado:
            self.parent_container.after(0, lambda: messagebox.showinfo(
                "Concluído",
                f"Processamento concluído!\n\n"
                f"Total: {total_processamentos} combinações\n"
                f"Cidades: {len(self.cidades_selecionadas)}\n"
                f"Anos: {len(self.anos_selecionados)}"
            ))
    
    def _executar_paralelo(self, num_instancias):
        """Executa o scraping em paralelo com múltiplas instâncias"""
        print(f"\n" + "="*60)
        print(f"EXECUÇÃO PARALELA - {num_instancias} INSTÂNCIAS")
        print("="*60)

        # Preparar lista de tarefas
        tarefas = []
        for cidade_nome in self.cidades_selecionadas:
            # Verifica cancelamento
            if self._cancelado:
                print("\nProcessamento cancelado pelo usuário")
                return

            cidade_config = self._buscar_config_cidade(cidade_nome)
            if cidade_config:
                for ano in self.anos_selecionados:
                    tarefas.append((cidade_config, int(ano)))
        
        if not tarefas:
            messagebox.showwarning("Aviso", "Nenhuma tarefa para executar")
            return
        
        print(f"Total de tarefas: {len(tarefas)}")
        
        # Dividir tarefas entre as instâncias
        import concurrent.futures

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_instancias)
        self.futures = []

        try:
            # Submeter tarefas
            for cidade_config, ano in tarefas:
                if self._cancelado:
                    break
                future = self.executor.submit(self._executar_tarefa, cidade_config, ano)
                self.futures.append(future)

            # Aguardar conclusão (ou cancelamento)
            if not self._cancelado:
                concurrent.futures.wait(self.futures)
        finally:
            # Limpar executor
            if self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None
                self.futures = []
        
        print("\n" + "="*60)
        print("EXECUÇÃO PARALELA CONCLUÍDA")
        print("="*60)

        # Mostrar mensagem apenas se não foi cancelado
        if not self._cancelado:
            self.parent_container.after(0, lambda: messagebox.showinfo(
                "Concluído",
                f"Processamento paralelo concluído!\n\n"
                f"Total de tarefas: {len(tarefas)}\n"
                f"Instâncias utilizadas: {num_instancias}"
            ))
    
    def _executar_tarefa(self, cidade_config, ano):
        """Executa uma tarefa individual (para uso em paralelo)"""
        try:
            # Verifica cancelamento antes de iniciar
            if self._cancelado:
                return

            print(f"\n🔄 Iniciando: {cidade_config['nome']} - {ano}")

            bot = BotBetha(cidade_config, ano)

            # Adicionar à lista de bots ativos para possível cancelamento
            self.bots_ativos.append(bot)

            # Armazena referência para possível cancelamento
            # (em execução paralela, múltiplos bots podem estar ativos)
            resultado = bot.executar_completo()

            if self._cancelado:
                bot.fechar_navegador()
                return

            if resultado['sucesso']:
                print(f"✓ Concluído: {cidade_config['nome']} - {ano}")
            else:
                print(f"✗ Falha: {cidade_config['nome']} - {ano}")

            bot.fechar_navegador()

            # Remover da lista de bots ativos
            if bot in self.bots_ativos:
                self.bots_ativos.remove(bot)

        except Exception as e:
            if not self._cancelado:
                print(f"✗ Erro em {cidade_config['nome']} - {ano}: {e}")
            # Remover bot da lista em caso de erro
            if 'bot' in locals() and bot in self.bots_ativos:
                self.bots_ativos.remove(bot)
    
    def _buscar_config_cidade(self, nome_cidade):
        """Busca a configuração de uma cidade específica"""
        for cidade in self.lista_cidades_betha:
            if cidade["nome"] == nome_cidade:
                return cidade
        return None