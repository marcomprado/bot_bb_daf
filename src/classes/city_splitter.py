"""
Classe responsável por dividir as cidades em lotes para execução paralela
"""

import os
import sys
import platform
import math
from typing import List, Tuple


def obter_caminho_dados(nome_arquivo):
    """
    Obtém o caminho correto para arquivos de dados (que precisam ser modificáveis)
    
    Args:
        nome_arquivo (str): Nome do arquivo de dados
        
    Returns:
        str: Caminho completo para o arquivo de dados
    """
    try:
        # Se estamos em um executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # Para arquivos de dados modificáveis, usa o diretório do usuário
            if platform.system() == "Darwin":  # macOS
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            elif platform.system() == "Windows":
                user_data_dir = os.path.expanduser("~/Documents/Sistema_FVN")
            else:  # Linux
                user_data_dir = os.path.expanduser("~/.sistema_fvn")
            
            # Cria o diretório se não existir
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)
                
            return os.path.join(user_data_dir, nome_arquivo)
        else:
            # No desenvolvimento, usa o diretório atual
            return nome_arquivo
    except Exception:
        # Fallback para caminho relativo
        return nome_arquivo


class CitySplitter:
    """
    Classe responsável por dividir lista de cidades em lotes para execução paralela
    
    Funcionalidades:
    - Dividir cidades em N instâncias sem sobreposição
    - Gerar arquivos de configuração para cada instância  
    - Validar e balancear a distribuição
    """
    
    def __init__(self, arquivo_cidades="cidades.txt"):
        """
        Inicializa o divisor de cidades
        
        Args:
            arquivo_cidades (str): Caminho para arquivo com lista completa de cidades
        """
        # Se não foi passado caminho absoluto, usa função para obter caminho
        if not os.path.isabs(arquivo_cidades):
            self.arquivo_cidades = obter_caminho_dados(arquivo_cidades)
        else:
            self.arquivo_cidades = arquivo_cidades
        self.lista_cidades = []
        self._carregar_cidades()
    
    def _carregar_cidades(self):
        """
        Carrega lista completa de cidades do arquivo
        
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        try:
            if os.path.exists(self.arquivo_cidades):
                with open(self.arquivo_cidades, "r", encoding="utf-8") as arquivo:
                    self.lista_cidades = [linha.strip() for linha in arquivo if linha.strip()]
                return True
            else:
                return False
        except Exception:
            return False
    
    def obter_total_cidades(self):
        """
        Retorna o número total de cidades disponíveis
        
        Returns:
            int: Número total de cidades
        """
        return len(self.lista_cidades)
    
    def calcular_distribuicao(self, num_instancias):
        """
        Calcula como as cidades serão distribuídas entre as instâncias
        
        Args:
            num_instancias (int): Número de instâncias desejadas
        
        Returns:
            dict: Informações sobre a distribuição
        """
        total_cidades = len(self.lista_cidades)
        
        if num_instancias <= 0 or num_instancias > total_cidades:
            return {
                'valido': False,
                'erro': f'Número de instâncias deve ser entre 1 e {total_cidades}'
            }
        
        # Calcula cidades por instância
        cidades_por_instancia = math.ceil(total_cidades / num_instancias)
        cidades_restantes = total_cidades % num_instancias
        
        # Distribui as cidades
        distribuicao = []
        inicio = 0
        
        for i in range(num_instancias):
            # Última instância pode ter menos cidades
            if i == num_instancias - 1:
                fim = total_cidades
            else:
                fim = inicio + cidades_por_instancia
                # Ajusta se passar do total
                if fim > total_cidades:
                    fim = total_cidades
            
            tamanho_lote = fim - inicio
            if tamanho_lote > 0:
                distribuicao.append({
                    'instancia': i + 1,
                    'inicio': inicio,
                    'fim': fim,
                    'quantidade': tamanho_lote
                })
            
            inicio = fim
        
        return {
            'valido': True,
            'total_cidades': total_cidades,
            'num_instancias': len(distribuicao),
            'distribuicao': distribuicao
        }
    
    def dividir_cidades(self, num_instancias):
        """
        Divide as cidades em lotes e cria arquivos para cada instância
        
        Args:
            num_instancias (int): Número de instâncias
        
        Returns:
            dict: Resultado da operação
        """
        distribuicao = self.calcular_distribuicao(num_instancias)
        
        if not distribuicao['valido']:
            return distribuicao
        
        try:
            # Remove arquivos anteriores se existirem
            self._limpar_arquivos_instancias()
            
            arquivos_criados = []
            
            for lote in distribuicao['distribuicao']:
                # Extrai cidades para esta instância
                inicio = lote['inicio']
                fim = lote['fim']
                cidades_instancia = self.lista_cidades[inicio:fim]
                
                # Cria arquivo para esta instância - usa caminho de dados
                nome_arquivo = f"listed_cities_instancia_{lote['instancia']}.txt"
                caminho_arquivo = obter_caminho_dados(nome_arquivo)
                
                with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                    for cidade in cidades_instancia:
                        arquivo.write(f"{cidade}\n")
                
                arquivos_criados.append({
                    'arquivo': caminho_arquivo,
                    'instancia': lote['instancia'],
                    'cidades': cidades_instancia,
                    'quantidade': len(cidades_instancia)
                })
            
            return {
                'sucesso': True,
                'arquivos_criados': arquivos_criados,
                'distribuicao': distribuicao
            }
            
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao criar arquivos: {str(e)}'
            }
    
    def _limpar_arquivos_instancias(self):
        """
        Remove arquivos de instâncias anteriores se existirem
        """
        try:
            # Padrão dos arquivos de instância
            import glob
            
            # Procura arquivos no diretório de dados
            diretorio_dados = os.path.dirname(obter_caminho_dados("dummy"))
            if hasattr(sys, '_MEIPASS'):
                # No executável, usa o diretório de dados do usuário
                padrao = os.path.join(diretorio_dados, "listed_cities_instancia_*.txt")
            else:
                # No desenvolvimento, usa diretório atual
                padrao = "listed_cities_instancia_*.txt"
            
            arquivos = glob.glob(padrao)
            for arquivo in arquivos:
                try:
                    os.remove(arquivo)
                except:
                    pass
        except Exception:
            pass
    
    def obter_resumo_distribuicao(self, num_instancias):
        """
        Gera resumo textual da distribuição para exibir na interface
        
        Args:
            num_instancias (int): Número de instâncias
        
        Returns:
            str: Texto descritivo da distribuição
        """
        distribuicao = self.calcular_distribuicao(num_instancias)
        
        if not distribuicao['valido']:
            return distribuicao['erro']
        
        total = distribuicao['total_cidades']
        linhas = [f"Total de cidades: {total}"]
        linhas.append(f"Divididas em {num_instancias} instancias:")
        
        for lote in distribuicao['distribuicao']:
            linhas.append(f"  Instancia {lote['instancia']}: {lote['quantidade']} cidades")
        
        return "\n".join(linhas)
    
    def validar_instancias(self, num_instancias):
        """
        Valida se o número de instâncias é viável
        
        Args:
            num_instancias (int): Número de instâncias
        
        Returns:
            tuple: (é_valido, mensagem)
        """
        if num_instancias < 1:
            return False, "Número mínimo é 1 instância"
        
        if num_instancias > 20:
            return False, "Número máximo é 20 instâncias"
        
        total_cidades = len(self.lista_cidades)
        if num_instancias > total_cidades:
            return False, f"Não é possível criar mais instâncias que cidades ({total_cidades})"
        
        return True, "Configuração válida" 