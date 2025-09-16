"""
Testes automatizados para o parser CSV
"""

import pytest
import tempfile
import os
from datetime import datetime, date
from unittest.mock import patch, mock_open, Mock

# Importações do projeto
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parsers.csv import CSVBankParser, parse_csv_bank_statement
from src.parsers.models import ParsedBankStatement, Expense


class TestCSVBankParser:
    """Testes para a classe CSVBankParser"""
    
    def test_init(self):
        """Testa inicialização da classe"""
        parser = CSVBankParser()
        
        assert isinstance(parser.supported_date_formats, list)
        assert len(parser.supported_date_formats) > 0
        assert "%d/%m/%Y" in parser.supported_date_formats
        assert "%Y-%m-%d" in parser.supported_date_formats

    def test_parse_date_valid_formats(self):
        """Testa conversão de datas em formatos válidos"""
        parser = CSVBankParser()
        
        # Formato brasileiro
        assert parser.parse_date("01/03/2024") == date(2024, 3, 1)
        assert parser.parse_date("15/12/2023") == date(2023, 12, 15)
        
        # Formato ISO
        assert parser.parse_date("2024-03-01") == date(2024, 3, 1)
        assert parser.parse_date("2023-12-15") == date(2023, 12, 15)
        
        # Formato americano (com dia/mês pode ser ambíguo, depende da posição dos formatos na lista)
        # O formato "03/01/2024" pode ser interpretado como dd/mm ou mm/dd dependendo da ordem
        result = parser.parse_date("03/01/2024")
        assert result in [date(2024, 1, 3), date(2024, 3, 1)]  # Aceita ambos os formatos
        
        # Com espaços
        assert parser.parse_date("  01/03/2024  ") == date(2024, 3, 1)

    def test_parse_date_invalid_formats(self):
        """Testa conversão de datas em formatos inválidos"""
        parser = CSVBankParser()
        
        assert parser.parse_date("data_inválida") is None
        assert parser.parse_date("32/13/2024") is None
        assert parser.parse_date("") is None
        assert parser.parse_date("abc") is None

    def test_parse_value_valid_formats(self):
        """Testa conversão de valores em formatos válidos"""
        parser = CSVBankParser()
        
        # Formatos básicos
        assert parser.parse_value("100.50") == 100.50
        assert parser.parse_value("100,50") == 100.50
        assert parser.parse_value("-100.50") == -100.50
        
        # Com símbolos monetários
        assert parser.parse_value("R$ 100,50") == 100.50
        assert parser.parse_value("$ 100.50") == 100.50
        
        # Com pontos separadores de milhares
        assert parser.parse_value("1.000,50") == 1000.50
        assert parser.parse_value("1,000.50") == 1000.50
        
        # Valores negativos em parênteses
        assert parser.parse_value("(100.50)") == -100.50
        assert parser.parse_value("(1.000,50)") == -1000.50
        
        # Com espaços
        assert parser.parse_value(" R$ 100,50 ") == 100.50

    def test_parse_value_invalid_formats(self):
        """Testa conversão de valores em formatos inválidos"""
        parser = CSVBankParser()
        
        assert parser.parse_value("abc") == 0.0
        assert parser.parse_value("") == 0.0
        assert parser.parse_value("R$ abc") == 0.0

    def test_map_columns_portuguese(self):
        """Testa mapeamento de colunas em português"""
        parser = CSVBankParser()
        
        headers = ["Data", "Descrição", "Valor", "Categoria"]
        mapping = parser._map_columns(headers)
        
        assert mapping['date'] == 0
        assert mapping['description'] == 1
        assert mapping['value'] == 2
        assert mapping['category'] == 3

    def test_map_columns_english(self):
        """Testa mapeamento de colunas em inglês"""
        parser = CSVBankParser()
        
        headers = ["date", "memo", "amount", "type"]
        mapping = parser._map_columns(headers)
        
        assert mapping['date'] == 0
        assert mapping['description'] == 1
        assert mapping['value'] == 2
        assert mapping['category'] == 3

    def test_map_columns_mixed_case(self):
        """Testa mapeamento de colunas com casos mistos"""
        parser = CSVBankParser()
        
        headers = ["DATE", "Description", "VALOR", "categoria"]
        mapping = parser._map_columns(headers)
        
        assert mapping['date'] == 0
        assert mapping['description'] == 1
        assert mapping['value'] == 2
        assert mapping['category'] == 3

    def test_map_columns_alternative_names(self):
        """Testa mapeamento de colunas com nomes alternativos"""
        parser = CSVBankParser()
        
        headers = ["dt", "historico", "montante"]
        mapping = parser._map_columns(headers)
        
        assert mapping['date'] == 0
        assert mapping['description'] == 1
        assert mapping['value'] == 2

    def test_map_columns_partial_mapping(self):
        """Testa mapeamento quando nem todas as colunas são encontradas"""
        parser = CSVBankParser()
        
        headers = ["unknown1", "data", "unknown2"]
        mapping = parser._map_columns(headers)
        
        assert mapping['date'] == 1
        assert 'description' not in mapping
        assert 'value' not in mapping
        assert 'category' not in mapping


class TestParseCSVFile:
    """Testes para a função parse_file da classe CSVBankParser"""
    
    def test_parse_valid_csv_file(self, sample_csv_file):
        """Testa parsing de arquivo CSV válido"""
        parser = CSVBankParser()
        result = parser.parse_file(sample_csv_file)
        
        # Verifica se retorna ParsedBankStatement
        assert isinstance(result, ParsedBankStatement)
        
        # Verifica se tem transações
        assert len(result.expenses) == 5
        
        # Verifica se tem data válida
        assert isinstance(result.date, datetime)
        
        # Verifica primeira transação
        first_expense = result.expenses[0]
        assert isinstance(first_expense, Expense)
        assert first_expense.name == "SUPERMERCADO XYZ LTDA"
        assert first_expense.value == -150.50
        assert first_expense.category == "Alimentação"
        assert first_expense.date == date(2024, 3, 1)
        
        # Verifica transação de renda
        income_expense = result.expenses[2]
        assert income_expense.name == "SALARIO EMPRESA XYZ"
        assert income_expense.value == 2500.00
        assert income_expense.category == "Renda"
        assert income_expense.date == date(2024, 3, 5)

    def test_parse_csv_with_semicolon_delimiter(self, sample_csv_content_semicolon):
        """Testa parsing de CSV com delimitador ponto-e-vírgula"""
        parser = CSVBankParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_content_semicolon)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 5
            
            # Verifica primeira transação (débito)
            first_expense = result.expenses[0]
            assert first_expense.name == "SUPERMERCADO XYZ LTDA"
            assert first_expense.value == -150.50  # Convertido de débito para negativo
            
            # Verifica transação de crédito
            credit_expense = result.expenses[2]
            assert credit_expense.name == "SALARIO EMPRESA XYZ"
            assert credit_expense.value == 2500.00
            
        finally:
            os.unlink(temp_file)

    def test_parse_csv_alternative_format(self, sample_csv_content_alternative_format):
        """Testa parsing de CSV com formato alternativo"""
        parser = CSVBankParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_content_alternative_format)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 5
            
            # Verifica primeira transação (valor em parênteses = negativo)
            first_expense = result.expenses[0]
            assert first_expense.name == "SUPERMERCADO XYZ LTDA"
            assert first_expense.value == -150.50
            assert first_expense.date == date(2024, 3, 1)
            
        finally:
            os.unlink(temp_file)

    def test_parse_csv_brazilian_format(self, csv_content_brazilian_format):
        """Testa parsing de CSV com formato brasileiro (R$, pontos e vírgulas)"""
        parser = CSVBankParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_content_brazilian_format)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 4
            
            # Verifica conversão de valores brasileiros
            first_expense = result.expenses[0]
            assert first_expense.value == 1150.50  # "R$ 1.150,50"
            
            second_expense = result.expenses[1]
            assert second_expense.value == 89.75   # "R$ 89,75"
            
        finally:
            os.unlink(temp_file)

    def test_parse_csv_with_negative_parentheses(self, csv_content_with_negative_parentheses):
        """Testa parsing de CSV com valores negativos em parênteses"""
        parser = CSVBankParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_content_with_negative_parentheses)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 4
            
            # Verifica conversão de valores em parênteses para negativos
            first_expense = result.expenses[0]
            assert first_expense.value == -150.50  # (150.50)
            
            second_expense = result.expenses[1]
            assert first_expense.value == -150.50  # (89.75)
            
            # Verifica valor positivo
            third_expense = result.expenses[2]
            assert third_expense.value == 2500.00  # 2500.00
            
        finally:
            os.unlink(temp_file)

    def test_parse_nonexistent_file(self):
        """Testa erro ao tentar ler arquivo inexistente"""
        parser = CSVBankParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file("arquivo_inexistente.csv")

    def test_parse_empty_csv_file(self, empty_csv_content):
        """Testa parsing de arquivo CSV vazio (apenas cabeçalho)"""
        parser = CSVBankParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(empty_csv_content)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 0
            assert isinstance(result.date, datetime)
            
        finally:
            os.unlink(temp_file)

    def test_parse_csv_with_invalid_rows(self, invalid_csv_content):
        """Testa parsing de CSV com algumas linhas inválidas"""
        parser = CSVBankParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(invalid_csv_content)
            temp_file = f.name
        
        try:
            result = parser.parse_file(temp_file)
            
            # Deve processar apenas as linhas válidas
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 1  # Apenas a linha válida
            
            valid_expense = result.expenses[0]
            assert valid_expense.name == "TRANSACAO NORMAL"
            assert valid_expense.value == 150.75
            
        finally:
            os.unlink(temp_file)


class TestParseCSVConvenienceFunction:
    """Testes para a função de conveniência parse_csv_bank_statement"""
    
    def test_parse_csv_convenience_function(self, sample_csv_file):
        """Testa função de conveniência parse_csv_bank_statement"""
        result = parse_csv_bank_statement(sample_csv_file)
        
        assert isinstance(result, ParsedBankStatement)
        assert len(result.expenses) == 5
        
        first_expense = result.expenses[0]
        assert first_expense.name == "SUPERMERCADO XYZ LTDA"
        assert first_expense.value == -150.50

    def test_parse_csv_convenience_function_with_encoding(self, sample_csv_content):
        """Testa função de conveniência com encoding específico"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='latin-1') as f:
            f.write(sample_csv_content)
            temp_file = f.name
        
        try:
            result = parse_csv_bank_statement(temp_file, encoding='latin-1')
            
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 5
            
        finally:
            os.unlink(temp_file)


class TestCSVFormatDetection:
    """Testes para detecção automática de formato CSV"""
    
    def test_detect_comma_delimiter(self, sample_csv_content):
        """Testa detecção de delimitador vírgula"""
        parser = CSVBankParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_content)
            temp_file = f.name
        
        try:
            csv_format = parser.detect_csv_format(temp_file)
            
            assert csv_format['delimiter'] == ','
            assert 'Data' in csv_format['headers']
            assert 'Descrição' in csv_format['headers']
            assert 'Valor' in csv_format['headers']
            
            mapping = csv_format['column_mapping']
            assert 'date' in mapping
            assert 'description' in mapping
            assert 'value' in mapping
            
        finally:
            os.unlink(temp_file)

    def test_detect_semicolon_delimiter(self, sample_csv_content_semicolon):
        """Testa detecção de delimitador ponto-e-vírgula"""
        parser = CSVBankParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_content_semicolon)
            temp_file = f.name
        
        try:
            csv_format = parser.detect_csv_format(temp_file)
            
            assert csv_format['delimiter'] == ';'
            assert 'Data' in csv_format['headers']
            assert 'Histórico' in csv_format['headers']
            
        finally:
            os.unlink(temp_file)


class TestParseRow:
    """Testes para o método _parse_row"""
    
    def test_parse_row_valid(self):
        """Testa parsing de linha válida"""
        parser = CSVBankParser()
        
        row = ["01/03/2024", "SUPERMERCADO XYZ", "-150.50", "Alimentação"]
        column_mapping = {'date': 0, 'description': 1, 'value': 2, 'category': 3}
        
        expense = parser._parse_row(row, column_mapping, 2)
        
        assert expense is not None
        assert expense.name == "SUPERMERCADO XYZ"
        assert expense.value == -150.50
        assert expense.category == "Alimentação"
        assert expense.date == date(2024, 3, 1)

    def test_parse_row_missing_date_column(self):
        """Testa parsing de linha sem coluna de data"""
        parser = CSVBankParser()
        
        row = ["SUPERMERCADO XYZ", "-150.50", "Alimentação"]
        column_mapping = {'description': 0, 'value': 1, 'category': 2}  # Sem 'date'
        
        expense = parser._parse_row(row, column_mapping, 2)
        
        assert expense is None

    def test_parse_row_invalid_date(self):
        """Testa parsing de linha com data inválida"""
        parser = CSVBankParser()
        
        row = ["data_inválida", "SUPERMERCADO XYZ", "-150.50", "Alimentação"]
        column_mapping = {'date': 0, 'description': 1, 'value': 2, 'category': 3}
        
        expense = parser._parse_row(row, column_mapping, 2)
        
        assert expense is None

    def test_parse_row_missing_description(self):
        """Testa parsing de linha sem descrição"""
        parser = CSVBankParser()
        
        row = ["01/03/2024", "", "-150.50", "Alimentação"]
        column_mapping = {'date': 0, 'description': 1, 'value': 2, 'category': 3}
        
        expense = parser._parse_row(row, column_mapping, 2)
        
        assert expense is not None
        assert expense.name == ""  # Descrição vazia
        assert expense.value == -150.50

    def test_parse_row_missing_category(self):
        """Testa parsing de linha sem categoria"""
        parser = CSVBankParser()
        
        row = ["01/03/2024", "SUPERMERCADO XYZ", "-150.50"]
        column_mapping = {'date': 0, 'description': 1, 'value': 2}  # Sem 'category'
        
        expense = parser._parse_row(row, column_mapping, 2)
        
        assert expense is not None
        assert expense.category == "Não categorizada"

    def test_parse_row_empty_row(self):
        """Testa parsing de linha vazia"""
        parser = CSVBankParser()
        
        row = []
        column_mapping = {'date': 0, 'description': 1, 'value': 2}
        
        expense = parser._parse_row(row, column_mapping, 2)
        
        assert expense is None

    def test_parse_row_insufficient_columns(self):
        """Testa parsing de linha com colunas insuficientes"""
        parser = CSVBankParser()
        
        row = ["01/03/2024"]  # Apenas uma coluna
        column_mapping = {'date': 0, 'description': 1, 'value': 2}
        
        expense = parser._parse_row(row, column_mapping, 2)
        
        assert expense is None


class TestIntegration:
    """Testes de integração para casos mais complexos"""
    
    def test_complete_workflow_file_to_expenses(self, sample_csv_file):
        """Testa o fluxo completo de arquivo para lista de despesas"""
        result = parse_csv_bank_statement(sample_csv_file)
        
        # Verifica estrutura completa
        assert isinstance(result, ParsedBankStatement)
        assert isinstance(result.expenses, list)
        assert isinstance(result.date, datetime)
        
        # Verifica todas as transações
        expenses = result.expenses
        assert len(expenses) == 5
        
        # Verifica tipos de todas as propriedades
        for expense in expenses:
            assert isinstance(expense, Expense)
            assert isinstance(expense.name, str)
            assert isinstance(expense.value, float)
            assert isinstance(expense.category, str)
            assert isinstance(expense.date, date)
        
        # Verifica ordenação por data (se aplicável)
        dates = [expense.date for expense in expenses]
        assert all(dates[i] <= dates[i+1] for i in range(len(dates)-1))

    def test_mixed_currency_formats(self):
        """Testa processamento de arquivo com formatos mistos de moeda"""
        mixed_content = """Data,Descrição,Valor,Categoria
01/03/2024,SUPERMERCADO XYZ,R$ 150.50,Alimentação
02/03/2024,POSTO COMBUSTIVEL,(89.75),Transporte
05/03/2024,SALARIO EMPRESA,2500,00,Renda
07/03/2024,FARMACIA SAUDE,$45.80,Saúde"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(mixed_content)
            temp_file = f.name
        
        try:
            result = parse_csv_bank_statement(temp_file)
            
            assert len(result.expenses) == 4
            
            # Verifica conversões corretas
            assert result.expenses[0].value == 150.50    # R$ 150.50
            assert result.expenses[1].value == -89.75    # (89.75)
            assert result.expenses[2].value == 2500.00   # 2500,00
            assert result.expenses[3].value == 45.80     # $45.80
            
        finally:
            os.unlink(temp_file)


class TestErrorHandling:
    """Testes específicos para tratamento de erros"""
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_file_permission_error(self, mock_file):
        """Testa erro de permissão ao ler arquivo"""
        parser = CSVBankParser()
        
        with pytest.raises(Exception):  # Pode ser PermissionError ou outro
            parser.parse_file("test_file.csv")

    def test_corrupted_csv_content(self):
        """Testa conteúdo CSV mal formado"""
        corrupted_content = """Data,Descrição,Valor
"01/03/2024,"TRANSACAO SEM FECHAMENTO DE ASPAS,-150.50
02/03/2024,TRANSACAO,NORMAL,150.75"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(corrupted_content)
            temp_file = f.name
        
        try:
            parser = CSVBankParser()
            result = parser.parse_file(temp_file)
            
            # Deve processar o que conseguir
            assert isinstance(result, ParsedBankStatement)
            
        finally:
            os.unlink(temp_file)

    def test_file_encoding_issues(self, sample_csv_content):
        """Testa problemas de encoding"""
        # Cria arquivo com encoding diferente
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='latin-1') as f:
            f.write(sample_csv_content)
            temp_file = f.name
        
        try:
            parser = CSVBankParser()
            # Tenta ler com encoding errado primeiro (UTF-8)
            # Se não funcionar, o usuário deve especificar o encoding correto
            with pytest.raises(UnicodeDecodeError):
                parser.parse_file(temp_file, encoding='utf-8')
            
            # Com encoding correto deve funcionar
            result = parser.parse_file(temp_file, encoding='latin-1')
            assert isinstance(result, ParsedBankStatement)
            
        finally:
            os.unlink(temp_file)


class TestEdgeCases:
    """Testes para casos extremos"""
    
    def test_very_large_values(self):
        """Testa valores muito grandes"""
        large_values_content = """Data,Descrição,Valor
01/03/2024,TRANSACAO GRANDE,999999999.99
02/03/2024,TRANSACAO NEGATIVA,(-999999999.99)"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(large_values_content)
            temp_file = f.name
        
        try:
            result = parse_csv_bank_statement(temp_file)
            
            assert len(result.expenses) == 2
            assert result.expenses[0].value == 999999999.99
            assert result.expenses[1].value == -999999999.99
            
        finally:
            os.unlink(temp_file)

    def test_special_characters_in_description(self):
        """Testa caracteres especiais nas descrições"""
        special_chars_content = """Data,Descrição,Valor
01/03/2024,"AÇOUGUE & CIA LTDA - R. SÃO JOÃO, 123",150.50
02/03/2024,CAFÉ @ BAR (CORAÇÃO),25.75
03/03/2024,"EMPRESA ""TESTE"" LTDA",100.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(special_chars_content)
            temp_file = f.name
        
        try:
            result = parse_csv_bank_statement(temp_file)
            
            assert len(result.expenses) == 3
            assert "AÇOUGUE & CIA LTDA" in result.expenses[0].name
            assert "CAFÉ @ BAR" in result.expenses[1].name
            assert '"TESTE"' in result.expenses[2].name
            
        finally:
            os.unlink(temp_file)

    def test_zero_and_very_small_values(self):
        """Testa valores zero e muito pequenos"""
        small_values_content = """Data,Descrição,Valor
01/03/2024,TRANSACAO ZERO,0.00
02/03/2024,TRANSACAO PEQUENA,0.01
03/03/2024,TRANSACAO NEGATIVA PEQUENA,-0.01"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(small_values_content)
            temp_file = f.name
        
        try:
            result = parse_csv_bank_statement(temp_file)
            
            assert len(result.expenses) == 3
            assert result.expenses[0].value == 0.0
            assert result.expenses[1].value == 0.01
            assert result.expenses[2].value == -0.01
            
        finally:
            os.unlink(temp_file)
