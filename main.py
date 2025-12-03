#!/usr/bin/env python3
"""
Sistema de Automação Web - Ponto de Entrada Principal
Coordena as interfaces gráficas e gerencia a execução do sistema
"""

import sys
import os
import threading
import platform
import tkinter as tk
import customtkinter as ctk
from typing import Dict, Optional

# Importa as GUIs
from src.view.gui1 import GUI1
from src.view.gui2 import GUI2
from src.view.gui3 import GUI3
from src.view.gui4 import GUI4
from src.view.gui5 import GUI5
from src.view.view_config import ConfigGUI

# Importa funções de gerenciamento de caminhos
from src.classes.file.path_manager import obter_caminho_dados, copiar_arquivo_cidades_se_necessario

# Importa gerenciador de configurações
from src.classes.config_page import ConfigManager

# Importa o bot principal e processador paralelo
from src.bots.bot_bbdaf import BotBBDAF
from src.classes.methods.parallel_processor import ProcessadorParalelo
from src.classes.data_extractor import DataExtractor

# Importa ButtonFactory para botões de aba
from src.view.modules.buttons import ButtonFactory

# Importa o sistema de execução automática
from src.classes.methods.auto_execution import get_automatic_executor


class SistemaFVN:
    """
    Sistema principal que coordena todas as interfaces e execução
    """
    
    def __init__(self):
        """Inicializa o sistema"""
        # Configuração do tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Copia arquivo cidades.txt se necessário (para executável)
        copiar_arquivo_cidades_se_necessario()

        # Carrega configurações de tamanho da janela
        self.config_manager = ConfigManager()

        # Define padrão baseado na plataforma
        if platform.system() == "Windows":
            default_geometry = {"width": 650, "height": 950}
        else:  # macOS e Linux
            default_geometry = {"width": 600, "height": 950}

        window_config = self.config_manager.get_config("window_geometry", default_geometry)

        # Janela principal
        self.janela = ctk.CTk()
        self.janela.title("Sistema FVN - Automação Web")
        self.janela.geometry(f"{window_config['width']}x{window_config['height']}")
        self.janela.resizable(True, True)
        self.janela.minsize(600, 600)
        self.janela.configure(fg_color="#f8f9fa")
        
        # Estado do sistema
        self.aba_atual = "bbdaf"
        self.sistema_var = ctk.StringVar()
        self.executando = False
        self.bot_atual = None
        self.thread_execucao = None
        self.processador_paralelo = None
        
        # Configura ícone
        self._configurar_icone()

        # Centraliza janela
        self._centralizar_janela()

        # Configura protocolo de fechamento
        self.janela.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        # Cria interface
        self._criar_interface()

        # Inicia sistema de execução automática se configurado
        self._iniciar_execucao_automatica()
    
    def _configurar_icone(self):
        """Configura o ícone da aplicação se disponível"""
        try:
            caminhos_icone = [
                obter_caminho_dados("assets/app_icon.ico"),
                obter_caminho_dados("assets/fvn_icon.ico"),
                obter_caminho_dados("assets/logo.ico"),
                obter_caminho_dados("app_icon.ico"),
                obter_caminho_dados("icon.ico")
            ]
            
            for caminho in caminhos_icone:
                if os.path.exists(caminho):
                    self.janela.iconbitmap(caminho)
                    print(f"Ícone carregado: {caminho}")
                    break
        except Exception as e:
            print(f"Aviso: Não foi possível carregar ícone - {e}")
    
    def _centralizar_janela(self):
        """Centraliza janela na tela"""
        self.janela.update_idletasks()
        largura = self.janela.winfo_width()
        altura = self.janela.winfo_height()
        screen_width = self.janela.winfo_screenwidth()
        screen_height = self.janela.winfo_screenheight()

        # Calculate center position
        pos_x = (screen_width // 2) - (largura // 2)
        pos_y = (screen_height // 2) - (altura // 2)

        # Ensure window stays within screen boundaries
        pos_x = max(0, min(pos_x, screen_width - largura))
        pos_y = max(0, min(pos_y, screen_height - altura))

        self.janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def _salvar_geometria(self):
        """Salva a geometria atual da janela nas configurações"""
        try:
            # Obtém tamanho atual da janela
            width = self.janela.winfo_width()
            height = self.janela.winfo_height()

            # Salva nas configurações
            self.config_manager.set_config("window_geometry", {"width": width, "height": height})
            self.config_manager.save_config_to_file()
            print(f"✓ Geometria salva: {width}x{height}")
        except Exception as e:
            print(f"⚠ Erro ao salvar geometria: {e}")

    def _ao_fechar(self):
        """Handler para quando a janela é fechada"""
        # Salva geometria atual
        self._salvar_geometria()

        # Cancela qualquer execução em andamento
        if self.executando:
            self._cancelar_execucao()

        # Fecha a janela
        self.janela.destroy()

    def _criar_interface(self):
        """Cria a interface principal com sistema de abas"""
        # Container principal
        container_principal = ctk.CTkFrame(
            self.janela,
            corner_radius=0,
            fg_color="#f8f9fa"
        )
        container_principal.pack(fill="both", expand=True)
        
        # Sistema de abas
        self._criar_sistema_abas(container_principal)
        
        # Container para o conteúdo das abas
        self.container_conteudo = ctk.CTkFrame(
            container_principal,
            corner_radius=0,
            fg_color="#f8f9fa"
        )
        self.container_conteudo.pack(fill="both", expand=True)
        
        # Cria GUI1 (BB DAF)
        self.gui1 = GUI1(
            parent_frame=self.container_conteudo,
            on_executar=self._executar_bbdaf,
            on_cancelar=self._cancelar_execucao
        )

        # Cria GUI2 (FNDE)
        self.gui2 = GUI2(self.container_conteudo)

        # Cria GUI3 (Betha)
        self.gui3 = GUI3(self.container_conteudo)

        # Cria GUI4 (Saldo FNS)
        self.gui4 = GUI4(self.container_conteudo)

        # Cria GUI5 (Resoluçoes PDF)
        self.gui5 = GUI5(self.container_conteudo)

        # Cria ConfigGUI (Configurações)
        self.config_gui = ConfigGUI(self.container_conteudo)

        # Mapeamento centralizado de abas para navegação eficiente
        self.mapa_abas = {
            "bbdaf": {"nome": "Sistema BB DAF", "gui": self.gui1},
            "fnde": {"nome": "Sistema FNDE", "gui": self.gui2},
            "betha": {"nome": "Sistema Betha", "gui": self.gui3},
            "consfns": {"nome": "Saldo FNS", "gui": self.gui4},
            "resolucoes": {"nome": "Resoluçoes PDF", "gui": self.gui5},
            "config": {"nome": None, "gui": self.config_gui}
        }
        self.todas_guis = [self.gui1, self.gui2, self.gui3, self.gui4, self.gui5, self.config_gui]
        self.gui_atual = None  # Rastreia GUI atualmente visível

        # Mostra aba inicial
        self._mostrar_aba("bbdaf")
    
    def _criar_sistema_abas(self, parent):
        """Cria o sistema de navegação com dropdown de sistemas"""
        # Container das abas
        container_abas = ctk.CTkFrame(
            parent,
            corner_radius=0,
            fg_color="#e9ecef",
            height=50
        )
        container_abas.pack(fill="x")
        container_abas.pack_propagate(False)

        # Dropdown de sistemas (esquerda)
        def on_sistema_change(valor):
            """Callback quando sistema é alterado no dropdown"""
            # Mapeia nome do sistema para identificador da aba
            mapa_sistemas = {
                "Sistema BB DAF": "bbdaf",
                "Sistema FNDE": "fnde",
                "Sistema Betha": "betha",
                "Saldo FNS": "consfns",
                "Resoluçoes PDF": "resolucoes"
            }
            aba = mapa_sistemas.get(valor)
            if aba:
                self._mostrar_aba(aba)

        self.dropdown_sistemas = ctk.CTkOptionMenu(
            container_abas,
            values=["Sistema BB DAF", "Sistema FNDE", "Sistema Betha", "Saldo FNS", "Resoluçoes PDF"],
            variable=self.sistema_var,
            command=on_sistema_change,
            font=ctk.CTkFont(size=14, weight="bold"),
            dropdown_font=ctk.CTkFont(size=13),
            width=200,
            height=36,
            fg_color="#0066cc",
            button_color="#0052a3",
            button_hover_color="#004080"
        )
        self.dropdown_sistemas.pack(side="left", padx=10, pady=7)

        # Frame fixo para botões de ícone (direita)
        frame_botoes_fixos = ctk.CTkFrame(
            container_abas,
            fg_color="transparent"
        )
        frame_botoes_fixos.pack(side="right", padx=(0, 10), pady=7)

        # Botão de ícone para configurações (fixo)
        self.botao_config = ButtonFactory.create_icon_config_button(
            frame_botoes_fixos,
            command=lambda: self._mostrar_aba("config")
        )
        self.botao_config.pack(side="left", padx=(5, 5))

        # Botão de ícone para abrir pasta (fixo)
        self.botao_pasta = ButtonFactory.create_icon_folder_button(
            frame_botoes_fixos,
            command=self._abrir_pasta_arquivos
        )
        self.botao_pasta.pack(side="left", padx=(5, 0))

        # Adiciona efeito hover aos botões de ícone
        ButtonFactory.add_icon_hover_effect(self.botao_pasta)
        ButtonFactory.add_icon_hover_effect(self.botao_config)
    
    def _mostrar_aba(self, aba: str):
        """
        Alterna entre as abas de forma eficiente
        """
        # Valida se a aba existe
        if aba not in self.mapa_abas:
            return

        self.aba_atual = aba
        config = self.mapa_abas[aba]

        # Atualiza dropdown se não for config (config mantém sistema selecionado)
        if config["nome"]:
            self.sistema_var.set(config["nome"])

        # Oculta apenas a GUI atualmente visível (otimização)
        if self.gui_atual and self.gui_atual != config["gui"]:
            self.gui_atual.ocultar()

        # Mostra a nova GUI
        config["gui"].mostrar()
        self.gui_atual = config["gui"]
    
    def _executar_bbdaf(self, parametros: Dict):
        """
        Executa o bot BB DAF com os parâmetros fornecidos
        
        Args:
            parametros: Dicionário com os parâmetros de execução
        """
        if self.executando:
            return
        
        self.executando = True
        
        # Salva cidades selecionadas
        self._salvar_cidades_selecionadas(parametros['cidades'])
        
        # Executa em thread separada
        self.thread_execucao = threading.Thread(
            target=self._executar_bot_thread,
            args=(parametros,),
            daemon=True
        )
        self.thread_execucao.start()
    
    def _executar_bot_thread(self, parametros: Dict):
        """
        Executa o bot em thread separada
        
        Args:
            parametros: Parâmetros de execução
        """
        try:
            modo = parametros.get('modo', 'individual')
            
            if modo == 'paralelo':
                # Execução paralela
                self.processador_paralelo = ProcessadorParalelo()
                resultado = self.processador_paralelo.executar_paralelo_threads(
                    num_instancias=parametros.get('num_instancias', 2),
                    data_inicial=parametros.get('data_inicial'),
                    data_final=parametros.get('data_final')
                )
            else:
                # Execução individual
                self.bot_atual = BotBBDAF()
                self.bot_atual.configurar_extrator_dados(DataExtractor("bbdaf"))
                
                resultado = self.bot_atual.executar_completo(
                    cidades=parametros.get('cidades'),
                    data_inicial=parametros.get('data_inicial'),
                    data_final=parametros.get('data_final')
                )
            
            # Processa resultado na thread principal
            self.janela.after(0, self._processar_resultado, resultado)
            
        except Exception as e:
            resultado = {'sucesso': False, 'erro': str(e)}
            self.janela.after(0, self._processar_resultado, resultado)
    
    def _processar_resultado(self, resultado: Dict):
        """
        Processa o resultado da execução
        
        Args:
            resultado: Resultado da execução
        """
        self.executando = False
        
        # Passa resultado para a GUI processar
        self.gui1.processar_resultado(resultado)
        
        # Limpa referências
        self.bot_atual = None
        self.processador_paralelo = None
    
    def _cancelar_execucao(self):
        """Cancela a execução em andamento"""
        if self.processador_paralelo:
            self.processador_paralelo.cancelar()
        
        if self.bot_atual:
            self.bot_atual.fechar_navegador()
        
        # Cancela execução da GUI3 se estiver rodando
        if hasattr(self, 'gui3') and self.gui3:
            self.gui3.cancelar_execucao()
        
        self.executando = False
    
    def _salvar_cidades_selecionadas(self, cidades: list):
        """
        Salva cidades selecionadas no arquivo
        
        Args:
            cidades: Lista de cidades selecionadas
        """
        try:
            caminho_arquivo = obter_caminho_dados("listed_cities.txt")
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                for cidade in cidades:
                    arquivo.write(f"{cidade}\n")
        except Exception as e:
            print(f"Erro ao salvar cidades: {e}")
    
    def _abrir_pasta_arquivos(self):
        """Abre a pasta arquivos_baixados no explorador do sistema"""
        import platform
        import subprocess
        
        try:
            # Caminho da pasta de arquivos
            pasta_arquivos = obter_caminho_dados("arquivos_baixados")
            
            # Cria a pasta se não existir
            if not os.path.exists(pasta_arquivos):
                os.makedirs(pasta_arquivos)
            
            # Abre no explorador do sistema
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(pasta_arquivos)
            elif sistema == "Darwin":  # macOS
                subprocess.run(["open", pasta_arquivos])
            elif sistema == "Linux":
                subprocess.run(["xdg-open", pasta_arquivos])
            else:
                print(f"Sistema operacional '{sistema}' não suportado")
                return
            
            print(f"Pasta de arquivos aberta: {pasta_arquivos}")
            
        except Exception as e:
            print(f"Erro ao abrir pasta de arquivos: {str(e)}")
    
    def _iniciar_execucao_automatica(self):
        """Inicia o sistema de execução automática se estiver configurado"""
        try:
            executor = get_automatic_executor()
            status = executor.get_status()

            if status.get('enabled', False):
                executor.start_monitoring()
                print("✓ Sistema de execução automática iniciado")

                next_exec = status.get('next_execution')
                if next_exec:
                    print(f"  Próxima execução: {next_exec}")
        except Exception as e:
            print(f"⚠ Não foi possível iniciar execução automática: {e}")

    def executar(self):
        """Executa o loop principal da aplicação"""
        self.janela.mainloop()


def verificar_dependencias():
    """
    Verifica se todas as dependências necessárias estão instaladas
    
    Returns:
        bool: True se todas as dependências estão instaladas
    """
    dependencias_necessarias = [
        'selenium',
        'customtkinter',
        'dateutil',
        'bs4',
        'pandas',
        'openpyxl'
    ]
    
    dependencias_ausentes = []
    
    for dep in dependencias_necessarias:
        try:
            __import__(dep)
        except ImportError:
            dependencias_ausentes.append(dep)
    
    if dependencias_ausentes:
        print("Dependências ausentes encontradas:")
        for dep in dependencias_ausentes:
            print(f"   - {dep}")
        print("\nInstale as dependências executando:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Função principal - ponto de entrada do sistema"""
    print("=" * 60)
    print("SISTEMA FVN - AUTOMAÇÃO WEB")
    print("=" * 60)
    
    # Verifica argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--cli":
            # Modo CLI direto
            print("Modo CLI ativado")
            from bots.bot_bbdaf import BotBBDAF
            from classes.data_extractor import DataExtractor
            
            bot = BotBBDAF()
            bot.configurar_extrator_dados(DataExtractor("bbdaf"))
            
            # Pega datas dos argumentos ou usa padrão
            data_inicial = sys.argv[2] if len(sys.argv) > 2 else None
            data_final = sys.argv[3] if len(sys.argv) > 3 else None
            
            resultado = bot.executar_completo(
                data_inicial=data_inicial,
                data_final=data_final
            )
            
            if resultado['sucesso']:
                print("\nProcessamento concluído com sucesso!")
                return 0
            else:
                print(f"\nErro: {resultado['erro']}")
                return 1
        
        elif sys.argv[1] == "--parallel":
            # Modo paralelo via CLI
            print("Modo paralelo via CLI")
            from src.classes.methods.parallel_processor import ProcessadorParalelo
            
            num_instancias = int(sys.argv[2]) if len(sys.argv) > 2 else 2
            processador = ProcessadorParalelo()
            
            resultado = processador.executar_paralelo_subprocess(num_instancias)
            
            if resultado['sucesso']:
                print("\nProcessamento paralelo concluído!")
                return 0
            else:
                print(f"\nErro: {resultado['erro']}")
                return 1
    
    # Verifica dependências
    print("Verificando dependências...")
    if not verificar_dependencias():
        return 1
    
    print("Todas as dependências estão instaladas.")
    print("Iniciando interface gráfica...")
    
    # Modo GUI (padrão)
    try:
        sistema = SistemaFVN()
        sistema.executar()
        return 0
    except Exception as e:
        print(f"Erro ao inicializar sistema: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())