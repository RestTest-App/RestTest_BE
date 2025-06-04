from fastapi import APIRouter
from api.v1.auth import auth_router
from api.v1.user import user_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router.router, tags=["auth"])
router.include_router(user_router.router, tags=["user"])