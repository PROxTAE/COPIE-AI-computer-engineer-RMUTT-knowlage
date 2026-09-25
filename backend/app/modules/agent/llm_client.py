"""The only place that talks to the LLM provider (Gemini). Swap providers here.

Every call has a timeout (LLM_TIMEOUT_S) and is retried once on server/network errors
(not on 4xx such as a bad key or an exhausted quota, where retrying cannot help).
Any failure is raised as LLMError so callers can fall back without crashing.
"""
import json
import logging
import time
from functools import lru_cache

from google import genai
from google.genai import errors, types

from app.core.config import settings

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 2  # first try + 1 retry


class LLMError(RuntimeError):
    """The LLM is not configured, unreachable, timed out or returned unusable output."""


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise LLMError("GEMINI_API_KEY is not set")
    if not settings.llm_model:
        raise LLMError("LLM_MODEL is not set")
    timeout_ms = int(settings.llm_timeout_s * 1000)
    return genai.Client(api_key=settings.gemini_api_key, http_options=types.HttpOptions(timeout=timeout_ms))


def _generate(system: str, prompt: str, temperature: float, json_mode: bool) -> str:
    client = _client()
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        response_mime_type="application/json" if json_mode else None,
    )
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        started = time.perf_counter()
        try:
            response = client.models.generate_content(model=settings.llm_model, contents=prompt, config=config)
            text = (response.text or "").strip()
            if not text:
                raise LLMError("empty response")
            log.info("llm ok model=%s json=%s latency_ms=%d", settings.llm_model, json_mode, _ms(started))
            return text
        except errors.ClientError as exc:
            last_error = exc
            log.warning("llm request rejected after %dms: %s", _ms(started), _short(exc))
            break
        except Exception as exc:  # noqa: BLE001 — server/network errors vary; all are retried once
            last_error = exc
            log.warning("llm attempt %d failed after %dms: %s", attempt, _ms(started), _short(exc))
    raise LLMError(f"LLM call failed: {_short(last_error)}") from last_error


def _short(exc: Exception | None) -> str:
    return str(exc)[:200]


def _ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def generate_text(system: str, prompt: str, *, temperature: float = 0.3) -> str:
    return _generate(system, prompt, temperature, json_mode=False)


def generate_json(system: str, prompt: str) -> dict:
    raw = _generate(system, prompt, 0.0, json_mode=True)
    try:
        data = json.loads(_strip_code_fence(raw))
    except json.JSONDecodeError as exc:
        raise LLMError(f"LLM returned invalid JSON: {raw[:200]}") from exc
    if not isinstance(data, dict):
        raise LLMError("LLM JSON is not an object")
    return data


def _strip_code_fence(text: str) -> str:
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0]
    return text.strip()
