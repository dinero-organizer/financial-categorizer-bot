# Ambiente e Variáveis

Configurações necessárias para execução local e produção.

## Variáveis de ambiente
- `BOT_TOKEN_TELEGRAM`: token do bot do Telegram. Usado em `main.py`.
- `GOOGLE_API_KEY`: chave da API do Google para o Gemini. Usada em `src/ai/transaction_classifier.py`.
- `DEBUG`: quando definido como `1`, `true`, `yes` ou `on`, ativa modo de depuração (mantém temporários).
- `APP_ENV`/`ENVIRONMENT`: quando `production`/`prod`, desativa modo de depuração por padrão.

## Carregamento de variáveis
`main.py` utiliza `dotenv.load_dotenv()`, permitindo definir variáveis em um arquivo `.env` no diretório do projeto.

## Dependências
As bibliotecas necessárias estão em `requirements.txt` (por exemplo, `python-telegram-bot`, `google-generativeai`, `ofxtools`, `python-dotenv`).

## Fontes
- Código: `main.py`, `src/ai/transaction_classifier.py`, `src/handlers/bot_defs/handle_document.py`, `requirements.txt`.
- Documentação: `python-dotenv` (`https://pypi.org/project/python-dotenv/`).

