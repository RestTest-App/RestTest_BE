from requests_oauthlib import OAuth2Session

from core.config import kakao_settings
from domain.auth.service.auth_service import AuthService
from exception.client_exception import ForbiddenException

import os
import requests

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class KakaoAuthService(AuthService):

    KAKAO_CLIENT_ID = kakao_settings.KAKAO_CLIENT_ID
    KAKAO_CLIENT_SECRET_KEY = kakao_settings.KAKAO_CLIENT_SECRET_KEY
    KAKAO_REDIRECT_URI = kakao_settings.KAKAO_REDIRECT_URI

    KAKAO_AUTHORIZE_URL = kakao_settings.KAKAO_AUTHORIZE_URL
    KAKAO_TOKEN_URL = kakao_settings.KAKAO_TOKEN_URL
    KAKAO_PROFILE_URL = kakao_settings.KAKAO_PROFILE_URL

    async def fetch_kakao_user_info(self, code: str) -> dict:
        resp = requests.post(
            self.KAKAO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": self.KAKAO_CLIENT_ID,
                "client_secret": self.KAKAO_CLIENT_SECRET_KEY,
                "redirect_uri": self.KAKAO_REDIRECT_URI,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        )
        resp.raise_for_status()
        token_data = resp.json()
        access_token = token_data["access_token"]

        # 프로필 조회
        profile_resp = requests.get(
            self.KAKAO_PROFILE_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_resp.raise_for_status()
        profile = profile_resp.json()

        email = profile.get("kakao_account", {}).get("email")
        if not email:
            raise ForbiddenException("카카오에 등록된 이메일이 없습니다.")
        return {"email": email, "auth_provider": "KAKAO"}
