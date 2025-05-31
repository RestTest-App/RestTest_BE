from fastapi import APIRouter
from api.v1.auth import auth_router

router = APIRouter()

router.include_router(auth_router.router, tags=["auth"])