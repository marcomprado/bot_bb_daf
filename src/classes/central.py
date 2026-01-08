# Configurações centralizadas do sistema de web scraping

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
    # Nome do arquivo com todas as 852 cidades de MG
    'arquivo_cidades': 'cidades.txt',

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

# Configurações do sistema MDS (Ministério do Desenvolvimento Social)
MDS_CONFIG = {
    # URLs do sistema MDS (duas URLs operando simultaneamente)
    'url_parcelas': 'https://aplicacoes.mds.gov.br/suaswebcons/restrito/execute.jsf?b=*dpotvmubsQbsdfmbtQbhbtNC&event=*fyjcjs',
    'url_saldo': 'https://aplicacoes.mds.gov.br/suaswebcons/restrito/execute.jsf?b=*tbmepQbsdfmbtQbhbtNC&event=*fyjcjs',

    # Parâmetros padrão
    'uf_padrao': 'MG',
    'esfera_padrao': 'M',  # MUNICIPAL (usado no Saldo por Conta)

    # Timeout para elementos MDS (em segundos)
    'timeout_selenium': 8,
    'max_tentativas_espera': 30,  # 30 tentativas de 1 segundo = 30 segundos total
    'max_retries': 3,  # Tentativas por município em caso de falha
    'timeout_aguarda_download': 3,  # Segundos após clicar gerar CSV
    'timeout_renomear_arquivo': 10,  # Segundos aguardando arquivo aparecer

    # Pausas específicas para MDS (em segundos)
    'pausa_aguarda_download': 3.0,
    'pausa_tentativa_espera': 1.0,

    # Diretórios específicos
    'diretorio_saida': 'mds',
    'subdiretorios_finais': ['parcela', 'saldo'],
    'prefixo_relatorio': 'RELATORIO_MDS',

    # Formato de nome de arquivo (sem sufixo - a pasta já identifica)
    'formato_arquivo': '{municipio}.csv',
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

# Seletores para elementos MDS - Parcelas Pagas
SELETORES_MDS_PARCELAS = {
    # Formulário Parcelas Pagas (6 passos)
    'select_ano': 'form:ano',  # ID
    'select_uf': 'form:uf',  # ID
    'select_municipio': 'form:municipio',  # ID
    'botao_pesquisar': 'form:pesquisar',  # ID
    'botao_gerar_csv': "//input[@type='submit' and @value='Gerar Relatório CSV']",  # XPATH
    'mensagem_sem_registros': "//span[@id='mensagens']//div[@class='info']",  # XPATH - mensagem de resultado vazio
}

# Seletores para elementos MDS - Saldo por Conta
SELETORES_MDS_SALDO = {
    # Formulário Saldo por Conta (8 passos)
    'select_ano': 'form:ano',  # ID
    'select_uf': 'form:uf',  # ID
    'select_mes': 'form:mes',  # ID
    'select_esfera': 'form:esferaAdministrativa',  # ID
    'select_municipio': 'form:municipio',  # ID
    'botao_pesquisar': 'form:pesquisar',  # ID
    'botao_gerar_csv': "//input[@type='submit' and @value='Gerar Relatório CSV']",  # XPATH
    'mensagem_sem_registros': "//span[@id='mensagens']//div[@class='info']",  # XPATH - mensagem de resultado vazio
}

# Configuracoes do Portal Saude MG
PORTAL_SAUDE_CONFIG = {
    # URL base do portal
    'url_base': 'https://portal-antigo.saude.mg.gov.br/deliberacoes/documents',
    'params_base': 'by_format=pdf&category_id=4795&ordering=newest&q=reso',

    # Timeouts (em segundos)
    'timeout_selenium': 10,
    'timeout_carregamento_maximo': 60,
    'timeout_scroll': 120,  # 2 minutos max para scroll infinito

    # Pausas (em segundos)
    'pausa_entre_scrolls': 0.8,
    'pausa_antes_download': 0.5,
    'pausa_entre_downloads': 0.5,

    # Limites de scroll
    'max_scrolls': 50,
    'scrolls_sem_conteudo_max': 3,

    # Diretorios
    'diretorio_saida': 'arquivos_baixados/portal_saude_mg',

    # Download
    'max_tentativas_download': 3,
    'tamanho_minimo_pdf': 1024,  # 1KB minimo para PDF valido
}

# Seletores para Portal Saude MG
SELETORES_PORTAL_SAUDE = {
    # Filtros
    'select_ano': 'select[name="by_year"]',
    'select_mes': 'select[name="by_month"]',
    'input_busca': 'input[name="q"]',

    # Resultados
    'link_documento': 'h2.title > a',
    'item_resultado': '.result-item, .document-item, .item',
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

    # Mensagens específicas MDS
    'inicio_mds': ' SISTEMA DE AUTOMAÇÃO WEB - MDS',
    'mds_processado': ' Município processado com sucesso - MDS',
    'mds_erro': ' Erro ao processar município - MDS',
    'mds_todos_municipios': ' Processando todos os municípios de MG - MDS',
    'mds_parcelas': ' [PARCELAS] Processando município',
    'mds_saldo': ' [SALDO] Processando município',
    'mds_sincronizado': ' Processamento sincronizado (Parcelas + Saldo)',

    # Mensagens específicas Pagamentos de Resoluções
    'inicio_pagamentos_res': ' SISTEMA DE AUTOMAÇÃO WEB - PAGAMENTOS DE RESOLUÇÕES',
    'pagamentos_res_processado': ' Município processado com sucesso - Pagamentos de Resoluções',
    'pagamentos_res_erro': ' Erro ao processar município - Pagamentos de Resoluções',
    'pagamentos_res_todos_municipios': ' Processando todos os municípios de MG - Pagamentos de Resoluções',
    'pagamentos_res_orcamentarios': ' [ORÇAMENTÁRIOS] Processando município',
    'pagamentos_res_restos': ' [RESTOS A PAGAR] Processando município',
    'pagamentos_res_sincronizado': ' Processamento sincronizado (Orçamentários + Restos a Pagar)',
}

# Configurações do sistema Pagamentos de Resoluções
PAGAMENTOS_RES_CONFIG = {
    # URLs do sistema (duas URLs operando simultaneamente)
    'url_orcamentarios': 'http://pagamentoderesolucoes.saude.mg.gov.br/pagamentos-orcamentarios',
    'url_restos_a_pagar': 'http://pagamentoderesolucoes.saude.mg.gov.br/restos-a-pagar',

    # Parâmetros padrão
    'uf_padrao': 'MG',

    # Timeout para elementos (em segundos)
    'timeout_selenium': 2,
    'max_tentativas_espera': 5,
    'max_retries': 3,
    'timeout_aguarda_download': 30,  # Timeout para aguardar CSV baixar
    'timeout_renomear_arquivo': 10,  # Aumentado para Windows executables

    # Pausas específicas (em segundos)
    'pausa_aguarda_download': 3.0,  # Aumentado para Windows executables
    'pausa_tentativa_espera': 0.5,
    'pausa_apos_consulta': 0.5,

    # Diretórios específicos
    'diretorio_saida': 'pagamentos_resolucoes',
    'subdiretorios_finais': ['orcamentarios', 'restos_a_pagar'],
    'prefixo_relatorio': 'RELATORIO_PAGAMENTOS_RES',

    # Formato de nome de arquivo
    'formato_arquivo_orcamentarios': '{municipio}_orcamentarios.csv',
    'formato_arquivo_restos': '{municipio}_restos_a_pagar.csv',
}

# Seletores para Pagamentos Orçamentários
SELETORES_PAGAMENTOS_RES_ORCAMENTARIOS = {
    # Formulário Pagamentos Orçamentários (4 passos)
    'select_ano': 'ano_pagamento',  # ID do select
    'select_municipio': 'dsc_municipio',  # ID do select
    'botao_consultar': 'input.btn.btn-success[type="submit"][value="Consultar"]',  # CSS Selector
    'botao_gerar_csv': 'button.dt-button.buttons-csv.buttons-html5',  # CSS Selector
    'mensagem_sem_registros': '//td[@class="dataTables_empty"]',  # XPATH - mensagem de tabela vazia
}

# Seletores para Restos a Pagar
SELETORES_PAGAMENTOS_RES_RESTOS = {
    # Formulário Restos a Pagar (4 passos)
    'select_ano': 'ano_pagamento',  # ID do select
    'select_municipio': 'dsc_municipio',  # ID do select
    'botao_consultar': 'input.btn.btn-success[type="submit"][value="Consultar"]',  # CSS Selector
    'botao_gerar_csv': 'button.dt-button.buttons-csv.buttons-html5',  # CSS Selector
    'mensagem_sem_registros': '//td[@class="dataTables_empty"]',  # XPATH - mensagem de tabela vazia
}