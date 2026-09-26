import pytest

from app.modules.rag import reranker, retriever, service
from app.modules.rag.scope import mentions_other_unit
from app.modules.rag.thai_text import BM25Index, tokenize

from .retrieval_cases import HELD_OUT, HELD_OUT_2, IN_SCOPE


def keyword_scorer(pairs):
    """Fake reranker: 1.0 only for the chunk with the 16,000 baht fee, else 0.001 (below MIN_RELEVANCE)."""
    return [1.0 if "16,000" in text else 0.001 for _query, text in pairs]


@pytest.fixture
def fake_reranker(monkeypatch):
    monkeypatch.setattr(service, "USE_RERANKER", True)
    monkeypatch.setattr(reranker, "load_scorer", lambda *a, **k: keyword_scorer)


# ---------- Thai tokenizer / BM25 ----------

def test_tokenize_keeps_department_words_whole() -> None:
    assert "สหกิจศึกษา" in tokenize("ออกสหกิจศึกษาต้องได้เกรดเฉลี่ยเท่าไหร่")
    assert "หน่วยกิต" in tokenize("หลักสูตรมีกี่หน่วยกิต")


def test_tokenize_drops_stopwords_but_keeps_meaningful_ones() -> None:
    tokens = tokenize("ภาคนี้เรียนอะไรบ้าง")
    assert "ภาค" in tokens and "เรียน" in tokens
    assert "อะไร" not in tokens and "บ้าง" not in tokens


def test_bm25_finds_the_fee_page() -> None:
    idx = service._indexes()
    ids = idx.bm25.search("ค่าเทอมเท่าไหร่", 3)
    assert ids and idx.by_id[ids[0]].doc_id == "tuition-fees"


def test_bm25_on_empty_corpus() -> None:
    assert BM25Index([]).search("อะไรก็ได้", 3) == []


# ---------- scope rule ----------

@pytest.mark.parametrize(
    "query",
    ["ภาคไฟฟ้าเรียนอะไร", "ภาควิชาวิศวกรรมไฟฟ้าเรียนอะไร", "วิศวะโยธาจบไปทำอะไร", "คณะบริหารธุรกิจค่าเทอมเท่าไหร่",
     "จุฬาเปิดรับสมัครเมื่อไหร่", "ราชมงคลล้านนามีภาคคอมไหม", "ภาควิชาเคมีอยู่ตึกไหน"],
)
def test_other_units_are_out_of_scope(query: str) -> None:
    assert mentions_other_unit(query)
    assert service.search_department_knowledge(query) == []


@pytest.mark.parametrize(
    "query",
    ["วิชาวิศวกรรมซอฟต์แวร์เรียนอะไร", "ภาคการศึกษาฤดูร้อนจ่ายเท่าไหร่", "คณะวิศวกรรมศาสตร์อยู่ที่ไหน",
     "จบ ปวส. ไฟฟ้าสมัครได้ไหม", "ภาคคอมกับภาคไฟฟ้าต่างกันยังไง"],
)
def test_own_department_questions_are_in_scope(query: str) -> None:
    assert not mentions_other_unit(query)


def test_no_evaluation_question_is_flagged_as_other_unit() -> None:
    flagged = [q for q, _ in IN_SCOPE + HELD_OUT + HELD_OUT_2 if mentions_other_unit(q)]
    assert flagged == []


# ---------- reranking ----------

def test_rerank_orders_by_score() -> None:
    idx = service._indexes()
    fee = next(c for c in idx.chunks if "16,000" in c.text)
    chunks = [idx.by_id["contact#0"], fee]
    ranked = reranker.rerank("ค่าเทอม", chunks, keyword_scorer)
    assert [c.doc_id for c, _ in ranked] == ["tuition-fees", "contact"]


def test_scores_come_from_reranker_and_irrelevant_chunks_are_dropped(fake_reranker) -> None:
    results = service.search_department_knowledge("ค่าเทอมเท่าไหร่")
    assert results
    assert all(r.source.doc_id == "tuition-fees" and r.source.score == 1.0 for r in results)
    assert all("16,000" in r.text for r in results)


def test_nothing_relevant_returns_empty(fake_reranker) -> None:
    assert service.search_department_knowledge("หัวหน้าภาควิชาคือใคร") == []


# ---------- fallbacks and retry ----------

def test_keyword_fallback_without_models() -> None:
    results = service.search_department_knowledge("ค่าเทอมเท่าไหร่")
    assert results and results[0].source.doc_id == "tuition-fees"


def test_vector_failure_falls_back_to_bm25(monkeypatch) -> None:
    def broken(_query, _k):
        raise RuntimeError("chroma error")

    monkeypatch.setattr(service, "USE_VECTOR", True)
    monkeypatch.setattr(retriever, "sync_index", lambda _chunks: 53)
    monkeypatch.setattr(retriever, "vector_search", broken)
    results = service.search_department_knowledge("หัวหน้าภาควิชาคือใคร")
    assert results and results[0].source.doc_id == "staff"


def test_reranker_failure_falls_back_to_keyword_filter(monkeypatch) -> None:
    def broken(_pairs):
        raise RuntimeError("out of memory")

    monkeypatch.setattr(service, "USE_RERANKER", True)
    monkeypatch.setattr(reranker, "load_scorer", lambda *a, **k: broken)
    assert service.search_department_knowledge("ค่าเทอมเท่าไหร่")[0].source.doc_id == "tuition-fees"
    assert service.search_department_knowledge("สูตรต้มยำกุ้ง") == []


def test_failed_model_is_retried_after_wait(monkeypatch) -> None:
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise OSError("no internet")
        return "model"

    clock = [100.0]
    monkeypatch.setattr(service.time, "monotonic", lambda: clock[0])
    optional = service._Optional("test model", flaky)
    assert optional.get() is None
    assert optional.get() is None and len(calls) == 1  # still waiting
    clock[0] += service.RETRY_SECONDS + 1
    assert optional.get() == "model" and len(calls) == 2
    assert optional.get() == "model" and len(calls) == 2  # cached once loaded


def test_ensure_index_counts_chunks_without_models() -> None:
    assert service.ensure_index() > 0


def test_public_api_exports_profanity_check() -> None:
    from app.modules.rag import contains_profanity

    assert contains_profanity("ภาคนี้แม่งเรียนอะไร")
    assert not contains_profanity("ภาคนี้เรียนอะไร")
