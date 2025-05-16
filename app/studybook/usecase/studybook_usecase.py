# app/studybook/usecase/studybook_usecase.py

from fastapi import UploadFile, HTTPException
from app.studybook.dto.response.my_studybook_response_dto import (
    MyStudybookResponseDTO, StudyBookItemDTO
)
from app.studybook.dto.response.upload_studybook_response_dto import UploadStudybookResponseDTO
from app.studybook.dto.response.delete_studybook_response_dto import DeleteStudybookResponseDTO
from domain.studybook.entity.studybook import StudyBook
from domain.studybook.entity.studybook_question import StudyBookQuestion
from domain.user.entity.user import User
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

# 🧠 dummy들
def dummy_ocr_from_image(file: UploadFile):
    return [
        {
            "description": "이미지 문제 1?",
            "options": ["A", "B", "C", "D"],
            "answer": 1
        },
        {
            "description": "이미지 문제 2?",
            "options": ["가", "나", "다", "라"],
            "answer": 3
        }
    ]
def dummy_ocr_process(file: UploadFile):
    return [
        {
            "description": "1 + 1 = ?",
            "options": ["1", "2", "3", "4"],
            "answer": 2,
        },
        {
            "description": "2 + 2 = ?",
            "options": ["2", "3", "4", "5"],
            "answer": 3,
        }
    ]

async def upload_my_studybook_by_pdf_usecase(file: UploadFile, current_user: User, db: Session) -> UploadStudybookResponseDTO:
    ocr_result = dummy_ocr_process(file)

    new_book = StudyBook(
        name=file.filename.replace(".pdf", ""),
        created_at=datetime.now(),
        question_count=len(ocr_result),
        file_color="#%06x" % (uuid.uuid4().int & 0xFFFFFF),
        user_id=current_user.id,
    )
    db.add(new_book)
    db.flush()

    for item in ocr_result:
        question = StudyBookQuestion(
            study_book_id=new_book.id,
            description=item["description"],
            description_detail=None,
            description_image=None,
            options=item["options"],
            answer=item["answer"],
            explanation=None,
            option_explanations=None,
        )
        db.add(question)

    db.commit()

    return UploadStudybookResponseDTO(
        studybook_id=new_book.id,
        message="문제집이 성공적으로 생성되었습니다."
    )
async def upload_my_studybook_by_img_usecase(file: UploadFile, current_user: User, db: Session) -> UploadStudybookResponseDTO:
    ocr_result = dummy_ocr_from_image(file)

    new_book = StudyBook(
        name=file.filename.replace(".jpg", "").replace(".png", ""),
        created_at=datetime.now(),
        question_count=len(ocr_result),
        file_color="#%06x" % (uuid.uuid4().int & 0xFFFFFF),
        user_id=current_user.id,
    )
    db.add(new_book)
    db.flush()

    for item in ocr_result:
        question = StudyBookQuestion(
            study_book_id=new_book.id,
            description=item["description"],
            description_detail=None,
            description_image=None,
            options=item["options"],
            answer=item["answer"],
            explanation=None,
            option_explanations=None,
        )
        db.add(question)

    db.commit()

    return UploadStudybookResponseDTO(
        studybook_id=new_book.id,
        message="이미지 문제집이 성공적으로 생성되었습니다."
    )

async def get_my_studybooks_usecase(current_user: User, db: Session) -> MyStudybookResponseDTO:
    studybooks = (
        db.query(StudyBook)
        .filter(StudyBook.user_id == current_user.id)
        .order_by(StudyBook.created_at.desc())
        .all()
    )

    response_items = [
        StudyBookItemDTO(
            id=sb.id,
            name=sb.name,
            question_count=sb.question_count,
            file_color=sb.file_color,
            created_at=sb.created_at
        )
        for sb in studybooks
    ]

    return MyStudybookResponseDTO(studybooks=response_items)

async def delete_my_studybook_usecase(studybook_id: int, current_user: User, db: Session) -> DeleteStudybookResponseDTO:
    studybook = db.query(StudyBook).filter(
        StudyBook.id == studybook_id,
        StudyBook.user_id == current_user.id
    ).first()

    if not studybook:
        raise HTTPException(status_code=404, detail="해당 문제집을 찾을 수 없습니다.")

    # ✅ 연결된 문제 먼저 삭제
    db.query(StudyBookQuestion).filter(StudyBookQuestion.study_book_id == studybook.id).delete()

    db.delete(studybook)
    db.commit()

    return DeleteStudybookResponseDTO(message="문제집이 성공적으로 삭제되었습니다.")