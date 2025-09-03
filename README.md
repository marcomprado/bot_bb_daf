# 🏛️ Sistema FVN - Automação Web

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://www.selenium.dev)

Sistema de automação web para extração de dados municipais com interface gráfica moderna e processamento paralelo.

## ✨ Funcionalidades

### 📊 Sistema BB DAF
- Extração automatizada de dados FPM (Fundo de Participação dos Municípios)
- Processamento em lote de múltiplas cidades
- Suporte para execução paralela com múltiplas instâncias
- Geração automática de planilhas Excel formatadas

### 🎓 Sistema FNDE
- Integração com o sistema FNDE (Fundo Nacional de Desenvolvimento da Educação)
- Coleta de dados educacionais municipais
- Exportação estruturada de informações

## 🔧 Requisitos

- **Python 3.8+**
- **Google Chrome** instalado
- **Sistema Operacional**: Windows, macOS ou Linux
- **Memória RAM**: 4GB+ recomendado para processamento paralelo

## 📁 Estrutura do Projeto

```
bot-bb/
├── main.py                 # Ponto de entrada principal
├── src/
│   ├── view/              # Interface gráfica (GUI)
│   ├── bots/              # Motores de automação
│   ├── classes/           # Utilitários e configurações
│   └── assets/            # Recursos estáticos
├── arquivos_baixados/     # Dados extraídos
└── requirements.txt       # Dependências Python
```

## 📄 Licença

**⚠️ SOFTWARE PROPRIETÁRIO - TODOS OS DIREITOS RESERVADOS**

Este software é propriedade de Marco Martinelli do Carmo Prado. O código-fonte é disponibilizado apenas para visualização. É expressamente proibido copiar, modificar, distribuir ou usar este software sem permissão escrita do proprietário.

Veja o arquivo [LICENSE](LICENSE) para os termos completos.

---

<p align="center">
  Desenvolvido por Marco Martinelli do Carmo Prado
</p>