# Configuração local no Windows (PowerShell)

Este guia configura a V1 localmente, em modo **paper trading apenas**. Não necessita de API keys, ligação à Internet depois da instalação, corretora ou dinheiro real. Os dados de demonstração são determinísticos e identificados como MOCK.

## Pré-requisitos

Instale Python **3.11 ou superior** a partir de [python.org](https://www.python.org/downloads/windows/) e, no instalador, selecione **Add python.exe to PATH**. As restrições deste projeto não excluem Python 3.14: o pip pode selecionar as versões mais recentes permitidas (`<3.0` para bibliotecas de aplicação e `<9.0` para pytest), em vez de ficar preso a versões antigas sem wheels para Python 3.14. A confirmação final é feita localmente por `python -m pip install -r requirements.txt`.

Abra PowerShell na raiz do repositório e confirme o interpretador:

```powershell
py --version
py -3.14 --version
```

Se não tiver Python 3.14 instalado, use a versão instalada no restante guia (por exemplo, substitua `py -3.14` por `py -3.13`).

## Criar e ativar o ambiente virtual

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip --version
python -m pip install --upgrade pip
```

Se a política local impedir a ativação de scripts, aplique a alteração **apenas à sessão PowerShell atual** e ative novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Instalar e configurar

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Não preencha chaves de corretora: não são usadas nem suportadas. Confirme que `.env` mantém `PAPER_TRADING_ONLY=true`.

Para confirmar que o pip selecionou wheels compatíveis com a sua plataforma Windows, execute:

```powershell
python -m pip check
python -m pip list
```

## Validar a V1

```powershell
python -m pytest -q
python -m app pipeline AAPL
python -m app portfolio
python -m app performance
python -m app trades
```

O comando `pipeline` utiliza dados MOCK e pode criar `data\ai_trade.db`. A saída com `EXECUTED_PAPER` é uma execução simulada; não envia ordens reais.

## Iniciar a API

Com o ambiente virtual ainda ativo:

```powershell
python -m uvicorn app.main:app --reload
```

Em outra janela PowerShell, pode verificar:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod -Method Post http://127.0.0.1:8000/pipeline/AAPL
```

Pare o servidor com `Ctrl+C`. Não existem endpoints de trading real.

## Apagar e recriar um ambiente corrompido

Feche processos Python que usem o projeto, abra um novo PowerShell na raiz e execute:

```powershell
Deactivate  # ignore se não estiver num venv
Remove-Item -Recurse -Force .venv
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env -Force
python -m pytest -q
```

## Compatibilidade Windows e Python 3.14

* O código não invoca comandos Unix, `subprocess`, `os.system` nem caminhos codificados para POSIX. O comando Unix `source .venv/bin/activate` do README não se aplica ao Windows; use `Activate.ps1` deste guia.
* O URL SQLite `sqlite:///data/ai_trade.db` é relativo à raiz do projeto e é aceite pelo driver SQLite/SQLAlchemy no Windows. Não altere o separador para `\` no URL.
* `pandas` e `numpy` podem ter wheels específicos por versão de Python e arquitetura. As faixas atuais permitem ao pip selecionar as versões recentes compatíveis com Python 3.14. Num Windows ARM64 ou numa instalação muito recente sem wheel disponível, use temporariamente Python 3.13 ou instale depois de o fornecedor publicar uma wheel; não altere o código da aplicação para contornar isso.
