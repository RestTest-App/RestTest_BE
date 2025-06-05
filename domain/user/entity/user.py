from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Integer
from sqlalchemy.dialects.mysql import SET
from database.base import Base
from sqlalchemy.dialects.mysql import JSON


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, comment="사용자 고유 식별값")
    auth_provider = Column(String(50), nullable=False, comment="소셜로그인 API 제공자")
    email = Column(String(255), nullable=False, comment="사용자 이메일")
    nickname = Column(String(50), nullable=False, comment="사용자 닉네임")
    gender = Column(String(10), nullable=False, comment="사용자 성별")
    birthday = Column(DateTime, nullable=False, comment="사용자 생년월일")
    job = Column(String(100), nullable=False, comment="사용자 직업")
    agree_to_terms = Column(Boolean, nullable=False, comment="선택약관 동의 여부")
    created_at = Column(DateTime, nullable=False, comment="계정 생성 일시")
    studybook_limit = Column(Integer, nullable=False,
                             default=5, comment="나의 문제집 생성 제한 횟수")
    rest_goal = Column(Integer, nullable=True, comment="쉬엄모드 목표")
    test_goal = Column(Integer, nullable=True, comment="시험모드 목표")
    profile_image = Column(String(255), nullable=True,
                           comment="프로필 이미지 S3 URI")
    total_study_days = Column(Integer, nullable=False,
                              default=0, comment="총 학습일")
    monthly_study_date = Column(
        JSON, nullable=False, default=list, comment="학습한 날짜")
    is_study_today = Column(Boolean, nullable=False,
                            default=False, comment="오늘 학습 여부")
