#!/usr/bin/env python3
"""
Script de teste para a integração Gemini
Execute: python test_gemini_integration.py
"""

import os
import pytest
from src.ai.transaction_classifier import categorize_with_gemini


def test_basic_categorization():
    """Testa categorização básica de transações (integração real com Gemini)."""
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY não configurada; pulando teste de integração")

    test_transactions = [
        {"id": 1, "name": "Uber *uber.com.br", "value": -15.50, "date": "2024-01-15"},
        {"id": 2, "name": "Restaurante Sushi Bar", "value": -89.90, "date": "2024-01-14"},
        {"id": 3, "name": "Salário Janeiro", "value": 3500.00, "date": "2024-01-05"},
        {"id": 4, "name": "Farmácia São João", "value": -45.30, "date": "2024-01-12"},
        {"id": 5, "name": "Netflix", "value": -32.90, "date": "2024-01-10"},
    ]

    result = categorize_with_gemini(test_transactions)

    assert isinstance(result, list)
    assert len(result) == len(test_transactions)
    assert all("category" in tx for tx in result)


def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    
    print("🔍 Verificando configuração do ambiente...")
    
    # Verifica API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY não configurada")
        print("   Configure com: export GOOGLE_API_KEY='sua-chave-aqui'")
        return False
    else:
        print(f"✅ GOOGLE_API_KEY configurada: {api_key[:10]}...")
    
    # Verifica dependências
    try:
        import google.generativeai as genai
        print("✅ Biblioteca 'google-generativeai' instalada")
    except ImportError:
        print("❌ Biblioteca 'google-generativeai' não encontrada")
        print("   Instale com: pip install google-generativeai")
        return False
    
    return True


def main():
    """Função principal do teste"""
    
    print("🚀 Teste de Integração Gemini para Categorização de Transações")
    print("=" * 70)
    
    # Verifica ambiente
    if not check_environment():
        print("\n❌ Ambiente não configurado corretamente")
        print("Configure o ambiente antes de executar os testes.")
        return
    
    print("\n" + "=" * 70)
    
    # Executa teste
    print("\n🧪 Executando: Categorização Básica")
    print("-" * 50)
    
    success = test_basic_categorization()
    
    # Resumo dos resultados
    print("\n" + "=" * 70)
    print("📊 RESUMO DO TESTE")
    print("=" * 70)
    
    status = "✅ PASSOU" if success else "❌ FALHOU"
    print(f"{status} - Categorização Básica")
    
    if success:
        print("\n🎉 Teste passou! A integração está funcionando corretamente.")
    else:
        print("\n⚠️  Teste falhou. Verifique as configurações e dependências.")


if __name__ == "__main__":
    main()