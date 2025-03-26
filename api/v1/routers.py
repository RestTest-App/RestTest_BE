from fastapi import APIRouter
from api.v1.test import test_router

router = APIRouter()
router.include_router(test_router.router, tags=["test"])