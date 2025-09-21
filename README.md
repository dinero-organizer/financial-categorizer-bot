# Financial Categorizer Bot

## Sobre
Bot do Telegram que recebe extratos bancários em CSV/OFX, faz o parsing, converte para um formato único de transações, envia ao Google Gemini para categorização e devolve um arquivo JSON com o resultado.

Fontes: código neste repositório (`main.py`, `src/handlers/bot_defs/handle_document.py`, `src/parsers/csv.py`, `src/parsers/ofx.py`, `src/ai/transaction_classifier.py`) e documentação oficial das bibliotecas `python-telegram-bot` (`https://docs.python-telegram-bot.org/`), `google-generativeai` (`https://ai.google.dev/`), e `ofxtools` (`https://ofxtools.readthedocs.io/`).

## Sumário
- [Integração com Gemini](docs/GEMINI_INTEGRATION.md)
- [Manipulação no Telegram](docs/TELEGRAM_HANDLING.md)
- [Ambiente e Variáveis](docs/ENVIRONMENT.md)
- [Parsers de Extrato](docs/PARSERS.md)

## Diagrama
```mermaid
flowchart LR
  user[Usuario Telegram] -->|Documento CSV ou OFX| api[Telegram API]
  api --> bot[Bot python-telegram-bot]
  bot --> handler[handle_document src/handlers/bot_defs/handle_document.py]
  handler --> tmp[(Armazenamento temporario)]
  handler --> csv[parse_csv_bank_statement src/parsers/csv.py]
  handler --> ofx[parse_ofx_file src/parsers/ofx.py]
  csv --> stmt[ParsedBankStatement src/parsers/models.py]
  ofx --> stmt
  stmt --> map[Mapear para JSON de transacoes]
  map --> ai[Gemini categorize_with_gemini src/ai/transaction_classifier.py]
  ai --> result[JSON categorizado]
  result --> reply[reply_document Telegram]

  subgraph Ambiente
    env[Variaveis BOT_TOKEN_TELEGRAM GOOGLE_API_KEY DEBUG APP_ENV]
    log[Logging]
    clean[Remocao de temporarios]
  end
  env -.-> bot
  clean -.-> tmp
  log -.-> handler
```