"""User lookup and the context interface consumed by the agent."""

from typing import TypedDict

from sqlmodel import Session

from app.modules.user.models import User as UserRow
from app.modules.user.services.skill_store import get_latest_skill
from app.schemas.contract import SkillProfile, User


class UserContext(TypedDict):
    user: User
    skill: SkillProfile | None


def to_contract_user(user: UserRow) -> User:
    return User.model_validate(user, from_attributes=True)


def get_user_context(db: Session, user_id: str) -> UserContext:
    user = db.get(UserRow, user_id)
    if user is None:
        raise LookupError(f"user not found: {user_id}")
    return {"user": to_contract_user(user), "skill": get_latest_skill(db, user_id)}
