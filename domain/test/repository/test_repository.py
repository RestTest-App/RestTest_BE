# DB 접근을 위한 로직을 작성 (CRUD) DB 접근에 중점
from sqlalchemy.orm import Session
from domain.test.entity.exam import Exam


class TestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_test(self, name: str) -> Exam:
        test = Exam(name=name)
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)
        return test

    def get_test_all(self) -> list[Exam]:
        return self.db.query(Exam).all()
