"""Keyword retrieval over character n-grams (no Thai tokenizer needed).

Ranking: TF-IDF cosine over character 2- and 3-grams.
Out-of-scope gate: share of the query's (IDF-weighted) 3-grams found in the best
chunk. Unrelated questions share only a few common 3-grams with the documents.
"""
import math
import re
from collections import Counter
from dataclasses import dataclass

from .chunker import Chunk

# \w alone drops Thai vowel/tone marks (ั ิ ่ ...), so the Thai block is added explicitly.
WORD_RE = re.compile(r"[\w฀-๿]+")
RANK_NGRAMS = (2, 3)
GATE_NGRAM = 3

# Words people type -> words the department documents use.
QUERY_SYNONYMS: dict[str, str] = {
    "แล็บ": "ห้องปฏิบัติการ",
    "แลป": "ห้องปฏิบัติการ",
    "lab": "ห้องปฏิบัติการ",
    "ห้องคอม": "ห้องปฏิบัติการคอมพิวเตอร์",
    "เฟซบุ๊ก": "facebook",
    "เฟสบุ๊ค": "facebook",
    "เฟสบุ๊ก": "facebook",
    "เพจ": "facebook",
    "ทำงาน": "อาชีพ",
    "ค่าเทอม": "ค่าบำรุงการศึกษา ค่าลงทะเบียน บาท",
    "ค่าเรียน": "ค่าบำรุงการศึกษา ค่าลงทะเบียน บาท",
    "ซัมเมอร์": "ภาคการศึกษาฤดูร้อน",
    "จ่าย": "ค่าบำรุงการศึกษา บาท",
    "ทุน": "ทุนการศึกษา",
    "เบอร์": "โทรศัพท์",
    "โทร": "โทรศัพท์",
    "อยู่ที่ไหน": "ที่อยู่",
    "ที่ตั้ง": "ที่อยู่",
    "กี่โมง": "เวลาทำการ",
    "เปิดกี่โมง": "เวลาทำการ",
    "จบ": "สำเร็จการศึกษา",
    "กี่ปี": "ระยะเวลาเรียน ปี",
    "สมัคร": "คุณสมบัติ ผู้เข้าศึกษา",
    "ม.6": "มัธยมศึกษาตอนปลาย",
    "ฝึกงาน": "ฝึกงาน สหกิจศึกษา ฝึกประสบการณ์วิชาชีพ",
    "เกรด": "เกรดเฉลี่ย",
    "ใครสอน": "อาจารย์ วิชาที่สอน",
    "สอน": "วิชาที่สอน",
    "หัวหน้าภาค": "หัวหน้าภาควิชา",
    "แบบฟอร์ม": "แบบฟอร์ม คำร้อง",
    "ฟอร์ม": "แบบฟอร์ม คำร้อง",
    "เล่มหลักสูตร": "เอกสารหลักสูตร ดาวน์โหลด",
    "จุดเด่น": "จุดเด่นของหลักสูตร",
}


def expand_query(query: str) -> str:
    lowered = query.lower()
    extra = [target for word, target in QUERY_SYNONYMS.items() if word in lowered]
    return " ".join([query, *extra])


def ngrams(text: str, sizes: tuple[int, ...]) -> Counter[str]:
    words = WORD_RE.findall(text.lower())
    return Counter(
        word[i : i + n] for word in words for n in sizes for i in range(len(word) - n + 1)
    )


def _idf(counts: list[Counter[str]]) -> dict[str, float]:
    doc_freq = Counter(term for count in counts for term in count)
    total = len(counts)
    return {term: math.log((1 + total) / (1 + df)) + 1 for term, df in doc_freq.items()}


def _unit(weights: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(w * w for w in weights.values()))
    return {term: w / norm for term, w in weights.items()} if norm else {}


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class LexicalIndex:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        # The heading is repeated so a match on it counts more than a match in the body.
        texts = [f"{c.title} {c.section or ''} {c.section or ''} {c.text}" for c in chunks]
        rank_counts = [ngrams(t, RANK_NGRAMS) for t in texts]
        self.rank_idf = _idf(rank_counts)
        self.vectors = [_unit({t: tf * self.rank_idf[t] for t, tf in c.items()}) for c in rank_counts]
        self.gate_sets = [set(ngrams(t, (GATE_NGRAM,))) for t in texts]
        self.gate_idf = _idf([Counter(s) for s in self.gate_sets])
        self.unseen_idf = math.log(1 + len(chunks)) + 1

    def coverage(self, query: str) -> float:
        """Best share (0-1) of the query's 3-grams, weighted by IDF, found in one chunk."""
        grams = ngrams(query, (GATE_NGRAM,))
        total = sum(self.gate_idf.get(g, self.unseen_idf) for g in grams)
        if not total:
            return 0.0
        return max(
            sum(self.gate_idf[g] for g in grams if g in chunk_grams) / total
            for chunk_grams in self.gate_sets
        )

    def search(self, query: str, top_k: int, min_coverage: float) -> list[Hit]:
        expanded = expand_query(query)
        if not self.chunks or self.coverage(expanded) < min_coverage:
            return []
        query_vec = _unit(
            {t: tf * self.rank_idf[t] for t, tf in ngrams(expanded, RANK_NGRAMS).items() if t in self.rank_idf}
        )
        hits = [
            Hit(chunk, sum(w * vec.get(t, 0.0) for t, w in query_vec.items()))
            for chunk, vec in zip(self.chunks, self.vectors)
        ]
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return [hit for hit in hits[:top_k] if hit.score > 0]
