"""Database-backed skill profile storage."""

import json
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.modules.user.models import SkillProfileRow
from app.schemas.contract import AssessmentAnswer, SkillProfile, SkillScores


def _iso_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _to_profile(row: SkillProfileRow) -> SkillProfile:
    scores = SkillScores.model_validate_json(row.scores_json)
    values = scores.model_dump()
    top_skills = sorted(values, key=lambda key: -values[key])[:2]
    return SkillProfile(scores=scores, top_skills=top_skills, taken_at=_iso_utc(row.created_at))


def save_skill_profile(
    db: Session,
    user_id: str,
    scores: SkillScores,
    answers: list[AssessmentAnswer],
) -> SkillProfile:
    row = SkillProfileRow(
        user_id=user_id,
        scores_json=json.dumps(scores.model_dump(), ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        answers_json=json.dumps(
            [answer.model_dump() for answer in answers],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_profile(row)


def get_latest_skill(db: Session, user_id: str) -> SkillProfile | None:
    statement = (
        select(SkillProfileRow)
        .where(SkillProfileRow.user_id == user_id)
        .order_by(SkillProfileRow.created_at.desc(), SkillProfileRow.id.desc())
        .limit(1)
    )
    row = db.exec(statement).first()
    return _to_profile(row) if row is not None else None
