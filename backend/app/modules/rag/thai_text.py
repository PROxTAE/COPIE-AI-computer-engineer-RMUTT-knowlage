"""Thai word tokenization for keyword search (BM25).

pythainlp's newmm engine with a dictionary extended by department terms, so
words like "สหกิจศึกษา" or "หน่วยกิต" are not cut into meaningless pieces.
"""
from functools import lru_cache

from rank_bm25 import BM25Okapi

from .chunker import Chunk
from .lexical import expand_query

# Department words the default dictionary splits wrongly (e.g. "สหกิจ" -> "สห" + "กิจ").
DOMAIN_WORDS = frozenset({
    "สหกิจ", "สหกิจศึกษา", "หน่วยกิต", "ฝึกงาน", "ค่าเทอม", "เกรดเฉลี่ย", "โครงงาน",
    "ภาควิชา", "แล็บ", "หลักสูตร", "ปริญญา", "วิศวกรรมคอมพิวเตอร์", "ไมโครคอนโทรลเลอร์",
    "ธุรการ", "เทียบโอน", "ปฏิบัติการ", "ค่าบำรุงการศึกษา",
})
# Stopwords that carry meaning in questions about the department.
KEEP_WORDS = frozenset({"ภาค", "เรียน", "ปี", "เทอม", "วิชา", "ค่า", "จบ", "สอน", "งาน"})


@lru_cache(maxsize=1)
def _dictionary():
    from pythainlp.corpus import thai_words
    from pythainlp.util import dict_trie

    return dict_trie(set(thai_words()) | DOMAIN_WORDS)


@lru_cache(maxsize=1)
def _stopwords() -> frozenset[str]:
    from pythainlp.corpus import thai_stopwords

    return frozenset(thai_stopwords()) - KEEP_WORDS


def tokenize(text: str) -> list[str]:
    """Content words of `text`: lower-cased, no stopwords, spaces, punctuation or 1-char tokens."""
    from pythainlp.tokenize import word_tokenize

    stop = _stopwords()
    tokens = word_tokenize(text.lower(), custom_dict=_dictionary(), engine="newmm", keep_whitespace=False)
    return [t for t in tokens if len(t) > 1 and t not in stop and any(ch.isalnum() for ch in t)]


class BM25Index:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        # Section headings are repeated so a match on them counts more than one in the body.
        docs = [tokenize(f"{c.title} {c.section or ''} {c.section or ''} {c.text}") for c in chunks]
        self._bm25 = BM25Okapi(docs) if chunks else None

    def search(self, query: str, k: int) -> list[str]:
        """Chunk ids with a positive BM25 score, best first."""
        if self._bm25 is None or k <= 0:
            return []
        scores = self._bm25.get_scores(tokenize(expand_query(query)))
        order = sorted(range(len(self.chunks)), key=lambda i: scores[i], reverse=True)[:k]
        return [self.chunks[i].chunk_id for i in order if scores[i] > 0]
