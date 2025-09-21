"""
Testes para o classificador de transações (camada de prompt/robustez)
"""

import json
import pytest

from src.ai.transaction_classifier import TransactionClassifier


class DummyClient:
    class GenerativeModel:
        def __init__(self, *_args, **_kwargs):
            pass

        def generate_content(self, prompt):
            # Retorna um JSON determinístico
            return type("Resp", (), {"text": json.dumps({
                "categorizations": [
                    {"id": 1, "category": "Transporte", "confidence": 0.9, "reasoning": "Uber"}
                ]
            })})


def test_process_categorization_response_valid(monkeypatch):
    classifier = TransactionClassifier(api_key="dummy")

    # Injeta client dummy (evita chamada real)
    monkeypatch.setattr(classifier, "client", DummyClient)

    txs = [{"id": 1, "name": "Uber", "value": -12.3, "date": "2024-01-01"}]
    out = classifier.categorize_transactions(txs)

    assert out[0]["category"] == "Transporte"
    assert out[0]["categorization_confidence"] == 0.9


def test_process_categorization_response_invalid_json(monkeypatch):
    classifier = TransactionClassifier(api_key="dummy")

    class BadClient:
        class GenerativeModel:
            def __init__(self, *_args, **_kwargs):
                pass

            def generate_content(self, prompt):
                return type("Resp", (), {"text": "not-json"})

    monkeypatch.setattr(classifier, "client", BadClient)

    txs = [{"id": 1, "name": "X", "value": -1.0, "date": "2024-01-01"}]
    out = classifier.categorize_transactions(txs)

    assert out[0]["category"] == "Outros"
    assert out[0]["categorization_confidence"] == 0.0


