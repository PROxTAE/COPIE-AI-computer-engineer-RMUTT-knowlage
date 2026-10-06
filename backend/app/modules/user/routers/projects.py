"""Authenticated endpoints for projects (folders of conversations)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from app.modules.user.auth.deps import get_current_user
from app.modules.user.database import get_session
from app.modules.user.services.project_service import (
    create_project,
    delete_project,
    list_projects,
    rename_project,
)
from app.schemas.contract import Project, ProjectInput, User

router = APIRouter(prefix="/api/projects", tags=["history"])
CurrentUser = Annotated[User, Depends(get_current_user)]
Database = Annotated[Session, Depends(get_session)]


@router.get("", response_model=list[Project])
def read_projects(user: CurrentUser, db: Database) -> list[Project]:
    return list_projects(db, user.id)


@router.post("", response_model=Project, status_code=201)
def add_project(data: ProjectInput, user: CurrentUser, db: Database) -> Project:
    return create_project(db, user.id, data)


@router.patch("/{project_id}", response_model=Project)
def edit_project(project_id: str, data: ProjectInput, user: CurrentUser, db: Database) -> Project:
    return rename_project(db, user.id, project_id, data)


@router.delete("/{project_id}", status_code=204)
def remove_project(project_id: str, user: CurrentUser, db: Database) -> Response:
    delete_project(db, user.id, project_id)
    return Response(status_code=204)
