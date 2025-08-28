"""
Utilidades simples para a função Lambda
"""

from typing import Any, Dict
import hashlib

def format_currency(amount: float) -> str:
    """Formata o valor como uma string de moeda."""
    return f"R${amount:,.2f}"


def generate_transaction_id(data: Dict[str, Any]) -> str:
    """Gera um ID único para uma transação com base nos dados da transação."""
    content = f"{data.get('date', '')}{data.get('amount', '')}{data.get('description', '')}"
    return hashlib.md5(content.encode()).hexdigest()[:12]
    