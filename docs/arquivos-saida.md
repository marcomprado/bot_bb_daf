# 📊 Arquivos de Saída

## Estrutura de Diretórios

O sistema organiza automaticamente os arquivos extraídos:

```
arquivos_baixados/
├── 2024-01-15/                    # Pasta da data (YYYY-MM-DD)
│   ├── ouro_branco_143022.xlsx    # Dados da cidade
│   ├── belo_horizonte_143127.xlsx # Dados de outra cidade
│   └── relatorio_consolidado_143500.xlsx  # Relatório final
├── 2024-01-16/                    # Nova pasta no dia seguinte
│   └── ...
```

### Nomenclatura

- **Arquivos de dados**: `{nome_da_cidade}_{HHMMSS}.xlsx`
- **Relatório consolidado**: `relatorio_consolidado_{HHMMSS}.xlsx`
- **Pasta por data**: `YYYY-MM-DD`

## Formato dos Arquivos Excel

### Estrutura Visual

```
NOME DO MUNICÍPIO                           ← Linha 1 (título)
FPM - FUNDO DE PARTICIPACAO DOS MUNICIPIOS  ← Linha 2 (subtítulo)
                                            ← Linha 3 (espaçamento)
DATA        | PARCELA         | VALOR DISTRIBUÍDO (R$)  ← Linha 4 (cabeçalhos)
10.01.2023  | PARCELA DE IPI  | 333.889,50C            ← Dados em azul (C)
10.01.2023  | RETENCAO PASEP  | 34.105,11D             ← Dados em vermelho (D)
10.01.2023  | TOTAL NA DATA   | 2.672.655,70C          ← Total em azul
                                                        ← Linha em branco (nova data)
11.01.2023  | PARCELA DE IPI  | 245.123,45C            ← Nova data
```

### Características

- ✅ **3 colunas**: DATA, PARCELA, VALOR DISTRIBUÍDO (R$)
- ✅ **Nome do município**: Primeiro linha em destaque
- ✅ **Cores automáticas**: 
  - 🔵 **Azul** para valores terminados em "C" (crédito)
  - 🔴 **Vermelho** para valores terminados em "D" (débito)
- ✅ **Linha em branco**: Antes de cada nova data
- ✅ **Bordas e alinhamento**: Formatação profissional
- ✅ **Larguras otimizadas**: Colunas ajustadas automaticamente

## Relatório Consolidado

O arquivo `relatorio_consolidado_*.xlsx` contém duas abas:

### Aba 1: Resumo Geral
| Campo | Descrição |
|-------|-----------|
| Data e Hora do Processamento | Timestamp da execução |
| Total de Cidades Tentadas | Quantidade total |
| Cidades Processadas com Sucesso | Sucessos |
| Cidades com Erro | Falhas |
| Taxa de Sucesso (%) | Percentual de sucesso |
| Diretório dos Arquivos | Caminho da pasta |

### Aba 2: Detalhes por Cidade
| Campo | Descrição |
|-------|-----------|
| Cidade | Nome da cidade processada |
| Status | Sucesso ou Erro |
| Registros Encontrados | Quantidade de dados extraídos |
| Observações | Detalhes do erro (se houver) |

## Exemplo de Dados

| DATA       | PARCELA         | VALOR DISTRIBUÍDO (R$) |
|------------|-----------------|------------------------|
| 10.01.2023 | PARCELA DE IPI  | 333.889,50C           |
| 10.01.2023 | PARCELA DE IR   | 3.076.622,12C         |
| 10.01.2023 | RETENCAO PASEP  | 34.105,11D            |
| 10.01.2023 | RFB-PREV-PARC60 | 21.648,49D            |
| 10.01.2023 | DEDUCAO FUNDEB  | 682.102,32D           |
| 10.01.2023 | TOTAL NA DATA   | 2.672.655,70C         | 