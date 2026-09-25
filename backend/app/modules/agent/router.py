"""HTTP endpoints of the agent module: POST /api/chat, POST /api/assessment/submit."""
from fastapi import APIRouter

from app.modules.agent.mock import mock_assessment_submit, mock_chat
from app.schemas.contract import AgentResponse, AssessmentSubmit, ChatRequest

router = APIRouter(prefix="/api", tags=["agent"])


@router.post("/chat", response_model=AgentResponse)
def chat(req: ChatRequest) -> AgentResponse:
    # TODO(agent/orchestrator): require auth + call orchestrator.handle_chat
    return mock_chat(req)


@router.post("/assessment/submit", response_model=AgentResponse)
def assessment_submit(req: AssessmentSubmit) -> AgentResponse:
    # TODO(agent/skill-flow): require auth + call orchestrator.handle_assessment_submit
    return mock_assessment_submit(req)
