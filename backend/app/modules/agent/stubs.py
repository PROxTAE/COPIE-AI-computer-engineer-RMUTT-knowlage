"""TEMPORARY stand-ins for teammates' functions (contract §4) until their modules are merged.

services.py uses these only when the real function cannot be imported. They never invent
department/curriculum data: lookups return "not found"; the assessment questions are
clearly marked [STUB]. Remove this file before M3 (no stub allowed in the real flow).
"""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException

from app.schemas.contract import (
    SKILL_KEYS,
    AgentResponse,
    AssessmentAnswer,
    AssessmentFormData,
    AssessmentOption,
    AssessmentQuestion,
    CardsData,
    Course,
    CourseTableData,
    RetrievedChunk,
    SkillProfile,
    SkillScores,
    User,
)

# ---------- P4 rag ----------


def search_department_knowledge(query: str, top_k: int = 4) -> list[RetrievedChunk]:
    return []


# ---------- P5 curriculum ----------


def get_courses(year: int, semester: int) -> CourseTableData | None:
    return None


def get_course_detail(query: str) -> Course | None:
    return None


def get_curriculum_overview() -> CardsData:
    return CardsData(cards=[])


# ---------- P5 skill ----------

_SCALE = ["ไม่เคยเลย", "เคยได้ยิน", "เคยลองทำ", "ทำได้", "ทำได้ดี / สอนคนอื่นได้"]


def get_assessment() -> AssessmentFormData:
    options = [AssessmentOption(value=v, label=label) for v, label in enumerate(_SCALE)]
    return AssessmentFormData(
        assessment_id="skill_v1",
        title="[STUB] ประเมินความถนัดสาย Computer Engineering",
        questions=[
            AssessmentQuestion(id=f"q{i}", text=f"[STUB] คำถามด้าน {key}", options=options)
            for i, key in enumerate(SKILL_KEYS, start=1)
        ],
    )


def calculate_skill(answers: list[AssessmentAnswer]) -> SkillScores:
    by_id = {a.question_id: a.value for a in answers}
    return SkillScores(
        **{key: round(by_id.get(f"q{i}", 0) / 4 * 100) for i, key in enumerate(SKILL_KEYS, start=1)}
    )


def top_skills(scores: SkillScores, n: int = 2) -> list[str]:
    values = scores.model_dump()
    return sorted(SKILL_KEYS, key=lambda k: -values[k])[:n]


# ---------- P2 user (in-memory, lost on restart) ----------

_DEV_USER = User(id="stub-user", email="stub@example.com", name="Stub User", onboarded=True)
_conversations: dict[str, dict] = {}
_skills: dict[str, SkillProfile] = {}


def get_current_user() -> User:
    return _DEV_USER


def get_session():
    yield None


def get_user_context(db, user_id: str) -> dict:
    return {"user": _DEV_USER, "skill": _skills.get(user_id)}


def get_or_create_conversation(db, user_id: str, conversation_id: str | None, first_message: str) -> str:
    if conversation_id is None:
        conversation_id = str(uuid4())
        _conversations[conversation_id] = {"user_id": user_id, "title": first_message[:40], "messages": []}
        return conversation_id
    conversation = _conversations.setdefault(conversation_id, {"user_id": user_id, "title": "", "messages": []})
    if conversation["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงบทสนทนานี้")
    return conversation_id


def add_user_message(db, conversation_id: str, text: str) -> str:
    message_id = str(uuid4())
    _conversations[conversation_id]["messages"].append({"role": "user", "text": text})
    return message_id


def add_assistant_message(db, conversation_id: str, response: AgentResponse) -> None:
    _conversations[conversation_id]["messages"].append({"role": "assistant", "text": response.message})


def get_recent_messages(db, conversation_id: str, limit: int = 6) -> list[dict]:
    return _conversations.get(conversation_id, {"messages": []})["messages"][-limit:]


def save_skill_profile(db, user_id: str, scores: SkillScores, answers: list[AssessmentAnswer]) -> SkillProfile:
    profile = SkillProfile(
        scores=scores,
        top_skills=top_skills(scores),
        taken_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    _skills[user_id] = profile
    return profile


def get_latest_skill(db, user_id: str) -> SkillProfile | None:
    return _skills.get(user_id)
