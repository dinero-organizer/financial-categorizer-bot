# Parsers de Extrato

Este domínio documenta os parsers para arquivos CSV e OFX.

## CSV
- Implementação: `src/parsers/csv.py` (`CSVBankParser`, `parse_csv_bank_statement`).
- Funcionalidades:
  - Detecta delimitador com `csv.Sniffer`.
  - Mapeia colunas comuns (data, descrição, valor, débito/crédito).
  - Converte valores monetários e datas para tipos nativos.
  - Retorna `ParsedBankStatement` com uma lista de `Expense`.

## OFX
- Implementação: `src/parsers/ofx.py` (`parse_ofx_file`, `parse_ofx_content`).
- Funcionalidades:
  - Usa `ofxtools.OFXTree` para parse.
  - Converte `STMTTRN` em `Expense` com data, descrição e valor.
  - Retorna `ParsedBankStatement` com as transações.

## Modelos
- `src/parsers/models.py`: define `Expense` e `ParsedBankStatement`.

## Fontes
- Código: `src/parsers/csv.py`, `src/parsers/ofx.py`, `src/parsers/models.py`.
- Documentação: módulo `csv` da biblioteca padrão (`https://docs.python.org/3/library/csv.html`), `ofxtools` (`https://ofxtools.readthedocs.io/`).

