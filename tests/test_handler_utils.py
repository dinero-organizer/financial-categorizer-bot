"""
Testes para utilitários do handler de documentos
"""

import types
import pytest
from pathlib import Path

from src.handlers.handle_document import _sanitize_filename, _detect_file_type, _categorize_with_ai, MAX_FILE_SIZE_MB


def test_sanitize_filename_strips_directories():
    assert _sanitize_filename("../../etc/passwd") == "passwd"
    assert _sanitize_filename("C:/temp/file.csv") == "file.csv"
    assert _sanitize_filename("..\\..\\windows\\system32\\drivers\\etc\\hosts") == "hosts"
    assert _sanitize_filename("") == "arquivo"


def test_detect_file_type():
    assert _detect_file_type("file.csv") == "csv"
    assert _detect_file_type("file.OFX") == "ofx"
    assert _detect_file_type("file.txt") is None


def test_ai_fallback_on_exception(monkeypatch):
    # Força exceção no categorize_with_gemini usando monkeypatch no módulo
    from src.handlers import handle_document as hd

    calls = {"count": 0}

    def fake_categorize_with_gemini(_tx):
        calls["count"] += 1
        raise RuntimeError("AI error")

    monkeypatch.setattr(hd, "categorize_with_gemini", fake_categorize_with_gemini)

    txs = [{"id": 1, "name": "Teste", "value": 10.0, "date": "2024-01-01"}]
    result, ai_ok = hd._categorize_with_ai(txs)

    assert ai_ok is False
    assert len(result) == 1
    assert result[0]["category"] == "Não categorizada"
    assert result[0]["categorization_confidence"] == 0.0


def test_max_file_size_constant_reasonable():
    assert isinstance(MAX_FILE_SIZE_MB, int)
    assert 1 <= MAX_FILE_SIZE_MB <= 100
