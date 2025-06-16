import os
import json
from openai import OpenAI
from app.utils.logger import logger
from exception.client_exception import UnprocessableEntityException

# .env.dev에서 OPENAI_API_KEY 직접 불러오기
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_option_explanations(question: dict) -> list[str]:
    """
    GPT에게 보기별 해설 생성 요청
    """
    prompt = f"""
다음은 자격증 시험 문제입니다. 아래 문제와 보기를 보고, 각 보기마다 해설을 한 줄씩 JSON 배열 형식으로 작성해주세요.

문제: {question['description']}
보기:
{chr(10).join([f"{i+1}. {opt}" for i, opt in enumerate(question['options'])])}

출력 예시 (JSON만 출력): 
[
  "보기1 해설",
  "보기2 해설",
  "보기3 해설",
  "보기4 해설"
]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 보기별 해설을 짧고 명확하게 작성하는 AI입니다."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.7,
            max_tokens=512
        )
        content = response.choices[0].message.content.strip()

        try:
            explanations = json.loads(content)
            if not isinstance(explanations, list) or len(explanations) != len(question["options"]):
                raise ValueError("형식 오류")
            return explanations
        except Exception:
            logger.warning(f"[GPT WARNING] option_explanations 파싱 실패: {content}")
            raise UnprocessableEntityException("AI 해설 생성 실패 (JSON 파싱 에러)")

    except Exception as e:
        logger.warning(f"[GPT WARNING] GPT API 호출 실패: {str(e)}")
        raise UnprocessableEntityException("AI 해설 생성 실패")

async def generate_today_questions(certificate_name: str) -> list[dict]:
    """
    GPT에게 오늘의 시험 문제 10개 생성 요청
    """
    prompt = f"""
당신은 자격증 시험 문제 출제 AI입니다.
다음 자격증 이름을 기반으로 객관식 4지선다 문제 10개를 JSON 배열 형태로 생성해주세요.

자격증 이름: {certificate_name}
자격증에서 나올 수 있는 다양한 범위에서 문제를 뽑아 작성해주세요
출력 포맷 예시:
[
  {{
    "description": "문제 내용",
    "description_detail": "문제 상세 설명 (선택사항, 없으면 null)",
    "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
    "answer": 2,  // 인덱스 (0부터 시작)
    "option_explanations": ["해설1", "해설2", "해설3", "해설4"]
  }},
  ...
]
반드시 유효한 JSON으로만 출력해 주세요.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 자격증 시험 문제를 정확히 JSON 형식으로 출력하는 AI입니다."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        content = response.choices[0].message.content.strip()

        try:
            result = json.loads(content)
            if not isinstance(result, list) or len(result) != 10:
                raise ValueError("문제 수 오류 또는 형식 오류")
            return result
        except Exception:
            logger.warning(f"[GPT WARNING] today_test_question 파싱 실패: {content}")
            raise UnprocessableEntityException("AI 문제 생성 실패 (JSON 파싱 에러)")
    except Exception as e:
        logger.warning(f"[GPT WARNING] GPT API 호출 실패: {str(e)}")
        raise UnprocessableEntityException("AI 문제 생성 실패")