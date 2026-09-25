"""LLM text generation for answers. Every function may raise LLMError; the orchestrator decides the fallback."""
from app.modules.agent.llm_client import generate_text
from app.modules.agent.prompts import (
    GENERAL_SYSTEM,
    RAG_SYSTEM,
    SKILL_NAMES_TH,
    SKILL_SYSTEM,
    USER_TYPE_TH,
)
from app.schemas.contract import RetrievedChunk, SkillScores


def answer_from_rag(question: str, chunks: list[RetrievedChunk]) -> str:
    documents = "\n\n".join(
        f"[{i}] {c.source.title}{' — ' + c.source.section if c.source.section else ''}\n{c.text}"
        for i, c in enumerate(chunks, start=1)
    )
    return generate_text(RAG_SYSTEM, f"เอกสาร:\n{documents}\n\nคำถาม: {question}")


def explain_skill(scores: SkillScores, top: list[str], user_type: str | None, study_year: int | None) -> str:
    lines = "\n".join(f"- {SKILL_NAMES_TH[k]}: {v}" for k, v in scores.model_dump().items())
    return generate_text(
        SKILL_SYSTEM,
        f"ผู้ใช้: {_who(user_type, study_year)}\nคะแนน:\n{lines}\n"
        f"ด้านเด่น: {', '.join(SKILL_NAMES_TH[k] for k in top)}",
    )


def general_answer(message: str, user_type: str | None, study_year: int | None, recent: list[dict]) -> str:
    history = "\n".join(f"{m.get('role')}: {m.get('text')}" for m in recent) or "-"
    return generate_text(
        GENERAL_SYSTEM,
        f"ผู้ใช้: {_who(user_type, study_year)}\nบทสนทนาล่าสุด:\n{history}\n\nข้อความ: {message}",
        temperature=0.5,
    )


def skill_summary_template(top: list[str]) -> str:
    """Summary without the LLM, used when it is unavailable."""
    names = " และ ".join(f"**{SKILL_NAMES_TH[k]}**" for k in top)
    return f"จากแบบประเมิน ด้านที่คุณโดดเด่นที่สุดคือ {names} ครับ (ผลจากการประเมินตนเอง ใช้เป็นแนวทางเท่านั้น)"


def _who(user_type: str | None, study_year: int | None) -> str:
    who = USER_TYPE_TH.get(user_type or "", "ไม่ทราบสถานะ")
    return f"{who} ชั้นปี {study_year}" if study_year else who
