import re
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Set
from model.model_pretrain.filtering_model import load_model, predict_hate_speech

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 모델 및 토크나이저 로드
model, tokenizer = load_model()

#로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 요청 데이터 모델 정의
class TextRequest(BaseModel):
    text: str = Field(..., examples=["메롱"])

class TextResponse(BaseModel):
    text: str = Field(..., examples=["메롱"])
    labels: List[str] = Field(..., examples=[["clean"]])
    message: str = Field(..., examples=["메롱"])

# 유틸리티 함수: 문장 단위로 텍스트 분할
def split_text_by_sentences(text: str, max_length: int = 512) -> List[str]:
    """텍스트를 문장 단위로 분할하고, 각 블록이 max_length를 넘지 않도록 조정"""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# 유틸리티 함수: 응답 생성
def generate_response(text: str, labels: Set[str], is_clean: bool) -> TextResponse:
    """필터링된 텍스트에 대한 응답을 생성하는 함수"""
    if is_clean:
        message = f"{text}"
    else:
        message = f"{', '.join(labels)}에 위배되는 문장입니다."

    return TextResponse(text=text, labels=list(labels), message=message)

# 텍스트 필터링 API 엔드포인트
@app.post("/api/v1/ai/text", response_model=TextResponse)
def filter_text(request: TextRequest):
    """텍스트 필터링 API 엔드포인트: 유해성 검열"""
    try:
        #요청 데이터 로깅
        logger.info(f"request.text = {request.text}")
        text_chunks = split_text_by_sentences(request.text, max_length=512)
        overall_labels = set()

        for chunk in text_chunks:
            result = predict_hate_speech(model, tokenizer, chunk)
            overall_labels.update(result)

        # 유해한 라벨 필터링
        if 'clean' not in overall_labels:
            response = generate_response(request.text, overall_labels, is_clean=False)
            logger.info(f"response = {response}")
            return response

        # 'clean'인 경우
        response = generate_response(request.text, {"clean"}, is_clean=True)
        logger.info(f"response = {response}")
        return response


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류가 발생했습니다: {str(e)}")

# uvicorn 명령어 예시
# uvicorn ai_server:app --reload
# /opt/homebrew/bin/python3 -m uvicorn ai_server:app --reload -> lucy환경실행
