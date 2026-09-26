"""Combined router for the user module."""

from fastapi import APIRouter

from app.modules.user.routers.auth import router as auth_router
from app.modules.user.routers.feedback import router as feedback_router
from app.modules.user.routers.history import router as history_router
from app.modules.user.routers.skills import router as skills_router
from app.modules.user.routers.users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(history_router)
router.include_router(skills_router)
router.include_router(feedback_router)

__all__ = ["router"]
