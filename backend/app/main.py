"""FastAPI entry point: one backend app that mounts every module's router. Owner: P3."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.modules.agent import router as agent_router
from app.modules.rag import ensure_index
from app.modules.user import create_all
from app.modules.user import router as user_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    # Build the knowledge index once at startup so the first question is not slow.
    # A broken knowledge file must not stop the API: RAG answers "not found" until it is fixed.
    try:
        log.info("knowledge index ready: %d chunks", ensure_index())
    except Exception:
        log.exception("could not build the knowledge index")
    yield


app = FastAPI(title="COPIE API", version="0.1.0", lifespan=lifespan)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(user_router)
app.include_router(agent_router)
