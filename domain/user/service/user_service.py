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

    @staticmethod
    async def upload_profile_image(self, image: UploadFile) -> str:
        ext = image.filename.split(".")[-1]
        filename = f"profile_image_{uuid.uuid4()}.{ext}"
        content = await image.read()

        self._s3.put_object(
            Bucket=self._bucket,
            Key=filename,
            Body=content,
            ContentType=image.content_type
        )

        return f"https://{self.bucket}.s3.{aws_settings.AWS_REGION_NAME}.amazonaws.com/{filename}"

    @staticmethod
    async def delete_profile_image(self, image_url: str):
        if not image_url:
            raise BadRequestException(message="파일 경로를 찾을 수 없습니다.")
        key = image_url.split(".amazonaws.com/")[-1]
        self._s3.delete_object(Bucket=self._bucket, Key=key)