import sys

import requests

from tests.auth_test import BASE_URL


def generate_token():
    payload = {
        "code": "resttest"
    }

    response = requests.post(f"{BASE_URL}/sign-in-test", json=payload)
    print("응답 : ", response.status_code)

    try:
        response_json = response.json()
    except ValueError:
        print(response.text)
        sys.exit(1)

    if response.status_code != 201:
        print("로그인 실패")
        sys.exit(1)

    print("access token : ", response_json.get("data").get("access_token"))
    print("refresh token : ", response_json.get("data").get("refresh_token"))
    data = response_json.get("data", {})
    return data.get("access_token"), data.get("refresh_token")

generate_token()