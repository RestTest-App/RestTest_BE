from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.dependency import get_db
from app.test.dto.request.test_request import TestRequest
from app.test.dto.response.test_response import TestResponse
from app.test.usecase.test_usecase import create_test_usecae, get_tests_usecase

router = APIRouter(prefix="/test", tags=["test"])

@router.post("/", response_model=TestResponse)
def create_test(request: TestRequest, db: Session = Depends(get_db)):
    return create_test_usecae(db, request)

@router.get("/", response_model=list[TestResponse])
def get_tests(db: Session = Depends(get_db)):
    return get_tests_usecase(db)