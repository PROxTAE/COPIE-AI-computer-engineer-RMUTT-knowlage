import hashlib
import uuid
from collections.abc import Sequence
from itertools import pairwise
from pathlib import Path

import chromadb
import pytest

from app.modules.rag.chunker import MAX_CHARS, Chunk, load_chunks, split_long_text
from app.modules.rag.ingest import (
    COLLECTION_NAME,
    build_index,
    open_collection,
    passage_text,
)
from app.modules.rag.service import KNOWLEDGE_DIR


def fake_embed(texts: Sequence[str]) -> list[list[float]]:
    """Deterministic 8-dim vectors so tests never download the real model."""
    return [[b / 255 for b in hashlib.sha256(t.encode()).digest()[:8]] for t in texts]


def make_chunk(i: int, doc_id: str = "doc", section: str | None = "S") -> Chunk:
    return Chunk(f"{doc_id}#{i}", doc_id, "Title", section, "https://example.ac.th/", f"text {i}")


@pytest.fixture
def collection():
    client = chromadb.EphemeralClient()
    return client.create_collection(f"test_{uuid.uuid4().hex}", metadata={"hnsw:space": "cosine"})


# ---------- split_long_text ----------

def test_short_text_is_not_split() -> None:
    assert split_long_text("สั้น") == ["สั้น"]


def test_long_text_pieces_fit_and_overlap() -> None:
    lines = [f"บรรทัดที่ {i} " + "ก" * 60 for i in range(40)]
    text = "\n".join(lines)
    pieces = split_long_text(text, max_chars=800, overlap=100)
    assert len(pieces) > 1
    assert all(len(p) <= 800 for p in pieces)
    for left, right in pairwise(pieces):
        assert left[-50:] in right, "consecutive pieces should overlap"
    assert "บรรทัดที่ 0 " in pieces[0] and "บรรทัดที่ 39 " in pieces[-1]


def test_text_without_breaks_is_still_split() -> None:
    pieces = split_long_text("ก" * 2000, max_chars=800, overlap=100)
    assert all(len(p) <= 800 for p in pieces)
    assert sum(len(p) for p in pieces) >= 2000


def test_real_knowledge_chunks_fit_max_chars() -> None:
    chunks = load_chunks(KNOWLEDGE_DIR)
    assert all(len(c.text) <= MAX_CHARS for c in chunks)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


# ---------- build_index ----------

def test_passage_text_has_e5_prefix_and_context() -> None:
    text = passage_text(make_chunk(0))
    assert text.startswith("passage: Title | S\n")


def test_index_holds_every_chunk_with_metadata(collection) -> None:
    chunks = [make_chunk(i) for i in range(3)] + [make_chunk(0, doc_id="other", section=None)]
    assert build_index(chunks, collection, fake_embed) == 4
    got = collection.get(ids=["other#0"], include=["metadatas", "documents"])
    assert got["metadatas"][0] == {"doc_id": "other", "title": "Title", "section": "", "url": "https://example.ac.th/"}
    assert got["documents"][0] == "text 0"


def test_running_twice_does_not_duplicate(collection) -> None:
    chunks = [make_chunk(i) for i in range(5)]
    build_index(chunks, collection, fake_embed)
    assert build_index(chunks, collection, fake_embed) == 5


def test_removed_chunks_are_deleted(collection) -> None:
    build_index([make_chunk(i) for i in range(5)], collection, fake_embed)
    assert build_index([make_chunk(i) for i in range(2)], collection, fake_embed) == 2
    assert sorted(collection.get(include=[])["ids"]) == ["doc#0", "doc#1"]


def test_duplicate_ids_are_rejected(collection) -> None:
    with pytest.raises(ValueError, match="duplicate"):
        build_index([make_chunk(0), make_chunk(0)], collection, fake_embed)


def test_more_chunks_than_one_batch(collection) -> None:
    chunks = [make_chunk(i) for i in range(70)]
    assert build_index(chunks, collection, fake_embed) == 70


def test_rebuild_empties_the_collection(tmp_path: Path) -> None:
    first = open_collection(tmp_path)
    build_index([make_chunk(i) for i in range(3)], first, fake_embed)
    assert open_collection(tmp_path).count() == 3
    rebuilt = open_collection(tmp_path, rebuild=True)
    assert rebuilt.name == COLLECTION_NAME
    assert rebuilt.count() == 0
