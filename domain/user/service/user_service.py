import uuid
import os
from pathlib import Path

from fastapi import UploadFile
from exception.client_exception import BadRequestException


class UserService:

    def __init__(self):
        self.upload_dir = Path("uploads/profile_images")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload_profile_image(self, image: UploadFile) -> str:
        """프로필 이미지를 로컬 저장소에 업로드"""
        # 파일 확장자 검증
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        ext = image.filename.split(".")[-1].lower()
        if ext not in allowed_extensions:
            raise BadRequestException(message="png, jpg, jpeg 파일만 업로드 가능합니다.")

        filename = f"profile_image_{uuid.uuid4()}.{ext}"
        filepath = self.upload_dir / filename
        content = await image.read()

        with open(filepath, "wb") as f:
            f.write(content)

        return f"/uploads/profile_images/{filename}"

    def delete_profile_image(self, image_url: str):
        """로컬 저장소에서 프로필 이미지 삭제"""
        if not image_url:
            raise BadRequestException(message="파일 경로를 찾을 수 없습니다.")

        filename = image_url.split("/")[-1]
        filepath = self.upload_dir / filename

        if filepath.exists():
            os.remove(filepath)
