"""
Parser para arquivos OFX
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Union
import io

from ofxtools import OFXTree
from ofxtools.models import STMTTRN

from src.utils.logger import get_logger
from src.parsers.models import ParsedBankStatement, Expense

logger = get_logger(__name__)


def parse_ofx_file(file_path: str) -> ParsedBankStatement:
    """
    Faz o parsing de um arquivo OFX e retorna os dados formatados.
    
    Args:
        file_path: Caminho para o arquivo OFX
        
    Returns:
        ParsedBankStatement: Dados formatados do extrato bancário
        
    Raises:
        ValueError: Se o arquivo OFX for inválido
        FileNotFoundError: Se o arquivo não for encontrado
    """
    try:
        logger.info(f"Iniciando parsing do arquivo OFX: {file_path}")
        
        # Carrega e faz parsing do arquivo OFX
        parser = OFXTree()
        with open(file_path, 'rb') as ofx_file:
            parser.parse(ofx_file)
        
        ofx = parser.convert()
        
        # Extrai informações da conta
        if not ofx.statements:
            raise ValueError("Nenhum extrato encontrado no arquivo OFX")
        
        statement = ofx.statements[0]  # Pega o primeiro extrato
        
        # Extrai as transações
        expenses = []
        if statement.transactions:
            for transaction in statement.transactions:
                expense = _convert_transaction_to_expense(transaction, len(expenses))
                expenses.append(expense)
        
        # Data do extrato (usa a data da última transação ou data atual se não houver transações)
        statement_date = datetime.now()
        if expenses:
            statement_date = datetime.combine(expenses[-1].date, datetime.min.time())
        
        result = ParsedBankStatement(expenses=expenses, date=statement_date)
        
        logger.info(f"Parsing concluído. {len(expenses)} transações encontradas")
        return result
        
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer parsing do arquivo OFX: {str(e)}")
        raise ValueError(f"Erro ao processar arquivo OFX: {str(e)}")


def parse_ofx_content(content: Union[str, bytes]) -> ParsedBankStatement:
    """
    Faz o parsing do conteúdo OFX a partir de string ou bytes.
    
    Args:
        content: Conteúdo do arquivo OFX
        
    Returns:
        ParsedBankStatement: Dados formatados do extrato bancário
    """
    try:
        logger.info("Iniciando parsing do conteúdo OFX")
        
        # Converte para bytes se necessário
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Carrega e faz parsing do conteúdo OFX
        parser = OFXTree()
        parser.parse(io.BytesIO(content))
        
        ofx = parser.convert()
        
        # Extrai informações da conta
        if not ofx.statements:
            raise ValueError("Nenhum extrato encontrado no conteúdo OFX")
        
        statement = ofx.statements[0]  # Pega o primeiro extrato
        
        # Extrai as transações
        expenses = []
        if statement.transactions:
            for transaction in statement.transactions:
                expense = _convert_transaction_to_expense(transaction, len(expenses))
                expenses.append(expense)
        
        # Data do extrato
        statement_date = datetime.now()
        if expenses:
            statement_date = datetime.combine(expenses[-1].date, datetime.min.time())
        
        result = ParsedBankStatement(expenses=expenses, date=statement_date)
        
        logger.info(f"Parsing concluído. {len(expenses)} transações encontradas")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao fazer parsing do conteúdo OFX: {str(e)}")
        raise ValueError(f"Erro ao processar conteúdo OFX: {str(e)}")


def _convert_transaction_to_expense(transaction: STMTTRN, id) -> Expense:
    """
    Converte uma transação OFX para o modelo Expense.
    
    Args:
        transaction: Transação do OFX
        
    Returns:
        Expense: Objeto Expense formatado
    """
    # Nome da transação (usa memo ou payee, priorizando memo)
    name = transaction.memo or transaction.payee or "Transação sem descrição"
    
    # Valor da transação (converte Decimal para float)
    value = float(transaction.trnamt) if transaction.trnamt else 0.0
    
    # Categoria padrão (será classificada posteriormente pelo AI)
    category = "Não categorizado"
    
    # Data da transação
    transaction_date = transaction.dtposted.date() if transaction.dtposted else datetime.now().date()
    
    return Expense(
        id=id,
        name=name,
        value=value,
        category=category,
        date=transaction_date
    )


