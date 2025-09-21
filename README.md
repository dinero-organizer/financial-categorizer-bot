# Financial Categorizer Bot

## Sobre
Bot do Telegram que recebe extratos bancários em CSV/OFX, faz o parsing, converte para um formato único de transações, envia ao Google Gemini para categorização e devolve um arquivo JSON com o resultado.

## Sumário
- [Integração com Gemini](docs/GEMINI_INTEGRATION.md)
- [Manipulação no Telegram](docs/TELEGRAM_HANDLING.md)
- [Ambiente e Variáveis](docs/ENVIRONMENT.md)
- [Parsers de Extrato](docs/PARSERS.md)
 - [Deploy em EC2](docs/DEPLOY_EC2.md)

## Diagrama
```mermaid
flowchart TB
  user[Usuario<br/>Telegram] --> api[Telegram<br/>API]
  api --> bot[Bot<br/>python-telegram-bot]
  bot --> handler[handle_document]
  handler --> tmp[Armazenamento<br/>temporario]
  handler --> parser{Tipo do<br/>arquivo}
  parser -->|CSV| csv[parse_csv_bank_<br/>statement]
  parser -->|OFX| ofx[parse_ofx_<br/>file]
  csv --> stmt[ParsedBank<br/>Statement]
  ofx --> stmt
  stmt --> map[Mapear p/ JSON<br/>de transacoes]
  map --> ai[Gemini<br/>categorize_with_gemini]
  ai --> result[JSON<br/>categorizado]
  result --> reply[reply_<br/>document]

  subgraph Ambiente
    env[Vars<br/>BOT_TOKEN_TELEGRAM<br/>GOOGLE_API_KEY<br/>DEBUG<br/>APP_ENV]
    log[Logging]
    clean[Remocao de<br/>temporarios]
  end
  env -.-> bot
  clean -.-> tmp
  log -.-> handler

  classDef small font-size:12px;
  class bot,handler,tmp,csv,ofx,stmt,map,ai,result,reply,env,clean small;
```