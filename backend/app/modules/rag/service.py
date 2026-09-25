"""search_department_knowledge(): the RAG entry point used by the agent (P3).

Day 1 retrieval is keyword-based over the real knowledge files (see lexical.py).
The vector + BM25 retriever replaces it later without changing this interface.
"""
import os
from functools import lru_cache
from pathlib import Path

from app.schemas.contract import RetrievedChunk, Source

from .chunker import load_chunks
from .guard import contains_profanity
from .lexical import LexicalIndex

KNOWLEDGE_DIR = Path(
    os.getenv("KNOWLEDGE_DIR", Path(__file__).resolve().parents[4] / "data" / "knowledge")
)
# Share of the query's 3-grams that must appear in one chunk; below it the
# question is treated as outside the department documents.
MIN_COVERAGE = 0.2
SNIPPET_CHARS = 200
MAX_QUERY_CHARS = 1000  # same limit as ChatRequest.message


@lru_cache(maxsize=1)
def _index() -> LexicalIndex:
    return LexicalIndex(load_chunks(KNOWLEDGE_DIR))


def ensure_index() -> int:
    """(Re)load the knowledge files. Returns the number of chunks."""
    _index.cache_clear()
    return len(_index().chunks)


def search_department_knowledge(query: str, top_k: int = 4) -> list[RetrievedChunk]:
    """Chunks most related to `query`, best first.

    Returns [] when the query is empty, profane, or not covered by the documents.
    """
    query = query.strip()[:MAX_QUERY_CHARS]
    if not query or top_k <= 0 or contains_profanity(query):
        return []

    return [
        RetrievedChunk(
            text=hit.chunk.text,
            source=Source(
                doc_id=hit.chunk.doc_id,
                title=hit.chunk.title,
                section=hit.chunk.section,
                url=hit.chunk.url,
                snippet=hit.chunk.text[:SNIPPET_CHARS],
                score=round(hit.score, 4),
            ),
        )
        for hit in _index().search(query, top_k, MIN_COVERAGE)
    ]
