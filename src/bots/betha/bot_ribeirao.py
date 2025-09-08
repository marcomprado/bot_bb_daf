#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Ribeirao das Neves - Script especifico para o municipio de Ribeirao das Neves
Contem a logica especifica apos navegar para Relatorios Favoritos
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime


def executar_script_ribeirao(navegador, wait):
    """
    Executa o script especifico para Ribeirao das Neves
    
    Este script e executado apos chegar em "Relatorios Favoritos"
    e contem a logica especifica para este municipio
    
    Args:
        navegador: Instancia do WebDriver
        wait: Instancia do WebDriverWait
        
    Returns:
        bool: True se executado com sucesso
    """
    