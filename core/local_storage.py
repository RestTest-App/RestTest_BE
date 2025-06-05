import os
from fastapi import UploadFile
from domain.storage.storage_provider import StorageProvider
from core.config import settings

class LocalStorageProvider(StorageProvider):

    def __init__(self):
        # 예: settings.UPLOAD_DIR = "/app/uploads/profile_images"
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async def save_file(self, file: UploadFile, destination_name: str) -> str:
        """
        file.filename 확장자와 상관없이, destination_name(예: UUID + 확장자)을 사용해 저장.
        반환값은 클라이언트가 접근 가능한 URL 경로(ex: "/static/profile_images/uuid.png").
        """
        # destination_name: "uuid4hex.png" 같은 형태로 넘겨준다고 가정
        dest_path = os.path.join(settings.UPLOAD_DIR, destination_name)

        with open(dest_path, "wb") as buffer:
            buffer.write(await file.read())

        # public path: settings.STATIC_URL + "/" + destination_name
        # 예: settings.STATIC_URL = "/static/profile_images"
        return f"{settings.STATIC_URL}/{destination_name}"

    async def delete_file(self, file_url_or_key: str) -> None:
        """
        file_url_or_key: 예시 "/static/profile_images/uuid.png" 형태일 때,
        실제 로컬 경로(settings.UPLOAD_DIR + "/uuid.png")를 계산하여 삭제.
        """
        # file_url_or_key에서 파일명만 뽑기
        filename = os.path.basename(file_url_or_key)
        path = os.path.join(settings.UPLOAD_DIR, filename)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception:
                pass
        # 존재하지 않거나 삭제 오류가 나도 무시