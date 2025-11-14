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
    
    def conectar(self, chrome_options=None):
        """
        Conecta direto ao Chrome sem webdriver-manager

        Args:
            chrome_options: Opções personalizadas do Chrome (opcional)

        Returns:
            webdriver.Chrome: Instância do navegador Chrome ou None se falhou
        """
        try:
            # Usa opções personalizadas se fornecidas, senão cria padrão
            if chrome_options:
                opcoes = chrome_options
            else:
                opcoes = webdriver.ChromeOptions()

            # Configurações básicas do Chrome
            opcoes.add_argument("--no-sandbox")
            opcoes.add_argument("--disable-dev-shm-usage")
            opcoes.add_argument("--disable-blink-features=AutomationControlled")
            opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])
            opcoes.add_experimental_option('useAutomationExtension', False)
            
            # Configurar diretório de download se especificado
            if self.download_dir:
                # Garantir que o caminho seja absoluto - Chrome requer isso
                abs_download_dir = os.path.abspath(self.download_dir)

                # Criar diretório se não existir (GARANTIA DE EXISTÊNCIA)
                if not os.path.exists(abs_download_dir):
                    os.makedirs(abs_download_dir, exist_ok=True)
                    print(f"  ✓ Diretório de download criado: {abs_download_dir}")
                else:
                    print(f"  ✓ Diretório de download (absoluto): {abs_download_dir}")

                prefs = {
                    "download.default_directory": abs_download_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": False,  # Desabilita verificação de segurança
                    "safebrowsing.disable_download_protection": True,  # Desabilita proteção de download
                    "plugins.always_open_pdf_externally": True,
                    # Chrome 87+ requer este formato atualizado para downloads automáticos
                    "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
                    # Preferência adicional para macOS 14+ e Windows
                    "savefile.default_directory": abs_download_dir,
                    # Desabilita popups e permite downloads automáticos
                    "profile.default_content_settings.popups": 0,  # Desabilita popup de download
                    "profile.default_content_setting_values.automatic_downloads": 1  # Permite downloads automáticos
                }
                opcoes.add_experimental_option("prefs", prefs)
            
            # Tenta conectar direto ao Chrome (usa ChromeDriver do sistema)
            self.navegador = webdriver.Chrome(options=opcoes)

            # Habilitar downloads via CDP - necessário para Chrome 87+
            # Chrome moderno requer permissão explícita via DevTools Protocol
            if self.download_dir:
                try:
                    self.navegador.execute_cdp_cmd("Browser.setDownloadBehavior", {
                        "behavior": "allow",
                        "downloadPath": abs_download_dir
                    })
                    print("  ✓ Downloads habilitados via CDP (Browser.setDownloadBehavior)")
                except Exception as e:
                    print(f"  ⚠ Aviso: Não foi possível configurar CDP download behavior: {e}")

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