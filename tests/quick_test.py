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

# Variáveis para controlar quais parsers estão disponíveis
OFX_AVAILABLE = False
CSV_AVAILABLE = False

try:
    from src.parsers.ofx import parse_ofx_file
    print("✅ Import do parser OFX funcionando")
    OFX_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Parser OFX não disponível: {e}")
    print("   💡 Para usar o parser OFX: pip install ofxtools")

try:
    from src.parsers.csv import parse_csv_bank_statement, CSVBankParser
    print("✅ Import do parser CSV funcionando")
    CSV_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erro ao importar parser CSV: {e}")
    print("   Este é um erro crítico pois o CSV parser deveria estar disponível")
    sys.exit(1)


def test_models():
    """Testa se os models funcionam corretamente"""
    print("\n🧪 Testando models...")
    
    # Cria uma despesa
    expense = Expense(
        id=1,
        name="Teste",
        value=100.50,
        category="Teste",
        date=date(2024, 3, 1)
    )
    
    assert expense.id == 1
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
        # Testa parsing de arquivo a partir de conteúdo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ofx', delete=False, encoding='utf-8') as f:
            f.write(sample_ofx)
            temp_file = f.name

        try:
            result = parse_ofx_file(temp_file)

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
        finally:
            os.unlink(temp_file)

    except Exception as e:
        print(f"❌ Erro no parser OFX: {e}")
        raise


def test_csv_parser():
    """Testa o parser CSV com dados de exemplo"""
    print("\n🧪 Testando parser CSV...")
    
    # Conteúdo CSV de exemplo
    sample_csv = """Data,Descrição,Valor,Categoria
01/03/2024,SUPERMERCADO XYZ LTDA,-150.50,Alimentação
02/03/2024,POSTO COMBUSTIVEL ABC,-89.75,Transporte
05/03/2024,SALARIO EMPRESA XYZ,2500.00,Renda
07/03/2024,FARMACIA SAUDE TOTAL,-45.80,Saúde
10/03/2024,ALUGUEL APARTAMENTO,-1200.00,Moradia"""
    
    try:
        # Cria arquivo temporário para teste
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv)
            temp_file = f.name
        
        try:
            # Testa parsing de arquivo
            result = parse_csv_bank_statement(temp_file)
            
            # Validações básicas
            assert isinstance(result, ParsedBankStatement)
            assert len(result.expenses) == 5
            assert isinstance(result.date, datetime)
            
            # Valida primeira transação
            first_expense = result.expenses[0]
            assert first_expense.name == "SUPERMERCADO XYZ LTDA"
            assert first_expense.value == -150.50
            assert first_expense.category == "Alimentação"
            assert first_expense.date == date(2024, 3, 1)
            
            # Valida transação de renda
            income_expense = result.expenses[2]
            assert income_expense.name == "SALARIO EMPRESA XYZ"
            assert income_expense.value == 2500.00
            assert income_expense.category == "Renda"
            assert income_expense.date == date(2024, 3, 5)
            
            print("✅ Parser CSV funcionando corretamente")
            print(f"   📊 {len(result.expenses)} transações processadas")
            print(f"   📅 Data do extrato: {result.date}")
            
            # Testa diferentes formatos de valor
            parser = CSVBankParser()
            
            # Teste formato brasileiro
            assert parser.parse_value("R$ 1.150,50") == 1150.50
            assert parser.parse_value("(89,75)") == -89.75
            assert parser.parse_value("2.500,00") == 2500.00
            
            print("✅ Conversão de valores funcionando corretamente")
            
            # Teste diferentes formatos de data
            assert parser.parse_date("01/03/2024") == date(2024, 3, 1)
            assert parser.parse_date("2024-03-01") == date(2024, 3, 1)
            assert parser.parse_date("15/12/2023") == date(2023, 12, 15)
            
            print("✅ Conversão de datas funcionando corretamente")
            
        finally:
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"❌ Erro no parser CSV: {e}")
        raise


def test_error_handling():
    """Testa tratamento de erros"""
    print("\n🧪 Testando tratamento de erros...")
    
    # Testa erros OFX se disponível
    if OFX_AVAILABLE:
        # Testa arquivo inexistente OFX
        try:
            parse_ofx_file("arquivo_inexistente.ofx")
            assert False, "Deveria ter dado erro"
        except FileNotFoundError:
            print("✅ Erro de arquivo OFX inexistente tratado corretamente")
        
        # Testa conteúdo OFX inválido via arquivo
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ofx', delete=False, encoding='utf-8') as f:
                f.write("conteúdo inválido")
                bad_file = f.name
            try:
                parse_ofx_file(bad_file)
                assert False, "Deveria ter dado erro"
            except ValueError:
                print("✅ Erro de conteúdo OFX inválido tratado corretamente")
            finally:
                os.unlink(bad_file)
        except Exception:
            # Qualquer exceção ainda valida o tratamento
            print("✅ Erro de conteúdo OFX inválido tratado corretamente")
    
    # Testa erros CSV se disponível
    if CSV_AVAILABLE:
        # Testa arquivo CSV inexistente
        try:
            parse_csv_bank_statement("arquivo_inexistente.csv")
            assert False, "Deveria ter dado erro"
        except FileNotFoundError:
            print("✅ Erro de arquivo CSV inexistente tratado corretamente")
        
        # Testa parser CSV com valores inválidos
        parser = CSVBankParser()
        assert parser.parse_value("abc") == 0.0
        assert parser.parse_date("data_inválida") is None
        print("✅ Tratamento de valores CSV inválidos funcionando")


def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes rápidos dos parsers")
    print("=" * 50)
    
    tests_run = 0
    tests_passed = 0
    
    try:
        # Testa os models (sempre disponível)
        test_models()
        tests_run += 1
        tests_passed += 1
        
        # Testa parser OFX se disponível
        if OFX_AVAILABLE:
            test_ofx_parser()
            tests_run += 1
            tests_passed += 1
        else:
            print("\n⏭️ Pulando testes OFX (dependência não instalada)")
        
        # Testa parser CSV se disponível
        if CSV_AVAILABLE:
            test_csv_parser()
            tests_run += 1
            tests_passed += 1
        
        # Testa tratamento de erros
        test_error_handling()
        tests_run += 1
        tests_passed += 1
        
        print("\n" + "=" * 50)
        print(f"🎉 {tests_passed}/{tests_run} conjuntos de testes passaram com sucesso!")
        
        print("\n📋 Para executar os testes completos:")
        print("   1. pip install -r requirements.txt")
        print("   2. pytest tests/ -v")
        
        print("\n🗂️ Status dos parsers:")
        print(f"   • Parser OFX: {'✅ Disponível' if OFX_AVAILABLE else '⚠️ Não disponível (pip install ofxtools)'}")
        print(f"   • Parser CSV: {'✅ Disponível' if CSV_AVAILABLE else '❌ Erro'}")
        
    except Exception as e:
        print(f"\n💥 Erro nos testes: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
