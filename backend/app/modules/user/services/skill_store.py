"""Database-backed skill profile storage."""

import json
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.modules.user.models import SkillProfileRow
from app.schemas.contract import AssessmentAnswer, SkillDimension, SkillProfile, SkillScores


def _iso_utc(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _to_profile(row: SkillProfileRow) -> SkillProfile:
    try:
        data = json.loads(row.scores_json)
        scores = SkillScores.model_validate(data)
    except Exception:
        scores = SkillScores(frontend=0, backend=0, network=0, embedded=0, ai_data=0, cybersecurity=0)
        data = {}

    values = scores.model_dump()
    top_skills = sorted(values, key=lambda key: -values[key])[:2]

    dims_data = data.get("dimensions")
    dimensions = None
    if isinstance(dims_data, list):
        try:
            dimensions = [SkillDimension.model_validate(d) for d in dims_data]
        except Exception:
            dimensions = None

    return SkillProfile(
        scores=scores,
        top_skills=top_skills,
        taken_at=_iso_utc(row.created_at),
        topic=data.get("topic"),
        score=data.get("score"),
        title=data.get("title"),
        dimensions=dimensions,
        custom_top_skills=data.get("custom_top_skills"),
    )


def save_skill_profile(
    db: Session,
    user_id: str,
    scores: SkillScores,
    answers: list[AssessmentAnswer],
) -> SkillProfile:
    scores_dict = scores.model_dump()
    extra_data = getattr(scores, "_extra_data", None)
    if extra_data:
        scores_dict.update(extra_data)

    row = SkillProfileRow(
        user_id=user_id,
        scores_json=json.dumps(scores_dict, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
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
    if db is None:
        return None
    statement = (
        select(SkillProfileRow)
        .where(SkillProfileRow.user_id == user_id)
        .order_by(SkillProfileRow.created_at.desc(), SkillProfileRow.id.desc())
        .limit(1)
    )
    row = db.exec(statement).first()
    return _to_profile(row) if row is not None else None


def get_all_user_skills(db: Session, user_id: str) -> list[SkillProfile]:
    if db is None:
        return []
    statement = (
        select(SkillProfileRow)
        .where(SkillProfileRow.user_id == user_id)
        .order_by(SkillProfileRow.created_at.desc(), SkillProfileRow.id.desc())
    )
    rows = db.exec(statement).all()
    return [_to_profile(r) for r in rows]


def get_skill_by_topic(db: Session, user_id: str, topic: str) -> SkillProfile | None:
    if db is None:
        return None
    topic_clean = topic.strip().lower()
    for prof in get_all_user_skills(db, user_id):
        if prof.topic and prof.topic.strip().lower() == topic_clean:
            return prof
    return None
