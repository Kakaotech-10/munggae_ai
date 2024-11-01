# Python 3.11 이미지 사용
FROM python:3.11-slim

WORKDIR /app

# Git 및 Git LFS 설치
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*


# requirements.txt 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# transformers 및 safetensors 최신 버전 설치
RUN pip install --no-cache-dir -U transformers safetensors

# 모델과 토크나이저 사전 다운로드 (safetensors 대신 pytorch_model.bin으로 대체)
RUN python -c "from transformers import BertForSequenceClassification; BertForSequenceClassification.from_pretrained('monologg/kobert', use_safetensors=False)"

# 애플리케이션 파일 복사
COPY . .

EXPOSE 8080

CMD ["uvicorn", "ai_server:app", "--host", "0.0.0.0", "--port", "8080"]
