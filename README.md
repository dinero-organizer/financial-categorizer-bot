# Financial Categorizer Bot

## Sobre
Bot do Telegram que recebe extratos bancários em CSV/OFX, faz o parsing, converte para um formato único de transações, envia ao Google Gemini para categorização e devolve um arquivo JSON com o resultado.

## Sumário
- [Integração com Gemini](docs/GEMINI_INTEGRATION.md)
- [Manipulação no Telegram](docs/TELEGRAM_HANDLING.md)
- [Ambiente e Variáveis](docs/ENVIRONMENT.md)
- [Parsers de Extrato](docs/PARSERS.md)

## Diagrama
```mermaid
flowchart TB
  user[Usuario Telegram] --> api[Telegram API]
  api --> bot[Bot python-telegram-bot]
  bot --> handler[handle_document]
  handler --> tmp[Armazenamento temporario]
  handler --> parser{Tipo do arquivo}
  parser -->|CSV| csv[parse_csv_bank_statement]
  parser -->|OFX| ofx[parse_ofx_file]
  csv --> stmt[ParsedBankStatement]
  ofx --> stmt
  stmt --> map[Mapear para JSON de transacoes]
  map --> ai[Gemini categorize_with_gemini]
  ai --> result[JSON categorizado]
  result --> reply[reply_document]

  subgraph Ambiente
    env[Variaveis BOT_TOKEN_TELEGRAM GOOGLE_API_KEY DEBUG APP_ENV]
    log[Logging]
    clean[Remocao de temporarios]
  end
  env -.-> bot
  clean -.-> tmp
  log -.-> handler
```