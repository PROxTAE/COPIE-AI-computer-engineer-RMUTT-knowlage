"""LLM text generation for answers. Every function may raise LLMError; the orchestrator decides the fallback.

The interaction mode of the current request (normal | devil | developer) is set once by the orchestrator
with `interaction_mode(...)`; every prose prompt here gets that mode's style layer via `_styled`.
"""
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from app.modules.agent.llm_client import generate_text
from app.modules.agent.prompts import (
    COURSE_SYNTHESIS_SYSTEM,
    CURRICULUM_SYNTHESIS_SYSTEM,
    DYNAMIC_SKILL_EXPLAIN_SYSTEM,
    FALLBACK_NUDGE,
    GENERAL_SYSTEM,
    OVERVIEW_SYNTHESIS_SYSTEM,
    RAG_SYSTEM,
    SKILL_INQUIRY_SYSTEM,
    SKILL_NAMES_TH,
    SKILL_SYSTEM,
    STYLE_INSTRUCTIONS,
    USER_TYPE_TH,
    with_style,
)
from app.schemas.contract import Course, InfoCard, RetrievedChunk, SkillScores

_interaction_mode: ContextVar[str] = ContextVar("interaction_mode", default="normal")


@contextmanager
def interaction_mode(mode: str | None) -> Iterator[None]:
    """Use `mode`'s answer style for every generator call inside the block (unknown values -> normal)."""
    token = _interaction_mode.set(mode if mode in STYLE_INSTRUCTIONS else "normal")
    try:
        yield
    finally:
        _interaction_mode.reset(token)


def current_interaction_mode() -> str:
    return _interaction_mode.get()


def _styled(system: str) -> str:
    return with_style(system, _interaction_mode.get())


def answer_from_rag(
    question: str,
    chunks: list[RetrievedChunk],
    user_type: str | None = None,
    study_year: int | None = None,
    skill_context: str | None = None,
) -> str:
    documents = "\n\n".join(
        f"[{i}] {c.source.title}{' — ' + c.source.section if c.source.section else ''}\n{c.text}"
        for i, c in enumerate(chunks, start=1)
    )
    user_info = ""
    if user_type or study_year:
        user_info += f"ผู้ใช้: {_who(user_type, study_year)}\n"
    if skill_context:
        user_info += f"{skill_context}\n"
    prefix = f"{user_info}\n" if user_info else ""
    return generate_text(_styled(RAG_SYSTEM), f"{prefix}เอกสาร:\n{documents}\n\nคำถาม: {question}")


def explain_skill(scores: SkillScores, top: list[str], user_type: str | None, study_year: int | None) -> str:
    lines = "\n".join(f"- {SKILL_NAMES_TH.get(k, k)}: {v}" for k, v in scores.model_dump().items())
    return generate_text(
        _styled(SKILL_SYSTEM),
        f"ผู้ใช้: {_who(user_type, study_year)}\nคะแนน:\n{lines}\n"
        f"ด้านเด่น: {', '.join(SKILL_NAMES_TH.get(k, k) for k in top)}",
    )


def explain_dynamic_skill(
    topic: str,
    score: int,
    top_skills: list[str],
    user_type: str | None = None,
    study_year: int | None = None,
    dimensions: list | None = None,
) -> str:
    dim_lines = ""
    if dimensions:
        dim_lines = "\nคะแนนรายด้าน:\n" + "\n".join(
            f"- {getattr(d, 'label', d.get('label') if isinstance(d, dict) else str(d))}: {getattr(d, 'score', d.get('score') if isinstance(d, dict) else '')}/100"
            for d in dimensions
        )
    top_str = ", ".join(top_skills) if top_skills else ""
    prompt = (
        f"ผู้ใช้: {_who(user_type, study_year)}\n"
        f"หัวข้อทักษะ: {topic}\n"
        f"คะแนนรวม: {score}/100\n"
        f"ด้านที่โดดเด่น: {top_str}\n"
        f"{dim_lines}\n"
        f"ประเมินและให้คำแนะนำในการพัฒนาทักษะ {topic} โดยเชื่อมโยงด้านที่ทำได้ดีและด้านที่สามารถพัฒนาต่อยอดได้"
    )
    return generate_text(_styled(DYNAMIC_SKILL_EXPLAIN_SYSTEM), prompt)


def answer_skill_inquiry(
    message: str,
    skill_context: str,
    user_type: str | None = None,
    study_year: int | None = None,
    recent: list[dict] | None = None,
) -> str:
    history = "\n".join(f"{m.get('role')}: {m.get('text')}" for m in (recent or [])) or "-"
    prompt = (
        f"ผู้ใช้: {_who(user_type, study_year)}\n"
        f"{skill_context}\n\n"
        f"บทสนทนาล่าสุด:\n{history}\n\n"
        f"คำถามของผู้ใช้: {message}"
    )
    return generate_text(_styled(SKILL_INQUIRY_SYSTEM), prompt, temperature=0.4)


def general_answer(
    message: str,
    user_type: str | None,
    study_year: int | None,
    recent: list[dict],
    skill_context: str | None = None,
) -> str:
    history = "\n".join(f"{m.get('role')}: {m.get('text')}" for m in recent) or "-"
    skill_part = f"\n{skill_context}" if skill_context else ""
    return generate_text(
        _styled(GENERAL_SYSTEM),
        f"ผู้ใช้: {_who(user_type, study_year)}{skill_part}\nบทสนทนาล่าสุด:\n{history}\n\nข้อความ: {message}",
        temperature=0.5,
    )


def synthesize_curriculum_intro(
    year: int,
    semester: int,
    courses: list[Course],
    total_credits: int,
    user_type: str | None = None,
    study_year: int | None = None,
    skill_context: str | None = None,
) -> str:
    course_list = ", ".join(f"{c.code} {c.name_th} ({c.credits} นก.)" for c in courses[:6])
    prompt = (
        f"ผู้ใช้: {_who(user_type, study_year)}\n"
        f"{skill_context or ''}\n"
        f"ระดับ: ชั้นปี {year} ภาคเรียนที่ {semester}\n"
        f"จำนวนหน่วยกิตรวม: {total_credits} หน่วยกิต\n"
        f"ตัวอย่างรายวิชา: {course_list}\n"
        f"เขียนข้อความเกริ่นนำ แนะนำภาพรวมเทอมนี้และวิชาสำคัญอย่างเป็นกันเอง"
    )
    return generate_text(_styled(CURRICULUM_SYNTHESIS_SYSTEM), prompt, temperature=0.3)


def synthesize_curriculum_overview(
    cards: list[InfoCard],
    user_type: str | None = None,
    study_year: int | None = None,
    skill_context: str | None = None,
) -> str:
    prompt = (
        f"ผู้ใช้: {_who(user_type, study_year)}\n"
        f"{skill_context or ''}\n"
        f"หลักสูตรวิศวกรรมคอมพิวเตอร์ 4 ปี\n"
        f"เขียนข้อความสรุปภาพรวมการเรียนการสอนตลอด 4 ปีสั้นๆ ให้น่าสนใจ"
    )
    return generate_text(_styled(OVERVIEW_SYNTHESIS_SYSTEM), prompt, temperature=0.3)


def synthesize_course_detail(
    course: Course,
    user_type: str | None = None,
    study_year: int | None = None,
    skill_context: str | None = None,
) -> str:
    prompt = (
        f"ผู้ใช้: {_who(user_type, study_year)}\n"
        f"{skill_context or ''}\n"
        f"วิชา: {course.code} {course.name_th} ({course.name_en})\n"
        f"หน่วยกิต: {course.credits}, ปี {course.year} เทอม {course.semester}\n"
        f"คำอธิบาย: {course.description or '-'}\n"
        f"เขียนสรุปแนะนำวิชานี้และทักษะที่จะได้รับอย่างเป็นกันเองและกระชับ"
    )
    return generate_text(_styled(COURSE_SYNTHESIS_SYSTEM), prompt, temperature=0.3)


def skill_summary_template(top: list[str]) -> str:
    """Summary without the LLM, used when it is unavailable."""
    names = " และ ".join(f"**{SKILL_NAMES_TH.get(k, k)}**" for k in top)
    return with_fallback_style(
        f"จากแบบประเมิน ด้านที่คุณโดดเด่นที่สุดคือ {names} ครับ (ผลจากการประเมินตนเอง ใช้เป็นแนวทางเท่านั้น)"
    )


def with_fallback_style(text: str) -> str:
    """Template answer (LLM unavailable) with a one-line nudge in the current mode's tone."""
    return text + FALLBACK_NUDGE.get(_interaction_mode.get(), "")


def _who(user_type: str | None, study_year: int | None) -> str:
    who = USER_TYPE_TH.get(user_type or "", "ไม่ทราบสถานะ")
    return f"{who} ชั้นปี {study_year}" if study_year else who
