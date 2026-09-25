"""route(): decide the intent of a message.

Order: local ML (USE_LOCAL_INTENT and confidence >= 0.80) -> LLM JSON router -> regex rule router.
Never raises: any LLM/ML failure falls through to the rule router.
"""
import logging

from pydantic import ValidationError

from app.core.config import settings
from app.modules.agent.llm_client import LLMError, generate_json
from app.modules.agent.prompts import ROUTER_SYSTEM, router_prompt
from app.modules.agent.rule_router import rule_route
from app.modules.agent.types import RouteResult

log = logging.getLogger(__name__)

ML_MIN_CONFIDENCE = 0.80
_ROUTE_FIELDS = ("intent", "year", "semester", "course_query", "search_query")


def route(
    message: str,
    user_type: str | None = None,
    study_year: int | None = None,
    recent: list[dict] | None = None,
) -> RouteResult:
    ml = _route_ml(message)
    if ml:
        return ml
    try:
        data = generate_json(ROUTER_SYSTEM, router_prompt(message, user_type, study_year, recent or []))
        return RouteResult(**{k: data.get(k) for k in _ROUTE_FIELDS}, source="llm")
    except (LLMError, ValidationError) as exc:
        log.warning("llm router failed, using rule router: %s", exc)
        return rule_route(message)


def _route_ml(message: str) -> RouteResult | None:
    """Intent from the local classifier; slots (year/semester/course) still come from the regex router."""
    if not settings.use_local_intent:
        return None
    try:
        from app.modules.intent_ml import predict_intent
    except ImportError:
        log.warning("USE_LOCAL_INTENT is on but app.modules.intent_ml.predict_intent is not available")
        return None
    try:
        intent, confidence = predict_intent(message)
    except Exception as exc:  # noqa: BLE001 — optional feature; any failure falls back to the LLM
        log.warning("predict_intent failed: %s", exc)
        return None
    if confidence < ML_MIN_CONFIDENCE:
        return None
    slots = rule_route(message)
    try:
        return RouteResult(
            intent=intent,
            year=slots.year,
            semester=slots.semester,
            course_query=slots.course_query,
            search_query=message if intent == "department_info" else None,
            source="ml",
        )
    except ValidationError:
        return None
