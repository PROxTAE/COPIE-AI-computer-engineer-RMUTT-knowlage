"""Tests run without the embedding / reranker models unless RUN_LIVE_RAG=1.

Offline, search uses its fallback path (BM25 candidates + keyword scope filter),
so `pytest` is fast, needs no download and never writes to storage/chroma.
Live accuracy tests: RUN_LIVE_RAG=1 python -m pytest -q app/modules/rag
"""
import os

import pytest

from app.modules.rag import service

LIVE = os.getenv("RUN_LIVE_RAG") == "1"
live = pytest.mark.skipif(not LIVE, reason="set RUN_LIVE_RAG=1 to load the real embedding and reranker models")


def _reset() -> None:
    service._indexes.cache_clear()
    service._vector.reset()
    service._reranker.reset()


@pytest.fixture(autouse=True)
def models_offline_unless_live(monkeypatch):
    if not LIVE:
        monkeypatch.setattr(service, "USE_VECTOR", False)
        monkeypatch.setattr(service, "USE_RERANKER", False)
    _reset()
    yield
    _reset()
