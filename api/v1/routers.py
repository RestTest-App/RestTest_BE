from fastapi import APIRouter
from api.v1.endpoints import test_endpoints

router = APIRouter()
router.include_router(test_endpoints.router, tags=["test"])