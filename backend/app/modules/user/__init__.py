"""Public API of the user module (P2).

Other modules import only from ``app.modules.user``, never from internal files.
"""

from app.modules.user.auth.deps import get_current_user
from app.modules.user.auth.jwt import validate_jwt_secret
from app.modules.user.database import create_all, get_session
from app.modules.user.routers import router
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
    "create_all",
    "get_all_user_skills",
    "get_current_user",
    "get_latest_skill",
    "get_or_create_conversation",
    "get_recent_messages",
    "get_session",
    "get_skill_by_topic",
    "get_user_context",
    "router",
    "save_skill_profile",
    "validate_jwt_secret",
]
