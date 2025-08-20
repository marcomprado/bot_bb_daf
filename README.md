# 🤖 Automação FPM - Web Scraping

Sistema automatizado para extração de dados do **Fundo de Participação dos Municípios (FPM)** do Banco do Brasil, desenvolvido em Python com Selenium.

## 🚀 Início Rápido

### Interface Gráfica (Recomendado)

```bash
# Clone e configure
git clone https://github.com/marcomprado/bot_bb_daf.git
cd bot_bb_daf
source venv/bin/activate  # macOS/Linux ou venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Execute a interface gráfica
python gui_main.py
```

### Terminal (Avançado)

```bash
# Execute diretamente
python main.py
```

## ⭐ Principais Funcionalidades

- ✅ **Interface Gráfica Moderna** - Seleção visual de cidades e datas
- ✅ **Seleção Múltipla** - Processe várias cidades de uma vez
- ✅ **Automação Completa** - Navegação automática no site do BB
- ✅ **Extração Inteligente** - Dados estruturados em Excel
- ✅ **Formatação Profissional** - Cores e layout idênticos ao site original
- ✅ **Relatório Consolidado** - Estatísticas detalhadas do processamento
- ✅ **Gestão de Navegador** - Fechamento automático após processamento

## 🎯 Como Usar

### Interface Gráfica

1. **Execute** `python gui_main.py`
2. **Selecione** período de datas (pré-preenchido com último mês)
3. **Escolha** cidades:
   - **Todas as Cidades**: Processa todas as 852 cidades de MG
   - **Seleção Individual**: Escolha específicas em popup
4. **Clique** em "Executar Processamento"
5. **Acompanhe** o progresso e aguarde conclusão

### Terminal

1. **Configure** o arquivo `listed_cities.txt` ou use a GUI primeiro
2. **Execute** `python main.py`
3. **Aguarde** o processamento automático

## 📊 Saída de Dados

```
arquivos_baixados/
├── 2024-01-15/
│   ├── belo_horizonte_143022.xlsx
│   ├── contagem_143127.xlsx
│   └── relatorio_consolidado_143500.xlsx
```

### Formato Excel
- **3 colunas**: DATA, PARCELA, VALOR DISTRIBUÍDO (R$)
- **Cores automáticas**: Azul (créditos), Vermelho (débitos)
- **Formatação profissional**: Layout idêntico ao site do BB

## 🛠️ Tecnologias

- **Python 3.6+**
- **Selenium** - Automação web
- **CustomTkinter** - Interface gráfica moderna
- **Pandas & OpenPyXL** - Manipulação e geração de Excel
- **BeautifulSoup** - Extração de dados

## 📁 Estrutura de Arquivos

```
├── gui_main.py              # Interface gráfica principal
├── main.py                  # Execução via terminal
├── classes/                 # Módulos de automação
│   ├── automation_core.py   # Núcleo centralizado
│   ├── web_scraping_bot.py  # Automação web
│   ├── data_extractor.py    # Extração de dados
│   └── ...
├── cidades.txt             # Lista estática de cidades (referência)
├── listed_cities.txt       # Cidades selecionadas (gerado pela GUI)
└── config.py               # Configurações centralizadas
```

## 🔧 Configuração

### Personalizar Cidades

**Para interface gráfica**: Use a seleção visual na própria interface.

**Para terminal**: Edite `listed_cities.txt`:
```
belo horizonte
contagem
uberlandia
```

### Alterar Configurações

Edite `config.py` para ajustar timeouts, URLs ou seletores CSS.

## ⚠️ Requisitos

- **Google Chrome** instalado
- **Python 3.6+**
- **Conexão estável** com internet
- **Permissões** para criação de arquivos

## 🆘 Resolução de Problemas

| Problema | Solução |
|----------|---------|
| Chrome não encontrado | Instale o Google Chrome |
| Erro de dependências | Execute `pip install -r requirements.txt --force-reinstall` |
| Interface não abre | Verifique Python 3.6+ e CustomTkinter |
| Processo não termina | Use botão "Cancelar" na interface |

## 📈 Estatísticas

- **852 cidades** de Minas Gerais suportadas
- **Processamento sequencial** otimizado
- **Taxa de sucesso** > 95% em condições normais
- **Tempo médio** ~30s por cidade

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Abra issues ou envie pull requests.

---

**Desenvolvido para automatizar consultas FPM e facilitar o trabalho com dados municipais.** 