"""
Testes automatizados para o parser OFX
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

from src.parsers.ofx import parse_ofx_file, parse_ofx_content, _convert_transaction_to_expense
from src.parsers.models import ParsedBankStatement, Expense


class TestParseOFXFile:
    """Testes para a função parse_ofx_file"""
    
    def test_parse_valid_ofx_file(self, sample_ofx_file):
        """Testa parsing de arquivo OFX válido"""
        result = parse_ofx_file(sample_ofx_file)
        
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
        assert first_expense.value == -150.00
        assert first_expense.category == "Não categorizado"
        assert first_expense.date == date(2024, 3, 1)
        
        # Verifica transação de crédito
        credit_expense = result.expenses[2]
        assert credit_expense.name == "SALARIO EMPRESA XYZ"
        assert credit_expense.value == 2500.00
        assert credit_expense.date == date(2024, 3, 5)
    
    def test_parse_nonexistent_file(self):
        """Testa erro ao tentar ler arquivo inexistente"""
        with pytest.raises(FileNotFoundError):
            parse_ofx_file("arquivo_inexistente.ofx")
    
    def test_parse_invalid_ofx_file(self, invalid_ofx_content):
        """Testa erro ao ler arquivo OFX inválido"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ofx', delete=False) as f:
            f.write(invalid_ofx_content)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Erro ao processar arquivo OFX"):
                parse_ofx_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_parse_ofx_file_no_statements(self, ofx_content_no_statements):
        """Testa erro ao ler arquivo OFX sem extratos"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ofx', delete=False) as f:
            f.write(ofx_content_no_statements)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Nenhum extrato encontrado no arquivo OFX"):
                parse_ofx_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_parse_empty_transactions_file(self, empty_ofx_content):
        """Testa parsing de arquivo OFX sem transações"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ofx', delete=False) as f:
            f.write(empty_ofx_content)
            temp_file = f.name
        
        try:
            result = parse_ofx_file(temp_file)
            
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 0
            assert isinstance(result.date, datetime)
        finally:
            os.unlink(temp_file)


class TestParseOFXContent:
    """Testes para a função parse_ofx_content"""
    
    def test_parse_valid_ofx_content_string(self, sample_ofx_content):
        """Testa parsing de conteúdo OFX como string"""
        result = parse_ofx_content(sample_ofx_content)
        
        assert isinstance(result, ParsedBankStatement)
        assert len(result.expenses) == 5
        
        # Verifica detalhes das transações
        expenses = result.expenses
        assert expenses[0].name == "SUPERMERCADO XYZ LTDA"
        assert expenses[1].name == "POSTO COMBUSTIVEL ABC"
        assert expenses[2].name == "SALARIO EMPRESA XYZ"
        assert expenses[3].name == "FARMACIA SAUDE TOTAL"
        assert expenses[4].name == "ALUGUEL APARTAMENTO"
        
        # Verifica valores
        assert expenses[0].value == -150.00
        assert expenses[1].value == -89.50
        assert expenses[2].value == 2500.00
        assert expenses[3].value == -45.80
        assert expenses[4].value == -1200.00
    
    def test_parse_valid_ofx_content_bytes(self, sample_ofx_content):
        """Testa parsing de conteúdo OFX como bytes"""
        content_bytes = sample_ofx_content.encode('utf-8')
        result = parse_ofx_content(content_bytes)
        
        assert isinstance(result, ParsedBankStatement)
        assert len(result.expenses) == 5
    
    def test_parse_invalid_ofx_content(self, invalid_ofx_content):
        """Testa erro ao processar conteúdo OFX inválido"""
        with pytest.raises(ValueError, match="Erro ao processar conteúdo OFX"):
            parse_ofx_content(invalid_ofx_content)
    
    def test_parse_ofx_content_no_statements(self, ofx_content_no_statements):
        """Testa erro ao processar conteúdo OFX sem extratos"""
        with pytest.raises(ValueError, match="Nenhum extrato encontrado no conteúdo OFX"):
            parse_ofx_content(ofx_content_no_statements)
    
    def test_parse_empty_transactions_content(self, empty_ofx_content):
        """Testa parsing de conteúdo OFX sem transações"""
        result = parse_ofx_content(empty_ofx_content)
        
        assert isinstance(result, ParsedBankStatement)
        assert len(result.expenses) == 0
        assert isinstance(result.date, datetime)


class TestConvertTransactionToExpense:
    """Testes para a função _convert_transaction_to_expense"""
    
    def test_convert_transaction_with_memo(self):
        """Testa conversão de transação com memo"""
        from decimal import Decimal
        from unittest.mock import Mock
        
        # Mock de uma transação OFX
        transaction = Mock()
        transaction.memo = "TESTE MEMO"
        transaction.payee = "TESTE PAYEE"
        transaction.trnamt = Decimal('-100.50')
        transaction.dtposted = datetime(2024, 3, 1, 8, 0, 0)
        
        expense = _convert_transaction_to_expense(transaction)
        
        assert expense.name == "TESTE MEMO"  # Prioriza memo
        assert expense.value == -100.50
        assert expense.category == "Não categorizado"
        assert expense.date == date(2024, 3, 1)
    
    def test_convert_transaction_with_payee_only(self):
        """Testa conversão de transação apenas com payee"""
        from decimal import Decimal
        from unittest.mock import Mock
        
        transaction = Mock()
        transaction.memo = None
        transaction.payee = "TESTE PAYEE"
        transaction.trnamt = Decimal('500.00')
        transaction.dtposted = datetime(2024, 3, 5, 14, 0, 0)
        
        expense = _convert_transaction_to_expense(transaction)
        
        assert expense.name == "TESTE PAYEE"
        assert expense.value == 500.00
        assert expense.date == date(2024, 3, 5)
    
    def test_convert_transaction_without_description(self):
        """Testa conversão de transação sem descrição"""
        from decimal import Decimal
        from unittest.mock import Mock
        
        transaction = Mock()
        transaction.memo = None
        transaction.payee = None
        transaction.trnamt = Decimal('-25.75')
        transaction.dtposted = datetime(2024, 3, 10, 16, 30, 0)
        
        expense = _convert_transaction_to_expense(transaction)
        
        assert expense.name == "Transação sem descrição"
        assert expense.value == -25.75
        assert expense.date == date(2024, 3, 10)
    
    def test_convert_transaction_without_amount(self):
        """Testa conversão de transação sem valor"""
        from unittest.mock import Mock
        
        transaction = Mock()
        transaction.memo = "TESTE SEM VALOR"
        transaction.payee = None
        transaction.trnamt = None
        transaction.dtposted = datetime(2024, 3, 1, 8, 0, 0)
        
        expense = _convert_transaction_to_expense(transaction)
        
        assert expense.name == "TESTE SEM VALOR"
        assert expense.value == 0.0
        assert expense.date == date(2024, 3, 1)
    
    def test_convert_transaction_without_date(self):
        """Testa conversão de transação sem data (usa data atual)"""
        from decimal import Decimal
        from unittest.mock import Mock
        
        transaction = Mock()
        transaction.memo = "TESTE SEM DATA"
        transaction.trnamt = Decimal('-50.00')
        transaction.dtposted = None
        
        expense = _convert_transaction_to_expense(transaction)
        
        assert expense.name == "TESTE SEM DATA"
        assert expense.value == -50.00
        assert expense.date == datetime.now().date()


class TestIntegration:
    """Testes de integração para casos mais complexos"""
    
    def test_complete_workflow_file_to_expenses(self, sample_ofx_file):
        """Testa o fluxo completo de arquivo para lista de despesas"""
        result = parse_ofx_file(sample_ofx_file)
        
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
    
class TestConvertTransactionToExpense:
    """Testes para a função _convert_transaction_to_expense"""
    
    def test_convert_transaction_with_memo(self):
        """Testa conversão de transação com memo"""
        from decimal import Decimal
        from unittest.mock import Mock
        
        # Mock de uma transação OFX
        transaction = Mock()
        transaction.memo = "TESTE MEMO"
        transaction.payee = "TESTE PAYEE"
        transaction.trnamt = Decimal('-100.50')
        transaction.dtposted = datetime(2024, 3, 1, 8, 0, 0)
        
        expense = _convert_transaction_to_expense(transaction)
        
        assert expense.name == "TESTE MEMO"  # Prioriza memo
        assert expense.value == -100.50
        assert expense.category == "Não categorizado"
        assert expense.date == date(2024, 3, 1)
    
    def test_convert_transaction_with_payee_only(self):
        """Testa conversão de transação apenas com payee"""
        from decimal import Decimal
        from unittest.mock import Mock
        
        transaction = Mock()
        transaction.memo = None
        transaction.payee = "TESTE PAYEE"
        transaction.trnamt = Decimal('500.00')
        transaction.dtposted = datetime(2024, 3, 5, 14, 0, 0)
        
        expense = _convert_transaction_to_expense(transaction)
        
        assert expense.name == "TESTE PAYEE"
        assert expense.value == 500.00
        assert expense.date == date(2024, 3, 5)


class TestIntegration:
    """Testes de integração para casos mais complexos"""
    
    def test_complete_workflow_file_to_expenses(self, sample_ofx_file):
        """Testa o fluxo completo de arquivo para lista de despesas"""
        result = parse_ofx_file(sample_ofx_file)
        
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
    
    def test_ofx_with_special_characters(self):
        """Testa OFX com caracteres especiais"""
        ofx_with_special_chars = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<SIGNONMSGSRSV1>
<SONRS>
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<DTSERVER>20240315120000
<LANGUAGE>POR
</SONRS>
</SIGNONMSGSRSV1>
<BANKMSGSRSV1>
<STMTTRNRS>
<TRNUID>1
<STATUS>
<CODE>0
<SEVERITY>INFO
</STATUS>
<STMTRS>
<CURDEF>BRL
<BANKACCTFROM>
<BANKID>123
<ACCTID>123456789
<ACCTTYPE>CHECKING
</BANKACCTFROM>
<BANKTRANLIST>
<DTSTART>20240301000000
<DTEND>20240315000000
<STMTTRN>
<TRNTYPE>DEBIT
<DTPOSTED>20240301080000
<TRNAMT>-150.00
<FITID>TRN001
<MEMO>AÇOUGUE & CIA LTDA - JOÃO
</STMTTRN>
</BANKTRANLIST>
<LEDGERBAL>
<BALAMT>850.00
<DTASOF>20240315120000
</LEDGERBAL>
</STMTRS>
</STMTRS>
</BANKMSGSRSV1>
</OFX>"""
        
        result = parse_ofx_content(ofx_with_special_chars)
        
        assert len(result.expenses) == 1
        # Testa se contém o texto independente do encoding
        name = result.expenses[0].name
        assert "OUGUE" in name and "CIA" in name and "LTDA" in name


class TestErrorHandling:
    """Testes específicos para tratamento de erros"""
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_file_permission_error(self, mock_file):
        """Testa erro de permissão ao ler arquivo"""
        with pytest.raises(ValueError, match="Erro ao processar arquivo OFX"):
            parse_ofx_file("test_file.ofx")
    
    def test_corrupted_ofx_content(self):
        """Testa conteúdo OFX corrompido"""
        corrupted_content = """OFXHEADER:100
<OFX>
<BANKMSGSRSV1>
<STMTTRNRS>
<STMTRS>
<BANKTRANLIST>
<STMTTRN>
<MEMO>TRANSACAO INCOMPLETA
</BANKTRANLIST>
</OFX>"""
        
        with pytest.raises(ValueError):
            parse_ofx_content(corrupted_content)

