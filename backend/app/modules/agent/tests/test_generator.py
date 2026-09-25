import pytest

from app.modules.agent import generator
from app.schemas.contract import RetrievedChunk, SkillScores, Source


@pytest.fixture
def captured(monkeypatch) -> dict:
    seen: dict = {}

    def fake(system: str, prompt: str, *, temperature: float = 0.3) -> str:
        seen.update(system=system, prompt=prompt)
        return "ok"

    monkeypatch.setattr(generator, "generate_text", fake)
    return seen


def chunk(doc_id: str, section: str | None, text: str) -> RetrievedChunk:
    return RetrievedChunk(text=text, source=Source(doc_id=doc_id, title=doc_id, section=section, snippet=text, score=1))


def test_rag_prompt_numbers_documents_in_order(captured) -> None:
    generator.answer_from_rag("ค่าเทอม", [chunk("fees", "ปกติ", "ข้อความ A"), chunk("faq", None, "ข้อความ B")])
    prompt = captured["prompt"]
    assert "[1] fees — ปกติ\nข้อความ A" in prompt
    assert "[2] faq\nข้อความ B" in prompt
    assert prompt.endswith("คำถาม: ค่าเทอม")
    assert "ห้ามเดา" in captured["system"]


def test_skill_prompt_contains_computed_scores(captured) -> None:
    scores = SkillScores(frontend=80, backend=70, network=10, embedded=20, ai_data=30, cybersecurity=0)
    generator.explain_skill(scores, ["frontend", "backend"], "current_student", 2)
    assert "- Frontend: 80" in captured["prompt"]
    assert "- Cybersecurity: 0" in captured["prompt"]
    assert "นักศึกษาปัจจุบัน ชั้นปี 2" in captured["prompt"]


def test_skill_summary_template_needs_no_llm() -> None:
    assert "**AI & Data** และ **Embedded / IoT**" in generator.skill_summary_template(["ai_data", "embedded"])
