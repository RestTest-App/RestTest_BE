from fastapi import APIRouter

from api.v1.review import review_router
from api.v1.test import test_router
from api.v1.auth import auth_router

from api.v1.test import test_router
from api.v1.studybook import studybook_router
from api.v1.studybook.studybook_question_router import router as studybook_question_router

router = APIRouter()

router.include_router(review_router.router, tags=["review"], prefix="/review")
router.include_router(auth_router.router, tags=["auth"])
router.include_router(studybook_router.router, tags=["studybook"], prefix="/studybook")
router.include_router(studybook_question_router, tags=["studybook_question"], prefix="/studybook-question")
