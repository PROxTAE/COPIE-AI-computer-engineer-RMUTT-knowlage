"""User lookup and the context interface consumed by the agent."""

from typing import TypedDict

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.modules.user.auth.google import GoogleIdentity
from app.modules.user.models import User as UserRow
from app.modules.user.services.skill_store import get_latest_skill
from app.schemas.contract import ProfileUpdate, SkillProfile, User


class UserContext(TypedDict):
    user: User
    skill: SkillProfile | None


def to_contract_user(user: UserRow) -> User:
    return User.model_validate(user, from_attributes=True)


class GoogleIdentityConflictError(RuntimeError):
    """Raised when a Google identity cannot safely claim an existing email."""


def upsert_google_user(db: Session, identity: GoogleIdentity) -> tuple[UserRow, bool]:
    user = db.exec(select(UserRow).where(UserRow.google_sub == identity["sub"])).first()
    if user is not None:
        return user, False

    email = identity["email"].strip().lower()
    if db.exec(select(UserRow).where(UserRow.email == email)).first() is not None:
        raise GoogleIdentityConflictError("email already belongs to another identity")

    user = UserRow(
        google_sub=identity["sub"],
        email=email,
        name=identity["name"],
        picture_url=identity["picture"],
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        concurrent_user = db.exec(
            select(UserRow).where(UserRow.google_sub == identity["sub"])
        ).first()
        if concurrent_user is not None:
            return concurrent_user, False
        if db.exec(select(UserRow).where(UserRow.email == email)).first() is not None:
            raise GoogleIdentityConflictError("email already belongs to another identity")
        raise

    db.refresh(user)
    return user, True


def update_profile(db: Session, user_id: str, profile: ProfileUpdate) -> User:
    user = db.get(UserRow, user_id)
    if user is None:
        raise LookupError(f"user not found: {user_id}")

    user.display_name = profile.display_name
    user.age_range = profile.age_range
    user.user_type = profile.user_type
    user.study_year = profile.study_year
    user.onboarded = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_contract_user(user)


def get_user_context(db: Session, user_id: str) -> UserContext:
    user = db.get(UserRow, user_id)
    if user is None:
        raise LookupError(f"user not found: {user_id}")
    return {"user": to_contract_user(user), "skill": get_latest_skill(db, user_id)}
