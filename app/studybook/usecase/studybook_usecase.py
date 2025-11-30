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
import json
from app.utils.gpt_ocr_processor import gpt_ocr_process

from exception.client_exception import (
    NotFoundException, ConflictException,
    RequestEntityTooLargeException, UnsupportedMediaTypeException,
    UnprocessableEntityException, BadRequestException
)
from exception.server_exception import InternalServerErrorException
from app.utils.dto.success import created, ok

logger = logging.getLogger(__name__)

# def dummy_ocr_from_image(file: UploadFile):
#     return [
#         {
#             "description": "이미지 문제 1?",
#             "options": ["A", "B", "C", "D"],
#             "answer": 1
#         },
#         {
#             "description": "이미지 문제 2?",
#             "options": ["가", "나", "다", "라"],
#             "answer": 3
#         }
#     ]
#
# def dummy_ocr_process(file: UploadFile):
#     return [
#         {
#             "description": "1 + 1 = ?",
#             "options": ["1", "2", "3", "4"],
#             "answer": 2,
#         },
#         {
#             "description": "2 + 2 = ?",
#             "options": ["2", "3", "4", "5"],
#             "answer": 3,
#         }
#     ]

async def upload_my_studybook_by_pdf_usecase(file: UploadFile, current_user: User, db: AsyncSession, answer_list: list = None, question_count: int = None):
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

        ocr_result = gpt_ocr_process(file, expected_question_count=question_count)
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

        for idx, item in enumerate(ocr_result):
            # answer_list가 있으면 해당 인덱스의 답을 사용, 없으면 OCR 결과 사용
            answer = answer_list[idx] if answer_list and idx < len(answer_list) else item.get("answer", 1)
            question = StudyBookQuestion(
                study_book_id=new_book.id,
                description=item["description"],
                description_detail=None,
                description_image=None,
                options=item["options"],
                answer=answer,
                option_explanations=None,
                explanation=item.get("explanation"),
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

async def upload_my_studybook_by_img_usecase(file: UploadFile, current_user: User, db: AsyncSession, answer_list: list = None):
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

        ocr_result = gpt_ocr_process(file)

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

        for idx, item in enumerate(ocr_result):
            # answer_list가 있으면 해당 인덱스의 답을 사용, 없으면 OCR 결과 사용
            answer = answer_list[idx] if answer_list and idx < len(answer_list) else item.get("answer", 1)
            question = StudyBookQuestion(
                study_book_id=new_book.id,
                description=item["description"],
                description_detail=None,
                description_image=None,
                options=item["options"],
                answer=answer,
                explanation=item.get("explanation"),
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
            data=json.loads(MyStudybookResponseDTO(studybooks=response_items).json()),
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

async def upload_my_studybook_by_dummy_usecase(
    studybook_name: str,
    questions: list[dict],
    current_user: User,
    db: AsyncSession
):
    # 중복 체크
    result = await db.execute(
        select(StudyBook).where(
            StudyBook.name == studybook_name,
            StudyBook.user_id == current_user.id
        )
    )
    existing_studybook = result.scalars().first()
    if existing_studybook:
        raise ConflictException("이미 있는 파일명입니다.")

    # StudyBook insert
    new_book = StudyBook(
        name=studybook_name,
        created_at=datetime.now(),
        question_count=len(questions),
        file_color="#%06x" % (uuid.uuid4().int & 0xFFFFFF),
        user_id=current_user.id,
    )
    db.add(new_book)
    await db.flush()

    # StudyBookQuestion insert
    for item in questions:
        question = StudyBookQuestion(
            study_book_id=new_book.id,
            description=item["description"],
            description_detail=None,
            description_image=None,
            options=item["options"],
            answer=item["answer"],
            option_explanations=None,
            explanation=item.get("explanation"),
        )
        db.add(question)

    await db.commit()

    logger.info(f"[SUCCESS] upload_my_studybook_by_dummy_usecase - user_id: {current_user.id}, studybook_id: {new_book.id}")

    return created(
        data=UploadStudybookResponseDTO(
            studybook_id=new_book.id,
            message="문제집이 성공적으로 생성되었습니다. (dummy)"
        ).dict(),
        message="문제집 생성 성공 (dummy)"
    )

async def get_studybook_detail_usecase(studybook_id: int, current_user: User, db: AsyncSession):
    """
    문제집 상세 조회
    """
    try:
        # 문제집 조회
        result = await db.execute(
            select(StudyBook).where(
                StudyBook.id == studybook_id,
                StudyBook.user_id == current_user.id
            )
        )
        studybook = result.scalars().first()

        if not studybook:
            raise NotFoundException("문제집을 찾을 수 없습니다.")

        # 문제들 조회
        questions_result = await db.execute(
            select(StudyBookQuestion).where(
                StudyBookQuestion.study_book_id == studybook_id
            ).order_by(StudyBookQuestion.id)
        )
        questions = questions_result.scalars().all()

        # DTO 생성
        from app.studybook.dto.response.studybook_detail_response_dto import (
            StudybookDetailResponseDTO, StudybookDetailDTO, QuestionItemDTO
        )

        question_items = [
            QuestionItemDTO(
                id=q.id,
                description=q.description,
                options=q.options,
                answer=q.answer,
                explanation=q.explanation
            )
            for q in questions
        ]

        detail_dto = StudybookDetailDTO(
            id=studybook.id,
            name=studybook.name,
            question_count=studybook.question_count,
            file_color=studybook.file_color,
            questions=question_items
        )

        logger.info(f"[SUCCESS] get_studybook_detail_usecase - user_id: {current_user.id}, studybook_id: {studybook_id}")

        return ok(
            data=detail_dto.dict(),
            message=f"문제집 상세 조회 성공"
        )

    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] get_studybook_detail_usecase - {str(e)}")
        raise InternalServerErrorException(f"문제집 조회 중 오류 발생: {str(e)}")


async def upload_my_studybook_usecase(
    files: list[UploadFile],
    current_user: User,
    db: AsyncSession,
    answer_list: list = None,
    question_count: int = None
):
    """
    PDF 또는 이미지 파일을 받아 문제집을 생성하는 통합 usecase

    Args:
        files: PDF 또는 이미지 파일 리스트
        current_user: 현재 사용자
        db: Database session
        answer_list: 정답 리스트 (선택사항)
        question_count: 예상 문제 개수 (PDF 전용, 선택사항)
    """
    try:
        if not files:
            raise BadRequestException("최소 1개 이상의 파일이 필요합니다.")

        # 첫 번째 파일의 확장자로 타입 결정
        first_file = files[0]
        file_ext = Path(first_file.filename).suffix.lower()

        if file_ext == ".pdf":
            # PDF 모드: 단일 파일만 처리
            if len(files) > 1:
                raise BadRequestException("PDF는 1개 파일만 업로드 가능합니다.")
            return await upload_my_studybook_by_pdf_usecase(
                files[0], current_user, db, answer_list, question_count
            )
        elif file_ext in [".jpg", ".jpeg", ".png"]:
            # 이미지 모드: 여러 파일 처리
            return await upload_my_studybook_by_images_usecase(
                files, current_user, db, answer_list
            )
        else:
            raise UnsupportedMediaTypeException("PDF 또는 이미지 파일(jpg, jpeg, png)만 업로드 가능합니다.")

    except (BadRequestException, UnsupportedMediaTypeException) as e:
        logger.warning(f"[CLIENT ERROR] upload_my_studybook_usecase - {str(e)}")
        raise e
    except Exception:
        logger.error("[SERVER ERROR] upload_my_studybook_usecase")
        logger.error(traceback.format_exc())
        raise InternalServerErrorException("문제집 생성 중 서버 오류가 발생했습니다.")


async def upload_my_studybook_by_images_usecase(
    files: list[UploadFile],
    current_user: User,
    db: AsyncSession,
    answer_list: list = None
):
    """
    여러 이미지 파일을 받아 하나의 문제집을 생성하는 usecase

    각 파일이 하나의 이미지로 처리되며, 모든 이미지의 문제를 하나의 문제집으로 통합합니다.
    """
    try:
        # 파일명 검증 (중복 체크용 이름)
        combined_name = "_".join([Path(f.filename).stem for f in files[:3]])
        if len(files) > 3:
            combined_name += f"_외{len(files)-3}개"

        result = await db.execute(
            select(StudyBook).where(
                StudyBook.name == combined_name,
                StudyBook.user_id == current_user.id
            )
        )
        existing_studybook = result.scalars().first()

        if existing_studybook:
            raise ConflictException("이미 있는 파일명입니다.")

        # 모든 파일에서 OCR 결과 수집
        all_questions = []
        for file in files:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in [".jpg", ".jpeg", ".png"]:
                raise UnsupportedMediaTypeException(f"잘못된 파일 형식: {file.filename} (jpg, jpeg, png만 가능)")

            ocr_result = gpt_ocr_process(file)
            if not ocr_result:
                raise UnprocessableEntityException(f"이미지를 분석할 수 없습니다: {file.filename}")

            all_questions.extend(ocr_result)

        # 문제집 생성
        new_book = StudyBook(
            name=combined_name,
            created_at=datetime.now(),
            question_count=len(all_questions),
            file_color="#%06x" % (uuid.uuid4().int & 0xFFFFFF),
            user_id=current_user.id,
        )
        db.add(new_book)
        await db.flush()

        # 문제 저장
        for idx, item in enumerate(all_questions):
            answer = answer_list[idx] if answer_list and idx < len(answer_list) else item.get("answer", 1)
            question = StudyBookQuestion(
                study_book_id=new_book.id,
                description=item["description"],
                description_detail=None,
                description_image=None,
                options=item["options"],
                answer=answer,
                explanation=item.get("explanation"),
                option_explanations=None,
            )
            db.add(question)

        await db.commit()

        logger.info(f"[SUCCESS] upload_my_studybook_by_images_usecase - user_id: {current_user.id}, studybook_id: {new_book.id}, file_count: {len(files)}")

        return created(
            data=UploadStudybookResponseDTO(
                studybook_id=new_book.id,
                message=f"{len(files)}개 이미지에서 {len(all_questions)}개 문제를 추출했습니다."
            ).dict(),
            message="이미지 문제집 생성 성공"
        )
    except (UnsupportedMediaTypeException, ConflictException, UnprocessableEntityException) as e:
        logger.warning(f"[CLIENT ERROR] upload_my_studybook_by_images_usecase - {str(e)}")
        raise e
    except Exception:
        logger.error("[SERVER ERROR] upload_my_studybook_by_images_usecase")
        logger.error(traceback.format_exc())
        raise InternalServerErrorException("이미지 문제집 생성 중 서버 오류가 발생했습니다.")
