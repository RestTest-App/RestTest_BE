# domain/studybook/studybook_question/repository/studybook_question_repository.py

from sqlalchemy.orm import Session
from domain.studybook.entity.studybook_question import StudyBookQuestion

def create_studybook_question(db: Session, question: StudyBookQuestion):
    """
    문제 객체를 DB에 저장합니다.
    """
    db.add(question)
    db.flush()  # 바로 ID 사용 가능하게 함
    return question
