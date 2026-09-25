"""search_department_knowledge(): the RAG entry point used by the agent (P3).

1. Reject empty / profane queries and questions the documents do not cover
   (keyword 3-gram coverage — vector scores cannot tell these apart).
2. Rank chunks with the e5 vector index and the keyword index, merged by RRF.
3. If the vector index cannot be used (model or Chroma unavailable), rank with
   keywords only, so the agent still gets real sources instead of an error.
"""
import logging
from functools import lru_cache

from app.schemas.contract import RetrievedChunk, Source

from . import retriever
from .chunker import KNOWLEDGE_DIR, Chunk, load_chunks
from .guard import contains_profanity
from .lexical import LexicalIndex

__all__ = ["KNOWLEDGE_DIR", "ensure_index", "search_department_knowledge"]

logger = logging.getLogger(__name__)

USE_VECTOR = True
# Share of the query's 3-grams that must appear in one chunk; below it the
# question is treated as outside the department documents.
MIN_COVERAGE = 0.2
CANDIDATES = 10  # chunks taken from each ranking before fusion
VECTOR_WEIGHT = 2.0
LEXICAL_WEIGHT = 1.0
SNIPPET_CHARS = 200
MAX_QUERY_CHARS = 1000  # same limit as ChatRequest.message


@lru_cache(maxsize=1)
def _index() -> LexicalIndex:
    return LexicalIndex(load_chunks(KNOWLEDGE_DIR))


@lru_cache(maxsize=1)
def _vector_ready() -> bool:
    if not USE_VECTOR:
        return False
    try:
        return retriever.sync_index(_index().chunks) > 0
    except Exception:
        logger.exception("vector index unavailable, using keyword search only")
        return False


def ensure_index() -> int:
    """(Re)load the knowledge files and sync the vector index. Returns the number of chunks.

    Call it at startup: it loads the embedding model, so the first question is not slow.
    """
    _index.cache_clear()
    _vector_ready.cache_clear()
    _vector_ready()
    return len(_index().chunks)


def _rank(query: str, lexical: LexicalIndex) -> list[retriever.Ranked]:
    lexical_ids = [hit.chunk.chunk_id for hit in lexical.search(query, CANDIDATES)]
    if _vector_ready():
        try:
            vector_ids = [r.chunk_id for r in retriever.vector_search(query, CANDIDATES)]
            return retriever.rrf_merge([vector_ids, lexical_ids], [VECTOR_WEIGHT, LEXICAL_WEIGHT])
        except Exception:
            logger.exception("vector search failed, using keyword ranking")
    return retriever.rrf_merge([lexical_ids], [LEXICAL_WEIGHT])


def search_department_knowledge(query: str, top_k: int = 4) -> list[RetrievedChunk]:
    """Chunks most related to `query`, best first (score 0-1).

    Returns [] when the query is empty, profane, or not covered by the documents.
    """
    query = query.strip()[:MAX_QUERY_CHARS]
    lexical = _index()
    if not query or top_k <= 0 or contains_profanity(query) or not lexical.in_scope(query, MIN_COVERAGE):
        return []

    by_id: dict[str, Chunk] = {c.chunk_id: c for c in lexical.chunks}
    ranked = [r for r in _rank(query, lexical) if r.chunk_id in by_id][:top_k]
    return [
        RetrievedChunk(
            text=by_id[r.chunk_id].text,
            source=Source(
                doc_id=by_id[r.chunk_id].doc_id,
                title=by_id[r.chunk_id].title,
                section=by_id[r.chunk_id].section,
                url=by_id[r.chunk_id].url,
                snippet=by_id[r.chunk_id].text[:SNIPPET_CHARS],
                score=round(r.score, 4),
            ),
        )
        for r in ranked
    ]
