import os
import shutil
import base64
import re
import json
from pdf2image import convert_from_path
from PIL import Image
from openai import OpenAI
from core.config import settings
from exception.client_exception import UnprocessableEntityException
from core.config import gpt_settings

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
def save_pdf_pages(pdf_path, dpi=500):
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
    cropped = img.crop((0, 200, w, h - 150))
    left = cropped.crop((0, 0, w // 2, cropped.height))
    right = cropped.crop((w // 2, 0, w, cropped.height))

    base = os.path.splitext(os.path.basename(path))[0]
    left_path = os.path.join(TMP_DIR, f"{base}_left.png")
    right_path = os.path.join(TMP_DIR, f"{base}_right.png")
    left.save(left_path)
    right.save(right_path)
    return [left_path, right_path]

# GPT Vision OCR 호출
def gpt_ocr_image(path):
    try:
        with open(path, "rb") as img_f:
            b64 = base64.b64encode(img_f.read()).decode("utf-8")
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "이 이미지는 시험지 일부입니다. 내용을 가능한 정확하게 추출해주세요."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        }]
        res = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.3)
        return res.choices[0].message.content.strip()
    except Exception as e:
        raise UnprocessableEntityException("GPT Vision OCR 실패: " + str(e))

# OCR 결과에서 문제 텍스트 블록 추출
def extract_questions(text):
    matches = list(re.finditer(r"(?:^|\n)(\d{1,3})[.)]", text))
    if not matches:
        raise UnprocessableEntityException("문제 번호 패턴을 찾을 수 없습니다.")

    chunks = []
    for i in range(0, len(matches), 20):
        start = matches[i].start()
        end = matches[i + 20].start() if i + 20 < len(matches) else len(text)
        chunks.append(text[start:end].strip())

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
다음은 객관식 시험 문제들입니다. 각 문제는 다음 형식의 JSON 배열로 출력해주세요:

[
  {{
    "description": "문제 설명",
    "options": ["보기1", "보기2", "보기3", "보기4"],
    "answer": 2
  }},
  ...
]

텍스트:
{content}
"""
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            json_block = json.loads(res.choices[0].message.content)
            result.extend(json_block)
        except json.JSONDecodeError as e:
            raise UnprocessableEntityException(f"GPT 응답 파싱 실패: {e}")
        except Exception as e:
            raise UnprocessableEntityException("GPT 문제 JSON 생성 실패: " + str(e))

    # 정답 번호 대입
    for i, q in enumerate(result):
        if (i + 1) in answer_map:
            q["answer"] = answer_map[i + 1]
    return result

# 최종 API용으로 사용할 함수
def gpt_ocr_process(pdf_file) -> list[dict]:
    reset_tmp_dir()

    # UploadFile을 tmp PDF로 저장
    tmp_pdf_path = os.path.join(TMP_DIR, "input.pdf")
    try:
        with open(tmp_pdf_path, "wb") as f:
            f.write(pdf_file.file.read())
    except Exception as e:
        raise UnprocessableEntityException("PDF 임시 저장 실패: " + str(e))

    # 전체 파이프라인 실행
    pages = save_pdf_pages(tmp_pdf_path)

    all_text = []
    last_image = None
    for path in pages:
        left, right = crop_and_split_image(path)
        all_text.append(gpt_ocr_image(left))
        all_text.append(gpt_ocr_image(right))
        last_image = right

    full_ocr_text = "\n\n".join(all_text)

    question_files = extract_questions(full_ocr_text)
    answer_map = extract_answers_from_image(last_image)
    questions_json = parse_questions_to_json(question_files, answer_map)

    return questions_json
