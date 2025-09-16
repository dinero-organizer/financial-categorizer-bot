"""
Configurações e fixtures compartilhadas para os testes
"""

import pytest
import tempfile
import os
from datetime import datetime, date
from decimal import Decimal


@pytest.fixture
def sample_ofx_content():
    """
    Fixture que retorna conteúdo OFX de exemplo para testes
    """
    return """OFXHEADER:100
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
<TRNTYPE>DEBIT
<DTPOSTED>20240302100000
<TRNAMT>-89.50
<FITID>TRN002
<MEMO>POSTO COMBUSTIVEL ABC
</STMTTRN>
<STMTTRN>
<TRNTYPE>CREDIT
<DTPOSTED>20240305140000
<TRNAMT>2500.00
<FITID>TRN003
<MEMO>SALARIO EMPRESA XYZ
</STMTTRN>
<STMTTRN>
<TRNTYPE>DEBIT
<DTPOSTED>20240307090000
<TRNAMT>-45.80
<FITID>TRN004
<MEMO>FARMACIA SAUDE TOTAL
</STMTTRN>
<STMTTRN>
<TRNTYPE>DEBIT
<DTPOSTED>20240310160000
<TRNAMT>-1200.00
<FITID>TRN005
<MEMO>ALUGUEL APARTAMENTO
</STMTTRN>
</BANKTRANLIST>
<LEDGERBAL>
<BALAMT>1014.70
<DTASOF>20240315120000
</LEDGERBAL>
</STMTRS>
</STMTRS>
</BANKMSGSRSV1>
</OFX>"""


@pytest.fixture
def sample_ofx_file(sample_ofx_content):
    """
    Fixture que cria um arquivo OFX temporário para testes
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ofx', delete=False, encoding='utf-8') as f:
        f.write(sample_ofx_content)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup: remove o arquivo temporário após o teste
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def empty_ofx_content():
    """
    Fixture que retorna conteúdo OFX sem transações para testes
    """
    return """OFXHEADER:100
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
</BANKTRANLIST>
<LEDGERBAL>
<BALAMT>1000.00
<DTASOF>20240315120000
</LEDGERBAL>
</STMTRS>
</STMTRS>
</BANKMSGSRSV1>
</OFX>"""


@pytest.fixture
def invalid_ofx_content():
    """
    Fixture que retorna conteúdo OFX inválido para testes de erro
    """
    return """INVALID OFX CONTENT
This is not a valid OFX file format
<INVALID>
<TAGS>
</INVALID>"""


@pytest.fixture
def ofx_content_no_statements():
    """
    Fixture que retorna conteúdo OFX válido mas sem extratos
    """
    return """OFXHEADER:100
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
</OFX>"""


# === FIXTURES PARA TESTES CSV ===

@pytest.fixture
def sample_csv_content():
    """
    Fixture que retorna conteúdo CSV de exemplo para testes
    """
    return """Data,Descrição,Valor,Categoria
01/03/2024,SUPERMERCADO XYZ LTDA,-150.50,Alimentação
02/03/2024,POSTO COMBUSTIVEL ABC,-89.75,Transporte
05/03/2024,SALARIO EMPRESA XYZ,2500.00,Renda
07/03/2024,FARMACIA SAUDE TOTAL,-45.80,Saúde
10/03/2024,ALUGUEL APARTAMENTO,-1200.00,Moradia"""


@pytest.fixture
def sample_csv_content_semicolon():
    """
    Fixture que retorna conteúdo CSV com delimitador ponto-e-vírgula
    """
    return """Data;Histórico;Débito;Crédito
01/03/2024;SUPERMERCADO XYZ LTDA;150,50;
02/03/2024;POSTO COMBUSTIVEL ABC;89,75;
05/03/2024;SALARIO EMPRESA XYZ;;2.500,00
07/03/2024;FARMACIA SAUDE TOTAL;45,80;
10/03/2024;ALUGUEL APARTAMENTO;1.200,00;"""


@pytest.fixture
def sample_csv_content_alternative_format():
    """
    Fixture que retorna conteúdo CSV com formato alternativo
    """
    return """date,memo,amount,type
2024-03-01,SUPERMERCADO XYZ LTDA,(150.50),expense
2024-03-02,POSTO COMBUSTIVEL ABC,(89.75),expense
2024-03-05,SALARIO EMPRESA XYZ,2500.00,income
2024-03-07,FARMACIA SAUDE TOTAL,(45.80),expense
2024-03-10,ALUGUEL APARTAMENTO,(1200.00),expense"""


@pytest.fixture
def sample_csv_file(sample_csv_content):
    """
    Fixture que cria um arquivo CSV temporário para testes
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(sample_csv_content)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup: remove o arquivo temporário após o teste
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def invalid_csv_content():
    """
    Fixture que retorna conteúdo CSV inválido para testes de erro
    """
    return """Data,Descrição,Valor
01/03/2024,TRANSACAO SEM VALOR
data_inválida,TRANSACAO COM DATA INVÁLIDA,100.50
01/03/2024,TRANSACAO NORMAL,150.75"""


@pytest.fixture
def empty_csv_content():
    """
    Fixture que retorna conteúdo CSV vazio (apenas cabeçalho)
    """
    return """Data,Descrição,Valor,Categoria"""


@pytest.fixture
def csv_content_no_header():
    """
    Fixture que retorna conteúdo CSV sem cabeçalho
    """
    return """01/03/2024,SUPERMERCADO XYZ LTDA,-150.50,Alimentação
02/03/2024,POSTO COMBUSTIVEL ABC,-89.75,Transporte
05/03/2024,SALARIO EMPRESA XYZ,2500.00,Renda"""


@pytest.fixture
def csv_content_brazilian_format():
    """
    Fixture que retorna conteúdo CSV com formato brasileiro (R$, pontos e vírgulas)
    """
    return """Data,Descrição,Valor,Categoria
01/03/2024,SUPERMERCADO XYZ LTDA,"R$ 1.150,50",Alimentação
02/03/2024,POSTO COMBUSTIVEL ABC,"R$ 89,75",Transporte
05/03/2024,SALARIO EMPRESA XYZ,"R$ 2.500,00",Renda
07/03/2024,FARMACIA SAUDE TOTAL,"R$ 45,80",Saúde"""


@pytest.fixture
def csv_content_with_negative_parentheses():
    """
    Fixture que retorna conteúdo CSV com valores negativos em parênteses
    """
    return """Data,Descrição,Valor,Categoria
01/03/2024,SUPERMERCADO XYZ LTDA,(150.50),Alimentação
02/03/2024,POSTO COMBUSTIVEL ABC,(89.75),Transporte
05/03/2024,SALARIO EMPRESA XYZ,2500.00,Renda
07/03/2024,FARMACIA SAUDE TOTAL,(45.80),Saúde"""