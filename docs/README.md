# 📚 Documentação - Sistema FVN

Documentação técnica do sistema de automação para extração de dados FPM.

## 📖 Guias Disponíveis

### 🎨 Interface do Usuário
- [**Interface Gráfica**](GUI_USAGE.md) - Como usar a interface visual moderna

### 🔧 Configuração e Instalação
- [**Instalação**](instalacao.md) - Guia completo de instalação
- [**Configuração**](configuracao.md) - Personalização de cidades e parâmetros

### 📋 Documentação Técnica
- [**Arquitetura**](arquitetura.md) - Estrutura técnica do sistema
- [**Arquivos de Saída**](arquivos-saida.md) - Formato dos Excel gerados

## 🚀 Uso Rápido

### Interface Gráfica
```bash
python gui_main.py
```

### Terminal
```bash
python main.py
```

## 📁 Estrutura de Arquivos

```
├── cidades.txt          # Lista estática (referência)
├── listed_cities.txt    # Cidades selecionadas (dinâmico)
├── gui_main.py          # Interface principal
├── main.py              # Execução terminal
└── classes/             # Módulos de automação
```

## 🆘 Suporte

1. Consulte os guias específicos acima
2. Verifique os logs de erro no terminal
3. Abra uma issue no repositório se necessário

---

**Mantenha sempre o Google Chrome atualizado para melhor compatibilidade.** 