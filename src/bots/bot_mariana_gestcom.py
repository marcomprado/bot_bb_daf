#!/usr/bin/env python3
# Bot de automacao do sistema Gestcom para Mariana
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.classes.chrome_driver import ChromeDriverSimples
from src.classes.methods.cancel_method import BotBase

env_path = Path(__file__).parent.parent / 'config' / '.env'
load_dotenv(env_path, encoding='utf-8-sig')


class BotMarianaGestcom(BotBase):

    def __init__(self, timeout=15):
        super().__init__()
        self.url = "https://mariana.sistemagestcom.com.br/#!/Entrar"
        self.timeout = timeout
        self._cancelado = False
        self._em_execucao = False
        self.usuario = os.getenv('MARIANA_GESTCOM_LOGIN', '')
        self.senha = os.getenv('MARIANA_GESTCOM_SENHA', '')

    def configurar_navegador(self) -> bool:
        try:
            opcoes = webdriver.ChromeOptions()
            opcoes.add_argument("--headless=new")
            opcoes.add_argument("--disable-gpu")
            opcoes.add_argument("--window-size=1920,1080")

            driver_simples = ChromeDriverSimples()
            self.navegador = driver_simples.conectar(chrome_options=opcoes)

            if self.navegador:
                self.wait = WebDriverWait(self.navegador, self.timeout)
                print("Navegador configurado com sucesso")
                return True
            return False
        except Exception as e:
            print(f"Erro ao configurar navegador: {e}")
            return False

    def fazer_login(self) -> bool:
        try:
            print("Navegando para pagina de login...")
            self.navegador.get(self.url)

            # aguarda campo de login carregar
            campo_login = self.wait.until(
                EC.presence_of_element_located((By.XPATH,
                    "/html/body/div[1]/div/div/ui-view/div/div/div/div/div/form/div/div[2]/input"))
            )
            campo_login.clear()
            campo_login.send_keys(self.usuario)

            campo_senha = self.navegador.find_element(By.XPATH,
                "/html/body/div[1]/div/div/ui-view/div/div/div/div/div/form/div/div[3]/input")
            campo_senha.clear()
            campo_senha.send_keys(self.senha)

            botao_entrar = self.navegador.find_element(By.XPATH,
                "/html/body/div[1]/div/div/ui-view/div/div/div/div/div/form/div/div[4]/button/span[1]")
            botao_entrar.click()

            time.sleep(2)
            print("Login realizado com sucesso")
            return True
        except TimeoutException:
            print("Timeout: pagina de login demorou para carregar")
            return False
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
            return False

    def limpar_recursos(self):
        try:
            if hasattr(self, 'navegador') and self.navegador:
                try:
                    for handle in self.navegador.window_handles:
                        self.navegador.switch_to.window(handle)
                        self.navegador.close()
                except:
                    pass
                self.navegador.quit()
                self.navegador = None
                self.wait = None
        except Exception:
            pass

    def fechar_navegador(self):
        self.limpar_recursos()
        print("Navegador fechado e recursos liberados")

    def __del__(self):
        self.limpar_recursos()

    def cancelar(self, forcado=False):
        self._em_execucao = False
        super().cancelar(forcado=forcado)
