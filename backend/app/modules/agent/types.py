"""Internal types of the agent module (not part of the public contract)."""
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.contract import Intent


class RouteResult(BaseModel):
    intent: Intent
    year: int | None = Field(default=None, ge=1, le=4)
    semester: int | None = Field(default=None, ge=1, le=3)
    course_query: str | None = None
    search_query: str | None = None  # question rewritten for RAG
    source: Literal["ml", "llm", "rule"]
