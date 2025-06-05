from sqlalchemy import Column, Integer, String
from database.base import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, nullable=False)
    question_id = Column(String, nullable=False)
    ai_explanation = Column(String, nullable=False)
    feedback = Column(String, nullable=False)
