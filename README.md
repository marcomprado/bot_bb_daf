# 🤖 Automação FPM - Web Scraping

> **📚 Documentação completa:** [`docs/`](docs/)

Sistema automatizado para extração de dados do **Fundo de Participação dos Municípios (FPM)** do Banco do Brasil, desenvolvido em Python com Selenium.

## 🚀 Início Rápido

```bash
# Clone e configure
git clone https://github.com/marcomprado/bot_bb_daf.git
cd bot_bb_daf
source venv/bin/activate  # macOS/Linux ou venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Configure as cidades
echo "ouro branco" > cidades.txt
echo "belo horizonte" >> cidades.txt

# Execute
python main.py
```

## ⭐ Principais Funcionalidades

- ✅ **Automação completa** do processo de consulta FPM
- ✅ **Seleção automática** de cidades do estado de Minas Gerais  
- ✅ **Preenchimento automático** de datas (último mês)
- ✅ **Extração estruturada** das tabelas de resultados
- ✅ **Excel formatado** com cores (azul/vermelho) e layout profissional
- ✅ **Organização automática** em pastas por data
- ✅ **Relatório consolidado** com estatísticas completas

## 📊 Saída de Dados

```
arquivos_baixados/
├── 2024-01-15/
│   ├── ouro_branco_143022.xlsx
│   ├── belo_horizonte_143127.xlsx
│   └── relatorio_consolidado_143500.xlsx
```

## 🛠️ Tecnologias

**Python 3.6+** • **Selenium** • **BeautifulSoup** • **Pandas** • **OpenPyXL**

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [📥 Instalação](docs/instalacao.md) | Guia completo de instalação e configuração |
| [⚙️ Configuração](docs/configuracao.md) | Personalização de cidades, URLs e parâmetros |
| [🏗️ Arquitetura](docs/arquitetura.md) | Estrutura técnica e componentes do sistema |
| [📊 Arquivos de Saída](docs/arquivos-saida.md) | Formato e organização dos Excel gerados |

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Abra issues ou envie pull requests.

---

**Desenvolvido com ❤️ para automatizar consultas FPM e facilitar o trabalho com dados municipais.** 