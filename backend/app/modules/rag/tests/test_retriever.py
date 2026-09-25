import uuid

import chromadb
import pytest

from app.modules.rag import retriever
from app.modules.rag.chunker import Chunk
from app.modules.rag.ingest import build_index

from .test_ingest import fake_embed


def make_chunk(i: int, text: str | None = None) -> Chunk:
    return Chunk(f"doc#{i}", "doc", "Title", "S", "https://example.ac.th/", text or f"text {i}")


# ---------- rrf_merge ----------

def test_rrf_first_everywhere_scores_one() -> None:
    merged = retriever.rrf_merge([["a", "b"], ["a", "c"]], [2.0, 1.0])
    assert merged[0].chunk_id == "a"
    assert merged[0].score == pytest.approx(1.0)


def test_rrf_weight_decides_disagreement() -> None:
    merged = retriever.rrf_merge([["v"], ["l"]], [2.0, 1.0])
    assert [r.chunk_id for r in merged] == ["v", "l"]


def test_rrf_scores_are_sorted_and_bounded() -> None:
    merged = retriever.rrf_merge([list("abcde"), list("edcba")], [1.0, 1.0])
    scores = [r.score for r in merged]
    assert scores == sorted(scores, reverse=True)
    assert all(0 < s <= 1 for s in scores)


def test_rrf_of_nothing_is_empty() -> None:
    assert retriever.rrf_merge([[], []], [1.0, 1.0]) == []


# ---------- incremental ingest ----------

class CountingEmbed:
    def __init__(self) -> None:
        self.texts: list[str] = []

    def __call__(self, texts):
        self.texts.extend(texts)
        return fake_embed(texts)


@pytest.fixture
def collection():
    client = chromadb.EphemeralClient()
    return client.create_collection(f"test_{uuid.uuid4().hex}", metadata={"hnsw:space": "cosine"})


def test_only_changed_chunks_are_embedded_again(collection) -> None:
    chunks = [make_chunk(i) for i in range(4)]
    build_index(chunks, collection, fake_embed)

    embed = CountingEmbed()
    chunks[2] = make_chunk(2, text="แก้ไขแล้ว")
    build_index(chunks, collection, embed)
    assert len(embed.texts) == 1 and "แก้ไขแล้ว" in embed.texts[0]
    assert collection.get(ids=["doc#2"])["documents"] == ["แก้ไขแล้ว"]


def test_unchanged_index_embeds_nothing(collection) -> None:
    chunks = [make_chunk(i) for i in range(4)]
    build_index(chunks, collection, fake_embed)
    embed = CountingEmbed()
    build_index(chunks, collection, embed)
    assert embed.texts == []


# ---------- sync_index / vector_search with a fake model ----------

@pytest.fixture
def fake_vector_store(monkeypatch, collection):
    from app.modules.rag import ingest

    monkeypatch.setattr(retriever, "_collection", lambda: collection)
    monkeypatch.setattr(ingest, "load_embedder", lambda *a, **k: fake_embed)
    return collection


def test_sync_index_builds_then_skips(fake_vector_store) -> None:
    chunks = [make_chunk(i) for i in range(3)]
    assert retriever.sync_index(chunks) == 3
    assert retriever.sync_index(chunks[:2]) == 2


def test_vector_search_returns_k_ranked_ids(fake_vector_store) -> None:
    retriever.sync_index([make_chunk(i) for i in range(5)])
    hits = retriever.vector_search("อะไรก็ได้", k=3)
    assert len(hits) == 3
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)


def test_vector_search_on_empty_index(fake_vector_store) -> None:
    assert retriever.vector_search("x", k=3) == []

