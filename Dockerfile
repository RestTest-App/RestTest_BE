FROM python:3.11-slim

WORKDIR /code

# 의존성 설치
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# poppler-utils 설치 추가
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*

# 소스 코드 복사
COPY . .

# 환경 변수로 reload 제어
ARG MODE=prod
ENV MODE=$MODE

# 배포용 CMD
CMD ["/bin/sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080 $([ \"$MODE\" = \"dev\" ] && echo '--reload' || echo '')"]
