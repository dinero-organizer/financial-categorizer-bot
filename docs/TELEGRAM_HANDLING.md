# Manipulação no Telegram

Este domínio descreve como o bot integra com o Telegram para receber arquivos e acionar o fluxo de processamento.

## Componentes
- Ponto de entrada: `main.py` (registra `MessageHandler(filters.Document.ALL, handle_document)`).
- Manipulador principal: `src/handlers/bot_defs/handle_document.py`.

## Fluxo
1. Detectar o tipo do arquivo (`_detect_file_type`).
2. Baixar o documento para diretório temporário (`_download_document_to_temp`).
3. Fazer parse do arquivo (`_parse_file_to_statement`), usando:
   - CSV: `parse_csv_bank_statement` em `src/parsers/csv.py`.
   - OFX: `parse_ofx_file` em `src/parsers/ofx.py`.
4. Converter para lista de transações (`_statement_to_transactions`).
5. Categorizar via IA (`_categorize_with_ai` → `categorize_with_gemini`).
6. Persistir resultado em JSON (`_write_result_json`).
7. Responder ao usuário com `reply_document` contendo o JSON.

## Limpeza de temporários
O manipulador decide se remove os arquivos temporários com base em `_should_cleanup_tmp()`, que considera as variáveis de ambiente `DEBUG` e `APP_ENV`/`ENVIRONMENT`.

## Fontes
- Código: `main.py`, `src/handlers/bot_defs/handle_document.py`.
- Documentação: `python-telegram-bot` (`https://docs.python-telegram-bot.org/`).

