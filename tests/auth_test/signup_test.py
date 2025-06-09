import sys
import requests
from tests.auth_test import BASE_URL


# 회원가입 테스트
def generate_user():
    payload = {
        "code": "resttest",
        "nickname": "Rest Kim",
        "gender": "male",
        "birthday": "2000-01-01",
        "job": "student",
        "certificates": [1, 2, 3],
        "agree_to_terms": True
    }

    response = requests.post(f"{BASE_URL}/sign-up-test", json=payload)
    print("응답 : ",response.status_code)

    try:
        response_json = response.json()
    except ValueError:
        print(response.text)
        sys.exit(1)

    print("access token : ", response_json.get("data").get("access_token"))
    print("refresh token : ", response_json.get("data").get("refresh_token"))
    data = response_json.get("data", {})
    return data.get("access_token"), data.get("refresh_token")

generate_user()