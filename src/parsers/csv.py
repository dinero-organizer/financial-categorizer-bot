"""
Parser para arquivos CSV bancários
"""

from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Any

import csv

from src.utils.logger import get_logger
from src.parsers.models import Expense, ParsedBankStatement

logger = get_logger(__name__)


class CSVBankParser:
    """Parser para arquivos CSV de extratos bancários"""

    def __init__(self):
        self.supported_date_formats = [
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%m/%d/%Y",
            "%Y/%m/%d"
        ]

    def parse_date(self, date_str: str) -> Optional[date]:
        """Converte string de data para objeto date"""
        date_str = date_str.strip()

        for date_format in self.supported_date_formats:
            try:
                return datetime.strptime(date_str, date_format).date()
            except ValueError:
                continue

        logger.warning(f"Não foi possível converter a data: {date_str}")
        return None

    def parse_value(self, value_str: str) -> float:
        """Converte string de valor para float"""
        try:
            # Remove caracteres comuns em valores monetários
            value_str = value_str.strip()
            value_str = value_str.replace("R$", "").replace("$", "")
            value_str = value_str.replace(" ", "")

            # Remove parênteses para valores negativos
            if value_str.startswith("(") and value_str.endswith(")"):
                inner_value = value_str[1:-1]
                # Se já tem sinal negativo, remove para evitar duplo negativo
                if inner_value.startswith("-"):
                    value_str = inner_value
                else:
                    value_str = "-" + inner_value

            # Detecta formato: se tem vírgula E ponto, assume formato brasileiro (1.000,50)
            # Se tem apenas vírgula, assume vírgula como decimal (100,50)
            # Se tem apenas ponto, assume ponto como decimal (100.50)
            if "," in value_str and "." in value_str:
                # Formato brasileiro: 1.000,50 ou 1,000.50
                # Verifica qual vem primeiro
                comma_pos = value_str.find(",")
                dot_pos = value_str.find(".")

                if comma_pos > dot_pos:
                    # Formato: 1.000,50 (brasileiro)
                    value_str = value_str.replace(".", "").replace(",", ".")
                else:
                    # Formato: 1,000.50 (americano)
                    value_str = value_str.replace(",", "")
            elif "," in value_str:
                # Apenas vírgula: assume como decimal
                value_str = value_str.replace(",", ".")
            # Se apenas ponto, mantém como está (já é decimal americano)

            return float(value_str)
        except (ValueError, AttributeError) as e:
            logger.error(f"Erro ao converter valor '{value_str}': {e}")
            return 0.0

    def detect_csv_format(self, file_path: str, encoding: str = 'utf-8-sig') -> Dict[str, Any]:
        """Detecta o formato do CSV automaticamente"""
        with open(file_path, 'r', encoding=encoding, newline='') as file:
            # Lê as primeiras linhas para detectar o formato
            sample = file.read(1024)
            file.seek(0)

            # Detecta o dialeto CSV
            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(sample)
                delimiter = dialect.delimiter
            except:
                delimiter = ','

            # Lê o cabeçalho
            reader = csv.reader(file, delimiter=delimiter)
            headers = next(reader, [])

            # Mapeia colunas comuns
            column_mapping = self._map_columns(headers)

            return {
                'delimiter': delimiter,
                'headers': headers,
                'column_mapping': column_mapping
            }

    def _map_columns(self, headers: List[str]) -> Dict[str, int]:
        """Mapeia colunas do CSV para campos do modelo"""
        headers_lower = [h.lower().strip() for h in headers]
        mapping = {}

        # Mapear data
        date_keywords = ['data', 'date', 'dt', 'fecha']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in date_keywords):
                mapping['date'] = i
                break

        # Mapear descrição/nome
        desc_keywords = ['descricao', 'descrição', 'description', 'historico', 'histórico', 'memo', 'detail']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in desc_keywords):
                mapping['description'] = i
                break

        # Mapear valor
        value_keywords = ['valor', 'value', 'amount', 'montante']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in value_keywords):
                mapping['value'] = i
                break

        # Se não encontrou valor único, procura por débito e crédito separados
        if 'value' not in mapping:
            debit_keywords = ['debito', 'débito', 'debit']
            credit_keywords = ['credito', 'crédito', 'credit']

            for i, header in enumerate(headers_lower):
                if any(keyword in header for keyword in debit_keywords):
                    mapping['debit'] = i
                elif any(keyword in header for keyword in credit_keywords):
                    mapping['credit'] = i

        # Mapear categoria (opcional)
        category_keywords = ['categoria', 'category', 'tipo', 'type', 'class']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in category_keywords):
                mapping['category'] = i
                break

        return mapping

    def parse_file(self, file_path: str, encoding: str = 'utf-8-sig') -> ParsedBankStatement:
        """Parse do arquivo CSV bancário"""
        logger.info(f"Iniciando parse do arquivo: {file_path}")

        if not Path(file_path).exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        try:
            # Detecta formato do CSV
            csv_format = self.detect_csv_format(file_path, encoding)
            column_mapping = csv_format['column_mapping']

            logger.info(
                f"Formato detectado - Delimitador: '{csv_format['delimiter']}', Colunas: {csv_format['headers']}")

            expenses = []

            with open(file_path, 'r', encoding=encoding, newline='') as file:
                reader = csv.reader(file, delimiter=csv_format['delimiter'])

                # Pula cabeçalho
                next(reader, None)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        expense = self._parse_row(row, column_mapping, row_num, len(expenses))
                        if expense:
                            expenses.append(expense)
                    except Exception as e:
                        logger.warning(f"Erro na linha {row_num}: {e}")
                        continue

            logger.info(f"Parse concluído. {len(expenses)} transações processadas.")

            return ParsedBankStatement(
                expenses=expenses,
                date=datetime.now()
            )

        except Exception as e:
            logger.error(f"Erro ao processar arquivo CSV: {e}")
            raise

    def _parse_row(self, row: List[str], column_mapping: Dict[str, int], row_num: int, id) -> Optional[Expense]:
        """Parse de uma linha do CSV"""
        if not row or len(row) < max(column_mapping.values(), default=0) + 1:
            return None

        # Extrai data
        date_col = column_mapping.get('date')
        if date_col is None or date_col >= len(row):
            logger.warning(f"Linha {row_num}: Coluna de data não encontrada")
            return None

        transaction_date = self.parse_date(row[date_col])
        if not transaction_date:
            logger.warning(f"Linha {row_num}: Data inválida")
            return None

        # Extrai descrição
        desc_col = column_mapping.get('description')
        if desc_col is None or desc_col >= len(row):
            name = f"Transação {row_num}"
        else:
            name = row[desc_col].strip()

        # Extrai valor (coluna única ou débito/crédito separados)
        value_col = column_mapping.get('value')
        if value_col is not None and value_col < len(row):
            # Valor em coluna única
            value = self.parse_value(row[value_col])
        else:
            # Verifica se tem débito e crédito separados
            debit_col = column_mapping.get('debit')
            credit_col = column_mapping.get('credit')

            if debit_col is None and credit_col is None:
                logger.warning(f"Linha {row_num}: Coluna de valor não encontrada")
                return None

            debit_value = 0.0
            credit_value = 0.0

            if debit_col is not None and debit_col < len(row) and row[debit_col].strip():
                debit_value = self.parse_value(row[debit_col])
                if debit_value > 0:  # Débito deve ser negativo
                    debit_value = -debit_value

            if credit_col is not None and credit_col < len(row) and row[credit_col].strip():
                credit_value = self.parse_value(row[credit_col])

            # Valor final é crédito - débito (considerando que débito já é negativo)
            value = credit_value + debit_value

        # Extrai categoria (opcional)
        category_col = column_mapping.get('category')
        if category_col is not None and category_col < len(row) and row[category_col].strip():
            category = row[category_col].strip()
        else:
            category = "Não categorizada"

        return Expense(
            id=id,
            name=name,
            value=value,
            category=category,
            date=transaction_date
        )


def parse_csv_bank_statement(file_path: str, encoding: str = 'utf-8-sig') -> ParsedBankStatement:
    """Função de conveniência para fazer parse de extrato bancário CSV"""
    parser = CSVBankParser()
    return parser.parse_file(file_path, encoding)
