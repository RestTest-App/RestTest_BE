FROM python:3.11-slim

WORKDIR /code

# 의존성 설치
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 소스 코드 복사
COPY . .

# 배포용 CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]