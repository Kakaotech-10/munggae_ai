import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Set
from model.model_pretrain.filtering_model import load_model, predict_hate_speech
from openai import OpenAI

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 모델 및 토크나이저 로드
model, tokenizer = load_model()

# OpenAI api (키 값 필요)
client = OpenAI(
    api_key=""
)

# 요청 데이터 모델 정의
class TextRequest(BaseModel):
    text: str = Field(..., examples=["메롱"])

class TextResponse(BaseModel):
    text: str = Field(..., examples=["메롱"])
    labels: List[str] = Field(..., examples=[["clean"]])
    message: str = Field(..., examples=["메롱"])

class PostContent(BaseModel):
    content: str

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

# 유틸리티 함수: 게시글 답변 생성 챗봇
def generate_reply(post_content):
    try:
        reply = client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {
                    "role": "system",
                    "content":
                    """
                    너는 게시글에 알맞는 답변을 해주는 챗봇이야. 답변은 한국어로 해줘. 답변은 반말로 해줘.
                    만약 정보를 물어본다거나, 도움이 필요한 글이거나 학습, 진로와 같이 진지한 주제의 글이면 답변을 최대한 자세히 해줘.
                    만약 글이 일상적인 글이고 일상 공유를 하고 진지하지 않은 성격이면 친구처럼 간단하고 친근하게 답해줘.
                    가끔씩 이모지도 사용하면서 답해줘.
                    """
                },
                {"role": "user", "content":post_content}
            ]
        )
        return reply.choices[0].message
    except Exception as e:
        print(f"Error generating response: {e}")
        return "답변을 생성하는 중 오류가 발생했습니다. 나중에 다시 시도해 주세요."

# 텍스트 필터링 API 엔드포인트
@app.post("/api/v1/ai/text/", response_model=TextResponse)
def filter_text(request: TextRequest):
    """텍스트 필터링 API 엔드포인트: 유해성 검열"""
    try:
        text_chunks = split_text_by_sentences(request.text, max_length=512)
        overall_labels = set()

        for chunk in text_chunks:
            result = predict_hate_speech(model, tokenizer, chunk)
            overall_labels.update(result)

        # 유해한 라벨 필터링
        if 'clean' not in overall_labels:
            return generate_response(request.text, overall_labels, is_clean=False)

        # 'clean'인 경우
        return generate_response(request.text, {"clean"}, is_clean=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류가 발생했습니다: {str(e)}")
    

@app.post("/reply")
def reply(post_content: PostContent):
    if not post_content.content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    reply = generate_reply(post_content.content)
    return {"reply": reply}

# uvicorn 명령어 예시
# uvicorn ai_server:app --reload
# /opt/homebrew/bin/python3 -m uvicorn ai_server:app --reload -> lucy환경실행
