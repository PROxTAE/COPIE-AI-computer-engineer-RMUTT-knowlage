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
    IN_SCOPE,
    OUT_OF_SCOPE,
    OUT_OF_SCOPE_2,
    OUT_OF_SCOPE_3,
    OUT_OF_SCOPE_4,
    OUT_OF_SCOPE_5,
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


def _hit_rates(cases: list[tuple[str, set[str]]]) -> tuple[float, float]:
    hit1 = hit4 = 0
    for question, expected in cases:
        ids = [r.source.doc_id for r in search_department_knowledge(question, top_k=4)]
        hit1 += bool(ids) and ids[0] in expected
        hit4 += any(i in expected for i in ids)
    return hit1 / len(cases), hit4 / len(cases)


def _rejected(questions: list[str]) -> float:
    return sum(not search_department_knowledge(q) for q in questions) / len(questions)


# Floors are the measured results (15 documents), so a change that makes retrieval
# worse fails. held_out_4 and held_out_5 were written after every setting was fixed
# and never used to change it: the numbers to quote.
LIVE_ACCURACY = [
    ("tuning", IN_SCOPE, 0.98, 1.0),
    ("held_out", HELD_OUT, 1.0, 1.0),
    ("held_out_2", HELD_OUT_2, 0.9, 0.9),
    ("held_out_3", HELD_OUT_3, 0.84, 0.84),
    ("held_out_4", HELD_OUT_4, 0.95, 1.0),
    ("held_out_5", HELD_OUT_5, 0.86, 1.0),
]
LIVE_REJECTION = [
    ("tuning", OUT_OF_SCOPE + OUT_OF_SCOPE_NEAR, 1.0),
    ("held_out_2", OUT_OF_SCOPE_2, 1.0),
    ("held_out_3", OUT_OF_SCOPE_3, 1.0),
    ("held_out_4", OUT_OF_SCOPE_4, 0.95),
    ("held_out_5", OUT_OF_SCOPE_5, 0.8),
]
# Without the models (fallback path, also what plain `pytest` runs). It gets weaker
# as documents are added: the 3-gram filter and BM25 alone cannot tell similar pages apart.
OFFLINE_ACCURACY = [
    ("tuning", IN_SCOPE, 0.78, 0.96),
    ("held_out", HELD_OUT, 0.95, 1.0),
    ("held_out_2", HELD_OUT_2, 0.85, 0.85),
    ("held_out_3", HELD_OUT_3, 0.72, 0.92),
    ("held_out_4", HELD_OUT_4, 0.87, 0.97),
    ("held_out_5", HELD_OUT_5, 0.46, 0.86),
]
OFFLINE_REJECTION = [
    ("tuning", OUT_OF_SCOPE, 0.7),
    ("near", OUT_OF_SCOPE_NEAR, 0.6),
    ("held_out_2", OUT_OF_SCOPE_2, 0.8),
    ("held_out_3", OUT_OF_SCOPE_3, 0.75),
    ("held_out_4", OUT_OF_SCOPE_4, 0.65),
    ("held_out_5", OUT_OF_SCOPE_5, 0.4),
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
