# 📚 Documentação - Automação FPM

Documentação completa do sistema de automação para extração de dados FPM.

## 📖 Índice da Documentação

### 🚀 Primeiros Passos
- [📥 **Instalação**](instalacao.md) - Guia completo de instalação e configuração inicial
- [⚙️ **Configuração**](configuracao.md) - Personalização de cidades, URLs e parâmetros

### 🔧 Documentação Técnica  
- [🏗️ **Arquitetura**](arquitetura.md) - Estrutura técnica e componentes do sistema
- [📊 **Arquivos de Saída**](arquivos-saida.md) - Formato e organização dos Excel gerados

## 🎯 Fluxo Básico de Uso

1. **Instale** seguindo o [guia de instalação](instalacao.md)
2. **Configure** as cidades no [arquivo de configuração](configuracao.md)
3. **Execute** o comando `python main.py`
4. **Verifique** os arquivos na pasta `arquivos_baixados/`

## 🆘 Resolução de Problemas

### Problemas Comuns

| Problema | Solução |
|----------|---------|
| Chrome não encontrado | Instale o Google Chrome |
| Erro de dependências | Execute `pip install -r requirements.txt --force-reinstall` |
| Seletor não encontrado | Verifique se a página não mudou |
| Cidade MG não encontrada | Confira se existe cidade com esse nome em MG |

### Debug

Para debug detalhado, monitore os logs no terminal:
- ✅ **Verde**: Operações bem-sucedidas  
- ❌ **Vermelho**: Erros críticos
- ⚠️ **Amarelo**: Avisos importantes
- 🔍 **Azul**: Informações de debug

## 📞 Suporte

1. Consulte esta documentação
2. Verifique os logs de erro no terminal
3. Abra uma [issue no GitHub](../../../issues) se necessário

---

**💡 Dica:** Mantenha sempre o Google Chrome atualizado para melhor compatibilidade. 