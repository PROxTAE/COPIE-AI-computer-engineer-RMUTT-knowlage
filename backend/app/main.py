"""FastAPI entry point: one backend app that mounts every module's router. Owner: P3."""
from fastapi import FastAPI

app = FastAPI(title="COPIE API", version="0.1.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Module routers are added here by their owners (via PR, P3 approves), e.g.
# from app.modules.user import router as user_router
# app.include_router(user_router)
