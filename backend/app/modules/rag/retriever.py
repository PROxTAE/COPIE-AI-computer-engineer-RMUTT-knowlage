"""Vector search over the Chroma index and rank fusion (RRF).

sync_index() keeps the collection equal to data/knowledge: chunks added,
changed or removed since the last ingest are fixed before searching, so a
stale index never answers with outdated text.

chromadb / sentence-transformers are imported only when the vector index is
used, so importing app.modules.rag stays fast and works without them.
"""
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

from .chunker import Chunk

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection

RRF_K = 60


@dataclass(frozen=True)
class Ranked:
    chunk_id: str
    score: float


@lru_cache(maxsize=1)
def _collection() -> "Collection":
    from .ingest import open_collection

    return open_collection()


def sync_index(chunks: list[Chunk]) -> int:
    """Re-embed only when the stored index differs from `chunks`, then load the
    query model so the first search is fast. Returns the index size."""
    from .ingest import build_index, content_hash, load_embedder, stored_hashes

    collection = _collection()
    wanted = {c.chunk_id: content_hash(c) for c in chunks}
    embed = load_embedder()
    if stored_hashes(collection) != wanted:
        build_index(chunks, collection, embed)
    return collection.count()


def vector_search(query: str, k: int) -> list[Ranked]:
    """Top-k chunk ids by cosine similarity (1 - distance), best first."""
    from .ingest import load_embedder

    collection = _collection()
    size = collection.count()
    if size == 0 or k <= 0:
        return []
    embedding = load_embedder()([f"query: {query}"])
    result = collection.query(query_embeddings=embedding, n_results=min(k, size), include=["distances"])
    return [Ranked(cid, 1 - dist) for cid, dist in zip(result["ids"][0], result["distances"][0])]


def rrf_merge(rankings: list[list[str]], weights: list[float], k: int = RRF_K) -> list[Ranked]:
    """Reciprocal rank fusion, scaled to 0-1.

    score(id) = sum of weight / (k + rank) over the rankings, divided by the
    score of an id ranked first in every ranking (the best possible score).
    """
    best_possible = sum(weights) / (k + 1)
    scores: dict[str, float] = {}
    for weight, ranking in zip(weights, rankings):
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + weight / (k + rank)
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [Ranked(cid, s / best_possible) for cid, s in ordered]
