"""
Arquivo de configuração centralizada para o sistema de web scraping
Contém todas as configurações e constantes utilizadas no projeto
"""

# Configurações do sistema
SISTEMA_CONFIG = {
    # URL do sistema de arrecadação federal
    'url_sistema': 'https://demonstrativos.apps.bb.com.br/arrecadacao-federal',
    
    # Timeout para aguardar elementos carregarem (em segundos)
    'timeout_selenium': 10,
    
    # Pausas entre ações (em segundos) - OTIMIZADO PARA MÁXIMA VELOCIDADE
    'pausa_entre_cidades': 0.3,        # Reduzido de 2s para 0.3s
    'pausa_apos_preenchimento': 0.1,   # Reduzido de 2s para 0.1s  
    'pausa_apos_clique': 0.3,          # Reduzido de 3s para 0.3s
    'pausa_entre_campos': 0.1,         # Reduzido de 1s para 0.1s
    'pausa_esc_calendario': 0.05,      # Reduzido de 0.5s para 0.05s
}

# Configurações de arquivos
ARQUIVOS_CONFIG = {
    # Nome do arquivo dinâmico que contém as cidades selecionadas
    'arquivo_cidades': 'listed_cities.txt',
    
    # Nome do arquivo estático de referência com todas as cidades
    'arquivo_cidades_estatico': 'cidades.txt',
    
    # Encoding para leitura de arquivos
    'encoding_arquivo': 'utf-8',
}

# Seletores CSS para elementos da página
SELETORES_CSS = {
    # Campo de nome do beneficiário (nome da cidade)
    'campo_beneficiario': '[formcontrolname="nomeBeneficiarioEntrada"]',
    
    # Botão seletor para escolher cidade específica por estado
    'botao_seletor_beneficiario': 'button[aria-label="Beneficiário"].selectButton',
    
    # Opções do dropdown de beneficiário com estado MG
    'opcao_cidade_mg': 'a[role="menuitem"][title*=" - MG "]',
    
    # Primeiro botão para continuar para página de datas
    'botao_continuar_inicial': '[aria-label="Continuar"]',
    
    # Segundo botão para continuar após preencher datas (botão de submit)
    'botao_continuar_datas': 'button[type="submit"][aria-label="Continuar"]',
    
    # Campos de data (inicial e final)
    'campos_data': 'input[placeholder="DD / MM / AAAA"]',
}

# Configurações de datas
DATAS_CONFIG = {
    # Formato de data usado no sistema
    'formato_data': '%d/%m/%Y',
    
    # Número de meses anteriores para data inicial
    'meses_anteriores': 1,
}

# Mensagens de log do sistema
MENSAGENS = {
    'inicio_processamento': ' SISTEMA DE AUTOMAÇÃO WEB - ARRECADAÇÃO FEDERAL',
    'fim_processamento': ' Processamento concluído!',
    'erro_critico': ' Erro crítico',
    'sucesso': 'success',
    'erro': 'error',
    'aviso': 'alert',
    'info': 'info',
} 