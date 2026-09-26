"""Orchestrator behaviour per intent. The router, tools and LLM are replaced with fakes.

Course/skill values below are test fixtures only, not curriculum data.
"""
from collections.abc import Generator

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.main import app
from app.modules.agent import orchestrator
from app.modules.agent.llm_client import LLMError
from app.modules.agent.types import RouteResult
from app.modules.user.models import User as UserRow
from app.schemas.contract import (
    AgentResponse,
    AssessmentFormData,
    AssessmentOption,
    AssessmentQuestion,
    CardsData,
    ChatRequest,
    Course,
    CourseTableData,
    InfoCard,
    RetrievedChunk,
    SkillProfile,
    SkillScores,
    Source,
    User,
)

STUDENT = User(id="u1", email="s@example.com", name="S", user_type="current_student", study_year=2, onboarded=True)
PROSPECT = User(id="u2", email="p@example.com", name="P", user_type="prospective", onboarded=True)
COURSE = Course(code="TEST-001", name_th="วิชาทดสอบ", name_en="Test Course", credits=3, credit_detail="3(2-2-5)",
                category="หมวดทดสอบ", description="คำอธิบาย", year=2, semester=1)
CHUNK = RetrievedChunk(text="ภาควิชาสอนเรื่องฮาร์ดแวร์และซอฟต์แวร์",
                       source=Source(doc_id="d1", title="ภาพรวม", section="เกี่ยวกับภาค", url=None, snippet="…", score=0.8))
FORM = AssessmentFormData(assessment_id="skill_v1", title="แบบทดสอบ", questions=[
    AssessmentQuestion(id="q1", text="คำถามทดสอบ", options=[AssessmentOption(value=0, label="ไม่เคย")])])
SKILL = SkillProfile(scores=SkillScores(frontend=80, backend=70, network=10, embedded=20, ai_data=30, cybersecurity=0),
                     top_skills=["frontend", "backend"], taken_at="2026-09-25T00:00:00Z")


def llm_down(*args, **kwargs):
    raise LLMError("down")


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            UserRow(
                id=STUDENT.id,
                email=STUDENT.email,
                name=STUDENT.name,
                user_type=STUDENT.user_type,
                study_year=STUDENT.study_year,
                onboarded=STUDENT.onboarded,
            )
        )
        db.commit()

    def test_session() -> Generator[Session, None, None]:
        with Session(engine) as db:
            yield db

    services = orchestrator.services
    assert services.get_current_user not in app.dependency_overrides
    assert services.get_session not in app.dependency_overrides
    app.dependency_overrides[services.get_current_user] = lambda: STUDENT
    app.dependency_overrides[services.get_session] = test_session
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.pop(services.get_current_user, None)
        app.dependency_overrides.pop(services.get_session, None)
        engine.dispose()
        assert services.get_current_user not in app.dependency_overrides
        assert services.get_session not in app.dependency_overrides


@pytest.fixture
def agent(monkeypatch):
    """Install fakes; returns a function that runs handle_chat for a route."""
    saved: list[AgentResponse] = []
    s = orchestrator.services
    monkeypatch.setattr(s, "get_or_create_conversation", lambda db, uid, cid, text: cid or "c1")
    monkeypatch.setattr(s, "get_recent_messages", lambda db, cid: [])
    monkeypatch.setattr(s, "add_user_message", lambda db, cid, text: "m1")
    monkeypatch.setattr(s, "add_assistant_message", lambda db, cid, resp: saved.append(resp))
    monkeypatch.setattr(s, "get_latest_skill", lambda db, uid: None)
    monkeypatch.setattr(s, "get_assessment", lambda: FORM)
    monkeypatch.setattr(s, "get_courses", lambda y, sem: CourseTableData(year=y, semester=sem, courses=[COURSE], total_credits=3))
    monkeypatch.setattr(s, "get_course_detail", lambda q: COURSE if q == "TEST-001" else None)
    monkeypatch.setattr(s, "get_curriculum_overview", lambda: CardsData(cards=[InfoCard(title="ปี 1", body="…")]))
    monkeypatch.setattr(s, "search_department_knowledge", lambda q: [CHUNK])
    g = orchestrator.generator
    monkeypatch.setattr(g, "answer_from_rag", lambda q, chunks: "ภาคสอนฮาร์ดแวร์และซอฟต์แวร์ [1]")
    monkeypatch.setattr(g, "explain_skill", lambda *a: "สรุปจาก LLM")
    monkeypatch.setattr(g, "general_answer", lambda *a: "สวัสดีครับ")

    def run(route: RouteResult, message: str = "ข้อความ", user: User = STUDENT, skill=None) -> AgentResponse:
        monkeypatch.setattr(s, "get_user_context", lambda db, uid: {"user": user, "skill": skill})
        monkeypatch.setattr(orchestrator.intent_router, "route", lambda *a: route)
        response = orchestrator.handle_chat(None, user, ChatRequest(message=message))
        AgentResponse.model_validate(response.model_dump())
        assert saved[-1] is response
        return response

    return run


def r(intent: str, **kw) -> RouteResult:
    return RouteResult(intent=intent, source="rule", **kw)


def test_curriculum_table(agent) -> None:
    resp = agent(r("curriculum", year=2, semester=1))
    assert resp.response_type == "course_table"
    assert resp.data.total_credits == 3
    assert resp.meta.tool == "curriculum.get_courses"
    assert resp.actions[0].payload.text == "ปี 2 เทอม 2 เรียนอะไรบ้าง"


def test_curriculum_uses_study_year_and_asks_semester(agent) -> None:
    resp = agent(r("curriculum"), "เทอมหน้าเรียนไร")
    assert (resp.response_type, resp.meta.intent) == ("text", "clarify")
    assert [a.label for a in resp.actions] == ["ปี 2 เทอม 1", "ปี 2 เทอม 2"]


def test_curriculum_without_year_asks_year(agent) -> None:
    resp = agent(r("curriculum"), "เทอมหน้าเรียนไร", user=PROSPECT)
    assert resp.meta.intent == "clarify"
    assert [a.label for a in resp.actions] == ["ปี 1", "ปี 2", "ปี 3", "ปี 4"]


def test_curriculum_overview(agent) -> None:
    resp = agent(r("curriculum"), "หลักสูตรมีกี่หน่วยกิต")
    assert (resp.response_type, resp.meta.tool) == ("cards", "curriculum.get_curriculum_overview")


def test_curriculum_term_without_data(agent, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator.services, "get_courses", lambda y, s: None)
    resp = agent(r("curriculum", year=4, semester=2))
    assert (resp.response_type, resp.meta.intent) == ("text", "curriculum")


def test_course_detail_card(agent) -> None:
    resp = agent(r("course_detail", course_query="TEST-001"))
    assert resp.response_type == "cards"
    assert resp.data.cards[0].title == "TEST-001 วิชาทดสอบ"


def test_unknown_course_falls_back_to_rag(agent) -> None:
    resp = agent(r("course_detail", course_query="ไม่มีวิชานี้"))
    assert (resp.response_type, resp.meta.intent) == ("text", "department_info")
    assert resp.sources


def test_department_info_with_sources(agent) -> None:
    resp = agent(r("department_info", search_query="ภาคเรียนอะไร"))
    assert "[1]" in resp.message
    assert resp.sources[0].doc_id == "d1"


def test_department_info_not_found(agent, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator.services, "search_department_knowledge", lambda q: [])
    resp = agent(r("department_info", search_query="ภาคไฟฟ้าเรียนอะไร"))
    assert "ไม่พบข้อมูล" in resp.message
    assert resp.sources == []


def test_department_info_llm_down_shows_snippet(agent, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator.generator, "answer_from_rag", llm_down)
    resp = agent(r("department_info", search_query="ภาคเรียนอะไร"))
    assert resp.response_type == "text"
    assert CHUNK.text in resp.message
    assert resp.sources


def test_skill_without_profile_returns_form(agent) -> None:
    resp = agent(r("skill_analysis"))
    assert (resp.response_type, resp.meta.tool) == ("assessment_form", "skill.get_assessment")


def test_skill_with_profile_returns_radar(agent) -> None:
    resp = agent(r("skill_analysis"), skill=SKILL)
    assert resp.response_type == "skill_radar"
    assert resp.data.scores == SKILL.scores
    assert resp.data.summary == "สรุปจาก LLM"


def test_skill_radar_works_without_llm(agent, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator.generator, "explain_skill", llm_down)
    resp = agent(r("skill_analysis"), skill=SKILL)
    assert resp.response_type == "skill_radar"
    assert "Frontend" in resp.data.summary


def test_general(agent) -> None:
    resp = agent(r("general"), "สวัสดี")
    assert (resp.response_type, resp.message) == ("text", "สวัสดีครับ")


def test_general_llm_down_is_error(agent, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator.generator, "general_answer", llm_down)
    resp = agent(r("general"), "สวัสดี")
    assert (resp.response_type, resp.data.code) == ("error", "llm_unavailable")


def test_clarify_offers_actions(agent) -> None:
    resp = agent(r("clarify"), "อันนั้นอะ")
    assert resp.response_type == "text"
    assert len(resp.actions) == 3


def test_tool_exception_is_error(agent, monkeypatch) -> None:
    def boom(*a):
        raise RuntimeError("db down")

    monkeypatch.setattr(orchestrator.services, "get_courses", boom)
    resp = agent(r("curriculum", year=1, semester=1))
    assert (resp.response_type, resp.data.code) == ("error", "tool_failed")


def test_api_chat_end_to_end(monkeypatch, api_client: TestClient) -> None:
    monkeypatch.setattr(orchestrator.intent_router, "route", lambda *a: r("clarify"))
    first = api_client.post("/api/chat", json={"conversation_id": None, "message": "อันนั้นอะ"})
    assert first.status_code == 200
    body = AgentResponse.model_validate(first.json())
    again = api_client.post("/api/chat", json={"conversation_id": body.conversation_id, "message": "ต่อ"})
    assert again.json()["conversation_id"] == body.conversation_id


def test_api_chat_forbidden_conversation(monkeypatch, api_client: TestClient) -> None:
    def forbidden(*a):
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงบทสนทนานี้")

    monkeypatch.setattr(orchestrator.services, "get_or_create_conversation", forbidden)
    response = api_client.post("/api/chat", json={"conversation_id": "someone-else", "message": "สวัสดี"})
    assert response.status_code == 403
