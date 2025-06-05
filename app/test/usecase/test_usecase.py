# from sqlalchemy.orm import Session
# from app.test.dto.request.test_request import TestRequest
# from app.test.dto.response.test_response import TestResponse
# from domain.test.service.test_service import TestService
#
# def create_test_usecae(db: Session, request: TestRequest) -> TestResponse:
#     service = TestService(db)
#     new_test = service.create_test(request.name)
#     return TestResponse.from_orm(new_test)
#
# def get_tests_usecase(db: Session) -> list[TestResponse]:
#     service = TestService(db)
#     tests = service.get_tests()
#     return [TestResponse.model_validate(t) for t in tests]