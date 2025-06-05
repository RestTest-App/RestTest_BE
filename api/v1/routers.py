from fastapi import APIRouter

from api.v1.review import review_router
from api.v1.test import test_router
from api.v1.auth import auth_router

router = APIRouter()
router.include_router(review_router.router, tags=["review"], prefix="/review")
router.include_router(auth_router.router, tags=["auth"])
