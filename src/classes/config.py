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

# Configurações do sistema FNDE
FNDE_CONFIG = {
    # URL base do sistema FNDE
    'url_base': 'https://www.fnde.gov.br/pls/simad/internet_fnde.LIBERACOES_01_PC',

    # Parâmetros padrão
    'uf_padrao': 'MG',
    'entidade_padrao': '02',  # PREFEITURA
    'programa_padrao': '',    # Vazio para todos os programas

    # Timeout para elementos FNDE (em segundos)
    'timeout_selenium': 1,

    # Pausas específicas para FNDE (em segundos)
    'pausa_entre_municipios': 0.5,
    'pausa_apos_selecao': 0.3,
    'pausa_apos_busca': 1.0,

    # Diretórios específicos
    'diretorio_saida': 'arquivos_baixados/fnde',
    'prefixo_arquivo': 'fnde',

    # Anos disponíveis no sistema FNDE
    'anos_disponiveis': list(range(2025, 1999, -1)),  # 2025 até 2000
}

# Configurações do sistema Consulta FNS
CONSFNS_CONFIG = {
    # URL base do sistema Consulta FNS
    'url_base': 'https://consultafns.saude.gov.br/#/conta-bancaria',

    # Parâmetros padrão
    'uf_padrao': 'MINAS GERAIS',
    'uf_value': '12',  # Valor do option para Minas Gerais

    # Timeout para elementos (em segundos)
    'timeout_selenium': 1,
    'timeout_carregamento_minimo': 1,   # Tempo mínimo de aguardo
    'timeout_carregamento_maximo': 30,  # Tempo máximo de aguardo (2 minutos)

    # Pausas específicas para ConsFNS (em segundos) - OTIMIZADO PARA VELOCIDADE
    'pausa_entre_municipios': 0.2,
    'pausa_apos_selecao_estado': 0.0,  # Removido - WebDriverWait já espera dropdown carregar
    'pausa_apos_selecao_municipio': 0.0,  # Removido - verificação de esfera já espera
    'pausa_apos_selecao_esfera': 1,  # Reduzido de 0.3s para 0.1s
    'pausa_apos_consulta': 0.0,  # Removido - WebDriverWait já espera botão ficar disponível
    'pausa_antes_download': 0.3,  # Reduzido de 1.0s para 0.3s

    # Diretórios específicos
    'diretorio_saida': 'consfns',  # Será usado com obter_caminho_dados()
    'prefixo_arquivo': 'CONSFNS',
}

# Seletores para elementos FNDE
SELETORES_FNDE = {
    # Formulário principal
    'select_ano': 'select[name="p_ano"]',
    'select_municipio': 'select[name="p_municipio"]',
    'select_entidade': 'select[name="p_tp_entidade"]',
    'botao_buscar': 'input[name="buscar"]',

    # Elementos de resultado
    'tabela_resultados': 'table',
    'linhas_tabela': 'table tr',
    'celulas_tabela': 'table td',

    # Indicadores de carregamento
    'corpo_pagina': 'body',
    'conteudo_principal': 'table, .tabela, .resultado',
}

# Seletores para elementos Consulta FNS
SELETORES_CONSFNS = {
    # Formulário principal
    'select_estado': 'select[name="estado"]',
    'select_municipio': 'select[name="municipio"]',
    'select_esfera': 'select[name="esfera"]',  # Campo condicional (aparece para algumas cidades)
    'botao_consultar': 'button[ng-click="contaBancariaCtrl.pesquisar()"]',
    'botao_gerar_planilha': 'button[ng-click="contaBancariaCtrl.gerarPlanilha()"]',

    # Indicadores de carregamento e resultados
    'corpo_pagina': 'body',
    'conteudo_resultados': '.ng-scope, table, .resultado',
    'loading_indicator': '.loading, .carregando, .spinner',
}

# Lista completa de municípios de MG (853 municípios)
# Esta lista é carregada dinamicamente do arquivo cidades.txt
# mas pode ser usada como fallback
MUNICIPIOS_MG_FALLBACK = [
    'BELO HORIZONTE',
    'UBERLANDIA', 
    'CONTAGEM',
    'JUIZ DE FORA',
    'BETIM',
    'MONTES CLAROS',
    'RIBEIRAO DAS NEVES',
    'UBERABA',
    'GOVERNADOR VALADARES',
    'IPATINGA',
    'SANTA LUZIA',
    'SETE LAGOAS',
    'DIVINOPOLIS',
    'IBIRITE',
    'POCOS DE CALDAS',
    'PATOS DE MINAS',
    'POUSO ALEGRE',
    'TEOFILO OTONI',
    'BARBACENA',
    'SABARA',
    'VARGINHA',
    'CONSELHEIRO LAFAIETE',
    'VESPASIANO',
    'ITABIRA',
    'ARAGUARI',
    'PASSOS',
    'UBERLANDIA',
    'CORONEL FABRICIANO',
    'MURIAE',
    'ITUIUTABA',
    'ARAXAS',
    'LAVRAS',
    'ITAJUBA',
    'CAMPOS ALTOS',
    'TRES CORACOES',
    'NOVA LIMA',
    'NOVA SERRANA',
    'SAO JOAO DEL REI',
    'TIMOTEO',
    'PARA DE MINAS',
    'VICOSA',
    'MANHUACU',
    'ITAUNA',
    'PATROCINIO',
    'POUSO ALEGRE',
    'UNAI',
    'CARATINGA',
    'GUAXUPE',
    'NOVA ERA',
    'DIAMANTINA',
]

# Mensagens de log do sistema
MENSAGENS = {
    'inicio_processamento': ' SISTEMA DE AUTOMAÇÃO WEB - ARRECADAÇÃO FEDERAL',
    'fim_processamento': ' Processamento concluído!',
    'erro_critico': ' Erro crítico',
    'sucesso': 'success',
    'erro': 'error',
    'aviso': 'alert',
    'info': 'info',

    # Mensagens específicas FNDE
    'inicio_fnde': ' SISTEMA DE AUTOMAÇÃO WEB - FNDE',
    'municipio_processado': ' Município processado com sucesso',
    'municipio_erro': ' Erro ao processar município',
    'todos_municipios': ' Processando todos os municípios de MG',

    # Mensagens específicas Consulta FNS
    'inicio_consfns': ' SISTEMA DE AUTOMAÇÃO WEB - CONSULTA FNS',
    'consfns_processado': ' Município processado com sucesso - ConsFNS',
    'consfns_erro': ' Erro ao processar município - ConsFNS',
    'consfns_todos_municipios': ' Processando todos os municípios de MG - ConsFNS',
    'consfns_aguardando': ' Aguardando carregamento da consulta...',
    'consfns_download': ' Gerando planilha para download...',
} 