import os
import shutil
import base64
import re
import json
import requests
from pdf2image import convert_from_path
from PIL import Image
from openai import OpenAI
from core.config import settings
from exception.client_exception import UnprocessableEntityException
from core.config import gpt_settings
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# tmp dir 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_DIR = os.path.join(BASE_DIR, "app", "utils", "tmp")
os.makedirs(TMP_DIR, exist_ok=True)

# OpenAI 클라이언트
client = OpenAI(api_key=gpt_settings.OPENAI_API_KEY)
# TMP 초기화
def reset_tmp_dir():
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

# PDF → 이미지 저장
def save_pdf_pages(pdf_path, dpi=600):
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
    except Exception as e:
        raise UnprocessableEntityException("PDF → 이미지 변환 실패: " + str(e))

    paths = []
    for i, img in enumerate(images, start=1):
        path = os.path.join(TMP_DIR, f"page{i:02d}.png")
        img.save(path)
        paths.append(path)
    return paths

# 이미지 crop + split
def crop_and_split_image(path):
    img = Image.open(path)
    w, h = img.size
    # 양쪽 절반으로 나누기 (상하 크롭 제거)
    left = img.crop((0, 0, w // 2, h))
    right = img.crop((w // 2, 0, w, h))

    base = os.path.splitext(os.path.basename(path))[0]
    left_path = os.path.join(TMP_DIR, f"{base}_left.png")
    right_path = os.path.join(TMP_DIR, f"{base}_right.png")
    left.save(left_path)
    right.save(right_path)
    return [left_path, right_path]

# Naver OCR 호출 (텍스트만)
def naver_ocr_image(path):
    import json
    import uuid
    import time

    try:
        with open(path, "rb") as img_f:
            img_data = img_f.read()

        # Naver OCR API의 multipart/form-data 요청
        message_data = {
            "version": "V2",
            "requestId": str(uuid.uuid4()),
            "timestamp": int(time.time() * 1000),
            "images": [
                {
                    "format": "png",
                    "name": "image"
                }
            ]
        }
        files = {
            "message": (None, json.dumps(message_data)),
            "file": ("image.png", img_data, "application/octet-stream")
        }
        headers = {
            "X-OCR-SECRET": gpt_settings.NAVER_SECRET_KEY,
        }
        print(f"[DEBUG] Naver OCR Request URL: {gpt_settings.NAVER_OCR_URL}")
        print(f"[DEBUG] Headers: {headers}")
        print(f"[DEBUG] Files keys: {list(files.keys())}")

        response = requests.post(
            gpt_settings.NAVER_OCR_URL,
            files=files,
            headers=headers,
            timeout=60
        )

        print(f"[DEBUG] Naver OCR Response Status: {response.status_code}")
        print(f"[DEBUG] Naver OCR Response Length: {len(response.text)}")

        if response.status_code != 200:
            print(f"[DEBUG] Naver OCR API Error Response (first 500 chars): {response.text[:500]}")
            raise UnprocessableEntityException(f"Naver OCR API 오류: {response.status_code} - {response.text[:200]}")

        # Response가 비어있는지 확인
        if not response.text or not response.text.strip():
            print(f"[DEBUG] Naver OCR returned empty response")
            raise UnprocessableEntityException("Naver OCR API returned empty response")

        try:
            result = response.json()
        except json.JSONDecodeError as je:
            print(f"[DEBUG] Failed to parse Naver OCR JSON. Response (first 500 chars): {response.text[:500]}")
            raise UnprocessableEntityException(f"Naver OCR API returned invalid JSON: {str(je)}")

        # Naver OCR 응답에서 텍스트 추출
        extracted_text = ""
        if "images" in result and len(result["images"]) > 0:
            image_data = result["images"][0]
            if "fields" in image_data:
                for field in image_data["fields"]:
                    if "inferText" in field:
                        extracted_text += field["inferText"] + "\n"

        print(f"[DEBUG] Extracted {len(extracted_text)} characters of text")
        return extracted_text.strip()
    except UnprocessableEntityException:
        raise
    except Exception as e:
        print(f"[DEBUG] Exception in naver_ocr_image: {str(e)}")
        raise UnprocessableEntityException("Naver OCR 실패: " + str(e))

# OCR 결과에서 문제 텍스트 블록 추출 - 구조 기반 추출
def extract_questions(text):
    # OCR 텍스트를 파일에 저장 (디버깅용)
    debug_text_path = os.path.join(TMP_DIR, "ocr_full_text.txt")
    with open(debug_text_path, "w", encoding="utf-8") as f:
        f.write(text)

    # 구조 기반 추출: 문제 번호로 분할하지 않고 전체 텍스트를 청크로 나누기
    # GPT가 직접 질문 + 선택지 패턴을 인식해서 문제를 분할할 것임

    # 매우 긴 텍스트는 청크로 나누기 (너무 길면 GPT가 처리 못할 수 있음)
    # 대략 6000자 정도씩 나누기 (더 많은 컨텍스트를 위해 증가)
    chunk_size = 6000
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size].strip()
        if chunk:
            chunks.append(chunk)

    print(f"[DEBUG] Total text length: {len(text)}")
    print(f"[DEBUG] Split into {len(chunks)} chunks (chunk_size={chunk_size})")

    question_files = []
    for idx, chunk in enumerate(chunks, start=1):
        out_path = os.path.join(TMP_DIR, f"questions_part_{idx:02d}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(chunk)
        question_files.append(out_path)

    return question_files

# GPT Vision으로 정답 추출
def extract_answers_from_image(image_path):
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "이 이미지는 1~100번 문제의 정답 목록입니다. 다음 형식으로 추출해주세요.\n\n1:3\n2:1\n..."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        }]
        res = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.3)
        answer_text = res.choices[0].message.content.strip()

        answer_map = {}
        for line in answer_text.splitlines():
            if match := re.match(r"(\d{1,3}):([1-4])", line.strip()):
                answer_map[int(match[1])] = int(match[2])
        return answer_map
    except Exception as e:
        raise UnprocessableEntityException("정답 이미지 GPT Vision 호출 실패: " + str(e))

# 문제 chunk 들 → JSON 변환
def parse_questions_to_json(question_files, answer_map):
    result = []
    for qf in question_files:
        with open(qf, "r", encoding="utf-8") as f:
            content = f.read()

        prompt = f"""
다음은 객관식 시험 문제들입니다. 문제 번호로 구분하지 말고, 다음과 같은 구조로 문제를 추출해주세요:
- 질문 문장이 있고, 그 다음에 4개의 선택지(옵션)가 주르륵 나오는 부분을 하나의 문제로 묶으세요.
- 번호는 무시하고 구조만 보세요. (예: "1) 정답", "① 정답" 등 기호는 선택지의 일부일 수 있으므로 제거해서 순수 텍스트만 추출하세요)
- 문제 문장에 "---" 또는 "----" 같은 빈칸 표시가 있으면 그대로 유지하세요. (예: "The bank --- money" → 그대로 "The bank --- money")

각 문제를 다음 형식의 JSON 배열로 출력해주세요:

[
  {{
    "description": "문제 설명 (질문 전체, 빈칸 기호 포함)",
    "options": ["선택지1의 순수 텍스트", "선택지2의 순수 텍스트", "선택지3의 순수 텍스트", "선택지4의 순수 텍스트"],
    "answer": null
  }},
  ...
]

중요 사항:
1. options 배열은 정확히 4개의 선택지여야 합니다.
2. answer는 null로 두세요 (나중에 GPT가 자동으로 채웁니다).
3. 선택지에서 번호 기호(1), 2), ①, ②, ㄱ, ㄴ 등)를 모두 제거하고 순수 텍스트만 남기세요.
4. description에는 문제의 전체 설명을 포함하세요. **빈칸 표시(---, ----, ___ 등)는 반드시 유지하세요.**
5. 빈칙이 없는 일반 문제도 빠짐없이 포함하세요.

텍스트:
{content}
"""
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            response_content = res.choices[0].message.content
            print(f"[DEBUG] GPT Response: {response_content}")
            if not response_content:
                raise UnprocessableEntityException("GPT 응답이 비어있습니다.")

            # 마크다운 형식의 JSON을 처리 (```json ... ```)
            if response_content.startswith("```"):
                # 첫 번째 ``` 찾기
                start = response_content.find("```") + 3
                # json 키워드 건너뛰기
                if response_content[start:start+4] == "json":
                    start += 4
                # 끝 ``` 찾기
                end = response_content.rfind("```")
                response_content = response_content[start:end].strip()

            json_block = json.loads(response_content)
            print(f"[DEBUG] Parsed {len(json_block)} questions from chunk")
            result.extend(json_block)
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON Decode Error: {e}, Content: {response_content[:200]}")
            raise UnprocessableEntityException(f"GPT 응답 파싱 실패: {e}")
        except Exception as e:
            raise UnprocessableEntityException("GPT 문제 JSON 생성 실패: " + str(e))

    print(f"[DEBUG] Total questions parsed before answer mapping: {len(result)}")

    # 정답 번호 대입 (구조 기반 추출에서는 순번으로 매핑)
    # answer_map에서 순번 1부터 대입
    for i, q in enumerate(result):
        question_number = i + 1
        if question_number in answer_map:
            q["answer"] = answer_map[question_number]
        elif q.get("answer") is None:
            # 아직 답이 없으면 나중에 GPT가 채우도록 None 유지
            q["answer"] = None

    return result

# 누락된 답을 GPT에서 가져오기
def get_missing_answers_from_gpt(questions: list[dict]) -> list[dict]:
    """
    답이 없는 문제들을 GPT에 10개씩 배치로 물어봐서 답을 채우기
    """
    questions_without_answers = [(idx, q) for idx, q in enumerate(questions) if not q.get("answer")]

    if not questions_without_answers:
        return questions

    # 10개씩 배치로 나누기
    batch_size = 10
    for i in range(0, len(questions_without_answers), batch_size):
        batch = questions_without_answers[i:i+batch_size]
        batch_questions = [q for _, q in batch]
        batch_indices = [idx for idx, _ in batch]

        # 배치 문제들을 GPT에 전달
        prompt = f"""
다음은 객관식 시험의 문제들입니다. 각 문제의 정답을 JSON 형식으로 반환해주세요.
다음 형식으로 응답해주세요:
[
  {{"index": 0, "answer": 1}},
  {{"index": 1, "answer": 3}},
  ...
]

중요: answer는 반드시 1부터 4까지의 숫자여야 합니다 (0이 아닌 1부터 시작).
선택지 번호를 나타냅니다. 예) 첫 번째 선택지=1, 두 번째 선택지=2, 세 번째 선택지=3, 네 번째 선택지=4

문제들:
"""
        for idx, q in enumerate(batch_questions):
            prompt += f"\n{idx}. {q['description']}\n"
            if q.get("options"):
                for opt_idx, opt in enumerate(q["options"], 1):
                    prompt += f"   {opt_idx}) {opt}\n"

        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            response_content = res.choices[0].message.content
            print(f"[DEBUG] Answer completion response: {response_content}")

            # 마크다운 형식의 JSON 처리
            if response_content.startswith("```"):
                start = response_content.find("```") + 3
                if response_content[start:start+4] == "json":
                    start += 4
                end = response_content.rfind("```")
                response_content = response_content[start:end].strip()

            answers = json.loads(response_content)

            # 추출된 답을 원래 배열에 적용
            for answer_item in answers:
                batch_idx = answer_item.get("index")
                answer_val = answer_item.get("answer")
                if batch_idx is not None and answer_val is not None:
                    original_idx = batch_indices[batch_idx]
                    questions[original_idx]["answer"] = answer_val
                    print(f"[DEBUG] Updated question {original_idx} with answer {answer_val}")

        except json.JSONDecodeError as e:
            print(f"[DEBUG] Answer JSON Decode Error: {e}, Content: {response_content}")
            # 답을 가져올 수 없으면 기본값 1 설정
            for idx in batch_indices:
                if not questions[idx].get("answer"):
                    questions[idx]["answer"] = 1
        except Exception as e:
            print(f"[DEBUG] Answer completion error: {str(e)}")
            # 에러 발생 시 기본값 1 설정
            for idx in batch_indices:
                if not questions[idx].get("answer"):
                    questions[idx]["answer"] = 1

    return questions

# 정답 검수 및 해설 생성
def verify_and_add_explanations(questions: list[dict]) -> list[dict]:
    """
    각 문제의 정답을 검수하고 해설을 생성합니다.
    배치 처리로 여러 문제를 한 번에 처리합니다.
    """
    batch_size = 5

    for i in range(0, len(questions), batch_size):
        batch = questions[i:i+batch_size]

        # 배치 문제들을 프롬프트에 포함
        prompt = """다음은 영어 객관식 문제들입니다. 각 문제에 대해:
1. 정답이 올바른지 검수하고, 잘못되었으면 수정
2. 한국어 해설 작성 (문법, 의미 등 설명)

다음 JSON 형식으로 응답해주세요:
[
  {
    "index": 0,
    "verified_answer": 1,
    "explanation": "해설 텍스트"
  },
  ...
]

문제들:
"""

        for idx, q in enumerate(batch):
            prompt += f"\n{idx}. {q['description']}\n"
            if q.get("options"):
                for opt_idx, opt in enumerate(q["options"], 1):
                    prompt += f"   {opt_idx}) {opt}\n"
            prompt += f"현재 정답: {q.get('answer', 'N/A')}\n"

        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            response_content = res.choices[0].message.content

            # 마크다운 형식의 JSON 처리
            if response_content.startswith("```"):
                start = response_content.find("```") + 3
                if response_content[start:start+4] == "json":
                    start += 4
                end = response_content.rfind("```")
                response_content = response_content[start:end].strip()

            verifications = json.loads(response_content)

            # 검수 결과 적용
            for verification in verifications:
                batch_idx = verification.get("index")
                if batch_idx is not None and batch_idx < len(batch):
                    original_idx = i + batch_idx
                    questions[original_idx]["answer"] = verification.get("verified_answer", questions[original_idx].get("answer"))
                    questions[original_idx]["explanation"] = verification.get("explanation", "")

        except json.JSONDecodeError as e:
            print(f"[DEBUG] Verification JSON Decode Error: {e}")
            # 해설 추가 실패 시 빈 해설로 진행
            for idx in range(len(batch)):
                original_idx = i + idx
                if "explanation" not in questions[original_idx]:
                    questions[original_idx]["explanation"] = ""
        except Exception as e:
            print(f"[DEBUG] Verification error: {str(e)}")
            # 에러 발생 시 빈 해설로 진행
            for idx in range(len(batch)):
                original_idx = i + idx
                if "explanation" not in questions[original_idx]:
                    questions[original_idx]["explanation"] = ""

    return questions

# PDF에서 직접 텍스트 추출 (빈칸 보존)
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    pdfplumber를 사용하여 PDF에서 직접 텍스트를 추출합니다.
    Naver OCR보다 빈칸(---, ___ 등)을 잘 보존합니다.
    """
    if pdfplumber is None:
        print("[DEBUG] pdfplumber not available, returning empty string")
        return ""

    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    print(f"[DEBUG] Extracted text from page {page_num}: {len(page_text)} characters")

        full_text = "\n\n".join(text_parts)
        print(f"[DEBUG] Total extracted text: {len(full_text)} characters")
        return full_text
    except Exception as e:
        print(f"[DEBUG] Error extracting text from PDF: {e}")
        return ""

# 최종 API용으로 사용할 함수 (PDF 직접 추출 + Naver OCR 보완)
def gpt_ocr_process(pdf_file, expected_question_count: int = None) -> list[dict]:
    reset_tmp_dir()

    # UploadFile을 tmp PDF로 저장
    tmp_pdf_path = os.path.join(TMP_DIR, "input.pdf")
    try:
        with open(tmp_pdf_path, "wb") as f:
            f.write(pdf_file.file.read())
    except Exception as e:
        raise UnprocessableEntityException("PDF 임시 저장 실패: " + str(e))

    # PDF를 페이지별 이미지로 변환
    pages = save_pdf_pages(tmp_pdf_path)

    # 1단계: PDF에서 직접 텍스트 추출 (빈칸 보존)
    print(f"[DEBUG] 1단계: PDF 직접 추출 시작")
    full_ocr_text = extract_text_from_pdf(tmp_pdf_path)

    # 2단계: PDF 직접 추출이 실패했거나 부족하면 Naver OCR 사용
    if not full_ocr_text or len(full_ocr_text) < 500:
        print(f"[DEBUG] 2단계: PDF 직접 추출 실패/불충분, Naver OCR 진행")
        all_text = []
        last_image = None

        for page_num, page_path in enumerate(pages, start=1):
            try:
                # 페이지를 좌우로 분할
                split_paths = crop_and_split_image(page_path)
                print(f"[DEBUG] Page {page_num} split into 2 halves")

                for half_idx, half_path in enumerate(split_paths):
                    position = "좌측" if half_idx == 0 else "우측"
                    try:
                        print(f"[DEBUG] Page {page_num}-{position}: Naver OCR 처리")
                        ocr_result = naver_ocr_image(half_path)
                        if ocr_result:
                            all_text.append(ocr_result)
                            print(f"[DEBUG] Page {page_num}-{position} OCR result length: {len(ocr_result)}")
                        last_image = half_path
                    except Exception as e:
                        print(f"[DEBUG] Error processing page {page_num}-{position}: {e}")
                        continue
            except Exception as e:
                print(f"[DEBUG] Error splitting page {page_num}: {e}")
                try:
                    ocr_result = naver_ocr_image(page_path)
                    if ocr_result:
                        all_text.append(ocr_result)
                        last_image = page_path
                except Exception as e2:
                    print(f"[DEBUG] Fallback OCR also failed: {e2}")
                    continue

        full_ocr_text = "\n\n".join(all_text)
        last_image = pages[-1]  # 정답 추출용 마지막 이미지
    else:
        print(f"[DEBUG] 2단계: PDF 직접 추출 성공, Naver OCR 스킵")
        last_image = pages[-1]  # 정답 추출용 마지막 이미지

    print(f"[DEBUG] Total extracted text: {len(full_ocr_text)} characters")

    # 문제 추출
    question_files = extract_questions(full_ocr_text)

    # 정답 이미지에서 추출
    if last_image:
        answer_map = extract_answers_from_image(last_image)
    else:
        print("[DEBUG] No last_image available for answer extraction")
        answer_map = {}

    questions_json = parse_questions_to_json(question_files, answer_map)

    # 3단계: 최종 검증
    extracted_count = len(questions_json)
    if expected_question_count is not None:
        print(f"[DEBUG] 3단계: 최종 검증 - Expected {expected_question_count} questions, got {extracted_count}")
        if extracted_count < expected_question_count:
            print(f"[WARNING] Still missing {expected_question_count - extracted_count} questions")

    # 누락된 답 채우기
    questions_json = get_missing_answers_from_gpt(questions_json)

    # 정답 검수 및 해설 생성
    print(f"[DEBUG] 정답 검수 및 해설 생성 중...")
    questions_json = verify_and_add_explanations(questions_json)

    return questions_json
