"""The only place the agent imports other modules (contract §4 functions).

While a teammate's module does not export its functions yet, the stand-in from stubs.py
is used and listed in STUBBED. Once every module is merged STUBBED must be empty (M3).
"""
import logging

log = logging.getLogger(__name__)
STUBBED: list[str] = []

try:
    from app.modules.rag import search_department_knowledge
except ImportError:
    from app.modules.agent.stubs import search_department_knowledge

    STUBBED.append("rag")

try:
    from app.modules.tools import (
        calculate_skill,
        get_assessment,
        get_course_detail,
        get_courses,
        get_curriculum_overview,
        top_skills,
    )
except ImportError:
    from app.modules.agent.stubs import (
        calculate_skill,
        get_assessment,
        get_course_detail,
        get_courses,
        get_curriculum_overview,
        top_skills,
    )

    STUBBED.append("tools")

try:
    from app.modules.user import (
        add_assistant_message,
        add_user_message,
        get_all_user_skills,
        get_current_user,
        get_latest_skill,
        get_or_create_conversation,
        get_recent_messages,
        get_session,
        get_skill_by_topic,
        get_user_context,
        save_skill_profile,
    )
except ImportError:
    from app.modules.agent.stubs import (
        add_assistant_message,
        add_user_message,
        get_all_user_skills,
        get_current_user,
        get_latest_skill,
        get_or_create_conversation,
        get_recent_messages,
        get_session,
        get_skill_by_topic,
        get_user_context,
        save_skill_profile,
    )

    STUBBED.append("user")

if STUBBED:
    log.warning("agent is using stubs for: %s", ", ".join(STUBBED))

__all__ = [
    "STUBBED",
    "add_assistant_message",
    "add_user_message",
    "calculate_skill",
    "get_all_user_skills",
    "get_assessment",
    "get_course_detail",
    "get_courses",
    "get_current_user",
    "get_curriculum_overview",
    "get_latest_skill",
    "get_or_create_conversation",
    "get_recent_messages",
    "get_session",
    "get_skill_by_topic",
    "get_user_context",
    "save_skill_profile",
    "search_department_knowledge",
    "top_skills",
]
