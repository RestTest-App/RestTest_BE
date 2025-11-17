import uuid
import boto3

from fastapi import UploadFile
from core.config import aws_settings
from exception.client_exception import BadRequestException


class UserService:

    def __init__(self):
        self._s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_settings.AWS_SECRET_ACCESS_KEY,
            region_name=aws_settings.AWS_REGION_NAME
        )
        self._bucket = aws_settings.AWS_BUCKET_NAME

    async def upload_profile_image(self, image: UploadFile) -> str:
        """프로필 이미지를 S3에 업로드"""
        # 파일 확장자 검증
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        ext = image.filename.split(".")[-1].lower()
        if ext not in allowed_extensions:
            raise BadRequestException(message="png, jpg, jpeg 파일만 업로드 가능합니다.")

        filename = f"profile_image_{uuid.uuid4()}.{ext}"
        content = await image.read()

        self._s3.put_object(
            Bucket=self._bucket,
            Key=filename,
            Body=content,
            ContentType=image.content_type
        )

        return f"https://{self._bucket}.s3.{aws_settings.AWS_REGION_NAME}.amazonaws.com/{filename}"

    def delete_profile_image(self, image_url: str):
        """S3에서 프로필 이미지 삭제"""
        if not image_url:
            raise BadRequestException(message="파일 경로를 찾을 수 없습니다.")
        key = image_url.split(".amazonaws.com/")[-1]
        self._s3.delete_object(Bucket=self._bucket, Key=key)
