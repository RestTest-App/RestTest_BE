# domain/studybook/studybook_question/service/studybook_question_service.py

from sqlalchemy.orm import Session
from domain.studybook.entity.studybook_question import StudyBookQuestion
from domain.studybook.studybook_question.repository.studybook_question_repository import create_studybook_question

def register_question(db: Session, question_data: dict):
    """
    문제 등록 서비스 로직
    """
    question = StudyBookQuestion(**question_data)
    return create_studybook_question(db, question)
