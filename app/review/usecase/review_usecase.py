from sqlalchemy.orm import Session

from app.review.dto.request.review_test_mode_request import ReviewTestModeRequest
from app.review.dto.response.get_review_note_list_response import GetReviewNoteListResponse, ExamListInfo
from app.review.dto.response.get_review_rest_mode_response import GetReviewRestModeResponse, QuestionInfo
from app.review.dto.response.get_review_test_mode_response import GetReviewTestModeResponse, ExamInfo
from domain.review.entity.review_note_by_rest import ReviewNoteByRest
from domain.review.entity.review_note_by_rest_question import ReviewNoteByRestQuestion
from domain.review.entity.review_note_by_test import ReviewNoteByTest

# def add_review_note_test_mode_usecase(
#         db: Session,
#         request: ReviewTestModeRequest,
#         exam_id : int,
# ) -> GetReviewTestModeResponse:
#     repository = ReviewNoteRepository(db)
#
#     review_note = repository.create_review_note_test_mode(
#         user_id = 1,  # 실제 로그인한 사용자 ID로 대체
#         study_tracker_id = request.result_id # TODO() : 이거 뭔지 모르겟네..
#     )
#
#     return GetReviewTestModeResponse(
#         review_note_id=review_note.id,
#         created_at=review_note.created_at,
#         exam=ExamInfo(
#             exam_id=exam_id,
#             name="정보처리기사",
#             year=2024,
#             month=3,
#             trial=1,
#             time=90,
#             pass_rate=63.5,
#             score=450,
#             is_passed=True,
#             solved_at=review_note.created_at
#         ),
#         questions=[]
#     )

def get_review_note_list_usecase(
        db: Session,
        user_id: int) -> GetReviewNoteListResponse:
    notes = db.query(ReviewNoteByTest).filter(ReviewNoteByTest.user_id == user_id).all()

    exams = []
    for note in notes:
        exams.append(ExamListInfo(
            review_note_id=note.id,
            name="2024년 1회 정보처리기사",  # 실제 exam 테이블에서 조인 필요
            exam_id=str(note.study_tracker_id),
            certificate="정보처리기사",
            read_count=0,
            pass_rate=63.5,
            is_passed=True
        ))

    return GetReviewNoteListResponse(
        category=["정보처리기사", "한국사능력검정시험", "컴퓨터활용능력", "쉬엄모드"],  # 향후 복수 카테고리로 확장 가능
        selected_category="정보처리기사",
        exams=exams
    )

def get_review_note_rest_mode_usecase(db: Session, review_note_id: int) -> GetReviewRestModeResponse:
    note = db.query(ReviewNoteByRest).filter(ReviewNoteByRest.id == review_note_id).first()
    result = []

    questions = db.query(ReviewNoteByRestQuestion).filter(
        ReviewNoteByRestQuestion.review_note_by_rest_id == note.id).all()

    question_infos = []
    for q in questions:
        question_infos.append(QuestionInfo(
            question_id=q.question_id,
            answer_rate=0.0,
            section="네트워크",  # 예시
            description="샘플 문제 설명",
            description_detail="상세 설명",
            description_image="",
            options=["1", "2", "3", "4"],
            option_explanations=["설명1", "설명2", "설명3", "설명4"],
            answer=2,
            selected_answer=q.selected_answer,
            is_correct=q.is_correct
        ))

    return GetReviewRestModeResponse(
        review_note_id=note.id,
        name=note.name,
        created_at=note.created_at,
        updated_at=note.updated_at,
        certificate_name="정보처리기사",  # 실제 certificate 조인 필요
        question_count=len(question_infos),
        questions=question_infos
    )


def get_review_note_test_mode_usecase(db: Session, review_note_id: int) -> GetReviewTestModeResponse:
    note = db.query(ReviewNoteByTest).filter(ReviewNoteByTest.id == review_note_id).first()

    return GetReviewTestModeResponse(
            review_note_id=note.id,
            created_at=note.created_at,
            exam=ExamInfo(
                exam_id=1,
                name="정보처리기사",
                year=2024,
                month=3,
                trial=1,
                time=90,
                pass_rate=63.5,
                score=450,
                is_passed=True,
                solved_at=note.created_at
            ),
            questions=[]  # 실제 문제와 조인 필요
        )

def delete_review_note_usecase(
    db: Session,
    review_note_id: int,
) -> dict:
    # 시험모드에서 먼저 시도
    note = db.query(ReviewNoteByTest).filter(ReviewNoteByTest.id == review_note_id).first()

    if not note:
        # 쉬엄모드에서 다시 시도
        note = db.query(ReviewNoteByRest).filter(ReviewNoteByRest.id == review_note_id).first()

    if note:
        db.delete(note)
        db.commit()
        return {"message": "복습노트가 삭제되었습니다."}
    else:
        return {"message": "해당 복습노트를 찾을 수 없습니다."}