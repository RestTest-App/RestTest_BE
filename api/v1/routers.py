from fastapi import APIRouter

from api.v1.review import review_router
from api.v1.auth import auth_router
from api.v1.user import user_router, certificate_router
from api.v1.studybook import studybook_router
from api.v1.studybook import studybook_question_router
from api.v1.test import test_router
router = APIRouter(prefix="/api/v1")

router.include_router(review_router.router, tags=["review"], prefix="/review")
router.include_router(auth_router.router, tags=["auth"], prefix="/auth")
router.include_router(user_router.router, tags=["user"], prefix="/user")
router.include_router(studybook_router.router, tags=["studybook"], prefix="/studybook")
router.include_router(studybook_question_router.router, tags=["studybook_question"], prefix="/studybook-question")
router.include_router(test_router.router, tags=["test"], prefix="/test")
router.include_router(certificate_router.router, tags=["certificate"], prefix="/user")