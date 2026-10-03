"""Service functions used by the user module and the agent."""

from app.modules.user.services.history_service import (
    add_assistant_message,
    add_user_message,
    get_or_create_conversation,
    get_recent_messages,
)
from app.modules.user.services.skill_store import (
    get_all_user_skills,
    get_latest_skill,
    get_skill_by_topic,
    save_skill_profile,
)
from app.modules.user.services.user_service import get_user_context

__all__ = [
    "add_assistant_message",
    "add_user_message",
    "get_all_user_skills",
    "get_latest_skill",
    "get_or_create_conversation",
    "get_recent_messages",
    "get_skill_by_topic",
    "get_user_context",
    "save_skill_profile",
]
