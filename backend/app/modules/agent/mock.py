"""Day 1 mock responses so the frontend can call /api/chat before the real agent exists.

TEMPORARY: removed before M3 (no mock allowed in the real flow after Day 3).
All course/skill values below are placeholders, not real curriculum data.
"""
import re
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.contract import (
    Action,
    ActionPayload,
    AgentResponse,
    AssessmentFormData,
    AssessmentOption,
    AssessmentQuestion,
    CardsData,
    ChatRequest,
    Course,
    CourseTableData,
    ErrorData,
    InfoCard,
    ResponseMeta,
    SkillRadarData,
    SkillScores,
    Source,
)

_SCALE = ["ไม่เคยเลย", "เคยได้ยิน", "เคยลองทำ", "ทำได้", "ทำได้ดี / สอนคนอื่นได้"]
_FORCE_TYPE = re.compile(r"^mock:(text|course_table|cards|assessment_form|skill_radar|error)\b")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ask(label: str, text: str) -> Action:
    return Action(type="ask", label=label, payload=ActionPayload(text=text))


def _course_table(year: int, semester: int) -> dict:
    courses = [
        Course(
            code=f"MOCK-{year}{semester}{i}",
            name_th=f"[MOCK] วิชาตัวอย่าง {i}",
            name_en=f"[MOCK] Sample Course {i}",
            credits=3,
            credit_detail="3(2-3-5)",
            category="[MOCK] หมวดวิชาเฉพาะ",
            description=None,
            year=year,
            semester=semester,
        )
        for i in range(1, 4)
    ]
    other = 2 if semester == 1 else 1
    return {
        "message": f"[MOCK] รายวิชาของ **ปี {year} เทอม {semester}**",
        "response_type": "course_table",
        "data": CourseTableData(
            year=year, semester=semester, courses=courses, total_credits=sum(c.credits for c in courses)
        ),
        "actions": [_ask(f"ดูปี {year} เทอม {other}", f"ปี {year} เทอม {other} เรียนอะไรบ้าง")],
        "intent": "curriculum",
        "tool": "curriculum.get_courses",
    }


def _cards() -> dict:
    return {
        "message": "[MOCK] รายละเอียดวิชา",
        "response_type": "cards",
        "data": CardsData(
            cards=[InfoCard(title="[MOCK] วิชาตัวอย่าง", body="คำอธิบายรายวิชา **ตัวอย่าง**", icon="cpu", tags=["mock"])]
        ),
        "intent": "course_detail",
        "tool": "curriculum.get_course_detail",
    }


def _assessment_form() -> dict:
    options = [AssessmentOption(value=v, label=label) for v, label in enumerate(_SCALE)]
    return {
        "message": "[MOCK] ยังไม่มีข้อมูล skill ของคุณ ลองตอบคำถามเหล่านี้ก่อนนะ",
        "response_type": "assessment_form",
        "data": AssessmentFormData(
            assessment_id="skill_v1",
            title="[MOCK] ประเมินความถนัดสาย Computer Engineering",
            questions=[
                AssessmentQuestion(id="q1", text="[MOCK] คำถามตัวอย่างข้อ 1", options=options),
                AssessmentQuestion(id="q2", text="[MOCK] คำถามตัวอย่างข้อ 2", options=options),
            ],
        ),
        "intent": "skill_analysis",
        "tool": "skill.get_assessment",
    }


def _skill_radar() -> dict:
    scores = SkillScores(frontend=50, backend=50, network=50, embedded=50, ai_data=50, cybersecurity=50)
    return {
        "message": "[MOCK] ผลประเมิน skill ของคุณ",
        "response_type": "skill_radar",
        "data": SkillRadarData(
            scores=scores, top_skills=["frontend", "backend"], summary="[MOCK] สรุปผลประเมิน", taken_at=_now()
        ),
        "intent": "skill_analysis",
        "tool": "skill.calculate_skill",
    }


def _text() -> dict:
    return {
        "message": "[MOCK] สวัสดีครับ ผม COPIE ผู้ช่วยภาควิชาวิศวกรรมคอมพิวเตอร์ ตอนนี้ยังเป็นคำตอบจำลองอยู่นะครับ [1]",
        "response_type": "text",
        "data": None,
        "sources": [
            Source(doc_id="mock-doc", title="[MOCK] เอกสารตัวอย่าง", section="ตัวอย่าง", url=None, snippet="ข้อความตัวอย่าง", score=0.9)
        ],
        "actions": [_ask("ปี 1 เทอม 1 เรียนอะไร", "ปี 1 เทอม 1 เรียนอะไรบ้าง"), _ask("ประเมิน skill", "อยากประเมิน skill")],
        "intent": "department_info",
        "tool": "rag.search_department_knowledge",
    }


def _error() -> dict:
    return {
        "message": "[MOCK] ขออภัย ระบบขัดข้องชั่วคราว ลองใหม่อีกครั้งนะครับ",
        "response_type": "error",
        "data": ErrorData(code="llm_unavailable"),
        "intent": "general",
        "tool": None,
    }


def _clarify_curriculum() -> dict:
    return {
        "message": "[MOCK] อยากดูรายวิชาของปีไหน เทอมไหนครับ",
        "response_type": "text",
        "data": None,
        "actions": [_ask(f"ปี {y} เทอม {s}", f"ปี {y} เทอม {s} เรียนอะไรบ้าง") for y in (1, 2) for s in (1, 2)],
        "intent": "clarify",
        "tool": None,
    }


def _build(conversation_id: str | None, parts: dict) -> AgentResponse:
    return AgentResponse(
        conversation_id=conversation_id or str(uuid4()),
        message_id=str(uuid4()),
        message=parts["message"],
        response_type=parts["response_type"],
        data=parts["data"],
        sources=parts.get("sources", []),
        actions=parts.get("actions", []),
        meta=ResponseMeta(intent=parts["intent"], tool=parts["tool"], latency_ms=0),
    )


def mock_chat(req: ChatRequest) -> AgentResponse:
    """Keyword mock: "ปี N เทอม M" -> course_table, skill words -> assessment_form, else text.

    Prefix a message with `mock:<response_type>` to force any response type for UI work.
    """
    text = req.message.strip()
    forced = _FORCE_TYPE.match(text)
    if forced:
        kind = forced.group(1)
        builders = {
            "text": _text,
            "course_table": lambda: _course_table(1, 1),
            "cards": _cards,
            "assessment_form": _assessment_form,
            "skill_radar": _skill_radar,
            "error": _error,
        }
        return _build(req.conversation_id, builders[kind]())

    lowered = text.lower()
    if re.search(r"skill|ถนัด|ประเมิน", lowered):
        parts = _assessment_form()
    elif "ปี" in text or "เทอม" in text:
        year = re.search(r"ปี\s*([1-4])", text)
        semester = re.search(r"เทอม\s*([12])", text)
        parts = (
            _course_table(int(year.group(1)), int(semester.group(1))) if year and semester else _clarify_curriculum()
        )
    elif re.search(r"วิชา", text):
        parts = _cards()
    else:
        parts = _text()
    return _build(req.conversation_id, parts)
