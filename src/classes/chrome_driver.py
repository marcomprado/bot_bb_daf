"""
Classe simples para conexão direta com ChromeDriver
Remove a complexidade do webdriver-manager e conecta direto ao Chrome
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import subprocess
import time
import os


class ChromeDriverSimples:
    """
    Classe para conectar direto ao ChromeDriver sem webdriver-manager
    """
    
    def __init__(self, download_dir=None):
        self.navegador = None
        self.download_dir = download_dir
    
    def conectar(self):
        """
        Conecta direto ao Chrome sem webdriver-manager
        
        Returns:
            webdriver.Chrome: Instância do navegador Chrome ou None se falhou
        """
        try:
            # Configurações básicas do Chrome
            opcoes = webdriver.ChromeOptions()
            opcoes.add_argument("--no-sandbox")
            opcoes.add_argument("--disable-dev-shm-usage")
            opcoes.add_argument("--disable-blink-features=AutomationControlled")
            opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])
            opcoes.add_experimental_option('useAutomationExtension', False)
            
            # Configurar diretório de download se especificado
            if self.download_dir:
                prefs = {
                    "download.default_directory": self.download_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True,
                    "plugins.always_open_pdf_externally": True
                }
                opcoes.add_experimental_option("prefs", prefs)
            
            # Tenta conectar direto ao Chrome (usa ChromeDriver do sistema)
            self.navegador = webdriver.Chrome(options=opcoes)
            
            # Remove indicadores de automação
            self.navegador.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✓ ChromeDriver conectado com sucesso")
            return self.navegador
            
        except WebDriverException as e:
            print(f"✗ Erro ao conectar ChromeDriver: {e}")
            return None
        except Exception as e:
            print(f"✗ Erro inesperado: {e}")
            return None
    
    def fechar(self):
        """Fecha o navegador"""
        try:
            if self.navegador:
                self.navegador.quit()
                self.navegador = None
                print("✓ Navegador fechado")
        except Exception as e:
            print(f"Aviso: Erro ao fechar navegador - {e}")


# Função de teste
def teste_conexao():
    """Testa a conexão com ChromeDriver"""
    driver = ChromeDriverSimples()
    
    navegador = driver.conectar()
    if navegador:
        print("Teste de conexão bem-sucedido!")
        navegador.get("https://www.google.com")
        print(f"Título da página: {navegador.title}")
        driver.fechar()
        return True
    else:
        print("Falha no teste de conexão")
        return False


if __name__ == "__main__":
    teste_conexao()