"""Build the Chroma vector index from data/knowledge.

    python -m app.modules.rag.ingest            # add / update / remove changed chunks
    python -m app.modules.rag.ingest --rebuild  # drop the collection and embed everything again

Running it twice never duplicates chunks: ids are stable ("<doc_id>#<n>"),
ids that no longer exist are deleted, and only chunks whose content changed
(tracked by a hash in the metadata) are embedded again.
"""
import argparse
import hashlib
import time
from collections.abc import Callable, Sequence
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings

from .chunker import KNOWLEDGE_DIR, Chunk, load_chunks

COLLECTION_NAME = "ce_knowledge"
BATCH_SIZE = 32

Embedder = Callable[[Sequence[str]], list[list[float]]]


def passage_text(chunk: Chunk) -> str:
    """Text that gets embedded. e5 models expect the "passage: " prefix on documents."""
    return f"passage: {chunk.title} | {chunk.section or ''}\n{chunk.text}"


def content_hash(chunk: Chunk) -> str:
    return hashlib.sha1(passage_text(chunk).encode() + chunk.url.encode()).hexdigest()


def chunk_metadata(chunk: Chunk) -> dict[str, str]:
    # Chroma metadata values cannot be None, so a missing section is stored as "".
    return {
        "doc_id": chunk.doc_id,
        "title": chunk.title,
        "section": chunk.section or "",
        "url": chunk.url,
        "hash": content_hash(chunk),
    }


@lru_cache(maxsize=1)
def load_embedder(model_name: str = settings.embedding_model) -> Embedder:
    """Load the sentence-transformers model once (downloads it on first use)."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)

    def embed(texts: Sequence[str]) -> list[list[float]]:
        vectors = model.encode(list(texts), batch_size=BATCH_SIZE, normalize_embeddings=True)
        return vectors.tolist()

    return embed


def open_collection(chroma_dir: str | Path = settings.chroma_dir, rebuild: bool = False) -> Collection:
    client = chromadb.PersistentClient(path=str(chroma_dir))
    if rebuild and COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    return client.get_or_create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def stored_hashes(collection: Collection) -> dict[str, str | None]:
    stored = collection.get(include=["metadatas"])
    return {cid: (meta or {}).get("hash") for cid, meta in zip(stored["ids"], stored["metadatas"])}


def build_index(chunks: list[Chunk], collection: Collection, embed: Embedder) -> int:
    """Make the collection hold exactly `chunks`. Returns the collection size.

    `embed` is only called for new or changed chunks.
    """
    ids = [chunk.chunk_id for chunk in chunks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate chunk ids — check for two files with the same doc_id")

    have = stored_hashes(collection)
    stale = set(have) - set(ids)
    if stale:
        collection.delete(ids=sorted(stale))

    changed = [c for c in chunks if have.get(c.chunk_id) != content_hash(c)]
    for start in range(0, len(changed), BATCH_SIZE):
        batch = changed[start : start + BATCH_SIZE]
        collection.upsert(
            ids=[c.chunk_id for c in batch],
            embeddings=embed([passage_text(c) for c in batch]),
            documents=[c.text for c in batch],
            metadatas=[chunk_metadata(c) for c in batch],
        )
    return collection.count()


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Embed data/knowledge into Chroma.")
    parser.add_argument("--rebuild", action="store_true", help="delete the collection first")
    args = parser.parse_args(argv)

    started = time.perf_counter()
    chunks = load_chunks(KNOWLEDGE_DIR)
    collection = open_collection(rebuild=args.rebuild)
    total = build_index(chunks, collection, lambda texts: load_embedder()(texts))
    docs = len({c.doc_id for c in chunks})
    print(
        f"indexed {total} chunks from {docs} documents into '{COLLECTION_NAME}' "
        f"at {settings.chroma_dir} in {time.perf_counter() - started:.1f}s"
    )


if __name__ == "__main__":
    main()
