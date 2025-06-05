from fastapi import UploadFile
from pathlib import Path
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

from exception.client_exception import (
    NotFoundException, BadRequestException, ConflictException,
    RequestEntityTooLargeException, UnsupportedMediaTypeException,
    UnprocessableEntityException
)
from exception.server_exception import InternalServerErrorException
from exception.success import created, ok

# 401 Unauthorized 처리는 추후 인증 미들웨어와 통합 예정
# from exception.client_exception import UnauthorizedException

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

"""
[upload_my_studybook_by_pdf_usecase]
- 400: UnsupportedMediaTypeException("잘못된 pdf 형식입니다.")
- 409: ConflictException("이미 있는 파일명입니다.")
- 413: RequestEntityTooLargeException("최대 업로드 용량을 초과했습니다.")
- 422: UnprocessableEntityException("PDF를 분석할 수 없습니다.")
- 500: InternalServerErrorException("PDF 문제집 생성 중 서버 오류가 발생했습니다.")
"""
async def upload_my_studybook_by_pdf_usecase(file: UploadFile, current_user: User, db: Session):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext != ".pdf":
            raise UnsupportedMediaTypeException("잘못된 pdf 형식입니다.")

        if db.query(StudyBook).filter(StudyBook.name == file.filename.replace(".pdf", ""), StudyBook.user_id == current_user.id).first():
            raise ConflictException("이미 있는 파일명입니다.")

        if hasattr(file, 'size') and file.size and file.size > 100 * 1024 * 1024:
            raise RequestEntityTooLargeException("최대 업로드 용량을 초과했습니다.")

        ocr_result = dummy_ocr_process(file)

        if not ocr_result:
            raise UnprocessableEntityException("PDF를 분석할 수 없습니다.")

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

        return created(
            data=UploadStudybookResponseDTO(
                studybook_id=new_book.id,
                message="문제집이 성공적으로 생성되었습니다."
            ).dict(),
            message="문제집 생성 성공"
        )
    except (UnsupportedMediaTypeException, ConflictException, RequestEntityTooLargeException, UnprocessableEntityException) as e:
        raise e
    except Exception:
        raise InternalServerErrorException("PDF 문제집 생성 중 서버 오류가 발생했습니다.")

"""
[upload_my_studybook_by_img_usecase]
- 400: UnsupportedMediaTypeException("잘못된 이미지 파일 형식입니다.")
- 409: ConflictException("이미 있는 파일명입니다.")
- 422: UnprocessableEntityException("이미지를 분석할 수 없습니다.")
- 500: InternalServerErrorException("이미지 문제집 생성 중 서버 오류가 발생했습니다.")
"""
async def upload_my_studybook_by_img_usecase(file: UploadFile, current_user: User, db: Session):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [".jpg", ".jpeg", ".png"]:
            raise UnsupportedMediaTypeException("잘못된 이미지 파일 형식입니다.")

        if db.query(StudyBook).filter(StudyBook.name == file.filename.replace(file_ext, ""), StudyBook.user_id == current_user.id).first():
            raise ConflictException("이미 있는 파일명입니다.")

        ocr_result = dummy_ocr_from_image(file)

        if not ocr_result:
            raise UnprocessableEntityException("이미지를 분석할 수 없습니다.")

        new_book = StudyBook(
            name=file.filename.replace(file_ext, ""),
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

        return created(
            data=UploadStudybookResponseDTO(
                studybook_id=new_book.id,
                message="이미지 문제집이 성공적으로 생성되었습니다."
            ).dict(),
            message="이미지 문제집 생성 성공"
        )
    except (UnsupportedMediaTypeException, ConflictException, UnprocessableEntityException) as e:
        raise e
    except Exception:
        raise InternalServerErrorException("이미지 문제집 생성 중 서버 오류가 발생했습니다.")

"""
[get_my_studybooks_usecase]
- 400: BadRequestException("잘못된 Query Parameter이 전달되었습니다.") (선택적 추가)
- 401: UnauthorizedException("만료된 access token 입니다.") (추후 처리 예정)
- 403: ForbiddenException("접근 권한이 없습니다.") (추후 처리 예정)
- 500: InternalServerErrorException("문제집 불러오기 중 서버 오류가 발생했습니다.")
"""
async def get_my_studybooks_usecase(current_user: User, db: Session):
    try:
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

        return ok(
            data=MyStudybookResponseDTO(studybooks=response_items).dict(),
            message="나의 문제집 불러오기 성공"
        )
    except Exception:
        raise InternalServerErrorException("문제집 불러오기 중 서버 오류가 발생했습니다.")

"""
[delete_my_studybook_usecase]
- 400: BadRequestException("잘못된 나의 문제집 정보입니다.") (필요 시 추가)
- 401: UnauthorizedException("access token이 만료되었습니다.") (추후 처리 예정)
- 404: NotFoundException("해당 문제집을 찾을 수 없습니다.")
- 409: ConflictException("이미 삭제된 문제집입니다.") (필요 시 처리)
- 500: InternalServerErrorException("문제집 삭제 중 서버 오류가 발생했습니다.")
"""
async def delete_my_studybook_usecase(studybook_id: int, current_user: User, db: Session):
    try:
        studybook = db.query(StudyBook).filter(
            StudyBook.id == studybook_id,
            StudyBook.user_id == current_user.id
        ).first()

        if not studybook:
            raise NotFoundException(detail="해당 문제집을 찾을 수 없습니다.")

        db.query(StudyBookQuestion).filter(StudyBookQuestion.study_book_id == studybook.id).delete()
        db.delete(studybook)
        db.commit()

        return ok(
            data=DeleteStudybookResponseDTO(message="문제집이 성공적으로 삭제되었습니다.").dict(),
            message="문제집 삭제 성공"
        )
    except NotFoundException as e:
        raise e
    except Exception:
        raise InternalServerErrorException("문제집 삭제 중 서버 오류가 발생했습니다.")
