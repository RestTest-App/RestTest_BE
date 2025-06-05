# # 비즈니스 로직이 복잡할 경우 활용 (DB 접근은 repository를 활용)
# from sqlalchemy.orm import Session
# from domain.test.repository.test_repository import TestRepository
#
# class TestService:
#     def __init__(self, db: Session):
#         self.repository = TestRepository(db)
#
#     def create_test(self, name: str) -> dict:
#         test = self.repository.create_test(name)
#         return test
#
#     def get_tests(self):
#         return self.repository.get_test_all()