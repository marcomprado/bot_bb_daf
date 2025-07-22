# 🎨 Guia da Interface Gráfica

## 🚀 Como Usar a Interface

### 1. Inicialização

Execute o comando no terminal:
```bash
python main_gui.py
```

### 2. Interface Principal

A janela será aberta com:

- **🏠 Título**: "🤖 Sistema de Automação FPM"
- **📝 Campo Município**: Digite o nome do município (ex: "ouro branco")
- **📅 Datas**: Campos pré-preenchidos com período do último mês
- **🚀 Botão**: "Buscar e Salvar em Excel"
- **📊 Área de Status**: Feedback em tempo real

### 3. Preenchimento

1. **Digite o município** no campo "📍 Município"
2. **Ajuste as datas** se necessário (formato: DD/MM/AAAA)
3. **Clique em "🚀 Buscar e Salvar em Excel"**

### 4. Acompanhamento

A área de status mostrará:
- ✅ Validação dos parâmetros
- 🔧 Configuração do sistema
- 🌐 Abertura do navegador
- 🏙️ Processamento do município
- 📊 Extração dos dados
- 💾 Salvamento do arquivo Excel

## ✨ Funcionalidades Avançadas

### 🔄 Processamento Assíncrono
- Interface **não trava** durante processamento
- Botões ficam **desabilitados** durante execução
- **Thread separada** para automação

### 🔍 Validações Automáticas
- ✅ Verificação de campos obrigatórios
- ✅ Validação de formato de data
- ✅ Prevenção de execuções duplas

### 🎨 Interface Responsiva
- ✅ Tema escuro moderno
- ✅ Redimensionamento automático
- ✅ Centralização na tela

## 📁 Saída de Dados

### Localização dos Arquivos
```
arquivos_baixados/
└── 2024-01-15/              # Pasta da data atual
    └── ouro_branco_143022.xlsx  # Arquivo do município
```

### Formato do Arquivo Excel
- **3 colunas**: DATA, PARCELA, VALOR DISTRIBUÍDO (R$)
- **Formatação**: Cores azul (crédito) e vermelho (débito)
- **Layout**: Idêntico ao site original do Banco do Brasil

## ⚠️ Troubleshooting

### Problemas Comuns

| Erro | Solução |
|------|---------|
| "Erro: Por favor, digite o nome do município" | Preencha o campo município |
| "Formato de data inválido" | Use o formato DD/MM/AAAA |
| "Falha na configuração do navegador" | Verifique se o Chrome está instalado |
| "Cidade MG não encontrada" | Verifique se existe município com esse nome em MG |

### Logs Detalhados
- Monitore a **área de status** na interface
- Verifique o **terminal** para logs técnicos
- Erros aparecem com ❌ vermelho
- Sucessos aparecem com ✅ verde

## 🔧 Personalização

### Alterar Datas Padrão
As datas vêm pré-preenchidas com:
- **Data Início**: 30 dias atrás
- **Data Fim**: Data atual

Você pode alterar conforme necessário antes de processar.

### Múltiplos Municípios
Para processar vários municípios:
1. Execute um município por vez
2. Aguarde o processamento terminar
3. Preencha o próximo município
4. Repita o processo

## 🎯 Diferenças da Versão Terminal

| Recurso | GUI | Terminal |
|---------|-----|----------|
| **Interface** | Gráfica moderna | Linha de comando |
| **Municípios** | Um por vez | Lista completa |
| **Datas** | Personalizáveis | Mês anterior fixo |
| **Feedback** | Tempo real visual | Logs no terminal |
| **Facilidade** | Muito fácil | Requer conhecimento técnico |

## 🏆 Vantagens da Interface Gráfica

- ✅ **Fácil de usar** - Não requer conhecimento técnico
- ✅ **Visual moderno** - Interface elegante e profissional  
- ✅ **Feedback imediato** - Vê o progresso em tempo real
- ✅ **Validação automática** - Previne erros de entrada
- ✅ **Flexibilidade** - Escolha qualquer período de datas
- ✅ **Segurança** - Não permite execuções duplas

---

**🎨 Interface desenvolvida com CustomTkinter para máxima usabilidade e experiência moderna.** 