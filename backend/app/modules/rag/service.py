"""search_department_knowledge(): the RAG entry point used by the agent (P3).

1. Reject empty or profane questions and questions about another department,
   faculty or university (scope.py).
2. Candidates: e5 vector search and Thai-word BM25, merged by RRF.
3. A cross-encoder reranker scores each candidate 0-1 (does this chunk answer
   the question?). Chunks below MIN_RELEVANCE are dropped, so an unrelated
   question returns [] and Source.score is a real relevance score.

If a model cannot be loaded (no internet on first run, missing library), search
still works with what is available and retries loading later:
- no reranker: keyword 3-gram coverage decides scope, RRF decides order
- no vector index: BM25 alone provides the candidates
"""
import logging
import time
from dataclasses import dataclass
from functools import lru_cache

from app.schemas.contract import RetrievedChunk, Source

from . import reranker, retriever
from .chunker import KNOWLEDGE_DIR, Chunk, load_chunks
from .guard import contains_profanity
from .lexical import LexicalIndex
from .scope import mentions_other_unit
from .thai_text import BM25Index

__all__ = ["KNOWLEDGE_DIR", "ensure_index", "search_department_knowledge"]

logger = logging.getLogger(__name__)

USE_VECTOR = True
USE_RERANKER = True
CANDIDATES = 10  # chunks taken from each ranking before fusion
# Fused chunks sent to the reranker: 10 found one more answer in 113 questions but was 60% slower.
RERANK_CANDIDATES = 6
VECTOR_WEIGHT = 2.0
BM25_WEIGHT = 1.0
# Reranker probability below which a chunk does not answer the question. On the
# tuning questions, out-of-scope ones scored at most 0.0034 and answerable ones
# mostly above 0.01, so the cut sits in that gap.
MIN_RELEVANCE = 0.005
# Fallback scope filter when the reranker is unavailable: share of the query's
# 3-grams that must appear in one chunk.
MIN_COVERAGE = 0.2
RETRY_SECONDS = 60  # wait before trying again to load a model that failed
SNIPPET_CHARS = 200
MAX_QUERY_CHARS = 1000  # same limit as ChatRequest.message


@dataclass(frozen=True)
class _Indexes:
    chunks: list[Chunk]
    by_id: dict[str, Chunk]
    lexical: LexicalIndex
    bm25: BM25Index


@lru_cache(maxsize=1)
def _indexes() -> _Indexes:
    chunks = load_chunks(KNOWLEDGE_DIR)
    return _Indexes(chunks, {c.chunk_id: c for c in chunks}, LexicalIndex(chunks), BM25Index(chunks))


class _Optional:
    """Loads an optional component; on failure logs it, returns None, and retries
    after RETRY_SECONDS instead of staying disabled until restart."""

    def __init__(self, name: str, load) -> None:
        self.name, self._load = name, load
        self._value, self._ok, self._failed_at = None, False, None

    def get(self):
        if self._ok:
            return self._value
        if self._failed_at is not None and time.monotonic() - self._failed_at < RETRY_SECONDS:
            return None
        try:
            self._value, self._ok = self._load(), True
            return self._value
        except Exception:
            self._failed_at = time.monotonic()
            logger.exception("%s unavailable, searching without it", self.name)
            return None

    def reset(self) -> None:
        self._value, self._ok, self._failed_at = None, False, None


def _load_vector() -> bool:
    if not USE_VECTOR:
        raise RuntimeError("USE_VECTOR is False")
    return retriever.sync_index(_indexes().chunks) > 0


def _load_reranker() -> reranker.Scorer:
    if not USE_RERANKER:
        raise RuntimeError("USE_RERANKER is False")
    return reranker.load_scorer()


_vector = _Optional("vector index", _load_vector)
_reranker = _Optional("reranker", _load_reranker)


def ensure_index() -> int:
    """(Re)load the knowledge files, sync the vector index and load the models.
    Returns the number of chunks. Call it at startup so the first question is fast."""
    _indexes.cache_clear()
    _vector.reset()
    _reranker.reset()
    _vector.get()
    _reranker.get()
    return len(_indexes().chunks)


def _candidates(query: str, idx: _Indexes) -> list[retriever.Ranked]:
    bm25_ids = idx.bm25.search(query, CANDIDATES)
    if _vector.get():
        try:
            vector_ids = [r.chunk_id for r in retriever.vector_search(query, CANDIDATES)]
            return retriever.rrf_merge([vector_ids, bm25_ids], [VECTOR_WEIGHT, BM25_WEIGHT])
        except Exception:
            logger.exception("vector search failed, using BM25 candidates only")
    return retriever.rrf_merge([bm25_ids], [BM25_WEIGHT])


def _ranked(query: str, idx: _Indexes) -> list[tuple[Chunk, float]]:
    fused = [(idx.by_id[r.chunk_id], r.score) for r in _candidates(query, idx) if r.chunk_id in idx.by_id]
    scorer = _reranker.get()
    if scorer is not None:
        try:
            scored = reranker.rerank(query, [chunk for chunk, _ in fused[:RERANK_CANDIDATES]], scorer)
            return [(chunk, score) for chunk, score in scored if score >= MIN_RELEVANCE]
        except Exception:
            logger.exception("reranking failed, using keyword scope filter")
    return fused if idx.lexical.in_scope(query, MIN_COVERAGE) else []


def search_department_knowledge(query: str, top_k: int = 4) -> list[RetrievedChunk]:
    """Chunks that answer `query`, best first; Source.score is 0-1 relevance.

    Returns [] when the query is empty, profane, about another department /
    faculty / university, or not answered by the department documents.
    """
    query = query.strip()[:MAX_QUERY_CHARS]
    if not query or top_k <= 0 or contains_profanity(query) or mentions_other_unit(query):
        return []
    return [
        RetrievedChunk(
            text=chunk.text,
            source=Source(
                doc_id=chunk.doc_id,
                title=chunk.title,
                section=chunk.section,
                url=chunk.url,
                snippet=chunk.text[:SNIPPET_CHARS],
                score=round(score, 4),
            ),
        )
        for chunk, score in _ranked(query, _indexes())[:top_k]
    ]
