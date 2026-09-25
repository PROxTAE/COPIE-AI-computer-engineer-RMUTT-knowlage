"""HTTP endpoints of the agent module: POST /api/chat, POST /api/assessment/submit."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.agent import orchestrator, services
from app.modules.agent.mock import mock_assessment_submit, mock_chat
from app.schemas.contract import AgentResponse, AssessmentSubmit, ChatRequest, User

router = APIRouter(prefix="/api", tags=["agent"])

CurrentUser = Annotated[User, Depends(services.get_current_user)]
Session = Annotated[object, Depends(services.get_session)]


@router.post("/chat", response_model=AgentResponse)
def chat(req: ChatRequest, user: CurrentUser, db: Session) -> AgentResponse:
    if req.message.startswith("mock:"):  # UI fixtures for P1/P6, removed with mock.py before M3
        return mock_chat(req)
    return orchestrator.handle_chat(db, user, req)


@router.post("/assessment/submit", response_model=AgentResponse)
def assessment_submit(req: AssessmentSubmit) -> AgentResponse:
    # TODO(agent/skill-flow): require auth + call orchestrator.handle_assessment_submit
    return mock_assessment_submit(req)
