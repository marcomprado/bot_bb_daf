# ⚙️ Configuração

## Lista de Cidades

Edite o arquivo `cidades.txt` com uma cidade por linha:

```
ouro branco
belo horizonte
contagem
uberlandia
juiz de fora
```

### ⚡ Seleção Automática por Estado

O sistema seleciona automaticamente cidades do estado de **Minas Gerais (MG)**:

1. ✅ Sistema preenche o campo com o nome da cidade
2. ✅ Clica automaticamente no seletor de beneficiário
3. ✅ Procura e seleciona especificamente a opção "- MG"
4. ✅ Confirma a seleção antes de continuar

**Exemplo:**
- Digite: `ouro branco`
- Sistema encontra: `OURO BRANCO - RN`, `OURO BRANCO - MG`, `OURO BRANCO - SP`
- **Seleciona automaticamente:** `OURO BRANCO - MG` ✅

## Personalização

### URL do Sistema

Para alterar a URL, edite `config.py`:
```python
'url_sistema': 'https://nova-url.exemplo.com'
```

### Timeouts e Pausas

Ajuste os tempos em `config.py`:
```python
SISTEMA_CONFIG = {
    'timeout_selenium': 10,        # Tempo limite para elementos
    'pausa_entre_cidades': 2,      # Pausa entre cidades
    'pausa_apos_preenchimento': 2, # Pausa após preencher campos
}
```

### Diretório de Saída

Para alterar onde salvar os arquivos, modifique `main.py`:
```python
data_extractor = DataExtractor(diretorio_base="minha_pasta")
```

## Seletores CSS

Os seletores podem ser ajustados em `config.py` se a página mudar:
```python
SELETORES_CSS = {
    'campo_beneficiario': '[formcontrolname="nomeBeneficiarioEntrada"]',
    'botao_continuar_inicial': '[aria-label="Continuar"]',
    # ... outros seletores
}
``` 