"""handle_chat(): route the message, fill missing info, call the right tool, build an AgentResponse.

Every response is synthesized with conversational fluency via the LLM, incorporating
user profile and stored skill context. When LLM is down, robust template fallbacks ensure
continuity without 500 errors.

The request's interaction mode (normal | devil | developer) only changes the tone of prose:
routing, tool calls, data, scores and sources are produced exactly as in normal mode.
"""
import logging
import time
from dataclasses import dataclass, field
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.modules.agent import generator, intent_router, services
from app.modules.agent.dynamic_skill import (
    DYNAMIC_ASSESSMENTS,
    extract_skill_topic,
    format_user_skills_context,
    generate_dynamic_assessment_form,
    score_dynamic_assessment,
)
from app.modules.agent.llm_client import LLMError
from app.modules.agent.prompts import SKILL_NAMES_TH
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


ERROR_MESSAGES = {
    "normal": {
        "llm_unavailable": "ขออภัยครับ ตอนนี้ระบบตอบคำถามขัดข้องชั่วคราว ลองใหม่อีกครั้งนะครับ",
        "tool_failed": "ขออภัยครับ ดึงข้อมูลไม่สำเร็จ ลองใหม่อีกครั้งนะครับ",
        "unknown": "ขออภัยครับ เกิดข้อผิดพลาดบางอย่าง ลองใหม่อีกครั้งนะครับ",
    },
    "devil": {
        "llm_unavailable": "ระบบตอบคำถามขัดข้องชั่วคราวครับ ระหว่างนี้ลองคิดคำถามให้คมขึ้นอีกนิด แล้วส่งมาใหม่ครับ",
        "tool_failed": "ดึงข้อมูลไม่สำเร็จครับ ไม่ใช่ความผิดของคุณ ลองส่งอีกครั้งครับ",
        "unknown": "เกิดข้อผิดพลาดบางอย่างครับ ลองใหม่อีกครั้ง อย่าเพิ่งยอมแพ้ครับ",
    },
    "developer": {
        "llm_unavailable": "`503` ระบบตอบคำถามขัดข้องชั่วคราวครับ ลอง retry อีกครั้งในอีกสักครู่ครับ",
        "tool_failed": "`tool_failed` ดึงข้อมูลไม่สำเร็จครับ ลอง retry อีกครั้งครับ",
        "unknown": "`unknown_error` เกิดข้อผิดพลาดบางอย่างครับ ลองใหม่อีกครั้งครับ",
    },
}


def error_reply(code: str, intent: str, tool: str | None = None) -> Reply:
    messages = ERROR_MESSAGES.get(generator.current_interaction_mode(), ERROR_MESSAGES["normal"])
    return Reply(messages[code], intent, "error", ErrorData(code=code), tool)


def handle_chat(db, user: User, req: ChatRequest) -> AgentResponse:
    started = time.perf_counter()
    context = services.get_user_context(db, user.id)
    profile: User = _field(context, "user") or user
    conversation_id = services.get_or_create_conversation(db, user.id, req.conversation_id, req.message)
    recent = services.get_recent_messages(db, conversation_id)
    services.add_user_message(db, conversation_id, req.message)

    try:
        all_skills = services.get_all_user_skills(db, user.id)
    except Exception:
        all_skills = []
    latest_skill = _field(context, "skill") or (all_skills[0] if all_skills else None)
    if not all_skills and latest_skill:
        all_skills = [latest_skill]
    skill_context = format_user_skills_context(all_skills)

    route = intent_router.route(req.message, profile.user_type, profile.study_year, recent)
    log.info("route intent=%s source=%s mode=%s", route.intent, route.source, req.interaction_mode)
    with generator.interaction_mode(req.interaction_mode):
        try:
            reply = dispatch(db, route, req.message, profile, latest_skill, all_skills, skill_context, recent)
        except Exception:  # a failing tool must not become an HTTP 500
            log.exception("tool failed for intent=%s", route.intent)
            reply = error_reply("tool_failed", route.intent)

    response = build_response(conversation_id, reply, started, req.interaction_mode)
    try:
        services.add_assistant_message(db, conversation_id, response)
    except Exception:  # the answer is still valid if saving history fails
        log.exception("could not save assistant message")
    return response


def build_response(conversation_id: str, reply: Reply, started: float, interaction_mode: str = "normal") -> AgentResponse:
    meta = {
        "intent": reply.intent,
        "tool": reply.tool,
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "interaction_mode": interaction_mode,
    }
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


def dispatch(
    db,
    route: RouteResult,
    message: str,
    profile: User,
    skill: SkillProfile | None,
    all_skills: list[SkillProfile] | None = None,
    skill_context: str = "",
    recent: list[dict] | None = None,
) -> Reply:
    recent = recent or []
    all_skills = all_skills or ([] if skill is None else [skill])
    if route.intent == "curriculum":
        return curriculum(route, message, profile, skill_context)
    if route.intent == "course_detail":
        return course_detail(route, message, profile, skill_context)
    if route.intent == "department_info":
        return department_info(route.search_query or message, profile, skill_context)
    if route.intent == "skill_analysis":
        return skill_analysis(
            db,
            profile,
            skill,
            all_skills,
            skill_context,
            message,
            recent,
            retake=any(w in message for w in RETAKE_WORDS),
        )
    if route.intent == "clarify":
        return clarify()
    return general(message, profile, recent, skill_context)


# ---------- curriculum ----------


def curriculum(route: RouteResult, message: str, profile: User, skill_context: str | None = None) -> Reply:
    year = route.year or (profile.study_year if profile.user_type in STUDENT_TYPES else None)
    semester = route.semester
    if route.year is None and semester is None and not any(w in message for w in TERM_WORDS):
        return curriculum_overview(profile, skill_context)
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

    try:
        intro_msg = generator.synthesize_curriculum_intro(
            year,
            semester,
            table.courses,
            table.total_credits,
            profile.user_type,
            profile.study_year,
            skill_context,
        )
    except Exception:
        intro_msg = generator.with_fallback_style(
            f"นี่คือรายวิชาของ **ปี {year} เทอม {semester}** รวม {table.total_credits} หน่วยกิตครับ"
        )

    return Reply(
        intro_msg,
        "curriculum",
        "course_table",
        table,
        tool,
        actions=actions,
    )


def curriculum_overview(profile: User | None = None, skill_context: str | None = None) -> Reply:
    overview = services.get_curriculum_overview()
    tool = "curriculum.get_curriculum_overview"
    if not overview.cards:
        return Reply("ยังไม่มีข้อมูลภาพรวมหลักสูตรในระบบครับ", "curriculum", tool=tool)

    try:
        intro = generator.synthesize_curriculum_overview(
            overview.cards,
            profile.user_type if profile else None,
            profile.study_year if profile else None,
            skill_context,
        )
    except Exception:
        intro = generator.with_fallback_style("ภาพรวมหลักสูตรแต่ละชั้นปีครับ")

    return Reply(
        intro,
        "curriculum",
        "cards",
        overview,
        tool,
        actions=[ask(f"ปี {y} เทอม 1", f"ปี {y} เทอม 1 เรียนอะไรบ้าง") for y in range(1, 5)],
    )


# ---------- course detail ----------


def course_detail(route: RouteResult, message: str, profile: User | None = None, skill_context: str | None = None) -> Reply:
    course = services.get_course_detail(route.course_query or message)
    if course is None:
        return department_info(message, profile, skill_context)

    try:
        intro = generator.synthesize_course_detail(
            course,
            profile.user_type if profile else None,
            profile.study_year if profile else None,
            skill_context,
        )
    except Exception:
        intro = generator.with_fallback_style(f"ข้อมูลวิชา **{course.code} {course.name_th}** ครับ")

    return Reply(
        intro,
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


def department_info(query: str, profile: User | None = None, skill_context: str | None = None) -> Reply:
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
        try:
            message = generator.answer_from_rag(
                query,
                chunks,
                user_type=profile.user_type if profile else None,
                study_year=profile.study_year if profile else None,
                skill_context=skill_context,
            )
        except TypeError:
            message = generator.answer_from_rag(query, chunks)
    except LLMError:
        log.warning("rag generator unavailable, showing the top document snippet")
        first = chunks[0]
        message = generator.with_fallback_style(
            f"ตอนนี้ระบบสรุปคำตอบขัดข้อง ขอแสดงข้อความจากเอกสารที่เกี่ยวข้องที่สุดแทนครับ [1]\n\n"
            f"> {first.text[:SNIPPET_CHARS]}"
        )
    return Reply(message, "department_info", tool=tool, sources=sources)


# ---------- skill ----------


def skill_analysis(
    db,
    profile: User,
    skill: SkillProfile | None,
    all_skills: list[SkillProfile] | None = None,
    skill_context: str = "",
    message: str = "",
    recent: list[dict] | None = None,
    retake: bool = False,
) -> Reply:
    all_skills = all_skills or ([] if skill is None else [skill])
    recent = recent or []
    topic, is_general_cpe = extract_skill_topic(message)

    if retake:
        if is_general_cpe:
            form = services.get_assessment()
            tool = "skill.get_assessment"
            msg = "ทำแบบประเมินใหม่ได้เลยครับ ผลล่าสุดจะใช้แทนผลเดิม"
        else:
            form = generate_dynamic_assessment_form(topic)
            tool = "skill.generate_dynamic_assessment"
            msg = f"ทำแบบประเมินทักษะ {topic} ใหม่ได้เลยครับ ผลล่าสุดจะนำมาอัปเดตแทนผลเดิม"
        return Reply(msg, "skill_analysis", "assessment_form", form, tool)

    # Check if existing skill exists for this topic
    existing = None
    if is_general_cpe:
        existing = skill or services.get_latest_skill(db, profile.id)
    else:
        try:
            existing = services.get_skill_by_topic(db, profile.id, topic)
        except Exception:
            existing = None
        if not existing:
            for s in all_skills:
                if s.topic and s.topic.strip().lower() == topic.strip().lower():
                    existing = s
                    break

    # If NO assessment exists for this topic:
    if existing is None:
        if is_general_cpe:
            form = services.get_assessment()
            tool = "skill.get_assessment"
            msg = "ยังไม่มีข้อมูล skill ของคุณ ลองตอบแบบประเมินนี้ก่อนนะครับ"
        else:
            form = generate_dynamic_assessment_form(topic)
            tool = "skill.generate_dynamic_assessment"
            msg = (
                f"ตอนนี้ยังไม่มีข้อมูลทักษะ **{topic}** ของคุณในระบบครับ ผมสร้างแบบประเมินทักษะ {topic} "
                f"({len(form.questions)} ข้อ) ให้คุณแล้ว ลองตอบแบบประเมินนี้เพื่อให้ COPIE วิเคราะห์และบันทึกระดับทักษะได้เลยครับ"
            )

        return Reply(msg, "skill_analysis", "assessment_form", form, tool)

    # If assessment ALREADY exists for this topic:
    wants_chart = any(w in message.lower() for w in ("กราฟ", "radar", "เรดาร์", "แผนภูมิ"))
    if wants_chart or is_general_cpe:
        return skill_radar(existing, profile, "skill.get_latest_skill")

    # Use as context to answer the user's question via LLM!
    try:
        text = generator.answer_skill_inquiry(
            message,
            skill_context,
            profile.user_type,
            profile.study_year,
            recent,
        )
    except LLMError:
        return skill_radar(existing, profile, "skill.get_latest_skill")

    actions = [
        ask("ขอดู Radar Chart", "ขอดูกราฟ Radar"),
        ask(f"ทำแบบประเมิน {topic} ใหม่", f"ขอทำแบบประเมิน {topic} ใหม่"),
    ]
    return Reply(text, "skill_analysis", "text", actions=actions)


def skill_radar(skill: SkillProfile, profile: User, tool: str) -> Reply:
    try:
        if skill.topic and skill.score is not None:
            top_names = skill.custom_top_skills or [SKILL_NAMES_TH.get(k, k) for k in skill.top_skills]
            try:
                summary = generator.explain_dynamic_skill(
                    skill.topic,
                    skill.score,
                    top_names,
                    profile.user_type,
                    profile.study_year,
                    dimensions=skill.dimensions,
                )
            except TypeError:
                summary = generator.explain_dynamic_skill(
                    skill.topic,
                    skill.score,
                    top_names,
                    profile.user_type,
                    profile.study_year,
                )
        else:
            summary = generator.explain_skill(skill.scores, skill.top_skills, profile.user_type, profile.study_year)
    except LLMError:
        summary = generator.skill_summary_template(skill.top_skills)

    data = SkillRadarData(
        scores=skill.scores,
        top_skills=skill.top_skills,
        summary=summary,
        taken_at=skill.taken_at,
        topic=skill.topic,
        title=skill.title,
        dimensions=skill.dimensions,
        custom_top_skills=skill.custom_top_skills,
    )
    return Reply(
        f"นี่คือผลประเมินทักษะ {skill.topic} ของคุณครับ" if skill.topic else "นี่คือผลประเมิน skill ของคุณครับ",
        "skill_analysis",
        "skill_radar",
        data,
        tool,
        actions=[ask(f"ทำแบบประเมิน {skill.topic} ใหม่", f"ขอทำแบบประเมิน {skill.topic} ใหม่")] if skill.topic else [ask("ทำแบบประเมินใหม่", "ขอทำแบบประเมิน skill ใหม่")],
    )


def handle_assessment_submit(db, user: User, req: AssessmentSubmit) -> AgentResponse:
    """Score answers (standard or dynamic), save to DB profile, return a radar / summary."""
    with generator.interaction_mode(req.interaction_mode):
        return _assessment_submit(db, user, req)


def _assessment_submit(db, user: User, req: AssessmentSubmit) -> AgentResponse:
    started = time.perf_counter()
    conversation_id = services.get_or_create_conversation(db, user.id, req.conversation_id, SUBMIT_TEXT)
    services.add_user_message(db, conversation_id, SUBMIT_TEXT)
    profile: User = _field(services.get_user_context(db, user.id), "user") or user

    # Check if standard skill_v1 or dynamic assessment
    if req.assessment_id in DYNAMIC_ASSESSMENTS:
        definition = DYNAMIC_ASSESSMENTS[req.assessment_id]
        check_answers(req, {q["id"] for q in definition["questions"]}, req.assessment_id)
        try:
            pct, scores, top, dimensions_list, custom_top = score_dynamic_assessment(definition, req.answers)
            topic = definition.get("topic", "ทั่วไป")
            title = definition.get("title") or f"แบบประเมินทักษะ: {topic}"
            extra_data = {
                "topic": topic,
                "score": pct,
                "title": title,
                "dimensions": [d.model_dump() for d in dimensions_list],
                "custom_top_skills": custom_top,
            }
            scores._extra_data = extra_data
            skill = services.save_skill_profile(db, user.id, scores, req.answers)
            try:
                try:
                    summary = generator.explain_dynamic_skill(
                        topic,
                        pct,
                        custom_top,
                        profile.user_type,
                        profile.study_year,
                        dimensions=dimensions_list,
                    )
                except TypeError:
                    summary = generator.explain_dynamic_skill(
                        topic,
                        pct,
                        custom_top,
                        profile.user_type,
                        profile.study_year,
                    )
            except LLMError:
                summary = generator.with_fallback_style(
                    f"คุณได้คะแนนการประเมินทักษะ **{topic}** อยู่ที่ **{pct}/100** ครับ ผลการประเมินนี้ถูกบันทึกไว้ในระบบเรียบร้อยแล้ว"
                )

            data = SkillRadarData(
                scores=scores,
                top_skills=top,
                summary=summary,
                taken_at=skill.taken_at,
                topic=topic,
                title=title,
                dimensions=dimensions_list,
                custom_top_skills=custom_top,
            )
            reply = Reply(
                f"ประเมินทักษะ **{topic}** เรียบร้อยแล้วครับ คุณได้คะแนน {pct}/100",
                "skill_analysis",
                "skill_radar",
                data,
                "skill.calculate_skill",
                actions=[ask(f"ทำแบบประเมิน {topic} ใหม่", f"ขอทำแบบประเมิน {topic} ใหม่")],
            )
        except Exception:
            log.exception("dynamic assessment scoring or saving failed")
            reply = error_reply("tool_failed", "skill_analysis")
    else:
        try:
            form = services.get_assessment()
        except Exception:
            log.exception("get_assessment failed")
            return build_response(conversation_id, error_reply("tool_failed", "skill_analysis"), started, req.interaction_mode)

        check_answers(req, {q.id for q in form.questions}, form.assessment_id)
        try:
            scores = services.calculate_skill(req.answers)
            skill = services.save_skill_profile(db, user.id, scores, req.answers)
            reply = skill_radar(skill, profile, "skill.calculate_skill")
        except Exception:
            log.exception("assessment submit failed")
            reply = error_reply("tool_failed", "skill_analysis")

    response = build_response(conversation_id, reply, started, req.interaction_mode)
    try:
        services.add_assistant_message(db, conversation_id, response)
    except Exception:
        log.exception("could not save assistant message")
    return response


def check_answers(req: AssessmentSubmit, question_ids: set[str], assessment_id: str) -> None:
    if req.assessment_id != assessment_id:
        raise HTTPException(status_code=422, detail="แบบประเมินนี้ไม่ใช่เวอร์ชันปัจจุบัน กรุณาเริ่มทำใหม่")
    answered = [a.question_id for a in req.answers]
    if len(answered) != len(set(answered)) or set(answered) != question_ids:
        raise HTTPException(status_code=422, detail="กรุณาตอบแบบประเมินให้ครบทุกข้อ ข้อละหนึ่งคำตอบ")


# ---------- general / clarify ----------


def general(message: str, profile: User, recent: list[dict], skill_context: str | None = None) -> Reply:
    try:
        text = generator.general_answer(message, profile.user_type, profile.study_year, recent, skill_context)
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
