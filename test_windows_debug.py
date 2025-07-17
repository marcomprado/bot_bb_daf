#!/usr/bin/env python3
"""
Teste específico para diagnosticar problema do Windows
Simula condições do Windows e testa subprocess GUI
"""

import sys
import os
import subprocess
import threading
import time
from datetime import datetime

def simular_subprocess_windows():
    """Simula o subprocess usado pela GUI no Windows"""
    print("=" * 60)
    print("🔬 DIAGNÓSTICO ESPECÍFICO WINDOWS")
    print("=" * 60)
    
    print(f"📁 Diretório atual: {os.getcwd()}")
    print(f"📁 Python executável: {sys.executable}")
    print(f"📁 Plataforma: {sys.platform}")
    
    # Verifica arquivos necessários
    print("\n📋 VERIFICANDO ARQUIVOS:")
    arquivos_necessarios = ['main.py', 'listed_cities.txt', 'cidades.txt']
    
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo} - ENCONTRADO")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
            if arquivo == 'listed_cities.txt':
                print("   Criando arquivo temporário para teste...")
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write("ouro branco\n")
                print(f"✅ {arquivo} - CRIADO")
    
    print("\n🔄 TESTANDO SUBPROCESS COMO NA GUI:")
    
    # Teste 1: Subprocess Popen (como na GUI)
    print("\nTeste 1: subprocess.Popen (método da GUI)")
    try:
        processo = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        print(f"🚀 Processo iniciado (PID: {processo.pid})")
        print("⏳ Aguardando 5 segundos...")
        
        # Aguarda 5 segundos
        time.sleep(5)
        
        # Verifica status
        if processo.poll() is None:
            print("✅ Processo ainda executando (normal)")
            processo.terminate()
            stdout, stderr = processo.communicate()
            print(f"📝 Processo terminado voluntariamente")
        else:
            print(f"❌ Processo já terminou (código: {processo.returncode})")
            stdout, stderr = processo.communicate()
            print("📝 STDOUT:")
            print(stdout[:500] if stdout else "   (vazio)")
            print("📝 STDERR:")
            print(stderr[:500] if stderr else "   (vazio)")
        
    except Exception as e:
        print(f"❌ Erro no subprocess: {e}")
    
    # Teste 2: Verificação de dependências
    print("\n🔍 VERIFICANDO DEPENDÊNCIAS:")
    dependencias = ['selenium', 'webdriver_manager', 'pandas', 'bs4', 'openpyxl']
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NÃO INSTALADO")
    
    # Teste 3: Execução direta do main.py
    print("\n🎯 TESTE EXECUÇÃO DIRETA:")
    try:
        resultado = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            timeout=10  # Timeout de 10 segundos
        )
        
        print(f"📊 Código de retorno: {resultado.returncode}")
        if resultado.stdout:
            print("📝 STDOUT (primeiros 300 chars):")
            print(resultado.stdout[:300])
        if resultado.stderr:
            print("📝 STDERR (primeiros 300 chars):")
            print(resultado.stderr[:300])
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - processo executou por mais de 10s (normal)")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")

def simular_thread_gui():
    """Simula exatamente como a GUI executa o subprocess"""
    print("\n" + "=" * 60)
    print("🎨 SIMULAÇÃO EXATA DA GUI")
    print("=" * 60)
    
    processo = None
    cancelado = False
    
    def executar_subprocess():
        nonlocal processo
        try:
            print("🚀 Iniciando subprocess como na GUI...")
            processo = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            print(f"📋 Processo criado (PID: {processo.pid})")
            
            # Aguarda processo terminar (como na GUI)
            stdout, stderr = processo.communicate()
            
            print(f"🏁 Processo terminou (código: {processo.returncode})")
            
            if not cancelado:
                print("📨 Finalizando execução...")
                print("✅ SERIA MOSTRADO: 'processo foi terminado'")
            
        except Exception as e:
            print(f"❌ Erro na thread: {e}")
            if not cancelado:
                print("📨 Finalizando com erro...")
                print("✅ SERIA MOSTRADO: 'processo foi terminado'")
    
    # Executa em thread separada (como na GUI)
    print("🔄 Iniciando thread...")
    thread = threading.Thread(target=executar_subprocess, daemon=True)
    thread.start()
    
    # Aguarda um pouco e mostra status
    for i in range(10):
        time.sleep(1)
        print(f"⏳ Segundo {i+1}/10 - Thread ativa: {thread.is_alive()}")
        
        if not thread.is_alive():
            print("🏁 Thread terminou")
            break
    
    if thread.is_alive():
        print("⚠️ Thread ainda executando após 10s")
        if processo:
            print("🛑 Terminando processo...")
            processo.terminate()

def main():
    """Função principal do diagnóstico"""
    print(f"⏰ Diagnóstico iniciado: {datetime.now().strftime('%H:%M:%S')}")
    
    # Executa testes
    simular_subprocess_windows()
    simular_thread_gui()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    print("Se você vê este texto, o subprocess está funcionando.")
    print("O problema no Windows pode ser:")
    print("1. ❌ Dependências não instaladas")
    print("2. ❌ Chrome não encontrado") 
    print("3. ❌ Erro de codificação de arquivo")
    print("4. ❌ Permissões de arquivo")
    print("\n🔧 Execute este script no Windows para diagnosticar!")

if __name__ == "__main__":
    main() 