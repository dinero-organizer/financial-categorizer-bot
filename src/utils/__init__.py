"""
Utilidades simples para a diversos fins
"""


def format_currency(amount: float) -> str:
    """Formata o valor como uma string de moeda."""
    return f"R${amount:,.2f}"
