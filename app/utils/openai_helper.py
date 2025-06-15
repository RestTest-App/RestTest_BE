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
