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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
import uuid
import traceback
import logging

from exception.client_exception import (
    NotFoundException, BadRequestException, ConflictException,
    RequestEntityTooLargeException, UnsupportedMediaTypeException,
    UnprocessableEntityException
)
from exception.server_exception import InternalServerErrorException
from exception.success import created, ok

logger = logging.getLogger(__name__)

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

async def upload_my_studybook_by_pdf_usecase(file: UploadFile, current_user: User, db: AsyncSession):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext != ".pdf":
            raise UnsupportedMediaTypeException("잘못된 pdf 형식입니다.")

        result = await db.execute(
            select(StudyBook).where(
                StudyBook.name == file.filename.replace(".pdf", ""),
                StudyBook.user_id == current_user.id
            )
        )
        existing_studybook = result.scalars().first()

        if existing_studybook:
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
        await db.flush()

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

        await db.commit()

        logger.info(f"[SUCCESS] upload_my_studybook_by_pdf_usecase - user_id: {current_user.id}, studybook_id: {new_book.id}")

        return created(
            data=UploadStudybookResponseDTO(
                studybook_id=new_book.id,
                message="문제집이 성공적으로 생성되었습니다."
            ).dict(),
            message="문제집 생성 성공"
        )
    except (UnsupportedMediaTypeException, ConflictException, RequestEntityTooLargeException, UnprocessableEntityException) as e:
        logger.warning(f"[CLIENT ERROR] upload_my_studybook_by_pdf_usecase - {str(e)}")
        raise e
    except Exception:
        logger.error("[SERVER ERROR] upload_my_studybook_by_pdf_usecase")
        logger.error(traceback.format_exc())
        raise InternalServerErrorException("PDF 문제집 생성 중 서버 오류가 발생했습니다.")

async def upload_my_studybook_by_img_usecase(file: UploadFile, current_user: User, db: AsyncSession):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [".jpg", ".jpeg", ".png"]:
            raise UnsupportedMediaTypeException("잘못된 이미지 파일 형식입니다.")
        print(current_user)
        result = await db.execute(
            select(StudyBook).where(
                StudyBook.name == file.filename.replace(file_ext, ""),
                StudyBook.user_id == current_user.id
            )
        )
        existing_studybook = result.scalars().first()

        if existing_studybook:
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
        await db.flush()

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

        await db.commit()

        logger.info(f"[SUCCESS] upload_my_studybook_by_img_usecase - user_id: {current_user.id}, studybook_id: {new_book.id}")

        return created(
            data=UploadStudybookResponseDTO(
                studybook_id=new_book.id,
                message="이미지 문제집이 성공적으로 생성되었습니다."
            ).dict(),
            message="이미지 문제집 생성 성공"
        )
    except (UnsupportedMediaTypeException, ConflictException, UnprocessableEntityException) as e:
        logger.warning(f"[CLIENT ERROR] upload_my_studybook_by_img_usecase - {str(e)}")
        raise e
    except Exception:
        logger.error("[SERVER ERROR] upload_my_studybook_by_img_usecase")
        logger.error(traceback.format_exc())
        raise InternalServerErrorException("이미지 문제집 생성 중 서버 오류가 발생했습니다.")

async def get_my_studybooks_usecase(current_user: User, db: AsyncSession):
    try:
        result = await db.execute(
            select(StudyBook).where(
                StudyBook.user_id == current_user.id
            ).order_by(StudyBook.created_at.desc())
        )
        studybooks = result.scalars().all()

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

        logger.info(f"[SUCCESS] get_my_studybooks_usecase - user_id: {current_user.id}, studybook_count: {len(response_items)}")

        return ok(
            data=MyStudybookResponseDTO(studybooks=response_items).dict(),
            message="나의 문제집 불러오기 성공"
        )
    except Exception:
        logger.error("[SERVER ERROR] get_my_studybooks_usecase")
        logger.error(traceback.format_exc())
        raise InternalServerErrorException("문제집 불러오기 중 서버 오류가 발생했습니다.")

async def delete_my_studybook_usecase(studybook_id: int, current_user: User, db: AsyncSession):
    try:
        result = await db.execute(
            select(StudyBook).where(
                StudyBook.id == studybook_id,
                StudyBook.user_id == current_user.id
            )
        )
        studybook = result.scalars().first()

        if not studybook:
            raise NotFoundException(detail="해당 문제집을 찾을 수 없습니다.")

        await db.execute(
            delete(StudyBookQuestion).where(
                StudyBookQuestion.study_book_id == studybook.id
            )
        )
        await db.delete(studybook)
        await db.commit()

        logger.info(f"[SUCCESS] delete_my_studybook_usecase - user_id: {current_user.id}, studybook_id: {studybook_id}")

        return ok(
            data=DeleteStudybookResponseDTO(message="문제집이 성공적으로 삭제되었습니다.").dict(),
            message="문제집 삭제 성공"
        )
    except NotFoundException as e:
        logger.warning(f"[CLIENT ERROR] delete_my_studybook_usecase - {str(e)}")
        raise e
    except Exception:
        logger.error("[SERVER ERROR] delete_my_studybook_usecase")
        logger.error(traceback.format_exc())
        raise InternalServerErrorException("문제집 삭제 중 서버 오류가 발생했습니다.")
