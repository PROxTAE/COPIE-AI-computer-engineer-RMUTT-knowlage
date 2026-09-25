"""handle_chat(): route the message, fill missing info, call the right tool, build an AgentResponse.

Curriculum and skill answers are built from tool data with templates (no LLM), so they keep
working when the LLM is down. The endpoint never returns 500 for agent failures: they become
response_type="error" with a code the UI can show.
"""
import logging
import time
from dataclasses import dataclass, field
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.modules.agent import generator, intent_router, services
from app.modules.agent.llm_client import LLMError
from app.modules.agent.types import RouteResult
from app.schemas.contract import (
    Action,
    ActionPayload,
    AgentResponse,
    AssessmentSubmit,
    CardsData,
    ChatRequest,
    Course,
    ErrorData,
    InfoCard,
    ResponseMeta,
    SkillProfile,
    SkillRadarData,
    User,
)

log = logging.getLogger(__name__)

STUDENT_TYPES = ("current_student", "near_graduate")
RETAKE_WORDS = ("ใหม่", "อีกครั้ง", "อีกรอบ", "ทำซ้ำ")
SUBMIT_TEXT = "ส่งแบบประเมิน skill"
TERM_WORDS = ("เทอม", "ภาคเรียน", "ปีนี้", "ปีหน้า")  # asks about a specific term, not the whole program
SNIPPET_CHARS = 300


@dataclass
class Reply:
    message: str
    intent: str
    response_type: str = "text"
    data: object = None
    tool: str | None = None
    sources: list = field(default_factory=list)
    actions: list = field(default_factory=list)


def ask(label: str, text: str) -> Action:
    return Action(type="ask", label=label, payload=ActionPayload(text=text))


def error_reply(code: str, intent: str, tool: str | None = None) -> Reply:
    messages = {
        "llm_unavailable": "ขออภัยครับ ตอนนี้ระบบตอบคำถามขัดข้องชั่วคราว ลองใหม่อีกครั้งนะครับ",
        "tool_failed": "ขออภัยครับ ดึงข้อมูลไม่สำเร็จ ลองใหม่อีกครั้งนะครับ",
        "unknown": "ขออภัยครับ เกิดข้อผิดพลาดบางอย่าง ลองใหม่อีกครั้งนะครับ",
    }
    return Reply(messages[code], intent, "error", ErrorData(code=code), tool)


def handle_chat(db, user: User, req: ChatRequest) -> AgentResponse:
    started = time.perf_counter()
    context = services.get_user_context(db, user.id)
    profile: User = _field(context, "user") or user
    conversation_id = services.get_or_create_conversation(db, user.id, req.conversation_id, req.message)
    recent = services.get_recent_messages(db, conversation_id)
    services.add_user_message(db, conversation_id, req.message)

    route = intent_router.route(req.message, profile.user_type, profile.study_year, recent)
    log.info("route intent=%s source=%s", route.intent, route.source)
    try:
        reply = dispatch(db, route, req.message, profile, _field(context, "skill"), recent)
    except Exception:  # a failing tool must not become an HTTP 500
        log.exception("tool failed for intent=%s", route.intent)
        reply = error_reply("tool_failed", route.intent)

    response = build_response(conversation_id, reply, started)
    try:
        services.add_assistant_message(db, conversation_id, response)
    except Exception:  # the answer is still valid if saving history fails
        log.exception("could not save assistant message")
    return response


def build_response(conversation_id: str, reply: Reply, started: float) -> AgentResponse:
    meta = {"intent": reply.intent, "tool": reply.tool, "latency_ms": int((time.perf_counter() - started) * 1000)}
    payload = {
        "conversation_id": conversation_id,
        "message_id": str(uuid4()),
        "message": reply.message,
        "response_type": reply.response_type,
        "data": reply.data,
        "sources": reply.sources,
        "actions": reply.actions,
        "meta": ResponseMeta(**meta),
    }
    try:
        return AgentResponse.model_validate(payload)
    except ValidationError:
        log.exception("response does not match the contract")
        fallback = error_reply("unknown", reply.intent, reply.tool)
        return AgentResponse(
            conversation_id=conversation_id,
            message_id=payload["message_id"],
            message=fallback.message,
            response_type="error",
            data=fallback.data,
            meta=ResponseMeta(**meta),
        )


def dispatch(db, route: RouteResult, message: str, profile: User, skill, recent: list[dict]) -> Reply:
    if route.intent == "curriculum":
        return curriculum(route, message, profile)
    if route.intent == "course_detail":
        return course_detail(route, message)
    if route.intent == "department_info":
        return department_info(route.search_query or message)
    if route.intent == "skill_analysis":
        return skill_analysis(db, profile, skill, retake=any(w in message for w in RETAKE_WORDS))
    if route.intent == "clarify":
        return clarify()
    return general(message, profile, recent)


# ---------- curriculum ----------


def curriculum(route: RouteResult, message: str, profile: User) -> Reply:
    year = route.year or (profile.study_year if profile.user_type in STUDENT_TYPES else None)
    semester = route.semester
    if route.year is None and semester is None and not any(w in message for w in TERM_WORDS):
        return curriculum_overview()
    if year is None:
        return Reply(
            "อยากดูรายวิชาของชั้นปีไหนครับ",
            "clarify",
            actions=[ask(f"ปี {y}", f"ปี {y} เรียนอะไรบ้าง") for y in range(1, 5)],
        )
    if semester is None:
        return Reply(
            f"อยากดูรายวิชาของ **ปี {year}** เทอมไหนครับ",
            "clarify",
            actions=[ask(f"ปี {year} เทอม {s}", f"ปี {year} เทอม {s} เรียนอะไรบ้าง") for s in (1, 2)],
        )

    table = services.get_courses(year, semester)
    tool = "curriculum.get_courses"
    if table is None:
        return Reply(f"ยังไม่มีข้อมูลรายวิชาของ **ปี {year} เทอม {semester}** ในระบบครับ", "curriculum", tool=tool)
    other = 2 if semester == 1 else 1
    actions = [ask(f"ดูปี {year} เทอม {other}", f"ปี {year} เทอม {other} เรียนอะไรบ้าง")]
    if semester == 2 and year < 4:
        actions.append(ask(f"ดูปี {year + 1} เทอม 1", f"ปี {year + 1} เทอม 1 เรียนอะไรบ้าง"))
    return Reply(
        f"นี่คือรายวิชาของ **ปี {year} เทอม {semester}** รวม {table.total_credits} หน่วยกิตครับ",
        "curriculum",
        "course_table",
        table,
        tool,
        actions=actions,
    )


def curriculum_overview() -> Reply:
    overview = services.get_curriculum_overview()
    tool = "curriculum.get_curriculum_overview"
    if not overview.cards:
        return Reply("ยังไม่มีข้อมูลภาพรวมหลักสูตรในระบบครับ", "curriculum", tool=tool)
    return Reply(
        "ภาพรวมหลักสูตรแต่ละชั้นปีครับ",
        "curriculum",
        "cards",
        overview,
        tool,
        actions=[ask(f"ปี {y} เทอม 1", f"ปี {y} เทอม 1 เรียนอะไรบ้าง") for y in range(1, 5)],
    )


# ---------- course detail ----------


def course_detail(route: RouteResult, message: str) -> Reply:
    course = services.get_course_detail(route.course_query or message)
    if course is None:
        return department_info(message)
    return Reply(
        f"ข้อมูลวิชา **{course.code} {course.name_th}** ครับ",
        "course_detail",
        "cards",
        CardsData(cards=[course_card(course)]),
        "curriculum.get_course_detail",
        actions=[ask(f"ดูปี {course.year} เทอม {course.semester}", f"ปี {course.year} เทอม {course.semester} เรียนอะไรบ้าง")],
    )


def course_card(course: Course) -> InfoCard:
    credits = course.credit_detail or str(course.credits)
    lines = [f"**{course.name_en}**", f"- หน่วยกิต: {credits}", f"- เรียนปี {course.year} เทอม {course.semester}"]
    if course.category:
        lines.append(f"- หมวด: {course.category}")
    if course.description:
        lines += ["", course.description]
    tags = [t for t in (course.category, f"ปี {course.year} เทอม {course.semester}") if t]
    return InfoCard(title=f"{course.code} {course.name_th}", body="\n".join(lines), icon="book-open", tags=tags)


# ---------- department info (RAG) ----------


def department_info(query: str) -> Reply:
    tool = "rag.search_department_knowledge"
    chunks = services.search_department_knowledge(query)
    if not chunks:
        return Reply(
            "ยังไม่พบข้อมูลนี้ในเอกสารของภาคครับ ลองถามเรื่องอื่นเกี่ยวกับภาควิชาดูไหมครับ",
            "department_info",
            tool=tool,
            actions=[ask("ภาคเรียนเกี่ยวกับอะไร", "ภาควิชาวิศวกรรมคอมพิวเตอร์เรียนเกี่ยวกับอะไร"),
                     ask("จบไปทำอาชีพอะไร", "จบวิศวกรรมคอมพิวเตอร์ไปทำอาชีพอะไรได้บ้าง")],
        )
    sources = [c.source for c in chunks]
    try:
        message = generator.answer_from_rag(query, chunks)
    except LLMError:
        log.warning("rag generator unavailable, showing the top document snippet")
        first = chunks[0]
        message = (
            f"ตอนนี้ระบบสรุปคำตอบขัดข้อง ขอแสดงข้อความจากเอกสารที่เกี่ยวข้องที่สุดแทนครับ [1]\n\n"
            f"> {first.text[:SNIPPET_CHARS]}"
        )
    return Reply(message, "department_info", tool=tool, sources=sources)


# ---------- skill ----------


def skill_analysis(db, profile: User, skill: SkillProfile | None, retake: bool = False) -> Reply:
    skill = None if retake else skill or services.get_latest_skill(db, profile.id)
    if skill is None:
        return Reply(
            "ทำแบบประเมินใหม่ได้เลยครับ ผลล่าสุดจะใช้แทนผลเดิม"
            if retake
            else "ยังไม่มีข้อมูล skill ของคุณ ลองตอบแบบประเมินนี้ก่อนนะครับ",
            "skill_analysis",
            "assessment_form",
            services.get_assessment(),
            "skill.get_assessment",
        )
    return skill_radar(skill, profile, "skill.get_latest_skill")


def skill_radar(skill: SkillProfile, profile: User, tool: str) -> Reply:
    try:
        summary = generator.explain_skill(skill.scores, skill.top_skills, profile.user_type, profile.study_year)
    except LLMError:
        summary = generator.skill_summary_template(skill.top_skills)
    data = SkillRadarData(scores=skill.scores, top_skills=skill.top_skills, summary=summary, taken_at=skill.taken_at)
    return Reply(
        "นี่คือผลประเมิน skill ของคุณครับ",
        "skill_analysis",
        "skill_radar",
        data,
        tool,
        actions=[ask("ทำแบบประเมินใหม่", "ขอทำแบบประเมิน skill ใหม่")],
    )


def handle_assessment_submit(db, user: User, req: AssessmentSubmit) -> AgentResponse:
    """Score the answers with the skill tool (formula, not the LLM), save the profile, return a radar."""
    started = time.perf_counter()
    conversation_id = services.get_or_create_conversation(db, user.id, req.conversation_id, SUBMIT_TEXT)
    try:
        form = services.get_assessment()
    except Exception:  # the tool may be unavailable; answer with an error instead of a 500
        log.exception("get_assessment failed")
        return build_response(conversation_id, error_reply("tool_failed", "skill_analysis"), started)
    check_answers(req, {q.id for q in form.questions}, form.assessment_id)

    services.add_user_message(db, conversation_id, SUBMIT_TEXT)
    profile: User = _field(services.get_user_context(db, user.id), "user") or user
    try:
        scores = services.calculate_skill(req.answers)
        skill = services.save_skill_profile(db, user.id, scores, req.answers)
        reply = skill_radar(skill, profile, "skill.calculate_skill")
    except Exception:  # scoring or saving failed; the UI shows a retry button
        log.exception("assessment submit failed")
        reply = error_reply("tool_failed", "skill_analysis")
    response = build_response(conversation_id, reply, started)
    try:
        services.add_assistant_message(db, conversation_id, response)
    except Exception:  # the answer is still valid if saving history fails
        log.exception("could not save assistant message")
    return response


def check_answers(req: AssessmentSubmit, question_ids: set[str], assessment_id: str) -> None:
    if req.assessment_id != assessment_id:
        raise HTTPException(status_code=422, detail="แบบประเมินนี้ไม่ใช่เวอร์ชันปัจจุบัน กรุณาเริ่มทำใหม่")
    answered = [a.question_id for a in req.answers]
    if len(answered) != len(set(answered)) or set(answered) != question_ids:
        raise HTTPException(status_code=422, detail="กรุณาตอบแบบประเมินให้ครบทุกข้อ ข้อละหนึ่งคำตอบ")


# ---------- general / clarify ----------


def general(message: str, profile: User, recent: list[dict]) -> Reply:
    try:
        text = generator.general_answer(message, profile.user_type, profile.study_year, recent)
    except LLMError:
        return error_reply("llm_unavailable", "general")
    return Reply(text, "general")


def clarify() -> Reply:
    return Reply(
        "ขอรายละเอียดเพิ่มอีกนิดได้ไหมครับ ตอนนี้ COPIE ช่วยเรื่องเหล่านี้ได้",
        "clarify",
        actions=[
            ask("ข้อมูลภาควิชา", "ภาควิชาวิศวกรรมคอมพิวเตอร์เรียนเกี่ยวกับอะไร"),
            ask("รายวิชาแต่ละเทอม", "ปี 1 เทอม 1 เรียนอะไรบ้าง"),
            ask("ประเมิน skill", "ช่วยวิเคราะห์ skill ของผม"),
        ],
    )


def _field(context, name: str):
    """UserContext may be a dict or an object depending on the user module."""
    if context is None:
        return None
    return context.get(name) if isinstance(context, dict) else getattr(context, name, None)
