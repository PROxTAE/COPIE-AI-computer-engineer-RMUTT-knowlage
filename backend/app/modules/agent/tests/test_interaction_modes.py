"""Interaction modes (normal | devil | developer) change the tone only: same route, tools, data and sources."""
import pytest
from fastapi.testclient import TestClient

from app.modules.agent import generator, orchestrator
from app.modules.agent.prompts import (
    DYNAMIC_SKILL_EXPLAIN_SYSTEM,
    PERSONA,
    RAG_SYSTEM,
    STYLE_INSTRUCTIONS,
    with_style,
)
from app.modules.agent.tests.test_orchestrator import (  # noqa: F401 - fixtures
    CHUNK,
    SKILL,
    agent,
    api_client,
    llm_down,
    r,
)
from app.schemas.contract import AgentResponse, AssessmentSubmit, ChatRequest, ResponseMeta

MODES = ("normal", "devil", "developer")


# ---------- prompts ----------


def test_normal_mode_keeps_the_original_prompt() -> None:
    assert with_style(RAG_SYSTEM, "normal") == RAG_SYSTEM
    assert with_style(RAG_SYSTEM, None) == RAG_SYSTEM


@pytest.mark.parametrize("mode", ["devil", "developer"])
def test_mode_swaps_persona_and_keeps_task_rules_first(mode: str) -> None:
    system = with_style(RAG_SYSTEM, mode)
    assert PERSONA not in system  # the polite default persona is replaced, not just appended to
    assert RAG_SYSTEM[len(PERSONA):].strip() in system
    assert system.index("ห้ามเดา") < system.index("[บุคลิก")
    assert "ห้ามเปลี่ยนข้อเท็จจริง" in system


def test_soft_tone_rules_are_dropped_outside_normal() -> None:
    assert "ให้กำลังใจผู้ใช้" in with_style(DYNAMIC_SKILL_EXPLAIN_SYSTEM, "normal")
    assert "ให้กำลังใจผู้ใช้" not in with_style(DYNAMIC_SKILL_EXPLAIN_SYSTEM, "devil")


def test_devil_is_harsh_on_excuses_but_not_on_the_person() -> None:
    devil = STYLE_INSTRUCTIONS["devil"]
    assert "ห้ามคำหยาบ" in devil
    assert "ห้ามบอกให้เลิกเรียน" in devil
    assert "ทำร้ายตัวเอง" in devil  # crisis is the only reason to drop the harsh tone


@pytest.fixture
def captured(monkeypatch) -> dict:
    seen: dict = {}

    def fake(system: str, prompt: str, *, temperature: float = 0.3) -> str:
        seen.update(system=system, prompt=prompt)
        return "ok"

    monkeypatch.setattr(generator, "generate_text", fake)
    return seen


def test_generator_uses_the_mode_of_the_block(captured) -> None:
    with generator.interaction_mode("developer"):
        generator.general_answer("debug ยังไง", "current_student", 2, [])
    assert "Developer Mode" in captured["system"]
    assert "Developer Mode" in captured["prompt"]  # reminder at the end of the user prompt
    generator.general_answer("debug ยังไง", "current_student", 2, [])
    assert "Developer Mode" not in captured["system"]
    assert captured["prompt"].endswith("ข้อความ: debug ยังไง")


def test_devil_answers_with_more_temperature(monkeypatch) -> None:
    seen: list[float] = []
    monkeypatch.setattr(generator, "generate_text", lambda system, prompt, *, temperature=0.3: seen.append(temperature) or "ok")
    generator.general_answer("x", None, None, [])
    with generator.interaction_mode("devil"):
        generator.general_answer("x", None, None, [])
    assert seen[1] > seen[0]


def test_unknown_mode_falls_back_to_normal(captured) -> None:
    with generator.interaction_mode("root"):
        assert generator.current_interaction_mode() == "normal"
        generator.general_answer("สวัสดี", None, None, [])
    assert "[บุคลิก" not in captured["system"]


def test_fallback_template_follows_the_mode() -> None:
    assert generator.with_fallback_style("ข้อมูล") == "ข้อมูล"
    with generator.interaction_mode("devil"):
        assert generator.with_fallback_style("ข้อมูล").startswith("ข้อมูล\n\n>")
    with generator.interaction_mode("developer"):
        assert "`next:`" in generator.skill_summary_template(["frontend"])


# ---------- orchestrator ----------


@pytest.mark.parametrize("mode", MODES)
def test_meta_records_the_request_mode(agent, mode: str) -> None:
    assert agent(r("clarify"), mode=mode).meta.interaction_mode == mode


def test_same_question_same_facts_in_every_mode(agent, monkeypatch) -> None:
    seen_modes: list[str] = []

    def rag(query, chunks, **kwargs):
        seen_modes.append(generator.current_interaction_mode())
        return "ภาคสอนฮาร์ดแวร์และซอฟต์แวร์ [1]"

    monkeypatch.setattr(orchestrator.generator, "answer_from_rag", rag)
    answers = [agent(r("department_info", search_query="ภาคเรียนอะไร"), mode=mode) for mode in MODES]
    assert seen_modes == list(MODES)
    assert {a.response_type for a in answers} == {"text"}
    assert all(a.sources == answers[0].sources == [CHUNK.source] for a in answers)
    assert {a.meta.tool for a in answers} == {"rag.search_department_knowledge"}


def test_course_table_data_is_identical_across_modes(agent) -> None:
    tables = [agent(r("curriculum", year=2, semester=1), mode=mode).data for mode in MODES]
    assert tables[0] == tables[1] == tables[2]


def test_skill_scores_do_not_change_with_mode(agent, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator.generator, "explain_skill", llm_down)
    radars = [agent(r("skill_analysis"), skill=SKILL, mode=mode).data for mode in MODES]
    assert all(radar.scores == SKILL.scores for radar in radars)
    assert "`next:`" in radars[2].summary


def test_llm_down_error_keeps_code_but_changes_tone(agent, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator.generator, "general_answer", llm_down)
    normal = agent(r("general"), "สวัสดี")
    devil = agent(r("general"), "สวัสดี", mode="devil")
    assert normal.data.code == devil.data.code == "llm_unavailable"
    assert normal.message != devil.message


def test_mode_does_not_leak_into_the_next_request(agent) -> None:
    agent(r("clarify"), mode="devil")
    assert generator.current_interaction_mode() == "normal"


# ---------- contract ----------


def test_requests_default_to_normal() -> None:
    assert ChatRequest(message="hi").interaction_mode == "normal"
    assert AssessmentSubmit(conversation_id="c", assessment_id="a", answers=[]).interaction_mode == "normal"


def test_history_without_mode_reads_as_normal() -> None:
    assert ResponseMeta.model_validate({"intent": "general", "tool": None, "latency_ms": 5}).interaction_mode == "normal"


def test_api_rejects_unknown_mode(api_client: TestClient) -> None:
    response = api_client.post("/api/chat", json={"conversation_id": None, "message": "สวัสดี", "interaction_mode": "admin"})
    assert response.status_code == 422


def test_api_echoes_mode(monkeypatch, api_client: TestClient) -> None:
    monkeypatch.setattr(orchestrator.intent_router, "route", lambda *a: r("clarify"))
    response = api_client.post("/api/chat", json={"conversation_id": None, "message": "อันนั้นอะ", "interaction_mode": "developer"})
    assert response.status_code == 200
    assert AgentResponse.model_validate(response.json()).meta.interaction_mode == "developer"
