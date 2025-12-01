import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from app.utils.logger import logger
from exception.client_exception import UnprocessableEntityException


# openai api key 분기처리
MODE = os.getenv("MODE", "dev")

if MODE == "dev":
    load_dotenv(".env.dev")
elif MODE == "prod":
    load_dotenv(".env")

_api_key = os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise RuntimeError(f"OPENAI_API_KEY가 설정되지 않았습니다. (MODE={MODE})")



client = OpenAI(api_key=_api_key)

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
당신은 대한민국 국가기술자격 및 전문 자격증 시험 출제 위원입니다.
주어진 자격증 이름('{certificate_name}')을 분석하여, 실제 시험과 유사한 난이도와 형식의 4지선다 객관식 문제 10개를 출제해주세요.

###[출제 지침]
1. **주요 자격증 처리**:
   - '정보처리기사' 관련: 소프트웨어 설계, 개발, 데이터베이스, 프로그래밍 언어 활용, 정보시스템 구축 관리 등 실제 필기 과목 비율을 고려하세요.
   - '컴퓨터활용능력' 관련: 컴퓨터 일반, 스프레드시트(Excel), 데이터베이스(Access) 일반 내용을 포함하세요.
   - 기타 자격증: 해당 분야의 핵심 이론, 실무 지식, 관련 법규 등을 포함하세요.

2. **생소한 자격증 처리**:
   - 만약 학습 데이터에 없는 생소한 자격증이라면, 자격증 이름의 의미를 분석하여 해당 분야의 기초 지식이나 일반 상식, 논리적 추론 문제를 생성하세요. 절대 빈 응답을 보내지 마세요.

3. **문제 품질**:
   - 문제는 명확하고 간결해야 합니다.
   - 정답은 논란의 여지가 없이 하나여야 합니다.
   - 오답(Distractor)은 매력적이어야 하며 터무니없지 않아야 합니다.
   - 각 보기에 대한 명확한 해설을 제공해야 합니다.

4. **출력 형식 (엄격 준수)**:
   - 오직 **순수 JSON 배열**만 출력하세요.
   - Markdown 코드 블럭(```json 등)이나 사족(설명 멘트)을 절대 포함하지 마세요.
   - JSON 키 값은 아래 예시를 정확히 따르세요.

###[출력 예시 데이터 구조(엄격하게 준수)]
[
  {{
    "description": "문제 지문 (예: 다음 중 데이터베이스의 특징으로 옳지 않은 것은?)",
    "description_detail": "지문 외에 추가적인 코드나 표, 상황 설명이 필요한 경우 작성 (없으면 null)",
    "options": ["실시간 접근성", "계속적인 변화", "동시 공유", "주소에 의한 참조"],
    "answer": 3,  // 정답의 인덱스 (0, 1, 2, 3 중 하나, 위 예시에서는 '주소에 의한 참조'가 정답)
    "option_explanations": [
        "실시간 접근성은 DB의 특징이 맞습니다.",
        "데이터는 삽입, 삭제, 갱신으로 계속 변합니다.",
        "여러 사용자가 동시에 사용할 수 있습니다.",
        "데이터베이스는 주소가 아닌 내용(Content)에 의해 참조됩니다."
    ]
  }}
]

### 다시 한번 강조합니다
- 반드시 유효한 JSON 배열만 출력하세요.
- 코드블록(```` ````, ` ```json `) 사용 금지.
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