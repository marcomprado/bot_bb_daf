# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-01-17

### 🔧 **Melhorias no Sistema de Arquivos**
- ✅ **Separação de arquivos**: `cidades.txt` (estático) e `listed_cities.txt` (dinâmico)
- ✅ **Proteção de dados**: `cidades.txt` nunca mais será sobrescrito
- ✅ **Arquivo de referência**: Lista completa de 852 cidades preservada
- ✅ **Gitignore atualizado**: `listed_cities.txt` não versionado

### 🚀 **Melhorias na Interface**
- ✅ **Fechamento automático**: Navegador fecha ao terminar processamento
- ✅ **Botão cancelar aprimorado**: Para bot E fecha navegador
- ✅ **Popup unificado**: "processo foi terminado" em todas as situações
- ✅ **Gestão de processo**: Controle completo de início/fim/cancelamento

### 🏗️ **Melhorias Técnicas**
- ✅ **AutomationCore otimizado**: Fechamento automático em todos os cenários
- ✅ **Tratamento de erros**: Navegador sempre fechado, mesmo em erro
- ✅ **FileManager inteligente**: Detecta tipo de arquivo e orienta usuário
- ✅ **Arquitetura mantida**: Front-end como ponte para back-end

### 📁 **Nova Estrutura de Arquivos**
```
├── cidades.txt          # 🔒 Estático (852 cidades de MG)
├── listed_cities.txt    # 🔄 Dinâmico (seleção atual)
├── gui_main.py          # 🎨 Interface principal
└── main.py              # ⚡ Execução terminal
```

## [2.0.0] - 2024-01-16

### 🚀 NOVA VERSÃO: Sistema de Queue v2.0
- ✅ **Interface v2.0** com seleção múltipla de cidades
- ✅ **Sistema de queue** para processamento sequencial
- ✅ **Progresso visual** com barra de progresso e contadores
- ✅ **Navegador persistente** (3x mais eficiente)
- ✅ **Cancelamento** durante processamento
- ✅ **Lista expandida** com 30+ cidades de MG
- ✅ **Checkbox "Selecionar Todas"** para conveniência
- ✅ **Relatório consolidado** automático

### 🔧 Melhorias Técnicas v2.0
- ✅ **AutomationBridgeV2** com processamento sequencial
- ✅ **Interface responsiva** com threading assíncrono
- ✅ **Manutenção de estado** do navegador entre cidades
- ✅ **Callbacks de progresso** em tempo real
- ✅ **Tratamento de erros** individual por cidade
- ✅ **Performance otimizada** com reutilização de recursos

### 📁 Nova Estrutura v2.0
```
client/
├── gui_interface_v2.py      # Interface com queue
├── automation_bridge_v2.py  # Automação sequencial
├── demo_interface_v2.py     # Demonstração v2.0
└── [arquivos v1.0 mantidos] # Compatibilidade
```

### 📚 Documentação v2.0
- ✅ **UPGRADE_V2.md** - Guia completo da migração
- ✅ **Demo interativo** da nova interface
- ✅ **Comparação detalhada** v1.0 vs v2.0
- ✅ **README atualizado** com destaque para v2.0

### 🔄 Compatibilidade
- ✅ **v1.0 mantida** - Todos os arquivos originais preservados
- ✅ **Dados compatíveis** - Mesmo formato de saída Excel
- ✅ **Migração suave** - Reutiliza configurações existentes

## [1.1.0] - 2024-01-16

### ✨ NOVA FUNCIONALIDADE: Interface Gráfica
- ✅ **Interface moderna** com CustomTkinter
- ✅ **Campos interativos** para município e datas personalizadas
- ✅ **Feedback em tempo real** durante processamento
- ✅ **Validação automática** de campos e formatos
- ✅ **Threading assíncrono** (interface não trava)
- ✅ **Design responsivo** com tema escuro
- ✅ **Arquivo principal**: `main_gui.py` (interface otimizada)

### 🔧 Melhorias Técnicas
- ✅ **Ponte de automação** (`automation_bridge.py`)
- ✅ **Arquitetura modular** para GUI
- ✅ **Processamento individual** por município
- ✅ **Tratamento de erros** amigável
- ✅ **Documentação completa** da interface

### 📁 Nova Estrutura
```
client/
├── gui_interface.py      # Interface principal
├── automation_bridge.py  # Ponte com automação
├── demo_interface.py     # Demonstração
└── README.md            # Documentação
```

### 📚 Documentação
- ✅ **Guia completo** da interface gráfica
- ✅ **Instruções de uso** passo a passo
- ✅ **Troubleshooting** e soluções
- ✅ **README atualizado** com duas versões

## [1.0.0] - 2024-01-15

### Adicionado
- ✅ Automação completa do processo de consulta FPM
- ✅ Seleção automática de cidades do estado de Minas Gerais
- ✅ Preenchimento automático de datas (último mês)
- ✅ Extração estruturada de dados das tabelas de resultados
- ✅ Geração de arquivos Excel com formatação profissional
- ✅ Organização automática por data em pastas diárias
- ✅ Cores automáticas (azul para créditos, vermelho para débitos)
- ✅ Relatório consolidado com estatísticas completas
- ✅ Arquitetura orientada a objetos modular
- ✅ Tratamento robusto de erros
- ✅ Configuração centralizada
- ✅ Documentação completa

### Estrutura técnica
- **WebScrapingBot**: Automação principal do Selenium
- **DataExtractor**: Extração e formatação de dados
- **DateCalculator**: Cálculo automático de datas
- **FileManager**: Gerenciamento de arquivos
- **Config centralizada**: Configurações em arquivo único

### Funcionalidades destacadas
- Navegação automática entre páginas
- Dropdown inteligente para seleção de estado
- Excel formatado identicamente ao site original
- Recuperação automática de erros
- Logs detalhados para debug
- Processamento em lote de múltiplas cidades

## [Unreleased]

### Planejado
- [ ] Suporte a outros estados além de MG
- [ ] Conversão para executável (.exe)
- [ ] Modo headless para execução em servidor
- [ ] Exportação em outros formatos (CSV, JSON)
- [ ] Agendamento automático de execuções
- [ ] Interface v3.0 com drag & drop 