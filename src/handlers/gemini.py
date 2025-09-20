"""
Auxiliares AWS para a função Lambda
"""

from src.ai.transaction_classifier import categorize_with_gemini


def categorize_json_statement(json_statement: dict) -> dict:
    """
    Categoriza um extrato bancário em formato JSON usando Gemini
    
    Args:
        json_statement: Extrato bancário em formato JSON
    
    Returns:
        Extrato bancário com transações categorizadas
    """
    # Extrai as transações do JSON
    transactions = json_statement.get('transactions', [])
    if not transactions:
        return json_statement
    
    # Categoriza as transações
    categorized_transactions = categorize_with_gemini(transactions)
    
    # Atualiza o JSON com as transações categorizadas
    result = json_statement.copy()
    result['transactions'] = categorized_transactions
    result['categorization_info'] = {
        'method': 'gemini',
        'total_transactions': len(categorized_transactions),
        'categories_used': 'default'
    }
    
    return result