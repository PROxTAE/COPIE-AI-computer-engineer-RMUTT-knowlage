"""Phase 1 skill-store compatibility stubs; persistence follows in its own slice."""

from datetime import datetime, timezone

from sqlmodel import Session

from app.schemas.contract import AssessmentAnswer, SkillProfile, SkillScores


def save_skill_profile(
    db: Session,
    user_id: str,
    scores: SkillScores,
    answers: list[AssessmentAnswer],
) -> SkillProfile:
    del db, user_id, answers
    values = scores.model_dump()
    top_skills = sorted(values, key=values.get, reverse=True)[:2]
    taken_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return SkillProfile(scores=scores, top_skills=top_skills, taken_at=taken_at)


def get_latest_skill(db: Session, user_id: str) -> SkillProfile | None:
    del db, user_id
    return None
