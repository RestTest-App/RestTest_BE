from fastapi import APIRouter

from api.v1.review import review_router
from api.v1.test import test_router

router = APIRouter()
# router.include_router(test_router.router, tags=["test"])
router.include_router(review_router.router, tags=["review"], prefix="/review")