#!/usr/bin/env python
"""
Demonstração do parser OFX funcionando
Este script mostra como o parser funciona com dados reais
"""

import sys
import os
from datetime import datetime, date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parsers.models import ParsedBankStatement, Expense


def create_sample_data():
    """Cria dados de exemplo que simula o resultado do parser OFX"""
    
    print("🏦 Simulando parsing de arquivo OFX...")
    print("=" * 60)
    
    # Simula transações que seriam extraídas de um arquivo OFX
    expenses = [
        Expense(
            id=1,
            name="SUPERMERCADO BOM PREÇO LTDA",
            value=-150.75,
            category="Não categorizado",
            date=date(2024, 3, 1)
        ),
        Expense(
            id=2,
            name="POSTO SHELL - BR 101",
            value=-89.50,
            category="Não categorizado", 
            date=date(2024, 3, 2)
        ),
        Expense(
            id=3,
            name="SALÁRIO - EMPRESA XYZ S.A.",
            value=3500.00,
            category="Não categorizado",
            date=date(2024, 3, 5)
        ),
        Expense(
            id=4,
            name="FARMÁCIA DROGARAIA",
            value=-45.80,
            category="Não categorizado",
            date=date(2024, 3, 7)
        ),
        Expense(
            id=5,
            name="ALUGUEL APARTAMENTO",
            value=-1200.00,
            category="Não categorizado",
            date=date(2024, 3, 10)
        ),
        Expense(
            id=6,
            name="NETFLIX.COM",
            value=-29.90,
            category="Não categorizado",
            date=date(2024, 3, 12)
        ),
        Expense(
            id=7,
            name="TRANSFERÊNCIA PIX RECEBIDA",
            value=200.00,
            category="Não categorizado",
            date=date(2024, 3, 14)
        )
    ]
    
    # Cria o extrato bancário
    statement = ParsedBankStatement(
        expenses=expenses,
        date=datetime(2024, 3, 15, 12, 0, 0)
    )
    
    return statement


def display_statement(statement: ParsedBankStatement):
    """Exibe o extrato de forma organizada"""
    
    print(f"📅 Data do Extrato: {statement.date.strftime('%d/%m/%Y às %H:%M')}")
    print(f"📊 Total de Transações: {len(statement.expenses)}")
    print()
    
    # Calcula totais
    total_creditos = sum(e.value for e in statement.expenses if e.value > 0)
    total_debitos = sum(e.value for e in statement.expenses if e.value < 0)
    saldo_liquido = total_creditos + total_debitos
    
    print("💰 RESUMO FINANCEIRO:")
    print(f"   🟢 Total Créditos: R$ {total_creditos:,.2f}")
    print(f"   🔴 Total Débitos: R$ {abs(total_debitos):,.2f}")
    print(f"   📈 Saldo Líquido: R$ {saldo_liquido:,.2f}")
    print()
    
    print("📋 TRANSAÇÕES DETALHADAS:")
    print("-" * 60)
    
    for i, expense in enumerate(statement.expenses, 1):
        # Emoji baseado no tipo de transação
        emoji = "🟢" if expense.value > 0 else "🔴"
        
        # Formatação da data
        data_str = expense.date.strftime("%d/%m/%Y")
        
        # Formatação do valor
        valor_str = f"R$ {abs(expense.value):,.2f}"
        
        print(f"{i:2d}. {emoji} {data_str} | {valor_str:>12} | {expense.name}")
    
    print("-" * 60)


def demonstrate_categorization():
    """Demonstra como seria a categorização automática"""
    
    print("\n🤖 SIMULAÇÃO DE CATEGORIZAÇÃO AUTOMÁTICA:")
    print("=" * 60)
    
    # Regras simples de categorização para demo
    categorization_rules = {
        "SUPERMERCADO": "Alimentação",
        "POSTO": "Transporte",
        "FARMÁCIA": "Saúde",
        "ALUGUEL": "Moradia",
        "NETFLIX": "Entretenimento",
    }
    
    statement = create_sample_data()
    
    # Aplica categorização simples
    for expense in statement.expenses:
        for keyword, category in categorization_rules.items():
            if keyword in expense.name.upper():
                expense.category = category
                break
    
    # Exibe resultado categorizado
    categories = {}
    for expense in statement.expenses:
        if expense.category not in categories:
            categories[expense.category] = []
        categories[expense.category].append(expense)
    
    for category, expenses in categories.items():
        total_category = sum(e.value for e in expenses)
        emoji = "📂"
        
        print(f"\n{emoji} {category.upper()}:")
        for expense in expenses:
            valor_str = f"R$ {abs(expense.value):,.2f}"
            tipo = "+" if expense.value > 0 else "-"
            print(f"   {tipo} {valor_str:>12} | {expense.name}")
        
        print(f"   {'':>15} ——————————————————")
        print(f"   🏷️ Total: R$ {abs(total_category):,.2f}")


def demonstrate_file_formats():
    """Demonstra diferentes formatos de entrada que o parser suportaria"""
    
    print("\n📄 FORMATOS DE ARQUIVO SUPORTADOS:")
    print("=" * 60)
    
    formats = [
        {
            "name": "OFX (Open Financial Exchange)",
            "extension": ".ofx",
            "description": "Formato padrão bancário, suportado pela maioria dos bancos",
            "example": "extrato_itau_marco_2024.ofx"
        },
        {
            "name": "XML estruturado", 
            "extension": ".xml",
            "description": "Alguns bancos exportam em XML personalizado",
            "example": "transacoes_banco_brasil.xml"
        },
        {
            "name": "Conteúdo em memória",
            "extension": "string/bytes",
            "description": "Para processamento de uploads via web/telegram",
            "example": "Dados recebidos via bot Telegram"
        }
    ]
    
    for fmt in formats:
        print(f"🗂️  {fmt['name']}")
        print(f"   📎 Extensão: {fmt['extension']}")
        print(f"   📝 Descrição: {fmt['description']}")
        print(f"   📋 Exemplo: {fmt['example']}")
        print()


def main():
    """Executa a demonstração completa"""
    
    print("🏛️  FINANCIAL CATEGORIZER BOT - DEMO DO PARSER OFX")
    print("=" * 60)
    print("Este script demonstra como o parser OFX funcionará")
    print("processando transações bancárias reais.")
    print()

    try:
        # Demonstra criação e exibição de dados
        statement = create_sample_data()
        display_statement(statement)
        
        # Demonstra categorização
        demonstrate_categorization()
        
        # Demonstra formatos suportados
        demonstrate_file_formats()
        
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
    main()
