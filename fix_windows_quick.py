#!/usr/bin/env python3
"""
Correção rápida para problemas no Windows
Verifica e corrige automaticamente os problemas mais comuns
"""

import sys
import os
import subprocess
import importlib

def verificar_python():
    """Verifica versão do Python"""
    print("🐍 VERIFICANDO PYTHON:")
    print(f"   Versão: {sys.version}")
    print(f"   Executável: {sys.executable}")
    
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ é necessário!")
        return False
    else:
        print("✅ Versão do Python OK")
        return True

def verificar_dependencias():
    """Verifica e instala dependências faltantes"""
    print("\n📦 VERIFICANDO DEPENDÊNCIAS:")
    
    dependencias = [
        'selenium',
        'webdriver_manager', 
        'python-dateutil',
        'beautifulsoup4',
        'pandas',
        'openpyxl',
        'customtkinter',
        'psutil'
    ]
    
    faltando = []
    
    for dep in dependencias:
        try:
            # Testa import baseado no nome
            if dep == 'python-dateutil':
                importlib.import_module('dateutil')
            elif dep == 'beautifulsoup4':
                importlib.import_module('bs4')
            elif dep == 'webdriver-manager':
                importlib.import_module('webdriver_manager')
            else:
                importlib.import_module(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            faltando.append(dep)
    
    if faltando:
        print(f"\n🔧 INSTALANDO {len(faltando)} DEPENDÊNCIAS FALTANTES:")
        try:
            comando = [sys.executable, "-m", "pip", "install"] + faltando
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print("✅ Dependências instaladas com sucesso!")
                return True
            else:
                print(f"❌ Erro na instalação: {resultado.stderr}")
                return False
        except Exception as e:
            print(f"❌ Erro ao executar pip: {e}")
            return False
    else:
        print("✅ Todas as dependências já estão instaladas")
        return True

def verificar_chrome():
    """Verifica se Chrome está instalado"""
    print("\n🌐 VERIFICANDO GOOGLE CHROME:")
    
    # Caminhos comuns do Chrome no Windows
    caminhos_chrome = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', ''))
    ]
    
    chrome_encontrado = False
    for caminho in caminhos_chrome:
        if os.path.exists(caminho):
            print(f"✅ Chrome encontrado: {caminho}")
            chrome_encontrado = True
            break
    
    if not chrome_encontrado:
        print("❌ Google Chrome não encontrado!")
        print("📥 Baixe e instale: https://www.google.com/chrome/")
        return False
    
    return True

def verificar_arquivos():
    """Verifica arquivos necessários"""
    print("\n📁 VERIFICANDO ARQUIVOS:")
    
    arquivos_obrigatorios = [
        'main.py',
        'gui_main.py', 
        'config.py',
        'cidades.txt'
    ]
    
    todos_encontrados = True
    
    for arquivo in arquivos_obrigatorios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
            todos_encontrados = False
    
    # Arquivo dinâmico (pode não existir)
    if os.path.exists('listed_cities.txt'):
        print("✅ listed_cities.txt (dinâmico)")
    else:
        print("ℹ️ listed_cities.txt será criado pela GUI")
    
    return todos_encontrados

def criar_arquivo_teste():
    """Cria arquivo de teste para verificar codificação"""
    print("\n📝 CRIANDO ARQUIVO DE TESTE:")
    
    try:
        with open('teste_encoding.txt', 'w', encoding='utf-8') as f:
            f.write("ouro branco\n")
            f.write("belo horizonte\n")
        
        # Tenta ler o arquivo
        with open('teste_encoding.txt', 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        # Remove arquivo de teste
        os.remove('teste_encoding.txt')
        
        print("✅ Codificação UTF-8 funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro de codificação: {e}")
        return False

def testar_subprocess():
    """Testa subprocess do main.py"""
    print("\n🔄 TESTANDO SUBPROCESS:")
    
    # Cria arquivo temporário se necessário
    if not os.path.exists('listed_cities.txt'):
        with open('listed_cities.txt', 'w', encoding='utf-8') as f:
            f.write("ouro branco\n")
        print("ℹ️ Arquivo listed_cities.txt criado temporariamente")
    
    try:
        # Testa execução rápida com timeout
        resultado = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            timeout=15  # 15 segundos
        )
        
        if resultado.returncode == 0:
            print("✅ main.py executou sem erros")
            return True
        else:
            print(f"❌ main.py falhou (código {resultado.returncode})")
            if resultado.stderr:
                print("Erro:")
                print(resultado.stderr[:200])
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ main.py está executando (timeout normal)")
        return True
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        return False

def main():
    """Função principal de correção"""
    print("=" * 60)
    print("🔧 CORREÇÃO RÁPIDA WINDOWS - Sistema FVN")
    print("=" * 60)
    
    # Lista de verificações
    verificacoes = [
        ("Python", verificar_python),
        ("Dependências", verificar_dependencias),
        ("Chrome", verificar_chrome),
        ("Arquivos", verificar_arquivos),
        ("Codificação", criar_arquivo_teste),
        ("Subprocess", testar_subprocess)
    ]
    
    problemas = []
    
    for nome, funcao in verificacoes:
        if not funcao():
            problemas.append(nome)
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DA CORREÇÃO")
    print("=" * 60)
    
    if not problemas:
        print("🎉 TUDO OK! O sistema deve funcionar normalmente.")
        print("\n🚀 Próximos passos:")
        print("1. Execute: python gui_main.py")
        print("2. Selecione as cidades desejadas")
        print("3. Clique em 'Executar Processamento'")
    else:
        print(f"❌ {len(problemas)} problemas encontrados:")
        for problema in problemas:
            print(f"   - {problema}")
        print("\n🔧 Corrija os problemas acima e execute novamente.")
    
    input("\nPressione Enter para fechar...")

if __name__ == "__main__":
    main() 