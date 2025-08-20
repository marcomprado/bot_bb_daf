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

python -m venv venv   #para windows
python3 -m venv venv  #para MAC e LINUX
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

---

## 🔨 Como criar o executável (Windows e macOS)

### 1. Gerar executável com PyInstaller

> **Pré-requisito:**
> - Ative o ambiente virtual (`source venv/bin/activate` no macOS/Linux ou `venv\Scripts\activate` no Windows)
> - Instale o PyInstaller:
>   ```sh
>     pip install pyinstaller
>   ```

#### **Para a interface gráfica (GUI):**

```sh
# Windows e macOS (gera executável na pasta dist/)
pyinstaller --noconfirm --onefile --windowed --icon=assets/app_icon.ico gui_main.py
```

- O executável será criado em `dist/gui_main.exe` (Windows) ou `dist/gui_main` (macOS/Linux).

---

### 2. Criar DMG para distribuição no macOS

#### **Com create-dmg (recomendado, visual):**

   brew install create-dmg
   create-dmg SistemaFVN.dmg dist/

   ou 
   hdiutil create -volname "Sistema FVN" -srcfolder dist/ -ov -format UDZO SistemaFVN.dmg
