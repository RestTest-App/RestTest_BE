from core.config import kakao_settings
from exception.client_exception import ForbiddenException
import requests

class KakaoAuthService:

    def __init__(self):
        self.client_id = kakao_settings.KAKAO_CLIENT_ID
        self.client_secret = kakao_settings.KAKAO_CLIENT_SECRET_KEY
        self.redirect_uri = kakao_settings.KAKAO_REDIRECT_URI
        self.authorize_url = kakao_settings.KAKAO_AUTHORIZE_URL
        self.token_url = kakao_settings.KAKAO_TOKEN_URL
        self.profile_url = kakao_settings.KAKAO_PROFILE_URL

    async def fetch_kakao_user_info(self, code: str) -> dict:
        resp = requests.post(
            self.token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        )
        resp.raise_for_status()
        token_data = resp.json()
        access_token = token_data["access_token"]

        # 카카오 프로필 조회
        profile_resp = requests.get(
            self.profile_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_resp.raise_for_status()
        profile = profile_resp.json()

        # 이메일 확인
        email = profile.get("kakao_account", {}).get("email")
        if not email:
            raise ForbiddenException("카카오에 등록된 이메일이 없습니다.")

        return {"email": email, "auth_provider": "KAKAO"}
