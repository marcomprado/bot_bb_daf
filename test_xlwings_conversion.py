#!/usr/bin/env python3
"""
Script de teste para conversão XLS -> XLSX usando xlwings
Testa a conversão dos arquivos já baixados na pasta raw
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.classes.file.file_converter import FileConverter

def main():
    print("="*60)
    print("TESTE DE CONVERSÃO XLS -> XLSX COM XLWINGS")
    print("="*60)

    # Instancia o conversor para Ribeirão das Neves
    print("\n1. Inicializando FileConverter...")
    converter = FileConverter("ribeirao_das_neves")

    # Verifica quantos arquivos existem na pasta raw
    import glob
    arquivos_xls = glob.glob(os.path.join(converter.raw_dir, "*.xls"))
    print(f"\n2. Arquivos XLS encontrados na pasta raw: {len(arquivos_xls)}")

    if arquivos_xls:
        print("\nArquivos a serem convertidos:")
        for i, arquivo in enumerate(arquivos_xls, 1):
            nome = os.path.basename(arquivo)
            tamanho = os.path.getsize(arquivo) / 1024  # KB
            print(f"   {i:2d}. {nome[:50]:<50} ({tamanho:.1f} KB)")

    # Executa a conversão
    print("\n3. Iniciando conversão com xlwings...")
    print("   (Excel será aberto em modo invisível para cada arquivo)")

    total, convertidos = converter.converter_todos_raw()

    # Mostra resultado
    print("\n" + "="*60)
    print("RESULTADO DA CONVERSÃO")
    print("="*60)
    print(f"Total de arquivos processados: {total}")
    print(f"Arquivos convertidos com sucesso: {convertidos}")

    if convertidos > 0:
        print(f"\n✅ Sucesso! Os arquivos XLSX estão em:")
        print(f"   {converter.converted_dir}")

        # Lista arquivos convertidos
        arquivos_xlsx = glob.glob(os.path.join(converter.converted_dir, "*.xlsx"))
        if arquivos_xlsx:
            print(f"\nArquivos convertidos ({len(arquivos_xlsx)}):")
            for arquivo in arquivos_xlsx:
                nome = os.path.basename(arquivo)
                tamanho = os.path.getsize(arquivo) / 1024  # KB
                print(f"   ✓ {nome[:50]:<50} ({tamanho:.1f} KB)")
    else:
        print("\n⚠️ Nenhum arquivo foi convertido")

    return convertidos

if __name__ == "__main__":
    try:
        convertidos = main()
        sys.exit(0 if convertidos > 0 else 1)
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)