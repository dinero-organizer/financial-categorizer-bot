"""
Testes do download e validação de arquivo no handler (tamanho e nome)
"""

import asyncio
import pytest
from types import SimpleNamespace
from pathlib import Path

from src.handlers import handle_document as hd


class DummyTgFile:
    def __init__(self, path):
        self.path = path

    async def download_to_drive(self, local_path):
        Path(local_path).write_bytes(b"data")


class DummyBot:
    async def get_file(self, file_id):
        return DummyTgFile("dummy")


@pytest.mark.asyncio
async def test_download_rejects_large_files(tmp_path, monkeypatch):
    context = SimpleNamespace(bot=DummyBot())
    document = SimpleNamespace(file_name="x.csv", file_id="1", file_size=hd.MAX_FILE_SIZE_MB * 1024 * 1024 + 1)

    with pytest.raises(ValueError):
        await hd._download_document_to_temp(context, document, str(tmp_path))


@pytest.mark.asyncio
async def test_download_accepts_valid_file(tmp_path):
    context = SimpleNamespace(bot=DummyBot())
    document = SimpleNamespace(file_name="x.csv", file_id="1", file_size=1024)

    local = await hd._download_document_to_temp(context, document, str(tmp_path))
    assert Path(local).exists()


