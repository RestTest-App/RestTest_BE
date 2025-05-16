from fastapi import APIRouter
from api.v1.test import test_router
from api.v1.studybook import studybook_router
router = APIRouter()
# router.include_router(test_router.router, tags=["test"])
router.include_router(studybook_router.router, tags=["studybook"], prefix="/studybook")