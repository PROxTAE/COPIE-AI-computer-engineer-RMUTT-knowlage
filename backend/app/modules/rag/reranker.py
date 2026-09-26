"""Cross-encoder reranking: reads the question and a chunk together and returns
the probability (0-1) that the chunk answers the question.

Unlike vector similarity (topic closeness), this tells "ภาคไฟฟ้าเรียนอะไร" apart
from a computer-engineering page, so it is also the out-of-scope filter.
"""
import os
from collections.abc import Callable, Sequence
from functools import lru_cache

from .chunker import Chunk

RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
# 256 tokens keeps a question + the start of a chunk; longer inputs tripled the
# latency without changing any result on the evaluation sets.
MAX_TOKENS = 256

Scorer = Callable[[Sequence[tuple[str, str]]], list[float]]


def pair_text(chunk: Chunk) -> str:
    return f"{chunk.title} | {chunk.section or ''}\n{chunk.text}"


@lru_cache(maxsize=1)
def load_scorer(model_name: str = RERANK_MODEL) -> Scorer:
    """Load the cross-encoder once (downloads ~2.2GB on first use)."""
    import torch
    from sentence_transformers import CrossEncoder

    model = CrossEncoder(model_name, max_length=MAX_TOKENS)
    sigmoid = torch.nn.Sigmoid()

    def score(pairs: Sequence[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        return [float(s) for s in model.predict(list(pairs), activation_fn=sigmoid, batch_size=16)]

    return score


def rerank(query: str, chunks: Sequence[Chunk], scorer: Scorer) -> list[tuple[Chunk, float]]:
    """`chunks` sorted by relevance to `query`, best first, with their 0-1 scores."""
    scores = scorer([(query, pair_text(c)) for c in chunks])
    return sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
