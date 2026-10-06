"""Projects: user-owned folders that group conversations."""

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select, update

from app.modules.user.models import Conversation, Project, utc_now
from app.modules.user.services.history_service import iso_utc
from app.schemas.contract import Project as ProjectOut
from app.schemas.contract import ProjectInput


def _out(row: Project, count: int) -> ProjectOut:
    return ProjectOut(
        id=row.id,
        name=row.name,
        created_at=iso_utc(row.created_at),
        updated_at=iso_utc(row.updated_at),
        conversation_count=count,
    )


def _owned_project(db: Session, user_id: str, project_id: str) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.user_id != user_id:
        raise HTTPException(status_code=404, detail="ไม่พบโปรเจกต์นี้")
    return project


def _name(data: ProjectInput) -> str:
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="ชื่อโปรเจกต์ต้องไม่ว่าง")
    return name


def _count(db: Session, project_id: str) -> int:
    statement = select(func.count()).select_from(Conversation).where(Conversation.project_id == project_id)
    return db.exec(statement).one()


def list_projects(db: Session, user_id: str) -> list[ProjectOut]:
    counts = dict(
        db.exec(
            select(Conversation.project_id, func.count())
            .where(Conversation.user_id == user_id, Conversation.project_id.is_not(None))
            .group_by(Conversation.project_id)
        ).all()
    )
    rows = db.exec(select(Project).where(Project.user_id == user_id).order_by(Project.name, Project.id)).all()
    return [_out(row, counts.get(row.id, 0)) for row in rows]


def create_project(db: Session, user_id: str, data: ProjectInput) -> ProjectOut:
    project = Project(user_id=user_id, name=_name(data))
    db.add(project)
    db.commit()
    db.refresh(project)
    return _out(project, 0)


def rename_project(db: Session, user_id: str, project_id: str, data: ProjectInput) -> ProjectOut:
    project = _owned_project(db, user_id, project_id)
    project.name = _name(data)
    project.updated_at = utc_now()
    db.add(project)
    db.commit()
    db.refresh(project)
    return _out(project, _count(db, project.id))


def delete_project(db: Session, user_id: str, project_id: str) -> None:
    """Delete the folder only; its conversations stay and become ungrouped."""
    project = _owned_project(db, user_id, project_id)
    db.exec(update(Conversation).where(Conversation.project_id == project.id).values(project_id=None))
    db.delete(project)
    db.commit()
