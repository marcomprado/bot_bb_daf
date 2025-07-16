# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- [ ] Interface gráfica opcional
- [ ] Modo headless para execução em servidor
- [ ] Exportação em outros formatos (CSV, JSON)
- [ ] Agendamento automático de execuções 