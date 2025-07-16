# 📥 Instalação

## Pré-requisitos

- Python 3.6 ou superior
- Google Chrome instalado
- Conexão com internet estável

## Configuração inicial

### 1. Clone o repositório
```bash
git clone https://github.com/marcomprado/bot_bb_daf.git
cd bot_bb_daf
```

### 2. Ative o ambiente virtual
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

## Verificação da instalação

Execute o comando para verificar se tudo está funcionando:
```bash
python main.py
```

Se aparecer a tela de verificação de dependências e o navegador abrir, a instalação foi bem-sucedida!

## Solução de problemas

### Chrome não encontrado
- Certifique-se de que o Google Chrome está instalado
- O ChromeDriver será baixado automaticamente

### Erro de dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Problemas de codificação
- Certifique-se de que o arquivo `cidades.txt` está em UTF-8 