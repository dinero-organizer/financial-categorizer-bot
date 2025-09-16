#!/usr/bin/env python
"""
Teste rápido e simples para validar o parser OFX sem dependências externas complexas
"""

import sys
import os
import tempfile
from datetime import datetime, date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.parsers.models import ParsedBankStatement, Expense
    print("✅ Import dos models funcionando")
except ImportError as e:
    print(f"❌ Erro ao importar models: {e}")
    sys.exit(1)

try:
    from src.parsers.ofx import parse_ofx_content, parse_ofx_file
    print("✅ Import do parser OFX funcionando")
except ImportError as e:
    print(f"❌ Erro ao importar parser OFX: {e}")
    print("⚠️  Certifique-se de que 'ofxtools' está instalado: pip install ofxtools")
    sys.exit(1)


def test_models():
    """Testa se os models funcionam corretamente"""
    print("\n🧪 Testando models...")
    
    # Cria uma despesa
    expense = Expense(
        name="Teste",
        value=100.50,
        category="Teste",
        date=date(2024, 3, 1)
    )
    
    assert expense.name == "Teste"
    assert expense.value == 100.50
    assert expense.category == "Teste"
    assert expense.date == date(2024, 3, 1)
    
    # Cria um extrato
    statement = ParsedBankStatement(
        expenses=[expense],
        date=datetime(2024, 3, 1, 12, 0, 0)
    )
    
    assert len(statement.expenses) == 1
    assert statement.expenses[0] == expense
    assert statement.date == datetime(2024, 3, 1, 12, 0, 0)
    
    print("✅ Models funcionando corretamente")


def test_ofx_parser():
    """Testa o parser OFX com dados de exemplo"""
    print("\n🧪 Testando parser OFX...")
    
    # Conteúdo OFX de exemplo
    sample_ofx = """OFXHEADER:100
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
<MEMO>SUPERMERCADO XYZ LTDA
</STMTTRN>
<STMTTRN>
<TRNTYPE>CREDIT
<DTPOSTED>20240305140000
<TRNAMT>2500.00
<FITID>TRN002
<MEMO>SALARIO EMPRESA XYZ
</STMTTRN>
</BANKTRANLIST>
<LEDGERBAL>
<BALAMT>2350.00
<DTASOF>20240315120000
</LEDGERBAL>
</STMTRS>
</STMTRS>
</BANKMSGSRSV1>
</OFX>"""
    
    try:
        # Testa parsing de conteúdo
        result = parse_ofx_content(sample_ofx)
        
        # Validações básicas
        assert isinstance(result, ParsedBankStatement)
        assert len(result.expenses) == 2
        assert isinstance(result.date, datetime)
        
        # Valida primeira transação
        first_expense = result.expenses[0]
        assert first_expense.name == "SUPERMERCADO XYZ LTDA"
        assert first_expense.value == -150.00
        assert first_expense.category == "Não categorizado"
        assert first_expense.date == date(2024, 3, 1)
        
        # Valida segunda transação
        second_expense = result.expenses[1]
        assert second_expense.name == "SALARIO EMPRESA XYZ"
        assert second_expense.value == 2500.00
        assert second_expense.date == date(2024, 3, 5)
        
        print("✅ Parser OFX funcionando corretamente")
        print(f"   📊 {len(result.expenses)} transações processadas")
        print(f"   📅 Data do extrato: {result.date}")
        
        # Testa parsing de arquivo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ofx', delete=False, encoding='utf-8') as f:
            f.write(sample_ofx)
            temp_file = f.name
        
        try:
            file_result = parse_ofx_file(temp_file)
            assert len(file_result.expenses) == 2
            print("✅ Parsing de arquivo OFX funcionando")
        finally:
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"❌ Erro no parser OFX: {e}")
        raise


def test_error_handling():
    """Testa tratamento de erros"""
    print("\n🧪 Testando tratamento de erros...")
    
    # Testa arquivo inexistente
    try:
        parse_ofx_file("arquivo_inexistente.ofx")
        assert False, "Deveria ter dado erro"
    except FileNotFoundError:
        print("✅ Erro de arquivo inexistente tratado corretamente")
    
    # Testa conteúdo inválido
    try:
        parse_ofx_content("conteúdo inválido")
        assert False, "Deveria ter dado erro"
    except ValueError:
        print("✅ Erro de conteúdo inválido tratado corretamente")


def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes rápidos do parser OFX")
    print("=" * 50)
    
    try:
        test_models()
        test_ofx_parser()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 Todos os testes passaram com sucesso!")
        print("\n📋 Para executar os testes completos:")
        print("   1. pip install -r requirements.txt")
        print("   2. pytest tests/ -v")
        
    except Exception as e:
        print(f"\n💥 Erro nos testes: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
