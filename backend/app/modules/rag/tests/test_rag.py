import re
from datetime import date
from pathlib import Path

import pytest

from app.modules.rag import ensure_index, search_department_knowledge
from app.modules.rag.chunker import (
    REQUIRED_KEYS,
    KnowledgeFormatError,
    chunk_file,
    has_front_matter,
    load_chunks,
    parse_front_matter,
    split_sections,
)
from app.modules.rag.guard import contains_profanity
from app.modules.rag.service import KNOWLEDGE_DIR, SNIPPET_CHARS
from app.schemas.contract import RetrievedChunk

from .conftest import LIVE, live
from .retrieval_cases import (
    HELD_OUT,
    HELD_OUT_2,
    HELD_OUT_3,
    HELD_OUT_4,
    HELD_OUT_5,
    HELD_OUT_6,
    IN_SCOPE,
    OUT_OF_SCOPE,
    OUT_OF_SCOPE_2,
    OUT_OF_SCOPE_3,
    OUT_OF_SCOPE_4,
    OUT_OF_SCOPE_5,
    OUT_OF_SCOPE_6,
    OUT_OF_SCOPE_NEAR,
)

KNOWLEDGE_FILES = [p for p in sorted(KNOWLEDGE_DIR.glob("*.md")) if has_front_matter(p)]


# ---------- knowledge data ----------

def test_knowledge_dir_has_documents() -> None:
    assert len(KNOWLEDGE_FILES) >= 8


@pytest.mark.parametrize("path", KNOWLEDGE_FILES, ids=lambda p: p.name)
def test_front_matter_is_complete_and_real(path: Path) -> None:
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"), path.name)
    assert all(meta[key] for key in REQUIRED_KEYS)
    assert meta["doc_id"] == path.stem
    assert re.match(r"^https://[\w.-]+\.rmutt\.ac\.th/", meta["source_url"]), meta["source_url"]
    date.fromisoformat(meta["updated"])
    assert "## " in body


def test_doc_ids_are_unique() -> None:
    ids = [chunk_file(p)[0].doc_id for p in KNOWLEDGE_FILES]
    assert len(ids) == len(set(ids))


def test_every_knowledge_file_is_listed_in_sources() -> None:
    sources = (KNOWLEDGE_DIR / "SOURCES.md").read_text(encoding="utf-8")
    for path in KNOWLEDGE_FILES:
        assert f"| {path.stem} |" in sources, f"{path.name} missing from SOURCES.md"


def test_knowledge_text_does_not_trip_profanity_guard() -> None:
    for chunk in load_chunks(KNOWLEDGE_DIR):
        assert not contains_profanity(chunk.text), chunk.chunk_id


# ---------- chunker ----------

VALID_HEADER = "---\ndoc_id: x\ntitle: T\nsource_url: https://example.ac.th/\nupdated: 2026-09-25\n---\n"


def test_missing_front_matter_raises() -> None:
    with pytest.raises(KnowledgeFormatError, match="front-matter"):
        parse_front_matter("# no header\n## A\ntext", "bad.md")


def test_unclosed_front_matter_raises() -> None:
    with pytest.raises(KnowledgeFormatError, match="not closed"):
        parse_front_matter("---\ndoc_id: x\n", "bad.md")


def test_missing_required_key_names_the_key() -> None:
    raw = VALID_HEADER.replace("source_url: https://example.ac.th/\n", "")
    with pytest.raises(KnowledgeFormatError, match="source_url"):
        parse_front_matter(raw, "bad.md")


def test_split_sections_by_heading() -> None:
    sections = split_sections("# Title\nintro\n## A\nalpha\n## B\nbeta\n")
    assert sections == [(None, "intro"), ("A", "alpha"), ("B", "beta")]


def test_file_without_subheadings_is_one_chunk(tmp_path: Path) -> None:
    path = tmp_path / "x.md"
    path.write_text(VALID_HEADER + "# Title\nonly body text\n", encoding="utf-8")
    chunks = chunk_file(path)
    assert len(chunks) == 1
    assert chunks[0].section is None
    assert chunks[0].chunk_id == "x#0"


def test_file_saved_with_bom_is_read(tmp_path: Path) -> None:
    path = tmp_path / "x.md"
    path.write_text(VALID_HEADER + "## A\nalpha\n", encoding="utf-8-sig")
    assert [c.chunk_id for c in load_chunks(tmp_path)] == ["x#0"]


def test_files_without_front_matter_are_skipped(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# readme\n", encoding="utf-8")
    (tmp_path / "x.md").write_text(VALID_HEADER + "## A\nalpha\n", encoding="utf-8")
    assert [c.chunk_id for c in load_chunks(tmp_path)] == ["x#0"]


# ---------- search_department_knowledge ----------

def test_ensure_index_loads_chunks() -> None:
    assert ensure_index() > 0


def test_demo_question_returns_sources() -> None:
    results = search_department_knowledge("ภาควิชาวิศวกรรมคอมพิวเตอร์เรียนเกี่ยวกับอะไร")
    assert results
    assert all(isinstance(r, RetrievedChunk) for r in results)


def test_results_follow_contract() -> None:
    results = search_department_knowledge("ค่าเทอมเท่าไหร่", top_k=3)
    assert 0 < len(results) <= 3
    scores = [r.source.score for r in results]
    assert scores == sorted(scores, reverse=True)
    for r in results:
        assert r.source.url and r.source.url.startswith("https://")
        assert r.source.snippet == r.text[:SNIPPET_CHARS]
        assert r.source.title and r.source.doc_id


@pytest.mark.parametrize("query", ["", "   ", "เหี้ยอะไรเนี่ย", "ภาคนี้แม่งเรียนอะไร", "f u c k"])
def test_empty_or_profane_query_returns_nothing(query: str) -> None:
    assert search_department_knowledge(query) == []


def test_top_k_zero_returns_nothing() -> None:
    assert search_department_knowledge("ค่าเทอมเท่าไหร่", top_k=0) == []


FAQ_DOC = "faq-prospective"


def _docs_by_url() -> dict[str, set[str]]:
    by_url: dict[str, set[str]] = {}
    for chunk in load_chunks(KNOWLEDGE_DIR):
        if chunk.doc_id != FAQ_DOC:
            by_url.setdefault(chunk.url, set()).add(chunk.doc_id)
    return by_url


def _answering_docs(result: RetrievedChunk, by_url: dict[str, set[str]]) -> set[str]:
    """A FAQ answer restates the page in its "ที่มา:" link, so it counts as the documents from that page."""
    if result.source.doc_id == FAQ_DOC:
        return {FAQ_DOC} | by_url.get(result.source.url or "", set())
    return {result.source.doc_id}


def _hit_rates(cases: list[tuple[str, set[str]]]) -> tuple[float, float]:
    by_url = _docs_by_url()
    hit1 = hit4 = 0
    for question, expected in cases:
        answered = [_answering_docs(r, by_url) for r in search_department_knowledge(question, top_k=4)]
        hit1 += bool(answered) and bool(answered[0] & expected)
        hit4 += any(docs & expected for docs in answered)
    return hit1 / len(cases), hit4 / len(cases)


def _rejected(questions: list[str]) -> float:
    return sum(not search_department_knowledge(q) for q in questions) / len(questions)


# Floors are the measured results (16 documents incl. faq-prospective), so a change
# that makes retrieval worse fails. Only held_out_4/5/6 were written after every
# setting and document was fixed and never used to change them: the numbers to quote.
# tuning and held_out 1-3 reached 100% after the FAQ was written with their misses
# in view, so they overstate accuracy.
LIVE_ACCURACY = [
    ("tuning", IN_SCOPE, 1.0, 1.0),
    ("held_out", HELD_OUT, 1.0, 1.0),
    ("held_out_2", HELD_OUT_2, 1.0, 1.0),
    ("held_out_3", HELD_OUT_3, 1.0, 1.0),
    ("held_out_4", HELD_OUT_4, 0.95, 1.0),
    ("held_out_5", HELD_OUT_5, 0.86, 0.93),
    ("held_out_6", HELD_OUT_6, 0.88, 0.91),
]
LIVE_REJECTION = [
    ("tuning", OUT_OF_SCOPE + OUT_OF_SCOPE_NEAR, 1.0),
    ("held_out_2", OUT_OF_SCOPE_2, 1.0),
    ("held_out_3", OUT_OF_SCOPE_3, 1.0),
    ("held_out_4", OUT_OF_SCOPE_4, 0.95),
    ("held_out_5", OUT_OF_SCOPE_5, 0.8),
    ("held_out_6", OUT_OF_SCOPE_6, 0.9),
]
# Without the reranker (fallback path; plain `pytest` also runs without the vector
# model). Word + 3-gram keyword coverage filters scope, 3-gram keywords rank.
# It rejects most unrelated questions but also more answerable ones: keyword
# matching alone cannot reach the reranker's accuracy.
OFFLINE_ACCURACY = [
    ("tuning", IN_SCOPE, 0.78, 0.88),
    ("held_out", HELD_OUT, 0.83, 0.83),
    ("held_out_2", HELD_OUT_2, 0.85, 0.95),
    ("held_out_3", HELD_OUT_3, 0.64, 0.76),
    ("held_out_4", HELD_OUT_4, 0.72, 0.8),
    ("held_out_5", HELD_OUT_5, 0.66, 0.86),
    ("held_out_6", HELD_OUT_6, 0.53, 0.6),
]
OFFLINE_REJECTION = [
    ("tuning", OUT_OF_SCOPE, 1.0),
    ("near", OUT_OF_SCOPE_NEAR, 0.85),
    ("held_out_2", OUT_OF_SCOPE_2, 1.0),
    ("held_out_3", OUT_OF_SCOPE_3, 0.95),
    ("held_out_4", OUT_OF_SCOPE_4, 0.75),
    ("held_out_5", OUT_OF_SCOPE_5, 0.6),
    ("held_out_6", OUT_OF_SCOPE_6, 0.75),
]


@live
@pytest.mark.parametrize(("name", "cases", "min_hit1", "min_hit4"), LIVE_ACCURACY, ids=[a[0] for a in LIVE_ACCURACY])
def test_live_retrieval_accuracy(name: str, cases, min_hit1: float, min_hit4: float) -> None:
    hit1, hit4 = _hit_rates(cases)
    assert hit4 >= min_hit4, f"{name} hit@4 {hit4:.1%}"
    assert hit1 >= min_hit1, f"{name} hit@1 {hit1:.1%}"


@live
@pytest.mark.parametrize(("name", "questions", "minimum"), LIVE_REJECTION, ids=[r[0] for r in LIVE_REJECTION])
def test_live_out_of_scope_rejection(name: str, questions: list[str], minimum: float) -> None:
    assert _rejected(questions) >= minimum


@pytest.mark.skipif(LIVE, reason="measures the fallback path used without models")
@pytest.mark.parametrize(("name", "cases", "min_hit1", "min_hit4"), OFFLINE_ACCURACY, ids=[a[0] for a in OFFLINE_ACCURACY])
def test_fallback_retrieval_accuracy(name: str, cases, min_hit1: float, min_hit4: float) -> None:
    hit1, hit4 = _hit_rates(cases)
    assert hit4 >= min_hit4, f"{name} hit@4 {hit4:.1%}"
    assert hit1 >= min_hit1, f"{name} hit@1 {hit1:.1%}"


@pytest.mark.skipif(LIVE, reason="measures the fallback path used without models")
@pytest.mark.parametrize(("name", "questions", "minimum"), OFFLINE_REJECTION, ids=[r[0] for r in OFFLINE_REJECTION])
def test_fallback_out_of_scope_rejection(name: str, questions: list[str], minimum: float) -> None:
    assert _rejected(questions) >= minimum


# ---------- profanity guard ----------

@pytest.mark.parametrize("text", ["เหี้ยยยย", "ค ว ย", "สัสสส", "ไอ้สัตว์", "What the FUCK"])
def test_profanity_detected(text: str) -> None:
    assert contains_profanity(text)


@pytest.mark.parametrize(
    "text",
    [
        "จัดสัดส่วนพื้นที่", "ภาคอยู่ห่างจากกรุงเทพไหม", "หีบห่อพัสดุ", "ใบไม้เหี่ยว",
        "อาจารย์ผู้เชี่ยวชาญด้าน IoT", "แม่งานกิจกรรมรับน้อง", "ดอกทองกวาว", "ค่าเทอมเท่าไหร่",
    ],
)
def test_harmless_words_not_flagged(text: str) -> None:
    assert not contains_profanity(text)


# ---------- section sources ----------

def test_section_source_line_sets_chunk_url(tmp_path: Path) -> None:
    path = tmp_path / "x.md"
    path.write_text(
        VALID_HEADER + "## A\nalpha\n## B\nที่มา: https://other.ac.th/page/\n\nbeta\n", encoding="utf-8"
    )
    a, b = chunk_file(path)
    assert (a.url, a.text) == ("https://example.ac.th/", "alpha")
    assert (b.url, b.text) == ("https://other.ac.th/page/", "beta")


def test_every_chunk_links_to_a_real_page() -> None:
    for chunk in load_chunks(KNOWLEDGE_DIR):
        assert chunk.url.startswith("https://"), chunk.chunk_id
        assert not chunk.text.startswith("ที่มา:"), chunk.chunk_id


def test_fee_chunks_cite_the_page_that_states_them() -> None:
    chunks = [c for c in load_chunks(KNOWLEDGE_DIR) if c.doc_id == "tuition-fees"]
    sixteen = [c for c in chunks if "16,000" in c.text and "20,000" not in c.text]
    assert sixteen and all(c.url == "https://engineer.rmutt.ac.th/computer/" for c in sixteen)
